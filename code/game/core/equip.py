#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import random

from game.core.item import ItemBase

from game.define.constant import *
from corelib.frame import Game
from game.common import utility
from random import sample
from collections import OrderedDict
import copy

#装备基类
class EquipBase(ItemBase):
    def __init__(self, res, data=None, owner=None):
        ItemBase.__init__(self, res, data=data, owner=owner)

#角色装备
class Equip(EquipBase):
    def __init__(self, res, data=None, owner=None):
        EquipBase.__init__(self, res, data=data, owner=owner)

    def getAttr(self):
        equipRes = Game.res_mgr.res_equip.get(self.id)
        return equipRes.attr


#角色法宝
# 法宝id(id, int)
# 法宝uid(uid, string)
# 	客户端判断这个字段是否新增
# 锻造者名称(maker, string)
# 是否锁定(isLock, int)0=不锁定 1=锁定
# 数量(num, int)0代表删除
class FaBao(EquipBase):
    def __init__(self, res, data=None, owner=None):
        self.maker = ""
        self.isLock = 0

        EquipBase.__init__(self, res, data=data, owner=owner)

    def to_save_dict(self, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            EquipBase.to_save_dict(self, forced=forced)
            self.save_cache["maker"] = self.maker
            self.save_cache["isLock"] = self.isLock
        return self.save_cache

    # 读库数据初始化
    def load_from_dict(self, data):
        EquipBase.load_from_dict(self, data)
        self.maker = data.get("maker", "")  # 锻造者名称
        self.isLock = data.get("isLock", 0)  # 是否锁定

    # 登录初始化下发数据
    def to_init_data(self, iNum=None):
        init_data = EquipBase.to_init_data(self, iNum=iNum)
        init_data["maker"] = self.maker
        init_data["isLock"] = self.isLock
        return init_data

    def SetLockStatus(self, st):
        self.isLock = st
        self.markDirty()

    def SetMaker(self, name):
        self.maker = name
        self.markDirty()

    def getSkillAddAttr(self, skillLv):
        resp = {}
        fabaoRes = Game.res_mgr.res_equip.get(self.id)
        if not fabaoRes:
            return resp
        for skillNo in fabaoRes.skills:
            skillRes = Game.res_mgr.res_skill.get(skillNo)
            if not skillRes:
                continue
            #没有技能效果的才是属性加成技能
            if skillRes.effectId:
                continue
            # 法宝的技能等级是根据部位等级来的
            skillRes = Game.res_mgr.res_idlv_skill.get((skillRes.skillId, skillLv))
            if not skillRes:
                continue
            if not skillRes.args or len(skillRes.args) != 2:
                continue
            attr, val =  skillRes.args[0], int(skillRes.args[1])
            if attr in resp:
                resp[attr] += val
            else:
                resp[attr] = val
        return resp


#角色神装
class GodEquip(EquipBase):
    def __init__(self, res, data=None, owner=None):
        self.jpAttr = OrderedDict()
        self.step = 0
        self.upStepFailTimes = 0

        baseAttrRes = Game.res_mgr.res_common.get("GodEquipBaseAttrValue")
        randomAttrList = sample(GOD_EQUIP_ATTR, 3)
        self.jpAttr = OrderedDict(list(zip(randomAttrList, [baseAttrRes.i]*3)))

        EquipBase.__init__(self, res, data=data, owner=owner)


    def to_save_dict(self, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            EquipBase.to_save_dict(self, forced=forced)
            self.save_cache["jpAttr"] = self.jpAttr
            self.save_cache["step"] = self.step
            self.save_cache["upStepFailTimes"] = self.upStepFailTimes

        return self.save_cache

    def load_from_dict(self, data):
        EquipBase.load_from_dict(self, data)
        self.jpAttr = data.get("jpAttr", {})
        self.step = data.get("step", 0)
        self.upStepFailTimes = data.get("upStepFailTimes", 0)

    def to_init_data(self, iNum=None):
        init_data = EquipBase.to_init_data(self, iNum=iNum)

        init_data["jpAttr"] = []
        for k, v in self.jpAttr.items():
            init_data["jpAttr"].append({
                "attr": k,
                "per": v,
             })
        init_data["step"] = self.step
        init_data["upStepFailTimes"] = self.upStepFailTimes
        return init_data

    def getAttr(self):
        equipRes = Game.res_mgr.res_equip.get(self.id)
        attr = copy.deepcopy(equipRes.attr)

        for k, v in self.jpAttr.items():
            godAttr = int(v * equipRes.godAttr.get(k, 0) / 10000)
            if k in attr:
                attr[k] += godAttr
            else:
                attr[k] = godAttr

        return attr

    def upgrade(self, newResId):
        # 减掉旧装备极品属性
        self.ownerMode.owner.attr.delAttr(self.getAttr(), FIGHTABILITY_TYPE_15)
        self.id = newResId

        # 加上新装备极品属性
        self.ownerMode.owner.attr.addAttr(self.getAttr(), FIGHTABILITY_TYPE_15)

    def rebuildJpAttr(self):
        # 随机新的属性列表
        randomAttrList = sample(GOD_EQUIP_ATTR, len(self.jpAttr))
        # 减掉旧属性
        self.ownerMode.owner.attr.delAttr(self.getAttr(), FIGHTABILITY_TYPE_15)

        oldValues = list(self.jpAttr.values())   # 旧的极品属性数值
        newAttrPer = OrderedDict(list(zip(randomAttrList, oldValues)))
        self.jpAttr = newAttrPer
        # 加上新属性
        self.ownerMode.owner.attr.addAttr(self.getAttr(), FIGHTABILITY_TYPE_15)
        self.markDirty()

    def updateJpAttr(self, attr):
        self.ownerMode.owner.attr.delAttr(self.getAttr(), FIGHTABILITY_TYPE_15)

        for k, v in attr.items():
            if k in self.jpAttr:
                self.jpAttr[k] = self.jpAttr.get(k, 0) + v
                if self.jpAttr[k] > 10000:
                    self.jpAttr[k] = 10000
            else:
                self.jpAttr[k] = v

        self.ownerMode.owner.attr.addAttr(self.getAttr(), FIGHTABILITY_TYPE_15)
        self.markDirty()

    def getUpStepFailTimes(self):
        return self.upStepFailTimes

    def setUpStepFailTimes(self, times):
        self.upStepFailTimes = times
        self.markDirty()

    def getStep(self):
        return self.step

    def setStep(self, step):
        self.step = step
        self.markDirty()

    def getCouldXiLianAttr(self):
        attrList = []
        for k, v in self.jpAttr.items():
            if v < 10000:
                attrList.append(k)

        return attrList

#异兽之灵
class YiShouEquip(EquipBase):
    def __init__(self, res, data=None, owner=None):
        self.addlv = 0  #强化等级
        self.lock = 0 #锁定
        self.waste = 0 #是否弃置
        self.dicnum = 0 #强化次数-定向
        self.gongmingid = [0,0,0] #共鸣id 0代表无属性
        self.gongmingpet = [0,0,0] #共鸣的宠物id 0无需绑定宠物
        self.gongmingidBak = [0,0,0] #共鸣id 0代表无属性 候选
        self.gongmingpetBak = [0,0,0] #共鸣的宠物id 0无需绑定宠物 候选
        
        self.mainAttrData = {} #主属性 {属性id：[强化等级, 继承比例]}
        self.viceAttrData = {}  # 副属性 {属性id：[强化等级, 继承比例]}
        # self.petid=0 # 现在穿在哪个宠物id上

        self.mainAttr = [] # [{"hp":100}]
        self.viceAttr = []  # [{"hp":100}]
        self.gongmingAttr = []  # [{"hp":100}]

        if not data:
            #主属性
            attrId = utility.Choice(res.mainPool)
            self.mainAttrData[attrId] = [0, 1000]
            #副属性
            viceNum = utility.Choice(res.viceNum)
            vicePool = copy.deepcopy(res.vicePool)
            for i in range(viceNum):
                one = utility.ChoiceReturn(vicePool)
                attrId = one[0]
                vicePool.remove(one)
                viceRate = random.randint(850, 1000) #属性在85% ~ 100%随机
                self.viceAttrData[attrId] = [1, viceRate]

        EquipBase.__init__(self, res, data=data, owner=owner)

        #计算出属性
        for attrId, data in self.mainAttrData.items():
            attrRes = Game.res_mgr.res_petEquipAttr.get(attrId)
            if attrRes:
                self.mainAttr.append({attrRes.attrType: attrRes.baseVal + int(attrRes.addVal*data[0]*data[1]/1000)})

        for attrId, data in self.viceAttrData.items():
            attrRes = Game.res_mgr.res_petEquipAttr.get(attrId)
            if attrRes:
                self.viceAttr.append({attrRes.attrType: int(attrRes.baseVal*data[0]*data[1]/1000)})


        for idx in range(3):
            ridx=self.gongmingid[idx]
            if not ridx:
                continue

            bid = self.gongmingpet[idx]
            if bid:
                continue
            attrRes = Game.res_mgr.res_shoulinggongming.get(idx)
            if attrRes:
                self.gongmingAttr.append(attrRes.attr)

    def to_save_dict(self, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            EquipBase.to_save_dict(self, forced=forced)
            self.save_cache["addlv"] = self.addlv #强化等级
            self.save_cache["lock"] = self.lock  # 锁定
            self.save_cache["waste"] = self.waste  # 是否弃置
            self.save_cache["dicnum"] = self.dicnum  # 强化次数
            self.save_cache["gongmingid"] = self.gongmingid  # 共鸣id 0代表无属性
            self.save_cache["gongmingpet"] = self.gongmingpet  # 共鸣的宠物id 0无需绑定宠物
            self.save_cache["gongmingidBak"] = self.gongmingidBak  # 共鸣id 0代表无属性 候选
            self.save_cache["gongmingpetBak"] = self.gongmingpetBak  # 共鸣的宠物id 0无需绑定宠物 候选
            # self.save_cache["petid"] = self.petid  # 

            self.save_cache["mainAttrData"] = []
            for attrId, data in self.mainAttrData.items():
                self.save_cache["mainAttrData"].append({"attrId":attrId, "data":data})

            self.save_cache["viceAttrData"] = []
            for attrId, data in self.viceAttrData.items():
                self.save_cache["viceAttrData"].append({"attrId":attrId, "data":data})

        return self.save_cache

    def load_from_dict(self, data):
        EquipBase.load_from_dict(self, data)
        self.addlv = data.get("addlv", 0) #强化等级
        self.lock = data.get("lock", 0)  # 锁定
        self.waste = data.get("waste", 0)  # 是否弃置
        self.dicnum = data.get("dicnum", 0)  # 强化次数
        self.gongmingid = data.get("gongmingid", [0,0,0])  # 共鸣id 0代表无属性
        self.gongmingpet = data.get("gongmingpet", [0,0,0])  # 共鸣的宠物id 0无需绑定宠物
        self.gongmingidBak = data.get("gongmingidBak", [0,0,0])  # 共鸣id 0代表无属性 候选
        self.gongmingpetBak = data.get("gongmingpetBak", [0,0,0])  # 共鸣的宠物id 0无需绑定宠物 候选
        # self.petid = data.get("petid", 0)  # 共鸣的宠物id 0无需绑定宠物 候选

        mainAttrData = data.get("mainAttrData", [])
        for one in mainAttrData:
            attrId = one.get("attrId", 0)
            _data = one.get("data", [])
            if attrId and _data:
                self.mainAttrData[attrId] = _data

        viceAttrData = data.get("viceAttrData", [])
        for one in viceAttrData:
            attrId = one.get("attrId", 0)
            _data = one.get("data", [])
            if attrId and _data:
                self.viceAttrData[attrId] = _data


    def to_init_data(self, iNum=None):
        init_data = EquipBase.to_init_data(self, iNum=iNum)
        init_data["addlv"] = self.addlv
        init_data["lock"] = self.lock
        init_data["waste"] = self.waste
        init_data["dicnum"] = self.dicnum
        init_data["gongmingid"] = self.gongmingid
        init_data["gongmingpet"] = self.gongmingpet
        init_data["gongmingidBak"] = self.gongmingidBak
        init_data["gongmingpetBak"] = self.gongmingpetBak
        init_data["mainAttr"] = self.mainAttr
        init_data["viceAttr"] = self.viceAttr
        init_data["gongmingAttr"] = self.gongmingAttr

        # print("====to_init_data====",init_data["gongmingid"],init_data["gongmingpet"],init_data["gongmingAttr"])
        return init_data

    def Lock(self):
        self.lock = 1
        self.markDirty()

    def UnLock(self):
        self.lock = 0
        self.markDirty()

    def setWaste(self):
        self.waste = 1
        self.markDirty()

    def UnSetWaste(self):
        self.waste = 0
        self.markDirty()

    def resetMainAttr(self, attrId):
        self.mainAttrData = {}  # 主属性 {属性id：[强化等级, 继承比例]}
        self.mainAttr = []  # [{"hp":100}]

        self.mainAttrData[attrId] = [0, 1000]
        #计算出属性
        for attrId, data in self.mainAttrData.items():
            attrRes = Game.res_mgr.res_petEquipAttr.get(attrId)
            if attrRes:
                self.mainAttr.append({attrRes.attrType: attrRes.baseVal + int(attrRes.addVal*data[0]*data[1]/1000)})
        self.markDirty()


    def usegongming(self,idx):
        if self.gongmingidBak[idx]:
            self.gongmingid[idx]=self.gongmingidBak[idx]
            self.gongmingpet[idx]=self.gongmingpetBak[idx]

            self.gongmingidBak[idx]=0
            self.gongmingpetBak[idx]=0

            self.markDirty()

        self.gongmingAttr = []
        for idx in range(3):
            ridx=self.gongmingid[idx]
            if not ridx:
                continue

            bid = self.gongmingpet[idx]
            if bid:
                continue
            attrRes = Game.res_mgr.res_shoulinggongming.get(idx)
            if attrRes:
                self.gongmingAttr.append(attrRes.attr)

    def setgongming(self, petid):
        # self.petid=petid

        # self.gongmingAttr = []
        # for idx in range(3):
        #     ridx=self.gongmingid[idx]
        #     if not ridx:
        #         continue

        #     bid = self.gongmingpet[idx]
        #     if bid:
        #         if bid!=self.petid:
        #             continue
        #     attrRes = Game.res_mgr.res_shoulinggongming.get(idx)
        #     if attrRes:
        #         self.gongmingAttr.append(attrRes.attr)


        self.markDirty()

    def gongming(self,idx,cid,bindpet):
        self.gongmingidBak[idx]=cid
        self.gongmingpetBak[idx]=bindpet
        self.markDirty()
        

    def UpgradeDir(self,attrType,addvice):
        # print("========================")
        res = Game.res_mgr.res_petEquip.get(self.id)
        if not res:
            return
        
        # print("----------------")
        
        self.addlv += 1


        #self.mainAttrData = {}  # 主属性 {属性id：[强化等级, 继承比例]}
        keys = list(self.mainAttrData.keys())
        for key in keys:
            attrData = self.mainAttrData[key]
            lv = attrData[0] + 1
            rate = attrData[1]
            self.mainAttrData[key] = [lv, rate]

        #self.viceAttrData = {}  # 副属性 {属性id：[强化等级, 继承比例]}
        #增加副属性条数

        if addvice:

            found=False
            for attrId,attrData in self.viceAttrData.items():
                attrRes = Game.res_mgr.res_petEquipAttr.get(attrId)
                if attrRes.attrType==attrType:
                    found=True

                    lv = attrData[0] + 1
                    rate = int((attrData[1] + random.randint(850, 1000))/2)
                    self.viceAttrData[attrId] = [lv, rate]
                    # print("!!!!!!!!!!!!!!!",self.viceAttrData[attrId])
                    break
            
            if not found:

                attrId=0
                for k,v in Game.res_mgr.res_petEquipAttr.items():
                    if v.vice and v.q==res.quality and v.attrType==attrType:
                        attrId=k
                        break
                
                if attrId:
                    lv = 1
                    rate = random.randint(850, 1000)  # 属性在75% ~ 100%随机
                    self.viceAttrData[attrId] = [lv, rate]
                    # print("============",self.viceAttrData[attrId])


        
 

        self.mainAttr = []  # [{"hp":100}]
        self.viceAttr = []  # [{"hp":100}]

        # 计算出属性
        for attrId, data in self.mainAttrData.items():
            attrRes = Game.res_mgr.res_petEquipAttr.get(attrId)
            if attrRes:
                self.mainAttr.append({attrRes.attrType: attrRes.baseVal + int(attrRes.addVal * data[0] * data[1] / 1000)})

        for attrId, data in self.viceAttrData.items():
            attrRes = Game.res_mgr.res_petEquipAttr.get(attrId)
            if attrRes:
                self.viceAttr.append({attrRes.attrType: int(attrRes.baseVal * data[0] * data[1] / 1000)})



        self.markDirty()

    def Upgrade(self):
        res = Game.res_mgr.res_petEquip.get(self.id)
        if not res:
            return
        upRes = Game.res_mgr.res_qalv_petEquipUpgrade.get((res.quality, self.addlv + 1))
        if not upRes:
            return

        self.addlv += 1

        #self.mainAttrData = {}  # 主属性 {属性id：[强化等级, 继承比例]}
        keys = list(self.mainAttrData.keys())
        for key in keys:
            attrData = self.mainAttrData[key]
            lv = attrData[0] + 1
            rate = attrData[1]
            self.mainAttrData[key] = [lv, rate]

        #self.viceAttrData = {}  # 副属性 {属性id：[强化等级, 继承比例]}
        #增加副属性条数
        for i in range(upRes.viceAdd):
            # 4条以下
            if len(self.viceAttrData) < 4:
                vicePool = copy.deepcopy(res.vicePool)
                attrId = utility.Choice(vicePool)
                #相同属性
                if attrId in self.viceAttrData:
                    attrData = self.viceAttrData[attrId]
                    lv = attrData[0] + 1
                    rate = int((attrData[1] + random.randint(850, 1000))/2)
                    self.viceAttrData[attrId] = [lv, rate]
                else:
                    lv = 1
                    rate = random.randint(850, 1000)  # 属性在75% ~ 100%随机
                    self.viceAttrData[attrId] = [lv, rate]
            #4条及以上 只从当前4条内随机
            else:
                viceKeys = list(self.viceAttrData.keys())
                attrId = random.choice(viceKeys)
                attrData = self.viceAttrData[attrId]
                lv = attrData[0] + 1
                rate = int((attrData[1] + random.randint(850, 1000)) / 2)
                self.viceAttrData[attrId] = [lv, rate]

        self.mainAttr = []  # [{"hp":100}]
        self.viceAttr = []  # [{"hp":100}]

        # 计算出属性
        for attrId, data in self.mainAttrData.items():
            attrRes = Game.res_mgr.res_petEquipAttr.get(attrId)
            if attrRes:
                self.mainAttr.append({attrRes.attrType: attrRes.baseVal + int(attrRes.addVal * data[0] * data[1] / 1000)})

        for attrId, data in self.viceAttrData.items():
            attrRes = Game.res_mgr.res_petEquipAttr.get(attrId)
            if attrRes:
                self.viceAttr.append({attrRes.attrType: int(attrRes.baseVal * data[0] * data[1] / 1000)})

        self.markDirty()


Map_equip_type = {
    EQUIP_TYPE_EQUIP : Equip,  # 2=装备
    EQUIP_TYPE_FABAO : FaBao,  # 3=法宝
    EQUIP_TYPE_SHENZHUANG : GodEquip,  # 16=人物神装
    EQUIP_TYPE_YISHOU : YiShouEquip, # 17=异兽之灵
}

def CreatEquip(equipNo, data=None, owner=None):
    if YISHOU_EQUIP_START_NO <= equipNo <= YISHOU_EQUIP_END_NO:
        res = Game.res_mgr.res_petEquip.get(equipNo)
        equipCls = YiShouEquip
    else:
        res = Game.res_mgr.res_equip.get(equipNo)
        equipCls = Map_equip_type.get(res.type)
    if not res:
        return None, None
    if not equipCls:
        return None, None
    equipobj = equipCls(res, data=data, owner=owner)
    return res, equipobj