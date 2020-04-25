#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import uuid

from corelib.frame import Game

from corelib.message import observable
from game.core.attributeContainer import AttributeContainerBase
from game.define import constant, msg_define

from game.fight.skill import FightSkill

class FighterAttribute(AttributeContainerBase):
    def __init__(self, owner, attr):
        super(FighterAttribute, self).__init__(owner, attr)

        #战斗MVP计算
        self.total_hurt = 0  #总输出
        self.total_behurt = 0 #总承受伤害

        #单次攻击临时附加属性
        self.temp_attr = {}

        self.fa = 0 #战斗力
        self.recalFa()

    def getHP(self):
        return self.hp

    def delHP(self, n):
        self.hp -= n
        if self.hp <= 0:
            self.owner.safe_pub(msg_define.MSG_FIGHT_WILL_DEAD)
        return self.getHP()

    def getMaxHP(self):
        return self.maxHP

    def getAtk(self):
        atk = self.atk #基础
        atk += self.temp_attr.get(constant.ATTR_ATK, 0) #单次攻击临时附加
        return atk

    def getDefe(self):
        defe = self.defe #基础
        defe += self.temp_attr.get(constant.ATTR_DEFE, 0) #单次攻击临时附加
        return defe

    def getSpeed(self):
        return self.speed

    def getUnDefRate(self):
        # 无视防御率 万分比
        unDefRate = self.unDefRate #基础
        return unDefRate

    def getHit(self):
        # 命中
        hit = self.hit #基础
        return hit

    def getHitRate(self):
        # 命中率 万分比
        hitRate = self.hitRate #基础
        return hitRate

    def getMiss(self):
        # 闪避
        miss = self.miss #基础
        return miss

    def getMissRate(self):
        # 闪避率 万分比
        missRate = self.missRate #基础
        return missRate

    def getCirt(self):
        # 暴击
        cirt = self.cirt  # 基础
        return cirt

    def getCirtRate(self):
        # 暴击率 万分比
        cirtRate = self.cirtRate  # 基础
        return cirtRate

    def getCirtSub(self):
        # 抗暴
        cirtSub = self.cirtSub  # 基础
        return cirtSub

    def getCirtSubRate(self):
        # 抗暴率 万分比
        cirtSubRate = self.cirtSubRate  # 基础
        return cirtSubRate

    def getSkDamRate(self):
        # 技能伤害加深 万分比
        skDamRate = self.skDamRate #基础
        return skDamRate

    def getSkDamSubRate(self):
        # 技能伤害减免 万分比
        skDamSubRate = self.skDamSubRate #基础
        return skDamSubRate

    def getDamAdd(self):
        # 附加伤害
        damAdd = self.damAdd #基础
        return damAdd

    def getDamSub(self):
        # 附加伤害减免
        damSub = self.damSub #基础
        return damSub

    def getRealDam(self):
        # 纯粹伤害
        realDam = self.realDam #基础
        return realDam

    def getPvpDamRate(self):
        # pvp伤害加成 万分比
        pvpDamRate = self.pvpDamRate #基础
        return pvpDamRate

    def getPvpDamSubRate(self):
        # pvp伤害减免 万分比
        pvpDamSubRate = self.pvpDamSubRate #基础
        return pvpDamSubRate

    def getPveDamRate(self):
        # pve伤害加成 万分比
        pveDamRate = self.pveDamRate #基础
        return pveDamRate

    def getPveDamSubRate(self):
        # pve伤害减免 万分比
        pveDamSubRate = self.pveDamSubRate #基础
        return pveDamSubRate

    def getCirtDamRate(self):
        # 暴击伤害附加 万分比
        cirtDamRate = self.cirtDamRate #基础
        return cirtDamRate

    def getCirtDamSubRate(self):
        # 暴击伤害减免 万分比
        cirtDamSubRate = self.cirtDamSubRate #基础
        return cirtDamSubRate

    def getTreatRate(self):
        # 治疗效果加成 万分比
        TreatRate = self.TreatRate #基础
        return TreatRate

    def getBeTreatRate(self):
        # 受治疗效果加成 万分比
        beTreatRate = self.beTreatRate #基础
        return beTreatRate

    def to_client(self):
        resp = []
        resp.append(self.hp)
        resp.append(self.maxHP)
        resp.append(self.shield)
        resp.append(self.maxShield)
        resp.append(self.mp)
        resp.append(self.maxMP)
        return resp

    def recalFa(self):
        self.fa = 0
        for name in constant.ALL_ATTR:
            res = Game.res_mgr.res_attrbute.get(name)
            if res and res.ratio:
                iCurNum = getattr(self, name, 0)
                self.fa += int(iCurNum * res.ratio / 10000)

