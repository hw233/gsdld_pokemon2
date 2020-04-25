#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import random
import time

from game.common import utility
from game.define import msg_define, constant

from corelib.frame import Game
from corelib import spawn, spawn_later, gtime

import config
import copy

from game.core.cycleData import CycleDay


class PlayerZhuanpan(utility.DirtyFlag):
    def __init__(self, owner):
        utility.DirtyFlag.__init__(self)
        self.owner = owner  # 拥有者

        self.cycleDay = CycleDay(self)

        self.freeResetTime={} #免费重置时间 id:time.time()
        self.score={} #得分 resid:score
        self.rewardid ={} #已经领奖idx resid:[]




        self.save_cache = {} #存储缓存


    def markDirty(self):
        utility.DirtyFlag.markDirty(self)
        if self.owner:
            self.owner.markDirty()

    #存库数据
    def to_save_dict(self, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            self.save_cache = {}

            self.save_cache["cycleDay"] = self.cycleDay.to_save_bytes()

            self.save_cache["freeResetTime"] = utility.obj2list(self.freeResetTime)
            self.save_cache["score"] = utility.obj2list(self.score)
            self.save_cache["rewardid"] = utility.obj2list(self.rewardid)



        return self.save_cache

    #读库数据初始化
    def load_from_dict(self, data):

        self.cycleDay.load_from_dict(data.get("cycleDay", ""))

        self.freeResetTime = utility.list2obj(data.get("freeResetTime", []))
        self.score = utility.list2obj(data.get("score", []))
        self.rewardid = utility.list2obj(data.get("rewardid", []))

    #登录初始化下发数据
    def to_init_data(self):

        init_data = {}

        RewardData=self.getRewardData()
        
        for v in Game.res_mgr.res_zhuanpanSystem.values():
            if v.id not in RewardData:
                RewardData[v.id]={"disable":[],"data":{}}
                for vv in v.idxCanDisable.keys():
                    pool=[]
                    for k in Game.res_mgr.res_zhuanpanPool.values():
                        if k.sys==v.id and k.idx==vv:
                            value = (k.id, k.Weight)
                            pool.append(value)

                    
                    RewardData[v.id]["data"][vv]=utility.Choice(pool)

        
        self.setRewardData(RewardData)      


        init_data["RewardData"] = RewardData
        init_data["freeResetTime"] = self.freeResetTime
        init_data["score"] = self.score
        init_data["rewardid"] = self.rewardid


        return init_data

    #零点更新的数据
    def to_wee_hour_data(self):
        return self.to_init_data()


    # 角色下线时要做的清理操作
    def uninit(self):
        pass
    

    def getRewardData(self):
        return self.cycleDay.Query("RewardData",{})

    def setRewardData(self, v):
        self.cycleDay.Set("RewardData", v)


    def reset(self,resid):
        RewardData=self.getRewardData()
        RewardData.pop(resid,None)
        self.setRewardData(RewardData)

    def addscore(self,res):

        self.score[res.id]=self.score.get(res.id,0)+res.score
        self.markDirty()
