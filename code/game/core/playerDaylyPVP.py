#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import pickle
import time
import datetime
from game.common import utility
from corelib.frame import Game, spawn
from game.define import constant, msg_define
from corelib import gtime, spawn_later

from game.mgr.daylyPVP import get_rpc_daylyPVP

import app
import config

from game.core.cycleData import CycleDay, CycleWeek

class PlayerDaylyPVP(utility.DirtyFlag):
    def __init__(self, owner):
        utility.DirtyFlag.__init__(self)
        self.owner = owner      # 拥有者

        self.cycleDay = CycleDay(self)
        self.cycleWeek = CycleWeek(self)

        self.challengeNum = 0 #挑战次数
        self.lastRecoverTime = 0 #最后一次恢复时间
        self.TotalWin = 0 #历史总战胜次数
        self.TotalFightNum = 0 #历史总挑战次数
        self.winMax = 0 #历史最大连胜次数
        self.revengeNum = 0 #历史复仇次数
        self.beChallengeData = [] #复仇列表

        self.save_cache = {}


    def markDirty(self):
        utility.DirtyFlag.markDirty(self)
        if self.owner:
            self.owner.markDirty()

    def SetTodayWinStreak(self, num):
        """今日已连胜"""
        self.cycleDay.Set("todayDaylyPVPWinStreak", num)
        if num > self.winMax:
            self.winMax = num
            self.markDirty()

    def GetTodayWinStreak(self):
        """今日已连胜"""
        return self.cycleDay.Query("todayDaylyPVPWinStreak", 0)

    def SetTodayRevengeNum(self, num):
        """今日已复仇次数"""
        self.cycleDay.Set("todayDaylyPVPRevengeNum", num)

    def GetTodayRevengeNum(self):
        """今日已复仇次数"""
        return self.cycleDay.Query("todayDaylyPVPRevengeNum", 0)

    def SetWeekWin(self, num):
        """本周胜利次数"""
        self.cycleWeek.Set("DaylyPVPWeekWin", num)

    def GetWeekWin(self):
        """本周胜利次数"""
        return self.cycleWeek.Query("DaylyPVPWeekWin", 0)

    def GetLastWeekWin(self):
        """上周胜利次数"""
        return self.cycleWeek.Query("DaylyPVPWeekWin", 0, iWhichCyc=-1)

    def SetHasGetWeekRankReward(self, rs):
        """周排行榜奖励是否已领取"""
        self.cycleWeek.Set("DaylyPVPHasGetWeekRankReward", rs)

    def GetHasGetWeekRankReward(self):
        """周排行榜奖励是否已领取"""
        return self.cycleWeek.Query("DaylyPVPHasGetWeekRankReward", 0)

    def SetTodayBuyChallengeNum(self, num):
        """今日已购买挑战次数"""
        self.cycleDay.Set("todayDaylyPVPBuyChallengeNum", num)

    def GetTodayBuyChallengeNum(self):
        """今日已购买挑战次数"""
        return self.cycleDay.Query("todayDaylyPVPBuyChallengeNum", 0)

    def SetTodayBeChallengeNum(self, num):
        """今日被挑战次数"""
        self.cycleDay.Set("todayDaylyPVPBeChallengeNum", num)

    def GetTodayBeChallengeNum(self):
        """今日被挑战次数"""
        return self.cycleDay.Query("todayDaylyPVPBeChallengeNum", 0)

    def SetTodayGetRewardList(self, data):
        """今日已领取连胜奖励"""
        self.cycleDay.Set("todayDaylyPVPGetRewardList", data)

    def GetTodayGetRewardList(self):
        """今日已领取连胜奖励"""
        return self.cycleDay.Query("todayDaylyPVPGetRewardList", [])

    def SetTodayChallengeData(self, data):
        """今日挑战列表"""
        self.cycleDay.Set("todayDaylyPVPChallengeData", data)

    def GetTodayChallengeData(self):
        """今日挑战列表"""
        return self.cycleDay.Query("todayDaylyPVPChallengeData", [])

    def SetTodayDoChallengeNum(self, num):
        """当天发起挑战次数"""
        self.cycleDay.Set("todayDaylyPVPDoChallengeNum", num)

    def GetTodayDoChallengeNum(self):
        """当天发起挑战次数"""
        return self.cycleDay.Query("todayDaylyPVPDoChallengeNum", 0)

    def SetTodayChallengeWinNum(self, num):
        """当天击败对手 / 人"""
        self.cycleDay.Set("todayDaylyPVPChallengeWinNum", num)

    def GetTodayChallengeWinNum(self):
        """当天击败对手 / 人"""
        return self.cycleDay.Query("todayDaylyPVPChallengeWinNum", 0)

    def SetTodayChallengeMaxWin(self, num):
        """当天最高连胜"""
        self.cycleDay.Set("todayDaylyPVPChallengeMaxWin", num)

    def GetTodayChallengeMaxWin(self):
        """当天最高连胜"""
        return self.cycleDay.Query("todayDaylyPVPChallengeMaxWin", 0)

    def SetTodayRevengeWin(self, num):
        """当天复仇成功次数"""
        self.cycleDay.Set("todayDaylyPVPRevengeWin", num)

    def GetTodayRevengeWin(self):
        """当天复仇成功次数"""
        return self.cycleDay.Query("todayDaylyPVPRevengeWin", 0)

    def SetLastWeekRank(self, rank):
        """上周跨服排名名次"""
        self.cycleDay.Set("todayDaylyPVPLastWeekRank", rank)

    def GetLastWeekRank(self):
        """上周跨服排名名次"""
        return self.cycleDay.Query("todayDaylyPVPLastWeekRank", 0)


    # 存库数据
    def to_save_dict(self, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            self.save_cache = {}
            self.save_cache["cycleDay"] = self.cycleDay.to_save_bytes()
            self.save_cache["cycleWeek"] = self.cycleWeek.to_save_bytes()
            self.save_cache["challengeNum"] = self.challengeNum
            self.save_cache["lastRecoverTime"] = self.lastRecoverTime
            self.save_cache["TotalWin"] = self.TotalWin
            self.save_cache["TotalFightNum"] = self.TotalFightNum
            self.save_cache["beChallengeData"] = pickle.dumps(self.beChallengeData)
            self.save_cache["winMax"] = self.winMax
            self.save_cache["revengeNum"] = self.revengeNum
        return self.save_cache

    #读库数据初始化
    def load_from_dict(self, data):
        
        self.cycleDay.load_from_dict(data.get("cycleDay", ""))
        self.cycleWeek.load_from_dict(data.get("cycleWeek", ""))

        numRes = Game.res_mgr.res_common.get("pvpChallengeNumMax")
        self.challengeNum = data.get("challengeNum", numRes.i)  # 挑战次数 初始3次
        self.lastRecoverTime = data.get("lastRecoverTime", 0)  # 最后一次恢复时间
        self.TotalWin = data.get("TotalWin", 0)  # 历史总战胜次数
        self.TotalFightNum = data.get("TotalFightNum", 0) # 历史总挑战次数
        self.winMax = data.get("winMax", 0)  # 历史最大连胜次数
        self.revengeNum = data.get("revengeNum", 0)  # 历史复仇次数
        try:
            self.beChallengeData = data.get("beChallengeData", [])
            if self.beChallengeData:
                self.beChallengeData = pickle.loads(self.beChallengeData)
        except:
            self.beChallengeData = []

        #判断离线时长
        cdRes = Game.res_mgr.res_common.get("pvpChallengeNumCD")
        now = int(time.time())
        add = int((now - self.lastRecoverTime)/cdRes.i)
        self.challengeNum += add
        if self.challengeNum > numRes.i:
            self.challengeNum = numRes.i

        #设定最后一次恢复时间
        nowhour = gtime.current_hour()
        refresh = (0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22)
        last = 0
        for hour in refresh:
            if nowhour < hour:
                break
            last = hour

        #今日凌晨时间
        zero_day_time = int(gtime.zero_day_time())
        self.lastRecoverTime = zero_day_time + 3600*last

        nextRecoverTime = self.lastRecoverTime + 7200

        self.recover_task = spawn_later(nextRecoverTime-now, self.recoverChallengeNum)

    def recoverChallengeNum(self):
        if self.recover_task:
            self.recover_task.kill(block=False)
            self.recover_task = None
        numRes = Game.res_mgr.res_common.get("pvpChallengeNumMax")
        self.challengeNum += 1
        if self.challengeNum > numRes.i:
            self.challengeNum = numRes.i
        self.lastRecoverTime = int(time.time())
        self.recover_task = spawn_later(7200, self.recoverChallengeNum)
        self.markDirty()

    def uninit(self):
        if self.recover_task:
            self.recover_task.kill(block=False)
            self.recover_task = None

    #登录初始化下发数据
    def to_init_data(self):
        init_data = {}
        spawn(self.registerRobotData, config.serverNo, self.owner.GetFightData(constant.BATTLE_ARRAY_TYPE_NORMAL))  # 用额外的协程，避免卡死
        spawn(self.sendWeekRankData)  # 用额外的协程，避免卡死
        return init_data

    #零点更新的数据
    def to_wee_hour_data(self):
        init_data = {}
        return init_data

    def registerRobotData(self, serverNo, fightData):
        proxy = get_rpc_daylyPVP()
        if proxy:
            proxy.registerRobotData(serverNo, app.addr, fightData, _no_result=True)

    def no2id(self, no):
        serverNoClient = 0
        resId = Game.res_mgr.res_no2id_kuafuMap.get(no)
        if resId:
            res = Game.res_mgr.res_kuafuMap.get(resId)
            if res:
                serverNoClient = res.serverNoClient
        return serverNoClient

    def getDaylyPVPData(self, exclude=[]):
        challengeData = self.GetTodayChallengeData()
        if challengeData:
            return challengeData
        proxy = get_rpc_daylyPVP()
        if proxy:
            challengeData = proxy.matchPvpData(self.owner.id, self.owner.base.fa, exclude, self.owner.base.lv)
            if challengeData:
                upData, curData, lowData = challengeData
                if upData:
                    upData["sendNotice"] = 1
                self.SetTodayChallengeData(challengeData)
            else:
                fightData = self.owner.GetFightData(constant.BATTLE_ARRAY_TYPE_NORMAL)
                randomNames = utility.getRandomName(3)

                fightData["name"] = randomNames[0]
                upData = {
                    "serverNo": config.serverNo,
                    "addr": app.addr,
                    "fightData": fightData,
                    "isRobot": 1,
                }
                fightData["name"] = randomNames[1]
                curData = {
                    "serverNo": config.serverNo,
                    "addr": app.addr,
                    "fightData": fightData,
                    "isRobot": 1,
                }
                fightData["name"] = randomNames[2]
                lowData = {
                    "serverNo": config.serverNo,
                    "addr": app.addr,
                    "fightData": fightData,
                    "isRobot": 1,
                }
                self.SetTodayChallengeData([upData, curData, lowData])
        return challengeData

    def addBeChallengeRobotData(self):
        proxy = get_rpc_daylyPVP(force=1)
        if proxy:
            robotData = proxy.matchCustomData(1, exclude=[self.owner.id], lv=self.owner.base.lv)
            if robotData:
                beChallengeData = self.GetBeChallengeData()
                robotData["fightTime"] = int(time.time())
                robotData["isRobot"] = 1
                robotData["isGuide"] = 1
                robotData["isWin"] = 1
                beChallengeData.insert(0, robotData)
                self.SetBeChallengeData(beChallengeData)
            else:
                fightData = self.owner.GetFightData(constant.BATTLE_ARRAY_TYPE_NORMAL)
                randomNames = utility.getRandomName(3)

                fightData["name"] = randomNames[0]
                robotData = {
                    "serverNo": config.serverNo,
                    "addr": app.addr,
                    "fightData": fightData,
                    "isRobot": 1,
                }

                beChallengeData = self.GetBeChallengeData()
                robotData["fightTime"] = int(time.time())
                robotData["isRobot"] = 1
                robotData["isGuide"] = 1
                robotData["isWin"] = 1
                beChallengeData.insert(0, robotData)
                self.SetBeChallengeData(beChallengeData)

    def SetBeChallengeData(self, data):
        """被挑战列表"""
        self.beChallengeData = data
        self.markDirty()

    def GetBeChallengeData(self):
        """被挑战列表"""
        resp = []
        # 只保留一天的
        now = int(time.time())
        for oneData in self.beChallengeData:
            fightTime = oneData.get("fightTime", 0)
            if now - fightTime < 3600*24:
                resp.append(oneData)
        self.SetBeChallengeData(resp)
        return self.beChallengeData

    def SetRevengeNum(self, num): # 历史复仇次数
        self.revengeNum = num
        self.markDirty()

    def GetRevengeNum(self): # 历史复仇次数
        return self.revengeNum

    def SetChallengeNum(self, num):
        self.challengeNum = num
        self.markDirty()

    def GetChallengeNum(self):
        return self.challengeNum

    def SetTotalWin(self, num):
        self.TotalWin = num
        self.markDirty()

    def GetTotalWin(self):
        return self.TotalWin

    def SetTotalFightNum(self, num):
        self.TotalFightNum = num
        self.markDirty()

    def GetTotalFightNum(self):
        return self.TotalFightNum

    def checkRefresh(self):
        reset = 1
        exclude = []
        for oneData in self.getDaylyPVPData():
            if not oneData:
                continue
            isWin = oneData.get("isWin", 0)
            fightData = oneData.get("fightData", {})
            pid = fightData.get("pid", 0)
            exclude.append(pid)
            if not isWin:
                reset = 0
                break
        if reset:
            self.SetTodayChallengeData([])
            self.getDaylyPVPData(exclude)

    def sendWeekRankData(self):
        proxy = get_rpc_daylyPVP()
        if proxy:
            data = {
                "pid": self.owner.id,
                "name": self.owner.name,
                "weekWin": self.GetWeekWin(),
            }
            proxy.sendWeekRankData(config.serverNo, app.addr, data, _no_result=True)

    def getDaylyPVPRankData(self):
        proxy = get_rpc_daylyPVP()
        if proxy:
            return proxy.getDaylyPVPRankData()

    def packRivalList(self):
        days = self.owner.base.GetServerOpenDay()
        ares = Game.res_mgr.res_activity.get(constant.ACTIVITY_DAYLY_PVP)
        startD = ares.openDayRange[0]
        kf = 0
        if startD <= days:
            kf = 1

        rivalList = []
        for oneData in self.getDaylyPVPData():
            if not oneData:
                continue
            fightData = oneData.get("fightData", {})
            isWin = oneData.get("isWin", 0)
            name = fightData.get("name", '')
            if kf:
                serverNo = oneData.get("serverNo", 0)
                sid = self.no2id(serverNo)
                name = name + ".S" + str(sid)
            rival = {
                "pid": fightData.get("pid", 0),
                "name": name,
                "sex": fightData.get("sex", 0),
                "vipLv": fightData.get("vipLv", 0),
                "lv": fightData.get("lv", 0),
                "fa": fightData.get("fa", 0),
                "isWin": isWin,

                "portrait": fightData.get("portrait", 0),
                "headframe": fightData.get("headframe", 0),
            }
            rivalList.append(rival)
        return rivalList

    def packRevengeList(self):
        days = self.owner.base.GetServerOpenDay()
        ares = Game.res_mgr.res_activity.get(constant.ACTIVITY_DAYLY_PVP)
        startD = ares.openDayRange[0]
        kf = 0
        if startD <= days:
            kf = 1

        revengeList = []
        for oneData in self.GetBeChallengeData():
            if not oneData:
                continue
            fightData = oneData.get("fightData", {})
            name = fightData.get("name", '')
            if kf:
                serverNo = oneData.get("serverNo", 0)
                sid = self.no2id(serverNo)
                name = name + ".S" + str(sid)
            revenge = {
                "pid": fightData.get("pid", 0),
                "name": name,
                "sex": fightData.get("sex", 0),
                "vipLv": fightData.get("vipLv", 0),
                "lv": fightData.get("lv", 0),
                "fa": fightData.get("fa", 0),
                "isRevenge": oneData.get("isRevenge", 0),
                "revengeWin": oneData.get("revengeWin", 0),
                "fightTime": oneData.get("fightTime", 0),
                "isWin": oneData.get("isWin", 0),
                "isDouble": oneData.get("isDouble", 0),
                "isGuide": oneData.get("isGuide", 0),
                "portrait": fightData.get("portrait", 0),
                "headframe": fightData.get("headframe", 0),
            }
            revengeList.append(revenge)
        return revengeList