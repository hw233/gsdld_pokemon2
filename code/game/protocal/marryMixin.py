#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import random
import copy
from game.define import errcode, constant
from game import Game
from game.common import utility
import time

class MarryMixin(object):
    if 0:
        from game.core import player as player_md
        player = player_md.Player()

    # 检查对方可否结婚(marryCheck)
    #     请求
    #     对方pid(targetPid, int)
    #
    #     返回
    def rc_marryCheck(self, targetPid):
        if not Game.rpc_player_mgr.is_online(targetPid):
            return 0, errcode.EC_MARRY_NOT_ONLINE

        from game.mgr.player import get_rpc_player
        targetPlayer = get_rpc_player(targetPid, offline=False)
        if not targetPlayer:
            return 0, errcode.EC_NOFOUND

        if self.player.marry.getMarryStatus() or targetPlayer.getMarryStatus():
            return 0, errcode.EC_MARRY_ALREAY_MARRY

        if self.player.marry.isMarriedToday() or targetPlayer.isMarriedToday():
            return 0, errcode.EC_MARRY_ALEARY_TODAY

        return 1, {}

    # 求婚(marrySomeone)
    # 	请求
    # 		对方pid(targetPid, int)
    # 		身份类型(kind, int)
    #       结婚类型id(marryId, int)
    # 	返回
    def rc_marrySomeone(self, targetPid, kind, marryId):
        marryRes = Game.res_mgr.res_marry.get(marryId, None)
        if not marryRes:
            return 0, errcode.EC_NORES

        if not Game.rpc_player_mgr.is_online(targetPid):
            return 0, errcode.EC_MARRY_NOT_ONLINE

        from game.mgr.player import get_rpc_player
        targetPlayer = get_rpc_player(targetPid, offline=False)
        if not targetPlayer:
            return 0, errcode.EC_NOFOUND

        if self.player.marry.getMarryStatus() or targetPlayer.getMarryStatus():
            return 0, errcode.EC_MARRY_ALREAY_MARRY

        if self.player.marry.isMarriedToday() or targetPlayer.isMarriedToday():
            return 0, errcode.EC_MARRY_ALEARY_TODAY

        canCost = self.player.bag.canCostItem(marryRes.cost)
        if not canCost.get("rs", 0):
            return 0, errcode.EC_MARRY_NOT_ENOUGH

        pushData = {
            "targetName": self.player.name,
            "targetPid": self.player.id,
            "marryId": marryId,
            "kind": kind,
        }

        targetPlayer.marryPush(pushData)

        return 1, None

    # 求婚回应(marryAnswer)
    # 	请求
    # 		选择(option, int)
    # 			1 答应 2拒绝
    # 		你的身份(kind, int)
    # 			1 夫君 2 妻子
    #       对方pid(targetPid, int)
    #       结婚类型(marryId, int)
    # 	返回
    def rc_marryAnswer(self, option, kind, targetPid, marryId):
        from game.mgr.player import get_rpc_player
        targetPlayer = get_rpc_player(targetPid, offline=False)
        if not targetPlayer:
            return 0, errcode.EC_NOFOUND

        if option == 2:
            pushData = {
                "result": 3,
                "targetPid": self.player.id,
            }
            targetPlayer.marryResultPush(pushData)
            return 1, {}

        marryRes = Game.res_mgr.res_marry.get(marryId, None)
        if not marryRes:
            return 0, errcode.EC_NORES

        if self.player.getMarryStatus() or targetPlayer.getMarryStatus():
            return 0, errcode.EC_MARRY_ALREAY_MARRY

        respBag = targetPlayer.costItem(marryRes.cost, constant.ITEM_COST_MARRY, wLog=True)
        if not respBag.get("rs", 0):
            return 0, errcode.EC_COST_ERR

        myPid = self.player.id
        myName = self.player.name
        targetName = targetPlayer.getName()

        successPushData = {
            "husbandName": targetName,
            "husbandPid": targetPid,
            "wifeName": myName,
            "wifePid": myPid,
        }

        targetKind = 1
        if kind == 1:
            targetKind = 2
            successPushData = {
                "husbandName": myName,
                "husbandPid": myPid,
                "wifeName": targetName,
                "wifePid": targetPid,
            }

        self.player.marrySomeone(targetPid, targetName, kind, marryId)
        targetPlayer.marrySomeone(myPid, myName, targetKind, marryId)

        Game.rpc_player_mgr.broadcast("marrySuccessPush", successPushData, [myPid, targetPid])

        return 1, None

    # 赠送结婚礼金(presentMarryGfit)
    # 	请求
    # 		礼金类型(giftId, int)
    #       丈夫pid(husbandPid, int)
    #       妻子pid(wifePid, int)
    # 	返回
    # 		主动推送刷新(allUpdate,json)
    # 			游戏模型-货币
    # 			游戏模型-角色背包
    def rc_presentMarryGfit(self, giftId, husbandPid, wifePid):
        giftRes = Game.res_mgr.res_marryGift.get(giftId, None)
        giftMailRes1 = Game.res_mgr.res_mail.get(constant.MAIL_ID_MARRY_GIFT, None)
        giftMailRes2 = Game.res_mgr.res_mail.get(constant.MAIL_ID_MARRY_RETGIFT, None)

        if not giftRes or not giftMailRes1 or not giftMailRes2:
            return 0, errcode.EC_NORES

        respBag = self.player.bag.costItem(giftRes.cost, constant.ITEM_COST_MARRY_GIFT, wLog=True)
        if not respBag.get("rs", 0):
            return 0, errcode.EC_COST_ERR

        content = giftMailRes1.content % self.player.name
        Game.rpc_mail_mgr.sendPersonMail(self.player.id, giftMailRes2.title, giftMailRes2.content, giftRes.reward)
        Game.rpc_mail_mgr.sendPersonMail(husbandPid, giftMailRes1.title, content, giftRes.reward)
        Game.rpc_mail_mgr.sendPersonMail(wifePid, giftMailRes1.title, content, giftRes.reward)

        dUpdate = self.player.packRespBag(respBag)
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp

    # 离婚(divorce)
    # 	请求
    # 	返回
    def rc_divorce(self):
        if not self.player.getMarryStatus():
            return 0, errcode.EC_MARRY_NOT_MARRY

        spousePid = self.player.marry.getSpousePid()
        from game.mgr.player import get_rpc_player
        spousePlayer = get_rpc_player(spousePid, offline=True)
        if not spousePlayer:
            return 0, errcode.EC_NOFOUND

        self.player.marry.divorce()
        myMailRes = Game.res_mgr.res_mail.get(constant.MAIL_ID_DIVORCE, None)
        if myMailRes:
            Game.rpc_mail_mgr.sendPersonMail(spousePid, myMailRes.title, myMailRes.content, {})

        spousePlayer.divorce()

        return 1, None


    # 亲密度时间到了需要刷新一下
    def rc_MarryRefresh(self):

        # self.player.marry.checkEn()
        dUpdate = {}
        dUpdate["marryInfo"] = self.player.marry.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp

    # 已读亲密度真爱
    def rc_MarryTureLoveRead(self):
        self.player.marry.TrueLoveRead()

        return 1, {}


    # 已读亲密度真爱
    def rc_MarryMsgRead(self):
        self.player.marry.MsgRead()

        return 1, {}

    # 赠送亲密度
    def rc_MarryPowerBuy(self,id,num,bynum,costtype,costnum):

        res = Game.res_mgr.res_marryPower.get(id, None)

        if not res:
            return 0, errcode.EC_NORES

        if not self.player.marry.spousePid:
            return 0, errcode.EC_MARRY_NOT_MARRY



        self.player.marry.checkEn()

        en=0
        for x in self.player.marry.powerEn:
            if x["id"]==id:
                en=x["en"]
                break

        if res.enlimit and not en:
            return 0, errcode.EC_MARRY_NOT_EN

         
        useids=self.player.marry.getMarryUseIDs()
        usenum=useids.count(id)

        if res.uselimit and usenum>=res.uselimit:
            return 0, errcode.EC_MARRY_NOT_TODAY_LIMIT


        cost=copy.deepcopy(res.cost)

        for k,v in cost.items():
            cost[k]=cost[k]*(num-bynum)
            
        if costtype and costnum:
            cost[costtype]=cost.get(costtype,0)+costnum

        delkey=[]
        for k,v in cost.items():
            if not v:
                delkey.append(k)
        for k in delkey:
            del cost[k]

        # print("!!!!!!!",cost)

        respBag = self.player.bag.costItem(cost, constant.ITEM_COST_MARRY_POWER, wLog=True)
        if not respBag.get("rs", 0):
            return 0, errcode.EC_NOT_ENOUGH

        self.player.marry.addPower(id,res.add*num,res.uselimit,res.enlimit,num)

        from game.mgr.player import get_rpc_player
        targetPlayer = get_rpc_player(self.player.marry.spousePid, offline=False)
        if targetPlayer:
            targetPlayer.marryPowerPush(id,res.add*num,num,self.player.id,self.player.name)


        dUpdate = self.player.packRespBag(respBag)
        dUpdate["marryInfo"] = self.player.marry.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp


    # 亲密度等级领奖
    def rc_MarryLvReward(self,id):

        res = Game.res_mgr.res_marryLv.get(id, None)
        if not res:
            return 0, errcode.EC_NORES

        if id in self.player.marry.powerLvReward:
            return 0, errcode.EC_NORES

        if self.player.marry.power<res.power:
            return 0, errcode.EC_NORES

        respBag = self.player.bag.add(res.reward, constant.ITEM_ADD_MARRY_POWER, wLog=True)

        self.player.marry.powerLvReward.append(id)
        self.player.marry.markDirty()

        # 打包返回信息
        dUpdate = self.player.packRespBag(respBag)
        dUpdate["marryInfo"] = self.player.marry.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp



