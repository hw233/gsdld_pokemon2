#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import copy

from corelib.frame import spawn, Game
from game.define import constant

class MarryPlayerRpc(object):
    if 0:
        from game.core import player as player_md
        player = player_md.Player()

    def getMarryStatus(self):
        return self.player.marry.getMarryStatus()


    def isMarriedToday(self):
        return self.player.marry.isMarriedToday()


    def marryPush(self, data):
        spawn(self.player.call, "marryPush", data, noresult=True)


    def marryResultPush(self, data):
        spawn(self.player.call, "marryResultPush", data, noresult=True)


    def marrySomeone(self, pid, name, kind, marryId):
        marryRes = Game.res_mgr.res_marry.get(marryId, None)
        if not marryRes:
            return 0

        mailRes = Game.res_mgr.res_mail.get(constant.MAIL_ID_MARRY_REWARD, None)

        self.player.marry.marrySomeone(pid, kind, marryId)
        reward = copy.deepcopy(marryRes.reward)
        if self.player.marry.getMarryTimes() == 1:
            for k, v in marryRes.firstReward.items():
                reward.setdefault(k, 0)
                reward[k] += v

        self.player.house.setType(marryId)

        content = mailRes.content % name
        Game.rpc_mail_mgr.sendPersonMail(self.player.id, mailRes.title, content, reward)
        dUpdate = {}
        dUpdate["wallet"] = self.player.wallet.to_update_data([constant.CURRENCY_BINDGOLD, constant.CURRENCY_GOLD])
        dUpdate["houseInfo"] = self.player.house.to_init_data(),
        dUpdate["marryInfo"] = self.player.marry.to_init_data(),
        pushData = {
            "result": 1,
            "targetPid": pid,
            "allUpdate": dUpdate,
            "houseInfo": self.player.house.to_init_data(),
            "marryInfo": self.player.marry.to_init_data(),
        }
        self.marryResultPush(pushData)


    def marryPowerPush(self, id, en, num, pid, name):
        self.player.marry.marryPowerPush(id, en, num, pid, name)

        dUpdate = {}
        dUpdate["marryInfo"] = self.player.marry.to_init_data()
        pushData = {
            "id": id,  # 配置表id
            "allUpdate": dUpdate,
        }
        spawn(self.player.call, "marryPowerPush", pushData, noresult=True)


    def divorce(self):
        self.player.marry.divorce()
        spawn(self.player.call, "divorcePush", {}, noresult=True)


    def addHouseExp(self, exp, kind):
        self.player.house.addUnrecvExp(exp, kind)
        spawn(self.player.call, "houseUpgradePush", {}, noresult=True)