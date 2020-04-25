#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import time

from game.common import utility
from game.define import constant, msg_define
from corelib.frame import Game, spawn
from game.core.attributeContainer import FaAttributeContainer

class PlayerAttributeContainer(FaAttributeContainer):
    """玩家属性容器"""
    def __init__(self, owner, is_recal=1):
        super(PlayerAttributeContainer, self).__init__(owner, is_recal=is_recal)

        self.is_upload_rank = False

    def recalFa(self):
        self.is_upload_rank = super(PlayerAttributeContainer, self).recalFa()

    def cleanUpload(self):
        self.is_upload_rank = False

    def canUpload(self):
        return self.is_upload_rank

#角色属性
class PlayerAttr(utility.DirtyFlag):
    def __init__(self, owner):
        utility.DirtyFlag.__init__(self)
        self.owner = owner  # 拥有者

        # 分模块统计
        self.module_attr = {}  # {moduleType:obj}
        # 分容器统计
        self.container_attr = {}  # {containerType:obj}

        self.save_cache = {} #存储缓存


    def markDirty(self):
        utility.DirtyFlag.markDirty(self)
        if self.owner:
            self.owner.markDirty()

    #存库数据
    def to_save_dict(self, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            self.save_cache = {}
        return self.save_cache

    #读库数据初始化
    def load_from_dict(self, data):
        pass

    #登录初始化下发数据
    def to_init_data(self):
        init_data = {}
        init_data["module"] = {}
        for moduleType, moduleobj in self.module_attr.items():
            init_data["module"][moduleType] = moduleobj.packageList()

        init_data["container"] = {}
        for containerType, containerobj in self.container_attr.items():
            init_data["container"][containerType] = containerobj.packageList()

        return init_data

    def uninit(self):
        pass

    def to_container_data(self):
        data = {}
        for containerType, containerobj in self.container_attr.items():
            data[containerType] = containerobj.packageList()
        return data

    def recalAttr(self):
        # 分模块统计
        self.module_attr = {}  # {moduleType:obj}
        # 分容器统计
        self.container_attr = {}  # {containerType:obj}
        #图鉴
        self.owner.pet.recalAttr()
        # 图腾
        self.owner.totem.recalAttr()
        # 房子
        self.owner.house.recalAttr()
        # 称号
        self.owner.chenghao.recalAttr()
        # 头像
        self.owner.myhead.recalAttr()

    def addAttr(self, data, moduleType, containerType):
        # 分模块统计
        moduleobj = self.module_attr.setdefault(moduleType, PlayerAttributeContainer(self.owner))
        moduleobj.addAttr(data)
        #分容器统计
        containerobj = self.container_attr.setdefault(containerType, PlayerAttributeContainer(self.owner))
        containerobj.addAttr(data)

        self.markDirty()
        self.owner.safe_pub(msg_define.MSG_ROLE_ATTR_CHANGE, moduleType, containerType)

    def delAttr(self, data, moduleType, containerType):
        # 分模块统计
        moduleobj = self.module_attr.setdefault(moduleType, PlayerAttributeContainer(self.owner))
        moduleobj.delAttr(data)
        #分容器统计
        containerobj = self.container_attr.setdefault(containerType, PlayerAttributeContainer(self.owner))
        containerobj.delAttr(data)

        self.markDirty()
        self.owner.safe_pub(msg_define.MSG_ROLE_ATTR_CHANGE, moduleType, containerType)

    def getModule(self, moduleType):
        moduleobj = self.module_attr.setdefault(moduleType, PlayerAttributeContainer(self.owner))
        return moduleobj

    def getContainer(self, containerType):
        containerobj = self.container_attr.setdefault(containerType, PlayerAttributeContainer(self.owner))
        return containerobj

    def getModFa(self, moduleType):
        moduleobj = self.module_attr.setdefault(moduleType, PlayerAttributeContainer(self.owner))
        return moduleobj.fa

    def getContainerFa(self, containerType):
        containerobj = self.container_attr.setdefault(containerType, PlayerAttributeContainer(self.owner))
        return containerobj.fa

    def getAllModFa(self):
        resp = {}
        for moduleType, moduleobj in self.module_attr.items():
            resp[moduleType] = moduleobj.fa
        return resp

    def to_update_data(self):
        update_data = {}
        update_data["module"] = []
        for moduleType, moduleobj in self.module_attr.items():
            if moduleobj.isDirty():
                update_data["module"].append({"k": moduleType, "v": moduleobj.packDirty()})

        update_data["container"] = []
        for containerType, containerobj in self.container_attr.items():
            if containerobj.isDirty():
                update_data["container"].append({"k": containerType, "v": containerobj.packDirty()})
        return update_data

    def RecalFightAbility(self):
        #各模块战力
        for moduleType, moduleobj in self.module_attr.items():
            rankType = constant.MAP_FA_RANK_TYPE.get(moduleType)
            if rankType and moduleobj.canUpload():
                self.owner.rank.uploadRank(rankType, {"fa": moduleobj.fa})
                moduleobj.cleanUpload()

        # #属性池子战力
        # pool_fa = 0
        # for containerType, containerobj in self.container_attr.items():
        #     pool_fa += containerobj.fa
        # self.owner.rank.uploadRank(constant.RANK_TYPE_ATTR_FA, {"fa": pool_fa})

        #宠物各种榜
        # 出战队伍战力
        fight_fa = 0
        fightList = self.owner.pet.getFightPet(constant.BATTLE_ARRAY_TYPE_NORMAL)
        if fightList:
            wave = fightList[0]
            for one in wave:
                fight_fa += one.getPetFA()
            self.owner.base.SetFightAbility(fight_fa)

        # # 所有激活宠物战力
        # all_fa = 0
        # allList = self.owner.pet.getAllPet()
        # for one in allList:
        #     all_fa += one.attr.fa
        # self.owner.rank.uploadRank(constant.RANK_TYPE_PET_QA_FA, {"fa": all_fa})

        # 最强宠物战力
        bestData = self.owner.pet.getBest()
        need_update_rank = {
            constant.CROSS_RANK_TYPE_PET_WATER: bestData.get(constant.PKM2_ELE_TYPE_WATER), # 水系宠物
            constant.CROSS_RANK_TYPE_PET_LIGHT: bestData.get(constant.PKM2_ELE_TYPE_LIGHT), # 光系宠物
            constant.CROSS_RANK_TYPE_PET_GRASS: bestData.get(constant.PKM2_ELE_TYPE_GRASS), # 草系宠物
            constant.CROSS_RANK_TYPE_PET_DARK: bestData.get(constant.PKM2_ELE_TYPE_DARK), # 暗系宠物
            constant.CROSS_RANK_TYPE_PET_FIRE: bestData.get(constant.PKM2_ELE_TYPE_FIRE), # 火系宠物
            constant.CROSS_RANK_TYPE_PET_BEST: bestData.get(constant.PKM2_ELE_TYPE_NONE), # 最强宠物

            constant.CROSS_RANK_TYPE_PET_WATER_HEFU: bestData.get(constant.PKM2_ELE_TYPE_WATER),  # 合服水系宠物
            constant.CROSS_RANK_TYPE_PET_LIGHT_HEFU: bestData.get(constant.PKM2_ELE_TYPE_LIGHT),  # 合服光系宠物
            constant.CROSS_RANK_TYPE_PET_GRASS_HEFU: bestData.get(constant.PKM2_ELE_TYPE_GRASS),  # 合服草系宠物
            constant.CROSS_RANK_TYPE_PET_DARK_HEFU: bestData.get(constant.PKM2_ELE_TYPE_DARK),  # 合服暗系宠物
            constant.CROSS_RANK_TYPE_PET_FIRE_HEFU: bestData.get(constant.PKM2_ELE_TYPE_FIRE),  # 合服火系宠物
            constant.CROSS_RANK_TYPE_PET_BEST_HEFU: bestData.get(constant.PKM2_ELE_TYPE_NONE),  # 合服最强宠物
        }
        # 上传跨服榜
        for rankType, one in need_update_rank.items():
            if one:
                self.owner.rank.uploadCrossRank(rankType, {"fa": one.getPetFA(), "petId": one.id})
        #最强宠物保底奖励检查
        # self.owner.rank.checkBestPetCrossRank(bestData)
        #抛事件
        self.owner.safe_pub(msg_define.MSG_FA_CHANGE, fight_fa)




