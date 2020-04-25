#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import random

from game.define import constant
from corelib.frame import Game

from game.fight.actions import FightActions, Action

def doSkillAttack1(effect, actPoint, red, blue, data, log_actions):
    #技能伤害---直接伤害

    attacker = data.get("attacker")
    targets = data.get("targets", [])
    if not attacker or not targets:
        return

    #己方被动触发
    # action = Action(self.owner.fighter.uid, constant.FIGHT_ACTION_TYPE_1)

    #敌方被动触发

    #buff计算

    # 技能伤害率
    skillRate = effect.rate

    #执行攻击
    action = Action(effect.owner.fighter.uid, constant.FIGHT_ACTION_TYPE_1)
    action.data["sk"] = effect.owner.resID
    action.data["ef"] = effect.res.id
    action.data["tags"] = [tag.uid for tag in targets]
    log_actions.add_action(action)
    next_actions = FightActions(constant.FIGHT_DO_TYPE_CONCURRENCE)
    action.next_actions = next_actions

    for defender in targets:
        # 中途死亡单位过滤
        if defender.status.is_dead:
            continue

        isCirt, isMiss, iHurt = GetHurtVal(attacker, defender, skillRate, data)
        if iHurt:
            defender.attr.delHP(iHurt)
        if isMiss:
            damage_type = constant.FIGHT_DAMAGE_TYPE_4
        else:
            if isCirt:
                damage_type = constant.FIGHT_DAMAGE_TYPE_2
            else:
                damage_type = constant.FIGHT_DAMAGE_TYPE_1

        action = Action(defender.uid, constant.FIGHT_ACTION_TYPE_2)
        action.data["ef"] = effect.res.id
        action.data["tp"] = damage_type
        action.data["v"] = iHurt
        action.data["attr"] = defender.attr.to_client()
        next_actions.add_action(action)
        # 死亡流程

        # buff计算
        # 己方被动触发
        # 敌方被动触发

        # 清除临时附加

    #buff计算
    #己方被动触发
    #敌方被动触发

    #清除临时附加


def doSkillAttack2(effect, actPoint, red, blue, data, log_actions):
    #技能伤害---直接伤害(1特效多伤害)

    attacker = data.get("attacker")
    targets = data.get("targets", [])
    if not attacker or not targets:
        return
    # 技能伤害率
    skillRate = effect.rate
    atkNum = effect.atkNum

    # 执行攻击
    action = Action(effect.owner.fighter.uid, constant.FIGHT_ACTION_TYPE_1)
    action.data["sk"] = effect.owner.resID
    action.data["ef"] = effect.res.id
    action.data["tags"] = [tag.uid for tag in targets]
    log_actions.add_action(action)

    # 空节点
    action = Action(effect.owner.fighter.uid, constant.FIGHT_ACTION_TYPE_0)
    log_actions.add_action(action)
    next_actions = FightActions(constant.FIGHT_DO_TYPE_ORDER)
    action.next_actions = next_actions

    for i in range(atkNum):
        # 空节点
        action = Action(effect.owner.fighter.uid, constant.FIGHT_ACTION_TYPE_0)
        next_actions.add_action(action)
        oneAtk_actions = FightActions(constant.FIGHT_DO_TYPE_CONCURRENCE)
        action.next_actions = oneAtk_actions

        #己方被动触发
        # action = Action(self.owner.fighter.uid, constant.FIGHT_ACTION_TYPE_1)
        # oneAtk_actions.add_action(action)

        #敌方被动触发
        # action = Action(self.owner.fighter.uid, constant.FIGHT_ACTION_TYPE_1)
        # oneAtk_actions.add_action(action)

        #buff计算


        # 受击组 空节点
        action = Action(effect.owner.fighter.uid, constant.FIGHT_ACTION_TYPE_0)
        oneAtk_actions.add_action(action)
        hurt_actions = FightActions(constant.FIGHT_DO_TYPE_CONCURRENCE)
        action.next_actions = hurt_actions


        for defender in targets:
            # 中途死亡单位过滤
            if defender.status.is_dead:
                continue

            isCirt, isMiss, iHurt = GetHurtVal(attacker, defender, skillRate, data)
            if iHurt:
                defender.attr.delHP(iHurt)
            if isMiss:
                damage_type = constant.FIGHT_DAMAGE_TYPE_4
            else:
                if isCirt:
                    damage_type = constant.FIGHT_DAMAGE_TYPE_2
                else:
                    damage_type = constant.FIGHT_DAMAGE_TYPE_1

            action = Action(defender.uid, constant.FIGHT_ACTION_TYPE_2)
            action.data["ef"] = effect.res.id
            action.data["tp"] = damage_type
            action.data["v"] = iHurt
            action.data["attr"] = defender.attr.to_client()
            hurt_actions.add_action(action)

            # 死亡流程

            # buff计算
            # 己方被动触发
            # 敌方被动触发

            # 清除临时附加

        #buff计算
        #己方被动触发
        #敌方被动触发

        #清除临时附加

def doSkillAttack3(effect, actPoint, red, blue, data, log_actions):
    #技能伤害----直接伤害(多段特效多段伤害)

    attacker = data.get("attacker")
    targets = data.get("targets", [])
    if not attacker or not targets:
        return

    #己方被动触发
    # action = Action(self.owner.fighter.uid, constant.FIGHT_ACTION_TYPE_1)

    #敌方被动触发

    #buff计算

    # 技能伤害率
    skillRate = effect.rate

    #执行攻击
    action = Action(effect.owner.fighter.uid, constant.FIGHT_ACTION_TYPE_1)
    action.data["sk"] = effect.owner.resID
    action.data["ef"] = effect.res.id
    action.data["tags"] = [tag.uid for tag in targets]
    log_actions.add_action(action)
    next_actions = FightActions(constant.FIGHT_DO_TYPE_CONCURRENCE)
    action.next_actions = next_actions

    for defender in targets:
        # 中途死亡单位过滤
        if defender.status.is_dead:
            continue

        isCirt, isMiss, iHurt = GetHurtVal(attacker, defender, skillRate, data)
        if iHurt:
            defender.attr.delHP(iHurt)
        if isMiss:
            damage_type = constant.FIGHT_DAMAGE_TYPE_4
        else:
            if isCirt:
                damage_type = constant.FIGHT_DAMAGE_TYPE_2
            else:
                damage_type = constant.FIGHT_DAMAGE_TYPE_1

        action = Action(defender.uid, constant.FIGHT_ACTION_TYPE_2)
        action.data["ef"] = effect.res.id
        action.data["tp"] = damage_type
        action.data["v"] = iHurt
        action.data["attr"] = defender.attr.to_client()
        next_actions.add_action(action)
        data["lastAtion"] = action
        # 死亡流程

        # buff计算
        # 己方被动触发
        # 敌方被动触发

        # 清除临时附加

    #buff计算
    #己方被动触发
    #敌方被动触发

    #清除临时附加


def doSkillRestore1(effect, actPoint, red, blue, data, log_actions):
    # 技能回血--施法者攻击力n%点血量(万分比)

    attacker = data.get("attacker")
    targets = data.get("targets", [])
    if not attacker or not targets:
        return

    #己方被动触发
    # action = Action(self.owner.fighter.uid, constant.FIGHT_ACTION_TYPE_1)

    #敌方被动触发

    #buff计算

    # 治疗量
    addVal = attacker.attr.getAtk() * effect.rate/10000

    #执行攻击
    action = Action(effect.owner.fighter.uid, constant.FIGHT_ACTION_TYPE_1)
    action.data["sk"] = effect.owner.resID
    action.data["ef"] = effect.res.id
    action.data["tags"] = [tag.uid for tag in targets]
    log_actions.add_action(action)
    next_actions = FightActions(constant.FIGHT_DO_TYPE_CONCURRENCE)
    action.next_actions = next_actions

    for defender in targets:
        # 中途死亡单位过滤
        if defender.status.is_dead:
            continue

        restoreVal = GetRestoreVal(attacker, defender, addVal, data)

        action = Action(defender.uid, constant.FIGHT_ACTION_TYPE_9)
        action.data["ef"] = effect.res.id
        action.data["v"] = restoreVal
        action.data["attr"] = defender.attr.to_client()
        next_actions.add_action(action)
        # 死亡流程

        # buff计算
        # 己方被动触发
        # 敌方被动触发

        # 清除临时附加

    #buff计算
    #己方被动触发
    #敌方被动触发

    #清除临时附加

def GetRestoreVal(attacker, defender, addVal, data):
    #治疗生命 = 治疗量*（1+治疗效果提升万分比）
    restoreVal = addVal * (1 + attacker.attr.getTreatRate()/10000)

    #最终治疗生命 = 治疗生命*(1+受治疗效果提升万分比)
    restoreVal = restoreVal * (1 + defender.attr.getBeTreatRate()/10000)

    return restoreVal


def IsMiss(attacker, defender):
    """是否闪避"""
    #命中率 == 命中/固定值参数^2+ 其他万分比命中率加成   （固定值参数 = 316 ）
    #闪避率 == 闪避/固定值参数^2+ 其他万分比闪避率加成    （固定值参数 = 316 ）
    #命中 = MAX（（攻击方 命中率 - 防御方 闪避率），70%）

    #命中率 万分比
    hitRate = attacker.attr.getHit()*10000/(316**2) + attacker.attr.getHitRate()
    #闪避率 万分比
    missRate = defender.attr.getMiss()*10000/(316**2) + defender.attr.getMissRate()

    val = max(int(hitRate - missRate), 7000) #最终值 万分比

    if random.randint(1, 10000) > val: #闪避
        return True
    else:
        return False


