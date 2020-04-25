#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import random
import time

from game.define import errcode, constant, msg_define
from game import Game
from game.common import utility

from corelib import log, spawn

class ShopMixin(object):
    if 0:
        from game.core import player as player_md
        player = player_md.Player()

    def rc_shopData(self):


        # 打包返回信息
        dUpdate = {}

        dUpdate["shop"] = self.player.shop.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp

    def rc_shopRefreshFree(self,resid):


        res=Game.res_mgr.res_shopConst.get(resid)
        if not res:
            return 0, errcode.EC_NORES

        if not res.freeRefersh:
            return 0, errcode.EC_NOT_ABLE

        
        xnum = self.player.shop.getRefreshFreeNum()
        
        if res.freeRefersh-xnum[resid]["refershnum"]<=0:
            return 0, errcode.EC_TIMES_FULL

        # print("xnum",xnum)
        
        self.player.shop.manualRefresh(res)
        self.player.shop.CostRefreshFreeNum(resid)

        


        # 打包返回信息
        dUpdate = {}

        dUpdate["shop"] = self.player.shop.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp

    def rc_shopRefreshCost(self,resid):


        res=Game.res_mgr.res_shopConst.get(resid)
        if not res:
            return 0, errcode.EC_NORES

        if not res.costRefersh:
            return 0, errcode.EC_NOT_ABLE

        
        xnum = self.player.shop.getRefreshCostNum()
        

        if res.costRefersh-xnum[resid]["refershnum"]<=0:
            return 0, errcode.EC_TIMES_FULL

        costidx=xnum[resid]["refershnum"]
        if costidx>=len(res.costLadder):
            costidx=len(res.costLadder)-1

        if costidx==-1:
            return 0, errcode.EC_NORES

        cost={}
        cost[res.costLadder[costidx][0]]=res.costLadder[costidx][1]

        respBag = self.player.bag.costItem(cost, constant.ITEM_COST_ZHUANPAN_RESET, wLog=True)
        if not respBag.get("rs", 0):
            return 0, errcode.EC_COST_ERR


        # print("xnum",xnum)
        
        self.player.shop.manualRefresh(res)
        self.player.shop.CostRefreshCostNum(resid)

        


        # 打包返回信息
        dUpdate = self.player.packRespBag(respBag)

        dUpdate["shop"] = self.player.shop.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp

    def rc_shopBuy(self,resid,idx,iscost2,num):
        
        res=Game.res_mgr.res_shopConst.get(resid)
        if not res:
            return 0, errcode.EC_NORES

        if idx>=len(res.manualgroup):
            print("==========")
            return 0, errcode.EC_NORES


        

        sd=self.player.shop.getshopdata()
        gid=sd[resid][idx]["id"]
        gnum=sd[resid][idx]["buynum"]

        gres=Game.res_mgr.res_shopGroup.get(gid)
        if not gres:
            return 0, errcode.EC_NORES

        if gres.limitNum:
            lnum=gres.limitNum-gnum
            if lnum<num:
                return 0, errcode.EC_EXHAUSTED
            

        


        cost={}
        reward={}
        for _ in range(num):
            onecost=gres.cost1
            if iscost2:
                onecost=gres.cost2
            
            for k,v in onecost.items():
                cost[k]=cost.get(k,0)+v

            for k,v in gres.reward.items():
                reward[k]=reward.get(k,0)+v

        

        respBag1 = self.player.bag.costItem(cost, constant.ITEM_COST_SHOP, wLog=True)
        if not respBag1.get("rs", 0):
            return 0, errcode.EC_COST_ERR
            
        dd=self.player.shop.getGroupID2BuyNum(gres.refCycle)
        dd[gid]=gnum+num
        self.player.shop.setGroupID2BuyNum(gres.refCycle,dd)

        respBag = self.player.bag.add(reward, constant.ITEM_ADD_SHOP, wLog=True, mail=True)

        respBag = self.player.mergeRespBag(respBag, respBag1)
        
        # 打包返回信息
        dUpdate = self.player.packRespBag(respBag)

        dUpdate["shop"] = self.player.shop.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp