#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import copy
from game.define import errcode, constant
from game import Game
from game.common import utility


class HouseMixin(object):
    if 0:
        from game.core import player as player_md
        player = player_md.Player()


    # 获取房子信息(getHouseInfo)
    # 	请求
    # 	返回
    # 		对象个人数据(spouseInfo, json)
    # 			角色名称(name, string)
    # 			角色外形列表(showList, [json])
    # 				模块类型(modeType, int)
    # 					1=坐骑 2=翅膀 7=天仙 8=神兵
    # 				幻化类型(imageType, int)
    # 					1=坐骑 2=坐骑皮肤 (其他模块通用)
    # 				幻化id(imageId, int)
    # 					根据类型读取不同的配置表
    # 			称号id(title, int)
    # 			时装id(fashion, int)
    # 			性别(sex, int)
    # 				0=? 1=男 2=女
    # 			套装id(outfit, int)
    def rc_getHouseInfo(self):
        if not self.player.getMarryStatus():
            return 1, None

        spousePid = self.player.marry.getSpousePid()
        from game.mgr.player import get_rpc_player
        spousePlayer = get_rpc_player(spousePid, offline=True)
        if not spousePlayer:
            return 0, errcode.EC_NOFOUND

        resp = {
            "spouseInfo": spousePlayer.packbaseInfo(),
        }

        return 1, resp

    # 升阶(houseUpgrade)
    # 	请求
    # 		是否自动(auto, int)
    # 	返回
    # 		房子id(houseId, int)
    # 		经验(exp, int)
    # 		主动推送刷新(allUpdate,json)
    # 			游戏模型-货币
    # 			游戏模型-角色背包
    # 			游戏模型-角色属性
    # 			游戏模型-角色基础-战力
    def rc_houseUpgrade(self, auto):
        houseType = self.player.house.getHouseType()
        houseId = self.player.house.getHouseId()
        leftExp = self.player.house.getExp()

        if not houseType:
            return 0, errcode.EC_HOUSE_NO_HOUSE

        if not self.player.marry.getMarryStatus():
            return 0, errcode.EC_MARRY_NOT_MARRY

        houseRes = Game.res_mgr.res_house.get(houseId, None)
        if not houseRes:
            return 0, errcode.EC_NORES

        if not houseRes.exp:
            return 0, errcode.EC_HOUSE_MAX_LEVEL

        respBag = self.player.bag.costItem(houseRes.cost, constant.ITEM_COST_HOUSE_UPGRADE, wLog=True, auto=auto)
        if not respBag.get("rs", 0):
            return 0, errcode.EC_HOUSE_UPGRADE_NOT_ENOUGH

        leftExp += houseRes.addExp

        if leftExp >= houseRes.exp:
            leftExp -= houseRes.exp
            oldAttr = Game.res_mgr.res_marry_house_attr.get((houseType, houseId), None)
            if oldAttr:
                self.player.attr.delAttr(oldAttr, constant.PKM2_FA_TYPE_10, constant.PKM2_ATTR_CONTAINER_GLOBAL)

            houseId += 1
            self.player.house.setHouseId(houseId)
            newAttr = Game.res_mgr.res_marry_house_attr.get((houseType, houseId), None)
            self.player.attr.addAttr(newAttr, constant.PKM2_FA_TYPE_10, constant.PKM2_ATTR_CONTAINER_GLOBAL)
            self.player.attr.RecalFightAbility()

        self.player.house.setExp(leftExp)

        # 给对象加经验
        spousePid = self.player.marry.getSpousePid()
        from game.mgr.player import get_rpc_player
        spousePlayer = get_rpc_player(spousePid, offline=True)
        if spousePlayer:
            spousePlayer.addHouseExp(houseRes.addExp, self.player.marry.getKind())

        dUpdate = self.player.packRespBag(respBag)
        dUpdate["attr"] = self.player.attr.to_update_data()
        resp = {
            "allUpdate": dUpdate,
            "houseId": houseId,
            "exp": leftExp,
        }
        return 1, resp

    # 获取未领取经验信息(getUnrecvExpInfo)
    # 	请求
    # 	返回
    # 		经验列表(expList, [json]
    # 			时间(time, int)
    # 			经验(exp, int)
    # 			我当时类型(kind, int)
    def rc_getUnrecvExpInfo(self):
        unrecvExp = self.player.house.getUnrecvExp()
        resp = {
            "expList": unrecvExp,
        }

        return 1, resp

    # 领取经验(receiveExp)
    # 	请求
    # 	返回
    # 		房子id(houseId, int)
    # 		经验(exp, int)
    # 		主动推送刷新(allUpdate,json)
    # 			游戏模型-角色属性
    # 			游戏模型-角色基础-战力
    def rc_receiveExp(self):
        houseType = self.player.house.getHouseType()
        houseId = self.player.house.getHouseId()
        leftExp = self.player.house.getExp()

        if not houseType:
            return 0, errcode.EC_HOUSE_NO_HOUSE

        houseRes = Game.res_mgr.res_house.get(houseId, None)
        if not houseRes:
            return 0, errcode.EC_NORES

        if not houseRes.exp:
            return 0, errcode.EC_HOUSE_MAX_LEVEL

        unrecvExp = self.player.house.getUnrecvExp()
        self.player.house.resetUnrecvExp()

        for item in unrecvExp:
            leftExp += item.get("exp", 0)

        while leftExp >= houseRes.exp:
            leftExp -= houseRes.exp
            oldAttr = Game.res_mgr.res_marry_house_attr.get((houseType, houseId), None)
            if oldAttr:
                self.player.attr.delAttr(oldAttr, constant.PKM2_FA_TYPE_10, constant.PKM2_ATTR_CONTAINER_GLOBAL)

            houseId += 1
            self.player.house.setHouseId(houseId)
            newAttr = Game.res_mgr.res_marry_house_attr.get((houseType, houseId), None)
            self.player.attr.addAttr(newAttr, constant.PKM2_FA_TYPE_10, constant.PKM2_ATTR_CONTAINER_GLOBAL)
            self.player.attr.RecalFightAbility()
            houseRes = Game.res_mgr.res_house.get(houseId, None)
            if not houseRes:
                break

        self.player.house.setExp(leftExp)


        dUpdate = {}
        dUpdate["base"] = {"fa": self.player.base.fa}
        dUpdate["attr"] = self.player.attr.to_update_data()
        resp = {
            "allUpdate": dUpdate,
            "houseId": houseId,
            "exp": leftExp,
        }

        return 1, resp