#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import struct
import ujson

from gevent.queue import Queue
from gevent.event import AsyncResult
from gevent import sleep, GreenletExit
import time

from grpc import AbsExport, get_service
from corelib import log, spawn, spawn_later, iter_id_func

from game.define.errcode import EC_VALUE, EC_NOFOUND
from game import Game

DATA_HEAD_STRUCT = '<BH'
DATA_HEAD_LEN = struct.calcsize(DATA_HEAD_STRUCT)
TAG_REQ = 1
TAG_RESP = 2
MAX_CALL_ID = (1 << 16) - 1

FIELD_FUNC = "f"
FIELD_STATUS = "s"
FIELD_DATA = "d"
FIELD_ERROR = "m"

RES_OK = 1
RES_FALSE = 0


STATISTICS={}

class ErrorMsg(Exception):
    def __init__(self, errcode):
        self.errcode = errcode


class AbsExport(object):
    def on_close(self, process):
        pass


class Processer(object):
    """  """
    PRE = 'rc_'

    def __init__(self, gw_mgr, gwid, pid, addr, route_id):
        self.gw_mgr = gw_mgr
        self.gwid = gwid
        self.pid = pid
        self.addr = addr
        self.route_id = route_id
        self.export = None
        self.msgs = Queue()
        self.closing = False
        self._handle_task = spawn(self._handle)
        self._lock = None
        self._call_id = iter_id_func(end=MAX_CALL_ID)
        self._waits = {}  # key=func_id, value=AsyncResult
        

    def __enter__(self):
        if self._lock:
            self._lock.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._lock:
            self._lock.release()

    @property
    def closed(self):
        return self._handle_task is None

    @property
    def player_id(self):
        try:
            return self._player_id
        except AttributeError:
            p = getattr(self.export, 'player', None)
            if not (p and p.id):
                return None
            self._player_id = p.id
            return self._player_id

    def set_export(self, export):
        self.export = export

    def set_lock(self, lock):
        self._lock = lock

    def close(self, client=True):
        """ 关闭
        @params:
            client: 是否通知客户端断开
        """
        if not self._handle_task:
            return
        _task = self._handle_task
        self._handle_task = None

        def _close():
            self.msgs.put(None)
            self.gw_mgr.del_process(self.gwid, self.pid)
            spawn_later(0.2, _task.kill)
        if client:
            spawn(self.close_client)
            self.export = None
        _close()

    def force_close(self):
        """ 服务器强制网关断开连接 """
        pass

    def getProcesserInfo(self):
        mid = next(self._call_id)
        return self.gwid, self.pid, self.route_id, mid

    def call(self, fname, data, noresult=False, timeout=None):
        """ server -> client: rpc call """
        gw = self.gw_mgr.rpc_gws[self.gwid]
        data = ujson.dumps({FIELD_FUNC: fname,
                           FIELD_STATUS: 1,
                           FIELD_DATA: data,
                           FIELD_ERROR: ''})
        mid = next(self._call_id)
        gw.send(self.pid, self.route_id, b'%s%s' % (struct.pack(DATA_HEAD_STRUCT, TAG_REQ, mid), bytes(data, 'utf-8')))
        if noresult:
            return
        result = AsyncResult()
        self._waits[mid] = result
        return result.wait(timeout)

    def resp(self, mid, fname, status, msg, error_id):
        """ client -> server: response """
        gw = self.gw_mgr.rpc_gws[self.gwid]
        if status == RES_OK:
            data = ujson.dumps({FIELD_FUNC: '',  # fname,
                               FIELD_STATUS: status,
                               FIELD_DATA: msg,
                               FIELD_ERROR: ''})
        else:
            data = ujson.dumps({FIELD_FUNC: '',  # fname,
                               FIELD_STATUS: status,
                               FIELD_DATA: '',
                               FIELD_ERROR: error_id})
        gw.send(self.pid, self.route_id, b'%s%s' % (struct.pack(DATA_HEAD_STRUCT, TAG_RESP, mid), bytes(data, 'utf-8')))

    def router(self, addr_fnams):
        """ 添加gateway route """
        gw = self.gw_mgr.rpc_gws[self.gwid]
        gw.router(self.pid, addr_fnams)

    def remove_router(self, addr):
        """ 移除gateway route """
        log.debug('[gateway]remove_router:%s', addr)
        gw = self.gw_mgr.rpc_gws[self.gwid]
        gw.RRouter(self.pid, addr)

    def close_client(self):
        """ 服务器主动通知关闭连接 """
        gw = self.gw_mgr.rpc_gws[self.gwid]
        if not gw.stoped:
            gw.CClient(self.pid, _no_result=1)
            # gw.CStop(_no_result=1)

    def connect(self, host, port):
        """ 切换连接其它服 """
        self.closing = True  # 标识准备关闭,
        gw = self.gw_mgr.rpc_gws[self.gwid]
        gw.Connect(self.pid, '%s:%d' % (host, port))
        spawn_later(5, self.close, client=False)

    def _handle_exception(self, mid, fname, err):
        """ 发送异常消息 """
        try:
            self.resp(mid, fname, RES_FALSE, '', int(err))
        except TypeError:
            log.log_except("[gateway]_handle_exception error:mid(%s) fname(%s) err(%s)", mid, fname, err)

    def _handle_response(self, mid, params):
        log.debug("_handle_response(%s):procId(%d):%s", self.player_id, mid, params)
        result = self._waits.get(mid, None)
        if not result:
            return
        if params:
            rs = params[FIELD_DATA]
            result.set(rs)
        else:
            result.set()

    def _handle_request(self, tag, procId, params):
        """ 消息处理 """
        # log.debug("_handle_request(%s):tag(%d):procId(%d):%s", self.player_id, tag, procId, params)
        fname = params[FIELD_FUNC]
        func = getattr(self.export, '%s%s' % (self.PRE, fname), None)

        if func is None:
            print("======找不到协议=====",fname)
            self._handle_exception(procId, fname, EC_NOFOUND)
            return

        st=time.time()
        try:
            kw = params[FIELD_DATA]
            with self:
                if kw is not None: rs = func(**kw)
                else: rs = func()
            if rs is None:
                log.debug("_handle_resp(%s):tag(%d):procId(%d): ok(%s) data(%s)", self.player_id, tag, procId, 1, rs)
                return
            ok, data = rs
            # log.debug("_handle_resp(%s):tag(%d):procId(%d): ok(%s) data(%s)", self.player_id, tag, procId, ok, data)
            if not ok:
                self._handle_exception(procId, fname, data)
            else:
                if data is None:
                    data = '[]'
                self.resp(procId, fname, RES_OK, data, 0)
        except GreenletExit:
            log.error("[Processer(%s-%s)] stoped. _handle_msg:func(%s)", self.pid, self.player_id, fname)
        except:
            log.log_except("_handle_msg:func(%s) %s", fname, params)
            self._handle_exception(procId, fname, EC_VALUE)
        
        
        et=time.time()

        us=et-st
        if fname not in STATISTICS:
            STATISTICS[fname]={"max":us,"avg":us,"num":1,"tot":us,"n":fname}
        else:
            max=STATISTICS[fname]["max"]
            if us>max:
                max=us
            STATISTICS[fname]["num"]+=1
            STATISTICS[fname]["max"]=max
            STATISTICS[fname]["avg"]=int((STATISTICS[fname]["avg"]+us)/2)
            STATISTICS[fname]["tot"]=STATISTICS[fname]["num"]*STATISTICS[fname]["avg"]
        


    def handle(self, msg):
        self.msgs.put(msg)

    def _handle(self):
        try:
            while 1:
                msg = self.msgs.get()
                if msg is None:
                    break
                tag, procId = struct.unpack(DATA_HEAD_STRUCT, msg[:DATA_HEAD_LEN].encode(encoding="utf-8"))
                params = ujson.loads(msg[DATA_HEAD_LEN:])
                if tag == TAG_RESP:
                    self._handle_response(procId, params)
                    # spawn(self._handle_response, procId, params)
                else:
                    self._handle_request(tag, procId, params)
                    # spawn(self._handle_request, tag, procId, params)
        finally:
            if self.export:
                spawn(self.export.on_close, self)
                self.export = None


class Owner(object):
    """  """
    def gw_open(self, p):
        pass


class GateWay(object):
    """ gw代理 """
    def __init__(self, mgr, gwid, rpc_gw, loop_time=0.01):
        self.gwid = gwid
        self.mgr = mgr
        self.rpc_gw = rpc_gw
        self.sends = []
        self.resps = []
        self.resp_and_sends = []
        self.loop_time = loop_time
        self.router = rpc_gw.router
        self.CClient = rpc_gw.CClient
        self.RRouter = rpc_gw.RRouter
        self.Connect = rpc_gw.Connect
        self.CStop = rpc_gw.Stop

    

    @property
    def stoped(self):
        return self._loop_task is None

    def start(self):
        self._loop_task = spawn(self.loop)
        
    def stop(self):
        if self.stoped:
            return
        self._loop_task.kill(block=False)
        self._loop_task = None
        self.close_processers()


    def on_close(self, rpc=None):
        """ 网关断开 """
        log.error('******网关断开连接,将通知所有Processer')
        self.stop()

    def close_processers(self):
        for p in self.mgr.iter_gw_processers(self.gwid):
            self.mgr.del_process(self.gwid, p.pid)
            spawn(p.close, client=False)

    def flush(self):
        d, self.resp_and_sends = self.resp_and_sends, []
        #log.info('*******:%s', d)
        self.rpc_gw.RespAndSends(d, _no_result=1)

    def loop(self):
        try:
            while 1:
                sleep(self.loop_time)
                if not self.resp_and_sends:
                    continue
                self.flush()
        finally:
            spawn(self.stop)

    def send(self, *data):
        """ 主动推送消息 """
        self.resp_and_sends.append(data)

    def broadcast(self, group, data):
        self.rpc_gw.GameBroadcast(group, data, _no_result=1)

class GateWayMgr(AbsExport):
    _rpc_name_ = 'gw'
    RPC_SERVER_NAME = "gw"
    GWID = '_gwid_'

    def __init__(self, owner):
        self.owner = owner
        self.rpc_gws = {}  # {gwid: gw}
        self.processers = {}  # key=(gwid, pid) value=processer
        spawn(self.statisticslog)




    def statisticslog(self):
        global STATISTICS
        count=0
        Game.glog.log2File("STATISTICSLOGavg", "%s" % "----------------")
        Game.glog.log2File("STATISTICSLOGmax", "%s" % "----------------")
        Game.glog.log2File("STATISTICSLOGnum", "%s" % "----------------")
        Game.glog.log2File("STATISTICSLOGtot", "%s" % "----------------")
        while 1:
            sleep(300)
            x=list(STATISTICS.values())

            x.sort(key=lambda x: x["avg"], reverse=True)
            for v in x[:50]:
                Game.glog.log2File("STATISTICSLOGavg", "%s|%s" % (v["avg"],v["n"],))

            Game.glog.log2File("STATISTICSLOGavg", "%s" % "===")
            
            x.sort(key=lambda x: x["max"], reverse=True)
            for v in x[:50]:
                Game.glog.log2File("STATISTICSLOGmax", "%s|%s" % (v["max"],v["n"],))

            Game.glog.log2File("STATISTICSLOGmax", "%s" % "===")
            
            x.sort(key=lambda x: x["num"], reverse=True)
            for v in x[:50]:
                Game.glog.log2File("STATISTICSLOGnum", "%s|%s" % (v["num"],v["n"],))

            Game.glog.log2File("STATISTICSLOGnum", "%s" % "===")
            
            x.sort(key=lambda x: x["tot"], reverse=True)
            for v in x[:50]:
                Game.glog.log2File("STATISTICSLOGtot", "%s|%s" % (v["tot"],v["n"],))

            Game.glog.log2File("STATISTICSLOGtot", "%s" % "===")
            

            
            count+=1
            if count==12:
                Game.glog.log2File("STATISTICSLOGavg", "%s" % "----------------")
                Game.glog.log2File("STATISTICSLOGmax", "%s" % "----------------")
                Game.glog.log2File("STATISTICSLOGnum", "%s" % "----------------")
                Game.glog.log2File("STATISTICSLOGtot", "%s" % "----------------")
                count=0
                STATISTICS={}


    def get_let_gw(self):
        """ 获取当前微线程的远程网关对象 """
        svc = get_service()
        return getattr(svc, self.RPC_SERVER_NAME)

    def get_let_gwid(self):
        """ 获取当前微线程的网关id """
        return getattr(get_service(), self.GWID, None)

    def get_let_processer(self, pid, gwid=None):
        """ 获取processer """
        if gwid is None:
            gwid = getattr(get_service(), self.GWID, None)
        return self.processers.get((gwid, pid))

    def reg(self, rpc_gw, gwid, _proxy=True):
        """ 注册网关的远程对象 """
        log.info('[gateway]reg:gwid(%s)', gwid)
        rpc_gw.sub_close(self.gw_close)
        svc = get_service()
        gw = GateWay(self, gwid, rpc_gw)
        gw.start()
        # svc.reg_proxy(self.RPC_SERVER_NAME, gw)
        setattr(svc, self.RPC_SERVER_NAME, gw)
        setattr(svc, self.GWID, gwid)
        self.rpc_gws[gwid] = gw

    def del_process(self, gwid, pid):
        return self.processers.pop((gwid, pid), None)

    def gw_close(self, rpc_gw):
        """ 网关断开 """
        svc = rpc_gw.get_service()
        close_gwid = getattr(svc, self.GWID)
        log.warning('网关(%s - %s)断开', rpc_gw.get_addr(), close_gwid)
        self.rpc_gws.pop(close_gwid)
        for key in self.processers.values():
            gwid, pid = key
            if gwid != close_gwid:
                continue
            p = self.del_process(gwid, pid)
            if p:
                spawn(p.close, client=False)

    def send(self, pid, msg):
        """ client -> server """
        p = self.get_let_processer(pid)
        p.handle(msg)

    def sends(self, msgs):
        """ client -> server """
        gwid = self.get_let_gwid()
        for (pid, msg) in msgs:
            p = self.get_let_processer(pid, gwid=gwid)
            if not p:
                continue
            p.handle(msg)
        #log.debug("[gateway]sends")

    def open(self, pid, addr, route_id):
        """ 开启一个新连接 """
        gwid = self.get_let_gwid()
        if not gwid:
            log.error("[gateway]open(%s-%s) before reg", pid, addr)
            return
        else:
            log.debug("[gateway]open:%s-%s", pid, addr)
        p = Processer(self, gwid, pid, addr, route_id)
        self.processers[(gwid, pid)] = p
        self.owner.gw_open(p)

    def close(self, pid):
        """ 关闭一个连接 """
        log.debug("[gateway]close:%s", pid)
        gwid = self.get_let_gwid()
        p = self.del_process(gwid, pid)
        if p and not p.closing:
            p.close(client=False)

    def iter_gw_processers(self, gwid):
        """ 遍历gateway对应Processer """
        for (pgwid, pid), p in self.processers.items():
            if gwid != pgwid:
                continue
            yield p

    def broadcast(self, fname, data, sendInfo):
        data = ujson.dumps({FIELD_FUNC: fname,
                           FIELD_STATUS: 1,
                           FIELD_DATA: data,
                           FIELD_ERROR: ''},
                          ensure_ascii=True)

        for gwid, group in sendInfo.items():
            gw = self.rpc_gws.get(gwid)
            if not gw:
                continue
            gw.broadcast(group, data)








