#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import time

from game.common import utility
from game.define import msg_define, constant

from corelib.frame import Game
from corelib.gtime import get_days

#角色基础信息
class PlayerBase(utility.DirtyFlag):
    def __init__(self, owner):
        utility.DirtyFlag.__init__(self)
        self.owner = owner  # 拥有者
        self.pid = None  # 玩家
        self.name = ''  # 名字
        self.renameCount = 0  # 改名计数器
        self.fa = 0 #战力
        self.lv = 1 #等级 默认1级
        self.sex = 0 #性别 0=? 1=男 2=女
        self.exp = 0 # 当前经验值

        self.CliConfig = "" #客户端配置
        self.mymergetime = 0  # 合服时间戳

        self.save_cache = {} #存储缓存

        self.serverOpenTime = 0
        self.serverMergeTime = 0

    def markDirty(self):
        utility.DirtyFlag.markDirty(self)
        if self.owner:
            self.owner.markDirty()

    def uninit(self):
        pass

    #存库数据
    def to_save_dict(self, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            self.save_cache = {}
            self.save_cache["pid"] = self.pid
            self.save_cache["name"] = self.name
            if self.renameCount:
                self.save_cache["renameCount"] = self.renameCount
            if self.mymergetime:
                self.save_cache["mymergetime"] = self.mymergetime
            self.save_cache["fa"] = self.fa
            self.save_cache["lv"] = self.lv
            self.save_cache["sex"] = self.sex
            self.save_cache["exp"] = self.exp

            if self.CliConfig:
                self.save_cache["CliConfig"] = self.CliConfig

        return self.save_cache

    #读库数据初始化
    def load_from_dict(self, data):
        self.pid = data.get("pid", 0)
        self.name = data.get("name", "")
        self.renameCount = data.get("renameCount", 0)
        self.mymergetime = data.get("mymergetime", 0)
        self.fa = data.get("fa", 0)  # 战力
        self.lv = data.get("lv", 1)  # 等级 默认1级
        self.sex = data.get("sex", 0)  # 性别 0=? 1=男 2=女
        self.exp = data.get("exp", 0)  # 当前经验值

        self.CliConfig = data.get("CliConfig", "")

    def to_wee_hour_data(self):
        init_data = {}
        
        kv={}
        retval=[]
        for v in Game.res_mgr.res_cycle.values():
            kv[v.activityID]=True

        serverInfo = self.GetServerInfo()
        
        for v in kv.keys():
            res=Game.res_mgr.res_activity.get(v)
            retval.append({"activityID":v,"cycleFuncID":res.getCycleFuncID(serverInfo),"endtime":res.getCycleEndTime(serverInfo)})    

        init_data["cycle"]=retval

        return init_data
    
    #登录初始化下发数据
    def to_init_data(self):
        serverInfo = Game.rpc_server_info.GetServerInfo()
        mergetime = serverInfo.get("mergetime", 0)

        if mergetime and mergetime != self.mymergetime:
            print("===========================================================")
            print("MergeTime", "%s|%s|%s" % (self.owner.id, mergetime, self.mymergetime))
            Game.glog.log2File("MergeTime", "%s|%s|%s" % (self.owner.id, mergetime, self.mymergetime))
            print("===========================================================")

            self.mymergetime = mergetime

            # self.owner.charge.FirstCharge=[]
            # self.owner.charge.FirstChargeRMB=0
            # self.owner.charge.FirstChargeFlag += 1 #不确定要不要
            # self.owner.charge.markDirty()

            self.owner.arena.mergeClean()

            self.owner.levelContest.mergeClean()
            self.owner.fuli.mergeClean()


        init_data = {}
        init_data["pid"] = self.owner.id
        init_data["name"] = self.name
        init_data["renameCount"] = self.renameCount
        init_data["fa"] = self.fa
        init_data["lv"] = self.lv
        init_data["sex"] = self.sex
        init_data["exp"] = self.exp
        init_data["CliConfig"] = self.CliConfig

        init_data["newTime"] = self.owner.data.newTime
        init_data["curTimeZone"] = Game.get_cur_time_zone()

        kv={}
        retval=[]
        for v in Game.res_mgr.res_cycle.values():
            kv[v.activityID]=True

        serverInfo = self.GetServerInfo()
        
        for v in kv.keys():
            res=Game.res_mgr.res_activity.get(v)
            retval.append({"activityID":v,"cycleFuncID":res.getCycleFuncID(serverInfo),"endtime":res.getCycleEndTime(serverInfo)})    

        init_data["cycle"]=retval

        return init_data

    def SetCliConfig(self, CliConfig):
        self.CliConfig = CliConfig
        self.markDirty()

    def SetSex(self, sex):
        self.sex = sex
        self.markDirty()

    def GetSex(self):
        return self.sex

    def SetName(self, name):
        if name != "":
            self.renameCount += 1
        self.name = name
        self.markDirty()

    def GetLv(self):
        return self.lv

    def SetLv(self, lv):
        self.lv = lv
        self.markDirty()
        #抛出角色升级消息
        self.owner.safe_pub(msg_define.MSG_ROLE_LEVEL_UPGRADE, self.lv)
        #抛出change
        self.owner.safe_pub(msg_define.MSG_ROLE_XLV_UPGRADE)
        # 更新等级榜
        self.owner.rank.uploadRank(constant.RANK_TYPE_LV)

    def GetExp(self):
        return self.exp

    def SetExp(self, exp):
        self.exp = exp
        self.markDirty()

    def SetFightAbility(self, fa):
        self.fa = fa
        self.markDirty()
        #更新战力榜
        self.owner.rank.uploadRank(constant.RANK_TYPE_FA)

    def GetFightAbility(self):
        return self.fa

    def GetServerInfo(self):
        #读取服务器信息
        if not self.serverOpenTime and not self.serverMergeTime:
            server_info = Game.rpc_server_info.GetPlayerLoginInitData()
            self.serverOpenTime = server_info.get("opentime", 0)
            self.serverMergeTime = server_info.get("mergetime", 0)

        server_info = {}
        server_info["opentime"] = self.serverOpenTime
        server_info["mergetime"] = self.serverMergeTime
        return server_info

    def GetServerOpenDay(self):
        """获取开服天数"""
        day = get_days(self.serverOpenTime) + 1
        return day

    def GetServerMergeDay(self):
        """获取合服天数"""
        day = get_days(self.serverMergeTime) + 1
        return day
