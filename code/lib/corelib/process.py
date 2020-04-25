#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import sys
import errno
import subprocess, atexit

from os.path import join
from gevent.event import Event

from corelib import log

BUFSIZE = 1024 * 10

class LocalProcessMgr(object):
    def __init__(self, cwd=None):
        self.pids = {}
        atexit.register(self.killall)
        self.default_cwd = cwd

    @staticmethod
    def split_cmd(s):
        """
        str --> [], for subprocess.Popen()
        """
        SC = '"'
        a    = s.split(' ')
        cl = []
        i = 0
        m = 0
        while i < len(a) :
            if a[i] == '' :
                i += 1
                continue
            if a[i][0] == SC :
                n = i
                loop = True
                while loop:
                    if a[i] == '' :
                        i += 1
                        continue
                    if a[i][-1] == SC :
                        loop = False
                        m = i
                    i += 1
                cl.append((' '.join(a[n:m+1]))[1:-1])
            else:
                cl.append(a[i])
                i += 1
        return cl

    @property
    def count(self):
        return len(self.pids)

    def start_process(self, cmd, cwd=None, **kw):
        """ 启动进程 """
        executable = None
        if cwd is None:
            cwd = self.default_cwd
        if sys.platform == 'win32':
            pass
        else:
            cmd = self.split_cmd(cmd)
            #cmd = ["/bin/sh", "-c", cmd]
        kw.update(dict(args=cmd,
                cwd=cwd,
                executable=executable,
                bufsize=BUFSIZE,
                )
        )

        log.debug('启动子进程:%s', kw)
        popen = subprocess.Popen(**kw)
        self.pids[popen.pid] = popen
        return popen.pid

    def kill_process(self, pid):
        if pid in self.pids:
            popen = self.pids.pop(pid)
            if isinstance(popen, subprocess.Popen):
                try:
                    popen.kill()
                except Exception as e:
                    if hasattr(e, 'errno') and e.errno == errno.ESRCH:
                        pass
                    else:
                        log.error('kill subprocess error:%s - %s', type(e), e)

    def killall(self):
        log.info('进程退出，停止所有子进程')
        pids = list(self.pids.keys())
        while len(pids) > 0:
            pid = pids.pop()
            self.kill_process(pid)


class BaseApp(object):
    EXTRA_CMDS = []
    def __init__(self):
        self._exits = []
        self.stoped = False
        self._waiter = Event()
        sys.modules['app'] = self

    def start(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

    def sub_exit(self, func, *args, **kw):
        """ 注册监听进程退出消息 """
        self._exits.append((func, args, kw))

    def pub_exit(self):
        """ 进程准备退出 """
        for (func, args, kw) in self._exits:
            try:
                func(*args, **kw)
            except:
                log.log_except()

def daemon(app):
    sys.modules['app'] = app
    #win
    if sys.platform in ['win32', 'cygwin']:
        app.start()
        return
    #linux
    config = sys.modules['config']
    app_name = getattr(config, 'app_name', None)
    log_path = getattr(config, 'log_path', None)
    pidfile = getattr(config, 'pidfile', None)

    log.info('log_path:%s', log_path)
    app.stdin_path = join(log_path, '%s_in.log' % app_name)
    app.stdout_path = join(log_path, '%s_out.log' % app_name)
    app.stderr_path = join(log_path, '%s_err.log' % app_name)
    app.pidfile_path = pidfile
    app.pidfile_timeout = 3

    from linux.gdaemon import mydaemon
    mydaemon(app)