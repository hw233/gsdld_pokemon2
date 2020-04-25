#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from corelib.frame import Game
from game.define import constant

class AttributeContainerBase(object):
    """属性容器"""
    def __init__(self, owner, attr):
        self.owner = owner

        #客户端展示属性
        self.hp = attr.get("hp", 0) #生命
        self.maxHP = max(attr.get("maxHP", 0), self.hp) #最大血量
        self.shield = attr.get("shield", 0) #初始护盾
        self.maxShield = max(attr.get("maxShield", 0), self.shield)  # 最大护盾
        self.mp = attr.get("mp", 0) #初始魔法值
        self.maxMP = max(attr.get("maxMP", 0), self.mp)  # 最大魔法值

        #计算属性
        self.atk = attr.get("atk", 0) #攻击
        self.defe = attr.get("defe", 0) #防御
        self.speed = attr.get("speed", 0) #速度
        self.hit = attr.get("hit", 0) #命中
        self.miss = attr.get("miss", 0) #闪避
        self.cirt = attr.get("cirt", 0) #暴击
        self.cirtSub = attr.get("cirtSub", 0) #抗暴
        self.hitRate = attr.get("hitRate", 0) #命中率 万分比
        self.missRate = attr.get("missRate", 0) #闪避率 万分比
        self.cirtRate = attr.get("cirtRate", 0) #暴击率 万分比
        self.cirtSubRate = attr.get("cirtSubRate", 0) #抗暴率 万分比
        self.cirtDamRate = attr.get("cirtDamRate", 0) #暴击伤害附加 万分比
        self.cirtDamSubRate = attr.get("cirtDamSubRate", 0) #暴击伤害减免 万分比
        self.phyAddRate = attr.get("phyAddRate", 0) #物伤加深 万分比
        self.phySubRate = attr.get("phySubRate", 0) #物伤减免 万分比
        self.magicAddRate = attr.get("magicAddRate", 0) #法伤加深 万分比
        self.magicSubRate = attr.get("magicSubRate", 0) #法伤减免 万分比
        self.damAddRate = attr.get("damAddRate", 0) #伤害加深 万分比
        self.damSubRate = attr.get("damSubRate", 0) #伤害减免 万分比
        self.abnormalRate = attr.get("abnormalRate", 0) #异常成功率 万分比
        self.abnormalSubRate = attr.get("abnormalSubRate", 0) #异常抗性 万分比
        self.unDefRate = attr.get("unDefRate", 0) #无视防御率 万分比
        self.damAdd = attr.get("damAdd", 0) #附加伤害
        self.damSub = attr.get("damSub", 0) #附加伤害减免
        self.realDam = attr.get("realDam", 0) #纯粹伤害
        self.hpRecover = attr.get("hpRecover", 0) #生命回复
        self.vampireRate = attr.get("vampireRate", 0) #吸血率 万分比
        self.luck = attr.get("luck", 0) #幸运值
        self.skDamRate = attr.get("skDamRate", 0) #技能伤害加深 万分比
        self.skDamSubRate = attr.get("skDamSubRate", 0) #技能伤害减免 万分比
        self.pvpDamRate = attr.get("pvpDamRate", 0) #pvp伤害加成 万分比
        self.pvpDamSubRate = attr.get("pvpDamSubRate", 0) #pvp伤害减免 万分比
        self.pveDamRate = attr.get("pveDamRate", 0) #pve伤害加成 万分比
        self.pveDamSubRate = attr.get("pveDamSubRate", 0) #pve伤害减免 万分比

        self.grassAddition = attr.get("grassAddition", 0)  # 草系增伤 万分比
        self.waterAddition = attr.get("waterAddition", 0)  # 水系增伤 万分比
        self.fireAddition = attr.get("fireAddition", 0)  # 火系增伤 万分比
        self.lightAddition = attr.get("lightAddition", 0)  # 光系增伤 万分比
        self.darkAddition = attr.get("darkAddition", 0)  # 暗系增伤 万分比
        self.grassSub = attr.get("grassSub", 0)  # 草系伤减 万分比
        self.waterSub = attr.get("waterSub", 0)  # 水系伤减 万分比
        self.fireSub = attr.get("fireSub", 0)  # 火系伤减 万分比
        self.lightSub = attr.get("lightSub", 0)  # 光系伤减 万分比
        self.darkSub = attr.get("darkSub", 0)  # 暗系伤减 万分比
        self.TreatRate = attr.get("TreatRate", 0)  # 治疗效果加成 万分比
        self.beTreatRate = attr.get("beTreatRate", 0)  # 受治疗效果加成 万分比

        #加成类
        self.hpRate = attr.get("hpRate", 0)  # 生命加成 万分比
        self.atkRate = attr.get("atkRate", 0)  # 攻击加成 万分比
        self.defeRate = attr.get("defeRate", 0)  # 防御加成 万分比
        self.speedRate = attr.get("speedRate", 0)  # 速度加成 万分比

class DirtyAttributeContainer(AttributeContainerBase):
    """属性容器"""
    def __init__(self, owner):
        super(DirtyAttributeContainer, self).__init__(owner, {})
        self.dirty_data = {}

    def package(self):
        resp = {}
        for name in constant.ALL_ATTR:
            iCurNum = getattr(self, name, 0)
            if iCurNum:
                resp[name] = iCurNum
        return resp

    def packageList(self):
        resp = []
        for name in constant.ALL_ATTR:
            iCurNum = getattr(self, name, 0)
            resp.append(iCurNum)
        return resp

    def addAttr(self, data):
        for name, iNum in data.items():
            iCurNum = getattr(self, name, 0)
            setattr(self, name, int(iCurNum + iNum))
            self.dirty_data[name] = 1

    def delAttr(self, data):
        for name, iNum in data.items():
            iCurNum = getattr(self, name, 0)
            setattr(self, name, int(iCurNum - iNum))
            self.dirty_data[name] = 1

    def resetAttr(self, data):
        for name, iNum in data.items():
            setattr(self, name, iNum)
            self.dirty_data[name] = 1

    def packDirty(self):
        resp = {}
        for name in self.dirty_data.keys():
            iCurNum = getattr(self, name, 0)
            if iCurNum:
                resp[name] = iCurNum
        self.dirty_data = {}
        return resp

    def isDirty(self):
        return self.dirty_data == {}


class FaAttributeContainer(DirtyAttributeContainer):
    """战力属性容器"""
    def __init__(self, owner, is_recal=1):
        super(FaAttributeContainer, self).__init__(owner)

        self.fa = 0
        self.is_recal = is_recal

    def addAttr(self, data):
        super(FaAttributeContainer, self).addAttr(data)
        if data:
            self.recalFa()

    def delAttr(self, data):
        super(FaAttributeContainer, self).delAttr(data)
        if data:
            self.recalFa()

    def resetAttr(self, data):
        super(FaAttributeContainer, self).resetAttr(data)
        if data:
            self.recalFa()

    def recalFa(self):
        if not self.is_recal:
            return False
        self.fa = 0
        for name in constant.ALL_ATTR:
            res = Game.res_mgr.res_attrbute.get(name)
            if res and res.ratio:
                iCurNum = getattr(self, name, 0)
                self.fa += int(iCurNum * res.ratio / 10000)
        return True
