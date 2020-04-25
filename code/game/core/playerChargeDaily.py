#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from game.common import utility
from game.define import msg_define, constant
from game import Game
import config
from corelib import spawn_later, log, spawn
import copy
import time
import math
from corelib.gtime import getZeroTime, zero_day_time, current_time


class PlayerChargeDaily(utility.DirtyFlag):
    def __init__(self, owner):
        utility.DirtyFlag.__init__(self)
        self.owner = owner  # 拥有者

        self.chargeids = [] #已经充值id
     
        self.save_cache = {} #存储缓存


    def markDirty(self):
        utility.DirtyFlag.markDirty(self)
        if self.owner:
            self.owner.markDirty()

    #存库数据
    def to_save_dict(self, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            self.save_cache = {}

            self.save_cache["chargeids"] = self.chargeids


        return self.save_cache

    #读库数据初始化
    def load_from_dict(self, data):
        self.chargeids = data.get("chargeids", [])

         

    #登录初始化下发数据
    def to_init_data(self):


        init_data = {}
        
        init_data["chargeids"] = self.chargeids

        return init_data
    
    def to_wee_hour_data(self):
        return self.to_init_data()


    def getreward(self,res):
        reward={}
        if res.id not in self.chargeids:
            self.chargeids.append(res.id)
            
            for k,v in res.reward.items():
                reward[k]=reward.get(k,0)+v*2
        else:
            for k,v in res.reward.items():
                reward[k]=reward.get(k,0)+v

        if len(self.chargeids)>=res.max:
            self.chargeids=[]

        self.markDirty()


        return reward



    def uninit(slef):
        pass