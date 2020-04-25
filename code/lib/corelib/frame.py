#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os
import sys
import errno
import signal

import random
from collections import OrderedDict

import grpc
from gevent import sleep, getcurrent
from gevent.event import Event

from corelib import log, spawn, common, message
from corelib.process import LocalProcessMgr

MSG_FRAME_START = 'MSG_FRAME_START'
MSG_FRAME_STOP = 'MSG_FRAME_STOP'
MSG_FRAME_APP_ADD = 'MSG_FRAME_APP_ADD'
MSG_FRAME_APP_DEL = 'MSG_FRAME_APP_DEL'
MSG_ALL_LOGIC_START = 'MSG_ALL_LOGIC_START'

try:
    from psutil import pid_exists
except ImportError as err:
    if sys.platform.startswith('win'):
        raise err

    def pid_exists(pid):
        """Check whether pid exists in the current process table."""
        if pid < 0:
            return False
        try:
            os.kill(pid, 0)
        except OSError:
            err = sys.exc_info()[1]
            if err.errno == errno.ESRCH:
                # ESRCH == No such process
                return False
            elif err.errno == errno.EPERM:
                # EPERM clearly means there's a process to deny access to
                return True
            else:
                # According to "man 2 kill" possible error values are
                # (EINVAL, EPERM, ESRCH) therefore we should bever get
                # here. If we do let's be explicit in considering this
                # an error.
                raise err
        else:
            return True



def module_to_dict(md):
    """ 过滤模块内容,返回可序列化的数据对象 """
    d1 = {}
    for name in dir(md):
        if name.startswith('_'):
            continue
        value = getattr(md, name)
        if type(value) not in (bool, int, str, float, tuple, list, dict):
            continue
        d1[name] = value
    return d1


@message.observable_cls
class Game(object):
    app = None
    app_svrs = {}
    cur_time_zone = None

    @classmethod
    def get_service(cls, app_name, rpc_name):
        services = cls.app_svrs.get(app_name, {})
        service = services.get(rpc_name, None)
        return service

    @classmethod
    def get_cur_time_zone(cls):
        if cls.cur_time_zone is None:
            import pytz
            import datetime
            for tzName in pytz.all_timezones:
                # 获取本地时间
                localtime = datetime.datetime.now()
                # 设置当前时区
                tz = pytz.timezone(tzName)
                # 获取时区转换后的时间
                time = datetime.datetime.now(tz)

                if str(localtime)[:19] == str(time)[:19]:
                    cls.cur_time_zone = int(str(time)[-6:-3])
        return cls.cur_time_zone


class MultiAttr(object):
    def __init__(self, name):
        self.name = name
        self.key = '_multi_attr_%s' % self.name
        self.addrs = {}  # {addr: rpc_svr}

    def count(self):
        return len(self.addrs)

    def get_rpc_svr(self, addr=None):
        svr = None
        if addr:
            svr = self.addrs.get(addr, None)
        if svr:
            return svr
        task = getcurrent()
        try:
            addr = getattr(task, self.key)
        except AttributeError:
            addr = random.choice(list(self.addrs.keys()))
            setattr(task, self.key, addr)
        return self.addrs[addr]

    def _add(self, addr, rpc_obj):
        if addr in self.addrs:
            return
        if rpc_obj is None:
            rpc_obj = grpc.get_proxy_by_addr(addr, self.name)
        self.addrs[addr] = rpc_obj

    def _del(self, addr):
        self.addrs.pop(addr, None)

    def __iter__(self):
        for addr, rpc_obj in self.addrs.items():
            yield addr, rpc_obj