def IsCirt(attacker, defender):
    """是否暴击"""
    #暴击率 == 暴击/(2*固定值参数^2） + 其他万分比暴击率    （固定值参数 = 316）
    #抗暴率 == 抗暴/(2*固定值参数^2)  + 其他万分比抗暴率    （固定值参数 = 316）
    #暴击 = MAX （（  攻击方 暴击率 - 防御方  抗暴率），10%）

    #暴击率 万分比
    cirtRate = attacker.attr.getCirt()*10000/(316**2) + attacker.attr.getCirtRate()
    #抗暴率 万分比
    cirtSubRate = defender.attr.getCirtSub()*10000/(316**2) + defender.attr.getCirtSubRate()

    val = max(int(cirtRate - cirtSubRate), 1000) #最终值 万分比

    if random.randint(1, 10000) <= val: #暴击
        return True
    else:
        return False


def GetHurtVal(attacker, defender, skillRate, data):
    isCirt, isMiss, iHurt = 0, 0, 0
    #是否闪避
    isMiss = IsMiss(attacker, defender)
    if isMiss:
        return isCirt, isMiss, iHurt

    #攻击伤害 == 攻击方 Attack * (1-防御方 defend *（1-忽视敌方防御万分比) /
    #                            (防御方 defend  + 固定参数1 + 固定参数2* 防御方 等级））
    #（固定参数1 =598 ，固定参数2 =2 ）
    arg1 = 598
    arg2 = 2
    iHurt = attacker.attr.getAtk()*(1-defender.attr.getDefe()*(1-attacker.attr.getUnDefRate()/10000)
                            /(defender.attr.getDefe() +  arg1 + arg2*defender.lv))

    #技能伤害 == MAX（攻击伤害* 攻击方 技能伤害 系数  * （1 + 攻击方 技能伤害加深）*（1 - 防御方 技能减免系数 ），1）
    iHurt = max(iHurt*(skillRate/10000)*(1+attacker.attr.getSkDamRate()/10000)*(1-defender.attr.getSkDamSubRate()/10000), 1)


    #元素生克	火克草，草克水，水克火，光暗互克；元素克制系数为 20%
    #伤害加深减免 == MAX（技能伤害 *（1+元素克制系数+其他类型伤害加深-其他类型伤害减免），1）
    eleAdd = 0
    if attacker.eleType == constant.PKM2_ELE_TYPE_FIRE and defender.eleType == constant.PKM2_ELE_TYPE_GRASS:
        eleAdd = 0.2
    elif attacker.eleType == constant.PKM2_ELE_TYPE_GRASS and defender.eleType == constant.PKM2_ELE_TYPE_WATER:
        eleAdd = 0.2
    elif attacker.eleType == constant.PKM2_ELE_TYPE_WATER and defender.eleType == constant.PKM2_ELE_TYPE_FIRE:
        eleAdd = 0.2
    elif attacker.eleType == constant.PKM2_ELE_TYPE_LIGHT and defender.eleType == constant.PKM2_ELE_TYPE_DARK:
        eleAdd = 0.2
    elif attacker.eleType == constant.PKM2_ELE_TYPE_DARK and defender.eleType == constant.PKM2_ELE_TYPE_LIGHT:
        eleAdd = 0.2
    iHurt = max(iHurt*(1+eleAdd), 1)

    # 攻击伤害 == MAX（伤害加深减免 + 附加伤害值 - 附加伤害减免值 ，1）+纯粹伤害
    iHurt = max(iHurt + attacker.attr.getDamAdd() - defender.attr.getDamSub(), 1) + attacker.attr.getRealDam()

    #最终伤害 == MAX ( rand （0.85，1.05）* 攻击伤害 , 1 )
    iHurt = max((random.randint(85, 105)/100)* iHurt, 1)

    #PVP结算伤害 == （最终伤害 * （1 +  PVP 伤害加深 ））*（1-  PVP 伤害减免 ）
    if attacker.FIGHTER_TYPE != constant.FIGHTER_TYPE_MST and defender.FIGHTER_TYPE != constant.FIGHTER_TYPE_MST:
        iHurt = iHurt * (1 + attacker.attr.getPvpDamRate()/10000) * (1 - defender.attr.getPvpDamSubRate()/10000)
    #PVE结算伤害 == （最终伤害 * （1 +  PVE 伤害加深 ））*（1 -  PVE 伤害减免 ）
    else:
        iHurt = iHurt * (1 + attacker.attr.getPveDamRate()/10000) * (1 - defender.attr.getPveDamSubRate()/10000)

    # 是否暴击
    isCirt = IsCirt(attacker, defender)
    if isCirt:
        # 暴击伤害 == 最终伤害 * 暴击伤害系数   （暴击伤害系数 = 1.2）
        iHurt = iHurt * 1.2
        #暴伤加成后结算伤害 == 暴击伤害 *（1 + 暴击伤害附加万分比 -  暴击伤害减免万分比）
        iHurt = iHurt * (1 + (attacker.attr.getCirtDamRate() - defender.attr.getCirtDamSubRate())/10000)

    return isCirt, isMiss, int(iHurt)








