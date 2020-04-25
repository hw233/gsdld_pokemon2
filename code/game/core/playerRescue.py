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

class PlayerRescue(utility.DirtyFlag):
    def __init__(self, owner):
        utility.DirtyFlag.__init__(self)
        self.owner = owner  # 拥有者

        self.cycleDay = CycleDay(self)
        self.keyinfo={} #id:{"num1":??,"num2":??,"num3":??,"num4":??,"num5":??}
        self.Ding=1 #丁 resid
        self.socre=0 #分数
        self.rewards=[] #已经领奖id

        self.ChargeEndTime={} #特权结束时间 {resid:结束时间戳秒}

        self.taskData=[] #{id:任务id,et:任务结束时间戳秒0代表未接,petuid:[]}
        self.taskInit=0 #自动生成标记

        self.lastSystemID=0 #最后获取线索resid
        self.lastIDX=0 #最后获取线索位置[1~5]
        self.lastmapSubId=0 #那时候关卡id



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

            self.save_cache["keyinfo"] = utility.obj2list(self.keyinfo)
            self.save_cache["Ding"] = self.Ding

            utility.lazy_save_cache(self,"rewards",self.save_cache)
            utility.lazy_save_cache(self,"score",self.save_cache)
            utility.lazy_save_cache(self,"taskData",self.save_cache)
            utility.lazy_save_cache(self,"taskInit",self.save_cache)

            self.save_cache["ChargeEndTime"] = utility.obj2list(self.ChargeEndTime)




        return self.save_cache

    #读库数据初始化
    def load_from_dict(self, data):

        self.cycleDay.load_from_dict(data.get("cycleDay", ""))

        self.keyinfo = utility.list2obj(data.get("keyinfo", []))
        self.Ding = data.get("Ding", 1)
        self.score = data.get("score", 0)
        self.rewards = data.get("rewards", [])
        self.taskData = data.get("taskData", [])
        self.taskInit = data.get("taskInit", 0)

        self.ChargeEndTime = utility.list2obj(data.get("ChargeEndTime", []))

    #登录初始化下发数据
    def to_init_data(self):

        init_data = {}

        if not self.taskInit:
            self.taskInit=1
            self.refreshTaskInit()
            self.markDirty()


        init_data["freshNum"] = self.getfreshNum()

        init_data["keyinfo"] = self.keyinfo
        init_data["Ding"] = self.Ding
        init_data["score"] = self.score
        init_data["rewards"] = self.rewards

        init_data["taskData"] = self.taskData
        

        init_data["ChargeEndTime"]=self.ChargeEndTime

        return init_data

    #零点更新的数据
    def to_wee_hour_data(self):
        return self.to_init_data()


    # 角色下线时要做的清理操作
    def uninit(self):
        pass
    

    def choose(self,star):
        ii=[]
        for k,v in Game.res_mgr.res_rescueTask.items():
            if star and v.star!=star:
                continue
            ii.append((k,v.w,))
        return utility.Choice(ii)

    def refreshTaskUser(self,gold):

        self.markDirty()

        v=self.getfreshNum()
        v+=1
        self.setfreshNum(v)

        if gold:
            v=self.getfreshGold()
            v+=1
            self.setfreshGold(v)

        
        sentMaxTask = Game.res_mgr.res_common.get("sentMaxTask")

        one=None
        xx=sentMaxTask.i
        for v in self.taskData:
            if not v["et"]:
                if not one:
                    one=v
                xx-=1
                v["id"]=self.choose(0)

        for _ in range(xx):
            v={"id":self.choose(0),"et":0,"petuid":[]}
            if not one:
                one=v

            self.taskData.append(v)
        
        nt=time.time()
        for k,v in self.ChargeEndTime.items():
            if v>=nt:
                cres=Game.res_mgr.res_chargeSent.get(k)
                star=cres.baodi.get(self.getfreshGold(),0)
                if star:
                    v["id"]=self.choose(star)
    
    def refreshTaskInit(self):
        sentInitTask = Game.res_mgr.res_common.get("sentInitTask")
        for resid in sentInitTask.arrayint1:
            v={"id":resid,"et":0,"petuid":[]}
            self.taskData.append(v)



                    
            

    def getfreshNum(self):
        return self.cycleDay.Query("freshNum",0)

    def setfreshNum(self, v):
        self.cycleDay.Set("freshNum", v)

    def getfreshGold(self):
        return self.cycleDay.Query("freshGold",0)

    def setfreshGold(self, v):
        self.cycleDay.Set("freshGold", v)


    def rescueSystemKey(self,idIdx):

        print("======rescueSystemKey====",idIdx)
    
        for k,v in idIdx.items():
            if v>5:
                v=1
            res=Game.res_mgr.res_rescueSystem.get(k)
            if res:
                n=getattr(res,"num"+str(v))
                if not n:
                    v=1
                    n=res.num1
                
                x = self.keyinfo.setdefault(k,{"num1":0,"num2":0,"num3":0,"num4":0,"num5":0,"ok":0})
                x["num"+str(v)]+=1



        self.markDirty()


    def rescueAuto(self):

        print("======rescueAuto====")

        xx=[]
        
        sentUseDing = Game.res_mgr.res_common.get("sentUseDing")
        okv=random.randint(0,10000)




        if okv<sentUseDing.i:
            v=Game.res_mgr.res_rescueSystem.get(self.Ding)

            if self.owner.map.passSubId>=v.mapsubid:

                ####################    

                x = self.keyinfo.setdefault(self.Ding,{"num1":0,"num2":0,"num3":0,"num4":0,"num5":0,"ok":0})
                
                if x["num1"]<v.num1:
                    xx.append((self.Ding,"num1",))
                if x["num2"]<v.num2:
                    xx.append((self.Ding,"num2",))
                if x["num3"]<v.num3:
                    xx.append((self.Ding,"num3",))
                if x["num4"]<v.num4:
                    xx.append((self.Ding,"num4",))
                if x["num5"]<v.num5:
                    xx.append((self.Ding,"num5",))

                if xx:
                    w=random.choice(xx)
                    self.keyinfo[w[0]][w[1]]+=1

                    self.lastSystemID=w[0]
                    self.lastIDX= int(w[1][3:])
                    self.lastmapSubId=self.owner.map.mapSubId


                    

                    self.markDirty()
                    return


        #订不到 随机
        xx=[]
        for k,v in Game.res_mgr.res_rescueSystem.items():
            if v.mapsubid>self.owner.map.passSubId:
                continue
            
            x = self.keyinfo.setdefault(k,{"num1":0,"num2":0,"num3":0,"num4":0,"num5":0,"ok":0})
            if x["num1"]<v.num1:
                xx.append((k,"num1",))
            if x["num2"]<v.num2:
                xx.append((k,"num2",))
            if x["num3"]<v.num3:
                xx.append((k,"num3",))
            if x["num4"]<v.num4:
                xx.append((k,"num4",))
            if x["num5"]<v.num5:
                xx.append((k,"num5",))

        
        if xx:
            w=random.choice(xx)
            self.keyinfo[w[0]][w[1]]+=1

            self.lastSystemID=w[0]
            self.lastIDX= int(w[1][3:])
            self.lastmapSubId=self.owner.map.mapSubId


            

        self.markDirty()

