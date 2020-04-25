#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import copy

from game.common import utility
from game.core.equip import CreatEquip
from corelib.frame import Game
from game.define import constant

from game.core.attributeContainer import FaAttributeContainer

class PetAttributeContainer(FaAttributeContainer):
    def __init__(self, owner):
        super(PetAttributeContainer, self).__init__(owner)

        # 初始属性
        self.cache_calInitAttr = {}
        # 等级属性 进化属性
        self.cache_calLvAndEvolveAttr = {}
        # 技能
        self.cache_calSkillAttr = {}
        # 特性
        self.cache_calPeculiarityAttr = {}

        #战斗缓存
        self.fightAttr = {}


    def recalAttr(self, recalMod):
        self.fightAttr = {} #清理缓存

        total = {}
        # 初始属性
        if constant.PET_ATTR_MODULE_ALL in recalMod or constant.PET_ATTR_MODULE_INIT in recalMod:
            attr = self.calInitAttr()
        else:
            attr = self.cache_calInitAttr
        for name, iNum in attr.items():
            total[name] = total.get(name, 0) + iNum

        #等级属性 进化属性
        if constant.PET_ATTR_MODULE_ALL in recalMod or constant.PET_ATTR_MODULE_LV_EVOLVE in recalMod:
            attr = self.calLvAndEvolveAttr()
        else:
            attr = self.cache_calLvAndEvolveAttr
        for name, iNum in attr.items():
            total[name] = total.get(name, 0) + iNum

        #技能
        if constant.PET_ATTR_MODULE_ALL in recalMod or constant.PET_ATTR_MODULE_SKILL in recalMod:
            attr = self.calSkillAttr()
        else:
            attr = self.cache_calSkillAttr
        for name, iNum in attr.items():
            total[name] = total.get(name, 0) + iNum

        #特性
        if constant.PET_ATTR_MODULE_ALL in recalMod or constant.PET_ATTR_MODULE_PECULIARITY in recalMod:
            attr = self.calPeculiarityAttr()
        else:
            attr = self.cache_calPeculiarityAttr
        for name, iNum in attr.items():
            total[name] = total.get(name, 0) + iNum

        # 连协
        relation1 = self.owner.relation.calRelation1(constant.BATTLE_ARRAY_TYPE_NORMAL)
        attr = relation1.get(1, {})
        for name, iNum in attr.items():
            total[name] = total.get(name, 0) + iNum
        # 队伍加成
        relation2 = self.owner.relation.calRelation2(constant.BATTLE_ARRAY_TYPE_NORMAL)
        attr = relation2.get(1, {})
        for name, iNum in attr.items():
            total[name] = total.get(name, 0) + iNum
        # 羁绊
        relation3 = self.owner.relation.calRelation3(constant.BATTLE_ARRAY_TYPE_NORMAL)
        attr = relation3.get(1, {})
        for name, iNum in attr.items():
            total[name] = total.get(name, 0) + iNum

        attr = self.owner.relation.calRelation4()
        for name, iNum in attr.items():
            total[name] = total.get(name, 0) + iNum

        #装备


        #异兽装备


        #各类比率加成
        addition = self.calRateAdditionAttr()
        for name, iNum in addition.items():
            total[name] = total.get(name, 0) + iNum
        if total:
            self.resetAttr(total)
        return total

    def calInitAttr(self):
        # 初始属性
        resp = {}
        res = Game.res_mgr.res_pet.get(self.owner.resID)
        if res:
            for name, iNum in res.attr.items():
                resp[name] = resp.get(name, 0) + iNum
        self.cache_calInitAttr = resp
        return resp

    def calLvAndEvolveAttr(self):
        # 等级属性 进化属性
        resp = {}
        evolveRes = Game.res_mgr.res_idlv_petevolve.get((self.owner.resID, self.owner.evolveLv))
        if evolveRes:
            for name, iNum in evolveRes.attr.items():
                resp[name] = resp.get(name, 0) + iNum
            for name, iNum in evolveRes.lvAttr.items():
                resp[name] = resp.get(name, 0) + iNum * (self.owner.lv - 1)
        self.cache_calLvAndEvolveAttr = resp
        return resp

    def calSkillAttr(self):
        # 技能
        resp = {}
        for skill_id in self.owner.skills:
            skillRes = Game.res_mgr.res_skill.get(skill_id)
            if skillRes:
                for name, iNum in skillRes.attr.items():
                    resp[name] = resp.get(name, 0) + iNum
        self.cache_calSkillAttr = resp
        return resp

    def calPeculiarityAttr(self):
        #特性
        resp = {}
        for one in self.owner.peculiarity.values():
            skill_id = one[0]
            skillRes = Game.res_mgr.res_skill.get(skill_id)
            if skillRes:
                for name, iNum in skillRes.attr.items():
                    resp[name] = resp.get(name, 0) + iNum
        self.cache_calPeculiarityAttr = resp
        return resp

    # 其他比率加成
    def calRateAdditionAttr(self):
        player = self.owner.ownerPet.owner

        res = Game.res_mgr.res_pet.get(self.owner.resID)
        #统计比率属性
        addRate = {}
        for name in constant.PET_ADD_ATTR:
            #宠物自身  # 连协 羁绊 队伍加成  通用阵型已经加入到宠物自身了
            iNum =getattr(self, name, 0)
            if iNum:
                addRate[name] = addRate.get(name, 0) + iNum
            #元素池子
            cType = constant.MAP_ELETYPE_ATTR_CONTAINER.get(res.eleType)
            iNum =getattr(player.attr.getContainer(cType), name, 0)
            if iNum:
                addRate[name] = addRate.get(name, 0) + iNum
            #职业池子
            cType = constant.MAP_JOBTYPE_ATTR_CONTAINER.get(res.job)
            iNum =getattr(player.attr.getContainer(cType), name, 0)
            if iNum:
                addRate[name] = addRate.get(name, 0) + iNum
            #全局池子
            iNum =getattr(player.attr.getContainer(constant.PKM2_ATTR_CONTAINER_GLOBAL), name, 0)
            if iNum:
                addRate[name] = addRate.get(name, 0) + iNum

        total = {}
        #比率属性换算
        baseAttr = self.getBaseAttr()
        for name, rate in addRate.items():
            attrName = constant.MAP_ATTRRATE_ATTR.get(name)
            val = int(baseAttr.get(attrName, 0) * rate/10000)

            total[attrName] = total.get(attrName, 0) + val

        return total

    def getBaseAttr(self):
        #基数属性
        resp = {}
        for name, iNum in self.cache_calInitAttr.items():
            resp[name] = resp.get(name, 0) + iNum
        for name, iNum in self.cache_calLvAndEvolveAttr.items():
            resp[name] = resp.get(name, 0) + iNum
        return resp

    def getFightAttr(self, battletype):
        cache = self.fightAttr.get(battletype)
        if cache:
            return cache

        player = self.owner.ownerPet.owner
        res = Game.res_mgr.res_pet.get(self.owner.resID)

        total = {}
        # 初始属性
        attr = self.cache_calInitAttr
        for name, iNum in attr.items():
            total[name] = total.get(name, 0) + iNum
        #等级属性 进化属性
        attr = self.cache_calLvAndEvolveAttr
        for name, iNum in attr.items():
            total[name] = total.get(name, 0) + iNum
        #技能
        attr = self.cache_calSkillAttr
        for name, iNum in attr.items():
            total[name] = total.get(name, 0) + iNum
        #特性
        attr = self.cache_calPeculiarityAttr
        for name, iNum in attr.items():
            total[name] = total.get(name, 0) + iNum
        # 连协
        relation1 = self.owner.relation.calRelation1(battletype)
        attr = relation1.get(1, {})
        for name, iNum in attr.items():
            total[name] = total.get(name, 0) + iNum
        # 队伍加成
        relation2 = self.owner.relation.calRelation2(battletype)
        attr = relation2.get(1, {})
        for name, iNum in attr.items():
            total[name] = total.get(name, 0) + iNum
        # 羁绊
        relation3 = self.owner.relation.calRelation3(battletype)
        attr = relation3.get(1, {})
        for name, iNum in attr.items():
            total[name] = total.get(name, 0) + iNum

        attr = self.owner.relation.calRelation4()
        for name, iNum in attr.items():
            total[name] = total.get(name, 0) + iNum

        #装备


        #异兽装备


        #各类容器加成
        for name in constant.ALL_ATTR:
            #元素池子
            cType = constant.MAP_ELETYPE_ATTR_CONTAINER.get(res.eleType)
            iNum =getattr(player.attr.getContainer(cType), name, 0)
            if iNum:
                total[name] = total.get(name, 0) + iNum
            #职业池子
            cType = constant.MAP_JOBTYPE_ATTR_CONTAINER.get(res.job)
            iNum =getattr(player.attr.getContainer(cType), name, 0)
            if iNum:
                total[name] = total.get(name, 0) + iNum
            #全局池子
            iNum =getattr(player.attr.getContainer(constant.PKM2_ATTR_CONTAINER_GLOBAL), name, 0)
            if iNum:
                total[name] = total.get(name, 0) + iNum

        #各类比率加成
        addition = self.calRateAdditionAttr()
        for name, iNum in addition.items():
            total[name] = total.get(name, 0) + iNum

        resp = []
        for name in constant.ALL_ATTR:
            resp.append(total.get(name, 0))

        self.fightAttr[battletype] = resp
        return resp


class PetRelation(object):
    def __init__(self, owner):
        self.owner = owner

        self.relationship1 = {}  # 连协  同时上阵才能激活连协效果
        self.relationship2 = {}  # 队伍加成 上阵单位激活
        self.relationship3 = {}  # 羁绊 组合存在多个情况	1）同时上阵
        self.relationship4 = {}  # 羁绊 组合存在多个情况	2）存在即激活(不用上阵）

    def packRelation(self, battletype):
        resp = {}

        resp["r1"] = {}
        for wave, dwave in self.relationship1.get(battletype, {}).items():
            resp["r1"][str(wave)] = list(dwave.get("data", set()))

        resp["r2"] = {}
        for wave, dwave in self.relationship2.get(battletype, {}).items():
            resp["r2"][str(wave)] = list(dwave.get("data", set()))

        resp["r3"] = {}
        for wave, dwave in self.relationship3.get(battletype, {}).items():
            resp["r3"][str(wave)] = list(dwave.get("data", set()))

        resp["r4"] = list(self.relationship4.get("data", set()))

        return resp

    def packRelationAll(self):
        resp = {}

        resp["r1"] = {}
        for battletype, dType in self.relationship1.items():
            rsType = resp["r1"].setdefault(battletype, {})
            for wave, dwave in dType.items():
                rsType[str(wave)] = list(dwave.get("data", set()))

        resp["r2"] = {}
        for battletype, dType in self.relationship2.items():
            rsType = resp["r2"].setdefault(battletype, {})
            for wave, dwave in dType.items():
                rsType[str(wave)] = list(dwave.get("data", set()))

        resp["r3"] = {}
        for battletype, dType in self.relationship3.items():
            rsType = resp["r3"].setdefault(battletype, {})
            for wave, dwave in dType.items():
                rsType[str(wave)] = list(dwave.get("data", set()))

        resp["r4"] = list(self.relationship4.get("data", set()))

        return resp

    def updateRelationship1(self, battletype, wave, relationship):
        dtype = self.relationship1.setdefault(battletype, {})
        dwave = dtype.setdefault(wave, {})
        data = dwave.setdefault("data", set())
        if data.symmetric_difference(relationship):
            dwave["data"] = relationship
            dwave["dirty"] = 1
            return True
        return False

    def updateRelationship2(self, battletype, wave, relationship):
        dtype = self.relationship2.setdefault(battletype, {})
        dwave = dtype.setdefault(wave, {})
        data = dwave.setdefault("data", set())
        if data.symmetric_difference(relationship):
            dwave["data"] = relationship
            dwave["dirty"] = 1
            return True
        return False

    def updateRelationship3(self, battletype, wave, relationship):
        dtype = self.relationship3.setdefault(battletype, {})
        dwave = dtype.setdefault(wave, {})
        data = dwave.setdefault("data", set())
        if data.symmetric_difference(relationship):
            dwave["data"] = relationship
            dwave["dirty"] = 1
            return True
        return False

    def updateRelationship4(self, relationship):
        data = self.relationship4.setdefault("data", set())
        if data.symmetric_difference(relationship):
            self.relationship4["data"] = relationship
            self.relationship4["dirty"] = 1
            return True
        return False

    def calRelation1(self, battletype):
        # 连协
        dtype = self.relationship1.get(battletype, {})
        resp = {}
        for wave, dwave in dtype.items():
            if not dwave.get("dirty"):
                cache = dwave.get("cache")
                if cache:
                    resp[wave] = cache
                    continue

            data = dwave.get("data", set())
            total = resp.setdefault(wave, {})
            for relationID in data:
                obj = Game.res_mgr.res_petrelationship1.get(relationID)
                if obj:
                    index = obj.limit.index(self.owner.resID)
                    skill_id = getattr(obj, "skill%s"%(index+1), 0)
                    skillRes = Game.res_mgr.res_skill.get(skill_id)
                    if skillRes:
                        for name, iNum in skillRes.attr.items():
                            total[name] = total.get(name, 0) + iNum
            dwave["dirty"] = 0
            dwave["cache"] = total
        return resp

    def calRelation2(self, battletype):
        #队伍加成
        dtype = self.relationship2.get(battletype, {})
        resp = {}
        for wave, dwave in dtype.items():
            if not dwave.get("dirty"):
                cache = dwave.get("cache")
                if cache:
                    resp[wave] = cache
                    continue

            data = dwave.get("data", set())
            total = resp.setdefault(wave, {})
            for relationID in data:
                obj = Game.res_mgr.res_petrelationship2.get(relationID)
                if obj:
                    for name, iNum in obj.addAttr.items():
                        total[name] = total.get(name, 0) + iNum
            dwave["dirty"] = 0
            dwave["cache"] = total
        return resp

    def calRelation3(self, battletype):
        # 羁绊
        dtype = self.relationship3.get(battletype, {})
        resp = {}
        for wave, dwave in dtype.items():
            if not dwave.get("dirty"):
                cache = dwave.get("cache")
                if cache:
                    resp[wave] = cache
                    continue

            data = dwave.get("data", set())
            total = resp.setdefault(wave, {})
            for relationID in data:
                obj = Game.res_mgr.res_petrelationship3.get(relationID)
                if obj:
                    index = obj.limit.index(self.owner.resID)
                    addAttr = getattr(obj, "addAttr%s" % (index + 1), {})
                    for name, iNum in addAttr.items():
                        total[name] = total.get(name, 0) + iNum
            dwave["dirty"] = 0
            dwave["cache"] = total
        return resp

    def calRelation4(self):
        if not self.relationship4.get("dirty"):
            cache = self.relationship4.get("cache")
            if cache:
                return cache

        data = self.relationship4.get("data", set())
        total = {}
        for relationID in data:
            obj = Game.res_mgr.res_petrelationship3.get(relationID)
            if obj:
                index = obj.limit.index(self.owner.resID)
                addAttr = getattr(obj, "addAttr%s" % (index + 1), {})
                for name, iNum in addAttr.items():
                    total[name] = total.get(name, 0) + iNum
        self.relationship4["dirty"] = 0
        self.relationship4["cache"] = total
        return total

