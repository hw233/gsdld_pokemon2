#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import time
from game.common import utility
from corelib.frame import Game
from game.define import constant

class PlayerHouse(utility.DirtyFlag):
    def __init__(self, owner):
        utility.DirtyFlag.__init__(self)
        self.owner = owner      # 拥有者
        self.type = 0           # 房子类型 1普通 2高级 3豪华
        self.houseId = 1        # 房子id
        self.exp = 0            # 经验
        self.unrecvExp = []     # 未领取经验

        self.save_cache = {}

    def markDirty(self):
        utility.DirtyFlag.markDirty(self)
        if self.owner:
            self.owner.markDirty()

    # 存库数据
    def to_save_dict(self, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            self.save_cache = {}
            if self.type:
                self.save_cache["type"] = self.type
            if self.houseId != 1:
                self.save_cache["houseId"] = self.houseId
            if self.exp:
                self.save_cache["exp"] = self.exp
            if self.unrecvExp:
                self.save_cache["unrecvExp"] = self.unrecvExp
        return self.save_cache

    #读库数据初始化
    def load_from_dict(self, data):
        self.type = data.get("type", 0)
        self.houseId = data.get("houseId", 1)
        self.exp = data.get("exp", 0)
        self.unrecvExp = data.get("unrecvExp", [])

    #登录初始化下发数据
    def to_init_data(self):
        init_data = {}
        init_data["type"] = self.type
        init_data["houseId"] = self.houseId
        init_data["exp"] = self.exp
        init_data["hasUnrecvExp"] = int(len(self.unrecvExp) > 0)
        return init_data

    def recalAttr(self):
        attr = Game.res_mgr.res_marry_house_attr.get((self.type, self.houseId), None)
        if attr:
            self.owner.attr.addAttr(attr, constant.PKM2_FA_TYPE_10, constant.PKM2_ATTR_CONTAINER_GLOBAL)

    def uninit(self):
        pass

    def setType(self, type):
        if type > self.type:
            if self.type > 0:
                oldAttr = Game.res_mgr.res_marry_house_attr.get((self.type, self.houseId), None)
                if oldAttr:
                    self.owner.attr.delAttr(oldAttr, constant.PKM2_FA_TYPE_10, constant.PKM2_ATTR_CONTAINER_GLOBAL)

            self.type = type
            newAttr = Game.res_mgr.res_marry_house_attr.get((self.type, self.houseId), None)
            self.owner.attr.addAttr(newAttr, constant.PKM2_FA_TYPE_10, constant.PKM2_ATTR_CONTAINER_GLOBAL)

            self.markDirty()

    def getExp(self):
        return self.exp

    def setExp(self, exp):
        self.exp = exp
        self.markDirty()

    def setHouseId(self, houseId):
        self.houseId = houseId
        self.markDirty()

    def getHouseId(self):
        return self.houseId

    def getUnrecvExp(self):
        return self.unrecvExp

    def resetUnrecvExp(self):
        self.unrecvExp = []
        self.markDirty()

    def addUnrecvExp(self, exp, kind):
        self.unrecvExp.append({
            "kind": kind,
            "exp": exp,
            "time": int(time.time()),
        })
        self.markDirty()

    def getHouseType(self):
        return self.type



