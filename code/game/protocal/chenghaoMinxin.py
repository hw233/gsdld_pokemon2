#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import random
import copy
from game.define import errcode, constant
from game import Game
from game.common import utility

class ChenghaoMixin(object):
    if 0:
        from game.core import player as player_md
        player = player_md.Player()

    def rc_chenghaoActive(self, id):
        res = Game.res_mgr.res_chenghao.get(id)
        if not res:
            return 0, errcode.EC_NORES

        if id in self.player.chenghao.active:
            return 0, errcode.EC_CHENGHAO_HAS_ACT

        respBag = self.player.bag.costItem(res.cost, constant.ITEM_COST_CHENGHAO_MAKE, wLog=True)
        if not respBag.get("rs", 0):
            return 0, errcode.EC_CHENGHAO_ACT_NOT_ENOUGH

        self.player.chenghao.activeChenghao(id)
        self.player.attr.RecalFightAbility()

        dUpdate = self.player.packRespBag(respBag)
        dUpdate["attr"] = self.player.attr.to_update_data()
        dUpdate["chenghao"] = self.player.chenghao.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp

    def rc_chenghaoUse(self, id):
        res = Game.res_mgr.res_chenghao.get(id)
        if not res:
            return 0, errcode.EC_NORES

        if id not in self.player.chenghao.active:
            return 0, errcode.EC_CHENGHAO_HASNOT_ACT

        self.player.chenghao.useChenghao(id)
        
        dUpdate={}
        dUpdate["chenghao"] = self.player.chenghao.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp


    def rc_chenghaoUpgrade(self, id):
        res = Game.res_mgr.res_chenghao.get(id)
        if not res:
            return 0, errcode.EC_NORES

        if id not in self.player.chenghao.active:
            return 0, errcode.EC_CHENGHAO_HASNOT_ACT

        respBag = self.player.bag.costItem(res.cost, constant.ITEM_COST_CHENGHAO_UP, wLog=True)
        if not respBag.get("rs", 0):
            return 0, errcode.EC_CHENGHAO_UP_NOT_ENOUGH

        self.player.chenghao.upgradeChenghao(id)
        self.player.attr.RecalFightAbility()


        dUpdate = self.player.packRespBag(respBag)
        dUpdate["attr"] = self.player.attr.to_update_data()
        dUpdate["chenghao"] = self.player.chenghao.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp


