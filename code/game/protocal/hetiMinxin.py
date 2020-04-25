#!/usr/bin/env python
# -*- coding:utf-8 -*-
import random
import copy
from game.define import errcode, constant, msg_define
from game import Game
from game.common import utility
import time
from gevent import sleep

class HetiRpcMixin(object):
    if 0:
        from game.core import player as player_md
        player = player_md.Player()


    def rc_hetiBuy(self):

        vipLv = self.player.vip.GetVipLv()
        vipRes = Game.res_mgr.res_vip.get(vipLv, None)
        if not vipRes:
            return 0, errcode.EC_NORES

        buyCostRes = Game.res_mgr.res_common.get("hetiBuyCost")
        if not buyCostRes:
            return 0, errcode.EC_NORES
            
        hetiBuyNum = Game.res_mgr.res_common.get("hetiBuyNum")
        if not hetiBuyNum:
            return 0, errcode.EC_NORES

        

        num=self.player.heti.GethetiBuyNum()
        if num>=vipRes.hetiBuyNum+hetiBuyNum.i:
            return 0, errcode.EC_HETI_BUYMAX

        if self.player.heti.HetiNum==0:
            return 0, errcode.EC_HETI_NUMZERO

        respBag = self.player.bag.costItem(buyCostRes.arrayint2, constant.ITEM_COST_HETI, wLog=True)
        if not respBag.get("rs", 0):
            return 0, errcode.EC_COST_ERR

        self.player.heti.buyNum()

        dUpdate = self.player.packRespBag(respBag)
        dUpdate["heti"] = self.player.heti.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp

    def rc_hetiInfo(self):



        dUpdate = {}

        dUpdate["heti"] = self.player.heti.to_init_data()

        # if resp_items or resp_equips:
        #     dUpdate["bag"] = self.player.bag.to_update_data(items=resp_items, equips=resp_equips)
        # if resp_wallet:
        #     dUpdate["wallet"] = self.player.wallet.to_update_data(resp_wallet)

        
        resp = {
            "allUpdate": dUpdate,
        }

        return 1, resp

    def rc_hetiStart(self):

        heticishu = Game.res_mgr.res_common.get("heticishu")
        if not heticishu:
            return 0, errcode.EC_NORES

        
        n=self.player.heti.HetiNum
        if heticishu.i<=n:
            return 0, errcode.EC_HETI_MAX
        

        self.player.heti.start()

        self.player.safe_pub(msg_define.MSG_MINI_GAME_JOIN)

        dUpdate = {}
        dUpdate["heti"] = self.player.heti.to_init_data()

        # if resp_items or resp_equips:
        #     dUpdate["bag"] = self.player.bag.to_update_data(items=resp_items, equips=resp_equips)
        # if resp_wallet:
        #     dUpdate["wallet"] = self.player.wallet.to_update_data(resp_wallet)

        
        resp = {
            "allUpdate": dUpdate,
        }

        return 1, resp

    def rc_hetiAuto(self):
        dictx = {}
        for key in self.player.heti.obj:
            dictx[key] = dictx.get(key, 0) + 1
        
        for key,value in dictx.items():
            if(value == max(dictx.values())):
                break

        print("========",key)
        if key=="*-*":
            return self.rc_hetiCao(0)
        else:
            return self.rc_hetiHebing(key,0,0)

    def rc_hetiCao(self,data):
        iCurId = self.player.map.mapSubId
        mapSubRes = Game.res_mgr.res_mapSub.get(iCurId)
        if not mapSubRes:
            return 0, errcode.EC_NORES
        
        hetiTime = Game.res_mgr.res_common.get("hetiTime")
        if not hetiTime:
            return 0, errcode.EC_NORES
        
        nt=time.time()
        if nt>self.player.heti.st+hetiTime.i+3:
            return 0, errcode.EC_HETI_TIMEOUT

        if "*-*" not in self.player.heti.obj:
            return 0, errcode.EC_HETI_NOFOUND
        
        rid, score, boxtype=self.player.heti.caoPre()
        obj="*-*"
        dReward={}
        if rid:
            rewardRes = Game.res_mgr.res_reward.get(rid)
            if not rewardRes:
                return 0, errcode.EC_NORES
            dReward=rewardRes.doReward()
            keys = list(dReward.keys())
            if boxtype == 1: #大奖
                for itemid in keys:
                    if itemid == constant.CURRENCY_COIN:
                        dReward[itemid] = mapSubRes.offcoin * 300
            elif boxtype == 2: #小将
                for itemid in keys:
                    if itemid == constant.CURRENCY_COIN:
                        dReward[itemid] = mapSubRes.offcoin * 90
        else:
            obj=self.player.heti.cao()

        respBag = self.player.bag.add(dReward, constant.ITEM_ADD_HETI_REWARD, wLog=True)
        
        self.player.heti.addReward(dReward)

        dUpdate = self.player.packRespBag(respBag)
        dUpdate["heti"] = self.player.heti.to_init_data()
        resp = {
            "allUpdate": dUpdate,
            "data": data,
            "obj": obj,
            "score": score,
        }
        return 1, resp

    def rc_hetiHebing(self,obj,data1,data2):
        iCurId = self.player.map.mapSubId
        mapSubRes = Game.res_mgr.res_mapSub.get(iCurId)
        if not mapSubRes:
            return 0, errcode.EC_NORES

        hetihebingReward = Game.res_mgr.res_common.get("hetihebingReward")
        if not hetihebingReward:
            return 0, errcode.EC_NORES

        rewardRes = Game.res_mgr.res_reward.get(hetihebingReward.i)
        if not rewardRes:
            return 0, errcode.EC_NORES
        dReward=rewardRes.doReward()
        keys = list(dReward.keys())
        for itemid in keys:
            if itemid == constant.CURRENCY_COIN:
                dReward[itemid] = mapSubRes.offcoin * 40

        hetiTime = Game.res_mgr.res_common.get("hetiTime")
        if not hetiTime:
            return 0, errcode.EC_NORES
        
        nt=time.time()
        if nt>self.player.heti.st+hetiTime.i+3:
            return 0, errcode.EC_HETI_TIMEOUT
        
        if obj=="*-*":
            return 0, errcode.EC_PARAMS_ERR
        
        if self.player.heti.obj.count(obj)<2:
            return 0, errcode.EC_HETI_NOFOUND
        
        objs,score=self.player.heti.hebing(obj)

        respBag = self.player.bag.add(dReward, constant.ITEM_ADD_HETI_REWARD, wLog=True)
        
        self.player.heti.addReward(dReward)

        dUpdate = self.player.packRespBag(respBag)
        dUpdate["heti"] = self.player.heti.to_init_data()
        resp = {
            "allUpdate": dUpdate,
            "data1": data1,
            "data2": data2,
            "obj": objs,
            "score": score,
        }
        return 1, resp


    def rc_hetiDel(self,obj,data):


        hetiTime = Game.res_mgr.res_common.get("hetiTime")
        if not hetiTime:
            return 0, errcode.EC_NORES
        
        nt=time.time()
        if nt>self.player.heti.st+hetiTime.i+3:
            return 0, errcode.EC_HETI_TIMEOUT
        
        if obj=="*-*":
            return 0, errcode.EC_PARAMS_ERR
        
        if obj not in self.player.heti.obj:
            return 0, errcode.EC_HETI_NOFOUND
        
        score=self.player.heti.delv(obj)


        dUpdate = {}

        dUpdate["heti"] = self.player.heti.to_init_data()

        # sleep(1)
        
        resp = {
            "allUpdate": dUpdate,
            "data": data,
            "score": score,
            "obj": "*-*",
        }

        return 1, resp



    def rc_hetiDone(self):

        orank,nrank=self.player.heti.done()
        
        resp = {
            "item": self.player.heti.item,
            "score": self.player.heti.histscore,
            "gold": self.player.heti.histgold,
            "rank": nrank,
            "rankHis": orank,
        }

        return 1, resp