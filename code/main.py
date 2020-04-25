#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import gc
import sys
import os
import locale
from os.path import dirname, abspath

class SysSetting(object):
    """系统环境"""
    def __init__(self):
        self.app_argv = None #启动参数
        self.py_path = None #python目录
        self.executable = None #执行命令
        self.root_path = None #项目根目录
        self.lib_path = None #项目库目录

        self.init()

    def init(self):
        # wingIDE调试加载 必须在gevent path替换系统socket之前调用，否则会失效
        if sys.argv[-1] == 'subgame_debug':
            sys.argv.pop()
        try:
            print('启动wingide调试')
            import wingdbstub
        except ImportError:
            print('启动wingide调试失败')

        #减少周期性检查
        # sys.setswitchinterval() #3.2--
        # sys.setcheckinterval(1000) #2.x
        #启动参数
        self.app_argv = ' '.join(sys.argv[1:])
        #路径
        self.init_path()
        #启动gc
        gc.enable()

        from linux.block_fileon import BlockFileon
        BlockFileon()

    def init_path(self):
        """初始化路径"""
        executable = sys.executable
        self.py_path = dirname(executable) #python目录
        self.root_path = os.path.abspath(os.path.dirname(__file__))  #根目录

        if os.path.exists('main.py'):
            main_py = ' main.py'
        else:
            main_py = ' main.pyc'

        self.executable = executable + main_py
        self.lib_path = os.path.join(self.root_path, 'lib') #库目录
        sys.path.insert(0, self.lib_path) #加入库目录


message = u"""
启动方式:
.运行程序:
    python main.py <app> <start|stop|status|run>

.运行测试:
    python main.py test

.log 信息显示
    python main.py log <app>

.远程shell:
    python main.py tools shell ip port

.用meliae分析内存文件:
    python main.py tools meliae file_path
"""


def main():
    print(sys.path)
    sys_setting = SysSetting()
    if len(sys.argv) < 2:
        print(message)
        sys.exit(0)
    sys.modules['SysSetting'] = sys_setting
    from launch import Launcher
    launcher = Launcher()
    app = launcher.load_config()
    launcher.execute(app)

if __name__ == '__main__':
    main()
