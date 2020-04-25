#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from game.common import utility
from corelib.frame import Game
from game.define import constant
from game.core.equip import CreatEquip
from game.core.item import CreatItem

class BagContainerBase(utility.DirtyFlag):
    """背包容器"""
    def __init__(self, owner, size, name):
        utility.DirtyFlag.__init__(self)

        self.owner = owner

        self.name = name #背包名称唯一
        self.objs = {} #{k：v}
        self.size = size  # 背包容量
        self.buy_count = 0 #背包扩容次数

        self.save_cache = {}  # 存储缓存

    def markDirty(self):
        utility.DirtyFlag.markDirty(self)
        if self.owner:
            self.owner.markDirty()

    #存库数据
    def doSave(self, saveFunc, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            self.save_cache = {}
            self.save_cache["name"] = self.name
            self.save_cache["size"] = self.size
            self.save_cache["buy_count"] = self.buy_count

            self.save_cache["objs"] = []
            for val in self.objs.values():
                self.save_cache["objs"].append(saveFunc(val, forced=forced))
        return self.save_cache

    # 读库数据初始化
    def doLoad(self, data, loadFunc):
        self.name = data.get("name", '')
        self.size = data.get("size", self.size)
        self.buy_count = data.get("buy_count", 0)

        objsData = data.get("objs", [])  # 数据
        for one in objsData:
            k, v = loadFunc(one)
            if k is None:
                continue
            self.objs[k] = v

    def doAdd(self, data, reason, wLog=False):
        raise NotImplementedError

    def doCost(self, data, reason, wLog=False):
        raise NotImplementedError

    def addSize(self, num):
        self.size += num
        self.markDirty()

    def addBuyCount(self, count):
        self.buy_count += count
        self.markDirty()

    def getObj(self, key):
        return self.objs.get(key)

    def popObj(self, key):
        val = self.objs.pop(key, None)
        self.markDirty()
        return val

    def canAdd(self, num):
        if len(self.objs) + num > self.size:
            return 0
        else:
            return 1

    def getFree(self):
        return self.size - len(self.objs)


class EquipBagBase(BagContainerBase):
    # 存库数据
    def to_save_dict(self, forced=False):
        return super(EquipBagBase, self).doSave(self.saveFunc, forced=forced)

    def saveFunc(self, one, forced=False):
        return one.to_save_dict(forced=forced)

    def load_from_dict(self, data):
        super(EquipBagBase, self).doLoad(data, self.loadFunc)

    def loadFunc(self, one):
        k, v = None, None
        resID = one.get("resID", 0)
        _, obj = CreatEquip(resID, data=one, owner=self)
        if obj:
            k, v = obj.id, obj
        return k, v

    # 登录初始化下发数据
    def to_init_data(self):
        init_data = {}
        init_data["size"] = self.size
        init_data["buyCount"] = self.buy_count
        init_data["objs"] = []
        for obj in self.objs.values():
            init_data["objs"].append(obj.to_init_data())
        return init_data

    #更新下发数据
    def to_update_data(self, equips):
        update_data = {}
        if equips:
            update_data["size"] = self.size
            for equip in equips:
                lupdate = update_data.setdefault("objs", [])
                lupdate.append(equip.to_init_data())
        return update_data

    def doAdd(self, objs, reason, wLog=False):
        sLog = ""
        if not self.canAdd(len(objs)):
            return False, sLog
        for obj in objs:
            obj.set_owner(self)
            self.objs[obj.id] = obj
            if wLog:
                sLog.join("@%s" % obj.to_save_dict())
        # 致脏
        self.markDirty()
        return True, sLog


    def doCost(self, objs, reason, wLog=False):
        sLog = ""
        for obj in objs:
            if self.objs.pop(obj.id, None):
                obj.setNum(0)
                if wLog:
                    sLog.join("@%s" % obj.to_save_dict())
        # 致脏
        self.markDirty()
        return True, sLog


    def addByData(self, data, reason, wLog=False):
        sLog = ""
        resp_equips = []
        send_mails = {}
        for resID, num in data.items():
            if self.getFree() >= num:
                addList = []
                for i in range(num):
                    rs, obj = CreatEquip(resID)
                    if not rs:
                        continue
                    addList.append(obj)
                rs, _sLog = self.doAdd(addList, reason, wLog=wLog)
                if rs:
                    sLog.join(_sLog)
                    resp_equips.extend(addList)
            else:
                free = self.getFree()
                has = num - free
                addList = []
                for i in range(self.getFree()):
                    rs, obj = CreatEquip(resID)
                    if not rs:
                        continue
                    addList.append(obj)
                rs, _sLog = self.doAdd(addList, reason, wLog=wLog)
                if rs:
                    sLog.join(_sLog)
                    resp_equips.extend(addList)

                if has:
                    send_mails[resID] = send_mails.get(resID, 0) + has
        return sLog, resp_equips, send_mails


class PetEquipBag(EquipBagBase):
    """宠物普通装备"""
    pass


class YiShouEquipBag(EquipBagBase):
    """异兽之灵背包"""
    pass



class ItemBag(BagContainerBase):
    def __init__(self, owner, size, name):
        super(ItemBag, self).__init__(owner, size, name)
        self.resID_obj = {}

    # 存库数据
    def to_save_dict(self, forced=False):
        return super(ItemBag, self).doSave(self.saveFunc, forced=forced)

    def saveFunc(self, one, forced=False):
        return one.to_save_dict(forced=forced)

    def load_from_dict(self, data):
        super(ItemBag, self).doLoad(data, self.loadFunc)
        for obj in self.objs.values():
            self.resID_obj[obj.resID] = obj

    def loadFunc(self, one):
        k, v = None, None
        resID = one.get("resID", 0)
        _, obj = CreatItem(resID, data=one, owner=self)
        if obj:
            k, v = obj.id, obj
        return k, v

    # 登录初始化下发数据
    def to_init_data(self):
        init_data = {}
        init_data["size"] = self.size
        init_data["buyCount"] = self.buy_count
        init_data["objs"] = []
        for obj in self.objs.values():
            init_data["objs"].append(obj.to_init_data())
        return init_data

    #更新下发数据
    def to_update_data(self, items):
        update_data = {}
        if items:
            for item in items:
                lupdate = update_data.setdefault("objs", [])
                lupdate.append(item.to_init_data())
        return update_data

    def getNumByResID(self, resID):
        obj = self.resID_obj.get(resID)
        if obj:
            return obj.getNum()
        else:
            return 0

    def doAdd(self, objs, reason, wLog=False):
        sLog = ""
        if not self.canAdd(len(objs)):
            return False, sLog
        for obj in objs:
            old = 0
            add = obj.getNum()

            oldobj = self.resID_obj.get(obj.resID)
            if oldobj:
                old = oldobj.getNum()
                oldobj.setNum(old + add)
                obj = oldobj
            else:
                obj.set_owner(self)
                self.objs[obj.id] = obj
                self.resID_obj[obj.resID] = obj
            if wLog:
                new = obj.getNum()
                sLog.join("@%s_%s_%s" % (old, add, new))
        # 致脏
        self.markDirty()
        return True, sLog


    def addByData(self, data, reason, wLog=False):
        sLog = ""
        resp_items = []
        send_mails = {}
        for resID, num in data.items():
            res = Game.res_mgr.res_item.get(resID)
            if not res:
                continue
            # 判断是否需要唯一化的物品
            is_only = 0
            if res.timeType:
                is_only = 1
            if is_only:
                if self.getFree() >= num:
                    addList = []
                    for i in range(num):
                        _, obj = CreatItem(resID, owner=self)
                        if not obj:
                            continue
                        addList.append(obj)
                    rs, _sLog = self.doAdd(addList, reason, wLog=wLog)
                    if rs:
                        sLog.join(_sLog)
                        resp_items.extend(addList)
                else:
                    free = self.getFree()
                    has = num - free
                    addList = []
                    for i in range(self.getFree()):
                        _, obj = CreatItem(resID, owner=self)
                        if not obj:
                            continue
                        addList.append(obj)
                    rs, _sLog = self.doAdd(addList, reason, wLog=wLog)
                    if rs:
                        sLog.join(_sLog)
                        resp_items.extend(addList)

                    if has:
                        send_mails[resID] = send_mails.get(resID, 0) + has
            else:
                _, obj = CreatItem(resID, owner=self)
                obj.setNum(num)
                rs, _sLog = self.doAdd([obj], reason, wLog=wLog)
                if rs:
                    sLog.join(_sLog)
                    obj = self.resID_obj.get(obj.resID)
                    resp_items.append(obj)

        return sLog, resp_items, send_mails


    def costByData(self, data, reason, wLog=False):
        sLog = ""
        resp_items = []
        for resID, num in data.items():
            obj = self.resID_obj.get(resID)
            if not obj:
                return False, sLog, resp_items
            if obj.getNum() < num:
                return False, sLog, resp_items

        for resID, num in data.items():
            obj = self.resID_obj.get(resID)
            old = obj.getNum()
            dele = num
            new = old - dele
            if new <= 0:
                new = 0

            obj.setNum(new)
            resp_items.append(obj)
            #日志
            if wLog:
                sLog.join("@%s_%s_%s" % (old, dele, new))

            # 清理需要删除的物品
            if new <= 0:
                self.resID_obj.pop(resID, None)
                self.objs.pop(obj.id, None)

        return True, sLog, resp_items

















