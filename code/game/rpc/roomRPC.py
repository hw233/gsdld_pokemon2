#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import ujson
import time
import copy

from corelib.frame import spawn, Game, log
from game.define import constant, msg_define

class RoomLogicRpc(object):
    if 0:
        from game.mgr import logicgame as logic_md
        logic = logic_md.LogicGame()

    def roomMsg(self, msgtype, ids, data):
        # print "******",msgtype,ids,data

        if msgtype == "msg":
            if data["type"] == 3:
                pids = []
                for tid in ids:
                    pid = Game.player_mgr.getTeamid2pid(tid)
                    pids.append(pid)
            else:
                pids = ids
            resp = dict(rid=data["rid"], content=data["content"])
            Game.player_mgr.broadcast("worldMSGNotice", resp, keys=pids)
            return

        if data["type"] == 1:
            if msgtype == "bye":
                Game.player_mgr.broadcast("pushHusongFinish", {"id": data["id"]}, keys=ids)
                # spawn(self.owner.call, "pushHusongFinish", {"id": data["id"]}, noresult=True)
        elif data["type"] == 2:
            if msgtype == "bye":
                Game.player_mgr.broadcast("diaoyuExitPush", {"id": data["id"]}, keys=ids)
                # spawn(self.owner.call, "diaoyuExitPush", {"id": data["id"]}, noresult=True)
            elif msgtype == "update":
                Game.player_mgr.broadcast("diaoyuStatusPush", {"list": data}, keys=ids)
                # spawn(self.owner.call, "diaoyuStatusPush", {"list": data}, noresult=True)
            elif msgtype == "hello":
                Game.player_mgr.broadcast("diaoyuEntetPush", {"list": data}, keys=ids)
                # spawn(self.owner.call, "diaoyuEntetPush", {"list": data}, noresult=True)
        elif data["type"] == 3:
            pids = []
            for tid in ids:
                pid = Game.player_mgr.getTeamid2pid(tid)
                pids.append(pid)

            if msgtype == "bye":
                Game.player_mgr.broadcast("wakuangExitPush", {"id": data["id"]}, keys=pids)
                # spawn(self.owner.call, "wakuangExitPush", {"id": data["id"]}, noresult=True)
            elif msgtype == "update":
                Game.player_mgr.broadcast("wakuangStatusPush", {"list": data}, keys=pids)
                # spawn(self.owner.call, "wakuangStatusPush", {"list": data}, noresult=True)
            elif msgtype == "hello":
                Game.player_mgr.broadcast("wakuangEntetPush", {"list": data}, keys=pids)
                # spawn(self.owner.call, "wakuangEntetPush", {"list": data}, noresult=True)
        elif data["type"] == 4:
            if msgtype == "bye":
                Game.player_mgr.broadcast("kfbossExitPush", {"id": data["id"]}, keys=ids)
                # spawn(self.owner.call, "kfbossExitPush", {"id": data["id"]}, noresult=True)
            elif msgtype == "update":
                Game.player_mgr.broadcast("kfbossStatusPush", {"list": data}, keys=ids)
                # spawn(self.owner.call, "kfbossStatusPush", {"list": data}, noresult=True)
            elif msgtype == "hello":
                Game.player_mgr.broadcast("kfbossEntetPush", {"list": data}, keys=ids)
                # spawn(self.owner.call, "kfbossEntetPush", {"list": data}, noresult=True)
            elif msgtype == "gmsg":
                Game.player_mgr.broadcast("kfbossMsgPush", {"list": data}, keys=ids)
                # spawn(self.owner.call, "kfbossMsgPush", {"list": data}, noresult=True)
        elif data["type"] == 5:
            if msgtype == "gmsg":
                Game.player_mgr.broadcast("gongchengMsgPush", {"list": data}, keys=ids)
                # spawn(self.owner.call, "gongchengMsgPush", {"list": data}, noresult=True)
                Game.rpc_guild_mgr.receive_gongcheng(data, _no_result=True)
        elif data["type"] == 6:
            # if msgtype == "bye":
            #     Game.player_mgr.broadcast("jiujiyishouExitPush", {"id": data["id"]}, keys=ids)
            #     # spawn(self.owner.call, "jiujiyishouExitPush", {"id": data["id"]}, noresult=True)
            # elif msgtype == "update":
            #     Game.player_mgr.broadcast("jiujiyishouStatusPush", {"list": data}, keys=ids)
            #     # spawn(self.owner.call, "jiujiyishouStatusPush", {"list": data}, noresult=True)
            # elif msgtype == "hello":
            #     Game.player_mgr.broadcast("jiujiyishouEntetPush", {"list": data}, keys=ids)
            #     # spawn(self.owner.call, "jiujiyishouEntetPush", {"list": data}, noresult=True)

            if msgtype == "gmsg":
                Game.player_mgr.broadcast("jiujiyishouMsgPush", {"list": data}, keys=ids)
                # spawn(self.owner.call, "jiujiyishouMsgPush", {"list": data}, noresult=True)

    def diaoyuRank(self, index, data):

        reward = {}
        res = Game.res_mgr.res_diaoyurank.get(index + 1, None)
        if not res:
            res = Game.res_mgr.res_common.get("diaoyuRankReward")
            reward = res.arrayint2
        else:
            reward = res.reward

        mailRes = Game.res_mgr.res_mail.get(constant.MAIL_ID_DIAOYU_REWARD, None)
        content = mailRes.content % str(index + 1)
        Game.rpc_mail_mgr.sendPersonMail(int(data["id"]), mailRes.title, content, reward, push=False)

        from game.mgr.player import get_rpc_player
        proxy = get_rpc_player(data["id"])
        if not proxy:
            return

        proxy.diaoyuCleanScore()

    def gongchengCityReward(self, city, pid, type, num):
        res = Game.res_mgr.res_gongcheng.get(city, None)
        if not res:
            return False

        mailRes = Game.res_mgr.res_mail.get(type, None)
        if not mailRes:
            return False

        reward_org = {}

        if type == constant.MAIL_ID_GONGCHENG_ATK_SUCC:
            reward_org = res.ATK_SUCC
        elif type == constant.MAIL_ID_GONGCHENG_DEF_FAIL:
            reward_org = res.DEF_FAIL
        elif type == constant.MAIL_ID_GONGCHENG_ATK_FAIL:
            reward_org = res.ATK_FAIL
        elif type == constant.MAIL_ID_GONGCHENG_DEF_SUCC:
            reward_org = res.DEF_SUCC

        reward = copy.deepcopy(reward_org)

        for k, v in reward.items():
            reward[k] = v * num

        # print 'xxxxxxxxxx==1',num,reward_org
        # print 'xxxxxxxxxx==2',num,reward

        if reward:
            title = mailRes.title % res.name
            content = mailRes.content % (res.name, num, num)

            Game.rpc_mail_mgr.sendPersonMail(pid, title, content, reward)

        return True

    def wakuangRankMonth(self, index, data):

        res = Game.res_mgr.res_wakuangrankmonth.get(index + 1, None)
        if res:

            mailRes = Game.res_mgr.res_mail.get(constant.MAIL_ID_WAKUANG_MONTH_REWARD, None)
            content = mailRes.content % str(index + 1)

            for pid in data["pid"]:
                Game.rpc_mail_mgr.sendPersonMail(pid, mailRes.title, content, res.reward, push=False)

    def wakuangRankDay(self, index, data):

        res = Game.res_mgr.res_wakuangrankday.get(index + 1, None)
        if res:

            mailRes = Game.res_mgr.res_mail.get(constant.MAIL_ID_WAKUANG_DAY_REWARD, None)
            content = mailRes.content % str(index + 1)

            for pid in data["pid"]:
                Game.rpc_mail_mgr.sendPersonMail(pid, mailRes.title, content, res.reward, push=False)


    def wakuangGetHpInt(self, pids):
        from game.mgr.player import get_rpc_player

        hp = []

        for pid in pids:
            other = get_rpc_player(pid)
            if other:
                v = other.wakuangGetHpInt()
                hp.append(v)

        return hp

    def wakuangFight(self, name, redFight, blueList, sredhp, sid):
        from game.mgr.player import get_rpc_player

        blueFight = []
        sbluehp = {}
        for pid in blueList:
            other = get_rpc_player(pid)
            if other:
                blueFight.append(other.GetFightData(constant.BATTLE_ARRAY_TYPE_NORMAL))
                sbluehp[pid] = other.wakuangHpGet()

        # print '!!!!!!!!!!BBB',redFight,blueList,blueFight

        fightobj = Game.fight_mgr.createFight(constant.FIGHT_TYPE_220)
        fightobj.init_players_by_data(redFight, blueFight)

        allTeamHp = {}
        if not fightobj.teamIsAllDead(sredhp):
            # print '===============red is not all dead!'
            allTeamHp[constant.FIGHT_TEAM_RED] = sredhp
        if not fightobj.teamIsAllDead(sbluehp):
            # print '===============blue is not all dead!'
            allTeamHp[constant.FIGHT_TEAM_BLUE] = sbluehp
        fightobj.FixFighterHP(allTeamHp)

        fightobj.SetRounds(30)
        fightLog = fightobj.doFight(1)
        fightResult = fightLog["result"].get("win", 0)

        redhp = fightLog["resultInfo"][constant.FIGHT_TEAM_RED]
        bluehp = fightLog["resultInfo"][constant.FIGHT_TEAM_BLUE]
        if fightobj.teamIsAllDead(redhp):
            redhp = {}
        if fightobj.teamIsAllDead(bluehp):
            bluehp = {}

        # 打包返回信息
        resp = {
            "fightLog": fightLog,
        }

        for pid in blueList:
            other = get_rpc_player(pid)
            if other:
                other.wakuangHpSet(bluehp.get(pid, {}))

                if fightResult:
                    resp["attack"] = 0
                    other.wakuangFightLog(resp)
                else:
                    other.wakuangFightBack(name, sid)
        resp["redhp"] = redhp
        # from corelib.data import json_dumps
        # Game.glog.log2File("wakuangFight", "%s" % json_dumps(fightLog))
        return resp


    def kfbossRank(self, index, data):

        res = Game.res_mgr.res_kfbossrank.get(index + 1, None)
        if res:

            mailRes = Game.res_mgr.res_mail.get(constant.MAIL_ID_KFBOSS_REWARD, None)
            content = mailRes.content % str(index + 1)

            for pid in data["pid"]:
                Game.rpc_mail_mgr.sendPersonMail(pid, mailRes.title, content, res.reward, push=False)

    def gongchengPersonScore(self, index, pid):

        res = Game.res_mgr.res_gongchengPersonrRank.get(index + 1, None)
        if res:
            mailRes = Game.res_mgr.res_mail.get(constant.MAIL_ID_GONGCHENG_PERSON, None)
            content = mailRes.content % str(index + 1)

            Game.rpc_mail_mgr.sendPersonMail(pid, mailRes.title, content, res.reward, push=False)

    def gongchengGuildScore(self, index, pids):

        res = Game.res_mgr.res_gongchengGangRank.get(index + 1, None)
        if res:

            mailRes = Game.res_mgr.res_mail.get(constant.MAIL_ID_GONGCHENG_GUILD, None)
            content = mailRes.content % str(index + 1)

            for pid in pids:
                Game.rpc_mail_mgr.sendPersonMail(pid, mailRes.title, content, res.reward, push=False)

    def gongchengGuildReward(self, cityname, reward, pids):

        mailRes = Game.res_mgr.res_mail.get(constant.MAIL_ID_GONGCHENG_GUILDREWARD, None)
        title = mailRes.title % cityname
        content = mailRes.content % cityname

        for pid in pids:
            Game.rpc_mail_mgr.sendPersonMail(pid, title, content, reward, push=False)

    def gongchengNotiyGuild(self, guildid, cityid, atk):

        nowtime = time.time()
        rpc_guild = get_rpc_guild(guildid)
        if not rpc_guild:
            return

        from game.mgr.player import get_rpc_player

        members = rpc_guild.getMembers()
        for one in members:
            rid = one.get("rid", 0)
            if not rid:
                continue
            # isRobot = one.get("isRobot", 1)
            # if isRobot:
            #     continue
            rpc_player = get_rpc_player(rid)
            if not rpc_player:
                continue
            rpc_player.gongchengNotiyGuild(cityid, atk, nowtime)

    def robHusongCar(self, robid, data, fdata, historydata):
        from game.mgr.player import get_rpc_player
        proxy = get_rpc_player(data["id"])
        if not proxy:
            return

        return proxy.robHusongCar(robid, data, fdata, historydata)

    def diaoyuRob(self, robid, data, fdata, historydata):
        from game.mgr.player import get_rpc_player
        proxy = get_rpc_player(data["id"])
        if not proxy:
            return

        return proxy.diaoyuRob(robid, data, fdata, historydata)

    def kfbossFight(self, robid, data, fdata, historydata):
        from game.mgr.player import get_rpc_player
        proxy = get_rpc_player(data["id"])
        if not proxy:
            return

        return proxy.kfbossFight(robid, data, fdata, historydata)

    def revengeHusongCar(self, robid, data, fdata, historydata):
        from game.mgr.player import get_rpc_player
        proxy = get_rpc_player(data["id"])
        if not proxy:
            return

        return proxy.revengeHusongCar(robid, data, fdata, historydata)

    def jiujiyishouIn(self, id, jiujiyishouId, ppid, addr):
        from game.mgr.player import get_rpc_player
        proxy = get_rpc_player(id)
        if not proxy:
            return

        return proxy.jiujiyishouIn(jiujiyishouId, ppid, addr)

    def jiujiyishouQuit(self, id, ppid):
        from game.mgr.player import get_rpc_player
        proxy = get_rpc_player(id)
        if not proxy:
            return

        proxy.jiujiyishouQuit(ppid)

    def jiujiyishouFightPush(self, id, jiujiyishouId, fbId, fightLog):
        from game.mgr.player import get_rpc_player
        proxy = get_rpc_player(id)
        if not proxy:
            return

        proxy.jiujiyishouFightPush(jiujiyishouId, fbId, fightLog)

    def jiujiyishouResp(self, id):
        from game.mgr.player import get_rpc_player
        proxy = get_rpc_player(id)
        if not proxy:
            return

        proxy.jiujiyishouResp()