class FighterBuff(object):
    def __init__(self, owner):
        self.owner = owner

        self.attr_buffs = {}

    def cleanAll(self):
        #清除所有buff
        self.attr_buffs = {}

    def event_do(self, msgCode, log_actions):
        pass

    def cal_life_round(self, log_actions):
        #计算回合生命周期
        pass

    def has_buff(self, buff_id):
        pass


class FighterStatus(object):
    def __init__(self, owner):
        self.owner = owner

        self.is_dead = 0 #是否死亡
        self.first_round = 0 #优先行动回合
        self.action_status = 0 #0=等待 1=行动中
        self.frozen = 0 #冰冻
        self.dizzy = 0 #晕眩
        self.sleeping = 0 #沉睡
        self.silence = 0 #沉默
        self.weak = 0 #虚弱
        self.sneer = 0 #嘲讽
        self.chaos = 0 #混乱
        self.alienation = 0 #离间

    def isFrozen(self):
        # 冰冻
        return self.frozen == 1 #or self.frozen1 == 1

    def isDizzy(self):
        # 晕眩
        return self.dizzy == 1 #or self.dizzy1 == 1

    def isSleeping(self):
        # 沉睡
        return self.sleeping == 1 #or self.sleeping1 == 1

    def isSilence(self):
        # 沉默
        return self.silence == 1 #or self.silence1 == 1

    def isWeak(self):
        # 虚弱
        return self.weak == 1 #or self.weak1 == 1

    def isSneer(self):
        # 嘲讽
        return self.sneer == 1 #or self.sneer1 == 1

    def isChaos(self):
        #混乱
        return self.chaos == 1

    def isAlienation(self):
        #离间
        return self.alienation == 1

    def hard_control(self):
        return self.isFrozen() or self.isDizzy() or self.isSleeping()

    def soft_control(self):
        return self.isSilence() or self.isChaos() or self.isAlienation()


class FighterSkill(object):
    def __init__(self, owner, normal, skills, peculiarity):
        self.owner = owner

        self.cd = {} #技能cd

        self.normal = None  #普攻
        self.active_skills = [] #主动技能
        self.passive_skills = [] #被动技能
        self.peculiarity = [] #特性技能

        #连协技能

        # 兽灵技能

        # 百变怪技能

        self.init(normal, skills, peculiarity)

    def init(self, normal, skills, peculiarity):
        skillRes = Game.res_mgr.res_skill.get(normal)
        self.normal = FightSkill(self.owner, skillRes)

        for skill_id in skills:
            skillRes = Game.res_mgr.res_skill.get(skill_id)
            if not skillRes:
                continue
            if skillRes.active:
                obj = FightSkill(self.owner, skillRes)
                self.active_skills.append(obj)
            elif skillRes.effect:
                obj = FightSkill(self.owner, skillRes)
                self.passive_skills.append(obj)

        for skill_id in peculiarity:
            skillRes = Game.res_mgr.res_skill.get(skill_id)
            if skillRes and skillRes.effect:
                obj = FightSkill(self.owner, skillRes)
                self.peculiarity.append(obj)

    def getActionSkill(self):
        #主动技能1 > 主动技能2 > 普攻技能
        for skillobj in self.active_skills:
            cd = self.cd.get(skillobj.uid, 0)
            if cd:
                continue
            return skillobj
        return self.normal

    def add_cd(self, curSkill):
        res = Game.res_mgr.res_skill.get(curSkill.resID)
        if res and res.cd:
            self.cd[curSkill.uid] = res.cd

    def cd_skill(self):
        keys = list(self.cd.keys())
        for uid in keys:
            cd = self.cd.get(uid, 0)
            if cd > 0:
                cd -= 1
                self.cd[uid] = cd
            if cd <= 0:
                self.cd.pop(uid, None)

    def event_do(self, msgCode, log_actions):
        pass

