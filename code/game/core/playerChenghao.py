#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from game.common import utility
from game.define import constant, msg_define
from game import Game

# 称号(chenghaoInfo, json)
# 	已经激活id(active, [int])
# 	使用中id(use, int)
class PlayerChenghao(utility.DirtyFlag):
    def __init__(self, owner):
        utility.DirtyFlag.__init__(self)
        self.owner = owner  # 拥有者
        self.use = 0 #使用中id
        self.active = [] #激活列表
        self.levels = {} #称号等级
        self.save_cache = {} #存储缓存
        # self.owner.sub(msg_define.MSG_ROLE_LEVEL_UPGRADE, self.event_lv_uprade)

    def markDirty(self):
        utility.DirtyFlag.markDirty(self)
        if self.owner:
            self.owner.markDirty()

    #存库数据
    def to_save_dict(self, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            self.save_cache = {}
            if self.use:
                self.save_cache["use"] = self.use
            if self.active:
                self.save_cache["active"] = self.active

            if self.levels:
                self.save_cache["levels"] = {}
                for k, v in self.levels.items():
                    self.save_cache["levels"][str(k)] = v
        return self.save_cache

    #读库数据初始化
    def load_from_dict(self, data):
        self.use = data.get("use", 0) 
        self.active = data.get("active", [])

        levels = data.get("levels", {})
        for k, v in levels.items():
            self.levels[int(k)] = v

    #登录初始化下发数据
    def to_init_data(self):
        init_data = {}
        init_data["use"] = self.use
        init_data["active"] = self.active

        levels = []
        for k, v in self.levels.items():
            levels.append({"k": k, "v": v})
        init_data["levels"] = levels
        return init_data

    def recalAttr(self):
        total = {}
        # 激活列表
        for id in self.active:
            res = Game.res_mgr.res_chenghao.get(id)
            if res:
                for name, iNum in res.attr.items():
                    total[name] = total.get(name, 0) + iNum
        # 称号等级
        for id, lv in self.levels.items():
            res = Game.res_mgr.res_chenghao.get(id)
            if res:
                for name, iNum in res.attr.items():
                    total[name] = total.get(name, 0) + iNum*lv

        if total:
            self.owner.attr.addAttr(total, constant.PKM2_FA_TYPE_11, constant.PKM2_ATTR_CONTAINER_GLOBAL)


    def activeChenghao(self, id):
        if id in self.active:
            return False

        res = Game.res_mgr.res_chenghao.get(id)

        self.owner.attr.addAttr(res.attr, constant.PKM2_FA_TYPE_11, constant.PKM2_ATTR_CONTAINER_GLOBAL)

        self.active.append(id)
        self.use=id

        self.owner.safe_pub(msg_define.MSG_CHENGHAO_ACT, id)
        self.markDirty()
        return True

    def upgradeChenghao(self, id):
        if id not in self.active:
            return False

        res = Game.res_mgr.res_chenghao.get(id)

        self.owner.attr.addAttr(res.attr, constant.PKM2_FA_TYPE_11, constant.PKM2_ATTR_CONTAINER_GLOBAL)

        level = self.levels.setdefault(id, 0)
        self.levels[id] = level + 1

        self.markDirty()
        return True

    def useChenghao(self,id):
        self.use=id
        self.markDirty()
    
    def uninit(self):
        pass
        # self.owner.unsub(msg_define.MSG_ROLE_LEVEL_UPGRADE, self.event_lv_uprade)

    # def event_lv_uprade(self):
    #     if 1 not in self.active:
    #         if self.owner.checkOpenLimit(constant.CHENGHAO_OPEN_ID_1):
    #             self.active.append(1)
    #             res = Game.res_mgr.res_chenghao.get(1)
    #             self.owner.attr.addAttr(res.attr, constant.PKM2_FA_TYPE_11, constant.PKM2_ATTR_CONTAINER_GLOBAL)
    #             self.owner.attr.RecalFightAbility()
    #             self.owner.safe_pub(msg_define.MSG_CHENGHAO_ACT, 1)

    def getUse(self):
        return self.use

    def getChenghaoNum(self):
        return len(self.active)












