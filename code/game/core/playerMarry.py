#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import time
from game.common import utility
from corelib.frame import Game
from game.define import constant, msg_define

from game.core.cycleData import CycleDay

class PlayerMarry(utility.DirtyFlag):
    def __init__(self, owner):
        utility.DirtyFlag.__init__(self)
        self.owner = owner      # 拥有者
        self.marryId = 0        # 历史最高结婚档位
        
        self.isMarried = 0      # 是否已婚
        self.kind = 0           # 身份类型 1 丈夫 2 妻子
        self.spousePid = 0      # 对象pid

        self.marryTimes = 0     # 结婚次数
        self.marryTime = 0      # 结婚时间
        self.power = 0          # 亲密度
        self.powerEn = []        # 亲密度当前可操作数量 [{id,en,usetime}]
        self.powerMsg = []        # 亲密度普通消息 [{time,id,en}]
        self.powerMsgTrueLove = []        # 亲密度真爱消息 [{id,en,num, pid, name}]
        self.powerLvReward = []        # 已经领取等级奖励id

        self.cycleDay = CycleDay(self)

        self.save_cache = {}

    def markDirty(self):
        utility.DirtyFlag.markDirty(self)
        if self.owner:
            self.owner.markDirty()

    # 存库数据
    def to_save_dict(self, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            self.save_cache = {}
            if self.marryId:
                self.save_cache["id"] = self.marryId
            if self.isMarried:
                self.save_cache["married"] = self.isMarried
            if self.kind:
                self.save_cache["kind"] = self.kind
            if self.spousePid:
                self.save_cache["spid"] = self.spousePid
            if self.marryTimes:
                self.save_cache["n"] = self.marryTimes
            if self.power:
                self.save_cache["power"] = self.power
            if self.powerEn:
                self.save_cache["en"] = self.powerEn
            if self.powerMsg:
                self.save_cache["msg"] = self.powerMsg
            if self.powerMsgTrueLove:
                self.save_cache["tlove"] = self.powerMsgTrueLove
            if self.powerLvReward:
                self.save_cache["rw"] = self.powerLvReward
            if self.marryTime:
                self.save_cache["time"] = self.marryTime
            if self.cycleDay.data:
                self.save_cache["cycleDay"] = self.cycleDay.to_save_bytes()
        return self.save_cache

    #读库数据初始化
    def load_from_dict(self, data):
        self.marryId = data.get("id", 0)
        self.isMarried = data.get("married", 0)
        self.kind = data.get("kind", 0)
        self.spousePid = data.get("spid", 0)
        self.marryTimes = data.get("n", 0)
        self.power = data.get("power", 0)
        self.powerEn = data.get("en", [])
        self.powerMsg = data.get("msg", [])
        self.powerMsgTrueLove = data.get("tlove", [])
        self.powerLvReward = data.get("rw", [])
        self.marryTime = data.get("time", 0)
        self.cycleDay.load_from_dict(data.get("cycleDay", ""))


    #登录初始化下发数据
    def to_init_data(self):
        self.checkEn()
        init_data = {}
        init_data["isMarried"] = self.isMarried
        init_data["spousePid"] = self.spousePid
        init_data["kind"] = self.kind
        init_data["power"] = self.power
        init_data["powerEn"] = self.powerEn
        init_data["powerMsg"] = self.powerMsg
        init_data["powerMsgTrueLove"] = self.powerMsgTrueLove
        init_data["powerLvReward"] = self.powerLvReward
        init_data["MarryUseIDs"] = self.getMarryUseIDs()

        return init_data

    def to_wee_hour_data(self):
        init_data = {}
        return init_data

    def uninit(self):
        pass

    def getMarryStatus(self):
        return self.isMarried

    def marrySomeone(self, pid, kind, marryId):
        if marryId > self.marryId:
            self.marryId = marryId
        self.isMarried = 1
        self.spousePid = pid
        self.kind = kind
        self.marryTimes += 1
        self.marryTime = int(time.time())
        self.cycleDay.Set("isMarriedToday", 1)
        self.owner.safe_pub(msg_define.MSG_JIEHUN_AGREE)
        self.markDirty()

    def divorce(self):
        self.isMarried = 0
        self.spousePid = 0
        self.kind = 0
        self.markDirty()

    def getMarryId(self):
        return self.marryId

    def isFirst(self):
        return self.marryTimes == 1

    def getMarryTimes(self):
        return self.marryTimes

    def getSpousePid(self):
        return self.spousePid

    def getKind(self):
        return self.kind

    def isMarriedToday(self):
        return self.cycleDay.Query("isMarriedToday", 0)

    # 今日已领取登陆时段奖励
    def getMarryUseIDs(self):
        return self.cycleDay.Query("MarryUseIDs", [])

    # 今日已领取登陆时段奖励
    def setMarryUseIDs(self, todayReward):
        self.cycleDay.Set("MarryUseIDs", todayReward)
        self.markDirty()

    def getMaxPower(self):
        pmax=0
        for x in Game.res_mgr.res_marryLv.values():
            if x.power>pmax:
                pmax=x.power
                
        return pmax
        
    def marryPowerPush(self, id, en, num, pid, name):
        self.power+=en
        pmax=self.getMaxPower()
        if self.power>pmax:
            self.power=pmax

        res=Game.res_mgr.res_marryPower.get(id)
        if res:
            obj={
                    "time":time.time(),
                    "id":id,
                    "en":en,
                    "num":num,
                    "pid":pid,
                    "name":name,
                }
            if res.trueLove:
                self.powerMsgTrueLove.append(obj)
            else:
                self.powerMsg.append(obj)
                if len(self.powerMsg)>30:
                    self.powerMsg.pop(0)

        self.markDirty()

    def checkEn(self):
        for k,v in Game.res_mgr.res_marryPower.items():
            if v.enlimit:
                found=None
                for one in self.powerEn:
                    if one["id"]==k:
                        found=one
                        break
                if not found:
                    found={"id":k,"en":0,"usetime":1}
                    self.powerEn.append(found)
                    
                t=time.time()
                while found["usetime"]+v.cd<=t and found["usetime"]:
                    found["en"]+=1
                    found["usetime"]+=v.cd
                    if found["en"]>=v.enlimit:
                        found["usetime"]=0
        
        self.markDirty()

    def TrueLoveRead(self):
        if self.powerMsgTrueLove:
            self.powerMsgTrueLove.pop(0)
        self.markDirty()

    def MsgRead(self):
        self.powerMsgTrue=[]
        self.markDirty()

    def addPower(self, id, en,uselimit,enlimit,num):
        self.power+=en
        pmax=self.getMaxPower()
        if self.power>pmax:
            self.power=pmax
            
        if uselimit:
            useids=self.getMarryUseIDs()
            useids.extend([id]*num)
            self.setMarryUseIDs(useids)

        if enlimit:
            for x in self.powerEn:
                if x["id"]==id:
                    x["en"]-=1
                    if not x["usetime"]:
                        x["usetime"]=time.time()
                    break

        # TODO
        self.markDirty()


