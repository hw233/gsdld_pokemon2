#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from corelib.frame import Game
from game.fight.effect import Map_fight_effect_type

class BaseBuff(object):
    def __init__(self, fighter, caster, res):
        self.fighter = fighter #挂载者
        self.caster = caster #施法者

        self.uid = fighter.fightIns.iterFightInsUid("skill")
        self.resID = res.id #buffid
        self.res = res

        self.effects = {} #技能效果
        self.init()

    def init(self):
        order = 1
        while True:
            effRes = Game.res_mgr.res_group_order_effect.get((self.res.effect, order))
            if effRes:
                cls = Map_fight_effect_type.get(effRes.effType)
                if not cls:
                    break
                effobj = cls(self, effRes)
                self.effects[order] = effobj
                order += 1
            else:
                break

    def execSkill(self, actPoint, red, blue, log_actions):
        keys = list(self.effects.keys())
        keys.sort()

        data = {}
        for k in keys:
            obj = self.effects.get(k)
            if not obj:
                return
            obj.execute(actPoint, red, blue, data, log_actions)