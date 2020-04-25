#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from game.define import errcode, constant, msg_define
from game import Game

from corelib import log

from game.common import utility

import random
import time
import config
import copy

class RoleRpcMixin(object):
    if 0:
        from game.core import player as player_md
        player = player_md.Player()

    # 角色升级(roleUpgrade)
    # 请求
    #
    # 返回
    #     主动推送刷新(allUpdate, json)
    #         游戏模型 - 角色基础
    #             战力(fa, int)
    #             等级(lv, int)
    #             当前经验值(exp, int)
    #         游戏模型 - 角色属性
    def rc_roleUpgrade(self):
        iCurLv = self.player.base.GetLv()
        iNextLv = iCurLv + 1
        curRes = Game.res_mgr.res_level.get(iCurLv, None)
        nextRes = Game.res_mgr.res_level.get(iNextLv, None)
        if not nextRes:
            return 0, errcode.EC_MAX_LEVEL
        #先扣经验
        iCurExp = self.player.base.GetExp()
        if iCurExp < curRes.exp:
            return 0, errcode.EC_NOT_ENOUGH
        iNewExp = iCurExp - curRes.exp
        self.player.base.SetExp(iNewExp)
        self.player.base.SetLv(iNextLv)
        #打包返回信息
        dUpdate = {}
        dUpdate["base"] = {}
        dUpdate["base"]["fa"] = self.player.base.fa
        dUpdate["base"]["lv"] = self.player.base.lv
        dUpdate["base"]['exp'] = self.player.base.exp
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp



