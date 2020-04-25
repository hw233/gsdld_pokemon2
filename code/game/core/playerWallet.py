#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from game.common import utility
from game.define import constant
from corelib import spawn
from corelib.frame import Game

import config
import datetime
import time

class PlayerWallet(utility.DirtyFlag):
    def __init__(self, owner):
        utility.DirtyFlag.__init__(self)
        self.owner = owner  # 拥有者
        self.coin = 0 #银币
        self.gold = 0 #元宝
        self.bindGold = 0 #绑定元宝
        self.other = {} #其他货币 {道具id：数量}

        self.save_cache = {} #存储缓存

    def markDirty(self):
        utility.DirtyFlag.markDirty(self)
        if self.owner:
            self.owner.markDirty()

    def uninit(self):
        pass

    #存库数据
    def to_save_dict(self, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            self.save_cache = {}
            self.save_cache["coin"] = self.coin
            self.save_cache["gold"] = self.gold
            self.save_cache["bindGold"] = self.bindGold

            self.save_cache["other"] = {}
            for k, v in self.other.items():
                self.save_cache["other"][str(k)] = v
        return self.save_cache

    #读库数据初始化
    def load_from_dict(self, data):
        self.coin = data.get("coin", 0)  # 银币
        self.gold = data.get("gold", 0)  # 元宝
        self.bindGold = data.get("bindGold", 0)  # 绑定元宝

        other = data.get("other", {})  # 其他货币 {道具id：数量}
        for k, v in other.items():
            self.other[int(k)] = v

    #登录初始化下发数据
    def to_init_data(self):
        init_data = {}
        init_data["coin"] = self.coin
        init_data["gold"] = self.gold
        init_data["bindGold"] = self.bindGold
        init_data["other"] = self.other
        return init_data

    # 更新下发数据
    def to_update_data(self, lUpdate):
        update_data = {}
        for itemNo in lUpdate:
            if itemNo == constant.CURRENCY_COIN:
                update_data["coin"] = self.coin
            elif itemNo == constant.CURRENCY_GOLD:
                update_data["gold"] = self.gold
            elif itemNo == constant.CURRENCY_BINDGOLD:
                update_data["bindGold"] = self.bindGold
            else:
                other = update_data.setdefault("other", {})
                other[str(itemNo)] = self.other.get(itemNo, 0)
        return update_data

    def getCurrencyNum(self, itemNo):
        if itemNo == constant.CURRENCY_COIN:
            return self.coin
        elif itemNo == constant.CURRENCY_GOLD:
            return self.gold
        elif itemNo == constant.CURRENCY_BINDGOLD:
            return self.bindGold
        else:
            return self.other.get(itemNo, 0)

    #货币统一添加接口
    def addCurrency(self, reason, dAdd):
        for itemNo, num in dAdd.items():
            if itemNo == constant.CURRENCY_COIN:
                self.coin += num
            elif itemNo == constant.CURRENCY_GOLD:
                self.gold += num
                #运营统计
                self.owner.history.bagHistoryAdd(reason, {constant.CURRENCY_GOLD: num})
            elif itemNo == constant.CURRENCY_BINDGOLD:
                self.bindGold += num
                #运营统计
                self.owner.history.bagHistoryAdd(reason, {constant.CURRENCY_BINDGOLD: num})
            else:
                if itemNo==constant.CURRENCY_EXPLORE:

                    v = self.other.get(itemNo, 0) + num
                    
                    exploreMax = Game.res_mgr.res_common.get("exploreMax")

                    if v>exploreMax.i:
                        v=exploreMax.i

                    self.other[itemNo] = v
                    

                else:
                    self.other[itemNo] = self.other.get(itemNo, 0) + num
        self.markDirty()

    #货币统一花费接口
    def costCurrency(self, reason, dCost):
        for itemNo, num in dCost.items():
            if itemNo == constant.CURRENCY_COIN:
                self.coin -= num
            elif itemNo == constant.CURRENCY_GOLD:
                self.gold -= num
                #运营统计
                self.owner.history.bagHistoryCost(reason, {constant.CURRENCY_GOLD: num})
            elif itemNo == constant.CURRENCY_BINDGOLD:
                self.bindGold -= num
                #运营统计
                self.owner.history.bagHistoryCost(reason, {constant.CURRENCY_BINDGOLD: num})
            else:
                self.other[itemNo] = self.other.get(itemNo, 0) - num
        self.markDirty()





