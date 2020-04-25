#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import time

from corelib.frame import spawn, Game, log
from game.define import constant, msg_define

class BossPlayerRpc(object):
    if 0:
        from game.core import player as player_md
        player = player_md.Player()

    def sendYwBossKillReward(self, bossId, isTimeout=1):
        """击杀野外boss奖励"""
        resYwBoss = Game.res_mgr.res_ywBoss.get(bossId)
        if not resYwBoss:
            return
        barrRes = Game.res_mgr.res_barrier.get(resYwBoss.fbId)
        if not barrRes:
            return
        rewardRes = Game.res_mgr.res_reward.get(barrRes.rewardId)
        if not rewardRes:
            return
        dReward = rewardRes.doReward()
        respBag = self.player.bag.add(dReward, constant.ITEM_ADD_YWBOSS_REWARD, wLog=True)
        iTodayNum = self.player.boss.GetYwBossTodayTZ()
        # 修改挑战次数
        self.player.boss.SetYwBossTodayTZ(iTodayNum + 1)
        # 修改最后挑战时间
        now = int(time.time())
        self.player.boss.SetYwBossLastTZTime(now)

        #抛事件
        self.player.safe_pub(msg_define.MSG_KILL_YW_BOSS)
        if isTimeout:
            dUpdate = self.player.packRespBag(respBag)
            resp = {
                "allUpdate": dUpdate,
            }
            spawn(self.player.call, "ywBossKill", resp, noresult=True)
        return respBag


    def ssjBossTZNotice(self, id, fightLog, pid):
        ssjRes = Game.res_mgr.res_ssjBoss.get(id)
        if not ssjRes:
            return
        barrRes = Game.res_mgr.res_barrier.get(ssjRes.fbId)
        if not barrRes:
            return
        helpres = Game.res_mgr.res_common.get("ssjBossHelpNum")
        if not helpres:
            return

        fightResult = fightLog["result"].get("win", 0)
        respBag = {}
        if fightResult:
            dReward = {}
            if not self.player.boss.GetSsjBossTodayKill(id):
                rewardRes = Game.res_mgr.res_reward.get(barrRes.rewardId)
                if rewardRes:
                    dReward = rewardRes.doReward()
                #是否已首通
                isFirst = self.player.boss.GetSsjBossFirst(id)
                if not isFirst:
                    self.player.boss.SetSsjBossFirst(id)
                    dReward.update(barrRes.firstReward)
                #设置击杀
                    self.player.boss.SetSsjBossTodayKill(id)
            #是否协助
            if pid != self.player.id:
                iHelpNum = self.player.boss.GetSsjBossTodayHelp()
                if iHelpNum < helpres.i:
                    rewardRes = Game.res_mgr.res_reward.get(barrRes.helpRewardId)
                    if rewardRes:
                        dHelpReward = rewardRes.doReward()
                        for iNo, iNum in dHelpReward.items():
                            if dReward.get(iNo):
                                dReward[iNo] += iNum
                            else:
                                dReward[iNo] = iNum

                    self.player.boss.SetSsjBossTodayHelp(iHelpNum+1)

            respBag = self.player.bag.add(dReward, constant.ITEM_ADD_SSJBOSS_REWARD, wLog=True)
        # 打包返回信息
        dUpdate = self.player.packRespBag(respBag)
        dUpdate["boss"] = self.player.boss.to_ssjboss_data([id])
        resp = {
            "id": id,
            "fightLog": fightLog,
            "allUpdate": dUpdate,
        }
        spawn(self.player.call, "ssjBossTZNotice", resp, noresult=True)


    def sendYwBossTZ(self, resp):
        spawn(self.player.call, "ywBossTZ", resp, noresult=True)



class BossLogicRpc(object):
    if 0:
        from game.mgr import logicgame as logic_md
        logic = logic_md.LogicGame()

    def QmBossReBorn(self, bossid):
        # boss复活广播(qmBossRebirth)
        #     全民bossid(id, int)
        log.info("=========QmBossReBorn========== %s", bossid)
        resp = dict(id=bossid)
        Game.player_mgr.broadcast("qmBossRebirth", resp)

    def QmBossBeKill(self, bossid, reTime):
        # boss死亡广播(qmBossDead)
        #     全民bossid(id, int)
        #     重生时间戳(time, int)
        log.info("=========QmBossBeKill========== %s %s", bossid, reTime)
        resp = dict(id=bossid, time=reTime)
        Game.player_mgr.broadcast("qmBossDead", resp)

    def YwBossBeKill(self, bossid):
        # boss死亡广播(ywBossDead)
        #     野外BossId(id, int)
        log.info("=========YwBossBeKill========== %s", bossid)
        resp = dict(id=bossid)
        Game.player_mgr.broadcast("ywBossDead", resp)

    def YwBossRunaway(self, idList):
        # boss逃跑广播(ywBossRunaway)
        #     野外BossId列表(idList, [int])
        log.info("=========YwBossRunaway========== %s", idList)
        resp = dict(idList=idList)
        Game.player_mgr.broadcast("ywBossRunaway", resp)
        args = []
        self.logic.sendSystemTemplateMSG(1105, args)

    def YwBossRefresh(self, idList):
        # boss复活广播(ywBossRebirth)
        #     野外BossId列表(idList, [int])
        log.info("=========YwBossRefresh========== %s", idList)
        resp = dict(idList=idList)
        Game.player_mgr.broadcast("ywBossRebirth", resp)
        args = []
        self.logic.sendSystemTemplateMSG(1104, args)







