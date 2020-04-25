#!/usr/bin/env python
# -*- coding:utf-8 -*-

from game.common import utility
from game.define import constant, msg_define
from game import Game
import time
from random import randint
from corelib import spawn_later, log, spawn


from game.core.cycleData import CycleDay

class PlayerYabiao(utility.DirtyFlag):
    def __init__(self, owner):
        utility.DirtyFlag.__init__(self)
        self.cycleDay = CycleDay(self)
        self.owner = owner  # 拥有者
        self.time = 0 #
        self.mul = 1 #
        self.id = 0 #
        self.quality = 1 #
        self.becatch = [] #
        self.history = {} #
        self.count = 0 #
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
            self.save_cache["cycleDay"] = self.cycleDay.to_save_bytes()
            self.save_cache["time"] = self.time
            self.save_cache["mul"] = self.mul
            self.save_cache["id"] = self.id
            self.save_cache["quality"] = self.quality
            self.save_cache["becatch"] = self.becatch
            self.save_cache["history"] = self.history
            self.save_cache["count"] = self.count
        return self.save_cache

    #读库数据初始化
    def load_from_dict(self, data):
        self.cycleDay.load_from_dict(data.get("cycleDay", ""))
        self.time = data.get("time", 0) 
        self.mul = data.get("mul", 1) 
        self.id = data.get("id", 0) 
        self.quality = data.get("quality", 1) 
        self.becatch = data.get("becatch", []) 
        self.history = data.get("history", {}) 
        self.count = data.get("count", 0) 

    #登录初始化下发数据
    def to_init_data(self):
        init_data = {}
        init_data["time"] = self.time
        init_data["mul"] = self.mul
        init_data["quality"] = self.quality
        init_data["becatch"] = self.becatch
        init_data["rob"] = self.getYabiaoRob()
        init_data["husong"] = self.getYabiaoHusong()
        
        return init_data

    # def roomMsg(self,msgtype,data):
    #     if msgtype=="bye":
    #         spawn(self.owner.call, "pushHusongFinish", {"id":data["id"]}, noresult=True)
    
    def uninit(self):
        # self.owner.unsub(msg_define.MSG_ROLE_XLV_UPGRADE, self.event_lv_uprade)
        pass
    
    def addHistory(self,type,data):
        
        self.id+=1

        t = time.time()

        self.history[str(self.id)]={"type":type,"id":self.id,"time":t,"data":data}

        self.history.pop(str(self.id-50),None)

        self.markDirty()

    def modfiyHistoryFinish(self,id):

        # if str(id) in self.history:
        self.history[str(id)]["type"]=1
        self.markDirty()

    def getHistory(self):
        list = []
        for kk,vv in self.history.items():
            list.append(vv)
        return list

    def setTimeFinish(self):
        self.time=time.time()-1
        self.markDirty()

    def getYabiaoRob(self):
        return self.cycleDay.Query("YabiaoRob", 0)

    def addYabiaoRob(self):
        v = self.getYabiaoRob()
        self.setYabiaoRob(v + 1)
        return v

    def setYabiaoRob(self,v):
        self.cycleDay.Set("YabiaoRob", v)

    def getYabiaoHusong(self):
        return self.cycleDay.Query("YabiaoHusong", 0)

    def addYabiaoHusong(self):
        v = self.getYabiaoHusong()
        self.setYabiaoHusong(v+1)
        return v

    def setYabiaoHusong(self,v):
        self.cycleDay.Set("YabiaoHusong", v)

    def husong(self,mul):
        self.mul=mul
        yabiaoTime = Game.res_mgr.res_common.get("yabiaoTime")
        self.time=time.time()+yabiaoTime.i
        self.becatch=[]
        self.addYabiaoHusong()
        if self.quality==5:
            self.count+=1

        self.owner.safe_pub(msg_define.MSG_XY_PROTECT)

        self.markDirty()

    def getBecatchID(self):
        yabiaoJiebiaoLimit = Game.res_mgr.res_common.get("yabiaoJiebiaoLimit")
        retv = []
        for x in self.becatch:
            if x["type"]:
                if yabiaoJiebiaoLimit.i>len(retv):
                    retv.append(x["id"])
        return retv


    def flashCarMax(self):


        self.quality=5
        self.markDirty()

    def flashCar(self):


        q=1
   
        
        kks = {}
        num = 0
        for kk,vv in Game.res_mgr.res_yabiao.items():
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


        self.quality=q

        self.markDirty()

    def finishYabiao(self):
        self.time=0
        q=1
   
        
        kks = {}
        num = 0
        for kk,vv in Game.res_mgr.res_yabiao.items():
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


        self.quality=q
        self.markDirty()



    def robHusongCar(self,robid,data,fdata,historydata):

        
        pvpRounds = Game.res_mgr.res_common.get("pvpRounds")
        fightobj = Game.fight_mgr.createFight(constant.FIGHT_TYPE_180)
        fightobj.SetRounds(pvpRounds.i)

        mydata = self.owner.GetFightData()
        rs = fightobj.init_players_by_data(fdata, mydata)
        if not rs:
            return {}
        
        fightLog = fightobj.doFight()
        fightResult = fightLog["result"].get("win", 0)

        self.becatch.append({"id":robid,"name":fdata["name"],"type":fightResult})

        historydata["data"]["quality"]=self.quality

        if fightResult:

            if robid not in data["data"]["becatchID"]:
                data["data"]["becatchID"].append(robid)
                self.addHistory(0,historydata)

                days = self.owner.base.GetServerOpenDay()
                ares = Game.res_mgr.res_activity.get(constant.ACTIVITY_YABIAO)
                startD = ares.openDayRange[0]
                from game.mgr.room import get_rpc_room
                rpc_room = get_rpc_room(startD<=days)
                if rpc_room:
                    rpc_room.update(1,self.owner.id,data["data"])
            
        else:
            self.addHistory(4,historydata)

        self.markDirty()

        return {"data":data,"fightLog":fightLog}

    def revengeHusongCar(self,robid,data,fdata,historydata):

        
        pvpRounds = Game.res_mgr.res_common.get("pvpRounds")
        fightobj = Game.fight_mgr.createFight(constant.FIGHT_TYPE_180)
        fightobj.SetRounds(pvpRounds.i)

        mydata = self.owner.GetFightData()
        rs = fightobj.init_players_by_data(fdata, mydata)
        if not rs:
            return {}
        
        fightLog = fightobj.doFight()
        fightResult = fightLog["result"].get("win", 0)


        if fightResult:
            self.addHistory(5,historydata)



        return {"data":data,"fightLog":fightLog}
