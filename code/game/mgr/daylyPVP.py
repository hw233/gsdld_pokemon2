#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import time
import random
import pickle

from gevent import sleep
from game.common import utility
from grpc import DictExport, DictItemProxy, get_proxy_by_addr
from corelib import log, spawn
from game.models.daylyPVP import ModelDaylyPVP

from corelib.frame import Game, MSG_FRAME_STOP
from game.core.cycleData import CycleDay, CycleWeek

from game.define import constant, errcode, msg_define

import random
import config


def get_rpc_daylyPVP(force=0):

    if 3==int(config.serverNo[0:2]) and not hasattr(config, "p3cross"):
        print('test common daylyPVP')
        return Game.rpc_dayly_pvp_mgr_common

    if force:
        if hasattr(config, "day_addr"):
            return get_proxy_by_addr(config.day_addr, DaylyPVPMgr._rpc_name_)
        else:
            return Game.rpc_dayly_pvp_mgr_common

    days = Game.rpc_server_info.GetOpenDay()
    ares = Game.res_mgr.res_activity.get(constant.ACTIVITY_DAYLY_PVP)
    startD = ares.openDayRange[0]
    if startD <= days:
        if hasattr(config, "day_addr"):
            return get_proxy_by_addr(config.day_addr, DaylyPVPMgr._rpc_name_)
        else:
            return Game.rpc_dayly_pvp_mgr_common

    return Game.rpc_dayly_pvp_mgr_common

