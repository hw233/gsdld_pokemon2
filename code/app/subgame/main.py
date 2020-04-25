#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import sys
import os

import config
import gevent
import gevent.event
from gevent import sleep

from corelib.process import BaseApp
from corelib import log
from corelib.frame import AbsSubApplication, Game, MSG_FRAME_START, MSG_FRAME_STOP

SUB_LOGIC = 1
SUB_UNION = 2

class Application(BaseApp, AbsSubApplication):

    def __init__(self, name, pid, addr):
        BaseApp.__init__(self)
        AbsSubApplication.__init__(self)
        # channel服务的ip和端口
        self.name = name
        self.addr = addr
        self.pid = pid  # 父进程id

    def start(self):
        log.info('[subgame] start:%s', self.addr)
        self.stoped = False

        self.init_frame(self.pid, self.addr)

        # 用来阻塞住主协程
        self._waiter_stoped = gevent.event.Event()
        try:
            while 1:
                try:
                    if self._waiter.wait():
                        break
                except KeyboardInterrupt:
                    pass
        except Exception as e:
            log.log_except('subgame app error:%s', e)
        try:
            self._stop()
        finally:
            self._waiter_stoped.set()

        sleep(2)
        sleep(0.5)

    def after_start(self):
        log.info('[subgame]app(%s) start', self.name)
        import grpc
        gl = dict(g=Game,)
        grpc.shell_locals.update(self.frame.names)
        grpc.shell_locals.update(gl)

        #初始化完成,抛出开始消息
        Game.safe_pub(MSG_FRAME_START)

    def before_stop(self):
        """ 准备关闭 """
        log.info('[subgame]app(%s) before_stop', self.name)
        Game.safe_pub(MSG_FRAME_STOP)

    def _stop(self):
        if self.stoped:
            return
        self.stoped = True
        log.info('subgame app(%s) stoped', self.name)
        self.frame.stop()

    def stop(self):
        """ 主进程通知子进程关闭 """
        self._waiter.set()
        self._waiter_stoped.wait()

    def init_config(self, config_dict):
        """ 初始化环境 """
        import config
        config.__dict__.update(config_dict)
        # 更新全局配置,log等级等
        config.update()

def main():
    #assert len(sys.argv) == 3
    log.info('[subgame] main:%s', sys.argv)
    app_name = sys.argv[-3]
    pid = int(sys.argv[-2])
    addr = sys.argv[-1]
    if isinstance(addr, str):
        addr = eval(addr)
    addr = tuple(addr)

    app = Application(app_name, pid, addr)
    try:
        app.start()
    except:
        log.log_except()

if __name__ == '__main__':
    main()
