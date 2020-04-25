#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from game.common import utility
from corelib.frame import Game
from game.define import constant, msg_define
from game.core.cycleData import CycleDay

# 图腾模块(totems, json)
# 	已激活图腾列表(act, [json])
# 		图腾部位(pos, int)
# 		等级(lv, int)
# 		经验(exp, int)
# 		已升级次数(upNum, int)
# 		图腾暴击配置表id(bjId, int)

class PlayerTotem(utility.DirtyFlag):
    def __init__(self, owner):
        utility.DirtyFlag.__init__(self)
        self.owner = owner # 拥有者
        self.actList = {} #{图腾pos：obj}

        self.cycleDay = CycleDay(self)

        self.save_cache = {} #存储缓存

    def markDirty(self):
        utility.DirtyFlag.markDirty(self)
        if self.owner:
            self.owner.markDirty()

    # 存库数据
    def to_save_dict(self, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            self.save_cache = {}
            self.save_cache["actList"] = []
            for totem in self.actList.values():
                self.save_cache["actList"].append(totem.to_save_dict(forced=forced))
            self.save_cache["cycleDay"] = self.cycleDay.to_save_bytes()
        return self.save_cache

    #读库数据初始化
    def load_from_dict(self, data):
        self.cycleDay.load_from_dict(data.get("cycleDay", ""))
        totemData = data.get("actList", [])
        for one in totemData:
            res = Game.res_mgr.res_poslv_totem.get((one["pos"], one["lv"]), None)
            if res:
                totem = Totem(res, data=one, owner=self.owner)
                self.actList[totem.pos] = totem
            else:
                Game.glog.log2File("TotemLoadNotFindError", "%s|%s" % (self.owner.id, one))

    #登录初始化下发数据
    def to_init_data(self):
        init_data = {}
        init_data["actList"] = []
        for  totem in self.actList.values():
            init_data["actList"].append(totem.to_init_data())

        return init_data

    def to_wee_hour_data(self):
        init_data = {}
        init_data["actList"] = []
        for totem in self.actList.values():
            init_data["actList"].append(totem.to_wee_hour_data())
        return init_data

    def recalAttr(self):
        for eleType in constant.ALL_ELE_TYPE:
            total = {}
            for obj in self.actList.values(): # {图腾pos：obj}
                res = Game.res_mgr.res_poslv_totem.get((obj.pos, obj.lv), None)
                if res and res.ele == eleType:
                    for name, iNum in res.attr1.items():
                        total[name] = total.get(name, 0)
                    for name, iNum in res.attr2.items():
                        total[name] = total.get(name, 0)

            if total:
                self.owner.attr.addAttr(total, constant.PKM2_FA_TYPE_9, constant.MAP_ELETYPE_ATTR_CONTAINER.get(eleType))

    def uninit(self):
        pass

    def actTotem(self, res):
        if res.pos in self.actList:
            return False

        totem = Totem(res, owner=self.owner)
        totem.setBjResId(1)
        self.actList[res.pos] = totem

        self.owner.attr.addAttr(res.attr1, constant.PKM2_FA_TYPE_9, constant.MAP_ELETYPE_ATTR_CONTAINER.get(res.ele))
        self.owner.attr.addAttr(res.attr2, constant.PKM2_FA_TYPE_9, constant.MAP_ELETYPE_ATTR_CONTAINER.get(res.ele))
        totem.markDirty()

        # 抛事件
        self.owner.safe_pub(msg_define.MSG_TOTEM_ACT, res.pos)
        return True


    def getTotem(self, pos):
        return self.actList.get(pos, None)

    def getActNum(self):
        return len(self.actList)

    def getMaxLv(self):
        iMax = 0
        for totem in self.actList.values():
            if totem.lv > iMax:
                iMax = totem.lv
        return iMax

class Totem(utility.DirtyFlag):
    def __init__(self, res, data=None, owner=None):
        utility.DirtyFlag.__init__(self)
        self.pos = res.pos
        self.lv = 1
        self.exp = 0

        self.save_cache = {}

        if data:
            self.load_from_dict(data)
        if owner:
            self.set_owner(owner)

    def set_owner(self, owner):
        self.ownerTotem = owner.totem

    def markDirty(self):
        utility.DirtyFlag.markDirty(self)
        if self.ownerTotem:
            self.ownerTotem.markDirty()

    def to_save_dict(self, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            self.save_cache = {}
            self.save_cache["pos"] = self.pos
            self.save_cache["lv"] = self.lv
            self.save_cache["exp"] = self.exp

        return self.save_cache

    def load_from_dict(self, data):
        self.pos = data.get("pos", 0)
        self.lv = data.get("lv", 0)
        self.exp = data.get("exp", 0)


    def to_init_data(self):
        init_data = {}
        init_data["pos"] = self.pos
        init_data["lv"] = self.lv
        init_data["exp"] = self.exp
        bj = self.ownerTotem.cycleDay.Query("BjResId", {})
        times = self.ownerTotem.cycleDay.Query("UpgradeTimes", {})

        init_data["upNum"] = times.get(self.pos, 0)
        init_data["bjId"] = bj.get(self.pos, 0)

        return init_data

    def to_wee_hour_data(self):
        return self.to_init_data()

    def setBjResId(self, id):
        bj = self.ownerTotem.cycleDay.Query("BjResId", {})
        bj[self.pos] = id
        self.ownerTotem.cycleDay.Set("BjResId", bj)
        self.markDirty()

    def getBjResId(self):
        bj = self.ownerTotem.cycleDay.Query("BjResId", {})
        return bj.get(self.pos, 1)

    def setUpgradeTimes(self, num):
        times = self.ownerTotem.cycleDay.Query("UpgradeTimes", {})
        times[self.pos] = num
        self.ownerTotem.cycleDay.Set("UpgradeTimes", times)
        self.markDirty()

    def getUpgradeTimes(self):
        times = self.ownerTotem.cycleDay.Query("UpgradeTimes", {})
        return times.get(self.pos, 0)

    def getExp(self):
        return self.exp

    def setExp(self, exp):
        self.exp = exp
        self.markDirty()

    def getLv(self):
        return self.lv

    def setLv(self, lv, oldRes, newRes):
        self.lv = lv
        #清除旧等级属性
        self.ownerTotem.owner.attr.delAttr(oldRes.attr1, constant.PKM2_FA_TYPE_9, constant.MAP_ELETYPE_ATTR_CONTAINER.get(oldRes.ele))
        self.ownerTotem.owner.attr.delAttr(oldRes.attr2, constant.PKM2_FA_TYPE_9, constant.MAP_ELETYPE_ATTR_CONTAINER.get(oldRes.ele))
        #添加新等级属性
        self.ownerTotem.owner.attr.addAttr(newRes.attr1, constant.PKM2_FA_TYPE_9, constant.MAP_ELETYPE_ATTR_CONTAINER.get(newRes.ele))
        self.ownerTotem.owner.attr.addAttr(newRes.attr2, constant.PKM2_FA_TYPE_9, constant.MAP_ELETYPE_ATTR_CONTAINER.get(newRes.ele))
        self.markDirty()
        # 抛事件
        self.ownerTotem.owner.safe_pub(msg_define.MSG_TOTEM_UPGRADE)