@observable
class BaseFighter(object):
    """战斗单位基类"""
    def __init__(self, fightIns, teamIns, waveIns):
        self.fightIns = fightIns
        self.teamIns = teamIns
        self.waveIns = waveIns

        fightIns.sub(msg_define.MSG_FIGHT_WAVE_INIT, self.event_fight_wave_init)
        fightIns.sub(msg_define.MSG_FIGHT_BEFORE_ROUND_1, self.event_fight_before_round_1)
        fightIns.sub(msg_define.MSG_FIGHT_BEFORE_ROUND_2, self.event_fight_before_round_2)
        fightIns.sub(msg_define.MSG_FIGHT_DO_ROUND_1, self.event_fight_do_round_1)
        self.sub(msg_define.MSG_FIGHT_WILL_DEAD, self.event_fight_will_dead)

    def init(self, attr, normal, skills, peculiarity):
        self.attr = FighterAttribute(self, attr) #属性管理
        self.buff = FighterBuff(self) #buff管理
        self.status = FighterStatus(self) #状态管理
        self.skill = FighterSkill(self, normal, skills, peculiarity) #技能管理

    def event_fight_wave_init(self, log_actions):
        self.skill.event_do(msg_define.MSG_FIGHT_WAVE_INIT, log_actions)
        self.buff.event_do(msg_define.MSG_FIGHT_WAVE_INIT, log_actions)

    def event_fight_before_round_1(self, log_actions):
        # 回合启动类buff触发(如持续回血)
        self.skill.event_do(msg_define.MSG_FIGHT_BEFORE_ROUND_1, log_actions)
        self.buff.event_do(msg_define.MSG_FIGHT_BEFORE_ROUND_1, log_actions)

    def event_fight_before_round_2(self, log_actions):
        # 回合启动类被动技能触发
        self.skill.event_do(msg_define.MSG_FIGHT_BEFORE_ROUND_2, log_actions)
        self.buff.event_do(msg_define.MSG_FIGHT_BEFORE_ROUND_2, log_actions)

    def event_fight_do_round_1(self, log_actions):
        # 行动启动1
        self.skill.event_do(msg_define.MSG_FIGHT_DO_ROUND_BF_1, log_actions)
        self.buff.event_do(msg_define.MSG_FIGHT_DO_ROUND_BF_1, log_actions)

    def event_fight_will_dead(self):
        self.status.is_dead = 1

