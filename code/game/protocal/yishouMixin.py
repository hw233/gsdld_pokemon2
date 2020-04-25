#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import random

from game.define import errcode, constant, msg_define
from game import Game

from corelib import log
from game.common import utility


class YishouMixin(object):
    if 0:
        from game.core import player as player_md
        player = player_md.Player()

    # 宠物装备穿戴(petEquipWear)
    # 请求
    #     宠物id(id, int)
    #     装备uid(uid, int)
    # 返回
    #     主动推送刷新(allUpdate, json)
    #         游戏模型 - 宠物模块（只刷当前操作的）
    def rc_petEquipWear(self, id, uid):
        # 宠物未激活
        if id not in self.player.pet.all_pets:
            return 0, errcode.EC_PET_NOT_ACT
        wearEquip = self.player.pet.yishou_bag.getObj(uid)
        if not wearEquip:
            return 0, errcode.EC_PET_EQUIP_NOT_FIND

        pet = self.player.pet.getPet(id)
        equipRes = Game.res_mgr.res_petEquip.get(wearEquip.id)
        if not equipRes:
            return 0, errcode.EC_NORES

        # 穿戴等级
        if pet.GetLv() < equipRes.needLv:
            return 0, errcode.EC_PET_EQUIP_LV_LIMIT

        wearEquip = self.player.pet.yishou_bag.popObj(uid)
        pos = equipRes.pos
        # 已穿戴，需要替换
        takeoffEquipList = []
        if pet.equips.get(pos):
            takeoffEquipList.append(pet.popEquip(pos))
            self.player.pet.yishou_bag.doAdd(takeoffEquipList, constant.ITEM_ADD_PET_EQUIP_TAKE_OFF)
        pet.wearEquip(pos, wearEquip, id)
        # 重算宠物装备属性
        pet.RecalEquipAttr()
        # 重算战力
        self.player.attr.RecalFightAbility()

        # 打包返回信息
        dRole = {}
        dRole["roleBase"] = {"fa": self.player.base.fa}

        dPet = {}
        dPet["actList"] = [pet.to_init_data()]
        dPet.update(self.player.pet.to_update_data(equips=takeoffEquipList, delequips=[wearEquip]))

        dUpdate = {}
        dUpdate["pet"] = dPet
        dUpdate["role"] = dRole
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp

    # 宠物装备卸下(petEquipTakeOff)
    # 请求
    #     宠物id(id, int)
    #     装备uid(uid, int)
    # 返回
    #     主动推送刷新(allUpdate, json)
    #         游戏模型 - 宠物模块（只刷当前操作的）
    def rc_petEquipTakeOff(self, id, uid):
        # 宠物未激活
        if id not in self.player.pet.all_pets:
            return 0, errcode.EC_PET_NOT_ACT
        pet = self.player.pet.getPet(id)

        wearEquip = pet.getEquipByUid(uid)
        if not wearEquip:
            return 0, errcode.EC_PET_EQUIP_NOT_FIND

        equipRes = Game.res_mgr.res_petEquip.get(wearEquip.id)
        if not equipRes:
            return 0, errcode.EC_NORES

        pos = equipRes.pos
        takeoffEquipList = [wearEquip]
        rs = self.player.pet.yishou_bag.doAdd(takeoffEquipList, constant.ITEM_ADD_PET_EQUIP_TAKE_OFF)
        if not rs:
            return 0, errcode.EC_PET_EQUIP_BAG_SIZE_LIMIT

        pet.popEquip(pos)

        # 重算宠物装备属性
        pet.RecalEquipAttr()
        # 重算战力
        self.player.attr.RecalFightAbility()

        # 打包返回信息
        dRole = {}
        dRole["roleBase"] = {"fa": self.player.base.fa}

        dPet = {}
        dPet["actList"] = [pet.to_init_data()]
        dPet.update(self.player.pet.to_update_data(equips=takeoffEquipList))

        dUpdate = {}
        dUpdate["pet"] = dPet
        dUpdate["role"] = dRole
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp

    # 宠物装备强化(petEquipUpgrade)
    # 请求
    #     宠物id(id, int) #强化背包装备时传0
    #     装备uid(uid, int)
    # 返回
    #     主动推送刷新(allUpdate, json)
    #         游戏模型 - 宠物模块（只刷当前操作的）
    def rc_petEquipUpgrade(self, id, uid):
        pet = self.player.pet.getPet(id)
        if pet:
            equip = pet.getEquipByUid(uid)
        else:
            equip = self.player.pet.yishou_bag.getObj(uid)
        if not equip:
            return 0, errcode.EC_PET_EQUIP_NOT_FIND

        equipRes = Game.res_mgr.res_petEquip.get(equip.id)
        if not equipRes:
            return 0, errcode.EC_NORES

        nextUpRes = Game.res_mgr.res_qalv_petEquipUpgrade.get((equipRes.quality, equip.addlv))
        if not nextUpRes:
            return 0, errcode.EC_NORES

        # 扣道具
        respBag = self.player.bag.costItem(nextUpRes.cost, constant.ITEM_COST_PET_EQUIP_UPGRADE, wLog=True)
        if not respBag.get("rs", 0):
            return 0, errcode.EC_PET_EQUIP_UPGRADE_NOT_ENOUGH

        equip.Upgrade()

        if pet:
            # 重算宠物装备属性
            pet.RecalEquipAttr()
            # 重算战力
            self.player.attr.RecalFightAbility()

        # 打包返回信息
        dRole = {}
        dRole["roleBase"] = {"fa": self.player.base.fa}

        dPet = {}
        if pet:
            dPet["actList"] = [pet.to_init_data()]
        else:
            dPet.update(self.player.pet.to_update_data(equips=[equip]))

        dUpdate = self.player.packRespBag(respBag)
        dUpdate["pet"] = dPet
        dUpdate["role"] = dRole
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp

    # 宠物装备共鸣替换(petEquipGongmingTihuan)
    # 请求
    #     宠物id(id, int) #强化背包装备时传0
    #     装备uid(uid, int)
    #     格子index 0 1 2(idx, int)
    # 返回
    #     主动推送刷新(allUpdate, json)
    #         游戏模型 - 宠物模块（只刷当前操作的）
    def rc_petEquipGongmingTihuan(self, id, uid, idx):

        if idx not in [0, 1, 2]:
            return 0, errcode.EC_NORES

        # print("!!!!!!!!!!!!!!!!!",id, uid, idx)

        pet = self.player.pet.getPet(id)
        if pet:
            equip = pet.getEquipByUid(uid)
        else:
            equip = self.player.pet.yishou_bag.getObj(uid)
        if not equip:
            return 0, errcode.EC_PET_EQUIP_NOT_FIND

        equip.usegongming(idx)

        dRole = {}
        if pet:
            # 重算宠物装备属性
            pet.RecalEquipAttr()
            # 重算战力
            self.player.attr.RecalFightAbility()
            dRole["roleBase"] = {"fa": self.player.base.fa}

        dPet = {}
        if pet:
            dPet["actList"] = [pet.to_init_data()]
        else:
            dPet.update(self.player.pet.to_update_data(equips=[equip]))
            # print("======",dPet)

        dUpdate = {}
        dUpdate["pet"] = dPet
        dUpdate["role"] = dRole
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp

    # 宠物装备共鸣(petEquipGongming)
    # 请求
    #     宠物id(id, int) #强化背包装备时传0
    #     装备uid(uid, int)
    #     绑定宠物id(bindpet, int) #绑定的宠物id,不绑定传0
    #     被吃掉的装备uid(eatuid, int)
    #     格子index 0 1 2(idx, int)
    # 返回
    #     主动推送刷新(allUpdate, json)
    #         游戏模型 - 宠物模块（只刷当前操作的）
    def rc_petEquipGongming(self, id, uid, bindpet, eatuid, idx):

        # print("!!!!!!!!!!!!!!!!!",id, uid, bindpet, eatuid, idx)
        if idx not in [0, 1, 2]:
            return 0, errcode.EC_PET_EQUIP_GONGMING_BAD_IDX

        pet = self.player.pet.getPet(id)
        if pet:
            equip = pet.getEquipByUid(uid)
        else:
            equip = self.player.pet.yishou_bag.getObj(uid)
        if not equip:
            # print("!!!!!!!!!!!!!!!!!33333")
            return 0, errcode.EC_PET_EQUIP_NOT_FIND

        if bindpet:
            bpet = self.player.pet.getPet(bindpet)
            if not bpet:
                return 0, errcode.EC_PET_EQUIP_GONGMING_NOFOUND_BIND_PET

        eatequip = self.player.pet.yishou_bag.getObj(eatuid)
        if not eatequip:
            return 0, errcode.EC_PET_EQUIP_GONGMING_NOFOUND_EAT

        eatequipRes = Game.res_mgr.res_petEquip.get(eatequip.id)
        if not eatequipRes:
            return 0, errcode.EC_NORES

        equipRes = Game.res_mgr.res_petEquip.get(equip.id)
        if not equipRes:
            return 0, errcode.EC_NORES

        if eatequipRes.quality != equipRes.quality:
            return 0, errcode.EC_PET_EQUIP_GONGMING_TYPE_NOTSAME

        oriType = 0
        if bindpet:
            evolveRes = Game.res_mgr.res_idlv_petevolve.get((bpet.id, bpet.evolveLv))
            if not evolveRes:
                # print("!!!!!!!!!!!!!!!!!===")
                return 0, errcode.EC_NORES
            oriType = evolveRes.oriType
            if oriType == 2:
                oriType = 1

        # 扣道具
        equipCost = self.player.pet.yishou_bag.popObj(eatuid)
        if not equipCost:
            return 0, errcode.EC_PET_EQUIP_GONGMING_EAT_FAIL

        choose = []
        for kk, vv in Game.res_mgr.res_shoulinggongming.items():
            if vv.oriType == oriType and idx == vv.idx:
                choose.append((kk, vv.weight,))

        cid = utility.Choice(choose)

        equip.gongming(idx, cid, bindpet)

        dPet = {}
        if pet:
            dPet["actList"] = [pet.to_init_data()]
            dPet.update(self.player.pet.to_update_data(delequips=[equipCost]))
        else:
            dPet.update(self.player.pet.to_update_data(equips=[equip], delequips=[equipCost]))

        # print("eeeeeeeeeeeee",dPet)

        dUpdate = {}
        dUpdate["pet"] = dPet
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp

    # 宠物装备强化-定向(petEquipUpgradeDir)
    # 请求
    #     装备uid(uid, int)
    #     道具id(itemid, int)
    # 返回
    #     主动推送刷新(allUpdate, json)
    #         游戏模型 - 宠物模块（只刷当前操作的）
    def rc_petEquipUpgradeDir(self, id, uid, itemid):
        pet = self.player.pet.getPet(id)
        if pet:
            equip = pet.getEquipByUid(uid)
        else:
            equip = self.player.pet.yishou_bag.getObj(uid)
        if not equip:
            return 0, errcode.EC_PET_EQUIP_NOT_FIND

        itemres = Game.res_mgr.res_item.get(itemid)
        if not itemres:
            return 0, errcode.EC_NORES

        if itemres.type != 2:
            return 0, errcode.EC_NORES

        if itemres.subType != 16:
            return 0, errcode.EC_NORES

        equipRes = Game.res_mgr.res_petEquip.get(equip.id)
        if not equipRes:
            return 0, errcode.EC_NORES

        ysDirCardUpLv = Game.res_mgr.res_common.get("ysDirCardUpLv")
        if not ysDirCardUpLv:
            return 0, errcode.EC_NORES
        ysDirCardUseNum = Game.res_mgr.res_common.get("ysDirCardUseNum")
        if not ysDirCardUseNum:
            return 0, errcode.EC_NORES

        nextlv = 0
        for v in reversed(ysDirCardUpLv.arrayint1):
            if equip.addlv < v:
                nextlv = v

        if not nextlv:
            return 0, errcode.EC_NORES

        upnum = nextlv - equip.addlv

        cost = {itemid: ysDirCardUseNum.arrayint1[equip.dicnum]}
        respBag = self.player.bag.costItem(cost, constant.ITEM_COST_PET_EQUIP_UPGRADE, wLog=True)
        if not respBag.get("rs", 0):
            return 0, errcode.EC_PET_EQUIP_UPGRADE_NOT_ENOUGH

        addvice = False
        for upx in range(upnum):

            nextUpRes = Game.res_mgr.res_qalv_petEquipUpgrade.get((equipRes.quality, equip.addlv))
            if not nextUpRes:
                return 0, errcode.EC_NORES

            # 扣道具
            respBag1 = self.player.bag.costItem(nextUpRes.cost, constant.ITEM_COST_PET_EQUIP_UPGRADE, wLog=True)
            if not respBag.get("rs", 0):
                return 0, errcode.EC_PET_EQUIP_UPGRADE_NOT_ENOUGH

            respBag = self.player.mergeRespBag(respBag, respBag1)

            if upx == upnum - 1:
                addvice = True

            equip.UpgradeDir(itemres.arg1, addvice)

        equip.dicnum += 1
        equip.markDirty()

        if pet:
            # 重算宠物装备属性
            pet.RecalEquipAttr()
            # 重算战力
            self.player.attr.RecalFightAbility()

        # 打包返回信息
        dRole = {}
        dRole["roleBase"] = {"fa": self.player.base.fa}

        dPet = {}
        if pet:
            dPet["actList"] = [pet.to_init_data()]
        else:
            dPet.update(self.player.pet.to_update_data(equips=[equip]))

        dUpdate = self.player.packRespBag(respBag)
        dUpdate["pet"] = dPet
        dUpdate["role"] = dRole
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp

    # 宠物装备回收(petEquipRecycl)
    # 请求
    #     装备uid列表(uidList, int)
    # 返回
    #     主动推送刷新(allUpdate, json)
    #         游戏模型 - 宠物模块（只刷当前操作的）
    def rc_petEquipRecycl(self, uidList):
        delequips = []
        reward = {}
        for uid in uidList:
            equip = self.player.pet.yishou_bag.popObj(uid)
            if not equip:
                continue
            equipRes = Game.res_mgr.res_petEquip.get(equip.id)
            if not equipRes:
                continue
            upRes = Game.res_mgr.res_qalv_petEquipUpgrade.get((equipRes.quality, equip.addlv))
            if not upRes:
                continue
            for id, num in upRes.recycl.items():
                if id in reward:
                    reward[id] += num
                else:
                    reward[id] = num

            delequips.append(equip)

        respBag = self.player.bag.add(reward, constant.ITEM_ADD_PET_EQUIP_RECYCL, wLog=True)

        # 打包返回信息
        dUpdate = self.player.packRespBag(respBag)
        dPet = dUpdate.setdefault("pet", {})
        dPet.update(self.player.pet.to_update_data(delequips=delequips))
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp

    # 宠物装备上锁(petEquipLock)
    # 请求
    #     宠物id(id, int) #背包装备时传0
    #     装备uid(uid, int)
    # 返回
    #     主动推送刷新(allUpdate, json)
    #         游戏模型 - 宠物模块（只刷当前操作的）
    def rc_petEquipLock(self, id, uid):
        pet = self.player.pet.getPet(id)
        if pet:
            equip = pet.getEquipByUid(uid)
        else:
            equip = self.player.pet.yishou_bag.getObj(uid)
        if not equip:
            return 0, errcode.EC_PET_EQUIP_NOT_FIND

        equip.Lock()

        # 打包返回信息
        dPet = {}
        if pet:
            dPet["actList"] = [pet.to_init_data()]
        else:
            dPet.update(self.player.pet.to_update_data(equips=[equip]))

        dUpdate = {}
        dUpdate["pet"] = dPet
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp

    # 宠物装备解锁(petEquipUnLock)
    # 请求
    #     宠物id(id, int) #背包装备时传0
    #     装备uid(uid, int)
    # 返回
    #     主动推送刷新(allUpdate, json)
    #         游戏模型 - 宠物模块（只刷当前操作的）
    def rc_petEquipUnLock(self, id, uid):
        pet = self.player.pet.getPet(id)
        if pet:
            equip = pet.getEquipByUid(uid)
        else:
            equip = self.player.pet.yishou_bag.getObj(uid)
        if not equip:
            return 0, errcode.EC_PET_EQUIP_NOT_FIND

        equip.UnLock()

        # 打包返回信息
        dPet = {}
        if pet:
            dPet["actList"] = [pet.to_init_data()]
        else:
            dPet.update(self.player.pet.to_update_data(equips=[equip]))

        dUpdate = {}
        dUpdate["pet"] = dPet
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp

    # 宠物装备弃置(petEquipSetWaste)
    # 请求
    #     宠物id(id, int) #背包装备时传0
    #     装备uid(uid, int)
    # 返回
    #     主动推送刷新(allUpdate, json)
    #         游戏模型 - 宠物模块（只刷当前操作的）
    def rc_petEquipSetWaste(self, id, uid):
        pet = self.player.pet.getPet(id)
        if pet:
            equip = pet.getEquipByUid(uid)
        else:
            equip = self.player.pet.yishou_bag.getObj(uid)
        if not equip:
            return 0, errcode.EC_PET_EQUIP_NOT_FIND

        equip.setWaste()

        # 打包返回信息
        dPet = {}
        if pet:
            dPet["actList"] = [pet.to_init_data()]
        else:
            dPet.update(self.player.pet.to_update_data(equips=[equip]))

        dUpdate = {}
        dUpdate["pet"] = dPet
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp

    # 宠物装备不弃置(petEquipUnSetWaste)
    # 请求
    #     宠物id(id, int) #背包装备时传0
    #     装备uid(uid, int)
    # 返回
    #     主动推送刷新(allUpdate, json)
    #         游戏模型 - 宠物模块（只刷当前操作的）
    def rc_petEquipUnSetWaste(self, id, uid):
        pet = self.player.pet.getPet(id)
        if pet:
            equip = pet.getEquipByUid(uid)
        else:
            equip = self.player.pet.yishou_bag.getObj(uid)
        if not equip:
            return 0, errcode.EC_PET_EQUIP_NOT_FIND

        equip.UnSetWaste()

        # 打包返回信息
        dPet = {}
        if pet:
            dPet["actList"] = [pet.to_init_data()]
        else:
            dPet.update(self.player.pet.to_update_data(equips=[equip]))

        dUpdate = {}
        dUpdate["pet"] = dPet
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp

    # 宠物装备背包扩容(petEquipBagSizeBuy)
    # 请求
    #     扩容次数(count, int)
    # 返回
    #     主动推送刷新(allUpdate, json)
    #         游戏模型 - 宠物模块（只刷当前操作的）
    def rc_petEquipBagSizeBuy(self, count):
        yishouBagBuyAddSizeRes = Game.res_mgr.res_common.get("yishouzhilingBuyBagSizeSpacing")
        if not yishouBagBuyAddSizeRes:
            return 0, errcode.EC_NORES

        yishouBagBuyMaxCountRes = Game.res_mgr.res_common.get("yishouBagBuyMaxCount")
        if not yishouBagBuyMaxCountRes:
            return 0, errcode.EC_NORES

        yishouBagBuyCostRes = Game.res_mgr.res_common.get("yishouzhilingBuyBagSizeCost")
        if not yishouBagBuyCostRes:
            return 0, errcode.EC_NORES

        if count + self.player.pet.yishou_bag.buy_count > yishouBagBuyMaxCountRes.i:
            return 0, errcode.EC_PET_EQUIP_ADD_BAG_SIZE_MAX

        total = 0
        curCount = self.player.pet.yishou_bag.buy_count
        for i in range(count):
            curCount += 1
            for one in yishouBagBuyCostRes.arrayint2:
                start, end, price = one
                if start <= curCount <= end:
                    total += price

        # 扣道具
        cost = {constant.CURRENCY_GOLD: total}
        respBag = self.player.bag.costItem(cost, constant.ITEM_COST_YISHOU_BAG_SIZE_ADD, wLog=True)
        if not respBag.get("rs", 0):
            return 0, errcode.EC_PET_EQUIP_ADD_BAG_SIZE

        self.player.pet.yishou_bag.addSize(yishouBagBuyAddSizeRes.i * count)
        self.player.pet.yishou_bag.addBuyCount(count)

        # 打包返回信息
        dUpdate = self.player.packRespBag(respBag)
        dPet = dUpdate.setdefault("pet", {})
        dPet["yishou_bag"]["size"] = self.player.pet.yishou_bag.size
        dPet["yishou_bag"]["buyCount"] = self.player.pet.yishou_bag.buy_count

        dUpdate["pet"] = dPet
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp




