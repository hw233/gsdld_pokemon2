#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import time

from game.common import utility
from game.define import constant, msg_define
from corelib.frame import Game, spawn

#角色历史统计
class PlayerHistory(utility.DirtyFlag):
    def __init__(self, owner):
        utility.DirtyFlag.__init__(self)
        self.owner = owner  # 拥有者

        self.history_add = {} #{reason: {统计}}  目前只存储 绑钻 和 钻石，担心数据太多
        self.history_cost = {}  # {reason: {统计}}  目前只存储 绑钻 和 钻石，担心数据太多

        self.history_pet_add = {}  # {reason: {统计}}  resid: 数量
        self.history_pet_cost = {}  # {reason: {统计}}  resid: 数量

        self.save_cache = {} #存储缓存


    def markDirty(self):
        utility.DirtyFlag.markDirty(self)
        if self.owner:
            self.owner.markDirty()

    #存库数据
    def to_save_dict(self, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            self.save_cache = {}
            self.save_cache["item_add"] = self.history_add
            self.save_cache["item_cost"] = self.history_cost
            self.save_cache["pet_add"] = self.history_pet_add
            self.save_cache["pet_cost"] = self.history_pet_cost
        return self.save_cache

    #读库数据初始化
    def load_from_dict(self, data):
        self.history_add = data.get("item_add", {})
        self.history_cost = data.get("item_cost", {})
        self.history_add = data.get("pet_add", {})
        self.history_cost = data.get("pet_cost", {})


    #登录初始化下发数据
    def to_init_data(self):
        init_data = {}
        return init_data

    def to_wee_hour_data(self):
        pass

    def do_login(self):
        pass

    def uninit(self):
        pass

    def getHistory(self, key):
        return getattr(self, key)

    def setHistory(self, key, value):
        setattr(self, key, value)
        self.markDirty()

    def bagHistoryAdd(self, reason, dAdd):
        dreason = self.history_add.setdefault(str(reason), {})
        for itemNo, num in dAdd.items():
            sitemNo = str(itemNo)
            dreason[sitemNo] = dreason.get(sitemNo, 0) + num
        self.history_add[str(reason)] = dreason
        self.markDirty()

    def bagHistoryCost(self, reason, dCost):
        dreason = self.history_cost.setdefault(str(reason), {})
        for itemNo, num in dCost.items():
            sitemNo = str(itemNo)
            dreason[sitemNo] = dreason.get(sitemNo, 0) + num
        self.history_cost[str(reason)] = dreason
        self.markDirty()

    def petHistoryAdd(self, reason, dAdd):
        dreason = self.history_pet_add.setdefault(str(reason), {})
        for resID, num in dAdd.items():
            sresID = str(resID)
            dreason[sresID] = dreason.get(sresID, 0) + num
        self.history_pet_add[str(reason)] = dreason
        self.markDirty()

    def petHistoryCost(self, reason, dCost):
        dreason = self.history_pet_cost.setdefault(str(reason), {})
        for resID, num in dCost.items():
            sresID = str(resID)
            dreason[sresID] = dreason.get(sresID, 0) + num
        self.history_pet_cost[str(reason)] = dreason
        self.markDirty()









