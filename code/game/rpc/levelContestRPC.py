#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import ujson
import time
import config

from corelib.frame import spawn, Game, log
from game.define import constant, msg_define

class LevelContestLogicRpc(object):
    if 0:
        from game.mgr import logicgame as logic_md
        logic = logic_md.LogicGame()

    def levelContestRankReward(self, data):
        resAct = Game.res_mgr.res_activity.get(constant.ACTIVITY_LEVEL_CONTEST)
        serverInfo = Game.rpc_server_info.GetServerInfo()
        if not resAct.isOpen(serverInfo):
            return

        onlines = Game.player_mgr.players.keys()

        # 发放上榜玩家
        from game.mgr.player import get_rpc_player
        # data {段位:{rid:名次}
        for level, rankDict in data.items():
            resDict = None
            mailId = None
            if level == constant.LEVEL_CONTEST_LV_1:
                resDict = Game.res_mgr.res_levelContestRankReward1
                mailId = constant.MAIL_ID_LEVEL_CONTEST_RANK_1
            elif level == constant.LEVEL_CONTEST_LV_2:
                resDict = Game.res_mgr.res_levelContestRankReward2
                mailId = constant.MAIL_ID_LEVEL_CONTEST_RANK_2
            elif level == constant.LEVEL_CONTEST_LV_3:
                resDict = Game.res_mgr.res_levelContestRankReward3
                mailId = constant.MAIL_ID_LEVEL_CONTEST_RANK_3
            elif level == constant.LEVEL_CONTEST_LV_4:
                resDict = Game.res_mgr.res_levelContestRankReward4
                mailId = constant.MAIL_ID_LEVEL_CONTEST_RANK_4
            elif level == constant.LEVEL_CONTEST_LV_5:
                resDict = Game.res_mgr.res_levelContestRankReward5
                mailId = constant.MAIL_ID_LEVEL_CONTEST_RANK_5

            mailRes = Game.res_mgr.res_mail.get(mailId, None)
            if not resDict or not mailRes:
                continue

            for rid, rank in rankDict.items():
                if rid in onlines:
                    onlines.remove(rid)
                rewardRes = None
                for res in resDict.itervalues():
                    if res.min <= rank <= res.max:
                        rewardRes = res
                        break
                if rewardRes:
                    content = mailRes.content % str(rank)
                    Game.rpc_mail_mgr.sendPersonMail(rid, mailRes.title, content, rewardRes.rankReward, push=False)

                    player = get_rpc_player(rid)
                    if player:
                        player.setLevelContestRankRewardFlag()

        Game.glog.log2File("levelContestReward", "%s|%s" % (config.serverNo, data))

    def getLevelContestFightData(self, rid):
        from game.mgr.player import get_rpc_player
        player = get_rpc_player(rid)
        if not player:
            return
        return player.getLevelContestFightData()

    def saveLevelContestFightLog(self, rid, saveLog):
        from game.mgr.player import get_rpc_player
        player = get_rpc_player(rid)
        if not player:
            return
        player.saveLevelContestFightLog(saveLog)