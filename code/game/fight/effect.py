#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import random

from corelib.frame import Game
from game.define import constant
from game.common import utility

from game.fight.damage import doSkillAttack1, doSkillAttack2, doSkillAttack3, doSkillRestore1
from game.fight.actions import Action, FightActions

class FightEffectBase(object):
    """战斗效果基类"""
    def __init__(self, owner, res):
        self.owner = owner
        self.res = res

    def selectTargets(self, red, blue, data):
        targets = data.setdefault("targets", [])
        if self.res.target:
            if self.res.target_tp == 1: #全体
                objs = []
                objs.extend(red.getAll())
                objs.extend(blue.getAll())
                targets = self._selectTargets(objs)
            elif self.res.target_tp == 2: #我方
                if self.owner.fighter.teamIns.flag == constant.FIGHT_TEAM_RED:
                    objs = red.getAll()
                    targets = self._selectTargets(objs)
                elif self.owner.fighter.teamIns.flag == constant.FIGHT_TEAM_BLUE:
                    objs = blue.getAll()
                    targets = self._selectTargets(objs)
            elif self.res.target_tp == 3: #敌方
                if self.owner.fighter.teamIns.flag == constant.FIGHT_TEAM_RED:
                    objs = blue.getAll()
                    targets = self._selectTargets(objs)
                elif self.owner.fighter.teamIns.flag == constant.FIGHT_TEAM_BLUE:
                    objs = red.getAll()
                    targets = self._selectTargets(objs)
            elif self.res.target_tp == 4: #自己
                targets.append(self.owner.fighter)

        ##死亡单位
        if 3 not in self.res.target_scope:
            _no_dead = []
            for obj in targets:
                if obj.status.is_dead:
                    continue
                _no_dead.append(obj)
            data["targets"] = _no_dead
        else:
            data["targets"] = targets
        return targets

    def _selectTargets(self, objs):
        # 过滤
        l_targets = []
        for scope in self.res.target_scope:
            objs = self._selectTargets1(objs, scope)
            l_targets.append(objs)
        #去重
        l_norepeat = []
        for i in range(len(l_targets)-1):
            a = set(l_targets[i])
            b = set(l_targets[i+1])
            c = a.symmetric_difference(b)
            for obj in c:
                l_norepeat.insert(0, obj)
        if l_targets:
            for obj in l_targets[-1]:
                l_norepeat.insert(0, obj)
        #取目标
        if self.res.target_num:
            num = utility.Choice(self.res.target_num)
        else:
            num = 0

        resp = []
        for obj in l_norepeat:
            resp.append(obj)
            num -= 1
            if num <= 0:
                break
        return resp

    def _selectTargets1(self, objs, scope):
        #默认情况都选择非死亡单位
        _objs = []
        if scope == 3: #死亡单位
            for obj in objs:
                if obj.status.is_dead:
                    _objs.append(obj)
        else:
            for obj in objs:
                if not obj.status.is_dead:
                    _objs.append(obj)

        resp = []
        if scope == 1: #全体
            resp.extend(_objs)
        elif scope == 2: #随机
            random.shuffle(_objs)
            resp.extend(_objs)
        elif scope == 3: #死亡
            resp.extend(_objs)
        elif scope == 4: #职业-法攻
            for obj in _objs:
                if obj.job == constant.PKM2_JOB_TYPE_MAGIC:
                    resp.append(obj)
        elif scope == 5: #职业-物攻
            for obj in _objs:
                if obj.job == constant.PKM2_JOB_TYPE_PHY:
                    resp.append(obj)
        elif scope == 6: #职业-防御
            for obj in _objs:
                if obj.job == constant.PKM2_JOB_TYPE_DEF:
                    resp.append(obj)
        elif scope == 7: #职业-辅助
            for obj in _objs:
                if obj.job == constant.PKM2_JOB_TYPE_AUXILIARY:
                    resp.append(obj)
        elif scope == 8: #元素-水
            for obj in _objs:
                if obj.eleType == constant.PKM2_ELE_TYPE_WATER:
                    resp.append(obj)
        elif scope == 9: #元素-草
            for obj in _objs:
                if obj.eleType == constant.PKM2_ELE_TYPE_GRASS:
                    resp.append(obj)
        elif scope == 10: #元素-火
            for obj in _objs:
                if obj.eleType == constant.PKM2_ELE_TYPE_FIRE:
                    resp.append(obj)
        elif scope == 11: #元素-光
            for obj in _objs:
                if obj.eleType == constant.PKM2_ELE_TYPE_LIGHT:
                    resp.append(obj)
        elif scope == 12: #元素-暗
            for obj in _objs:
                if obj.eleType == constant.PKM2_ELE_TYPE_DARK:
                    resp.append(obj)
        elif scope == 13: #自己（建议选自己和已方时用）
            resp.append(self.owner.fighter)
        elif scope == 14:  # 前方(优先找前1排的对位)
            pass

        elif scope == 101: # 前一排（离我最近的一排）
            random.shuffle(_objs)
            resp.extend(_objs)
        elif scope == 201: #对位列
            random.shuffle(_objs)
            resp.extend(_objs)

        elif scope == 301: #属性最高-生命   按当前生命值排序 高--低
            _objs.sort(key=lambda x:x.attr.getHP(), reverse=True)
            resp.extend(_objs)
        elif scope == 302: #属性最高-攻击   按当前攻击值排序 高--低
            _objs.sort(key=lambda x:x.attr.getAtk(), reverse=True)
            resp.extend(_objs)
        elif scope == 303: #属性最高-防御   按当前防御值排序 高--低
            _objs.sort(key=lambda x:x.attr.getDefe(), reverse=True)
            resp.extend(_objs)
        elif scope == 304: #属性最高-速度   按当前速度值排序 高--低
            _objs.sort(key=lambda x:x.attr.getSpeed(), reverse=True)
            resp.extend(_objs)

        elif scope == 401: #属性最低-生命   按当前生命值排序 低--高
            _objs.sort(key=lambda x:x.attr.getHP())
            resp.extend(_objs)
        elif scope == 402: #属性最低-攻击   按当前攻击值排序 低--高
            _objs.sort(key=lambda x:x.attr.getAtk())
            resp.extend(_objs)
        elif scope == 403: #属性最低-防御   按当前防御值排序 低--高
            _objs.sort(key=lambda x:x.attr.getDefe())
            resp.extend(_objs)
        elif scope == 404: #属性最低-速度   按当前速度值排序 低--高
            _objs.sort(key=lambda x:x.attr.getSpeed())
            resp.extend(_objs)

        elif scope == 501: #属性比例最低-生命 低--高
            _objs.sort(key=lambda x:x.attr.getHP()/x.attr.getMaxHP())
            resp.extend(_objs)

        elif scope == 601: #畏缩
            pass
        elif scope == 602: #恐惧
            pass

        return resp


    def execute(self, actPoint, red, blue, data, log_actions):
        if actPoint != self.res.actPoint and actPoint != data.get("actPoint", 0):
            return False
        data["actPoint"] = actPoint
        self.selectTargets(red, blue, data)
        if not self.checkCondition(data):
            return False
        self.parseArgs()
        return True

    def parseArgs(self):
        raise NotImplementedError

    def checkCondition(self, data):
        if self.res.cond == 1: #上一条成功
            pass
        elif self.res.cond == 2: #上一条失败
            pass
        elif self.res.cond == 5: #概率 万分比
            iNum = random.randint(1, 10000)
            if iNum > int(self.res.condArgs):
                return False
        elif self.res.cond == 6: #目标携带buff
            #多目标情况下，存在有的人满足，有的人不满足
            targets = data.get("targets", [])
            targets_fix = []
            for obj in targets:
                if obj.buff.has_buff(int(self.res.condArgs)):
                    targets_fix.append(obj)
            data["targets_fix"] = targets_fix

        return True

class FightEffect100(FightEffectBase):
    """直接伤害-物理-n%的物理伤害(万分比)"""
    def parseArgs(self):
        self.rate = int(self.res.effArgs)

    def execute(self, actPoint, red, blue, data, log_actions):
        if not FightEffectBase.execute(self, actPoint, red, blue, data, log_actions):
            return False
        targets = data.get("targets", [])
        if not targets:
            return False
        data["attacker"] = self.owner.fighter
        #进入受击流程
        doSkillAttack1(self, actPoint, red, blue, data, log_actions)

        return True

class FightEffect101(FightEffectBase):
    """直接伤害-物理(1特效多伤害)"""
    def parseArgs(self):
        args = self.res.effArgs.split("_")
        self.atkNum = random.randint(int(args[0]), int(args[1]))
        self.rate = int(args[2])

    def execute(self, actPoint, red, blue, data, log_actions):
        if not FightEffectBase.execute(self, actPoint, red, blue, data, log_actions):
            return False
        targets = data.get("targets", [])
        if not targets:
            return False
        data["attacker"] = self.owner.fighter
        #进入受击流程
        doSkillAttack2(self, actPoint, red, blue, data, log_actions)

        return True

class FightEffect102(FightEffectBase):
    """直接伤害-物理(多段特效多段伤害)"""
    def parseArgs(self):
        self.rate = int(self.res.effArgs)

    def execute(self, actPoint, red, blue, data, log_actions):
        if not FightEffectBase.execute(self, actPoint, red, blue, data, log_actions):
            return False
        targets = data.get("targets", [])
        if not targets:
            return False
        lastAtion = data.get("lastAtion") #是否有上一个伤害节点
        if not lastAtion:
            # 空节点
            action = Action(self.owner.fighter.uid, constant.FIGHT_ACTION_TYPE_0)
            log_actions.add_action(action)
            next_actions = FightActions(constant.FIGHT_DO_TYPE_ORDER)
            action.next_actions = next_actions
        else:
            next_actions = FightActions(constant.FIGHT_DO_TYPE_ORDER)
            lastAtion.next_actions = next_actions

        data["attacker"] = self.owner.fighter
        #进入受击流程
        doSkillAttack3(self, actPoint, red, blue, data, next_actions)

        return True


class FightEffect200(FightEffect100):
    """直接伤害-法术-n%的法术伤害(万分比)"""
    pass

class FightEffect201(FightEffect101):
    """直接伤害-法术(1特效多伤害)"""
    pass

class FightEffect202(FightEffect102):
    """直接伤害-法术(多段特效多段伤害)"""
    pass




class FightEffect500(FightEffectBase):
    """回血-施法者攻击力n%点血量(万分比)"""
    def parseArgs(self):
        self.rate = int(self.res.effArgs)

    def execute(self, actPoint, red, blue, data, log_actions):
        if not FightEffectBase.execute(self, actPoint, red, blue, data, log_actions):
            return False
        targets = data.get("targets", [])
        if not targets:
            return False

        data["attacker"] = self.owner.fighter
        #进入回血流程
        doSkillRestore1(self, actPoint, red, blue, data, log_actions)

        return True



class FightEffect1402(FightEffectBase):
    """净化--净化所有负面状态(不可驱散状态除外)"""
    def execute(self, actPoint, red, blue, data, log_actions):
        if not FightEffectBase.execute(self, actPoint, red, blue, data, log_actions):
            return False
        targets = data.get("targets", [])
        if not targets:
            return False

        data["attacker"] = self.owner.fighter
        #进入回血流程
        doSkillRestore1(self, actPoint, red, blue, data, log_actions)

        return True




class FightEffect2200(FightEffectBase):
    """本次攻击临时提升-xx属性_xx点)"""
    def execute(self, actPoint, red, blue, data, log_actions):
        if not FightEffectBase.execute(self, actPoint, red, blue, data, log_actions):
            return False

        return True


Map_fight_effect_type = {
    constant.FIGHT_EFFECT_TYPE_100: FightEffect100, # 直接伤害-物理-n%的物理伤害(万分比)
    constant.FIGHT_EFFECT_TYPE_101: FightEffect101, # 直接伤害-物理(1特效多伤害)
    constant.FIGHT_EFFECT_TYPE_102: FightEffect102, # 直接伤害-物理(多段特效多段伤害)

    constant.FIGHT_EFFECT_TYPE_200: FightEffect200, # 直接伤害-法术-n%的法术伤害(万分比)
    constant.FIGHT_EFFECT_TYPE_201: FightEffect201, # 直接伤害-法术(多段特效多段伤害)
    constant.FIGHT_EFFECT_TYPE_202: FightEffect202, # 直接伤害-法术(多段特效多段伤害)



    constant.FIGHT_EFFECT_TYPE_500: FightEffect500, # 回血-施法者攻击力n%点血量(万分比)


    constant.FIGHT_EFFECT_TYPE_1402: FightEffect1402,  # 净化--净化所有负面状态(不可驱散状态除外)


    constant.FIGHT_EFFECT_TYPE_2200: FightEffect2200, # 本次攻击临时提升-xx属性_xx点
}
