class AddrNamesOp(object):
    """ 远程对象处理类,mixin进AbsMFActor子类中使用 """
    def _get_cls(self):
        return Game

    def _set_cls_attr(self, cls, app_name, addr, mode, name, rpc_obj=None):
        attr = cls.__dict__.get(name)
        if rpc_obj is None:
            rpc_obj = grpc.get_proxy_by_addr(addr, name)
        else:
            rpc_obj._rpc_addr = addr

        objs = cls.app_svrs.setdefault(app_name, {})
        objs[name] = rpc_obj

        if isinstance(attr, MultiAttr):
            attr._add(addr, rpc_obj)
        elif attr is None and mode != MultiCell.MODE:
            setattr(cls, name, rpc_obj)
        else:
            if isinstance(attr, grpc.RpcProxy):
                old_addr = attr.get_addr()
            else:
                old_addr = attr._rpc_addr if attr else None
            if old_addr == addr:
                return
            multi_attr = MultiAttr(name)
            if old_addr:
                multi_attr._add(old_addr, attr)
            multi_attr._add(addr, rpc_obj)
            setattr(cls, name, multi_attr)

    def _del_cls_attr(self, cls, app_name, addr, name):
        attr = cls.__dict__.get(name)
        if isinstance(attr, MultiAttr):
            attr._del(addr)
        else:
            setattr(cls, name, None)
        objs = cls.app_svrs.get(app_name, {})
        objs.pop(name, None)

    def add_my_names(self, app_name, addr, mode, name_objs):
        cls = self._get_cls()
        for name, obj in name_objs:
            self._set_cls_attr(cls, app_name, addr, mode, name, rpc_obj=obj)

    def add_addr_names(self, app_name, addr, mode, names):
        addr = tuple(addr)
        cls = self._get_cls()
        for name in names:
            self._set_cls_attr(cls, app_name, addr, mode, name)
        cls.pub(MSG_FRAME_APP_ADD, app_name, addr, names)

    def del_addr_names(self, app_name, addr, names):
        addr = tuple(addr)
        cls = self._get_cls()
        for name in names:
            self._del_cls_attr(cls, app_name, addr, name)
        cls.pub(MSG_FRAME_APP_DEL, app_name, addr, names)


class AbsMainApplication(AddrNamesOp):
    """ 主进程用户抽象类 """
    def __init__(self, config):
        self.config = config

    def init_frame(self):
        self.frame = MainFrame(self)
        self.frame.init()
        Game.app = self
        grpc.shell_locals['f'] = self.frame

    @property
    def name(self):
        return 'MainApplication'

class MainFrame(object):
    """ 主进程类 """
    _rpc_name_ = 'rpc_frame_main'

    def __init__(self, application):
        self.application = application
        self.cell_mgr = CellMgr(self)
        self.listen_port = None
        self.stoped = True
        #子进程字典
        self.sub_proxys = OrderedDict()  # {addr: sub_proxy}
        # 部件主进程字典
        self.part_proxys = {}  # {addr: part_proxy}

    def init(self, listen_port=None):
        if listen_port is None:
            listen_port = self.application.config.base_port
        self.listen_port = listen_port
        self.rpc_svr = grpc.RpcServer()
        self.rpc_svr.bind(('0.0.0.0', listen_port))
        self.rpc_svr.register(self)
        self.rpc_svr.start()

    def start(self):
        """ 启动 """
        self.cell_mgr.add_cells_by_cfg(self.application.config.frames)
        self.stoped = False
        self.cell_mgr.start()

    def _on_close(self, sub_proxy):
        self.del_sub_proxy(sub_proxy)

    def add_part_proxy(self, addr):
        addr = tuple(addr)
        self.part_proxys[addr] = grpc.get_proxy_by_addr(addr, PartMainFrame._rpc_name_)

    def get_addr_names(self):
        return [(sub_proxy._app_name, addr, sub_proxy._mode, sub_proxy._app_names) for addr, sub_proxy in self.sub_proxys.items()]

    def add_sub_proxy(self, addr, mode, app_name, names):
        """ 子进程功能注册 """
        addr = tuple(addr)
        sub_proxy = grpc.get_proxy_by_addr(addr, app_name)
        sub_proxy.sub_close(self._on_close)
        sub_proxy._app_name = app_name
        sub_proxy._app_names = names
        sub_proxy._mode = mode
        #通知更新
        self.application.add_addr_names(app_name, addr, mode, names)
        for other_sub_proxy in self.sub_proxys.values():
            spawn(other_sub_proxy.add_other_proxy, app_name, addr, mode, names)
        old_addr_names = self.get_addr_names()
        self.sub_proxys[tuple(addr)] = sub_proxy
        return old_addr_names

    def del_sub_proxy(self, sub_proxy):
        """ 子进程删除 """
        addr = sub_proxy.get_addr()
        if addr not in self.sub_proxys:
            return
        self.sub_proxys.pop(addr)
        app_name = sub_proxy._app_name
        names = sub_proxy._app_names
        if not self.stoped:
            #通知更新
            self.application.del_addr_names(app_name, addr, names)
            for sub_frame in self.sub_proxys.values():
                spawn(sub_frame.del_other_proxy, app_name, addr, names)

    def stop(self):
        self.stoped = True
        for sub_frame in list(self.sub_proxys.values())[::-1]:
            try:
                sub_frame.stop(_no_result=1)
            except:
                log.log_except()
        for part_proxy in self.part_proxys.values():
            spawn(part_proxy.stop, _no_result=1)
        sleep(1)
        self.rpc_svr.stop()
        grpc.uninit()
        self.cell_mgr.stop()

    def before_stop(self):
        """ 通知所有功能模块准备关闭 """
        self.cell_mgr.pause()
        for sub_proxy in list(self.sub_proxys.values())[::-1]:
            try:
                sub_proxy.before_stop()
            except:
                log.log_except()
        for part_proxy in self.part_proxys.values():
            part_proxy.before_stop()

    def reload_modules(self, module_name_list):
        if type(module_name_list) == str:
            module_name_list = [module_name_list]
        from corelib import xreload
        for module_name in module_name_list:
            xreload.reload_module(module_name)
        for sub_proxy in self.sub_proxys.values():
            sub_proxy.reload_modules(module_name_list)
        for part_proxy in self.part_proxys.values():
            part_proxy.reload_modules(module_name_list)

    rm=reload_modules

class AbsPartApplication(AddrNamesOp):
    def __init__(self, config):
        self.config = config

    def init_frame(self):
        self.frame = PartMainFrame(self)
        self.frame.init()
        Game.app = self

    @property
    def name(self):
        return "PartApplication" + self.config.part_name

class PartMainFrame(object):
    """ 部件主进程类 """
    _rpc_name_ = 'rpc_frame_part'

    def __init__(self, application):
        self.application = application
        self.cell_mgr = CellMgr(self)
        self.listen_port = None
        self.stoped = True

    def init(self, listen_port=None):
        if listen_port is None:
            listen_port = self.application.config.base_port
        self.listen_port = listen_port
        self.rpc_svr = grpc.RpcServer()
        self.rpc_svr.bind(('0.0.0.0', listen_port))
        self.rpc_svr.register(self)
        self.rpc_svr.start()

        self.main_proxy = grpc.get_proxy_by_addr(self.application.config.main_addr, MainFrame._rpc_name_)
        addr = (self.application.config.local_ip, self.listen_port)
        self.main_proxy.add_part_proxy(addr)

    def start(self):
        """ 启动 """
        self.cell_mgr.add_cells_by_cfg(self.application.config.frames)
        self.stoped = False
        self.cell_mgr.start()

    def stop(self):
        self.stoped = True
        self.cell_mgr.stop()
        self.application.stop()

    def before_stop(self):
        """ 通知所有功能模块准备关闭 """
        self.cell_mgr.pause()

    def reload_modules(self, module_name_list):
        from corelib import xreload
        for module_name in module_name_list:
            xreload.reload_module(module_name)


class AbsSubApplication(AddrNamesOp):
    """ 子进程用户抽象类 """
    def init_frame(self, pid, addr):
        """ 初始化框架,之后会去主进程注册 """
        self.frame = SubFrame(self, pid, addr)
        self.frame.init()
        Game.app = self

    def register(self, export, name=None):
        return self.frame.rpc_svr.register(export, name=name)

