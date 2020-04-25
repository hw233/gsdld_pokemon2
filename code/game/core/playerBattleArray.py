#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import time

from game.common import utility
from game.define import constant, msg_define
from corelib.frame import Game, spawn

#角色出战阵型
class PlayerBattleArray(utility.DirtyFlag):
    def __init__(self, owner):
        utility.DirtyFlag.__init__(self)
        self.owner = owner  # 拥有者

        self.troops = {} #{出战队伍类型: BattleArray}

        self.save_cache = {} #存储缓存


    def markDirty(self):
        utility.DirtyFlag.markDirty(self)
        if self.owner:
            self.owner.markDirty()

    #存库数据
    def to_save_dict(self, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            self.save_cache = {}
            self.save_cache["troops"] = []
            for one in self.troops.values():
                self.save_cache["troops"].append(one.to_save_dict(forced=forced))
        return self.save_cache

    #读库数据初始化
    def load_from_dict(self, data):
        troops = data.get("troops", [])
        for one in troops:
            obj = BattleArray(self)
            obj.load_from_dict(one)
            self.troops[obj.battletype] = obj

    #登录初始化下发数据
    def to_init_data(self):
        init_data = {}
        init_data["troops"] = []
        for obj in self.troops.values():
            init_data["troops"].append(obj.to_init_data())
        return init_data

    def to_wee_hour_data(self):
        pass

    def uninit(self):
        pass

    def getBattleArray(self, iType):
        obj = self.troops.get(iType)
        if not obj:
            obj = BattleArray(self, iType)
            self.troops[iType] = obj
            self.markDirty()
        return obj


class BattleArray(utility.DirtyFlag):
    def __init__(self, owner, battletype=0):
        utility.DirtyFlag.__init__(self)
        self.owner = owner

        self.battletype = battletype
        self.position = [] #[{位置： 唯一id}]

        self.save_cache = {}


    def markDirty(self):
        utility.DirtyFlag.markDirty(self)
        if self.owner:
            self.owner.markDirty()

    # 存库数据
    def to_save_dict(self, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            self.save_cache = {}
            self.save_cache["tp"] = self.battletype
            self.save_cache["d"] = []
            for one in self.position:
                oneSave = {}
                for k, v in one.items():
                    oneSave[str(k)] = v
                self.save_cache["d"].append(oneSave)
        return self.save_cache

    # 读库数据初始化
    def load_from_dict(self, data):
        self.battletype = data.get("tp", {})

        position = data.get("d", [])
        for one in position:
            oneSave = {}
            for k, v in one.items():
                oneSave[int(k)] = v
            self.position.append(oneSave)

    #登录初始化下发数据
    def to_init_data(self):
        init_data = {}
        init_data["tp"] = self.battletype
        init_data["d"] = self.position
        return init_data

    def setPosition(self, position):
        old = []
        for one in self.position:
            old.append(set(one.values()))

        new = []
        for one in position:
            new.append(set(one.values()))

        #补位对齐
        iLen = max(len(old), len(new))
        for i in range(iLen):
            if len(old) < i+1:
                old.append(set())
            if len(new) < i+1:
                new.append(set())

        #换阵
        change = []
        for i in range(iLen):
            one_old = old[i]
            one_new = new[i]

            for uid in one_old:
                pet = self.owner.owner.pet.getPet(uid)
                if pet and pet not in change:
                    change.append(pet)
            for uid in one_new:
                pet = self.owner.owner.pet.getPet(uid)
                if pet and pet not in change:
                    change.append(pet)

            # 原来的宠物先下阵
            for uid in one_old.difference(one_new):
                pet = self.owner.owner.pet.getPet(uid)
                if pet:
                    pet.removeBattleArray(self.battletype)
            #新宠物上阵
            for uid in one_new.difference(one_old):
                pet = self.owner.owner.pet.getPet(uid)
                if pet:
                    pet.addBattleArray(self.battletype)
        self.position = position
        self.markDirty()

        # 抛出消息
        self.owner.owner.safe_pub(msg_define.MSG_CHANGE_BATTLE_ARRAY, self.battletype, self.position)

        return change

    def getPosition(self):
        return self.position








