#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import random
import time

from game.define import errcode, constant, msg_define
from game import Game
from game.common import utility

from corelib import log, spawn
from game.fight import createFight

class MapMixin(object):
    if 0:
        from game.core import player as player_md
        player = player_md.Player()


    def rc_mapRewardTimeout(self):
        dUpdate = {}
        dUpdate["map"] = self.player.map.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp

    
    def rc_mapGetReward(self):

        offexp,offcoin,offexplore,offpetexp,rewardmap = self.player.map.gainOff()

        reward={}
        for k,v in rewardmap.items():
            k=int(k)
            reward[k]=reward.get(k,0)+v

        

        
        
        reward[constant.CURRENCY_EXP]=reward.get(constant.CURRENCY_EXP,0)+offexp
        reward[constant.CURRENCY_COIN]=reward.get(constant.CURRENCY_COIN,0)+offcoin
        reward[constant.CURRENCY_EXPLORE]=reward.get(constant.CURRENCY_EXPLORE,0)+offexplore
        reward[constant.CURRENCY_PETEXP]=reward.get(constant.CURRENCY_PETEXP,0)+offpetexp

        respBag = self.player.bag.add(reward, constant.ITEM_ADD_MAP_REWARD, wLog=True)

        # 打包返回信息
        dUpdate = self.player.packRespBag(respBag)

        dUpdate["map"] = self.player.map.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp


    def rc_mapObjTimeout(self):
        dUpdate = {}
        dUpdate["map"] = self.player.map.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp

    
    def rc_mapGetObj(self,resid):

        print("======rc_mapGetObj====",resid)

        
        
        objid = self.player.map.gainObj(resid)
        if not objid:
            return 0,errcode.EC_ALREADY_GONG

        objres = Game.res_mgr.res_mapObject.get(objid)
        if not objres:
            return 0,errcode.EC_NORES

        respBag={}
        
        reward={}

        if objres.rewardid:
            rewardRes = Game.res_mgr.res_reward.get(objres.rewardid)
            if not rewardRes:
                return 0,errcode.EC_NORES

            reward1 = rewardRes.doReward()

            for k,v in reward1.items():
                reward[k]=reward.get(k,0)+v

        
        if objres.reward:
            for k,v in objres.reward.items():
                reward[k]=reward.get(k,0)+v

        
        if reward:
            respBag = self.player.bag.add(reward, constant.ITEM_ADD_MAP_OBJ, wLog=True)

        isRescue=False
        if objres.rescueSystemKey:
            isRescue=True
            self.player.rescue.rescueSystemKey(objres.rescueSystemKey)
        if objres.rescueAuto:
            isRescue=True
            for _ in range(objres.rescueAuto):
                self.player.rescue.rescueAuto()


        # 打包返回信息
        dUpdate = self.player.packRespBag(respBag)

        dUpdate["map"] = self.player.map.to_init_data()
        
        if isRescue:
            dUpdate["rescue"] = self.player.rescue.to_init_data()

        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp

    
    def rc_mapQuickUse(self):

        res=Game.res_mgr.res_mapSub.get(self.player.map.mapSubId)
        if not res:
            return 0,errcode.EC_NORES

        mapQuickTimes=Game.res_mgr.res_common.get("mapQuickTimes")
        if not mapQuickTimes:
            return 0,errcode.EC_NORES

        mapQuickCostCharge=Game.res_mgr.res_common.get("mapQuickCostCharge")
        if not mapQuickCostCharge:
            return 0,errcode.EC_NORES

        mapQuickCost=Game.res_mgr.res_common.get("mapQuickCost")
        if not mapQuickCost:
            return 0,errcode.EC_NORES



        mapQuickUseTimesCharge=Game.res_mgr.res_common.get("mapQuickUseTimesCharge")
        if not mapQuickUseTimesCharge:
            return 0,errcode.EC_NORES

        mapQuickUseTimes=Game.res_mgr.res_common.get("mapQuickUseTimes")
        if not mapQuickUseTimes:
            return 0,errcode.EC_NORES
        
        times=mapQuickUseTimesCharge.i
        
        
        costL=mapQuickCostCharge.arrayint2

        nt=time.time()
        if self.player.map.ChargeEndTime.get(1,0)<nt:
            costL=mapQuickCost.arrayint2
            times=mapQuickUseTimes.i


        quickv=self.player.map.getquickUse()
        if quickv>=times:
            return 0,errcode.EC_EXHAUSTED

        costIdx=quickv
        if costIdx>=len(costL):
            costIdx=len(costL)-1

        cost={}
        cost[costL[costIdx][0]]=costL[costIdx][1]
        

        offexp=res.offexp*mapQuickTimes.i
        offexplore=res.offexplore*mapQuickTimes.i
        offcoin=res.offcoin*mapQuickTimes.i
        offpetexp=res.offpetexp*mapQuickTimes.i
        
        reward={}
        for _ in range(mapQuickTimes.i):
            for offreward in res.offreward:
                rewardRes = Game.res_mgr.res_reward.get(offreward)
                resp = rewardRes.doReward()
                for k,v in resp.items():
                    reward[k]=reward.get(k,0)+v


        
        respBag1 = self.player.bag.costItem(cost, constant.ITEM_COST_ZHUANPAN_ROLL, wLog=True)
        if not respBag1.get("rs", 0):
            return 0, errcode.EC_COST_ERR



        reward[constant.CURRENCY_EXP]=reward.get(constant.CURRENCY_EXP,0)+offexp
        reward[constant.CURRENCY_COIN]=reward.get(constant.CURRENCY_COIN,0)+offcoin
        reward[constant.CURRENCY_EXPLORE]=reward.get(constant.CURRENCY_EXPLORE,0)+offexplore
        reward[constant.CURRENCY_PETEXP]=reward.get(constant.CURRENCY_PETEXP,0)+offpetexp

        respBag = self.player.bag.add(reward, constant.ITEM_ADD_MAP_QUICK_USE, wLog=True)

        respBag = self.player.mergeRespBag(respBag, respBag1)

        
        quickv+=1
        self.player.map.setquickUse(quickv)

        # 打包返回信息
        dUpdate = self.player.packRespBag(respBag)

        dUpdate["map"] = self.player.map.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp

    def rc_mapQuickFree(self):

        res=Game.res_mgr.res_mapSub.get(self.player.map.mapSubId)
        if not res:
            return 0,errcode.EC_NORES

        mapQuickTimes=Game.res_mgr.res_common.get("mapQuickTimes")
        if not mapQuickTimes:
            return 0,errcode.EC_NORES

        mapQuickFreeTimesCharge=Game.res_mgr.res_common.get("mapQuickFreeTimesCharge")
        if not mapQuickFreeTimesCharge:
            return 0,errcode.EC_NORES

        mapQuickFreeTimes=Game.res_mgr.res_common.get("mapQuickFreeTimes")
        if not mapQuickFreeTimes:
            return 0,errcode.EC_NORES
        
        times=mapQuickFreeTimesCharge.i
        nt=time.time()
        if self.player.map.ChargeEndTime.get(1,0)<nt:
            times=mapQuickFreeTimes.i

        quickv=self.player.map.getquickFree()
        if quickv>=times:
            return 0,errcode.EC_EXHAUSTED
        

        offexp=res.offexp*mapQuickTimes.i
        offexplore=res.offexplore*mapQuickTimes.i
        offcoin=res.offcoin*mapQuickTimes.i
        offpetexp=res.offpetexp*mapQuickTimes.i
        
        reward={}
        for _ in range(mapQuickTimes.i):
            
            for offreward in res.offreward:
                rewardRes = Game.res_mgr.res_reward.get(offreward)
                resp = rewardRes.doReward()
                for k,v in resp.items():
                    reward[k]=reward.get(k,0)+v



        reward[constant.CURRENCY_EXP]=reward.get(constant.CURRENCY_EXP,0)+offexp
        reward[constant.CURRENCY_COIN]=reward.get(constant.CURRENCY_COIN,0)+offcoin
        reward[constant.CURRENCY_EXPLORE]=reward.get(constant.CURRENCY_EXPLORE,0)+offexplore
        reward[constant.CURRENCY_PETEXP]=reward.get(constant.CURRENCY_PETEXP,0)+offpetexp

        respBag = self.player.bag.add(reward, constant.ITEM_ADD_MAP_QUICK_FREE, wLog=True)

        quickv+=1
        self.player.map.setquickFree(quickv)

        # 打包返回信息
        dUpdate = self.player.packRespBag(respBag)

        dUpdate["map"] = self.player.map.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp

    def rc_mapNormalFight(self,boss=1):
        """场景普通战斗"""
        iCurId = self.player.map.mapSubId
        mapSubRes = Game.res_mgr.res_mapSub.get(iCurId)
        if not mapSubRes:
            return 0, errcode.EC_NORES

        if self.player.map.passSubId >= iCurId:
            return 0, errcode.EC_CODE_10002

        respBag = {}
        fightLog={}


        barrRes = Game.res_mgr.res_barrier.get(mapSubRes.bossBarrId)
        if not barrRes:
            return 0, errcode.EC_NORES

        barrRes.rewardId=100000
        rewardRes = Game.res_mgr.res_reward.get(barrRes.rewardId)
        if not rewardRes:
            return 0, errcode.EC_NORES

        ipassSubId = self.player.map.passSubId
        resEncounter = Game.res_mgr.res_passId_encounter.get(ipassSubId)
        if resEncounter:
            if self.player.map.GetPassEncounterId() < resEncounter.id:
                return 0, errcode.EC_ENCOUNTER_FIGHT_NOT_FINISH

        t1 = time.time()

        fightobj = createFight(constant.FIGHT_TYPE_100)
        rs = fightobj.init_data(self.player.GetFightData(constant.BATTLE_ARRAY_TYPE_NORMAL), barrRes.id)
        if not rs:
            return 0, errcode.EC_INIT_BARR_FAIL
        fightLog = fightobj.doFight()
        log_end = fightLog.get("end", {})
        winerList = log_end.get("winerList", [])
        fightResult = 1 if self.player.id in winerList else 0

        # 普通场景战斗事件消息
        self.player.safe_pub(msg_define.MSG_MORMAL_SCENE_FIGHT, fightResult)
        if fightResult:
            dReward = rewardRes.doReward()
            respBag = self.player.bag.add(dReward, constant.ITEM_ADD_MORMAL_SCENE_FIGHT, wLog=True)

        t2 = time.time()
        Game.glog.log2File("rc_mapNormalFight", "%s|%s|%s" % (t2 - t1, iCurId, barrRes.id))
    

        # 打包返回信息
        dUpdate = self.player.packRespBag(respBag)
        dUpdate["map"] = self.player.map.to_init_data()
        resp = {
            "fightLog": fightLog,
            "allUpdate": dUpdate,
        }
        return 1, resp

    # 领取关卡奖励(getMapPassReward)
    # 请求
    # 返回
    #     上次领奖的关卡id(rewardSubId, int)
    #     主动推送刷新(allUpdate, json)
    #         游戏模型 - 货币
    #         游戏模型 - 角色背包
    def rc_getMapPassReward(self,resid):
        ipassSubId = self.player.map.passSubId
        mapSubRes = Game.res_mgr.res_mapSub.get(resid)
        if not mapSubRes:
            return 0, errcode.EC_NORES

        if resid in self.player.map.rewardSubId:
            return 0, errcode.EC_ALREADY_REWARD

        if ipassSubId<resid:
            return 0, errcode.EC_NOT_ENOUGH


        self.player.map.SetRewardSubId(mapSubRes.id)
        respBag = self.player.bag.add(mapSubRes.passReward, constant.ITEM_ADD_MORMAL_SCENE_PASS, wLog=True)
        
        # 打包返回信息
        dUpdate = self.player.packRespBag(respBag)
        dUpdate["map"] = self.player.map.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp

    # 请求进入下一个地图(enterNextMap)
    # 请求
    #     地图id(mapId, int)
    # 返回
    #     关卡id(mapSubId, int)当前所在
    def rc_enterNextMap(self, mapId):
        iCurId = self.player.map.mapSubId
        mapSubRes = Game.res_mgr.res_mapSub.get(iCurId)
        if not mapSubRes:
            return 0, errcode.EC_NORES
        iNextId = iCurId + 1
        nextMapSubRes = Game.res_mgr.res_mapSub.get(iNextId)
        if not nextMapSubRes:
            return 0, errcode.EC_NORES
        if nextMapSubRes.mapId != mapId: #不是下一个地图id
            return 0, errcode.EC_NOT_ABLE
        mapRes = Game.res_mgr.res_mapWorld.get(mapId)
        if not mapRes:
            return 0, errcode.EC_NORES
        iLv = self.player.base.GetLv()
        if iLv < mapRes.lv:
            return 0, errcode.EC_NOT_ENOUGH

        #如果遭遇战没过，不允许进入下一个地图
        ipassSubId = self.player.map.passSubId
        resEncounter = Game.res_mgr.res_passId_encounter.get(ipassSubId)
        if resEncounter:
            if self.player.map.GetPassEncounterId() < resEncounter.id:
                return 0, errcode.EC_ENTER_MAP_LIMIT

        self.player.map.SetMapSubId(iNextId)
        dUpdate={}
        # 抛事件
        self.player.safe_pub(msg_define.MSG_ENTER_MAP, mapId)

        dUpdate["map"] = self.player.map.to_init_data()

        # 打包返回信息
        resp = {
            "mapSubId": iNextId,
            "allUpdate": dUpdate,
        }
        return 1, resp

    
    
    # 遭遇战战斗(encounterFight)
    # 请求
    #     遭遇战id(encounterId, int)
    # 返回
    #     战报(fightLog, json)
    #     主动推送刷新(allUpdate, json)
    #         游戏模型-货币
    #         游戏模型-角色背包
    #         游戏模型-地图
    #             已通关遭遇战id(passEncounterId, int)
    def rc_encounterFight(self, encounterId):
        resEncounter = Game.res_mgr.res_encounter.get(encounterId)
        if not resEncounter:
            return 0, errcode.EC_NORES
        if self.player.map.GetPassEncounterId() >= encounterId:
            return 0, errcode.EC_ENCOUNTER_FIGHT_HAS_FINISH
        ipassSubId = self.player.map.passSubId
        if ipassSubId < resEncounter.passId:
            return 0, errcode.EC_ENCOUNTER_FIGHT_LIMIT
        rewardRes = Game.res_mgr.res_reward.get(resEncounter.rewardId)
        if not rewardRes:
            return 0, errcode.EC_NORES

        fightLog={}
        respBag = {}
        fightResult=1

        # fightobj = Game.fight_mgr.createFight(constant.FIGHT_TYPE_112)
        # rs = fightobj.init_player(self.player)
        # if not rs:
        #     return 0, errcode.EC_INIT_BARR_FAIL
        # rs = fightobj.init_monster_by_user_defined(resEncounter.monster1)
        # if not rs:
        #     return 0, errcode.EC_INIT_BARR_FAIL
        # rs = fightobj.init_monster_by_user_defined(resEncounter.monster2)
        # if not rs:
        #     return 0, errcode.EC_INIT_BARR_FAIL
        # rs = fightobj.init_monster_by_user_defined(resEncounter.monster3)
        # if not rs:
        #     return 0, errcode.EC_INIT_BARR_FAIL
        # fightobj.setEncounterId(encounterId)
        # fightobj.fixEleValue(resEncounter.increase, resEncounter.decrease)
        # fightobj.SetRounds(resEncounter.maxRound)

        # fightLog = fightobj.doFight()
        # fightResult = fightLog["result"].get("win", 0)

        #战斗
        fightobj = createFight(constant.FIGHT_TYPE_100)
        rs = fightobj.init_data(self.player.GetFightData(constant.BATTLE_ARRAY_TYPE_NORMAL), 100000)
        if not rs:
            return 0, errcode.EC_INIT_BARR_FAIL
        fightLog = fightobj.doFight()
        log_end = fightLog.get("end", {})
        winerList = log_end.get("winerList", [])
        fightResult = 1 if self.player.id in winerList else 0




        if fightResult:
            dReward = rewardRes.doReward()
            respBag = self.player.bag.add(dReward, constant.ITEM_ADD_ENCOUNTER_FIGHT, wLog=True)
            self.player.map.SetPassEncounterId(encounterId)
        else:

            # if resEncounter.eleType==1:
            #     self.player.safe_pub(msg_define.MSG_XIANSHITUISONGLIBAO_ENCOUNTER_1_F)
            # elif resEncounter.eleType==2:
            #     self.player.safe_pub(msg_define.MSG_XIANSHITUISONGLIBAO_ENCOUNTER_2_F)
            # elif resEncounter.eleType==3:
            #     self.player.safe_pub(msg_define.MSG_XIANSHITUISONGLIBAO_ENCOUNTER_3_F)
            # elif resEncounter.eleType==4:
            #     self.player.safe_pub(msg_define.MSG_XIANSHITUISONGLIBAO_ENCOUNTER_4_F)
            # elif resEncounter.eleType==5:
            #     self.player.safe_pub(msg_define.MSG_XIANSHITUISONGLIBAO_ENCOUNTER_5_F)
            pass


        showFail = 0
        if encounterId > self.player.map.GetFirstFailEncounterId():
            showFail = 1
            self.player.map.SetFirstFailEncounterId(encounterId)

        # 打包返回信息
        dUpdate = self.player.packRespBag(respBag)
        dUpdate["map"] = self.player.map.to_init_data()
        resp = {
            "fightLog": fightLog,
            "allUpdate": dUpdate,
            "showFail": showFail
        }
        return 1, resp
