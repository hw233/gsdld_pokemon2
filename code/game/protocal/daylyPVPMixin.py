#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import random

from game.define import errcode, constant, msg_define
from game import Game

from corelib import log

from grpc import DictExport, DictItemProxy, get_proxy_by_addr
from corelib import spawn

import app
import config
from game.fight import createFight

class DaylyPVPMixin(object):
    if 0:
        from game.core import player as player_md
        player = player_md.Player()

    # 获取抢夺数据(getDaylyPVPData)
    # 请求
    # 返回
    #     附近对手列表(rivalList, [json])
    #         玩家id(pid, int)
    #         名字(name, string)
    #         性别(sex, int)
    #         vip等级(vipLv, int)
    #         等级(lv, int)
    #         战力(fa, int)
    #         是否已击败(isWin, int)
    #     复仇列表(revengeList, [json])
    #         玩家id(pid, int)
    #         名字(name, string)
    #         性别(sex, int)
    #         vip等级(vipLv, int)
    #         等级(lv, int)
    #         战力(fa, int)
    #         是否已复仇(isRevenge, int)
    #         复仇是否胜利(revengeWin, int)
    #         时间(fightTime, int)
    #         是否胜利(isWin, int)
    #     今日连胜数(winStreak, int)
    #     剩余挑战次数(challengeNum, int)
    #     今日已购买次数(buyNum, int)
    #     已领取连胜奖励列表(getRewardList, [int])
    #     本周击败对手(weekWin, int)
    #     最后一次恢复时间(recoverTime, int)
    #     主动推送刷新(allUpdate,json)
    #         游戏模型-货币
    #         游戏模型-角色背包
    #     总击败对手人数(TotalWin,int)
    def rc_getDaylyPVPData(self):
        # 打包返回信息
        dUpdate = {}
        dUpdate["wallet"] = self.player.wallet.to_update_data([constant.CURRENCY_DAYLY_PVP_COIN])
        resp = {
            "rivalList": self.player.daylypvp.packRivalList(),
            "revengeList": self.player.daylypvp.packRevengeList(),
            "winStreak": self.player.daylypvp.GetTodayWinStreak(), #今日连胜数
            "challengeNum": self.player.daylypvp.GetChallengeNum(), #剩余挑战次数
            "buyNum": self.player.daylypvp.GetTodayBuyChallengeNum(), #今日已购买次数
            "getRewardList": self.player.daylypvp.GetTodayGetRewardList(), #已领取连胜奖励列表
            "weekWin": self.player.daylypvp.GetWeekWin(), #本周击败对手
            "recoverTime": self.player.daylypvp.lastRecoverTime, #最后一次恢复时间
            "allUpdate": dUpdate,
            "TotalWin": self.player.daylypvp.TotalWin, #总击败对手人数
        }
        return 1, resp

    # 挑战对手(daylyPVPChallenge)
    # 请求
    #     玩家id(pid, int)
    # 返回
    #     附近对手列表(rivalList, [json])
    #         玩家id(pid, int)
    #         名字(name, string)
    #         性别(sex, int)
    #         vip等级(vipLv, int)
    #         等级(lv, int)
    #         战力(fa, int)
    #         是否已击败(isWin, int)
    #     今日连胜数(winStreak, int)
    #     剩余挑战次数(challengeNum, int)
    #     本周击败对手(weekWin, int)
    #     战报(fightLog, json)
    #     主动推送刷新(allUpdate,json)
    #         游戏模型-货币
    #         游戏模型-角色背包
    #     总击败对手人数(TotalWin,int)
    def rc_daylyPVPChallenge(self, pid):
        challengeNum = self.player.daylypvp.GetChallengeNum()
        if challengeNum <= 0:
            return 0, errcode.EC_DAYLY_PVP_CHALLENGE_NOT_ENOUGH

        winRes = Game.res_mgr.res_common.get("pvpChallengeWinReward")
        if not winRes:
            return 0, errcode.EC_NORES

        winPK = Game.res_mgr.res_common.get("pvpChallengeWinPK")
        if not winPK:
            return 0, errcode.EC_NORES

        upData, curData, lowData = self.player.daylypvp.getDaylyPVPData()

        otherData = None
        for oneData in (upData, curData, lowData):
            if not oneData:
                continue
            fightData = oneData.get("fightData", {})
            if pid == fightData.get("pid", 0):
                otherData = oneData
                break

        if not otherData:
            return 0, errcode.EC_DAYLY_PVP_NOT_DATA
        otherFightData = otherData.get("fightData", {})
        if not otherFightData:
            return 0, errcode.EC_INIT_BARR_FAIL
        if otherData.get("isWin", 0):
            return 0, errcode.EC_DAYLY_PVP_CHALLENGE_HAS_WIN


        fightobj = createFight(constant.FIGHT_TYPE_100)
        rs = fightobj.init_data(self.player.GetFightData(constant.BATTLE_ARRAY_TYPE_NORMAL), 100000)
        if not rs:
            return 0, errcode.EC_INIT_BARR_FAIL
        fightLog = fightobj.doFight()
        log_end = fightLog.get("end", {})
        winerList = log_end.get("winerList", [])
        fightResult = 1 if self.player.id in winerList else 0


        print("winerList",winerList)

        # fightobj = Game.fight_mgr.createFight(constant.FIGHT_TYPE_230)
        myFightData = self.player.GetFightData(constant.BATTLE_ARRAY_TYPE_NORMAL)
        # rs = fightobj.init_players_by_data(myFightData, otherFightData)
        # if not rs:
        #     return 0, errcode.EC_INIT_BARR_FAIL
        # fightobj.SetRounds(30)
        # fightLog = fightobj.doFight()
        # fightLog={"result":{"win":1}}
        # fightResult = fightLog["result"].get("win", 0)
        respBag = {}
        if fightResult:
            
            # resAct = Game.res_mgr.res_activity.get(constant.ACTIVITY_CHINESENEWYEAR_PK)
            # serverInfo = self.player.base.GetServerInfo()
            # if resAct.isOpen(serverInfo):
            #     self.player.meirimiaosha.addVirtual(winPK.i,constant.ACTIVITY_CHINESENEWYEAR_PK)

            # resAct = Game.res_mgr.res_activity.get(constant.ACTIVITY_CHINESENEWYEAR2_PK)
            # serverInfo = self.player.base.GetServerInfo()
            # if resAct.isOpen(serverInfo):
            #     self.player.meirimiaosha.addVirtual(winPK.i,constant.ACTIVITY_CHINESENEWYEAR2_PK)
                
            # 扣除次数 失败不扣
            self.player.daylypvp.SetChallengeNum(challengeNum - 1)

            dReward = {constant.CURRENCY_DAYLY_PVP_COIN: winRes.i}
            respBag = self.player.bag.add(dReward, constant.ITEM_ADD_DAYLY_PVP_CHALLENGE_WIN, wLog=True)
            #今日连胜
            todayWinStreak = self.player.daylypvp.GetTodayWinStreak()
            self.player.daylypvp.SetTodayWinStreak(todayWinStreak+1)
            #今日最高连胜
            itodayMaxWin = self.player.daylypvp.GetTodayChallengeMaxWin()
            if todayWinStreak > itodayMaxWin:
                self.player.daylypvp.SetTodayChallengeMaxWin(todayWinStreak)
            #本周胜利
            weekWin = self.player.daylypvp.GetWeekWin()
            self.player.daylypvp.SetWeekWin(weekWin + 1)
            #上传本周胜利次数
            spawn(self.player.daylypvp.sendWeekRankData)
            #历史胜利
            totalWin = self.player.daylypvp.GetTotalWin()
            self.player.daylypvp.SetTotalWin(totalWin + 1)
            #设置数据胜利
            otherData['isWin'] = 1
            self.player.daylypvp.SetTodayChallengeData((upData, curData, lowData))
            #判断是否全部挑战完成，刷新对手列表
            self.player.daylypvp.checkRefresh()
            #今日击败
            itodayWinNum = self.player.daylypvp.GetTodayChallengeWinNum()
            self.player.daylypvp.SetTodayChallengeWinNum(itodayWinNum + 1)
        else:
            self.player.safe_pub(msg_define.MSG_XIANSHITUISONGLIBAO_DAYLYPVP_F)
            
        if otherData.get("sendNotice", 0):
            addr = otherData.get("addr", "")
            from game.mgr.logicgame import LogicGame
            proxy = get_proxy_by_addr(addr, LogicGame._rpc_name_)
            if proxy:
                spawn(self.sendBeChallengeMsg, proxy, pid, config.serverNo, app.addr, myFightData, fightResult)

        totalFightNum = self.player.daylypvp.GetTotalFightNum()
        self.player.daylypvp.SetTotalFightNum(totalFightNum + 1)

        itodayNum = self.player.daylypvp.GetTodayDoChallengeNum()
        self.player.daylypvp.SetTodayDoChallengeNum(itodayNum + 1)

        self.player.safe_pub(msg_define.MSG_DAYLY_PVP_FIGHT)

        dUpdate = self.player.packRespBag(respBag)
        # dUpdate["meirimiaosha"] = self.player.meirimiaosha.to_init_data()
        resp = {
            "rivalList": self.player.daylypvp.packRivalList(),
            "winStreak": self.player.daylypvp.GetTodayWinStreak(), #今日连胜数
            "challengeNum": self.player.daylypvp.GetChallengeNum(), #剩余挑战次数
            "weekWin": self.player.daylypvp.GetWeekWin(), #本周击败对手
            "fightLog": fightLog,
            "allUpdate": dUpdate,
            "TotalWin": self.player.daylypvp.TotalWin, #总击败对手人数
        }
        return 1, resp

    def sendBeChallengeMsg(self, proxy, pid, serverNo, addr, myFightData, fightResult):
        proxy.daylyPvpBeChallenge(pid, serverNo, addr, myFightData, fightResult, _no_result=True)

    # 复仇对手(daylyPVPRevenge)
    # 请求
    #     玩家id(pid, int)
    # 返回
    #     复仇列表(revengeList, [json])
    #         玩家id(pid, int)
    #         名字(name, string)
    #         性别(sex, int)
    #         vip等级(vipLv, int)
    #         等级(lv, int)
    #         战力(fa, int)
    #         是否已复仇(isRevenge, int)
    #         复仇是否胜利(revengeWin, int)
    #         时间(fightTime, int)
    #         是否胜利(isWin, int)
    #     战报(fightLog, json)
    #     主动推送刷新(allUpdate,json)
    #         游戏模型-货币
    #         游戏模型-角色背包
    def rc_daylyPVPRevenge(self, pid):
        winRes = Game.res_mgr.res_common.get("pvpChallengeWinReward")
        if not winRes:
            return 0, errcode.EC_NORES
        winPK = Game.res_mgr.res_common.get("pvpRevengeWinPK")
        if not winPK:
            return 0, errcode.EC_NORES

        RevengeNumMaxRes = Game.res_mgr.res_common.get("pvpRevengeNumMax")

        otherData = None
        for oneData in self.player.daylypvp.GetBeChallengeData():
            fightData = oneData.get("fightData", {})
            if pid == fightData.get("pid", 0):
                otherData = oneData
                break

        if not otherData:
            return 0, errcode.EC_DAYLY_PVP_NOT_DATA
        otherFightData = otherData.get("fightData", {})
        if not otherFightData:
            return 0, errcode.EC_INIT_BARR_FAIL
        if otherData.get("isRevenge", 0):
            return 0, errcode.EC_DAYLY_PVP_HAS_REVENGE


        fightobj = createFight(constant.FIGHT_TYPE_100)
        rs = fightobj.init_data(self.player.GetFightData(constant.BATTLE_ARRAY_TYPE_NORMAL), 100000)
        if not rs:
            return 0, errcode.EC_INIT_BARR_FAIL
        fightLog = fightobj.doFight()
        log_end = fightLog.get("end", {})
        winerList = log_end.get("winerList", [])
        fightResult = 1 if self.player.id in winerList else 0

        # fightobj = Game.fight_mgr.createFight(constant.FIGHT_TYPE_231)
        myFightData = self.player.GetFightData(constant.BATTLE_ARRAY_TYPE_NORMAL)
        # rs = fightobj.init_players_by_data(myFightData, otherFightData)
        # if not rs:
        #     return 0, errcode.EC_INIT_BARR_FAIL
        # fightobj.SetRounds(30)
        # fightLog = fightobj.doFight()
        # fightLog={"result":{"win":1}}
        # fightResult = fightLog["result"].get("win", 0)
        respBag = {}
        iRevengeNum = self.player.daylypvp.GetTodayRevengeNum()
        if fightResult:

            # resAct = Game.res_mgr.res_activity.get(constant.ACTIVITY_CHINESENEWYEAR_PK)
            # serverInfo = self.player.base.GetServerInfo()
            # if resAct.isOpen(serverInfo):
            #     self.player.meirimiaosha.addVirtual(winPK.i,constant.ACTIVITY_CHINESENEWYEAR_PK)

            # resAct = Game.res_mgr.res_activity.get(constant.ACTIVITY_CHINESENEWYEAR2_PK)
            # serverInfo = self.player.base.GetServerInfo()
            # if resAct.isOpen(serverInfo):
            #     self.player.meirimiaosha.addVirtual(winPK.i,constant.ACTIVITY_CHINESENEWYEAR2_PK)
                
            
            if RevengeNumMaxRes.i > iRevengeNum:
                dReward = {constant.CURRENCY_DAYLY_PVP_COIN: winRes.i*2} #复仇两倍
                otherData['isDouble'] = 1
            else:
                dReward = {constant.CURRENCY_DAYLY_PVP_COIN: winRes.i}
            respBag = self.player.bag.add(dReward, constant.ITEM_ADD_DAYLY_PVP_REVENGE_WIN, wLog=True)

            # 设置数据胜利
            otherData['revengeWin'] = 1
            otherData['isRevenge'] = 1
            self.player.daylypvp.markDirty()

            itodayNum = self.player.daylypvp.GetTodayRevengeWin()
            self.player.daylypvp.SetTodayRevengeWin(itodayNum + 1)

        otherData['isRevenge'] = 1
        self.player.daylypvp.SetTodayRevengeNum(iRevengeNum+1)
        revengeNumTotal = self.player.daylypvp.GetRevengeNum()
        self.player.daylypvp.SetRevengeNum(revengeNumTotal+1)
        self.player.safe_pub(msg_define.MSG_DAYLY_PVP_REVENGE)

        dUpdate = self.player.packRespBag(respBag)
        # dUpdate["meirimiaosha"] = self.player.meirimiaosha.to_init_data()
        resp = {
            "revengeList": self.player.daylypvp.packRevengeList(),
            "fightLog": fightLog,
            "allUpdate": dUpdate,
        }
        return 1, resp


    # 领取连胜奖励(getDaylyPVPDataWinStreakReward)
    # 请求
    #     连胜奖励id(winRewardId, int)
    # 返回
    #     主动推送刷新(allUpdate,json)
    #         游戏模型-货币
    #         游戏模型-角色背包
    #     已领取连胜奖励列表(getRewardList, [int])
    def rc_getDaylyPVPDataWinStreakReward(self, winRewardId):
        winRewardRes = Game.res_mgr.res_pvploot.get(winRewardId)
        if not winRewardRes:
            return 0, errcode.EC_NORES
        getList = self.player.daylypvp.GetTodayGetRewardList()
        if winRewardId in getList:
            return 0, errcode.EC_DAYLY_PVP_REWARD_HAS_GET
        iWinNum = self.player.daylypvp.GetTodayWinStreak()
        if iWinNum < winRewardRes.pos:
            return 0, errcode.EC_DAYLY_PVP_WIN_NOT_ENOUGH

        getList.append(winRewardId)
        self.player.daylypvp.SetTodayGetRewardList(getList)

        respBag = self.player.bag.add(winRewardRes.reward, constant.ITEM_ADD_DAYLY_PVP_WINSTREAK_REWARD, wLog=True)

        # 抛事件
        self.player.safe_pub(msg_define.MSG_DAYLY_PVP_GET_REWARD)

        dUpdate = self.player.packRespBag(respBag)
        resp = {
            "getRewardList": self.player.daylypvp.GetTodayGetRewardList(),
            "allUpdate": dUpdate,
        }
        return 1, resp

    # 购买挑战次数(daylyPVPBuyChallengeNum)
    # 请求
    # 返回
    #     主动推送刷新(allUpdate,json)
    #         游戏模型-货币
    #         游戏模型-角色背包
    #     剩余挑战次数(challengeNum, int)
    #     今日已购买次数(buyNum, int)
    def rc_daylyPVPBuyChallengeNum(self):
        iVipLv = self.player.vip.GetVipLv()
        vipRes = Game.res_mgr.res_vip.get(iVipLv)
        if not vipRes:
            return 0, errcode.EC_NORES
        ihasBuy = self.player.daylypvp.GetTodayBuyChallengeNum()
        if ihasBuy >= vipRes.pvpbuynum: #PVP购买次数
            return 0, errcode.EC_DAYLY_PVP_BUY_CHALLENGE_NUM_LIMIT

        # 扣道具
        dCost = {constant.CURRENCY_GOLD: vipRes.pvpBuyCost}
        respBag = self.player.bag.costItem(dCost, constant.ITEM_COST_DAYLY_PVP_BUY_CHALLENGE_NUM, wLog=True)
        if not respBag.get("rs", 0):
            return 0, errcode.EC_DAYLY_PVP_BUY_CHALLENGE_NOT_ENOUGH

        self.player.daylypvp.SetTodayBuyChallengeNum(ihasBuy+1)
        iChallengeNum = self.player.daylypvp.GetChallengeNum()
        self.player.daylypvp.SetChallengeNum(iChallengeNum+1)

        dUpdate = self.player.packRespBag(respBag)
        resp = {
            "buyNum": self.player.daylypvp.GetTodayBuyChallengeNum(),
            "challengeNum": self.player.daylypvp.GetChallengeNum(),
            "allUpdate": dUpdate,
        }
        return 1, resp

    # 更换对手(daylyPVPRefresh)
    # 请求
    # 返回
    #     主动推送刷新(allUpdate,json)
    #         游戏模型-货币
    #         游戏模型-角色背包
    #     附近对手列表(rivalList, [json])
    #         玩家id(pid, int)
    #         名字(name, string)
    #         性别(sex, int)
    #         vip等级(vipLv, int)
    #         等级(lv, int)
    #         战力(fa, int)
    #         是否已击败(isWin, int)
    #     今日连胜数(winStreak, int)
    def rc_daylyPVPRefresh(self):
        costRes = Game.res_mgr.res_common.get("pvpChallengeRefreshCost")
        if not costRes:
            return 0, errcode.EC_NORES

        # 扣道具
        dCost = {constant.CURRENCY_BINDGOLD: costRes.i}
        respBag = self.player.bag.costItem(dCost, constant.ITEM_COST_DAYLY_PVP_REFRESH, wLog=True)
        if not respBag.get("rs", 0):
            return 0, errcode.EC_DAYLY_PVP_REFRESH_NOT_ENOUGH

        #更换对手
        exclude = []
        for oneData in self.player.daylypvp.getDaylyPVPData():
            if not oneData:
                continue
            fightData = oneData.get("fightData", {})
            pid = fightData.get("pid", 0)
            exclude.append(pid)
        self.player.daylypvp.SetTodayChallengeData([])
        self.player.daylypvp.getDaylyPVPData(exclude)
        # #连胜清除
        # self.player.daylypvp.SetTodayWinStreak(0)

        dUpdate = self.player.packRespBag(respBag)
        resp = {
            "rivalList": self.player.daylypvp.packRivalList(),
            "winStreak": self.player.daylypvp.GetTodayWinStreak(),
            "allUpdate": dUpdate,
        }
        return 1, resp

    # 获取排行榜数据(getDaylyPVPRankData)
    # 请求
    # 返回
    #     本周排行列表(rankList, [json])
    #         排名(rank, int)
    #         玩家id(pid, int)
    #         名字(name, string)
    #         本周击败对手(weekWin, int)
    #     上周排行列表(lastRankList, [json])
    #         排名(rank, int)
    #         玩家id(pid, int)
    #         名字(name, string)
    #         本周击败对手(weekWin, int)
    #     是否已领奖(isGetReward, int)
    #     我的排名(myRank, int)
    #     我击败的对手(myWin, int)
    #     我的上周排名(myLastRank, int)
    #     我上周击败的对手(myLastWin, int)
    def rc_getDaylyPVPRankData(self):
        allData = self.player.daylypvp.getDaylyPVPRankData()
        if not allData:
            return 0, errcode.EC_DAYLY_PVP_NOT_RANK_DATA
        curWeekRank, LastWeekRank = allData

        index = 1
        rankList = []
        myRank = 0
        myWin = self.player.daylypvp.GetWeekWin()
        for oneInfo in curWeekRank:
            serverNo = oneInfo.get("serverNo", 0)
            pid = oneInfo.get("data", {}).get("pid", 0)
            name = oneInfo.get("data", {}).get("name", 0)
            sid = self.player.daylypvp.no2id(serverNo)
            name = name + ".S" + str(sid)
            weekWin = oneInfo.get("data", {}).get("weekWin", 0)
            one = {
                "rank": index,
                "pid": pid,
                "name": name,
                "weekWin": weekWin
            }
            if pid == self.player.id:
                myRank = index
            index += 1
            rankList.append(one)

        index = 1
        lastRankList = []
        myLastRank = 0
        myLastWin = self.player.daylypvp.GetLastWeekWin()
        for oneInfo in LastWeekRank:
            serverNo = oneInfo.get("serverNo", 0)
            pid = oneInfo.get("data", {}).get("pid", 0)
            name = oneInfo.get("data", {}).get("name", 0)
            sid = self.player.daylypvp.no2id(serverNo)
            name = name + ".S" + str(sid)
            weekWin = oneInfo.get("data", {}).get("weekWin", 0)
            one = {
                "rank": index,
                "pid": pid,
                "name": name,
                "weekWin": weekWin
            }
            if pid == self.player.id:
                myLastRank = index
            index += 1
            lastRankList.append(one)

        self.player.daylypvp.SetLastWeekRank(myLastRank)

        resp = {
            "rankList": rankList,
            "lastRankList": lastRankList,
            "isGetReward": self.player.daylypvp.GetHasGetWeekRankReward(),
            "myRank": myRank,
            "myWin": myWin,
            "myLastRank": myLastRank,
            "myLastWin": myLastWin,
        }
        return 1, resp

    # 领取排行榜奖励(getDaylyPVPRankReward)
    # 请求
    # 返回
    #     主动推送刷新(allUpdate,json)
    #         游戏模型-货币
    #         游戏模型-角色背包
    #     是否已领奖(isGetReward, int)
    def rc_getDaylyPVPRankReward(self):
        isGetReward = self.player.daylypvp.GetHasGetWeekRankReward()
        if isGetReward:
            return 0, errcode.EC_DAYLY_PVP_WEEK_RANK_REWARD_HAS_GET

        allData = self.player.daylypvp.getDaylyPVPRankData()
        if not allData:
            return 0, errcode.EC_DAYLY_PVP_NOT_RANK_DATA
        curWeekRank, LastWeekRank = allData

        index = 1
        for oneInfo in LastWeekRank:
            pid = oneInfo.get("data", {}).get("pid", 0)
            if pid == self.player.id:
                break
            index += 1

        rankRes = Game.res_mgr.res_pvprank.get(index)
        if not rankRes:
            return 0, errcode.EC_NORES

        respBag = self.player.bag.add(rankRes.reward, constant.ITEM_ADD_DAYLY_PVP_WEEK_RANK_REWARD, wLog=True)

        self.player.daylypvp.SetHasGetWeekRankReward(1)

        dUpdate = self.player.packRespBag(respBag)
        resp = {
            "isGetReward": self.player.daylypvp.GetHasGetWeekRankReward(),
            "allUpdate": dUpdate,
        }
        return 1, resp


    # 生成机器人复仇数据(makeDaylyPVPRobotRevengeData)
    # 请求
    # 返回
    def rc_makeDaylyPVPRobotRevengeData(self):
        self.player.daylypvp.addBeChallengeRobotData()
        return 1, None





