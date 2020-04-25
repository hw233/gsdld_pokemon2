#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import sys, os
import imp

from os.path import exists, join, dirname, abspath, isfile, basename
from corelib import log

class APPConfig(object):
    """应用配置"""
    def __init__(self):
        self.app = None #应用类型
        self.cfg_path = '' #配置文件路径
        self.log_path = '' #日志路径
        self.pidfile = '' #进程文件
        self.app_path = '' #应用路径
        self.app_name = '' #应用名称
        self.sys_setting = sys.modules['SysSetting']
        self.res_path = '' #数据目录
        self.debug_key = ''

        #子进程调试参数 'player', 'union', 'glog', 'activity', ...
        if sys.platform in ['win32', 'cygwin']:
            self.debug_key = 'app_%s' % ('logic1', )
        #死循环检查功能
        self.use_dead_check = 0

    def update(self):
        """ 更新到全局模块 """
        sys.modules['config'] = self
        log.console_config(getattr(self, 'debug', False),
            log_file=getattr(self, 'log_file', None))

    def _get_config(self):
        config_root_path = join(dirname(self.sys_setting.root_path), 'config')
        if not exists(config_root_path):
            err = '全局配置目录不存在:%s' % config_root_path
            print(err)
            os.makedirs(config_root_path)

        config_name = sys.argv.pop(1)
        cfg_file = join(config_root_path, config_name +'.py')
        with open(cfg_file, 'rb') as f:
            cfg_data = f.read()
        cfg_path = join(config_root_path, config_name)
        if not exists(cfg_path):
            os.makedirs(cfg_path)
        return cfg_data, cfg_path, config_name

    def load_config(self):
        """ -c参数方式加载配置文件 """
        cfg_data, cfg_path, config_name = self._get_config()

        cfg_dict = {}
        exec(cfg_data, globals(), cfg_dict)

        #加载app config
        app = cfg_dict.get('app')
        if app is None:
            raise ValueError('app在config文件中未配置')

        app_path = join(self.sys_setting.root_path, 'app', app)
        if not exists(app_path):
            return False

        sys.path.insert(0, app_path)
        self.app_path = app_path
        self.app = app
        self.app_name = app
        self.res_path = join(dirname(self.sys_setting.root_path), 'data')
        #加载配置文件配置
        self.__dict__.update(cfg_dict)

        #配置文件所在目录,linux系统下用于存放配置、sock等文件
        self.cfg_path = cfg_path
        self.log_path = join(cfg_path, 'log')
        self.log_path = os.path.abspath(self.log_path)
        if not os.path.exists(self.log_path):
            os.makedirs(self.log_path)

        self.pidfile = join(cfg_path, 'pidfile.pid')
        self.pidfile = os.path.abspath(self.pidfile)
        pid_path = os.path.dirname(self.pidfile)
        if not os.path.exists(pid_path):
            os.makedirs(pid_path)

        return self.app


class Launcher(object):
    """启动器"""
    def __init__(self):
        self.sys_setting = sys.modules['SysSetting']

    def init_platform(self):
        """平台相关初始化"""
        #cygwin_check
        is_cygwin = False
        if sys.platform in ['win32', 'cygwin']:
            if sys.platform == 'cygwin':
                is_cygwin = True
            elif os.environ.get('GOOS', None) in ['linux']:
                is_cygwin = True
            elif os.environ.get('PWD', '').find('/') >= 0:
                is_cygwin = True

        ##死循环检查功能：只会在子应用进程安装
        config = sys.modules['config']
        if config.use_dead_check and sys.platform not in ('win32', ) and\
           config.app in ['web', 'logon', 'channel', 'battle', 'chat']:
            from gevent import spawn_later
            from corelib.tools import start_dead_check
            sec = 20
            spawn_later(sec, start_dead_check)
            print('install dead check after %d second' % sec)

    def load_config(self):
        """ 从网上下载配置 """
        config = APPConfig()
        sys.modules['config'] = config
        app = config.load_config()
        config.update()
        return app

    def execute(self, app):
        """执行"""
        app_config = sys.modules['config']
        app_path = app_config.app_path = join(self.sys_setting.root_path, 'app', app)

        self.init_platform() #平台相关初始化

        if os.path.exists(app_path):
            pass
        else:
            print('app(%s)no found!' % app)
            sys.exit(0)

        if exists(join(app_path, '__init__.py')) or exists(join(app_path, '__init__.pyc')):
            app_mod = __import__('%s.main' % app)
            main_md = app_mod.main
        elif exists(app_path):
            sys.path.insert(0, app_path)
            file, filename, _ = imp.find_module('main', [app_path])
            main_md = imp.load_module('main', file, filename, _)
        main_md.main()