class MonsterFighter(BaseFighter):
    """战斗单位-怪物"""
    FIGHTER_TYPE = constant.FIGHTER_TYPE_MST

    def __init__(self, fightIns, teamIns, waveIns, pos, mstRes, relation):
        super(MonsterFighter, self).__init__(fightIns, teamIns, waveIns)

        self.uid = fightIns.iterFightInsUid("mst") #唯一id
        self.resID = mstRes.id  # 资源id
        self.pos = pos #位置
        self.quality = mstRes.quality #品质
        self.petID = mstRes.petID #宠物id
        self.lv = mstRes.level #等级
        self.evLv = mstRes.evolveLv #进化等级
        skills = mstRes.skills #技能
        peculiarity = mstRes.skills #特性被动技能

        petRes = Game.res_mgr.res_pet.get(self.petID)
        self.eleType = petRes.eleType #元素类型
        self.eleVal = petRes.eleVal #元素属性值
        self.job = petRes.job #职业

        #连协
        self.relationship1 = relation.get("r1", {}).get(self.petID, [])
        #队伍加成
        self.relationship2 = relation.get("r2", {}).get(self.petID, [])
        #羁绊 组合存在多个情况
        self.relationship3 = relation.get("r3", {}).get(self.petID, [])

        #属性
        attr = self.getFightAttr(mstRes, skills, peculiarity)

        #初始化
        self.init(attr, mstRes.normal, skills, peculiarity)


    def calRelation1(self):
        # 连协
        total = {}
        for relationID in self.relationship1:
            obj = Game.res_mgr.res_petrelationship1.get(relationID)
            if obj:
                index = obj.limit.index(self.petID)
                skill_id = getattr(obj, "skill%s"%(index+1), 0)
                skillRes = Game.res_mgr.res_skill.get(skill_id)
                if skillRes:
                    for name, iNum in skillRes.attr.items():
                        total[name] = total.get(name, 0) + iNum
        return total

    def calRelation2(self):
        #队伍加成
        total = {}
        for relationID in self.relationship2:
            obj = Game.res_mgr.res_petrelationship2.get(relationID)
            if obj:
                for name, iNum in obj.addAttr.items():
                    total[name] = total.get(name, 0) + iNum
        return total

    def calRelation3(self):
        # 羁绊
        total = {}
        for relationID in self.relationship3:
            obj = Game.res_mgr.res_petrelationship3.get(relationID)
            if obj:
                index = obj.limit.index(self.petID)
                addAttr = getattr(obj, "addAttr%s" % (index + 1), {})
                for name, iNum in addAttr.items():
                    total[name] = total.get(name, 0) + iNum
        return total


    def getFightAttr(self, mstRes, skills, peculiarity):
        base = {}
        base[constant.ATTR_HP] = mstRes.hp
        base[constant.ATTR_ATK] = mstRes.atk
        base[constant.ATTR_DEFE] = mstRes.defe
        base[constant.ATTR_SPEED] = mstRes.speed
        base[constant.ATTR_HIT] = mstRes.hit
        base[constant.ATTR_MISS] = mstRes.miss
        base[constant.ATTR_GRASSADD] = mstRes.grassAddition
        base[constant.ATTR_WATERADD] = mstRes.waterAddition
        base[constant.ATTR_FIREADD] = mstRes.fireAddition
        base[constant.ATTR_LIGHTADD] = mstRes.lightAddition
        base[constant.ATTR_DARKADD] = mstRes.darkAddition
        for name, iNum in mstRes.attr.items():
            base[name] = base.get(name, 0) + iNum

        other = {}
        # 连协
        attr1 = self.calRelation1()
        for name, iNum in attr1.items():
            other[name] = other.get(name, 0) + iNum
        # 队伍加成
        attr2 = self.calRelation2()
        for name, iNum in attr2.items():
            other[name] = other.get(name, 0) + iNum
        # 羁绊
        attr3 = self.calRelation3()
        for name, iNum in attr3.items():
            other[name] = other.get(name, 0) + iNum
        #技能
        for skill_id in skills:
            skillRes = Game.res_mgr.res_skill.get(skill_id)
            if skillRes:
                for name, iNum in skillRes.attr.items():
                    other[name] = other.get(name, 0) + iNum
        #特性
        for skill_id in peculiarity:
            skillRes = Game.res_mgr.res_skill.get(skill_id)
            if skillRes:
                for name, iNum in skillRes.attr.items():
                    other[name] = other.get(name, 0) + iNum

        total = {}
        #各类比率加成
        addition = self.calRateAdditionAttr(base, other)
        for name, iNum in addition.items():
            total[name] = total.get(name, 0) + iNum

        #总计
        for name, iNum in base.items():
            total[name] = total.get(name, 0) + iNum

        for name, iNum in other.items():
            total[name] = total.get(name, 0) + iNum

        return total

    # 其他比率加成
    def calRateAdditionAttr(self, base, other):
        #统计比率属性
        addRate = {}
        for name in constant.PET_ADD_ATTR:
            iNum = other.get(name, 0)
            if iNum:
                addRate[name] = addRate.get(name, 0) + iNum

        total = {}
        #比率属性换算
        for name, rate in addRate.items():
            attrName = constant.MAP_ATTRRATE_ATTR.get(name)
            val = int(base.get(attrName, 0) * rate/10000)
            total[attrName] = total.get(attrName, 0) + val

        return total

class PetFighter(BaseFighter):
    """战斗单位-宠物"""
    FIGHTER_TYPE = constant.FIGHTER_TYPE_PET

    def __init__(self, fightIns, teamIns, waveIns, pos, data):
        super(PetFighter, self).__init__(fightIns, teamIns, waveIns)

        self.uid = data.get("id", "") #唯一id
        self.resID = data.get("resID", 0) #资源id
        self.pos = pos  # 位置
        self.lv = data.get("lv", 0)
        self.evLv = data.get("evLv", 0)
        skills = data.get("skills", []) #技能
        peculiarity = data.get("peculiarity", []) #特性
        attr_list = data.get("attr", []) #属性
        relation = data.get("relation", {}) #属性

        res = Game.res_mgr.res_pet.get(self.resID)
        self.eleType = res.eleType #元素类型
        self.eleVal = res.eleVal #元素属性值
        self.job = res.job #职业

        #连协
        self.relationship1 = relation.get("r1", [])
        #队伍加成
        self.relationship2 = relation.get("r2", [])
        #羁绊 组合存在多个情况	1）同时上阵
        self.relationship3 = relation.get("r3", [])
        #羁绊 组合存在多个情况	2）存在即激活(不用上阵）
        self.relationship4 = relation.get("r4", [])

        #初始化
        attr = {}
        for index, name in enumerate(constant.ALL_ATTR):
            val = attr_list[index]
            attr[name] = val

        self.init(attr, res.normal, skills, peculiarity)










