#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import random

from game.define import errcode, constant, msg_define
from game import Game

from corelib import log
from game.common import utility

class PetMixin(object):
    if 0:
        from game.core import player as player_md
        player = player_md.Player()

    # 宠物升级(petUpGrade)
    # 请求
    #     宠物唯一id(uid, str)
    # 返回
    #     主动推送刷新(allUpdate, json)
    #         游戏模型 - 宠物模块（只刷当前操作的）
    #         游戏模型 - 角色背包 - 道具列表
    #         游戏模型 - 角色基础 - 战力
    def rc_petUpGrade(self, uid):
        # 宠物未激活
        pet = self.player.pet.getPet(uid)
        if not pet:
            return 0, errcode.EC_PET_NOT_ACT
        res = Game.res_mgr.res_pet.get(pet.resID)
        if not res:
            return 0, errcode.EC_NORES
        #等级上限限制
        evolveRes = Game.res_mgr.res_idlv_petevolve.get((pet.resID, pet.evolveLv))
        if not evolveRes:
            return 0, errcode.EC_NORES
        iCurLv = pet.GetLv()
        if iCurLv >= evolveRes.lvLimit:
            return 0, errcode.EC_MAX_LEVEL
        #当前等级资源
        curRes = Game.res_mgr.res_qalv_petlv.get((res.quality, iCurLv))
        if not curRes:
            return 0, errcode.EC_NORES
        # 如果没有下一阶
        iNextLv = iCurLv + 1
        nextRes = Game.res_mgr.res_qalv_petlv.get((res.quality, iNextLv))
        if not nextRes:
            return 0, errcode.EC_MAX_LEVEL
        # 扣道具
        respBag = self.player.bag.costItem(curRes.cost, constant.ITEM_COST_PET_UPGRADE, wLog=True)
        if not respBag.get("rs", 0):
            return 0, errcode.EC_PET_UPGRADE_NOT_ENOUGH
        #设置等级
        pet.SetLv(iNextLv)
        #重算宠物属性
        pet.attr.recalAttr([constant.PET_ATTR_MODULE_LV_EVOLVE, constant.PET_ATTR_MODULE_SKILL])
        # 重算战力
        self.player.attr.RecalFightAbility()
        # 抛事件
        self.player.safe_pub(msg_define.MSG_PET_UPGRADE)

        # 打包返回信息
        dUpdate = self.player.packRespBag(respBag)
        dPet = dUpdate.setdefault("pet", {})
        dPet["all_pets"] = [pet.to_init_data()]
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp

    # 宠物进化(petEvolve)
    # 请求
    #     宠物唯一id(uid, str)
    #     消耗宠物列表(costPet, [str])
    # 返回
    #     主动推送刷新(allUpdate, json)
    #         游戏模型 - 宠物模块（只刷当前操作的）
    #         游戏模型 - 角色背包 - 道具列表
    #         游戏模型 - 角色基础 - 战力
    def rc_petEvolve(self, uid, costPet):
        #不能吃自己
        if uid in costPet:
            return 0, errcode.EC_PET_EVOLVE_EAT_SELF
        # 宠物未激活
        pet = self.player.pet.getPet(uid)
        if not pet:
            return 0, errcode.EC_PET_NOT_ACT
        res = Game.res_mgr.res_pet.get(pet.resID)
        if not res:
            return 0, errcode.EC_NORES
        # 等级不足
        iCurEvolveLv = pet.GetEvolveLv()
        curRes = Game.res_mgr.res_idlv_petevolve.get((pet.resID, iCurEvolveLv))
        if not curRes:
            return 0, errcode.EC_NORES
        if curRes.needLv > pet.GetLv():
            return 0, errcode.EC_NOLEVEL
        # 下一阶
        iNextEvolveLv = iCurEvolveLv + 1
        nextRes = Game.res_mgr.res_idlv_petevolve.get((pet.resID, iNextEvolveLv))
        if not nextRes:
            if curRes.changeID:
                iNextEvolveLv = 1
                nextRes = Game.res_mgr.res_idlv_petevolve.get((curRes.changeID, iNextEvolveLv))
            else:
                return 0, errcode.EC_MAX_LEVEL
        #检查是否消耗宠物
        if curRes.costPet1 or curRes.costPet2:
            rs, code = self.player.pet.getCostPet(costPet, curRes.costPet1, curRes.costPet2)
            if not rs:
                if code == 1: #1=没有足够的宠物
                    return 0, errcode.EC_PET_EVOLVE_NOT_ENOUGH
                elif code == 2: #2=宠物身上有装备，有各种物品时不可消耗
                    return 0, errcode.EC_PET_CAN_NOT_COST_WEAR
                elif code == 3: #3=宠物已出战
                    return 0, errcode.EC_PET_CAN_NOT_COST_FIGHT
                else:
                    return 0, errcode.EC_PET_EVOLVE_NOT_ENOUGH
        # 扣道具
        respBag = self.player.bag.costItem(curRes.cost, constant.ITEM_COST_PET_EVOLVE, wLog=True)
        if not respBag.get("rs", 0):
            return 0, errcode.EC_PET_EVOLVE_NOT_ENOUGH
        #扣宠物
        if costPet:
            backAdd = self.player.pet.costPet(constant.ITEM_COST_PET_EVOLVE, costPet, wLog=True)
            #返还材料
            respBag1 = self.player.bag.add(backAdd, constant.ITEM_ADD_PET_EVOLVE_BACK)
            respBag = self.player.mergeRespBag(respBag, respBag1)

        #是否变宠物ID
        if curRes.changeID:
            pet.SetResID(curRes.changeID)
        #设置进化等级
        pet.SetEvolveLv(iNextEvolveLv)
        #增加被动技能
        pet.setPrivate(nextRes.private)
        pet.addPeculiarity(nextRes.peculiarityAdd)
        # 图鉴激活
        if curRes.changeID:
            self.player.pet.actAlbum(pet)

        # 战力重算
        pet.attr.recalAttr([constant.PET_ATTR_MODULE_LV_EVOLVE, constant.PET_ATTR_MODULE_PECULIARITY])
        self.player.attr.RecalFightAbility()
        # 抛事件
        self.player.safe_pub(msg_define.MSG_PET_EVOLVE, uid)

        # 打包返回信息
        dUpdate = self.player.packRespBag(respBag)
        dUpdate["attr"] = self.player.attr.to_update_data()
        dPet = dUpdate.setdefault("pet", {})
        dPet["all_pets"] = [pet.to_init_data()]
        dPet["del_pets"] = costPet
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp

    # 上传布阵(rc_uploadBattleArray)
    # 请求
    #     出战队伍类型(tp, int)
    #     阵位列表(position, [json])  位置(str):  宠物唯一id(str)
    # 返回
    #     出战队伍类型(tp, int)
    #     阵位列表(position, [json])  位置(str):  宠物唯一id(str)
    def rc_uploadBattleArray (self, tp, position):
        #检查宠物互斥
        for one in position:
            petList = list(one.values())
            if not self.player.pet.checkPetMutex(petList):
                return 0, errcode.EC_PET_MUTEX_LIMIT
        #数据转化
        all = []
        for one in position:
            data = {}
            for k, v in one.items():
                data[int(k)] = v
            all.append(data)
        obj = self.player.battle_array.getBattleArray(tp)
        change = obj.setPosition(all)

        # 出战队伍战力
        if tp == constant.BATTLE_ARRAY_TYPE_NORMAL:
            self.player.attr.RecalFightAbility()
        # 打包返回
        dUpdate = {}
        dUpdate["base"] = {"fa": self.player.base.GetFightAbility()}
        dPet = dUpdate.setdefault("pet", {})
        dPet["all_pets"] = [pet.to_init_data() for pet in change]
        resp = {
            "allUpdate": dUpdate,
            "tp": tp,
            "position": position
        }
        return 1, resp


    # 宠物技能洗练(petSkillWash)
    # 请求
    #     宠物唯一id(uid, str)
    #     洗练类型(type, int) 1 = 普通 2 = 高级
    #     是否自动购买(auto, int) 补足当次需要材料 0 = 不自动 1 = 自动
    # 返回
    #     主动推送刷新(allUpdate, json)
    #         游戏模型 - 宠物模块（只刷当前操作的）
    #         游戏模型 - 角色背包 - 道具列表
    #         游戏模型 - 货币
    def rc_petSkillWash(self, uid, type, auto):
        # 宠物未激活
        pet = self.player.pet.getPet(uid)
        if not pet:
            return 0, errcode.EC_PET_NOT_ACT
        res = Game.res_mgr.res_pet.get(pet.resID)
        if not res:
            return 0, errcode.EC_NORES

        washRes = Game.res_mgr.res_idstar_petwash.get((pet.resID, pet.washStar))
        if not washRes:
            return 0, errcode.EC_NORES
        #1 = 普通 2 = 高级
        if type == 1:
            costRes = Game.res_mgr.res_common.get("petNormalWashCost")
            addRes = Game.res_mgr.res_common.get("petNormalWashExp")
        elif type == 2:
            costRes = Game.res_mgr.res_common.get("petAdvWashCost")
            addRes = Game.res_mgr.res_common.get("petAdvWashExp")
        else:
            costRes = None
            addRes = None
        if not costRes or not addRes:
            return 0, errcode.EC_NORES
        lockCostRes = Game.res_mgr.res_common.get("petWashLockCost")
        if not lockCostRes:
            return 0, errcode.EC_NORES
        #获取锁定技能个数，如果全锁定，不能洗练
        iCostGold = 0
        if len(pet.peculiarity):
            iLockNum = pet.GetLockPeculiarityNum()
            if iLockNum >= len(pet.peculiarity):
                return 0, errcode.EC_PET_WASH_ALL_LOCK
            #如果锁定了还要扣元宝
            iCostGold = lockCostRes.arrayint2.get(iLockNum, 0)
        if iCostGold:
            dCost = {constant.CURRENCY_GOLD:iCostGold}
        else:
            dCost = {}
        dCost.update(costRes.arrayint2)
        # 扣道具
        respBag = self.player.bag.costItem(dCost, constant.ITEM_COST_PET_WASH, wLog=True, auto=auto)
        if not respBag.get("rs", 0):
            return 0, errcode.EC_PET_WASH_NOT_ENOUGH
        #洗练技能
        pet.WashPeculiarity()
        #增加洗练次数
        iWashNum = pet.GetWashNum()
        iWashNum += addRes.i
        pet.SetWashNum(iWashNum)
        #升星
        iWashStar = pet.GetWashStar()
        starRes = Game.res_mgr.res_petwashstar.get(iWashStar)
        nextRes = Game.res_mgr.res_petwashstar.get(iWashStar + 1)
        if starRes and nextRes and iWashNum >= starRes.cnt:
            iWashStar += 1
            pet.SetWashStar(iWashStar)

        #抛事件
        self.player.safe_pub(msg_define.MSG_PET_SKILL_WASH)

        # 打包返回信息
        dUpdate = self.player.packRespBag(respBag)
        dPet = dUpdate.setdefault("pet", {})
        dPet["all_pets"] = [pet.to_init_data()]
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp

    # 宠物技能洗练锁定(petSkillWashLock)
    # 请求
    #     宠物唯一id(uid, str)
    #     技能部位(pos, int)
    # 返回
    #     主动推送刷新(allUpdate, json)
    #         游戏模型 - 宠物模块（只刷当前操作的）
    def rc_petSkillWashLock(self, uid, pos):
        # 宠物未激活
        pet = self.player.pet.getPet(uid)
        if not pet:
            return 0, errcode.EC_PET_NOT_ACT
        res = Game.res_mgr.res_pet.get(pet.resID)
        if not res:
            return 0, errcode.EC_NORES
        #宠物初始化有多少技能就固定了,不会扩充
        if not pet.peculiarity.get(pos):
            return 0, errcode.EC_PET_WASH_POS_ERROR
        pet.LockPeculiarity(pos)
        # 打包返回信息
        dUpdate = {}
        dPet = dUpdate.setdefault("pet", {})
        dPet["all_pets"] = [pet.to_init_data()]
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp

    # 宠物技能洗练解锁(petSkillWashUnLock)
    # 请求
    #     宠物唯一id(uid, str)
    #     技能部位(pos, int)
    # 返回
    #     主动推送刷新(allUpdate, json)
    #         游戏模型 - 宠物模块（只刷当前操作的）
    def rc_petSkillWashUnLock(self, uid, pos):
        # 宠物未激活
        pet = self.player.pet.getPet(uid)
        if not pet:
            return 0, errcode.EC_PET_NOT_ACT
        res = Game.res_mgr.res_pet.get(pet.resID)
        if not res:
            return 0, errcode.EC_NORES
        # 宠物初始化有多少技能就固定了,不会扩充
        if not pet.peculiarity.get(pos):
            return 0, errcode.EC_PET_WASH_POS_ERROR
        pet.UnLockPeculiarity(pos)
        # 打包返回信息
        dUpdate = {}
        dPet = dUpdate.setdefault("pet", {})
        dPet["all_pets"] = [pet.to_init_data()]
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp

    # 宠物技能更换(petSkillChange)
    # 请求
    #     宠物唯一id(uid, str)
    # 返回
    #     主动推送刷新(allUpdate, json)
    #         游戏模型 - 宠物模块（只刷当前操作的）
    def rc_petSkillChange(self, uid):
        # 宠物未激活
        pet = self.player.pet.getPet(uid)
        if not pet:
            return 0, errcode.EC_PET_NOT_ACT
        res = Game.res_mgr.res_pet.get(pet.resID)
        if not res:
            return 0, errcode.EC_NORES

        #宠物技能更换
        pet.PeculiarityChange()
        #重算宠物属性
        pet.attr.recalAttr([constant.PET_ATTR_MODULE_PECULIARITY])
        self.player.attr.RecalFightAbility()
        # 打包返回信息
        dUpdate = {}
        dUpdate["base"] = {"fa": self.player.base.GetFightAbility()}
        dPet = dUpdate.setdefault("pet", {})
        dPet["all_pets"] = [pet.to_init_data()]
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp


    # 宠物锁定(petLock)
    # 请求
    #     宠物唯一id(uid, str)
    # 返回
    #     主动推送刷新(allUpdate, json)
    #         游戏模型 - 宠物模块（只刷当前操作的）
    def rc_petLock(self, uid):
        # 宠物未激活
        pet = self.player.pet.getPet(uid)
        if not pet:
            return 0, errcode.EC_PET_NOT_ACT
        res = Game.res_mgr.res_pet.get(pet.resID)
        if not res:
            return 0, errcode.EC_NORES
        pet.SetLock(1)
        # 打包返回信息
        dUpdate = {}
        dPet = dUpdate.setdefault("pet", {})
        dPet["all_pets"] = [pet.to_init_data()]
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp


    # 宠物解锁(petUnLock)
    # 请求
    #     宠物唯一id(uid, str)
    # 返回
    #     主动推送刷新(allUpdate, json)
    #         游戏模型 - 宠物模块（只刷当前操作的）
    def rc_petUnLock(self, uid):
        # 宠物未激活
        pet = self.player.pet.getPet(uid)
        if not pet:
            return 0, errcode.EC_PET_NOT_ACT
        res = Game.res_mgr.res_pet.get(pet.resID)
        if not res:
            return 0, errcode.EC_NORES
        pet.SetLock(0)
        # 打包返回信息
        dUpdate = {}
        dPet = dUpdate.setdefault("pet", {})
        dPet["all_pets"] = [pet.to_init_data()]
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp



