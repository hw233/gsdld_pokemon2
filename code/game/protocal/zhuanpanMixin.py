#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import random
import time

from game.define import errcode, constant, msg_define
from game import Game
from game.common import utility

from corelib import log, spawn

class ZhuanpanMixin(object):
    if 0:
        from game.core import player as player_md
        player = player_md.Player()



    def rc_zhuanpanRoll(self,resid, ten):
        
        res=Game.res_mgr.res_zhuanpanSystem.get(resid)
        if not res:
            return 0,errcode.EC_NORES

        times=1
        cost={}
        if ten:            
            times=res.Ten
            cost=res.costTen
        else:
            cost=res.cost
            times=1
 
        respBag1 = self.player.bag.costItem(cost, constant.ITEM_COST_ZHUANPAN_ROLL, wLog=True)
        if not respBag1.get("rs", 0):
            return 0, errcode.EC_COST_ERR


        reward={}

        RewardData=self.player.zhuanpan.getRewardData()


        idxs=[]

        haveDisable=False

        for _ in range(times):
            idxWeight = []
            for v in res.idxWeight:
                if v[0] in RewardData[resid]["disable"]:
                    continue
                idxWeight.append(v)
                
            idx = utility.Choice(idxWeight)

            

            isDisable=res.idxCanDisable[idx]
            if isDisable:
                haveDisable=True

            
            
            if isDisable and idx not in RewardData[resid]["disable"]:
                RewardData[resid]["disable"].append(idx)
            
            idxs.append(idx)
            poolID=RewardData[resid]["data"][idx]

            self.player.zhuanpan.addscore(res)


            resPool=Game.res_mgr.res_zhuanpanPool.get(poolID)
            if resPool:
                for kk,vv in resPool.reward.items():
                    reward[kk]=reward.get(kk,0)+vv

            if isDisable:
                Game.rpc_commonres_mgr.zhuanpanAddMsg(resid,self.player.name,poolID)


        respBag = self.player.bag.add(reward, constant.ITEM_ADD_ZHUANPAN_ROLL, wLog=True, mail=True)

        respBag = self.player.mergeRespBag(respBag, respBag1)

        self.player.zhuanpan.setRewardData(RewardData)
        

        # 打包返回信息
        dUpdate = self.player.packRespBag(respBag)

        dUpdate["zhuanpan"] = self.player.zhuanpan.to_init_data()
        resp = {
            "allUpdate": dUpdate,
            "idx":idxs
        }

        if haveDisable:
            resp["msg"]=Game.rpc_commonres_mgr.zhuanpanGetMsg(resid)

        return 1, resp

    def rc_zhuanpanReset(self,resid):

        res=Game.res_mgr.res_zhuanpanSystem.get(resid)
        if not res:
            return 0,errcode.EC_NORES

        respBag = self.player.bag.costItem(res.costReset, constant.ITEM_COST_ZHUANPAN_RESET, wLog=True)
        if not respBag.get("rs", 0):
            return 0, errcode.EC_COST_ERR

        self.player.zhuanpan.reset(resid)
        # 打包返回信息
        dUpdate = self.player.packRespBag(respBag)

        dUpdate["zhuanpan"] = self.player.zhuanpan.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp



    def rc_zhuanpanFreeReset(self,resid):


        res=Game.res_mgr.res_zhuanpanSystem.get(resid)
        if not res:
            return 0,errcode.EC_NORES

        t=self.player.zhuanpan.freeResetTime.get(resid,0)

        nt=time.time()
        if t+res.free>nt:
            return 0,errcode.EC_NOT_ABLE


        self.player.zhuanpan.reset(resid)

        self.player.zhuanpan.freeResetTime[resid]=nt
        self.player.zhuanpan.markDirty()
        # 打包返回信息
        dUpdate = {}

        dUpdate["zhuanpan"] = self.player.zhuanpan.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp

    def rc_zhuanpanMsg(self, resid):
        x=Game.rpc_commonres_mgr.zhuanpanGetMsg(resid)
        resp = {
            "msg": x,
        }
        return 1, resp

    def rc_zhuanpanReward(self, resid, idx):


        res=Game.res_mgr.res_zhuanpanSystem.get(resid)
        if not res:
            return 0,errcode.EC_NORES

        if idx>=len(res.needs):
            return 0,errcode.EC_NORES

        

        x=self.player.zhuanpan.score.get(resid,0)
        if x<res.needs[idx]:
            return 0,errcode.EC_NOT_ENOUGH

        reward={}
        reward[res.rewardNeeds[idx][0]]=res.rewardNeeds[idx][1]

        cn=self.player.zhuanpan.rewardid.get(resid,[])
        if idx in cn:
            return 0,errcode.EC_ALREADY_REWARD
            
        
        cn.append(idx)
        if len(cn)==len(res.needs):
            cn=[]
            x-=res.needs[len(res.needs)-1]
            if x<0:
                x=0

        
        self.player.zhuanpan.rewardid[resid]=cn
        self.player.zhuanpan.score[resid]=x

        self.player.zhuanpan.markDirty()


        respBag = self.player.bag.add(reward, constant.ITEM_ADD_ZHUANPAN_REWARD, wLog=True, mail=True)

        # 打包返回信息
        dUpdate = self.player.packRespBag(respBag)

        dUpdate["zhuanpan"] = self.player.zhuanpan.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp