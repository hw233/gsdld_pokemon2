#!/usr/bin/env python
# -*- coding:utf-8 -*-
import config
from game.common import utility
from game.define import constant, msg_define
from game import Game
import time
from random import randint
from corelib import spawn_later, log, spawn
import copy


from game.core.cycleData import CycleDay

class PlayerDiaoyu(utility.DirtyFlag):
    def __init__(self, owner):
        utility.DirtyFlag.__init__(self)
        self.owner = owner  # 拥有者
        self.time = 0 #上次退出时间
        self.diaoyutime = 0 #上次钓鱼时间
        self.score = 0 #分数
        self.yulou = [] #鱼篓
        self.hp = {} #血量
        self.save_cache = {} #存储缓存
        self.status = 0 #钓鱼状态
        self.cycleDay = CycleDay(self)
        # self.owner.sub(msg_define.MSG_ROLE_XLV_UPGRADE, self.event_lv_uprade)

    def markDirty(self):
        utility.DirtyFlag.markDirty(self)
        if self.owner:
            self.owner.markDirty()

    #存库数据
    def to_save_dict(self, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            self.save_cache["cycleDay"] = self.cycleDay.to_save_bytes()
            self.save_cache = {}
            self.save_cache["time"] = self.time
            self.save_cache["diaoyutime"] = self.diaoyutime
            self.save_cache["score"] = self.score
            self.save_cache["yulou"] = self.yulou
            # self.save_cache["hp"] = self.hp
        return self.save_cache

    #读库数据初始化
    def load_from_dict(self, data):
        self.cycleDay.load_from_dict(data.get("cycleDay", ""))
        self.time = data.get("time", 0) 
        self.diaoyutime = data.get("diaoyutime", 0) 
        self.score = data.get("score", 0) 
        self.yulou = data.get("yulou", []) 
        # self.hp = data.get("hp", {}) 



    #登录初始化下发数据 不换鱼
    def to_init_data(self):

        self.yulou.sort()
        init_data = {}
        init_data["time"] = self.time
        init_data["becatch"] = self.getDiaoyuBecatch()
        init_data["rob"] = self.getDiaoyuRob()
        init_data["yulou"] = self.yulou
        # init_data["berob"] = self.getDiaoyuBerob()

        spawn(self.sendRpcScore) #用额外的协程，避免卡死

        init_data["score"] = self.getDiaoyuDayScore()

        # import app
        # from game.mgr.room import get_rpc_diaoyu
        # rpc_diaoyu = get_rpc_diaoyu()
        # if rpc_diaoyu:
        #     rpc_diaoyu.addScore(self.owner.id,app.addr,self.owner.name,config.serverNo,1)
        
        return init_data

    def sendRpcScore(self):
        import app
        from game.mgr.room import get_rpc_diaoyu
        rpc_diaoyu = get_rpc_diaoyu()
        if rpc_diaoyu and self.score:
            rpc_diaoyu.setScore(self.owner.id,app.addr,self.owner.name,config.serverNo,self.score)

    # def roomMsg(self,msgtype,data):
    #     if msgtype=="bye":
    #         spawn(self.owner.call, "diaoyuExitPush", {"id": data["id"]}, noresult=True)
    #     elif msgtype=="update":
    #         spawn(self.owner.call, "diaoyuStatusPush", {"list":data}, noresult=True)
    #     elif msgtype=="hello":
    #         spawn(self.owner.call, "diaoyuEntetPush", {"list":data}, noresult=True)

    
    def uninit(self):
        # self.owner.unsub(msg_define.MSG_ROLE_XLV_UPGRADE, self.event_lv_uprade)
        pass
    
    def diaoyuReward(self,quality):
        respBag = {}
        diaoyuXdayReward = Game.res_mgr.res_common.get("diaoyuXdayReward")
        if not diaoyuXdayReward:
            return respBag

        if quality in self.yulou:
            self.yulou.remove(quality)
        else:
            return respBag

        reward = {}

        res = Game.res_mgr.res_diaoyu.get(quality)
        if res:
            iOpenDay = self.owner.base.GetServerOpenDay()
            resreward = copy.deepcopy(res.reward)
            if iOpenDay>=diaoyuXdayReward.i:
                resreward=copy.deepcopy(res.reward2)
            
            for kk,vv in resreward.items():
                reward[kk] = reward.get(kk,0) + vv

        respBag = self.owner.bag.add(reward, constant.ITEM_ADD_DIAOYUREWARD, wLog=True)
        self.markDirty()
        return respBag

    def exitdiaoyu(self):
        # import app
        # from game.mgr.room import get_rpc_diaoyu
        # rpc_diaoyu = get_rpc_diaoyu()
        # if rpc_diaoyu:
        #     rpc_diaoyu.addScore(self.owner.id,app.addr,self.owner.name,config.serverNo,1)

        diaoyuXdayReward = Game.res_mgr.res_common.get("diaoyuXdayReward")
        iOpenDay = self.owner.base.GetServerOpenDay()

        reward = {}

        for quality in self.yulou:
            res = Game.res_mgr.res_diaoyu.get(quality)
            if res:
                
                resreward = copy.deepcopy(res.reward)
                if iOpenDay>=diaoyuXdayReward.i:
                    resreward=copy.deepcopy(res.reward2)
                
                for kk,vv in resreward.items():
                    reward[kk] = reward.get(kk,0) + vv

        respBag = self.owner.bag.add(reward, constant.ITEM_ADD_DIAOYUREWARD, wLog=True)

        spawn(self.sendRpcScore)  # 用额外的协程，避免卡死

        self.yulou = []
        self.status = 0
        self.time=time.time()

        self.markDirty()

        return respBag

    def exitRpcDiaoyu(self):
        from game.mgr.room import get_rpc_diaoyu
        rpc_diaoyu = get_rpc_diaoyu()
        if rpc_diaoyu:
            rpc_diaoyu.bye(2,self.owner.id)

    def diaoyuCleanScore(self):
        self.score = 0
        self.setDiaoyuDayScore(0)
        self.markDirty()

    # 返回鱼, 0代表时间不够
    def getFish(self):

        diaoyuFish = Game.res_mgr.res_common.get("diaoyuFish")
        now = time.time()
        if now <self.diaoyutime+diaoyuFish.i:
            return 0
        
        self.diaoyutime = now


        q=1
   
        
        kks = {}
        num = 0
        for kk,vv in Game.res_mgr.res_diaoyu.items():
            vvv = []
            for _ in range(vv.weight):
                vvv.append(num)
                num+=1
            kks[kk]=vvv
        
        x = randint(0,num-1)

        for kk,vv in kks.items():
            if x in vv:
                q=kk
                break 

        res = Game.res_mgr.res_diaoyu.get(q)

        import app
        from game.mgr.room import get_rpc_diaoyu
        rpc_diaoyu = get_rpc_diaoyu()
        if rpc_diaoyu:
            rpc_diaoyu.addScore(self.owner.id,app.addr,self.owner.name,config.serverNo,res.score)
            self.score = self.score + res.score
            self.addDiaoyuDayScore(res.score)
        
        self.yulou.append(q)

        self.markDirty()
        return q

    def robFishOk(self,q):
        res = Game.res_mgr.res_diaoyu.get(q)

        import app
        from game.mgr.room import get_rpc_diaoyu
        rpc_diaoyu = get_rpc_diaoyu()
        if rpc_diaoyu:
            rpc_diaoyu.addScore(self.owner.id,app.addr,self.owner.name,config.serverNo,res.score)
            self.score = self.score + res.score
            self.addDiaoyuDayScore(res.score)
        self.markDirty()
        
        return res.score

    def getDiaoyuDayScore(self):
        return self.cycleDay.Query("DiaoyuDayScore", 0)

    def addDiaoyuDayScore(self,v):
        n = self.getDiaoyuDayScore()
        self.cycleDay.Set("DiaoyuDayScore", n+v)

    def setDiaoyuDayScore(self,v):
        self.cycleDay.Set("DiaoyuDayScore", v)

    def getDiaoyuBecatch(self):
        return self.cycleDay.Query("DiaoyuBecatch", [])

    def addDiaoyuBecatch(self,v):
        n = self.getDiaoyuBecatch()
        n.append(v)
        
        self.cycleDay.Set("DiaoyuBecatch", n)


    def getDiaoyuRob(self):
        return self.cycleDay.Query("DiaoyuRob", 0)

    def addDiaoyuRob(self):
        o = self.getDiaoyuRob()
        
        self.cycleDay.Set("DiaoyuRob", o + 1)
        return o

    def getDiaoyuBerob(self):
        return self.cycleDay.Query("DiaoyuBerob", 0)

    def addDiaoyuBerob(self):
        o = self.getDiaoyuBerob()
        
        self.cycleDay.Set("DiaoyuBerob", o + 1)
        return o


    def addHistory(self,type,data):
        data["type"] = type
        data["time"] = time.time()
        self.addDiaoyuBecatch(data)

    def sethp(self,redhp):
        self.hp=redhp
        self.markDirty()

    def diaoyuRob(self,robid,data,fdata,historydata):

        oldRedHp = historydata["redhp"]
        

        pvpRounds = Game.res_mgr.res_common.get("pvpRounds")
        fightobj = Game.fight_mgr.createFight(constant.FIGHT_TYPE_160)
        fightobj.SetRounds(pvpRounds.i)

        mydata = self.owner.GetFightData()
        rs = fightobj.init_players_by_data(fdata, mydata)
        if not rs:
            return {}

        fix = {}
        if self.hp:
            fix[constant.FIGHT_TEAM_BLUE] = self.hp
        if oldRedHp:
            fix[constant.FIGHT_TEAM_RED] = oldRedHp
        
        # print("!!!!",fix)
        fightobj.FixFighterHP(fix)

        historydata["redhp"] = {}

        fightLog = fightobj.doFight(1)

        fightResult = fightLog["result"].get("win", 0)

        myhp = fightLog["resultInfo"][constant.FIGHT_TEAM_BLUE]
        redhp = fightLog["resultInfo"][constant.FIGHT_TEAM_RED]

        

        if fightobj.teamIsAllDead(myhp):
            myhp={}
        
  
        if fightobj.teamIsAllDead(redhp):
            redhp={}


        self.hp = myhp

        # a={1: {1: {899030007: {'role': {'fashion': 1, 'name': '\xe7\xa7\x8b\xe8\x8a\xaf\xe8\x8a\xab', 'title': 1, 'hp': 33610, 'attrExtra': {'onlineGoldExtra': 0, 'onlineExpExtra': 0}, 'sex': 1, 'rid': 899030007, 'outfit': 0, 'showList': [{'modeType': 1, 'imageType': 1, 'imageId': 1}, {'modeType': 2, 'imageType': 1, 'imageId': 1}, {'modeType': 7, 'imageType': 1, 'imageId': 1}, {'modeType': 8, 'imageType': 1, 'imageId': 1}]}}}, 3: {70: {'pet': {'petId': 70, 'hp': 34810, 'name': '', 'evolveLv': 0}}}, 4: {1: {'tiannv': {'tiannvType': 9, 'imageId': 1, 'hp': 33610, 'imageType': 1, 'tiannvId': 1}}}}, 2: {1: {499030007: {'role': {'fashion': 1, 'name': '\u6e29\u83ba\u537f', 'title': 1, 'hp': 33610, 'attrExtra': {'onlineGoldExtra': 0, 'onlineExpExtra': 0}, 'sex': 2, 'rid': 499030007, 'outfit': 0, 'showList': [{'modeType': 1, 'imageType': 1, 'imageId': 1}, {'modeType': 2, 'imageType': 1, 'imageId': 1}, {'modeType': 7, 'imageType': 1, 'imageId': 1}, {'modeType': 8, 'imageType': 1, 'imageId': 1}]}}}, 3: {70: {'pet': {'petId': 70, 'hp': 34810, 'name': '', 'evolveLv': 0}}}, 4: {1: {'tiannv': {'tiannvType': 9, 'imageId': 1, 'hp': 33610, 'imageType': 1, 'tiannvId': 1}}}}}

        if fightResult:

            if historydata["quality"] in self.yulou:
                self.yulou.remove(historydata["quality"])
            
            self.addDiaoyuBerob()

            self.addHistory(0,historydata)

            from game.mgr.room import get_rpc_diaoyu
            rpc_diaoyu = get_rpc_diaoyu()
            if rpc_diaoyu:
                dydata = self.owner.getDiaoyuInfo()
                rpc_diaoyu.updateNoBroadcast(2,self.owner.id,dydata)
            
        else:
            self.addHistory(1,historydata)


        dUpdate = {}
        
        dUpdate["diaoyu"] = self.to_init_data()

        spawn(self.owner.call, "diaoyuPush", {"allUpdate":dUpdate}, noresult=True)

        self.markDirty()

        return {"data":data,"fightLog":fightLog,"redhp":redhp}