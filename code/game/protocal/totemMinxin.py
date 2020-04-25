#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from game.define import errcode, constant
from game import Game
from game.common import utility

class TotemMixin(object):
    if 0:
        from game.core import player as player_md
        player = player_md.Player()

    #图腾激活(totemAct)
    #请求
    #    部位(pos, int)
    #
    #
    #返回
    #     主动推送刷新(allUpdate, json)
    #         游戏模型 - 图腾模块（只刷当前操作的）
    #         游戏模型 - 角色背包 - 道具列表
    #         游戏模型 - 货币
    def rc_totemAct(self, pos):
        res = Game.res_mgr.res_poslv_totem.get((pos, 0), None)
        if not res:
            return 0, errcode.EC_NORES

        nextRes = Game.res_mgr.res_poslv_totem.get((pos, 1), None)
        if not res:
            return 0, errcode.EC_NORES

        if pos in self.player.totem.actList:
            return 0, errcode.EC_TOTEM_HAS_ACT

        respBag = self.player.bag.costItem(res.tpCost, constant.ITEM_COST_TOTEM_ACT, wLog=True)
        if not respBag.get("rs", 0):
            return 0, errcode.EC_TOTEM_ACT_NOT_ENOUGH

        self.player.totem.actTotem(nextRes)

        # 战力重算
        self.player.attr.RecalFightAbility()

        dTotem = {}
        totem = self.player.totem.getTotem(pos)
        dTotem["actList"] = [totem.to_init_data()]

        dUpdate = self.player.packRespBag(respBag)
        dUpdate["attr"] = self.player.attr.to_update_data()
        dUpdate["totem"] = dTotem
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp


    # 图腾升级(totemUp)
    # 	请求
    # 		部位(pos, int)
    # 		次数(num, int)
    # 	返回
    # 		主动推送刷新(allUpdate, json)
    # 			游戏模型-图腾模块（只刷当前操作的）
    # 			游戏模型-角色背包-道具列表
    # 			游戏模型-货币
    def rc_totemUp(self, pos, num, auto):
        totem = self.player.totem.getTotem(pos)
        if not totem:
            return 0, errcode.EC_NOT_FIND_TOTEM

        oldlv = totem.getLv()
        res = Game.res_mgr.res_poslv_totem.get((pos, oldlv), None)
        if not res:
            return 0, errcode.EC_NORES

        leftExp = totem.getExp()
        if res.tpCost and leftExp >= res.exp:
            return 0, errcode.EC_TOTEM_NEED_TP

        totalAddExp = 0
        totalMulti = 0

        respBag = {}
        for i in range(num):
            oldlv = totem.getLv()

            res = Game.res_mgr.res_poslv_totem.get((pos, oldlv), None)

            respBag1 = self.player.bag.costItem(res.cost, constant.ITEM_COST_TOTEM_UPGRADE, wLog=True, auto=auto)
            if not respBag1.get("rs", 0):
                return 0, errcode.EC_TOTEM_UPGRADE_NOT_ENOUGH
            respBag = self.player.mergeRespBag(respBag, respBag1)

            oldExp = totem.getExp()
            oldBjId = totem.getBjResId()
            oldUpgradeTimes = totem.getUpgradeTimes()
            bjRes = Game.res_mgr.res_totemBj.get(oldBjId)
            multi = 1
            if oldUpgradeTimes+1 >= bjRes.num:
                multi = bjRes.multi
                nextBjId = oldBjId+1
                nextBjRes = Game.res_mgr.res_totemBj.get(nextBjId)
                if not nextBjRes:
                    nextBjId = oldBjId

                totem.setBjResId(nextBjId)
                totem.setUpgradeTimes(0)
            else:
                totem.setUpgradeTimes(oldUpgradeTimes+1)
                randomBj = utility.Choice(Game.res_mgr.res_random_totem)
                randomBjRes = Game.res_mgr.res_totemRan.get(randomBj, None)
                multi = randomBjRes.multi
    
            addRes = Game.res_mgr.res_common.get("totemsUpExp", None)
            addExp = addRes.i * multi
            newExp = oldExp + addExp

            if newExp > res.exp and not res.tpCost:
                newlv = oldlv + 1
                nextRes = Game.res_mgr.res_poslv_totem.get((pos, newlv), None)
                if nextRes:
                    leftExp = newExp - res.exp
                    totem.setLv(newlv, res, nextRes)
                    totem.setExp(leftExp)
                else:
                    totem.setExp(newExp)
            else:
                totem.setExp(newExp)

            if multi > 1:
                totalMulti += multi
            totalAddExp += addExp

        # 战力重算
        self.player.attr.RecalFightAbility()

        dTotem = {}
        dTotem["actList"] = [totem.to_init_data()]

        dUpdate = self.player.packRespBag(respBag)
        dUpdate["attr"] = self.player.attr.to_update_data()
        dUpdate["totem"] = dTotem
        resp = {
            "allUpdate": dUpdate,
            "multi": totalMulti,
            "addExp": totalAddExp,
        }
        return 1, resp

    # 图腾突破(totemTp)
    # 请求
    # 部位(pos, int)
    #
    #
    # 返回
    #     主动推送刷新(allUpdate, json)
    #     游戏模型 - 图腾模块（只刷当前操作的）
    #     图腾部位(pos, int)
    #     等级(lv, int)
    #     经验(exp, int)
    #     已升级次数(upNum, int)
    #     图腾暴击配置表id(bjId, int)
    #     游戏模型 - 角色背包 - 道具列表
    #     游戏模型 - 货币
    def rc_totemTp(self, pos):
        totem = self.player.totem.getTotem(pos)
        if not totem:
            return 0, errcode.EC_NOT_FIND_TOTEM

        res = Game.res_mgr.res_poslv_totem.get((pos, totem.getLv()), None)
        if not res:
            return 0, errcode.EC_NORES

        if not res.tpCost:
            return 0, errcode.EC_TOTEM_NOT_NEED_TP

        leftExp = totem.getExp()
        if leftExp < res.exp:
            return 0, errcode.EC_TOTEM_CAN_NOT_TP

        nextRes = Game.res_mgr.res_poslv_totem.get((pos, totem.getLv()+1), None)
        if not nextRes:
            return 0, errcode.EC_NORES

        respBag = self.player.bag.costItem(res.tpCost, constant.ITEM_COST_TOTEM_ACT, wLog=True)
        if not respBag.get("rs", 0):
            return 0, errcode.EC_TOTEM_ACT_NOT_ENOUGH

        while True:
            leftExp -= res.exp
            totem.setLv(nextRes.level, res, nextRes)

            if not nextRes.exp:
                break

            res = nextRes
            nextRes = Game.res_mgr.res_poslv_totem.get((pos, totem.getLv()+1), None)

            if leftExp < nextRes.exp:
                break

        totem.setExp(leftExp)

        # 战力重算
        self.player.attr.RecalFightAbility()


        dTotem = {}
        dTotem["actList"] = [totem.to_init_data()]

        dUpdate = self.player.packRespBag(respBag)
        dUpdate["attr"] = self.player.attr.to_update_data()
        dUpdate["totem"] = dTotem
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp