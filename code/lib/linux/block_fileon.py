#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os, sys

class BlockFileon(object):


    def __init__(self):
        self.exe_make_blocking()
        pass

    def make_blocking(self, fd):
        import fcntl
        flags = fcntl.fcntl(fd, fcntl.F_GETFL)
        if flags & os.O_NONBLOCK:
            fcntl.fcntl(fd, fcntl.F_SETFL, flags & ~os.O_NONBLOCK)


    def exe_make_blocking(self):
        """ 防止出现 Resource temporarily unavailable 错误"""
        if sys.platform in ['win32']:
            return
        try:
            self.make_blocking(sys.stdin.fileno())
            self.make_blocking(sys.stdout.fileno())
            self.make_blocking(sys.stderr.fileno())
        except Exception as e:
            print('Content-Type: text/plain %r' % e)