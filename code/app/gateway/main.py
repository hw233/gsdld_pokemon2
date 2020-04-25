#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import sys
import os
from os.path import join, dirname

from corelib import log
from corelib.process import LocalProcessMgr, BaseApp, daemon
import config


class Application(BaseApp):
    EXTRA_CMDS = ["go_get"]
    def __init__(self):
        BaseApp.__init__(self)
        self.proc_mgr = LocalProcessMgr()

    def start(self):
        self.stoped = False
        self._start_gw()
        try:
            while 1:
                if self._waiter.wait(2):
                    break
        except KeyboardInterrupt:
            pass
        except SystemExit:
            pass
        except:
            log.exception('app error')
        self._stop()

    def _start_gw(self):
        import SysSetting
        port = config.port
        gw_path = dirname(SysSetting.root_path)
        if sys.platform == 'win32':
            gw_exe = join(gw_path, config.win_exe)
        else:
            gw_exe = join(gw_path, config.linux_exe)
        addr = config.main_addr
        aes_key = config.aes_key
        conn_mode = config.conn_mode
        isSSL = getattr(config, "isSSL", 0)
        certFile = getattr(config, "certFile", "1_game.chinakinggame.com_bundle.crt")
        keyFile = getattr(config, "keyFile", "2_game.chinakinggame.com.key")
        # cmd = '%s -p %d -GAddr %s -ak %s' % (gw_exe, port, addr, aes_key)
        cmd = '%s -p %d -GAddr %s -ct %s -ssl %s -certFile %s -keyFile %s' % (gw_exe, port, addr, conn_mode, isSSL,
                                                                              certFile, keyFile)
        log.info('gateway:%s', cmd)
        stdin, stdout, stderr = sys.stdin.fileno(), sys.stdout.fileno(), sys.stderr.fileno()
        #golang default output to stderr,
        # self.proc_mgr.start_process(cmd, stdin=stdin, stdout=stdout, stderr=stdout)
        self.proc_mgr.start_process(cmd, stderr=None)

    def _stop(self):
        if self.stoped:
            return
        self.stoped = True
        self.proc_mgr.killall()

    def stop(self):
        self._waiter.set()

    def go_get(self, *args):
        """ 类似go get,先删除gopath/下的目录再执行go get """
        from shutil import rmtree
        from os.path import join, exists
        pkgs = [
            ('bitbucket.org/seewind/grpc', 'golang/grpc'),
            ('bitbucket.org/efun/gateway', ''),
        ]
        gopath = os.environ.get("GOPATH")
        #remove
        for root, pkg in pkgs:
            pkg_path = join(gopath, "src", root)
            log.info("remove:%s", pkg_path)
            if exists(pkg_path):
                rmtree(pkg_path)
            #go get
            cmd = "go get %s/%s" % (root, pkg)
            log.info("exec: %s", cmd)
            os.system(cmd)


def main():
    log.info('[gateway] start at:%s', config.port)
    app = Application()
    daemon(app)

if __name__ == '__main__':
    main()

