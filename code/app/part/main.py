#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import sys
from gevent import sleep

from corelib import log, spawn
from corelib.process import BaseApp, daemon
from corelib.frame import AbsPartApplication

import config


class Application(BaseApp, AbsPartApplication):

    def __init__(self):
        BaseApp.__init__(self)
        AbsPartApplication.__init__(self, config)
        self.restarted = False

    def start(self):
        self.init_frame()
        self.frame.start()

        while 1:
            try:
                self._waiter.wait()
                break
            except KeyboardInterrupt:
                log.info('app stoped:KeyboardInterrupt')
            except SystemExit:
                log.info('app stoped:SystemExit')
            except:
                log.log_except()
                break
            log.info('spawn app stop')
            spawn(self.stop)
            sleep(0.2)
        cmd = ' '.join(list(map(str, [sys.executable,] + sys.argv)))
        log.info('*****app(%s) stoped', cmd)
        self.stop()

        #守护进程方式,重启服务
        if self.restarted and hasattr(self, 'daemon_runner'):
            self.daemon_runner.domain_restart()

    def stop(self):
        if self.stoped:
            return
        self.stoped = True
        self._waiter.set()

    def restart(self, m, msg=None):
        """ 过min分钟后,自动重启, """
        spawn(self._restart, m, msg)

    def _restart(self, m, msg, restart=True):
        if restart:
            amsg = '重启'
        else:
            amsg = '关闭维护'
        if msg is None:
            msg = '服务器将在%%(min)s分钟后%s, 谢谢!' % amsg

        sleep(1)
        self.restarted = restart
        self._waiter.set()

def main():
    log.info('[part] main:%s', sys.argv)
    app = Application()
    daemon(app)

if __name__ == '__main__':
    main()

