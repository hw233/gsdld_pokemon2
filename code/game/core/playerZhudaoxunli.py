#!/usr/bin/env python
# -*- coding:utf-8 -*-

from game.common import utility
from game.define import constant, msg_define
from game import Game
import random
import copy
import time
import math


class PlayerZhudaoxunli(utility.DirtyFlag):
    def __init__(self, owner):
        utility.DirtyFlag.__init__(self)
        self.owner = owner  # 拥有者
        self.time = 0 #分数
        self.data = [] #数据
     

        self.save_cache = {} #存储缓存
        # self.owner.sub(msg_define.MSG_ROLE_XLV_UPGRADE, self.event_lv_uprade)

    def markDirty(self):
        utility.DirtyFlag.markDirty(self)
        if self.owner:
            self.owner.markDirty()

    #存库数据
    def to_save_dict(self, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            self.save_cache = {}
            self.save_cache["time"] = self.time
            self.save_cache["data"] = self.data
        
        return self.save_cache

    #读库数据初始化
    def load_from_dict(self, data):
        self.time = data.get("time", 0) 
        self.data = data.get("data", []) 
        pass
  

    #登录初始化下发数据
    def to_init_data(self):
        init_data = {}
        init_data["time"] = self.time

        for k in Game.res_mgr.res_zhudaoxunliDay.keys():

            found=False
            for v in self.data:
                if v["qihao"]==k:
                    found=True
                    break
            
            if not found:
                self.data.append({"qihao":k,"score":0,"reward":[],"rewardVip":[],"isVip":0})
            
        init_data["data"] = self.data


        if self.time:
                
            nt=time.time()
            passtime=nt-self.time
            d=math.ceil(passtime/86400)

            reward={}
            for k,v in Game.res_mgr.res_zhudaoxunliReward.items():
                dayres=Game.res_mgr.res_zhudaoxunliDay.get(v.qihao)
                if dayres.end>=d:
                    continue
                
                data=None
                for vv in self.data:
                    if vv["qihao"]==v.qihao:
                        data=vv
                        break
                
                if k not in data["reward"] and data["score"]>=v.need:
                    data["reward"].append(k)
                    for rk,rv in v.reward.items():
                        reward[rk]=reward.get(rk,0)+rv
                    
                
                if k not in data["rewardVip"] and data["score"]>=v.need and data["isVip"]:
                    data["rewardVip"].append(k)
                    for rk,rv in v.rewardVip.items():
                        reward[rk]=reward.get(rk,0)+rv
                
            

            if reward:
                res = Game.res_mgr.res_mail.get(constant.MAIL_ID_ZHUDAOXUNLI_NOR_REWARD, None)
                Game.rpc_mail_mgr.sendPersonMail(self.owner.id, res.title, res.content, reward, _no_result=1)

        self.markDirty()

        return init_data

    def uninit(self):
        pass
        # self.owner.unsub(msg_define.MSG_ROLE_XLV_UPGRADE, self.event_lv_uprade)

    def addqihao(self,qihao):
        self.markDirty()
        for v in self.data:
            if v["qihao"]==qihao:
                v["isVip"]=1



    def addscore(self,score):
        self.markDirty()
        if not self.time:
            return
        
        nt=time.time()
        passtime=nt-self.time
        d=math.ceil(passtime/86400)

        # print("=@@=======",d)
        for k,v in Game.res_mgr.res_zhudaoxunliDay.items():
            if v.start<=d<=v.end:
                
                # print("=======!!=",d)

                for vv in self.data:
                    if vv["qihao"]==k:
                        vv["score"]+=score

                break
        
        
    def setreward(self,qihao,resid):
        for v in self.data:
            if v["qihao"]==qihao:
                v["reward"].append(resid)

        self.markDirty()
    
    def setrewardVip(self,qihao,resid):
        for v in self.data:
            if v["qihao"]==qihao:
                v["rewardVip"].append(resid)

        self.markDirty()
