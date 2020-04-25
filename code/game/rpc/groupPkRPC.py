#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import ujson
import time

from corelib.frame import spawn, Game, log
from game.define import constant, msg_define

class GroupPKLogicRpc(object):
    if 0:
        from game.mgr import logicgame as logic_md
        logic = logic_md.LogicGame()

    def getGroupPKFightData(self, rid, pkType):
        from game.mgr.player import get_rpc_player
        player = get_rpc_player(rid)
        if not player:
            return
        return player.getGroupPKFightData(pkType)

    def groupPKLevelReward(self, data):
        from game.mgr.player import get_rpc_player
        for rid, one in data.items():
            player = get_rpc_player(rid)
            if not player:
                continue
            player.groupPKLevelReward(one)

    def groupPKfinalRankReward(self, data):
        eledata = data.get("eledata", {})
        lddata = data.get("lddata", {})

        elemailRes = Game.res_mgr.res_mail.get(constant.MAIL_ID_GROUP_PK_ELE_FINAL_REWARD, None)
        for rid, rank in eledata.items():
            if not elemailRes:
                continue
            for resobj in Game.res_mgr.res_groupPKfinalRankReward.itervalues():
                if resobj.stRank <= rank <= resobj.endRank:
                    content = elemailRes.content % str(rank)
                    Game.rpc_mail_mgr.sendPersonMail(rid, elemailRes.title, content, resobj.reward, push=False)
                    break

        ldmailRes = Game.res_mgr.res_mail.get(constant.MAIL_ID_GROUP_PK_LD_FINAL_REWARD, None)
        for rid, rank in lddata.items():
            if not ldmailRes:
                continue
            for resobj in Game.res_mgr.res_groupPKfinalRankReward.itervalues():
                if resobj.stRank <= rank <= resobj.endRank:
                    content = ldmailRes.content % str(rank)
                    Game.rpc_mail_mgr.sendPersonMail(rid, ldmailRes.title, content, resobj.reward, push=False)
                    break