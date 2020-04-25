#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import time
from collections import UserDict

from game.common import utility
from game.define import constant

from corelib.frame import Game
from game.core.item import CreatItem
from game.core.equip import CreatEquip
from game.core.bagContainer import YiShouEquipBag, PetEquipBag, ItemBag


class PlayerBag(utility.DirtyFlag):
    def __init__(self, owner):
        utility.DirtyFlag.__init__(self)
        self.owner = owner #拥有者

        self.item_bag = ItemBag(self, 9999999, "item_bag")
        self.equip_bag = PetEquipBag(self, constant.EQUIP_BAG_SIZE, "equip_bag")
        self.yishou_bag = YiShouEquipBag(self, constant.YI_SHOU_BAG_SIZE, "yishou_bag")

        self.id_items = {} #{资源id：[obj]}

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
            self.save_cache["item_bag"] = self.item_bag.to_save_dict(forced=forced)
            self.save_cache["equip_bag"] = self.equip_bag.to_save_dict(forced=forced)
            self.save_cache["yishou_bag"] = self.yishou_bag.to_save_dict(forced=forced)
        return self.save_cache

    #读库数据初始化
    def load_from_dict(self, data):
        item_bag = data.get("item_bag", {})
        self.item_bag.load_from_dict(item_bag)

        equip_bag = data.get("equip_bag", {})
        self.equip_bag.load_from_dict(equip_bag)

        yishou_bag = data.get("yishou_bag", {})
        self.yishou_bag.load_from_dict(yishou_bag)


    #登录初始化下发数据
    def to_init_data(self):
        init_data = {}
        init_data["item_bag"] = self.item_bag.to_init_data()
        init_data["equip_bag"] = self.equip_bag.to_init_data()
        init_data["yishou_bag"] = self.yishou_bag.to_init_data()
        return init_data


    def add(self, dAdd, reason, wLog=False, mail=False):
        sLog = ""
        types = dict(exp=0, wallet={}, pets={}, item={}, equip={}, yishou={})
        for resID, num in dAdd.items():
            if type(resID) != int:
                continue
            if resID == constant.CURRENCY_EXP: #经验
                types["exp"] = types["exp"] + num
            elif resID <= constant.CURRENCY_MAX_NO:  # 货币
                types["wallet"][resID] = types["wallet"].get(resID, 0) + num
            elif resID <= constant.PET_MAX_NO:  # 宠物
                types["pets"][resID] = types["pets"].get(resID, 0) + num
            elif resID <= constant.ITEM_MAX_NO: #道具
                types["item"][resID] = types["item"].get(resID, 0) + num
            elif resID <= constant.EQUIP_START_NO: #装备
                types["equip"][resID] = types["equip"].get(resID, 0) + num
            elif constant.YISHOU_EQUIP_START_NO <= resID <= constant.YISHOU_EQUIP_END_NO: #异兽装备
                types["yishou"][resID] = types["yishou"].get(resID, 0) + num

        #经验
        if types["exp"]:
            self.owner.base.SetExp(self.owner.base.GetExp() + types["exp"])
        #货币
        self.owner.wallet.addCurrency(reason, types["wallet"])
        #宠物
        sLog_pets, resp_pets, mail_pets = self.owner.pet.addNewPet(types["pets"], reason, wLog=wLog)
        #道具
        sLog_item, resp_items, mail_items = self.item_bag.addByData(types["item"], reason, wLog=wLog)
        #装备
        sLog_equip, resp_equips, mail_equips = self.equip_bag.addByData(types["equip"], reason, wLog=wLog)
        #异兽装备
        sLog_yishou, resp_yishou, mail_yishou = self.yishou_bag.addByData(types["yishou"], reason, wLog=wLog)

        #日志记录
        if wLog:
            if types["exp"]:
                sLog.join("#exp@%s_%s" % (types["exp"], self.owner.base.GetExp()))
            if types["wallet"]:
                sLog.join("#wallet@%s" % types["wallet"])
            if sLog_pets:
                sLog.join("#pets@%s" % sLog_pets)
            if sLog_item:
                sLog.join("#items@%s" % sLog_item)
            if sLog_equip:
                sLog.join("#equip@%s" % sLog_equip)
            if sLog_yishou:
                sLog.join("#yishou@%s" % sLog_yishou)
            Game.glog.log2File("bag_add", "%s|%s|%s" % (self.owner.id, reason, sLog))

        # 邮件发送
        send_mails = {}
        for k, v in mail_pets.items():
            send_mails[k] = send_mails.get(k, 0) + v
        for k, v in mail_items.items():
            send_mails[k] = send_mails.get(k, 0) + v
        for k, v in mail_equips.items():
            send_mails[k] = send_mails.get(k, 0) + v
        for k, v in mail_yishou.items():
            send_mails[k] = send_mails.get(k, 0) + v
        if send_mails and mail:
            mailRes = Game.res_mgr.res_mail.get(constant.MAIL_ID_BAG_FULL, None)
            Game.rpc_mail_mgr.sendPersonMail(self.owner.id, mailRes.title, mailRes.content, send_mails)

        #打包返回
        resp = {}
        if types["exp"]:
            resp["exp"] = self.owner.base.GetExp()
        if types["wallet"]:
            resp["wallet"] = list(types["wallet"].keys())
        if resp_pets:
            resp["pets"] = resp_pets
        if resp_items:
            resp["items"] = resp_items
        if resp_equips:
            resp["equips"] = resp_equips
        if resp_yishou:
            resp["yishou"] = resp_yishou
        return resp


    def canCostItem(self, dCost):
        types = dict(wallet={}, item={})

        for resID, num in dCost.items():
            if type(resID) != int:
                continue
            if resID <= constant.CURRENCY_MAX_NO:  # 货币
                types["wallet"][resID] = types["wallet"].get(resID, 0) + num
            elif resID <= constant.ITEM_MAX_NO:  # 道具
                types["item"][resID] = types["item"].get(resID, 0) + num

        not_enough = {}

        cost_wallet = {}  # {id:消耗数量}
        for resID, num in types["wallet"].items():
            if num <= 0:
                continue
            iCurrencyNum = self.owner.wallet.getCurrencyNum(resID)
            if iCurrencyNum >= num:
                cost_wallet[resID] = num
            else:
                not_enough[resID] = num - iCurrencyNum

        cost_items = {}  # {id:消耗数量}
        for resID, num in types["item"].items():
            if num <= 0:
                continue
            iHave = self.item_bag.getNumByResID(resID)
            if iHave >= num:
                cost_items[resID] = num
            else:
                not_enough[resID] = num - iHave

        resp = {}
        if not_enough:
            resp["rs"] = 0
        else:
            resp["rs"] = 1

        resp["not_enough"] = not_enough
        resp["cost_wallet"] = cost_wallet
        resp["cost_items"] = cost_items
        return resp


    def costItem(self, dCost, reason, force=False, wLog=False, auto=0):
        resp = self._costItem(dCost, reason, force, wLog)
        if not resp.get("rs", 0) and auto:
            autoCost = {}
            for buyNo, num in resp.get("not_enough", {}).items():
                quickRes = Game.res_mgr.res_shopQuick.get(buyNo)
                if not quickRes:
                    return resp
                shopRes = Game.res_mgr.res_shop.get(quickRes.shopId)
                if not shopRes:
                    return resp
                # 快速购买的商品数量固定为1，方便补足
                if shopRes.costId in autoCost:
                    autoCost[shopRes.costId] += shopRes.costValue * num
                else:
                    autoCost[shopRes.costId] = shopRes.costValue * num
            # 不用去商城购买，直接判断补足
            resp1 = self._costItem(autoCost, reason, wLog=True)
            # 不够钱补足,提示不够
            if not resp1.get("rs", 0):
                return resp
            resp = self.owner.mergeRespBag(resp, resp1)
            # 如果够，强制扣除有的部分材料
            resp2 = self._costItem(dCost, reason, force=True, wLog=True)
            resp = self.owner.mergeRespBag(resp, resp2)
            resp["rs"] = 1
        return resp


    def _costItem(self, dCost, reason, force=False, wLog=False):
        canCost = self.canCostItem(dCost)
        rs = canCost.get("rs", 0)
        not_enough = canCost.get("not_enough", {})
        cost_wallet = canCost.get("cost_wallet", {})
        cost_items = canCost.get("cost_items", {})
        if not rs and not force:
            resp = {}
            resp["rs"] = rs
            resp["not_enough"] = not_enough
            resp["wallet"] = []
            resp["items"] = []
            return resp

        #开始扣除
        #货币
        self.owner.wallet.costCurrency(reason, cost_wallet)
        #道具
        _, sLog_item, resp_items = self.item_bag.costByData(cost_items, reason, wLog=True)
        #记录消耗日志
        if wLog:
            sLog = ""
            sLog.join("#wallet@%s" % cost_wallet)
            sLog.join("#items@%s" % sLog_item)
            Game.glog.log2File("bag_cost", "%s|%s|%s" % (self.owner.id, reason, sLog))

        #致脏
        self.markDirty()
        resp = {}
        resp["rs"] = rs
        resp["not_enough"] = not_enough
        resp["wallet"] = list(cost_wallet.keys())
        resp["items"] = resp_items
        return resp



    # reason参考 constant的物品增加原因
    # wLog重要的行为才记录
    def costItemByTranceNo(self, uid, reason, wLog=False):
        obj = self.item_bag.getObj(uid)
        if not obj:
            return 0, None
        old = obj.getNum()
        dele = 1
        new = old - dele
        if new <= 0:
            new = 0
        obj.setNum(new)

        # 日志
        sLog = ""
        if wLog:
            sLog.join("#items@%s_%s_%s_%s" % (old, dele, new, obj.to_save_dict()))
            Game.glog.log2File("bag_cost", "%s|%s|%s" % (self.owner.id, reason, sLog))

        # 清理需要删除的物品
        if new <= 0:
            self.item_bag.resID_obj.pop(obj.resID, None)
            self.item_bag.objs.pop(obj.id, None)

        self.markDirty()
        return 1, obj