class DaylyPVPMgr(utility.DirtyFlag):
    _rpc_name_ = 'rpc_dayly_pvp_mgr'
    DATA_CLS = ModelDaylyPVP

    def __init__(self):
        utility.DirtyFlag.__init__(self)
        self.data = None

        self.cycleWeek = CycleWeek(self, keepCyc=2)

        self.players = {} #玩家缓存数据
        self.pid_matchId = {}

        self.save_cache = {}

        self._save_loop_task = None
        Game.sub(MSG_FRAME_STOP, self._frame_stop)

    def SetCurWeekRank(self, rankData):
        """本周排行榜"""
        self.cycleWeek.Set("DaylyPVPWeekRank", rankData)

    def GetCurWeekRank(self):
        """本周排行榜"""
        return self.cycleWeek.Query("DaylyPVPWeekRank", {})

    def GetLastWeekRank(self):
        """上周排行榜"""
        return self.cycleWeek.Query("DaylyPVPWeekRank", {}, iWhichCyc=-1)

    def start(self):
        self.data = self.DATA_CLS.load(Game.store, self.DATA_CLS.TABLE_KEY)
        if not self.data:
            self.data = self.DATA_CLS()
        else:
            self.load_from_dict(self.data.dataDict)
        self.data.set_owner(self)

        self._save_loop_task = spawn(self._saveLoop)

    def _frame_stop(self):
        if self._save_loop_task:
            self._save_loop_task.kill(block=False)
            self._save_loop_task = None

        self.save(forced=True, no_let=True)

    def _saveLoop(self):
        stime = 10 * 60
        while True:
            sleep(stime)
            try:
                self.save()
            except:
                log.log_except()

    def save(self, forced=False, no_let=False):
        self.data.save(Game.store, forced=forced, no_let=no_let)

    def load_from_dict(self, data):
        robots = data.get("robots", [])
        if robots:
            robots = pickle.loads(robots)
        for one in robots:
            matchId = one.get("matchId", 0)
            if not matchId:
                continue
            matchId_dict = self.players.setdefault(matchId, {})

            players = one.get("players", [])
            for player in players:
                pid = player.get("pid", 0)
                pdata = player.get("pdata", [])
                if not pid:
                    continue
                if not pdata:
                    continue
                matchId_dict[pid] = pdata

        self.cycleWeek.load_from_dict(data.get("cycleWeek", ""))

    def markDirty(self):
        utility.DirtyFlag.markDirty(self)
        self.data.modify()

    def to_save_dict(self, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            self.save_cache = {}
            if forced:
                data = self.players_to_save()
                self.save_cache["robots"] = pickle.dumps(data)
            self.save_cache["cycleWeek"] = self.cycleWeek.to_save_bytes()
        return self.save_cache

    def players_to_save(self):
        save = []
        for matchId, players in self.players.items():
            data = {}
            data["matchId"] = matchId
            data["players"] = []
            keys = list(players.keys())
            if len(keys) > 5:
                random_keys = random.sample(keys, 5)
            else:
                random_keys = keys
            for pid in random_keys:
                pdata = players.get(pid)
                pdata["isRobot"] = 1
                data["players"].append({"pid":pid, "pdata":pdata})
            save.append(data)
        return save

    def registerRobotData(self, serverNo, addr, fightData):
        fa = fightData.get("fa", 0)
        pid = fightData.get("pid", 0)
        matchId = self.getMatchId(fa)
        curMatchId = self.pid_matchId.get(pid)
        if curMatchId and matchId != curMatchId:
            matchId_dict = self.players.setdefault(curMatchId, {})
            pdata = matchId_dict.get(pid, {})
            if pdata:
                pdata["isRobot"] = 1

        matchId_dict = self.players.setdefault(matchId, {})
        if len(matchId_dict) < 50:
            matchId_dict[pid] = {
                "serverNo": serverNo,
                "addr": addr,
                "fightData": fightData,
                "isRobot": 0,
            }
            self.pid_matchId[pid] = matchId
        else:
            keys = list(matchId_dict.keys())
            key = random.choice(keys)
            matchId_dict.pop(key, None)
            matchId_dict[pid] = {
                "serverNo": serverNo,
                "addr": addr,
                "fightData": fightData,
                "isRobot": 0,
            }
            self.pid_matchId[pid] = matchId

    def getMatchId(self, fa):
        for fa_500, match_500 in Game.res_mgr.res_fa_pvpmatch.items():
            start_500, end_500 = fa_500
            if start_500 <= fa < end_500: #500范围
                for fa_50, match_50 in match_500.items():
                    start_50, end_50 = fa_50
                    if start_50 <= fa < end_50: #50范围
                        for fa_5, match_5 in match_50.items():
                            start_5, end_5 = fa_5
                            if start_5 <= fa < end_5: #5范围
                                for fa_1, match_1 in match_5.items():
                                    start_1, end_1 = fa_1
                                    if start_1 <= fa < end_1: #找到对应区间
                                        return match_1.id
        return max(list(Game.res_mgr.res_pvpmatch.keys()))

    def matchPvpData(self, pid, fa, exclude=[], lv=999):
        matchId = self.getMatchId(fa)
        if not matchId:
            return []
        exclude.append(pid)
        #各区间各取一个人 中低低
        upData = None
        iLen = len(Game.res_mgr.res_pvpmatch)
        for i in range(iLen):
            _matchId = matchId - i
            if _matchId < 1:
                break
            upData = self._match(exclude, _matchId, lv)
            if upData:
                break
        if upData:
            fightData = upData.get("fightData", {})
            exclude.append(fightData.get("pid", 0))
            # print("--------upData---------", fightData.get("pid", 0))

        curData = None
        delNum = random.randint(1, 2)
        if matchId > 2:
            for i in range(iLen):
                _matchId = matchId - delNum - i
                if _matchId < 1:
                    break
                curData = self._match(exclude, _matchId, lv)
                if curData:
                    break
        else:
            for i in range(iLen):
                _matchId = matchId - i
                if _matchId < 1:
                    break
                curData = self._match(exclude, _matchId, lv)
                if curData:
                    break

        if curData:
            fightData = curData.get("fightData", {})
            exclude.append(fightData.get("pid", 0))
            # print("--------curData---------", fightData.get("pid", 0))

        lowData = None
        delNum = random.randint(2, 3)
        if matchId > 3:
            for i in range(iLen):
                _matchId = matchId - delNum - i
                if _matchId < 1:
                    break
                lowData = self._match(exclude, _matchId, lv)
                if lowData:
                    break
        else:
            for i in range(iLen):
                _matchId = matchId - i
                if _matchId < 1:
                    break
                lowData = self._match(exclude, _matchId, lv)
                if lowData:
                    break

        if lowData:
            fightData = lowData.get("fightData", {})
            exclude.append(fightData.get("pid", 0))
            # print("--------lowData---------", fightData.get("pid", 0))

        if upData or curData or lowData:
            return upData, curData, lowData
        return []

    def _match(self, exclude, matchId, lv):
        matchId_dict = self.players.get(matchId, {})
        if not matchId_dict:
            return
        keys = list(matchId_dict.keys())
        for pid in exclude:
            if pid in keys:
                keys.remove(pid)

        useful = []
        for key in keys:
            pdata = matchId_dict.get(key, {})
            fightData = pdata.get("fightData", {})
            if fightData.get("lv", 0) < int(lv * 1.1 +3): #比自身等级1.1倍 + 3 的人
                useful.append(key)
        if useful:
            key = random.choice(useful)
            # print('------------_match------------', matchId, exclude, keys, key)
            return matchId_dict.get(key)

    def matchCustomData(self, matchId, exclude=[], lv=999):
        for i in range(len(Game.res_mgr.res_pvpmatch)):
            robotData = self._match(exclude, matchId, lv)
            if robotData:
                return robotData
            else:
                matchId += 1

    def sendWeekRankData(self, serverNo, addr, data):
        rankData = self.GetCurWeekRank()
        rankPid = rankData.get("rankPid", [])
        rankList = rankData.get("rankList", [])

        oneInfo = {
            "serverNo": serverNo,
            "addr": addr,
            "data": data,
        }
        pid = data.get("pid", 0)
        if rankList:
            if pid not in rankPid:
                last = rankList[-1]
                if last.get("data", {}).get("weekWin", 0) < data.get("weekWin", 0):
                    rankPid.append(pid)
                    rankList.append(oneInfo)
                    rankList.sort(key=lambda d:d.get("data", {}).get("weekWin", 0), reverse=True)
                    if len(rankList) > 100:
                        delData = rankList.pop(-1)
                        delPid = delData.get("data", {}).get("pid", 0)
                        if delPid in rankPid:
                            rankPid.remove(delPid)
                    rankData["rankPid"] = rankPid
                    rankData["rankList"] = rankList
                    self.SetCurWeekRank(rankData)
            else:
                for one in rankList:
                    if pid == one.get("data", {}).get("pid", 0):
                        one["serverNo"] = serverNo
                        one["addr"] = addr
                        one["data"] = data
                        break
                rankList.sort(key=lambda d: d.get("data", {}).get("weekWin", 0), reverse=True)
                rankData["rankList"] = rankList
                self.SetCurWeekRank(rankData)
        else:
            rankPid.append(pid)
            rankList.append(oneInfo)
            rankData["rankPid"] = rankPid
            rankData["rankList"] = rankList
            self.SetCurWeekRank(rankData)

    def getWeekRank(self):
        rankData = self.GetCurWeekRank()
        rankList = rankData.get("rankList", [])
        return rankList

    def getLastWeekRank(self):
        rankData = self.GetLastWeekRank()
        rankList = rankData.get("rankList", [])
        return rankList

    def getDaylyPVPRankData(self):
        return self.getWeekRank(), self.getLastWeekRank()

# class DaylyPVPPlayer(object):
#     def __init__(self, serverNo, addr, fightData):
#         self.pid = fightData.get("pid", 0)
#         self.addr = addr
#         self.serverNo = serverNo
#
#         self.matchId = 0
#
#     def SetMatchId(self, matchId):
#         self.matchId = matchId
#
#     def GetMatchId(self):
#         return self.matchId

class DaylyPVPMgrCommon(DaylyPVPMgr):
    _rpc_name_ = 'rpc_dayly_pvp_mgr_common'

    def sendWeekRankData(self, serverNo, addr, data):
        #本地无排行榜
        pass

    def getWeekRank(self):
        # 本地无排行榜
        return []

    def getLastWeekRank(self):
        # 本地无排行榜
        return []

    def getDaylyPVPRankData(self):
        return [], []


