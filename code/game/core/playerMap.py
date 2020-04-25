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


class PlayerMap(utility.DirtyFlag):
    def __init__(self, owner):
        utility.DirtyFlag.__init__(self)
        self.owner = owner  # 拥有者

        self.cycleDay = CycleDay(self)

        self.mapSubId = 1 #当前关卡
        self.passSubId = 0 #已通关关卡id
        self.rewardSubId = [] #领奖的关卡id

        self.offexp=0 #离线经验箱子 经验
        self.offcoin=0 #离线经验箱子 金币
        self.offexplore=0 #离线经验箱子 探索值
        self.offpetexp=0 #离线经验箱子 宠物经验
        self.offreward={} #离线经验箱子 道具{id:num}
        self.offtimes=0 #离线经验箱子 当前累计次数
        self.ChargeEndTime={} #特权结束时间 {resid:结束时间戳秒}
        self.offlasttime=time.time() #离线经验箱子 最后一次生成奖励时间错时间戳

        

        self.objIDs=[] #地图物件 ID
        self.objlasttime=time.time() #地图物 最后一次生成物件时间错时间戳
        self.objkey=[] #地图物 已扔关键id

        self.passEncounterId = 0 #已通关遭遇战id
        self.firstFailEncounterId = 0 #首次失败遭遇战最大id

        self.save_cache = {} #存储缓存

        # 监听普通场景打怪
        self.owner.sub(msg_define.MSG_MORMAL_SCENE_FIGHT, self.event_normal_fight)


    def markDirty(self):
        utility.DirtyFlag.markDirty(self)
        if self.owner:
            self.owner.markDirty()

    #存库数据
    def to_save_dict(self, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            self.save_cache = {}

            self.save_cache["cycleDay"] = self.cycleDay.to_save_bytes()

            self.save_cache["mapSubId"] = self.mapSubId
            self.save_cache["passSubId"] = self.passSubId
            self.save_cache["rewardSubId"] = self.rewardSubId

            self.save_cache["ChargeEndTime"] = utility.obj2list(self.ChargeEndTime)
   
            self.save_cache["passEncounterId"] = self.passEncounterId
            self.save_cache["firstFailEncounterId"] = self.firstFailEncounterId

            if self.offexp:
                self.save_cache["offexp"] = self.offexp
            if self.offcoin:
                self.save_cache["offcoin"] = self.offcoin
            if self.offexplore:
                self.save_cache["offexplore"] = self.offexplore
            if self.offpetexp:
                self.save_cache["offpetexp"] = self.offpetexp
            if self.offreward:
                self.save_cache["offreward"] = self.offreward
            if self.offtimes:
                self.save_cache["offtimes"] = self.offtimes
            if self.offlasttime:
                self.save_cache["offlasttime"] = self.offlasttime
            
            if self.objIDs:
                self.save_cache["objIDs"] = self.objIDs
            if self.objlasttime:
                self.save_cache["objlasttime"] = self.objlasttime
            if self.objkey:
                self.save_cache["objkey"] = self.objkey


        return self.save_cache

    #读库数据初始化
    def load_from_dict(self, data):

        self.cycleDay.load_from_dict(data.get("cycleDay", ""))

        self.ChargeEndTime = utility.list2obj(data.get("ChargeEndTime", []))

        self.mapSubId = data.get("mapSubId", 1)
        self.passSubId = data.get("passSubId", 0)
        self.rewardSubId = data.get("rewardSubId", [])
        self.offexp = data.get("offexp", 0)
        self.offcoin = data.get("offcoin", 0)
        self.offexplore = data.get("offexplore", 0)
        self.offpetexp = data.get("offpetexp", 0)
        self.offreward = data.get("offreward", {})
        self.offtimes = data.get("offtimes", 0)
        self.offlasttime = data.get("offlasttime", time.time())

        self.objIDs = data.get("objIDs", [])
        self.objlasttime = data.get("objlasttime", time.time())
        self.objkey = data.get("objkey", [])
        
        self.passEncounterId = data.get("passEncounterId", 0)  # 已通关遭遇战id
        self.firstFailEncounterId = data.get("firstFailEncounterId", 0)  # 首次失败遭遇战最大id


    #登录初始化下发数据
    def to_init_data(self):

        init_data = {}

        vipres = Game.res_mgr.res_vip.get(self.owner.vip.vip)

        mapOffTime = Game.res_mgr.res_common.get("mapOffTime")
        mapOffMaxTimes = Game.res_mgr.res_common.get("mapOffMaxTimes")

        mapObjTime = Game.res_mgr.res_common.get("mapObjTime")
        mapObjNum = Game.res_mgr.res_common.get("mapObjNum")

        res=Game.res_mgr.res_mapSub.get(self.mapSubId)

        nt=time.time()



        n=mapOffMaxTimes.i-self.offtimes
        for _ in range(n):
            netxt=self.offlasttime+mapOffTime.i
            if netxt>nt:
                break

            self.offtimes+=1
            self.offlasttime=netxt

            self.offexp+=res.offexp*(10000+vipres.offper)//10000
            self.offcoin+=res.offcoin*(10000+vipres.offper)//10000
            self.offexplore+=res.offexplore*(10000+vipres.offper)//10000
            self.offpetexp+=res.offpetexp*(10000+vipres.offper)//10000

            for offreward in res.offreward:
                rewardRes = Game.res_mgr.res_reward.get(offreward)
                resp = rewardRes.doReward()
                # resp={4:1}
                for k,v in resp.items():
                    k=str(k)
                    self.offreward[k]=self.offreward.get(k,0)+v


        if self.offtimes==mapOffMaxTimes.i:
            self.offlasttime=nt

        obj=[]
        n=mapObjNum.i-len(self.objIDs)
        for _ in range(n):
            netxt=self.objlasttime+mapObjTime.i
            if netxt>nt:
                break
            
            # 重复类型
            obj=res.objReuse
            rx=random.randint(1,10000)
            
            if len(self.objkey)>=len(res.objOnce):
                rx=999
            
            isOnce=False
            if rx<=res.objPercent:
                isOnce=True
                obj=[]
                ooo=copy.deepcopy(res.objOnce)
                for vv in ooo:
                    if vv[0] not in self.objkey:
                        obj.append(vv)
                        
                        

            moid = utility.Choice(obj)
            
            self.objIDs.append(moid)
            if isOnce:
                self.objkey.append(moid)

            self.objlasttime=netxt


        if len(self.objIDs)==mapObjNum.i:
            self.objlasttime=nt

        self.markDirty()


        
        init_data["mapSubId"] = self.mapSubId
        init_data["passSubId"] = self.passSubId
        init_data["rewardSubId"] = self.rewardSubId
        init_data["quickFree"] = self.getquickFree()
        init_data["quickUse"] = self.getquickUse()

        init_data["ChargeEndTime"]=self.ChargeEndTime

        init_data["offexp"] = self.offexp
        init_data["offcoin"] = self.offcoin
        init_data["offexplore"] = self.offexplore
        init_data["offpetexp"] = self.offpetexp
        init_data["offreward"] = self.offreward
        init_data["offlasttime"] = self.offlasttime
        init_data["offtimes"] = self.offtimes

        init_data["objIDs"] = self.objIDs
        init_data["objlasttime"] = self.objlasttime
        init_data["objkey"] = self.objkey

        init_data["passEncounterId"] = self.passEncounterId

        return init_data

    #零点更新的数据
    def to_wee_hour_data(self):
        return self.to_init_data()


    # 角色下线时要做的清理操作
    def uninit(self):
        self.owner.unsub(msg_define.MSG_MORMAL_SCENE_FIGHT, self.event_normal_fight)
    
    def gainOff(self):
        offexp = self.offexp
        offcoin = self.offcoin
        offexplore = self.offexplore
        offpetexp = self.offpetexp

        offreward={}
        for k,v in self.offreward.items():
            k=int(k)
            offreward[k]=v


        self.offexp = 0
        self.offcoin = 0
        self.offexplore = 0
        self.offpetexp = 0
        self.offreward = {}

        self.offtimes=0
        
        self.markDirty()

        return offexp, offcoin, offexplore, offpetexp, offreward

    def gainObj(self,resid):

        if resid not in self.objIDs:
            return 0
        
        self.objIDs.remove(resid)

        return resid
        

    def getquickFree(self):
        return self.cycleDay.Query("quickFree",0)

    def setquickFree(self, v):
        self.cycleDay.Set("quickFree", v)

    def getquickUse(self):
        return self.cycleDay.Query("quickUse",0)

    def setquickUse(self, v):
        self.cycleDay.Set("quickUse", v)



    def event_normal_fight(self, fightResult):
        """普通场景战斗"""
        if fightResult: #打赢才算

            self.passSubId = self.mapSubId
            self.mapSubId = self.GetNextMapSubId()

            # 更新地图关卡排行榜
            # baseInfo = self.owner.base.to_rank_data()
            # rankInfo = {}
            # rankInfo["id"] = self.owner.id
            # rankInfo["sortEle"] = [self.passSubId, self.owner.base.GetFightAbility()]
            # rankInfo["baseInfo"] = baseInfo
            # Game.sub_rank_mgr.updatePlayer(constant.RANK_TYPE_MAP, rankInfo)
            self.owner.rank.uploadRank(constant.RANK_TYPE_MAP)

            
            # 更新等级榜
            # rankInfo = {}
            # rankInfo["id"] = self.owner.id
            # rankInfo["sortEle"] = [self.owner.base.lv, self.passSubId, self.owner.base.fa]
            # rankInfo["baseInfo"] = baseInfo
            # Game.sub_rank_mgr.updatePlayer(constant.RANK_TYPE_LV, rankInfo)


    def GetNextMapSubId(self):
        iNextId = self.mapSubId + 1
        curRes = Game.res_mgr.res_mapSub.get(self.mapSubId)
        nextRes = Game.res_mgr.res_mapSub.get(iNextId)
        if not nextRes:
            return self.mapSubId
        if curRes.mapId != nextRes.mapId: #跨地图需要手动
            return self.mapSubId

        self.objIDs=[]
        self.objlasttime=0
        self.objkey=[]
        self.markDirty()

        return iNextId

    def SetRewardSubId(self, subId):
        self.rewardSubId.append(subId)
        self.markDirty()

    def SetMapSubId(self, subId):
        self.mapSubId = subId
        self.objIDs=[]
        self.objlasttime=0
        self.objkey=[]
        self.markDirty()

    def SetPassEncounterId(self, passEncounterId):
        self.passEncounterId = passEncounterId
        self.markDirty()

        self.owner.safe_pub(msg_define.MSG_PASS_ENCOUNTER_FIGHT)

    def GetPassEncounterId(self):
        return self.passEncounterId

    def initPassEncounterId(self):
        if self.passEncounterId:
            return
        keys = list(Game.res_mgr.res_passId_encounter.keys())
        keys.sort()
        for key in keys:
            resEncounter = Game.res_mgr.res_passId_encounter.get(key)
            if resEncounter.passId < self.passSubId:
                self.passEncounterId = resEncounter.id
                self.markDirty()
            else:
                break
    

    def GetFirstFailEncounterId(self):
        return self.firstFailEncounterId

    def SetFirstFailEncounterId(self, EncounterId):
        if EncounterId > self.firstFailEncounterId:
            self.firstFailEncounterId = EncounterId
            self.markDirty()