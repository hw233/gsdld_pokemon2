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

from game.core.cycleData import CycleDay, ActivityCycleData


class PlayerNiudan(utility.DirtyFlag):
    def __init__(self, owner):
        utility.DirtyFlag.__init__(self)
        self.owner = owner  # 拥有者

        self.cycleDay = CycleDay(self)
        self.activityCycleData = ActivityCycleData(self)
        self.RollNum = [] # 扭蛋次数 {"k":resid,"v":num}




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
            self.save_cache["activityCycleData"] = self.activityCycleData.to_save_bytes()
            self.save_cache["RollNum"] = self.RollNum

        return self.save_cache

    #读库数据初始化
    def load_from_dict(self, data):

        self.cycleDay.load_from_dict(data.get("cycleDay", ""))
        self.activityCycleData.load_from_dict(data.get("activityCycleData", ""))
        self.RollNum=data.get("RollNum", [])


    #登录初始化下发数据
    def to_init_data(self):

        init_data = {}


        init_data["xianshiniudanBaodi"] = self.getCycleBaodi(constant.ACTIVITY_XIANSHINIUDAN) #限时 保底-当前抽卡次数
        init_data["xianshiniudanReward"] = self.getCycleReward(constant.ACTIVITY_XIANSHINIUDAN) #限时 领奖 当前积分
        init_data["xianshiniudanNeeds"] = self.getCycleNeeds(constant.ACTIVITY_XIANSHINIUDAN) #限时 领奖 已经领奖idx
        
        # init_data["RollOneNum"] = self.getRollOneNum()

        xxx=self.getRollOneNum()
        freenum={}
        for k,v in Game.res_mgr.res_niudanSystem.items():
            onenum=xxx.get(k,0)
            sv=v.costFree-onenum
            if sv<0:
                sv=0
            freenum[k]=sv



        init_data["freenum"] = freenum


        


        return init_data

    #零点更新的数据
    def to_wee_hour_data(self):
        return self.to_init_data()


    # 角色下线时要做的清理操作
    def uninit(self):
        pass
    

    def getRollOneNum(self):
        return self.cycleDay.Query("RollOneNum", {})

    def setRollOneNum(self, obj):
        self.cycleDay.Set("RollOneNum", obj)

    def getCycleNeeds(self, actid):
        return self.activityCycleData.Query("CycleNeeds_"+str(actid), [])

    def setCycleNeeds(self, v, actid):
        self.activityCycleData.Set("CycleNeeds_"+str(actid), v, actid)

    def getCycleBaodi(self, actid):
        return self.activityCycleData.Query("CycleBaodi_"+str(actid), 0)

    def setCycleBaodi(self, v, actid):
        self.activityCycleData.Set("CycleBaodi_"+str(actid), v, actid)

    def getCycleReward(self, actid):
        return self.activityCycleData.Query("CycleReward_"+str(actid), 0)

    def setCycleReward(self, v, actid):
        self.activityCycleData.Set("CycleReward_"+str(actid), v, actid)

    def getRollNum(self):
        o={}
        for v in self.RollNum:
            o[v["k"]]=v["v"]


        
        return o

    def setRollNum(self, obj):
        self.RollNum=[]

        for k,v in obj.items():
            one={"k":k,"v":v}
            self.RollNum.append(one)
        

        self.markDirty()