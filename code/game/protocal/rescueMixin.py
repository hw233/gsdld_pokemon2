#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import random
import time

from game.define import errcode, constant, msg_define
from game import Game
from game.common import utility

from corelib import log, spawn

class RescueMixin(object):
    if 0:
        from game.core import player as player_md
        player = player_md.Player()



    def rc_rescueSave(self,resid):
        res = Game.res_mgr.res_rescueSystem.get(resid)
        if not res:
            return 0, errcode.EC_NORES


        if self.player.rescue.keyinfo[resid]["ok"]:
            return 0, errcode.EC_ALREADY_REWARD


        ok=True
        if res.num1>self.player.rescue.keyinfo[resid]["num1"]:
            ok=False
        elif res.num2>self.player.rescue.keyinfo[resid]["num2"]:
            ok=False
        elif res.num3>self.player.rescue.keyinfo[resid]["num3"]:
            ok=False
        elif res.num4>self.player.rescue.keyinfo[resid]["num4"]:
            ok=False
        elif res.num5>self.player.rescue.keyinfo[resid]["num5"]:
            ok=False
        

        if not ok:
            return 0, errcode.EC_NO_FINISH


        # if ok and not self.keyinfo[k]["ok"]:
            # self.keyinfo[k]["ok"]=1
            # self.score+=1


        # if self.player.map.mapSubId<res.mapsubid:
        #     return 0, errcode.EC_NOT_ABLE
        

        self.player.rescue.keyinfo[resid]["ok"]=1
        self.player.rescue.score+=1
        self.player.rescue.markDirty()

        
        # 打包返回信息
        dUpdate = {}
        dUpdate["rescue"] = self.player.rescue.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp


    def rc_rescueDing(self,resid):
        res = Game.res_mgr.res_rescueSystem.get(resid)
        if not res:
            return 0, errcode.EC_NORES


        if self.player.map.mapSubId<res.mapsubid:
            return 0, errcode.EC_NOT_ABLE
        

        self.player.rescue.Ding=resid
        self.player.rescue.markDirty()

        
        # 打包返回信息
        dUpdate = {}
        dUpdate["rescue"] = self.player.rescue.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp

    def rc_rescueReward(self,resid):
        res = Game.res_mgr.res_rescueReward.get(resid)
        if not res:
            return 0, errcode.EC_NORES

        if resid in self.player.rescue.rewards:
            return 0, errcode.EC_ALREADY_REWARD

        if self.player.rescue.score<res.score:
            return 0, errcode.EC_NOT_ENOUGH


        self.player.rescue.rewards.append(resid)
        self.player.rescue.markDirty()
        respBag = self.player.bag.add(res.reward, constant.ITEM_ADD_RESCUE_REWARD, wLog=True)
        
        # 打包返回信息
        dUpdate = self.player.packRespBag(respBag)
        dUpdate["rescue"] = self.player.rescue.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp


    def rc_rescueRefresh(self):

        sentFree = Game.res_mgr.res_common.get("sentFree")
        sentCost1 = Game.res_mgr.res_common.get("sentCost1")
        sentCost2 = Game.res_mgr.res_common.get("sentCost2")

        n=self.player.rescue.getfreshNum()
        respBag={}
        isGold=False
        if n>=sentFree.i:
            respBag = self.player.bag.costItem(sentCost1.arrayint2, constant.ITEM_COST_SENT_REFRESH, wLog=True)
            if not respBag.get("rs", 0):
                isGold=True
                respBag = self.player.bag.costItem(sentCost2.arrayint2, constant.ITEM_COST_SENT_REFRESH, wLog=True)
                if not respBag.get("rs", 0):
                    return 0, errcode.EC_COST_ERR


        self.player.rescue.refreshTaskUser(isGold)

        
        # 打包返回信息
        dUpdate = self.player.packRespBag(respBag)
        dUpdate["rescue"] = self.player.rescue.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp

    def rc_rescueFastXhour(self,idx,x):
        if not self.player.rescue.taskData[idx]["et"]:
            return 0, errcode.EC_NO_START

        nt = time.time()
        if self.player.rescue.taskData[idx]["et"]<=nt:
            return 0, errcode.EC_ALREADY_FINISH

        res = Game.res_mgr.res_rescueTask.get(self.player.rescue.taskData[idx]["id"])
        if not res:
            return 0, errcode.EC_NORES

        cost={}
        
        for _ in range(x):
            for k,v  in res.cost.items():
                cost[k]=cost.get(k,0)+v

        respBag = self.player.bag.costItem(cost, constant.ITEM_COST_SENT_FAST, wLog=True)
        if not respBag.get("rs", 0):
            return 0, errcode.EC_COST_ERR

        self.player.rescue.taskData[idx]["et"]-=x*3600
        self.player.rescue.markDirty()
        
        # 打包返回信息
        dUpdate = self.player.packRespBag(respBag)
        dUpdate["rescue"] = self.player.rescue.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp


    def rc_rescueFinishAll(self):
        
        reward={}
        newtaskData=[]
        for idx in range(len(self.player.rescue.taskData)):

            if not self.player.rescue.taskData[idx]["et"]:
                newtaskData.append(self.player.rescue.taskData[idx])
                continue

            nt = time.time()
            if self.player.rescue.taskData[idx]["et"]>nt:
                newtaskData.append(self.player.rescue.taskData[idx])
                continue

            
            res = Game.res_mgr.res_rescueTask.get(self.player.rescue.taskData[idx]["id"])
            if not res:
                newtaskData.append(self.player.rescue.taskData[idx])
                continue



            if res.rescueSystemKey:
                self.player.rescue.rescueSystemKey(res.rescueSystemKey)
            if res.rescueAuto:
                for _ in range(res.rescueAuto):
                    self.player.rescue.rescueAuto()

            for k,v in res.reward.items():
                reward[k]=reward.get(k,0)+v


        respBag = self.player.bag.add(reward, constant.ITEM_ADD_RESCUE_SENT, wLog=True)

        self.player.rescue.taskData=newtaskData
        self.player.rescue.markDirty()
        
        # 打包返回信息
        dUpdate = self.player.packRespBag(respBag)
        dUpdate["rescue"] = self.player.rescue.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp

    def rc_rescueFinish(self,idx):
        

        if not self.player.rescue.taskData[idx]["et"]:
            return 0, errcode.EC_NO_START

        nt = time.time()
        if self.player.rescue.taskData[idx]["et"]>nt:
            return 0, errcode.EC_NO_FINISH

        
        res = Game.res_mgr.res_rescueTask.get(self.player.rescue.taskData[idx]["id"])
        if not res:
            return 0, errcode.EC_NORES

        if res.rescueSystemKey:
            self.player.rescue.rescueSystemKey(res.rescueSystemKey)
        if res.rescueAuto:
            for _ in range(res.rescueAuto):
                self.player.rescue.rescueAuto()

        respBag = self.player.bag.add(res.reward, constant.ITEM_ADD_RESCUE_SENT, wLog=True)

        self.player.rescue.taskData.pop(idx)
        self.player.rescue.markDirty()
        
        # 打包返回信息
        dUpdate = self.player.packRespBag(respBag)
        dUpdate["rescue"] = self.player.rescue.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp

    def rc_rescueSent(self,idx,uids):

        if self.player.rescue.taskData[idx]["et"]:
            return 0, errcode.EC_CODE_10003

        res = Game.res_mgr.res_rescueTask.get(self.player.rescue.taskData[idx]["id"])
        if not res:
            return 0, errcode.EC_NORES

        if len(res.petid)!=len(uids):
            return 0, errcode.EC_NOT_ENOUGH

        for uidsidx in range(len(uids)):
            
            uid=uids[uidsidx]

            pet = self.player.pet.getPet(uid)
            if not pet:
                return 0, errcode.EC_PET_NOT_ACT
            petres = Game.res_mgr.res_pet.get(pet.resID)
            if not petres:
                return 0, errcode.EC_NORES
            
            evolveRes = Game.res_mgr.res_idlv_petevolve.get((pet.resID, pet.evolveLv))
            if not evolveRes:
                return 0, errcode.EC_NORES

            for td in self.player.rescue.taskData:
                if uid in td["petuid"]:
                    return 0, errcode.EC_CODE_10004

            if res.petid[uidsidx]:
                if res.petid[uidsidx]!=pet.resID:
                    return 0, errcode.EC_CODE_10005

            
            if res.eleType[uidsidx]:
                if res.eleType[uidsidx]!=petres.eleType:
                    return 0, errcode.EC_CODE_10006

            
            if res.showStar[uidsidx]:
                if res.showStar[uidsidx]>evolveRes.showStar:
                    return 0, errcode.EC_CODE_10007



        respBag = self.player.bag.costItem(res.explore, constant.ITEM_COST_SENT_PET, wLog=True)
        if not respBag.get("rs", 0):
            return 0, errcode.EC_COST_ERR


        self.player.rescue.taskData[idx]["et"]=time.time()+res.hour*3600
        self.player.rescue.taskData[idx]["petuid"]=uids
        self.player.rescue.markDirty()
        
        # 打包返回信息
        dUpdate = self.player.packRespBag(respBag)
        dUpdate["rescue"] = self.player.rescue.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp

    def rc_rescueXXX(self):

        
        # 打包返回信息
        dUpdate = {}
        dUpdate["rescue"] = self.player.rescue.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp