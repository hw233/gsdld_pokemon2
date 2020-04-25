#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from game.fight.scene import Map_fight_type

def createFight(iType):
    """创建一次战斗"""
    fightCls = Map_fight_type.get(iType)
    return fightCls(iType)
