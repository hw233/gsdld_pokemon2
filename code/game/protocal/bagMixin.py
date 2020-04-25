#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import time

from game.define import errcode, constant, msg_define
from game import Game

from corelib import log

class BagRpcMixin(object):
    if 0:
        from game.core import player as player_md
        player = player_md.Player()

    # 背包扩容(bagAddSize)
    # 请求
    #   类型(tp, int)    1=装备背包
    #   扩容数(add, int)
    #
    # 返回
    #   容量(size, int)
    #   主动推送刷新(allUpdate, json)
    #       游戏模型 - 货币
    def rc_bagAddSize(self, tp, add):
        if add <= 0:
            return 0, errcode.EC_VALUE
        bag = None
        if tp == 1:
            bag = self.player.bag.equip_bag
        if not bag:
            return 0, errcode.EC_NOFOUND

        iOldSize = bag.size
        maxRes = Game.res_mgr.res_common.get("bagMaxSize", None)
        if iOldSize + add > maxRes.i:
            return 0, errcode.EC_BAG_SIZE_MAX
        #先扣钱，再扩容
        res = Game.res_mgr.res_common.get("bagAddSizeCost", None)
        dCost = {}
        for itemNo, num in res.arrayint2.items():
            dCost[itemNo] = num * add
        respBag = self.player.bag.costItem(dCost, constant.ITEM_COST_ADD_BAGSIZE, wLog=True)
        if not respBag.get("rs", 0):
            return 0, errcode.EC_COST_ERR
        iNewSize = bag.addSize(add)
        #记录日志
        Game.glog.log2File("rc_bagAddSize", "%s|%s|%s|%s|%s" % (self.player.id, tp, iOldSize, add, iNewSize))
        #打包返回信息
        dUpdate = self.player.packRespBag(respBag)
        resp = {
            "size": bag.size,
            "allUpdate": dUpdate,
        }
        return 1, resp

    # 道具使用(itemUse)
    # 请求
    #   道具uid(uid, string)
    #   数量(num, int)
    #
    # 返回
    #   主动推送刷新(allUpdate, json)
    #       游戏模型 - 角色背包 - 道具列表
    #       游戏模型 - 其他各种数据变化
    def rc_itemUse(self, uid, num):
        if num <= 0:
            return 0, errcode.EC_PARAMS_ERR
        itemobj = self.player.bag.item_bag.getObj(uid)
        if not itemobj:
            return 0, errcode.EC_NOFOUND
        if itemobj.getNum() < num:
            return 0, errcode.EC_NOT_ENOUGH
        itemRes = Game.res_mgr.res_item.get(itemobj.resID)
        if not itemRes:
            return 0, errcode.EC_NORES
        if not itemRes.use:
            return 0, errcode.EC_TIMES_FULL

        itemobj.Use(num)
        return 1, None

    # 可选宝箱使用(selectBoxUse)
    # 请求
    #     道具uid(uid, string)
    #     数量(num, int)
    #     选择道具id(select, int)
    # 返回
    #     主动推送刷新(allUpdate, json)
    #         游戏模型 - 角色背包 - 道具列表
    #         游戏模型 - 其他各种数据变化
    def rc_selectBoxUse(self, uid, num, select):
        if num <= 0:
            return 0, errcode.EC_PARAMS_ERR
        itemobj = self.player.bag.item_bag.getObj(uid)
        if not itemobj:
            return 0, errcode.EC_NOFOUND
        if itemobj.getNum() < num:
            return 0, errcode.EC_NOT_ENOUGH
        itemRes = Game.res_mgr.res_item.get(itemobj.resID)
        if not itemRes:
            return 0, errcode.EC_NORES
        if not itemRes.use:
            return 0, errcode.EC_TIMES_FULL

        itemobj.Use(num,select)
        return 1, None

    # 道具合成(itemCompound)
    # 请求
    #     道具uid(uid, string)
    #     数量(num, int)
    # 返回
    #     主动推送刷新(allUpdate, json)
    #         游戏模型 - 角色背包 - 道具列表
    def rc_itemCompound(self, uid, num):
        if num <= 0:
            return 0, errcode.EC_PARAMS_ERR
        itemobj = self.player.item_bag.getObj(uid)
        if not itemobj:
            return 0, errcode.EC_NOFOUND
        itemRes = Game.res_mgr.res_item.get(itemobj.resID)
        if not itemRes or not itemRes.compound:
            return 0, errcode.EC_NORES
        iNeed = itemRes.compound[0] * num
        iCompoundId = itemRes.compound[1]
        isRewardID = 0
        if len(itemRes.compound) >= 3:
            isRewardID = itemRes.compound[2]
        rewardRes = None
        if isRewardID:
            rewardRes = Game.res_mgr.res_reward.get(iCompoundId)
            if not rewardRes:
                return 0, errcode.EC_NORES
        else:
            itemCompoundRes = Game.res_mgr.res_item.get(iCompoundId)
            if not itemCompoundRes:
                return 0, errcode.EC_NORES
        if itemobj.getNum() < iNeed:
            return 0, errcode.EC_NOT_ENOUGH
        dCost = {itemobj.resID: iNeed}
        respBag = self.player.bag.costItem(dCost, constant.ITEM_COST_COMPOUND,wLog=True)
        if not respBag.get("rs", 0):
            return 0, errcode.EC_COST_ERR
        if rewardRes:
            dReward = rewardRes.doReward()
            respBag1 = self.player.bag.add(dReward, constant.ITEM_ADD_COMPOUND, wLog=True)
        else:
            dAdd = {iCompoundId:num}
            respBag1 = self.player.bag.add(dAdd, constant.ITEM_ADD_COMPOUND,wLog=True)
        respBag = self.player.mergeRespBag(respBag, respBag1)

        # 打包返回信息
        cost_update = self.player.packRespBag(respBag)
        resp = {
            "allUpdate": cost_update,
        }
        return 1, resp





