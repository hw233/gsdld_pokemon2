#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from game.common import utility
from game.define import constant
from corelib import spawn
from corelib.frame import Game

from game.define import msg_define

#连协 羁绊 队伍加成
class PlayerRelationship(utility.DirtyFlag):
    def __init__(self, owner):
        utility.DirtyFlag.__init__(self)
        self.owner = owner  # 拥有者

        self.relationship4 = {}

        self.save_cache = {}  # 存储缓存

        # 宠物激活
        self.owner.sub(msg_define.MSG_PET_CHANGE, self.event_pet_change)
        # 出战阵型变更
        self.owner.sub(msg_define.MSG_CHANGE_BATTLE_ARRAY, self.event_change_battle_array)


    def markDirty(self):
        utility.DirtyFlag.markDirty(self)
        if self.owner:
            self.owner.markDirty()

    def uninit(self):
        # 宠物激活
        self.owner.unsub(msg_define.MSG_PET_CHANGE, self.event_pet_change)
        # 出战阵型变更
        self.owner.unsub(msg_define.MSG_CHANGE_BATTLE_ARRAY, self.event_change_battle_array)

    # 存库数据
    def to_save_dict(self, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            self.save_cache = {}

        return self.save_cache

    # 读库数据初始化
    def load_from_dict(self, data):
        pass

    # 登录初始化下发数据
    def to_init_data(self):
        init_data = {}

        return init_data

    def event_pet_change(self, push=1):
        #羁绊 组合存在多个情况	2）存在即激活(不用上阵）
        #统计分类
        allPets = {}
        for pet in self.owner.pet.all_pets.values():
            pets = allPets.setdefault(pet.resID, [])
            pets.append(pet)

        #判断上阵
        relationship4 = {}
        for obj in Game.res_mgr.res_petrelationship3.values():
            isOK = 0
            if obj.need:
                rs = Game.condition_mgr.check(obj.passID, player=self.owner)
                if rs:
                    isOK = 1
            else:
                isOK = 1

            #条件检查
            if isOK:
                isAdd = 1
                for resID in obj.limit:
                    if not allPets.get(resID):
                        isAdd = 0
                        break
                if isAdd:
                    for resID in obj.limit:
                        data = relationship4.setdefault(resID, set())
                        data.add(obj.id)

        #找出差异化的地方 更新
        change = {}
        for resID, new in relationship4.items():
            old = self.relationship4.get(resID, set())
            if old.symmetric_difference(new):
                change[resID] = new

        effect_pets = set()
        for pet in self.owner.pet.all_pets.values():
            data = change.get(pet.resID)
            if data:
                rs = pet.relation.updateRelationship4(data)
                if rs:
                    effect_pets.add(pet)

        self.relationship4 = relationship4
        self.markDirty()

        for pet in effect_pets:
            pet.attr.recalAttr([constant.PET_ATTR_MODULE_RELATION_4])

        #推送给客户端
        if push:
            if effect_pets:
                self.owner.attr.RecalFightAbility()
                dUpdate = {}
                dUpdate["base"] = {"fa": self.owner.base.GetFightAbility()}
                dPet = dUpdate.setdefault("pet", {})
                dPet["all_pets"] = [pet.to_init_data() for pet in effect_pets]
                resp = {
                    "allUpdate": dUpdate,
                }
                spawn(self.owner.call, "roleAllUpdate", resp, noresult=True)


    def event_change_battle_array(self, battletype, position):
        #数据统计
        allPetID = {}
        for pet in self.owner.pet.all_pets.values():
            allPetID[pet.resID] = allPetID.get(pet.resID, 0) + 1

        effect_pets = set()
        wave = 0
        for oneWave in position:
            #数据统计
            wave += 1
            waveEle = {}
            waveJob = {}
            waveRelation = {}
            wavePets = {}
            for uid in oneWave.values():
                pet = self.owner.pet.getPet(uid)
                if pet:
                    res = Game.res_mgr.res_pet.get(pet.resID)
                    #元素
                    waveEle[res.eleType] = waveEle.get(res.eleType, 0) + 1
                    #职业
                    waveJob[res.job] = waveJob.get(res.job, 0) + 1
                    #其他
                    for t in res.relation:
                        waveRelation[t] = waveRelation.get(t, 0) + 1

                    wavePets[pet.resID] = pet

            #连协
            relationship1 = {}
            for obj in Game.res_mgr.res_petrelationship1.values():
                if obj.passID and Game.condition_mgr.check(obj.passID, player=self.owner):
                    checkData = allPetID
                else:
                    checkData = wavePets
                isAdd = 1
                for resID in obj.limit:
                    if not checkData.get(resID):
                        isAdd = 0
                        break
                if isAdd:
                    for resID in obj.limit:
                        data = relationship1.setdefault(resID, set())
                        data.add(obj.id)
            #差异比较 删除旧的，增加新的
            for resID, pet in wavePets.items():
                data = relationship1.get(resID, set())
                rs = pet.relation.updateRelationship1(battletype, wave, data)
                if rs:
                    effect_pets.add(pet)

            #队伍加成
            relationship2 = {}
            for obj in Game.res_mgr.res_petrelationship2.values():
                isAdd = 1
                for k, v in obj.limit1.items():
                    if waveEle.get(k, 0) < v:
                        isAdd = 0
                        break
                for k, v in obj.limit2.items():
                    if waveJob.get(k, 0) < v:
                        isAdd = 0
                        break
                for k, v in obj.limit3.items():
                    if waveRelation.get(k, 0) < v:
                        isAdd = 0
                        break
                if isAdd:
                    curRes = relationship2.setdefault(obj.group)
                    if curRes:
                        #同组只取最高的
                        if obj.lv > curRes.lv:
                            relationship2[obj.group] = obj
                    else:
                        relationship2[obj.group] = obj
            # 差异比较 删除旧的，增加新的
            for resID, pet in wavePets.items():
                data = set()
                res = Game.res_mgr.res_pet.get(pet.resID)
                for obj in relationship2.values():
                    if obj.addall:
                        data.add(obj.id)
                    else:
                        if res.eleType in obj.addele:
                            data.add(obj.id)
                        if res.job in obj.addjob:
                            data.add(obj.id)
                        for oneType in res.relation:
                            if oneType in obj.addrelation:
                                data.add(obj.id)

                rs = pet.relation.updateRelationship2(battletype, wave, data)
                if rs:
                    effect_pets.add(pet)


            #羁绊 组合存在多个情况	1）同时上阵
            relationship3 = {}
            for obj in Game.res_mgr.res_petrelationship3.values():
                if obj.need:
                    rs = Game.condition_mgr.check(obj.passID, player=self.owner)
                    if rs:
                        continue
                    isAdd = 1
                    for resID in obj.limit:
                        if not wavePets.get(resID):
                            isAdd = 0
                            break
                    if isAdd:
                        for resID in obj.limit:
                            data = relationship3.setdefault(resID, set())
                            data.add(obj.id)
            # 差异比较 删除旧的，增加新的
            for resID, pet in wavePets.items():
                data = relationship3.get(resID, set())
                rs = pet.relation.updateRelationship3(battletype, wave, data)
                if rs:
                    effect_pets.add(pet)

        if effect_pets:
            for pet in effect_pets:
                pet.attr.recalAttr([constant.PET_ATTR_MODULE_RELATION_1, constant.PET_ATTR_MODULE_RELATION_2,
                                    constant.PET_ATTR_MODULE_RELATION_3, constant.PET_ATTR_MODULE_RELATION_4])

            # dUpdate = {}
            # dUpdate["base"] = {"fa": self.owner.base.GetFightAbility()}
            # dPet = dUpdate.setdefault("pet", {})
            # dPet["all_pets"] = [pet.to_init_data() for pet in effect_pets]
            # resp = {
            #     "allUpdate": dUpdate,
            # }
            # spawn(self.owner.call, "roleAllUpdate", resp, noresult=True)


    def do_login(self):
        #登陆时重算  连协 羁绊 队伍加成
        self.event_pet_change(push=0)

        for obj in self.owner.battle_array.troops.values():
            self.event_change_battle_array(obj.battletype, obj.position)






