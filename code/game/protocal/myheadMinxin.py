#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import random
import copy
from game.define import errcode, constant
from game import Game
from game.common import utility

class MyheadMixin(object):
    if 0:
        from game.core import player as player_md
        player = player_md.Player()

    def rc_myheadActive(self, id, itemId):
        res = Game.res_mgr.res_myhead.get(id)
        if not res:
            return 0, errcode.EC_NORES

        for x in self.player.myhead.active:
            if x["id"]==id:
                return 0, errcode.EC_MYHEAD_HAS_ACT

        rs, itemobj = self.player.bag.costItemByTranceNo(itemId, constant.ITEM_COST_MYHEAD_MAKE, wLog=True)
        if not rs:
            return 0, errcode.EC_MYHEAD_ACT_NOT_ENOUGH

        self.player.myhead.activeMyhead(id, itemobj.endTime)
        self.player.attr.RecalFightAbility()


        dUpdate = {}
        dUpdate["base"] = {"fa": self.player.base.fa}
        dUpdate["bag"] = {"item_bag": self.player.bag.item_bag.to_update_data(items=[itemobj])}
        dUpdate["attr"] = self.player.attr.to_update_data()
        dUpdate["myhead"] = self.player.myhead.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp


    # id=-1清除头像 -2清楚边框
    def rc_myheadUse(self, id):
        if id>=0:
            res = Game.res_mgr.res_myhead.get(id)
            if not res:
                return 0, errcode.EC_NORES

            found=False
            for x in self.player.myhead.active:
                if x["id"]==id:
                    found=True

            if not found:
                return 0, errcode.EC_MYHEAD_HASNOT_ACT

        self.player.myhead.useMyhead(id)
        
        dUpdate={}
        dUpdate["myhead"] = self.player.myhead.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp


    def rc_myheadFlash(self):
        self.player.myhead.Flash()
        self.player.attr.RecalFightAbility()

        dUpdate = {}
        dUpdate["base"] = {"fa": self.player.base.fa}
        dUpdate["attr"] = self.player.attr.to_update_data()
        dUpdate["myhead"] = self.player.myhead.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp
