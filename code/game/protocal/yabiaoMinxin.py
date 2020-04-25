#!/usr/bin/env python
# -*- coding:utf-8 -*-
import random
import copy
from game.define import errcode, constant
from game import Game
from game.common import utility
import config
from grpc import DictExport, DictItemProxy, get_proxy_by_addr
from corelib import gtime
import time

class YabiaoRpcMixin(object):
    if 0:
        from game.core import player as player_md
        player = player_md.Player()


    def rc_husong(self):

        yabiaoHusongNum = Game.res_mgr.res_common.get("yabiaoHusongNum")
        if not yabiaoHusongNum:
            return 0, errcode.EC_NORES
        
        yabiaoDoubleTime = Game.res_mgr.res_common.get("yabiaoDoubleTime")
        if not yabiaoDoubleTime:
            return 0, errcode.EC_NORES

        if self.player.yabiao.time!=0:
            return 0, errcode.EC_HUSONG_TIME_NO_ZERO
    
        if self.player.yabiao.getYabiaoHusong()>=yabiaoHusongNum.i:
            return 0, errcode.EC_HUSONG_NUM_USEUP



        mul=1
        currHour = gtime.current_hour()
        if currHour in yabiaoDoubleTime.arrayint1:
            mul=2

        self.player.yabiao.husong(mul)


        bhname = ""
        from game.mgr.guild import get_rpc_guild
        rpc_guild = get_rpc_guild(self.player.guild.GetGuildId())
        if rpc_guild:
            bhname = rpc_guild.getName()

        days = self.player.base.GetServerOpenDay()
        ares = Game.res_mgr.res_activity.get(constant.ACTIVITY_YABIAO)
        startD = ares.openDayRange[0]
        from game.mgr.room import get_rpc_room
        rpc_room = get_rpc_room(startD<=days)
        if not rpc_room:
            return 0, errcode.EC_GETD_RPC_ROOM_FAIL


        data={
            "power":self.player.base.fa,
            "quality":self.player.yabiao.quality,
            "bhname":bhname,
            "sex":self.player.base.GetSex(),
            "portrait":self.player.myhead.getPortrait(),
            "headframe":self.player.myhead.getHeadframe(),
            "becatchID":self.player.yabiao.getBecatchID(),
        }

        import app
        rrv = rpc_room.hello(1,self.player.id,config.serverNo,app.addr,self.player.name,data,self.player.yabiao.time,0)
        if not rrv:
            return 0, errcode.EC_CALL_RPC_ROOM_FAIL
        
        rrv = rpc_room.get(1,self.player.id)
        if not rrv:
            return 0, errcode.EC_CALL_RPC_ROOM_FAIL
        
        resp = {}
        resp["list"] = rrv["v"]
        dUpdate={}
        dUpdate["jiebiao"] = self.player.yabiao.to_init_data()
        resp["allUpdate"] = dUpdate


        return 1, resp


    def rc_getHusongData(self):


        
        days = self.player.base.GetServerOpenDay()
        ares = Game.res_mgr.res_activity.get(constant.ACTIVITY_YABIAO)
        startD = ares.openDayRange[0]
        from game.mgr.room import get_rpc_room
        rpc_room = get_rpc_room(startD<=days)
        if not rpc_room:
            return 0, errcode.EC_GETD_RPC_ROOM_FAIL
        
        rrv = rpc_room.getByServerNo(1,config.serverNo)
        if not rrv:
            return 0, errcode.EC_CALL_RPC_ROOM_FAIL

        resp = {}
        resp["list"] = rrv["v"]

        return 1, resp

    def rc_getHusongUserData(self,id):
        days = self.player.base.GetServerOpenDay()
        ares = Game.res_mgr.res_activity.get(constant.ACTIVITY_YABIAO)
        startD = ares.openDayRange[0]
        from game.mgr.room import get_rpc_room
        rpc_room = get_rpc_room(startD<=days)
        if not rpc_room:
            return 0, errcode.EC_GETD_RPC_ROOM_FAIL

        rrv = rpc_room.getOneByServerNo(1,config.serverNo,id)
        if not rrv:
            return 0, errcode.EC_CALL_RPC_ROOM_FAIL
        

        # print("1111111111",config.serverNo,id,rrv)

        data = rrv["v"]



        if len(data)==0:
            return 0, errcode.EC_HUSONG_NOFOUNDONE
        
        
        
        resp = {}
        resp["data"] = data[0]

        return 1, resp
    
    def rc_fastComplete(self):
        
        yabiaoFinish = Game.res_mgr.res_common.get("yabiaoFinish")
        if not yabiaoFinish:
            return 0, errcode.EC_NORES

        t = time.time()
        
        if self.player.yabiao.time<t:
            return 0, errcode.EC_FASTCOMPLETE_TIME_BAD

        days = self.player.base.GetServerOpenDay()
        ares = Game.res_mgr.res_activity.get(constant.ACTIVITY_YABIAO)
        startD = ares.openDayRange[0]
        from game.mgr.room import get_rpc_room
        rpc_room = get_rpc_room(startD<=days)
        if not rpc_room:
            return 0, errcode.EC_GETD_RPC_ROOM_FAIL

        respBag = self.player.bag.costItem(yabiaoFinish.arrayint2, constant.ITEM_COST_FASTCOMPLETE, wLog=True)
        if not respBag.get("rs", 0):
            return 0, errcode.EC_COST_ERR

        rrv=rpc_room.bye(1,self.player.id)
        if not rrv:
            return 0, errcode.EC_CALL_RPC_ROOM_FAIL

        self.player.yabiao.setTimeFinish()

        dUpdate = self.player.packRespBag(respBag)
        dUpdate["jiebiao"] = self.player.yabiao.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp
        
    def rc_getHusongRewardUI(self):
        resp={}
        dUpdate = {}

        dUpdate["jiebiao"] = self.player.yabiao.to_init_data()
    
        resp["allUpdate"] = dUpdate
        return 1,resp

    def rc_getHusongReward(self):

        yabiaoJiebiaoLimit = Game.res_mgr.res_common.get("yabiaoJiebiaoLimit")
        if not yabiaoJiebiaoLimit:
            return 0, errcode.EC_NORES
        # yabiaoDoubleTime = Game.res_mgr.res_common.get("yabiaoDoubleTime")
        # if not yabiaoDoubleTime:
        #     return 0, errcode.EC_NORES

        res = Game.res_mgr.res_yabiao.get(self.player.yabiao.quality)
        if not res:
            return 0, errcode.EC_NORES
        
        if self.player.yabiao.time==0:
            return 0, errcode.EC_HUSONGREWARD_NOSTART
        
        t = time.time()
        if self.player.yabiao.time>t:
            return 0, errcode.EC_HUSONGREWARD_TIMENOABLE

        # mul=1
        # currHour = gtime.current_hour()
        # if currHour in yabiaoDoubleTime.arrayint1:
        #     mul=2

        mul = self.player.yabiao.mul
        
        reward = {}
        for kk, vv in res.reward.items():
            reward[kk]=vv*mul
        
        bid = self.player.yabiao.getBecatchID()
        bidlen=len(bid)
        if bidlen>yabiaoJiebiaoLimit.i:
            bidlen=yabiaoJiebiaoLimit.i

        
        if 5!=self.player.yabiao.quality:
            for _ in range(bidlen):
                for kk, vv in res.rob.items():
                    reward[kk]-=vv
        

        self.player.yabiao.finishYabiao()

        # # 意外绑元奖励
        # DaySurpriseRewardNumRes = Game.res_mgr.res_common.get("DaySurpriseRewardNum")  # 每日意外绑元获得
        # iDayRewardNum = self.player.cycleDay.Query("DaySurpriseRewardNum", 0)
        # if iDayRewardNum < DaySurpriseRewardNumRes.i:
        #     DaySurpriseRes = Game.res_mgr.res_daySurprise.get(constant.DAY_SURPRISE_REWARD_3)
        #     if DaySurpriseRes and random.randint(1, 10000) <= DaySurpriseRes.odds:
        #         for iNo, iNum in DaySurpriseRes.reward.items():
        #             if reward.get(iNo):
        #                 reward[iNo] += iNum
        #             else:
        #                 reward[iNo] = iNum
        #         # 发送世界聊天
        #         for addr, logic in Game.rpc_logic_game:
        #             if logic:
        #                 logic.sendSystemTemplateMSG(DaySurpriseRes.chatId, [self.player.name])

        respBag = self.player.bag.add(reward, constant.ITEM_ADD_HUSONGREWARD, wLog=True)

        resp={}
        dUpdate = self.player.packRespBag(respBag)
        dUpdate["jiebiao"] = self.player.yabiao.to_init_data()
        resp["allUpdate"] = dUpdate
        return 1,resp

    def rc_robHusongCar(self,id):
        yabiaoJiebiaoLimit = Game.res_mgr.res_common.get("yabiaoJiebiaoLimit")
        if not yabiaoJiebiaoLimit:
            return 0, errcode.EC_NORES

        yabiaoJiebiaoNum = Game.res_mgr.res_common.get("yabiaoJiebiaoNum")
        if not yabiaoJiebiaoNum:
            return 0, errcode.EC_NORES

        yabiaoDoubleTime = Game.res_mgr.res_common.get("yabiaoDoubleTime")
        if not yabiaoDoubleTime:
            return 0, errcode.EC_NORES

        if self.player.yabiao.getYabiaoRob()>=yabiaoJiebiaoNum.i:
            return 0, errcode.EC_ROBHUSONG_USEUP

        days = self.player.base.GetServerOpenDay()
        ares = Game.res_mgr.res_activity.get(constant.ACTIVITY_YABIAO)
        startD = ares.openDayRange[0]
        from game.mgr.room import get_rpc_room
        rpc_room = get_rpc_room(startD<=days)
        if not rpc_room:
            return 0, errcode.EC_GETD_RPC_ROOM_FAIL

        rrv = rpc_room.getOneByServerNo(1,config.serverNo,id)
        if not rrv:
            return 0, errcode.EC_CALL_RPC_ROOM_FAIL
        
        data = rrv["v"]

        if len(data)==0:
            return 0, errcode.EC_HUSONG_NOFOUNDONE
        
        res = Game.res_mgr.res_yabiao.get(data[0]["data"]["quality"])
        if not res:
            return 0, errcode.EC_NORES
        
        if yabiaoJiebiaoLimit.i<=len(data[0]["data"]["becatchID"]):
            return 0, errcode.EC_ROBHUSONG_LIMIT

        if self.player.id in data[0]["data"]["becatchID"]:
            return 0, errcode.EC_ROBHUSONG_ALREADY

        from game.mgr.logicgame import LogicGame
        proxy = get_proxy_by_addr(data[0]["addr"], LogicGame._rpc_name_)
        if not proxy:
            return 0, errcode.EC_GETD_LOGIC_PROXY_ERR

        fdata = self.player.GetFightData()

        bhname = ""
        from game.mgr.guild import get_rpc_guild
        rpc_guild = get_rpc_guild(self.player.guild.GetGuildId())
        if rpc_guild:
            bhname = rpc_guild.getName()

        import app
        historydata={"addr":app.addr,"id":self.player.id,"endtime":0,"name":self.player.name,"data":{"quality":0,"power":self.player.base.fa,"bhname":bhname,"sex":self.player.base.GetSex()}}

        resp  = proxy.robHusongCar(self.player.id,data[0],fdata,historydata)
        if not resp:
            return 0, errcode.EC_CALL_LOGIC_PROXY_ERR

        self.player.yabiao.addYabiaoRob()

        respBag = {}
        fightResult = resp["fightLog"]["result"].get("win", 0)
        if fightResult:
            self.player.yabiao.addHistory(3,data[0])

            mul=1
            currHour = gtime.current_hour()
            if currHour in yabiaoDoubleTime.arrayint1:
                mul=2
            
            reward = {}
            for kk, vv in res.rob.items():
                reward[kk]=vv*mul

            respBag = self.player.bag.add(reward, constant.ITEM_ADD_ROBREWARD, wLog=True)
        else:
            self.player.yabiao.addHistory(2,data[0])

        dUpdate = self.player.packRespBag(respBag)
        dUpdate["jiebiao"] = self.player.yabiao.to_init_data()

        resp["allUpdate"] = dUpdate
        return 1, resp
            
    def rc_flashHusongCar(self,type):
        yabiaoFlash = Game.res_mgr.res_common.get("yabiaoFlash")
        if not yabiaoFlash:
            return 0, errcode.EC_NORES
        yabiaoFlashMax = Game.res_mgr.res_common.get("yabiaoFlashMax")
        if not yabiaoFlashMax:
            return 0, errcode.EC_NORES
        yabiaoFlashMaxPriority = Game.res_mgr.res_common.get("yabiaoFlashMaxPriority")
        if not yabiaoFlashMaxPriority:
            return 0, errcode.EC_NORES
        
        if self.player.yabiao.time!=0:
            return 0, errcode.EC_FLASHCAR_TIMENOABLE

        cost=yabiaoFlash.arrayint2
        if type:
            cost = yabiaoFlashMax.arrayint2

        if type:
            respBag = self.player.bag.costItem(yabiaoFlashMaxPriority.arrayint2, constant.ITEM_COST_FALSHCAR, wLog=True)
            if not respBag.get("rs", 0):
                respBag1 = self.player.bag.costItem(cost, constant.ITEM_COST_FALSHCAR, wLog=True)
                if not respBag1.get("rs", 0):
                    return 0, errcode.EC_COST_ERR
                else:
                    respBag = self.player.mergeRespBag(respBag, respBag1)
        else:
            respBag = self.player.bag.costItem(cost, constant.ITEM_COST_FALSHCAR, wLog=True)
            if not respBag.get("rs", 0):
                return 0, errcode.EC_COST_ERR

        if type:
            self.player.yabiao.flashCarMax()
        else:
            self.player.yabiao.flashCar()

        dUpdate = self.player.packRespBag(respBag)
        dUpdate["jiebiao"] = self.player.yabiao.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp
    
    def rc_getHusongHistroy(self):
        resp={}
        resp["list"]=self.player.yabiao.getHistory()
        return 1, resp

    def rc_revengeHusongCar(self,id):
        
        yabiaoDoubleTime = Game.res_mgr.res_common.get("yabiaoDoubleTime")
        if not yabiaoDoubleTime:
            return 0, errcode.EC_NORES
    

        if str(id) not in self.player.yabiao.history:
            return 0, errcode.EC_REVENGEHUSONG_NOIN

        if self.player.yabiao.history[str(id)]["type"]!=0:
            return 0, errcode.EC_REVENGEHUSONG_NOTYPE

        res = Game.res_mgr.res_yabiao.get(self.player.yabiao.history[str(id)]["data"]["data"]["quality"])
        if not res:
            return 0, errcode.EC_NORES
          
        
        from game.mgr.logicgame import LogicGame
        proxy = get_proxy_by_addr(self.player.yabiao.history[str(id)]["data"]["addr"], LogicGame._rpc_name_)
        if not proxy:
            return 0, errcode.EC_GETD_LOGIC_PROXY_ERR
  
        fdata = self.player.GetFightData()

        bhname = ""
        from game.mgr.guild import get_rpc_guild
        rpc_guild = get_rpc_guild(self.player.guild.GetGuildId())
        if rpc_guild:
            bhname = rpc_guild.getName()

        historydata={"id":self.player.id,"endtime":0,"name":self.player.name,"data":{"quality":self.player.yabiao.history[str(id)]["data"]["data"]["quality"],"power":self.player.base.fa,"bhname":bhname,"sex":self.player.base.GetSex()}}

        resp  = proxy.revengeHusongCar(self.player.id,{"id":self.player.yabiao.history[str(id)]["data"]["id"]},fdata,historydata)
        if not resp:
            return 0, errcode.EC_CALL_LOGIC_PROXY_ERR

        self.player.yabiao.modfiyHistoryFinish(id)

        respBag = {}
        fightResult = resp["fightLog"]["result"].get("win", 0)
        if fightResult:
            mul=1
            currHour = gtime.current_hour()
            if currHour in yabiaoDoubleTime.arrayint1:
                mul=2
            
            reward = {}
            for kk, vv in res.rob.items():
                reward[kk]=vv*mul

            respBag = self.player.bag.add(reward, constant.ITEM_ADD_REVREWARD, wLog=True)

        dUpdate = self.player.packRespBag(respBag)
        dUpdate["jiebiao"] = self.player.yabiao.to_init_data()

        resp["allUpdate"] = dUpdate
        return 1, resp