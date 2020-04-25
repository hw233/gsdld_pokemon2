#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import time

from game.common import utility
from game.define import constant

from corelib.frame import Game
from corelib import spawn


#所有物品基类
class ItemBase(utility.DirtyFlag):
    def __init__(self, res, data=None, owner=None):
        utility.DirtyFlag.__init__(self)
        self.id = "" # 物品唯一id （添加给角色才生成， 否则为一个系统设定值）角色id + 自增
        self.resID = res.id  # 配置表id
        self.iNum = 1 #数量  默认为1
        self.endTime = 0 #过期时间

        self.save_cache = {}  # 存储缓存

        if data:
            self.load_from_dict(data)
        if owner:
            self.set_owner(owner)
        if getattr(res, "timeType", None) and not self.endTime:
            self.init_endTime(res)

    def set_owner(self, ownerMode):
        self.ownerMode = ownerMode.owner
        if not self.id:
            pid = self.ownerMode.owner.id
            self.id = "%s-%s"%(pid, self.ownerMode.owner.data.GenerateItemTranceNo())
            self.markDirty()

    def markDirty(self):
        utility.DirtyFlag.markDirty(self)
        if self.ownerMode:
            self.ownerMode.markDirty()

    # 存库数据
    def to_save_dict(self, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            self.save_cache = {}
            self.save_cache["id"] = self.id
            self.save_cache["resID"] = self.resID
            self.save_cache["n"] = self.iNum
            self.save_cache["et"] = self.endTime
        return self.save_cache

    # 读库数据初始化
    def load_from_dict(self, data):
        self.id = data.get("id", "")  # 物品唯一id
        self.resID = data.get("resID", 0)  # 配置表id
        self.iNum = data.get("n", 1)  # 数量 默认为1
        self.endTime = data.get("et", 0)  # 过期时间

    # 登录初始化下发数据
    def to_init_data(self, iNum=None):
        init_data = {}
        init_data["id"] = self.id
        init_data["resID"] = self.resID
        if iNum is None:
            init_data["n"] = self.iNum
        else:
            init_data["n"] = iNum
        init_data["et"] = self.endTime
        return init_data

    def getNum(self):
        return self.iNum

    def setNum(self, num):
        self.iNum = num
        self.markDirty()

    def init_endTime(self, res):
        # res.timeType = 0 #限时类型 1=指定某年某月某时某分结束 2=从生成时刻开始倒计时
        # res.timeArg = '' #限时参数 1类型=2016-11-30 13:54:05 2类型=秒数
        self.endTime = 0
        if res.timeType == constant.ITEM_TIME_TYPE1:
            # 转换成时间数组
            timeArray = time.strptime(res.timeArg, "%Y-%m-%d %H:%M:%S")
            # 转换成时间戳
            self.endTime = time.mktime(timeArray)
        elif res.timeType == constant.ITEM_TIME_TYPE2:
            self.endTime = int(time.time()) + int(res.timeArg)
        self.markDirty()

    def Use(self, *args):
        pass

#货币道具
class CurrencyItem(ItemBase):
    def __init__(self, res, data=None, owner=None):
        ItemBase.__init__(self, res, data=data, owner=owner)

#普通道具
class NomalItem(ItemBase):
    def __init__(self, res, data=None, owner=None):
        ItemBase.__init__(self, res, data=data, owner=owner)

#宠物激活卡
class PetItem(ItemBase):
    def __init__(self, res, data=None, owner=None):
        ItemBase.__init__(self, res, data=data, owner=owner)

#宝箱
class BoxItem(ItemBase):
    def __init__(self, res, data=None, owner=None):
        ItemBase.__init__(self, res, data=data, owner=owner)

    def getReward(self):
        resp = {}
        itemRes = Game.res_mgr.res_item.get(self.resID)
        if not itemRes:
            return resp
        rewardRes = Game.res_mgr.res_reward.get(itemRes.rewardId)
        if not rewardRes:
            return resp
        resp = rewardRes.doReward()
        return resp

    def Use(self, xnum):
        reward = {}
        cnum = 0
        for i in range(xnum):
            rs = self.getReward()
            if not rs:
                continue
            cnum += 1
            for k, v in rs.items():
                reward[k] = reward.get(k, 0) + v
        if not cnum:
            return
        respBag = self.ownerMode.owner.bag.costItem({self.resID:cnum}, constant.ITEM_COST_OPEN_BOX, wLog=True)
        if not respBag.get("rs", 0):
            return
        respBag1 = self.ownerMode.owner.bag.add(reward, constant.ITEM_ADD_OPEN_BOX, wLog=True, mail=True)
        respBag = self.ownerMode.owner.mergeRespBag(respBag, respBag1)
        # 打包返回信息
        dUpdate = self.ownerMode.owner.packRespBag(respBag)
        resp = {
            "allUpdate": dUpdate,
        }
        spawn(self.ownerMode.owner.call, "itemUse", resp, noresult=True)


#可选宝箱
class SelectBoxItem(ItemBase):
    def __init__(self, res, data=None, owner=None):
        ItemBase.__init__(self, res, data=data, owner=owner)

    def getSelect(self, select):
        resp = {}
        itemRes = Game.res_mgr.res_item.get(self.resID)
        if not itemRes:
            return resp
        if select not in itemRes.selectReward:
            return resp
        resp[select] = itemRes.selectReward.get(select, 0)
        return resp

    def Use(self, xnum, select):
        reward={}
        cnum=0
        for i in range(xnum):
            r = self.getSelect(select)
            if not r:
                continue
            cnum+=1
            for k,v in r.items():
                reward[k]=reward.get(k,0)+v

        if not cnum:
            return
        respBag = self.ownerMode.owner.bag.costItem({self.resID:cnum}, constant.ITEM_COST_OPEN_BOX, wLog=True)
        if not respBag.get("rs", 0):
            return

        respBag2 = self.ownerMode.owner.bag.add(reward, constant.ITEM_ADD_OPEN_BOX, wLog=True, mail=True)
        respBag = self.ownerMode.owner.mergeRespBag(respBag, respBag2)

        # 打包返回信息
        dUpdate = self.ownerMode.owner.packRespBag(respBag)
        resp = {
            "allUpdate": dUpdate,
        }
        spawn(self.ownerMode.owner.call, "itemUse", resp, noresult=True)


Map_item_type = {
    constant.ITEM_TYPE_CURRENCY : CurrencyItem, #货币道具 Currency
    constant.ITEM_TYPE_NORMAL : NomalItem, #普通道具 Nomal
    constant.ITEM_TYPE_BOX : BoxItem, #宝箱道具 Box
    constant.ITEM_TYPE_SELECT_BOX : SelectBoxItem, #可选宝箱 SelectBoxItem
    constant.ITEM_TYPE_PET : PetItem, #宠物激活卡
}

def CreatItem(itemNo, data=None, owner=None):
    res = Game.res_mgr.res_item.get(itemNo)
    if not res:
        return None, None
    itemCls = Map_item_type.get(res.type)
    if not itemCls:
        return None, None
    itemobj = itemCls(res, data=data, owner=owner)
    return res, itemobj