class SubFrame(object):
    """ 子进程类 """
    def __init__(self, application, main_pid, addr):
        """  """
        self.addr = addr  # 子进程监听地址:(ip, 端口)
        self.main_pid = main_pid  # 父进程id
        self.main_addr = None  # 主进程地址
        self.main_proxy = None  # 远程主进程对象
        self.names = {}  # {name: export_obj}
        self.stoped = True
        self.application = application

    @property
    def name(self):
        return self.application.name

    @property
    def _rpc_name_(self):
        return self.application.name

    def init(self):
        #fix pypy ctypes import error:OSError: [error 10] No Such process
        if hasattr(signal, 'SIGCHLD'):
            signal.signal(signal.SIGCHLD, signal.SIG_DFL)

        self.rpc_svr = grpc.RpcServer()
        self.rpc_svr.bind(('0.0.0.0', int(self.addr[1])))
        self.rpc_svr.register(self)
        self.rpc_svr.start()

    def start(self):
        if not self.stoped:
            return
        log.info('[subFrame] start:%s', self.addr)
        self.stoped = False
        #去主进程注册输出的对象
        names = list(self.names.keys())
        self.application.add_my_names(self.name, self.addr, self.mode,
                                [(name, obj) for name, obj in self.names.items()])
        addr_names = self.main_proxy.add_sub_proxy(self.addr, self.mode, self.name, names)
        for app_name, addr, mode, names in addr_names:
            self.add_other_proxy(app_name, addr, mode, names)

        self.application.after_start()

    def before_stop(self):
        """ 准备关闭 """
        self.application.before_stop()

    def stop(self):
        if self.stoped:
            return
        self.stoped = True
        log.info('[subFrame](%s) stop', self.name)
        for name in self.names:
            obj = self.rpc_svr.get_export(name)
            if hasattr(obj, 'stop'):
                try:
                    obj.stop()
                except:
                    log.log_except('stop(%s) error', obj)
        #----------------------
        self.rpc_svr.stop()
        grpc.uninit()

    def is_idle(self):
        """ 是否空闲,返回True该子进程将被释放 """
        return False

    def set_main_addr(self, addr, mode):
        log.info('set_main_addr:%s', addr)
        self.main_addr = addr
        self.mode = mode
        self.main_proxy = grpc.get_proxy_by_addr(self.main_addr, MainFrame._rpc_name_)

    def init_config(self, config_dict):
        self.application.init_config(config_dict)

    def registers(self, funcs):
        """ 注册对象 """
        names = []
        for func in funcs:
            names.extend(self.register(func))
        return names

    def register(self, obj_func):
        """ 注册对象 """
        if isinstance(obj_func, str):
            objs = common.import1(obj_func)()
        else:
            objs = obj_func()
        names = self.reg_objs(objs)
        return names

    def reg_objs(self, objs):
        if not isinstance(objs, (tuple, list)):
            objs = (objs, )
        names = [self.reg_obj(obj) for obj in objs]
        return names

    def reg_obj(self, obj):
        name = self.rpc_svr.register(obj)
        self.names[name] = obj
        log.info('[subgame]register:%s', name)
        return name

    def add_other_proxy(self, app_name, addr, mode, names):
        """ 添加其他子进程的远程对象 """
        self.application.add_addr_names(app_name, addr, mode, names)

    def del_other_proxy(self, app_name, addr, names):
        """ 删除其他子进程的远程对象 """
        self.application.del_addr_names(app_name, addr, names)

    def exist_pid(self):
        """ 检查主进程是否存在,不存在的情况下自动退出 """
        return pid_exists(self.main_pid)

    def reload_modules(self, module_name_list):
        log.warning('********app(%s) reload_modules*******', self.name)
        from corelib import xreload
        for module_name in module_name_list:
            xreload.reload_module(module_name)
        log.warning('********app(%s) reload_modules end!!!!*******', self.name)


class CellMgr(object):
    """ 子进程管理类,启动管理子进程 """
    _rpc_name_ = 'rpc_frame_cell_mgr'

    def __init__(self, main_frame, unix_path=None):
        self.addrs = {}  # {app_name:addr} 记录app对应addr,
        self.total = 0  # 已经启动了的子进程总数
        self.unix_path = unix_path
        self.proc_mgr = LocalProcessMgr()
        self._pause_event = Event()
        #避免僵尸进程
        #因为并发服务器常常fork很多子进程，子进程终结之后需要
        #服务器进程去wait清理资源。如果将此信号的处理方式设为
        #忽略，可让内核把僵尸子进程转交给init进程去处理，省去了
        #大量僵尸进程占用系统资源。(Linux Only)
        if hasattr(signal, 'SIGCHLD'):
            signal.signal(signal.SIGCHLD, signal.SIG_IGN)

        self.config = main_frame.application.config
        self.main_frame = main_frame
        self.cells = OrderedDict()  # {name: cell}

    def get_cell(self, name):
        return self.cells.get(name)

    def add_cell(self, cell):
        self.cells[cell.name] = cell

    def add_cells_by_cfg(self, frames):
        """ 根据cfg配置情况,启动子进程
        cfg: [{name:'name', cls: '', funcs:['func1', 'func2', ...], kw:{}}, ]
            name: 名称
            mode: 子进程运行模式, single=单一子进程, multi=负载均衡子进程
            funcs: 子进程函数列表
            kw:  子进程类创建参数字典
        """
        for values in frames:
            name = values['name']
            funcs = values['funcs']
            cls_name = values.get('mode', '')
            kw = values.get('kw', {})
            #指定地址
            addr = values.get('addr', None)
            if addr:
                self.reg_sub_proxy_addr(name, addr)
            if not cls_name or cls_name == 'single':
                cls = SingleCell
            elif cls_name == 'multi':
                cls = MultiCell
            else:
                cls = common.import1(cls_name)
            cell = cls(self, name, funcs, **kw)
            self.add_cell(cell)

    def reg_sub_proxy_addr(self, name, addr):
        self.addrs[name] = addr

    def _get_addr(self, app_name):
        """ 根据app_name,获取子进程用的addr """
        if app_name in self.addrs:
            addr = self.addrs[app_name]
        elif self.config.free_addrs:
            addr = self.config.free_addrs.pop(0)
        elif self.unix_path:  # linux系统下,使用unix socket
            addr = os.path.join(self.unix_path, '%s.sock' % app_name)
        else:
            raise ValueError('no free addr for app_name(%s)' % app_name)
        log.info('sub_game addr: %s', addr)
        return addr

    def start(self):
        for cell in self.cells.values():
            cell.start()
        self._loop_task = spawn(self._loop)

    @property
    def stoped(self):
        return self._loop_task is None

    def stop(self):
        if self.stoped:
            return
        task, self._loop_task = self._loop_task, None
        task.kill()
        self.proc_mgr.killall()

    def pause(self):
        self._pause_event.clear()

    def resume(self):
        self._pause_event.set()

    def _loop(self):
        """ 管理游戏逻辑进程,维持合理的进程数量 """
        while not self.stoped:
            sleep(10)
            self._check_cells()

    def _check_cells(self):
        """ 检查cell是否正常 """
        for cell in self.cells.values():
            spawn(cell.check)

    def _new_subgame(self, app_name, sub_cmd=None, cwd=None, kw=None):
        """ 新建进程 """
        times = 30
        self.total += 1
        addr = self._get_addr(app_name)
        if kw is None:
            kw = {}

        kw.update(dict(name=app_name, pid=os.getpid(), addr=addr))
        if sub_cmd is None:
            sub_cmd = self.config.sub_game_cmd

        cmd = sub_cmd % kw
        if self.config.debug_key == app_name:
            cmd += ' subgame_debug'
            times = 50
        if cwd is None:
            cwd = self.config.root_path

        #启动
        env = None  # env存在时,启动有问题 dict(subgame_index=str(self.subgame_index), )
        pid = self.proc_mgr.start_process(cmd, cwd=cwd, env=env)
        sub_proxy = None
        for i in range(times):
            sleep(0.5)
            sub_proxy = grpc.get_proxy_by_addr(addr, app_name)
            if sub_proxy:
                break
        if sub_proxy is None:
            raise SystemError('new subgame error')
        sub_proxy._sub_pid = pid
        sub_proxy._sub_addr = addr
        return sub_proxy


class BaseCell(object):
    """ 单一个功能类 """
    MODE = ''

    def __init__(self, mgr, name, funcs=None, cmd=None, cwd=None, kw=None):
        """
        @param:
            name: 名称
            funcs: 子进程启动的函数列表
            cmd: 子进程启动命令
            cwd: 子进程启动时的当前目录
            kw: 启动命令参数
        """
        self.mgr = mgr
        self.name = name
        self.funcs = funcs
        self.cmd, self.cwd, self.kw = cmd, cwd, kw

    def _on_close(self, app):
        """ 子进程断线 """
        pass

    def _run_app(self, name, funcs):
        """ 启动子进程 """
        sub_proxy = self.mgr._new_subgame(name, sub_cmd=self.cmd, cwd=self.cwd, kw=self.kw)
        sub_proxy.set_main_addr(self.mgr.config.main_addr, self.MODE)
        sub_proxy.init_config(module_to_dict(self.mgr.config))
        if funcs:
            sub_proxy.registers(funcs,
                          _pickle=not all([isinstance(f, str) for f in funcs]))
        sub_proxy.start()
        sub_proxy.sub_close(self._on_close)
        return sub_proxy

    def _check_pid(self, pid):
        """ 检查进程(游戏逻辑进程和union进程)是否正常 """
        return pid_exists(pid)

    def check(self):
        """ 检查进程是否正常 """
        pass

    def start(self):
        self.check()


class SingleCell(BaseCell):
    """ 单核 """
    MODE = 'single'

    def __init__(self, *args, **kw):
        BaseCell.__init__(self, *args, **kw)
        self.sub_proxy = None

    def _on_close(self, sub_proxy):
        """ 子进程断线 """
        if sub_proxy != self.sub_proxy:
            raise ValueError('[SingleCell](%s) on_close call by other app', self.name)
        pid = self.sub_proxy._sub_pid
        addr = self.sub_proxy._sub_addr
        log.warning('close app:pid=%s, app_name=%s, addr=%s', pid, self.name, addr)
        self.mgr.proc_mgr.kill_process(pid)
        self.app = None

    def check(self):
        """ 检查进程是否正常 """
        if self.mgr.main_frame.application.stoped:
           return
        if self.sub_proxy is None:
            self.sub_proxy = self._run_app(self.name, self.funcs)
            self.mgr.reg_sub_proxy_addr(self.name, self.sub_proxy._sub_addr)
        elif not self._check_pid(self.sub_proxy._sub_pid):
            self._on_close(self.sub_proxy)


class MultiCell(BaseCell):
    """ 多核 """
    MODE = 'multi'

    def __init__(self, *args, **kw):
        """
        @param:
            check: 检查函数或字符串(def check(cell): return 0|1|-1), 检查函数返回: 0=不处理, -1=减少, 1=增加
        """
        self._check_func = kw.pop('check')
        if isinstance(self._check_func, str):
            self._check_func = common.import1(self._check_func)
        BaseCell.__init__(self, *args, **kw)
        self.sub_proxys = []
        self.index = 0

    def get_count(self):
        return len(self.sub_proxys)

    def _make_name(self):
        """ 新子进程名 """
        self.index += 1
        return '%s%d' % (self.name, self.index)

    def _on_close(self, sub_proxy):
        """ 子进程断线 """
        if sub_proxy not in self.sub_proxys:
            raise ValueError('[MultiCell](%s) on_close call by other app', self.name)
        pid = sub_proxy._sub_pid
        addr = sub_proxy._sub_addr
        log.warning('close app:pid=%s, app_name=%s, addr=%s', pid, self.name, addr)
        self.sub_proxys.remove(sub_proxy)
        self.mgr.proc_mgr.kill_process(pid)

    def check(self):
        """ 检查进程是否正常 """
        if self.mgr.main_frame.application.stoped:
           return
        while 1:
            rs = self._check_func(self)
            if rs == 1:
                self._inc()
            elif rs == -1:
                self._dec()
            else:
                break

            #检查所有子进程是否存在
            for sub_proxy in self.sub_proxys[:]:
                pid = sub_proxy._sub_pid
                if not self._check_pid(pid):
                    self._on_close(sub_proxy)

    def _inc(self):
        """ 增加 """
        log.info('[MultiCell](%s)_inc', self.name)
        sub_proxy = self._run_app(self._make_name(), self.funcs)
        sub_proxy.sub_close(self._on_close)
        self.sub_proxys.append(sub_proxy)
        return sub_proxy

    def _dec(self):
        """ 检查是否有空余的逻辑进程,释放 """
        # todo [::-1] 反转列表,测试用,为了方便内存泄漏测试,保留最早的进程
        for sub_proxy in self.sub_proxys[:][::-1]:
            if not sub_proxy.is_idle():
                continue
            self.sub_proxys.remove(sub_proxy)
            sub_proxy.stop()
            break




#------------------------
#------------------------
#------------------------

