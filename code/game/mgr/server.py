#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import time

from game.common import utility

from corelib.frame import Game, MSG_FRAME_STOP
from game.models.server import ModelServer
from corelib.gtime import get_days

class ServerInfo(utility.DirtyFlag):
    """服务器信息"""
    _rpc_name_ = 'rpc_server_info'

    def __init__(self):
        utility.DirtyFlag.__init__(self)
        self.data = None
        self.opentime = 0
        self.mergetime = 0

        self.profile_start = 0
        self.profile_end = 0

        self.save_cache = {}  # 存储缓存

        Game.sub(MSG_FRAME_STOP, self._frame_stop)

    def start(self):
        self.data = ModelServer.load(Game.store, ModelServer.TABLE_KEY)
        if not self.data:
            self.data = ModelServer()
            self.data.set_owner(self)
            self.opentime = int(time.time())
            self.data.save(Game.store, forced=True)
        else:
            self.data.set_owner(self)
        self.load_from_dict(self.data.dataDict)

    def _frame_stop(self):
        self.data.save(Game.store, forced=True, no_let=True)

    # 存库数据
    def to_save_dict(self, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            self.save_cache = {}
            self.save_cache["opentime"] = self.opentime
            self.save_cache["mergetime"] = self.mergetime
        return self.save_cache

    # 读库数据初始化
    def load_from_dict(self, data):
        self.opentime = data.get("opentime", 0)
        self.mergetime = data.get("mergetime", 0)
        if not self.opentime:
            self.opentime = int(time.time())
            self.markDirty()

    def GetPlayerLoginInitData(self):
        """获取玩家登陆时需要的数据"""
        resp = {}
        resp["opentime"] = self.opentime
        resp["mergetime"] = self.mergetime
        return resp

    def GetServerInfo(self):
        resp = {}
        resp["opentime"] = self.opentime
        resp["mergetime"] = self.mergetime
        return resp

    def SetServerOpenTime(self, iTime):
        self.opentime = iTime
        self.markDirty()

    def SetServerMergeTime(self, iTime):
        self.mergetime = iTime
        self.markDirty()

    def reloadConfig(self, tname):
        Game.res_mgr.loadByNames(tname)


    def doCommonProfileStart(self):
        self.profile_start = int(time.time())

        import GreenletProfiler
        GreenletProfiler.set_clock_type('cpu')
        GreenletProfiler.start()
        Game.glog.log2File("doCommonProfile", "%s|%s\n"%("start", self.profile_start))

    def doCommonProfileEnd(self):
        self.profile_end = int(time.time())

        import GreenletProfiler
        GreenletProfiler.stop()
        stats = GreenletProfiler.get_func_stats()
        stats.save('./callgrind_%s_%s.profile'%(self.profile_start, self.profile_end), type='callgrind')
        Game.glog.log2File("doCommonProfile", "%s|%s\n" % ("end", self.profile_end))

    def GetOpenTime(self):
        return self.opentime

    def GetOpenDay(self):
        """获取开服天数"""
        day = get_days(self.opentime) + 1
        return day