class Pet(utility.DirtyFlag):
    def __init__(self, res, data=None, owner=None):
        utility.DirtyFlag.__init__(self)
        self.id = "" #宠物唯一id
        self.resID = res.id #宠物资源id
        self.lv = 1 #宠物等级
        self.evolveLv = 1 #宠物进化等级
        self.skills = [] #宠物技能
        self.battle_array = [] #宠物已出战模块
        self.lock = 0 #是否锁定

        self.peculiarity = {}  #特性 {部位:(技能表id, 锁定状态)} 0=不锁定 1=锁定   0部位是专属技能
        for index, skillId in enumerate(res.peculiarity):
            self.peculiarity[index+1] = (skillId, 0)
        self.washSkill = {} #宠物已洗出技能列表 {部位:技能表id} 0部位是专属技能
        self.washStar = res.washSatr #宠物技能洗练星数 默认1星
        washstarRes = Game.res_mgr.res_petwashstar.get(self.washStar-1)
        if washstarRes:
            self.washNum = washstarRes.cnt  # 宠物洗练星数当前已洗练次数
        else:
            self.washNum = 0 #宠物洗练星数当前已洗练次数

        self.equip = {} #装备

        self.attr = PetAttributeContainer(self)
        self.relation = PetRelation(self)

        self.save_cache = {}  # 存储缓存

        if data:
            self.load_from_dict(data)

        self.ownerPet = None
        if owner:
            self.set_owner(owner)


        #初始化技能
        self.SetLv(self.lv)
        #初始化被动技能
        evolveRes = Game.res_mgr.res_idlv_petevolve.get((self.resID, self.evolveLv))
        for i in range(evolveRes.maxSlots):
            if not self.peculiarity.get(i+1):
                self.peculiarity[i+1] = (0, 0)


    def markDirty(self):
        utility.DirtyFlag.markDirty(self)
        if self.ownerPet:
            self.ownerPet.markDirty()

    def set_owner(self, owner):
        self.ownerPet = owner.pet
        if not self.id:
            self.id = "%s-%s"%(owner.id, owner.data.GeneratePetTranceNo())
            self.markDirty()

    # 存库数据
    def to_save_dict(self, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            res = Game.res_mgr.res_pet.get(self.resID)

            self.save_cache = {}
            self.save_cache["id"] = self.id
            self.save_cache["resID"] = self.resID
            if self.lv != 1:
                self.save_cache["lv"] = self.lv
            if self.evolveLv != 1:
                self.save_cache["evLv"] = self.evolveLv
            if self.skills != list(res.skills.keys()):
                self.save_cache["skills"] = self.skills
            if self.battle_array:
                self.save_cache["b_array"] = self.battle_array
            if self.lock:
                self.save_cache["lock"] = self.lock

            if self.washStar != res.washSatr:
                self.save_cache["washStar"] = self.washStar
            if self.washNum:
                self.save_cache["washNum"] = self.washNum
            if self.peculiarity:
                self.save_cache["peculiarity"] = {}
                for iPos, data in self.peculiarity.items():
                    self.save_cache["peculiarity"][str(iPos)] = data
            if self.washSkill:
                self.save_cache["washSkill"] = {}
                for iPos, skillId in self.washSkill.items():
                    self.save_cache["washSkill"][str(iPos)] = skillId

        return self.save_cache

    # 读库数据初始化
    def load_from_dict(self, data):
        self.id = data.get("id", '')  # 宠物唯一id
        self.resID = data.get("resID", 0)  # 宠物资源id
        self.lv = data.get("lv", 1)  # 宠物等级
        self.evolveLv = data.get("evLv", 1)  # 宠物进化等级
        self.skills = data.get("skills", [])  # 宠物技能
        self.battle_array = data.get("b_array", [])  # 宠物已出战模块
        self.lock = data.get("lock", 0)  # 是否锁定
        self.washStar = data.get("washStar", self.washStar)  # 宠物技能洗练星数 默认1星
        self.washNum = data.get("washNum", 0)  # 宠物洗练星数当前已洗练次数

        peculiarity = data.get("peculiarity", {})  # 宠物被动技能列表 {部位:(技能表id, 锁定状态)} 0=不锁定 1=锁定
        for k, v in peculiarity.items():
            self.peculiarity[int(k)] = v
        washSkill = data.get("washSkill", {})  # 宠物已洗出技能列表 {部位:技能表id}
        for k, v in washSkill.items():
            self.washSkill[int(k)] = v

    # 登录初始化下发数据
    def to_init_data(self):
        init_data = {}
        init_data["id"] = self.id
        init_data["resID"] = self.resID
        init_data["lv"] = self.lv
        init_data["evLv"] = self.evolveLv
        init_data["attr"] = self.attr.packageList()
        init_data["skills"] = self.skills
        init_data["b_array"] = self.battle_array
        init_data["washStar"] = self.washStar
        init_data["washNum"] = self.washNum
        init_data["lock"] = self.lock

        init_data["peculiarity"] = {}
        for iPos, data in self.peculiarity.items():
            init_data["peculiarity"][iPos] = data
        init_data["washSkill"] = {}
        for iPos, skillId in self.washSkill.items():
            init_data["washSkill"][iPos] = skillId

        #连协 羁绊 队伍加成
        init_data["relation"] = self.relation.packRelationAll()

        return init_data

    def to_fight_data(self, battletype):
        resp = {}
        resp["id"] = self.id
        resp["resID"] = self.resID
        resp["lv"] = self.lv
        resp["evLv"] = self.evolveLv
        resp["attr"] = self.attr.getFightAttr(battletype)
        resp["skills"] = self.skills
        #连协 羁绊 队伍加成
        resp["relation"] = self.relation.packRelation(battletype)
        #特性
        resp["peculiarity"] = []
        for one in self.peculiarity.values():
            resp["peculiarity"].append(one[0])
        #兽灵装备技能

        return resp


    #零点更新的数据
    def to_wee_hour_data(self):
        init_data = {}
        return init_data

    def isInBattle(self):
        if self.battle_array:
            return True
        return False

    def isWearSomething(self):
        if self.equip:
            return True

        return False

    def getEleType(self):
        res = Game.res_mgr.res_pet.get(self.resID)
        return res.eleType

    def getPetFA(self):
        res = Game.res_mgr.res_pet.get(self.resID)
        fa = self.attr.fa #自身基础战力
        fa += self.ownerPet.owner.attr.getContainerFa(res.eleType) #元素池子加成
        fa += self.ownerPet.owner.attr.getContainerFa(res.job) #职业池子加成
        fa += self.ownerPet.owner.attr.getContainerFa(constant.PKM2_ATTR_CONTAINER_GLOBAL) #全局池子加成
        return fa

    def GetLv(self):
        return self.lv

    def SetLv(self, lv):
        self.lv = lv
        #技能跟等级解锁
        res = Game.res_mgr.res_pet.get(self.resID)
        if res:
            skillIds = []
            for _id in self.skills:
                skillres = Game.res_mgr.res_skill.get(_id)
                skillIds.append(skillres.skillId)
            for k, v in res.skills.items():
                skillres = Game.res_mgr.res_skill.get(k)
                if self.lv >= v and skillres.skillId not in skillIds:
                    self.skills.append(k)
            #技能跟等级提升
            for _id in self.skills:
                curres = Game.res_mgr.res_skill.get(_id)
                nextres = Game.res_mgr.res_idlv_skill.get((curres.id, curres.level+1))
                if nextres and self.lv >= nextres.needLv:
                    self.skillLvUp(_id, 1)

        self.markDirty()

    def GetResID(self):
        return self.resID

    def SetResID(self, resID):
        self.resID = resID
        self.markDirty()

    def isLock(self):
        return self.lock

    def SetLock(self, lock):
        self.lock = lock
        self.markDirty()

    def GetEvolveLv(self):
        return self.evolveLv

    def SetEvolveLv(self, evolveLv):
        self.evolveLv = evolveLv
        self.markDirty()

    def addBattleArray(self, battletype):
        if battletype not in self.battle_array:
            self.battle_array.append(battletype)
            self.markDirty()

    def removeBattleArray(self, battletype):
        if battletype in self.battle_array:
            self.battle_array.remove(battletype)
            #清除 连协 羁绊 队伍加成
            self.relation.relationship1.pop(battletype, None)
            self.relation.relationship2.pop(battletype, None)
            self.relation.relationship3.pop(battletype, None)
            if battletype == constant.BATTLE_ARRAY_TYPE_NORMAL:
                self.attr.recalAttr([constant.PET_ATTR_MODULE_RELATION_1, constant.PET_ATTR_MODULE_RELATION_2,
                                     constant.PET_ATTR_MODULE_RELATION_3, constant.PET_ATTR_MODULE_RELATION_4])
            self.markDirty()

    def costBack(self):
        #消耗宠物返还材料
        back = {}
        res = Game.res_mgr.res_pet.get(self.resID)
        if not res:
            return back

        for i in range(self.lv):
            #当前等级资源
            iBackLv = self.lv - i - 1
            curRes = Game.res_mgr.res_qalv_petlv.get((res.quality, iBackLv))
            if not curRes:
                break
            for k, v in curRes.back.items():
                back[k] = back.get(k, 0) + v
        return back


    def skillLvUp(self, skill_id, upNum):
        if skill_id in self.skills:
            index = self.skills.index(skill_id)
            skillRes = Game.res_mgr.res_skill.get(skill_id)
            if skillRes:
                newRes = Game.res_mgr.res_idlv_skill.get(skillRes.skillId, skillRes.level + upNum)
                if newRes:
                    self.skills.remove(skill_id)
                    self.skills.insert(index, newRes.id)
                    self.markDirty()

    def setPrivate(self, skill_id):
        #设置专属特性
        if skill_id:
            self.peculiarity[0] = (skill_id, 0)
            self.markDirty()


    def addPeculiarity(self, addList):
        #增加特性
        keys = list(self.peculiarity.keys())
        if keys:
            curPos = max(keys) + 1
        else:
            curPos = 1

        res = Game.res_mgr.res_idlv_petevolve.get((self.resID, self.evolveLv))
        if res:
            if curPos > res.maxSlots:
                return

        for skill_id in addList:
            self.peculiarity[curPos] = (skill_id, 0)
            curPos += 1
        self.markDirty()

    def LockPeculiarity(self, pos):
        data = self.peculiarity.get(pos)
        if data:
            self.peculiarity[pos] = (data[0], 1) #{部位:(技能表id, 锁定状态)} 0=不锁定 1=锁定
            self.markDirty()

    def UnLockPeculiarity(self, pos):
        data = self.peculiarity.get(pos)
        if data:
            self.peculiarity[pos] = (data[0], 0)  # {部位:(技能表id, 锁定状态)} 0=不锁定 1=锁定
            self.markDirty()

    def GetLockPeculiarityNum(self):
        iNum = 0
        for pos, data in self.peculiarity.items():
            skillId, status = data
            if status == 1:
                iNum += 1
        return iNum

    def PeculiarityChange(self):
        """宠物技能更换"""
        for pos, data in self.peculiarity.items():
            skillId = self.washSkill.get(pos)
            if skillId:
                self.peculiarity[pos] = (skillId, data[1])
        self.washSkill = {}
        self.markDirty()

    def GetWashStar(self):
        return self.washStar

    def SetWashStar(self, star):
        self.washStar = star # 宠物技能洗练星数
        self.markDirty()

    def GetWashNum(self):
        return self.washNum

    def SetWashNum(self, iNum):
        self.washNum = iNum  # 宠物洗练星数当前已洗练次数
        self.markDirty()

    def WashPeculiarity(self):
        """技能洗练"""
        total_sub_type = {}  #统计分类
        washSkill = {} #当前不锁定可洗坑位
        for pos, data in self.peculiarity.items():
            skillId, status = data
            if status == 1:
                washSkill[pos] = skillId
                if pos != 0: #专属不算
                    skillRes = Game.res_mgr.res_skill.get(skillId)
                    one_type = total_sub_type.setdefault(skillRes.subType, [])
                    one_type.append(skillId)
            else:
                washSkill[pos] = 0

        # 【被动】触发技能同类型仅会出现1个
        # 【固定】属性技能同类型最多出现4个
        self.washSkill = {}
        for pos, skillId in washSkill.items():
            if skillId > 100:
                self.washSkill[pos] = skillId
                continue
            washRes = Game.res_mgr.res_idstar_petwash.get((self.resID, self.washStar))
            if pos == 0: #专属
                pool_group = washRes.private
                dWashData = Game.res_mgr.res_group_subtype_skills_petwashpool.get(pool_group)
                if not dWashData:
                    continue
                lRandPool = []
                for randData in dWashData.values():
                    lRandPool.extend(randData)
                if lRandPool:
                    skillId = utility.Choice(lRandPool)
                    self.washSkill[pos] = skillId

            else: #普通
                pool_group = washRes.peculiarity
                dWashData = copy.deepcopy(Game.res_mgr.res_group_subtype_skills_petwashpool.get(pool_group))

                for subType, skillids in total_sub_type.items():
                    # 【被动】触发技能同类型仅会出现1个
                    if subType <= constant.SKILL_SUB_TYPE_99 and len(skillids) >= 1:
                        if dWashData.get(subType):
                            dWashData.pop(subType)
                    # 【固定】属性技能同类型最多出现2个
                    if constant.SKILL_SUB_TYPE_200 < subType <= constant.SKILL_SUB_TYPE_299 and len(skillids) >= 4:
                        if dWashData.get(subType):
                            dWashData.pop(subType)
                if not dWashData:
                    continue
                lRandPool = []
                for randData in dWashData.values():
                    lRandPool.extend(randData)
                if lRandPool:
                    skillId = utility.Choice(lRandPool)
                    skillRes = Game.res_mgr.res_skill.get(skillId)
                    one_type = total_sub_type.setdefault(skillRes.subType, [])
                    one_type.append(skillId)
                    self.washSkill[pos] = skillId
        self.markDirty()
        return self.washSkill
