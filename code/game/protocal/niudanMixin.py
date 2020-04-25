#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import random
import time

from game.define import errcode, constant, msg_define
from game import Game
from game.common import utility

from corelib import log, spawn

class NiudanMixin(object):
    if 0:
        from game.core import player as player_md
        player = player_md.Player()



    def rc_niudanRoll(self,resid,ten,useFree=False):
        print("===rc_niudanRoll===",resid,ten,useFree)
        res=Game.res_mgr.res_niudanSystem.get(resid)
        if not res:
            print("111111111111111",resid)
            return 0,errcode.EC_NORES

        resxx=getattr(Game.res_mgr,"res_niudan"+res.mod)
        if not resxx:
            print("111111111111111",res.mod)
            return 0,errcode.EC_NORES


        serverInfo = self.player.base.GetServerInfo()

        #普通池
        resAct1=Game.res_mgr.res_activity.get(res.ptActID)
        if not resAct1:
            print("3333333333333",res.ptActID)
            return 0,errcode.EC_NORES
        if not resAct1.isOpen(serverInfo):
            return 0,errcode.EC_NOT_OPEN
        funcID1=resAct1.getCycleFuncID(serverInfo)
        if not funcID1:
            return 0,errcode.EC_NOT_OPEN

        #精英池
        resAct2=Game.res_mgr.res_activity.get(res.jyActID)
        if not resAct2:
            print("4444444444444",res.jyActID)
            return 0,errcode.EC_NORES
        if not resAct2.isOpen(serverInfo):
            return 0,errcode.EC_NOT_OPEN
        funcID2=resAct2.getCycleFuncID(serverInfo)
        if not funcID2:
            return 0,errcode.EC_NOT_OPEN

        #系统活动
        resActX=Game.res_mgr.res_activity.get(res.sysActID)
        if not resActX.isOpen(serverInfo):
            return 0,errcode.EC_NOT_OPEN
        funcIDX=resActX.getCycleFuncID(serverInfo)
        if not funcIDX:
            return 0,errcode.EC_NOT_OPEN

        modres={}


        #系统活动res
        modres=resxx.get(funcIDX)
        if not modres:
            print("55555555555",funcIDX)
            return 0,errcode.EC_NORES

        
        
        times=1
        cost={}
        reward={}
        rn={}
        onenum=0
        if ten:       
            if not res.costTen or  not res.Ten:
                print("666666666666")
                return 0,errcode.EC_NORES
            
            times=res.Ten
            cost=res.costTen
        else:
            cost=res.cost
            times=1

            rn=self.player.niudan.getRollOneNum()
            onenum=rn.get(resid,0)           


            if useFree:
                if onenum<res.costFree:
                    cost={}
                else:
                    return 0,errcode.EC_FREE_EXHAUSTED


        
        rxAll=self.player.niudan.getRollNum()
        rxAllNum=rxAll.get(resid,0)

        for k,v in res.reward.items():
            reward[k]=v*times

        modactnum=self.player.niudan.getCycleBaodi(res.sysActID)
        modactreward=self.player.niudan.getCycleReward(res.sysActID)


        

        for timesn in range(times):
            
            pool=[]

            # if ten and not timesn and res.abpool:
            #     for v in Game.res_mgr.res_niudanPool.values():
            #         if not v.scope[1]:
            #             v.scope[1]=constant.MAX_SAFE_INTEGER
                    
            #         if v.cycleFuncID==funcID and v.scope[0]<=rxAllNum<=v.scope[1]:
            #             value = (v.rewardten, v.WeightTen)
            #             pool.append(value)
            # else:
            for v in Game.res_mgr.res_niudanPool.values():
                if not v.scope[1]:
                    v.scope[1]=constant.MAX_SAFE_INTEGER
                
                if (v.cycleFuncID==funcID1 or v.cycleFuncID==funcID2) and v.scope[0]<=rxAllNum<=v.scope[1]:
                    value = (v.reward, v.Weight)
                    pool.append(value)

            randomReward = utility.Choice(pool)
            print("===============",randomReward)

            modactnum+=1
            modactreward+=1
            if modres.baodiNum:
                if modactnum>=modres.baodiNum[res.modidx]:
                    modactnum=0
                    randomReward={}
                    randomReward[modres.reward[res.modidx][0]]=modres.reward[res.modidx][1]
                    print("==!!!!!=====",randomReward)

            for k,v in randomReward.items():
                reward[k]=reward.get(k,0)+v

            rxAllNum+=1


        rxAll[resid]=rxAllNum
        

        respBag1 = self.player.bag.costItem(cost, constant.ITEM_COST_NIUDAN_ROLL, wLog=True)
        if not respBag1.get("rs", 0):
            if ten:       
                if res.costTenRep:
                    respBag1 = self.player.bag.costItem(res.costTenRep, constant.ITEM_COST_NIUDAN_ROLL, wLog=True)
                    if not respBag1.get("rs", 0):
                        return 0, errcode.EC_COST_ERR
                else:
                    return 0, errcode.EC_COST_ERR

            else:
                if res.costRep:
                    respBag1 = self.player.bag.costItem(res.costRep, constant.ITEM_COST_NIUDAN_ROLL, wLog=True)
                    if not respBag1.get("rs", 0):
                        return 0, errcode.EC_COST_ERR
                else:
                    return 0, errcode.EC_COST_ERR

        respBag = self.player.bag.add(reward, constant.ITEM_ADD_NIUDAN_ROLL, wLog=True, mail=True)

        respBag = self.player.mergeRespBag(respBag, respBag1)

        print("===rc_niudanRoll===reward=",reward)

        if not ten:
            onenum+=1
            for xresid in res.RollOneResID:
                rn[xresid]=onenum
            self.player.niudan.setRollOneNum(rn)


        self.player.niudan.setRollNum(rxAll)

        self.player.niudan.setCycleBaodi(modactnum,res.sysActID)
        self.player.niudan.setCycleReward(modactreward,res.sysActID)


        # 打包返回信息
        dUpdate = self.player.packRespBag(respBag)

        dUpdate["niudan"] = self.player.niudan.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp

    def rc_niudanXianshiReward(self,idx):
        

        
        totAct=constant.ACTIVITY_XIANSHINIUDAN
        serverInfo = self.player.base.GetServerInfo()
        
        resActX=Game.res_mgr.res_activity.get(totAct)
        if not resActX.isOpen(serverInfo):
            return 0,errcode.EC_NOT_OPEN
        funcIDX=resActX.getCycleFuncID(serverInfo)
        if not funcIDX:
            return 0,errcode.EC_NOT_OPEN

        modres=Game.res_mgr.res_niudanXianshi.get(funcIDX)
        if not modres:
            return 0,errcode.EC_NORES

        if not modres.needs:
            return 0,errcode.EC_NOT_OPEN

        if len(modres.needs)<idx+1:
            return 0,errcode.EC_NORES
        

        x=self.player.niudan.getCycleReward(totAct)
        print("=====",x,modres.needs,idx)
        if x<modres.needs[idx]:
            return 0,errcode.EC_NOT_ENOUGH

        reward={}
        reward[modres.rewardNeeds[idx][0]]=modres.rewardNeeds[idx][1]


        cn=self.player.niudan.getCycleNeeds(totAct)
        if idx in cn:
            return 0,errcode.EC_ALREADY_REWARD
            
        
        cn.append(idx)
        if len(cn)==len(modres.needs):
            cn=[]
            x-=modres.needs[len(modres.needs)-1]
            if x<0:
                x=0
        self.player.niudan.setCycleNeeds(cn,totAct)
        self.player.niudan.setCycleReward(x,totAct)

        respBag = self.player.bag.add(reward, constant.ITEM_ADD_NIUDAN_XIANSHI_REWARD, wLog=True, mail=True)

        # 打包返回信息
        dUpdate = self.player.packRespBag(respBag)

        dUpdate["niudan"] = self.player.niudan.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp