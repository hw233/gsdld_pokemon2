#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import random

from game.define import errcode, constant, msg_define
from game import Game

from corelib import log
from game.fight import createFight

class DaoGuanMixin(object):
    if 0:
        from game.core import player as player_md
        player = player_md.Player()

    # 挑战道馆(daoguanChallenge)
    # 请求
    #     道馆id(daoguanId, int)
    #     副本id(fbId, int)
    # 返回
    #     主动推送刷新(allUpdate, json)
    #         游戏模型 - 道馆
    #         游戏模型 - 货币
    #         游戏模型 - 角色背包
    #         游戏模型 - 角色属性
    #         游戏模型 - 角色基础 - 战力
    #     战报(fightLog, json)
    def rc_daoguanChallenge(self, daoguanId, fbId):
        daoguanRes = Game.res_mgr.res_pavilion.get(daoguanId)
        if not daoguanRes:
            return 0, errcode.EC_NORES
        if fbId not in daoguanRes.challengeList:
            return 0, errcode.EC_DAOGUAN_FIGHT_ID_ERROR
        barrRes = Game.res_mgr.res_barrier.get(fbId)
        if not barrRes:
            return 0, errcode.EC_NORES
        if self.player.daoguan.area != daoguanRes.area:
            return 0, errcode.EC_DAOGUAN_FIGHT_AREA_ERROR
        daoguanObj = self.player.daoguan.getPavilion(daoguanId)
        if not daoguanObj:
            return 0, errcode.EC_DAOGUAN_NOT_FIND
        if not daoguanObj.hasAllTaskFinish():
            return 0, errcode.EC_DAOGUAN_FIGHT_LIMIT
        if daoguanObj.firstFinish:
            return 0, errcode.EC_DAOGUAN_HAS_FIRST_FINISH
        if self.player.daoguan.getHaveChallengeNum() <= 0:
            return 0, errcode.EC_DAOGUAN_FIGHT_NUM_LIMIT
        if fbId in daoguanObj.finishChallengeList:
            return 0, errcode.EC_DAOGUAN_BARR_HAS_FINISH
        rewardRes = Game.res_mgr.res_reward.get(barrRes.rewardId)

        firstRewardRes = Game.res_mgr.res_reward.get(daoguanRes.firstRewardId)
        if not firstRewardRes:
            return 0, errcode.EC_NORES

        # fightobj = Game.fight_mgr.createFight(constant.FIGHT_TYPE_114)
        # rs = fightobj.init_by_barrId(self.player, barrRes.id)
        # if not rs:
        #     return 0, errcode.EC_INIT_BARR_FAIL
        # fightobj.fixEleValue(daoguanRes.increase, daoguanRes.decrease)
        # fightLog = fightobj.doFight()
        # fightResult = fightLog["result"].get("win", 0)

        fightobj = createFight(constant.FIGHT_TYPE_100)
        rs = fightobj.init_data(self.player.GetFightData(constant.BATTLE_ARRAY_TYPE_NORMAL), 100000)
        if not rs:
            return 0, errcode.EC_INIT_BARR_FAIL
        fightLog = fightobj.doFight()
        log_end = fightLog.get("end", {})
        winerList = log_end.get("winerList", [])
        fightResult = 1 if self.player.id in winerList else 0

        respBag = {}
        resp_attr = []
        if fightResult:
            dReward = {}
            if rewardRes:
                dReward = rewardRes.doReward()
            if dReward:
                respBag = self.player.bag.add(dReward, constant.ITEM_ADD_DAOGUAN, wLog=True)

            #已挑战副本
            ls = daoguanObj.getFinishChallengeList()
            ls.append(fbId)
            daoguanObj.setFinishChallengeList(ls)
            #加入已扫荡列表
            ls = self.player.daoguan.GetDaoGuanDaySweepList()
            if daoguanId not in ls:
                ls.append(daoguanId)
                self.player.daoguan.SetDaoGuanDaySweepList(ls)

            if daoguanObj.hasAllFinish():
                #首通道馆 属性 和 奖励
                respBag1 = self.player.bag.add(firstRewardRes.doReward(), constant.ITEM_ADD_DAOGUAN_FIRST, wLog=True)
                respBag = self.player.mergeRespBag(respBag, respBag1)

                # 附加过关属性
                self.player.attr.addAttr(daoguanRes.attr, constant.FIGHTABILITY_TYPE_36)
                resp_attr.extend(list(daoguanRes.attr.keys()))

                daoguanObj.doFirstFinish()
                self.player.safe_pub(msg_define.MSG_PASS_DAO_GUAN)

                #当前地区全部通关，去往下一个地区的道馆
                if self.player.daoguan.hasAllFinish():
                    self.player.daoguan.enterNextArea()
        else:
            #失败扣除次数
            #今日挑战次数
            iNum = self.player.daoguan.GetDaoGuanDayChallengeNum()
            iNum += 1
            self.player.daoguan.SetDaoGuanDayChallengeNum(iNum)

            if daoguanRes.eleType==1:
                self.player.safe_pub(msg_define.MSG_XIANSHITUISONGLIBAO_DAOGUAN_1_F)
            elif daoguanRes.eleType==2:
                self.player.safe_pub(msg_define.MSG_XIANSHITUISONGLIBAO_DAOGUAN_2_F)
            elif daoguanRes.eleType==3:
                self.player.safe_pub(msg_define.MSG_XIANSHITUISONGLIBAO_DAOGUAN_3_F)
            elif daoguanRes.eleType==4:
                self.player.safe_pub(msg_define.MSG_XIANSHITUISONGLIBAO_DAOGUAN_4_F)
            elif daoguanRes.eleType==5:
                self.player.safe_pub(msg_define.MSG_XIANSHITUISONGLIBAO_DAOGUAN_5_F)

        # 重算战力
        self.player.attr.RecalFightAbility()
        # 打包返回信息
        dUpdate = self.player.packRespBag(respBag, fa=self.player.base.fa, roleAttr=resp_attr)
        dUpdate["daoguan"] = self.player.daoguan.to_init_data()
        resp = {
            "fightLog": fightLog,
            "allUpdate": dUpdate,
        }
        return 1, resp

    # 扫荡道馆(daoguanSweep)
    # 请求
    #     道馆id(daoguanId, int)
    # 返回
    #     主动推送刷新(allUpdate,json)
    #         游戏模型-道馆
    #         游戏模型-货币
    #         游戏模型-角色背包
    def rc_daoguanSweep(self, daoguanId):
        daoguanRes = Game.res_mgr.res_pavilion.get(daoguanId)
        if not daoguanRes:
            return 0, errcode.EC_NORES
        rewardRes = Game.res_mgr.res_reward.get(daoguanRes.rewardId)
        if not rewardRes:
            return 0, errcode.EC_NORES
        ls = self.player.daoguan.GetDaoGuanDaySweepList()
        if daoguanId in ls:
            return 0, errcode.EC_DAOGUAN_HAS_SWEEP
        iPass = 0
        if self.player.daoguan.getArea() > daoguanRes.area:
            iPass = 1
        elif self.player.daoguan.getArea() == daoguanRes.area:
            daoguanObj = self.player.daoguan.getPavilion(daoguanId)
            if not daoguanObj:
                return 0, errcode.EC_DAOGUAN_NOT_FIND
            if daoguanObj.firstFinish:
                iPass = 1

        if not iPass:
            return 0, errcode.EC_DAOGUAN_SWEEP_LIMIT

        dReward = rewardRes.doReward()
        respBag = self.player.bag.add(dReward, constant.ITEM_ADD_DAOGUAN, wLog=True)

        ls.append(daoguanId)
        self.player.daoguan.SetDaoGuanDaySweepList(ls)
        # 打包返回信息
        dUpdate = self.player.packRespBag(respBag, fa=self.player.base.GetFightAbility())
        dUpdate["daoguan"] = self.player.daoguan.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp

    # 一键扫荡道馆(daoguanOneKeySweep)
    # 请求
    # 返回
    #     主动推送刷新(allUpdate,json)
    #         游戏模型-道馆
    #         游戏模型-货币
    #         游戏模型-角色背包
    def rc_daoguanOneKeySweep(self):
        #vip X 才开启一键扫荡
        iVipLv = self.player.vip.GetVipLv()
        vipRes = Game.res_mgr.res_vip.get(iVipLv)
        if not vipRes:
            return 0, errcode.EC_NORES
        if not vipRes.daoguanSweep:
            return 0, errcode.EC_DAOGUAN_SWEEP_LIMIT
        dReward = {}
        for daoguanId, daoguanRes in Game.res_mgr.res_pavilion.items():
            rewardRes = Game.res_mgr.res_reward.get(daoguanRes.rewardId)
            if not rewardRes:
                continue
            ls = self.player.daoguan.GetDaoGuanDaySweepList()
            if daoguanId in ls:
                continue
            iPass = 0
            if self.player.daoguan.getArea() > daoguanRes.area:
                iPass = 1
            elif self.player.daoguan.getArea() == daoguanRes.area:
                daoguanObj = self.player.daoguan.getPavilion(daoguanId)
                if not daoguanObj:
                    continue
                if daoguanObj.firstFinish:
                    iPass = 1
            if not iPass:
                continue
            _dReward = rewardRes.doReward()
            ls.append(daoguanId)
            self.player.daoguan.SetDaoGuanDaySweepList(ls)

            for itemId, num in _dReward.items():
                if itemId in dReward:
                    dReward[itemId] += num
                else:
                    dReward[itemId] = num

        respBag = self.player.bag.add(dReward, constant.ITEM_ADD_DAOGUAN, wLog=True)

        # 打包返回信息
        dUpdate = self.player.packRespBag(respBag, fa=self.player.base.GetFightAbility())
        dUpdate["daoguan"] = self.player.daoguan.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp


    # 道馆挑战次数购买(daoguanChallengeBuy)
    # 请求
    # 返回
    #     主动推送刷新(allUpdate,json)
    #         游戏模型-道馆
    #         游戏模型-货币
    #         游戏模型-角色背包
    def rc_daoguanChallengeBuy(self):
        iTodayBuy = self.player.daoguan.GetDaoGuanDayBuyChallengeNum()
        iVipLv = self.player.vip.GetVipLv()
        vipRes = Game.res_mgr.res_vip.get(iVipLv)
        if not vipRes:
            return 0, errcode.EC_NORES
        if iTodayBuy >= vipRes.daoguanBuyNum:
            return 0, errcode.EC_DAOGUAN_VIP_BUY_LIMIT
        costRes = Game.res_mgr.res_common.get("daoguanChallengeBuyCost")
        if not costRes:
            return 0, errcode.EC_NORES
        if len(costRes.arrayint1) <= iTodayBuy:
            return 0, errcode.EC_DAOGUAN_VIP_BUY_LIMIT
        iCost = costRes.arrayint1[iTodayBuy]
        dCost = {constant.CURRENCY_BINDGOLD: iCost}
        # 扣道具
        respBag = self.player.bag.costItem(dCost, constant.ITEM_COST_DAOGUAN_BUG_NUM, wLog=True)
        if not respBag.get("rs", 0):
            return 0, errcode.EC_DAOGUAN_VIP_BUY_NOT_ENOUGH

        self.player.daoguan.SetDaoGuanDayBuyChallengeNum(iTodayBuy+1)

        # 打包返回信息
        dUpdate = self.player.packRespBag(respBag)
        dUpdate["daoguan"] = self.player.daoguan.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp








