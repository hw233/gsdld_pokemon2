#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import random
import copy
from game.define import errcode, constant
from game import Game
from game.common import utility

class VipMixin(object):
    if 0:
        from game.core import player as player_md
        player = player_md.Player()



    def rc_vipDayReward(self, lv):
        """vip每日奖励"""
        vipLv = self.player.vip.GetVipLv()
        vipRes = Game.res_mgr.res_vip.get(lv, None)
        if not vipRes:
            return 0, errcode.EC_NORES
        if vipLv < lv:
            return 0, errcode.EC_VIP_REWARD_ALREADY
        getList = self.player.vip.GetVIPDayRewardList()
        if lv in getList:
            return 0, errcode.EC_VIP_REWARD_NOTABLE

        reward = copy.deepcopy(vipRes.dayReward)
        
        resAct = Game.res_mgr.res_activity.get(constant.ACTIVITY_VIPDAYREWARD)
        serverInfo = self.player.base.GetServerInfo()
        if resAct.isOpen(serverInfo):
            for k,v in reward.items():
                reward[k]=reward[k]*2


        respBag = self.player.bag.add(reward, constant.ITEM_ADD_VIP_DAY_REWARD, wLog=True)

        getList.append(lv)
        self.player.vip.SetVIPDayRewardList(getList)

        dUpdate = self.player.packRespBag(respBag)
        dUpdate["vipInfo"] = self.player.vip.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp


    def rc_vipReward(self, lv):
        res = Game.res_mgr.res_vip.get(lv)
        if not res:
            return 0, errcode.EC_NORES

        retval = self.player.vip.vipReward(lv)
        if retval == 1:
            return 0, errcode.EC_VIP_REWARD_ALREADY
        elif retval == 2:
            return 0, errcode.EC_VIP_REWARD_NOTABLE

        respBag = self.player.bag.costItem(res.cost, constant.ITEM_COST_VIP_REWARD, wLog=True)
        if not respBag.get("rs", 0):
            return 0, errcode.EC_COST_ERR

        respBag1 = self.player.bag.add(res.reward, constant.ITEM_ADD_VIP_REWARD, wLog=True)
        respBag = self.player.mergeRespBag(respBag, respBag1)

        self.player.vip.setVipReward(lv)

        dUpdate = self.player.packRespBag(respBag)
        dUpdate["vipInfo"] = self.player.vip.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp

    def rc_vipMonthReward(self):
        res = Game.res_mgr.res_common.get("monthCardDailyReward")
        if not res:
            return 0, errcode.EC_NORES

        retval = self.player.vip.vipRewardMonth()
        if not retval:
            return 0, errcode.EC_VIP_REWARD_NOTABLE_MONTH

        respBag = self.player.bag.add(res.arrayint2, constant.ITEM_ADD_VIP_REWARD_MONTH, wLog=True)

        dUpdate = self.player.packRespBag(respBag)
        dUpdate["vipInfo"] = self.player.vip.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp

    def rc_vipWeekReward(self):
        res = Game.res_mgr.res_common.get("weekCardDailyReward")
        if not res:
            return 0, errcode.EC_NORES

        retval = self.player.vip.vipRewardWeek()
        if not retval:
            return 0, errcode.EC_VIP_REWARD_NOTABLE_WEEK

        respBag = self.player.bag.add(res.arrayint2, constant.ITEM_ADD_VIP_REWARD_WEEK, wLog=True)

        dUpdate = self.player.packRespBag(respBag)
        dUpdate["vipInfo"] = self.player.vip.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp



    def rc_schdGift(self):

        res = Game.res_mgr.res_schd.get(self.player.charge.schdCharge+1)
        if not res:
            return 0, errcode.EC_NORES

        if self.player.charge.schdChargeRMB<res.rmb:
            return 0,errcode.EC_VIP_REWARD_NOTABLE

        self.player.charge.schdChargeReward()

        respBag = self.player.bag.add(res.reward, constant.ITEM_ADD_SCHD, wLog=True)

        dUpdate = self.player.packRespBag(respBag)
        dUpdate["chargeInfo"] = self.player.charge.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp


    def rc_dbscGift(self,id):

        res = Game.res_mgr.res_charge.get(id)
        if not res:
            return 0, errcode.EC_NORES

        if id not in self.player.charge.dbscid:
            return 0,errcode.EC_DBSC_REWARD_NOTABLE

        if id in self.player.charge.dbscreward:
            return 0,errcode.EC_DBSC_REWARD_ALREADY

        Game.glog.log2File("rc_dbscGift", "%s %s" % (self.player.id, id))

        self.player.charge.dbscReward(id)

        reward = copy.deepcopy(res.dbscReward)
        resAct = Game.res_mgr.res_activity.get(constant.ACTIVITY_CHARGE_TLREWAD)
        if resAct:
            serverInfo = self.player.base.GetServerInfo()
            if resAct.isOpen(serverInfo):
                if id not in self.player.charge.ChargeIDs:
                    self.player.charge.ChargeIDs.append(id)
                    for k, v in res.tlreward.items():
                        reward[k]=reward.get(k,0)+v

        respBag = self.player.bag.add(reward, constant.ITEM_ADD_DBSC, wLog=True)

        dUpdate = self.player.packRespBag(respBag)
        dUpdate["chargeInfo"] = self.player.charge.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        Game.glog.log2File("rc_dbscGift", "%s|%s" % (self.player.id, resp))
        return 1, resp

    def rc_vipBattleJump(self):
        battleJumpNum = self.player.vip.getBattleJumpNum()
        if battleJumpNum == -1:
            return 1, {}
        elif battleJumpNum == 0:
            #扣道具
            costRes = Game.res_mgr.res_common.get("battleJumpCost")
            if not costRes:
                return 0, errcode.EC_NORES
            respBag = self.player.bag.costItem(costRes.arrayint2, constant.ITEM_COST_BATTLE_JUMP, wLog=True)
            if not respBag.get("rs", 0):
                return 0, errcode.EC_BATTLE_JUMP_NOT_ENOUGH

            dUpdate = self.player.packRespBag(respBag)
            dUpdate["vipInfo"] = self.player.vip.to_init_data()
            resp = {
                "allUpdate": dUpdate,
            }
            return 1, resp
        else:
            #扣次数
            battleJumpNum -= 1
            self.player.vip.setBattleJumpNum(battleJumpNum)

            dUpdate = {}
            dUpdate["vipInfo"] = self.player.vip.to_init_data()
            resp = {
                "allUpdate": dUpdate,
            }
            return 1, resp

    def rc_vipZhiZunReward(self):
        res = Game.res_mgr.res_common.get("zhizunCardDailyReward")
        if not res:
            return 0, errcode.EC_NORES
        if not self.player.vip.zhizunCardFlag:
            return 0, errcode.EC_ZHIZUN_CARD_NO_HAVE

        isGet = self.player.vip.GetTodayZhiZunRewardFlag()
        if isGet:
            return 0, errcode.EC_ZHIZUN_CARD_DAYREWARD_HAS_GET

        respBag = self.player.bag.add(res.arrayint2, constant.ITEM_ADD_VIP_REWARD_ZHIZUN, wLog=True)

        self.player.vip.SetTodayZhiZunRewardFlag(1)

        dUpdate = self.player.packRespBag(respBag)
        dUpdate["vipInfo"] = self.player.vip.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp












