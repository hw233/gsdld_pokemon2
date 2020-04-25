#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os
import time
import functools

from daemon import daemon, runner
from daemon.runner import make_pidlockfile, DaemonRunnerStopFailureError, DaemonRunner
from gevent import sleep, getcurrent, signal_handler

from corelib.gtime import strftime
from corelib import log

class MyDaemonRunner(DaemonRunner):
    START_CMDS = ('start', 'restart')
    def __init__(self, app):
        for cmd in app.EXTRA_CMDS:
            DaemonRunner.action_funcs[cmd] = getattr(app, cmd)
        self.parse_args()
        self._stdout_path = app.stdout_path
        self._stdin_path = app.stdin_path
        self._stderr_path = app.stderr_path

        with open(app.stdin_path, 'a'):
            pass

        if self.action not in self.START_CMDS:
            app.stdin_path = '/dev/null'
            app.stdout_path = '/dev/null'
            app.stderr_path = '/dev/null'
        elif self.action in self.START_CMDS:
            self.pidfile = make_pidlockfile(
                app.pidfile_path, app.pidfile_timeout)
            status = self._get_status()
            if status[0] == 1:
                print('app is running.')
                raise ValueError('app is running')

            self._rename_log(app.stdout_path)
            self._rename_log(app.stderr_path)

        #主微线程
        self._main_let = getcurrent()
        def _wrap_run(func):
            """守护模式后,没有下面sleep,
            某些(admin进程在socket.getaddrinfo)会在卡死
            怀疑是gevent微线程切换问题,暂时这么处理
            """
            def _func(*args, **kw):
                sleep(0.05)
                return func(*args, **kw)
            return _func
        app.run = _wrap_run(app.start)
        DaemonRunner.__init__(self, app)
        self._init_signal()

    def _open_streams_from_app_stream_paths(self, app):
        """ Open the `daemon_context` streams from the paths specified.

            :param app: The application instance.

            Open the `daemon_context` standard streams (`stdin`,
            `stdout`, `stderr`) as stream objects of the appropriate
            types, from each of the corresponding filesystem paths
            from the `app`.
            """
        self.daemon_context.stdin = open(app.stdin_path, 'rt')
        self.daemon_context.stdout = open(app.stdout_path, 'w+t')
        self.daemon_context.stderr = open(app.stderr_path, 'w+t')

    def _init_signal(self):
        """ 初始化signal """
        SIGNAL_MAP = daemon.make_default_signal_map()
        log.debug('init_signal:%s', SIGNAL_MAP)
        self.daemon_context.signal_map = SIGNAL_MAP
        self.daemon_context.terminate = self.terminate

    def terminate(self, signal_number, stack_frame):
        """ 收到关闭的信号,在主线程上抛出异常 """
        log.warning("Terminating on signal %r", signal_number)
        exception = SystemExit(
            "Terminating on signal %(signal_number)r"
            % vars())
        self._main_let.throw(exception)

    def _rename_log(self, log_path):
        """ 备份之前的log文件,名字后加上当前时间 """
        import shutil
        from os.path import exists, basename, dirname, join
        if exists(log_path):
            dir_path, name = dirname(log_path), basename(log_path)
            name += '.' + strftime(fmt='%Y%m%d-%H%M%S')
            try:
                shutil.move(log_path, join(dir_path, name))
            except shutil.Error:
                pass


    def domain_restart(self):
        """ 重启守护进程 """
        import os
        config = sys.modules['config']
        argv = os.environ['APP_ARGV']
        self.pidfile.break_lock()
        restart_path = os.path.join(config.root_path, 'restart.py')
        if not os.path.exists(restart_path):
            restart_path = os.path.join(config.root_path, 'restart.pyc')

        args = '%s %s' % (sys.executable, argv)
        log.info('重启服务:%s', args)
        os.system('python %s %s' % (restart_path, args))


    def _run(self):
        self.app.start()

    def _get_status(self):
        if not self.pidfile.is_locked():
            return 0, None
        elif runner.is_pidfile_stale(self.pidfile):
            pid = self.pidfile.read_pid()
            self.pidfile.break_lock()
            return -1, pid
        else:
            return 1, None

    def _status(self):
        status, pid = self._get_status()
        if status == 0:
            print("app is stoped.")
        elif status == -1:
            print("pidfile existed but app(%s) is stoped!" % pid)
        else:
            print('app is running.')

    def _reload(self):
        if not hasattr(self.app, 'reload'):
            return
        pid = self.pidfile.read_pid()
        self.app.reload(pid)

    def _log(self, err=False):
        print('log path:\n%s\n%s' %(self._stdout_path, self._stderr_path))
        tail_cmd = 'tail -F %s'
        if err:
            tail_cmd = tail_cmd % (self._stderr_path, )
        else:
            tail_cmd = tail_cmd % (self._stdout_path, )
        print(tail_cmd)
        rs = None
        try:
            rs = os.system(tail_cmd)
        except:
            log.log_except()
        print('exit:', rs)

    def _vim(self):
        """ 编辑log """
        tail_cmd = 'vim %s'
        tail_cmd = tail_cmd % (self._stdout_path, )
        print(tail_cmd)
        os.system(tail_cmd)


    def _terminate_daemon_process(self):
        """ Terminate the daemon process specified in the current PID file.
        """
        if 1:
            DaemonRunner._terminate_daemon_process(self)
        else: #用app.stop
            import config
            from grpc import get_proxy_by_addr, uninit
            app = get_proxy_by_addr(config.admin_addr, 'app')
            app.stop(_no_result=True)
            sleep(0.5)
            del app
            uninit()
        timeout = 60
        while timeout > 0:
            timeout -= 1
            time.sleep(1)
            if not self.pidfile.is_locked():
                break
        if timeout <= 0:
            sys.exit('stop error:Timeout')

    #命令
    DaemonRunner.action_funcs['vim'] = _vim
    DaemonRunner.action_funcs['log'] = _log
    DaemonRunner.action_funcs['err'] = functools.partial(_log, err=True)
    DaemonRunner.action_funcs['run'] = _run
    DaemonRunner.action_funcs['status'] = _status
    DaemonRunner.action_funcs['reload'] = _reload

def mydaemon(app):
    def gevent_set_signal_handlers(signal_handler_map):
        signals = {}
        for (signal_number, handler) in signal_handler_map.items():
            #gevent.signal have not params, but, signal handler want params(signal_number, stack_frame)
            if callable(handler):
                signals[signal_number] = signal_handler(signal_number, handler, signal_number, None)
        app.signals = signals
        #use gevent signal to register terminate
    daemon.set_signal_handlers = gevent_set_signal_handlers

    myrunner = MyDaemonRunner(app)
    app.daemon_runner = myrunner
    #daemon.close_file_descriptor_if_open may be crack, don't use it
    myrunner.daemon_context.files_preserve = list(range(0, 1025))
    try:
        myrunner.do_action()
    except DaemonRunnerStopFailureError as err:
        log.exception('do_action')
        if not myrunner.pidfile.is_locked():
            print('pidfile no found, app is running?')
    except SystemExit as err:
        log.warning('app SystemExit:%s', err)
        raise
    except:
        log.exception('do_action')
