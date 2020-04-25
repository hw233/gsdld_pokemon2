#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import copy

from game.common import utility
from corelib.frame import Game
from game.define import constant, msg_define

from game.define import constant
from game.core.pet import Pet

#角色宠物
class PlayerPet(utility.DirtyFlag):
    def __init__(self, owner):
        utility.DirtyFlag.__init__(self)
        self.owner = owner  # 拥有者
        self.all_pets = {} # {宠物唯一id:obj}
        self.size = constant.PET_SIZE

        self.album = {} #宠物图鉴 {系：{图鉴pos：1}}

        self.save_cache = {} #存储缓存

    def markDirty(self):
        utility.DirtyFlag.markDirty(self)
        if self.owner:
            self.owner.markDirty()

    #存库数据
    def to_save_dict(self, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            self.save_cache = {}
            self.save_cache["size"] = self.size

            self.save_cache["all_pets"] = []
            for pet in self.all_pets.values():
                self.save_cache["all_pets"].append(pet.to_save_dict(forced=forced))

            self.save_cache["album"] = []
            for eleType, eleData in self.album.items():
                self.save_cache["album"].append({"tp":eleType, "d": utility.obj2json(eleData)})

        return self.save_cache

    #读库数据初始化
    def load_from_dict(self, data):
        self.size = data.get("size", constant.PET_SIZE)  # 宠物背包大小

        all_pets = data.get("all_pets", [])  # [宠物obj]
        for one in all_pets:
            res = Game.res_mgr.res_pet.get(one["resID"], None)
            if res:
                pet = Pet(res, data=one, owner=self.owner)
                self.all_pets[pet.id] = pet
            else:
                Game.glog.log2File("PetLoadNotFindError", "%s|%s" % (self.owner.id, one))

        album = data.get("album", [])  #图鉴
        for one in album:
            eleType = one.get("tp", 0)
            eleData = one.get("d", {})
            self.album[eleType] = utility.json2obj(eleData)


    #登录初始化下发数据
    def to_init_data(self):
        init_data = {}
        init_data["size"] = self.size
        init_data["all_pets"] = []
        for pet in self.all_pets.values():
            init_data["all_pets"].append(pet.to_init_data())

        return init_data

    #零点更新的数据
    def to_wee_hour_data(self):
        return self.to_init_data()

    def uninit(self):
        pass


    def do_login(self):
        #重算宠物属性
        for pet in self.all_pets.values():
            pet.attr.recalAttr([constant.PET_ATTR_MODULE_ALL])

    def getActPetNum(self):
        return len(self.all_pets)

    def getAlbumNum(self, eleType):
        # 图鉴数量
        return len(self.album.get(eleType, {}))

    def getAllAlbumNum(self):
        iTotal = 0
        for data in self.album.values():
            iTotal += len(data)
        return iTotal

    def actAlbum(self, pet):
        res = Game.res_mgr.res_pet.get(pet.resID)
        #图鉴激活
        isrecal1 = False
        if res:
            isrecal1 = self._actAlbum(res.eleType, pet.resID)

        isrecal2 = self._actAlbum(constant.PKM2_ELE_TYPE_NONE, pet.resID)

        #抛消息
        self.owner.safe_pub(msg_define.MSG_PET_ALBUMNUM_CHANGE)
        # 更新宠物图鉴榜
        self.owner.rank.uploadRank(constant.RANK_TYPE_PET_ALBUM)

        return isrecal1 or isrecal2

    def _actAlbum(self, eleType, resID):
        isrecal = False
        eledata = self.album.setdefault(eleType, {})
        if not eledata.get(resID):
            eledata[resID] = 1
            self.markDirty()

            # 图鉴属性
            eleTypeNum = self.getAlbumNum(eleType)
            albumRes = Game.res_mgr.res_typeneed_petalbum.get((eleType, eleTypeNum))
            if albumRes:
                albumOldRes = Game.res_mgr.res_typelv_petalbum.get((albumRes.eleType, albumRes.lv - 1))
                if albumOldRes:
                    # 扣除原来旧等级的属性
                    self.owner.attr.delAttr(albumOldRes.attr, constant.MAP_ELETYPE_ALBLUM_FA.get(eleType),
                                            constant.MAP_ELETYPE_ATTR_CONTAINER.get(eleType))
                # 附加新等级的属性
                self.owner.attr.addAttr(albumRes.attr, constant.MAP_ELETYPE_ALBLUM_FA.get(eleType),
                                        constant.MAP_ELETYPE_ATTR_CONTAINER.get(eleType))
                isrecal = True
        return isrecal

    def recalAttr(self):
        #图鉴
        for eleType in constant.ALL_ELE_TYPE:
            total = {}
            eleTypeNum = self.getAlbumNum(eleType)
            for albumRes in Game.res_mgr.res_type_petalbum.get(eleType, []):
                if albumRes.need <= eleTypeNum:
                    for name, iNum in albumRes.attr.items():
                        total[name] = total.get(name, 0) + iNum
            if total:
                self.owner.attr.addAttr(total, constant.MAP_ELETYPE_ALBLUM_FA.get(eleType),
                                        constant.MAP_ELETYPE_ATTR_CONTAINER.get(eleType))

    def addNewPet(self, dAdd, reason, wLog=False):
        """添加宠物"""
        sLog_pets = ""
        resp_pets = []
        mail_pets = {}
        eventdata = {}

        isrecal = False
        for itemNo, num in dAdd.items():
            itemRes = Game.res_mgr.res_item.get(itemNo)
            if not itemRes:
                mail_pets[itemNo] = mail_pets.get(itemNo, 0) + num
                continue
            petRes = Game.res_mgr.res_pet.get(int(itemRes.arg1))
            if not petRes:
                mail_pets[itemNo] = mail_pets.get(itemNo, 0) + num
                continue

            free = self.size - len(self.all_pets)
            if free >= num:
                iAdd = num
            else:
                iAdd = free
                mail_pets[itemNo] = mail_pets.get(itemNo, 0) + (num - free)
            for i in range(iAdd):
                pet = Pet(petRes, owner=self.owner)
                pet.attr.recalAttr([constant.PET_ATTR_MODULE_ALL])
                self.all_pets[pet.id] = pet
                resp_pets.append(pet)
                # 图鉴激活
                isrecal = self.actAlbum(pet)
            #统计
            self.owner.history.petHistoryAdd(reason, {petRes.id: iAdd})
            eventdata[petRes.id] = eventdata.get(petRes.id, 0) + iAdd
            #记录日志
            if wLog:
                sLog_pets.join("@%s" % {petRes.id: iAdd})
        # 战力重算
        if isrecal:
            self.owner.attr.RecalFightAbility()
        #抛事件
        self.owner.safe_pub(msg_define.MSG_PET_ACTIVATE, eventdata)
        self.owner.safe_pub(msg_define.MSG_PET_CHANGE)
        return sLog_pets, resp_pets, mail_pets


    def checkPetMutex(self, petList):
        petList = copy.deepcopy(petList)
        #宠物互斥
        for i in range(len(petList)):
            oneId = petList.pop(0)
            pet = self.getPet(oneId)
            if not pet:
                return False
            oneFightRes = Game.res_mgr.res_pet.get(pet.resID)
            if not oneFightRes:
                return False

            for otherId in petList:
                otherpet = self.getPet(otherId)
                if not otherpet:
                    return False
                otherFightRes = Game.res_mgr.res_pet.get(otherpet.resID)
                if not otherFightRes:
                    return False
                if pet.resID in otherFightRes.mutexList or otherpet.resID in oneFightRes.mutexList:
                    return False

        return True

    def getPet(self, id):
        return self.all_pets.get(id)

    def getAllPet(self):
        return list(self.all_pets.values())

    def getBest(self):
        """所有系的最强宠物 和 总的最强宠物"""
        best, fire, water, grass, light, dark = None, None, None, None, None, None
        for one in self.all_pets.values():
            fa = one.getPetFA()
            eleType = one.getEleType()
            # 最强宠物
            if best:
                best = one if fa > best.getPetFA() else best
            else:
                best = one
            # 火系宠物
            if eleType == constant.PKM2_ELE_TYPE_FIRE:
                if fire:
                    fire = one if fa > fire.getPetFA() else fire
                else:
                    fire = one
            # 水系宠物
            elif eleType == constant.PKM2_ELE_TYPE_WATER:
                if water:
                    water = one if fa > water.getPetFA() else water
                else:
                    water = one
            # 草系宠物
            elif eleType == constant.PKM2_ELE_TYPE_GRASS:
                if grass:
                    grass = one if fa > grass.getPetFA() else grass
                else:
                    grass = one
            # 光系宠物
            elif eleType == constant.PKM2_ELE_TYPE_LIGHT:
                if light:
                    light = one if fa > light.getPetFA() else light
                else:
                    light = one
            # 暗系宠物
            elif eleType == constant.PKM2_ELE_TYPE_DARK:
                if dark:
                    dark = one if fa > dark.getPetFA() else dark
                else:
                    dark = one
        resp = {
            constant.PKM2_ELE_TYPE_NONE: best,
            constant.PKM2_ELE_TYPE_WATER: water,  # 水
            constant.PKM2_ELE_TYPE_GRASS: grass, # 草
            constant.PKM2_ELE_TYPE_FIRE: fire, # 火
            constant.PKM2_ELE_TYPE_LIGHT: light, # 光
            constant.PKM2_ELE_TYPE_DARK: dark, # 暗
        }
        return resp


    def getFightPet(self, iType):
        """获取出战宠物数据"""
        fightList = []
        arrayobj = self.owner.battle_array.getBattleArray(iType)

        for one in arrayobj.position:
            data = []
            for uid in one.values():
                pet = self.all_pets.get(uid)
                if pet:
                    data.append(pet)
            fightList.append(data)
        return fightList


    def getCostPet(self, costPet, need1, need2):
        for uid in costPet:
            pet = self.getPet(uid)
            if not pet:
                continue
            if pet.isInBattle():  #已上阵 或 锁定的宠物不选中
                return False, 3
            if pet.isLock(): #已上阵 或 锁定的宠物不选中
                return False, 3
            if pet.isWearSomething(): #宠物身上有装备，有各种物品时不可消耗
                return False, 2

        cost = copy.deepcopy(costPet)
        #指定宠物id消耗
        for resID, star, num in need1:
            iNeed = num
            del1 = []
            for uid in cost:
                pet = self.getPet(uid)
                if not pet:
                    continue
                res = Game.res_mgr.res_pet.get(pet.resID)
                if not res:
                    continue
                evolveRes = Game.res_mgr.res_idlv_petevolve.get((pet.resID, pet.evolveLv))
                if not evolveRes:
                    continue
                if res.id == resID and evolveRes.showStar == star:
                    iNeed -= 1
                    del1.append(uid)
                    if iNeed <= 0:
                        break
            for uid in del1:
                cost.remove(uid)
            if iNeed != 0:
                return False, 1
        #某系宠物消耗
        for eleType, star, num in need2:
            iNeed = num
            del2 = []
            for uid in cost:
                pet = self.getPet(uid)
                if not pet:
                    continue
                res = Game.res_mgr.res_pet.get(pet.resID)
                if not res:
                    continue
                evolveRes = Game.res_mgr.res_idlv_petevolve.get((pet.resID, pet.evolveLv))
                if not evolveRes:
                    continue
                if res.eleType == eleType and evolveRes.showStar == star:
                    iNeed -= 1
                    del2.append(uid)
                    if iNeed <= 0:
                        break
            for uid in del2:
                cost.remove(uid)
            if iNeed != 0:
                return False, 1
        # code 1=没有足够的宠物， 2=宠物身上有装备，有各种物品时不可消耗  3=宠物已出战
        return True, 0


    def costPet(self, reason, del_pets, wLog=False):
        sLog_pet = ""
        dCost = {}
        backAdd = {} #计算需要返还的材料
        for uid in del_pets:
            pet = self.all_pets.pop(uid, None)
            if pet:
                dCost[pet.resID] = dCost.get(pet.resID, 0) + 1
                dBack = pet.costBack()
                for k, v in dBack.items():
                    backAdd[k] = backAdd.get(k, 0) + v
                if wLog:
                    sLog_pet.join("@%s"% pet.to_save_dict())
        self.markDirty()
        #统计
        self.owner.history.petHistoryCost(reason, dCost)
        #记录消耗日志
        if wLog:
            sLog = ""
            sLog.join("#pet@%s_%s" % (dCost, sLog_pet))
            Game.glog.log2File("pet_cost", "%s|%s|%s" % (self.owner.id, reason, sLog))

        #宠物变化
        self.owner.safe_pub(msg_define.MSG_PET_CHANGE)
        #计算需要返还的材料
        return backAdd

    def to_fight_data(self, battletype):
        resp = []

        battle_array = self.owner.battle_array.getBattleArray(battletype)
        position = battle_array.getPosition()

        for one in position:
            data = {}
            for pos, uid in one.items():
                pet = self.all_pets.get(uid)
                if pet:
                    data[pos] = pet.to_fight_data(battletype)
            resp.append(data)
        return resp




