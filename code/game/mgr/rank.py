#!/usr/bin/env python
# -*- coding:utf-8 -*-
from functools import cmp_to_key

from corelib.frame import MSG_FRAME_APP_ADD, MSG_FRAME_APP_DEL, MSG_FRAME_STOP
from game import Game
from corelib import log, spawn
from game.define.msg_define import MSG_RANK
from gevent import sleep
from game.define import constant
from game.models.rank import ModelRank
from game.models.daxiaRank import ModelDaxiaRank
from time import time
from game.common import utility
from game.define import constant, msg_define
from corelib.gtime import cur_day_hour_time, current_time, get_days
import copy
from game.core.cycleData import MergeData
from game.mgr.player import get_rpc_player
from game.mgr.room import get_rpc_boss
import config


class GRankMgr(object):
    _rpc_name_ = "rpc_global_rank_mgr"
    TIME_OUT = 0.1

    def __init__(self):
        self.ranks = {}   # type : GRank
        self.daxiaRanks = None #daxiaId : []
        self.app_pids = {}
        self.isLoading = True

        Game.sub(MSG_FRAME_APP_ADD, self._msg_app_add)
        Game.sub(MSG_FRAME_APP_DEL, self._msg_app_del)

        Game.sub(MSG_FRAME_STOP, self._frame_stop)
        self._cal_loop_task = None
        self._save_loop_task = None
        self._reward_loop_task = None

    def _msg_app_add(self, app_name, addr, names):
        if SubRankMgr._rpc_name_ not in names:
            return
        log.info('[rank_mgr]reg sub_rank_mgr:%s', app_name)
        self.app_pids[app_name] = set()

    def _msg_app_del(self, app_name, addr, names):
        """ 子进程退出,清理数据 """
        if SubRankMgr._rpc_name_ not in names:
            return
        log.info('[rank_mgr]unreg sub_rank_mgr:%s', app_name)
        self.app_pids.pop(app_name, None)

    def start(self):
        for x in range(constant.RANK_MAX_TYPE):
            type = x+1
            grank = GRank(type)
            grank.load()
            self.ranks[type] = grank

        self.daxiaRanks = DaxiaRank()
        self.daxiaRanks.load()

        self.isLoading = False

        self._cal_loop_task = spawn(self._calLoop)
        self._save_loop_task = spawn(self._saveLoop)
        self._reward_loop_task = spawn(self.wee_hours_task)

        spawn(self.sendReward)

    def sendReward(self):
        try:
            sleep(60)
            self.cal(log=1)
            self.sendToLogic()
            self._activity_reward()
        except:
            log.log_except()

    def wee_hours_task(self):
        """凌晨定时任务"""
        while 1:
            next_time = cur_day_hour_time(hour=24)
            delay = next_time - current_time()
            if delay > 5 * 60:
                sleep(5 * 60)
            else:
                sleep(delay + 2)
                try:
                    self.cal(log=1)
                except:
                    log.log_except()
                #=======================================
                try:
                    self.sendToLogic()
                except:
                    log.log_except()
                # =======================================
                try:
                    self._activity_reward()
                except:
                    log.log_except()
                # =======================================
                try:
                    self._activity_reward_kfkh()
                except:
                    log.log_except()
                # =======================================
                try:
                    self._activity_reward_heti()
                except:
                    log.log_except()
                # =======================================
                try:
                    self._activity_cost_rank()
                except:
                    log.log_except()
                # =======================================
                try:
                    self._activity_charge_rank()
                except:
                    log.log_except()
                # =======================================
                try:
                    self._activity_charge_rank_hefu()
                except:
                    log.log_except()
                # =======================================
                try:
                    self._activity_catchpet_rank_hefu()
                except:
                    log.log_except()
                # =======================================
                try:
                    self._activity_new_year_rank()
                except:
                    log.log_except()
                # =======================================


    def _activity_cost_rank(self):
        rankObj = self.ranks.get(constant.RANK_TYPE_COST)
        if not rankObj:
            return

        serverInfo = Game.rpc_server_info.GetServerInfo()
        resAct = Game.res_mgr.res_activity.get(constant.ACTIVITY_COST_RANK)
        if not resAct.isOpen(serverInfo) and not rankObj.cost_rank_reward:
            rankObj.cost_rank_reward = 1
            rankObj.cost_rank_reward_time = int(time())
            rankObj.markDirty()

            mailRes = Game.res_mgr.res_mail.get(constant.MAIL_ID_COST_RANK, None)
            rankList = rankObj.getRankList()
            for playerInfo in rankList:
                pid = playerInfo.get("id", 0)
                rank = playerInfo.get("rank", 0)
                costRankRes = None
                for one in Game.res_mgr.res_costRank.values():
                    if one.minRank <= rank <= one.maxRank:
                        costRankRes = one
                        break
                content = mailRes.content % str(rank)
                if pid:
                    Game.rpc_mail_mgr.sendPersonMail(pid, mailRes.title, content, costRankRes.reward, push=False)

    def _activity_charge_rank(self):
        rankObj = self.ranks.get(constant.RANK_TYPE_CHARGE)
        if not rankObj:
            return

        serverInfo = Game.rpc_server_info.GetServerInfo()
        resAct = Game.res_mgr.res_activity.get(constant.ACTIVITY_CHARGE_RANK)
        if not resAct.isOpen(serverInfo) and not rankObj.charge_rank_reward:
            rankObj.charge_rank_reward = 1
            rankObj.charge_rank_reward_time = int(time())
            rankObj.markDirty()

            mailRes = Game.res_mgr.res_mail.get(constant.MAIL_ID_CHARGE_RANK, None)
            rankList = rankObj.getRankList()
            for playerInfo in rankList:
                pid = playerInfo.get("id", 0)
                rank = playerInfo.get("rank", 0)
                chargeRankRes = None
                for one in Game.res_mgr.res_chargeRank.values():
                    if one.minRank <= rank <= one.maxRank:
                        chargeRankRes = one
                        break
                content = mailRes.content % str(rank)
                if pid:
                    Game.rpc_mail_mgr.sendPersonMail(pid, mailRes.title, content, chargeRankRes.reward, push=False)

    def _activity_charge_rank_hefu(self):
        rankObj = self.ranks.get(constant.RANK_TYPE_CHARGE_HEFU)
        if not rankObj:
            return

        serverInfo = Game.rpc_server_info.GetServerInfo()
        resAct = Game.res_mgr.res_activity.get(constant.ACTIVITY_CHARGE_RANK_HEFU)
        if not resAct.isOpen(serverInfo) and not rankObj.getcharge_rank_rewardHefu():
            rankObj.setcharge_rank_rewardHefu(1)
            rankObj.setcharge_rank_reward_timeHefu(int(time()))
            rankObj.markDirty()

            mailRes = Game.res_mgr.res_mail.get(constant.MAIL_ID_CHARGE_RANK_HEFU, None)
            rankList = rankObj.getRankList()
            for playerInfo in rankList:
                pid = playerInfo.get("id", 0)
                rank = playerInfo.get("rank", 0)
                chargeRankRes = None
                for one in Game.res_mgr.res_chargeRankHefu.values():
                    if one.minRank <= rank <= one.maxRank:
                        chargeRankRes = one
                        break
                content = mailRes.content % str(rank)
                if pid:
                    Game.rpc_mail_mgr.sendPersonMail(pid, mailRes.title, content, chargeRankRes.reward, push=False)

    def _activity_catchpet_rank_hefu(self):
        rankObj = self.ranks.get(constant.RANK_TYPE_CATCHPET_HEFU)
        if not rankObj:
            return

        serverInfo = Game.rpc_server_info.GetServerInfo()
        resAct = Game.res_mgr.res_activity.get(constant.ACTIVITY_CATCHPET_RANK_HEFU)
        if not resAct.isOpen(serverInfo) and not rankObj.getcatchpet_rank_rewardHefu():
            print("====ACTIVITY_CATCHPET_RANK_HEFU===XXXXXX")
            rankObj.setcatchpet_rank_rewardHefu(1)
            rankObj.setcatchpet_rank_reward_timeHefu(int(time()))
            rankObj.markDirty()

            mailRes = Game.res_mgr.res_mail.get(constant.MAIL_ID_CATCHPET_RANK_HEFU, None)
            rankList = rankObj.getRankList()
            for playerInfo in rankList:
                pid = playerInfo.get("id", 0)
                rank = playerInfo.get("rank", 0)
                catchpetRankRes = None
                for one in Game.res_mgr.res_catchPetRankRewardHefu.values():
                    if one.minRank <= rank <= one.maxRank:
                        catchpetRankRes = one
                        break
                content = mailRes.content % str(rank)
                if pid:
                    Game.rpc_mail_mgr.sendPersonMail(pid, mailRes.title, content, catchpetRankRes.reward, push=False)


    def _activity_new_year_rank(self):
        now = int(time())

        resAct = Game.res_mgr.res_activity.get(constant.ACTIVITY_NEWYEAR_RANK_OPEN)
        startTime, endTime = resAct.getStartTimeAndEndTime()
        for actRankRes in Game.res_mgr.res_actNewYearRank.values():
            rankObj = self.ranks.get(actRankRes.rankType)
            if not rankObj:
                continue

            if now >= endTime:
                mailRes = Game.res_mgr.res_mail.get(constant.MAIL_ID_NEW_YEAR_RANK_REWRAD, None)
                rankList = rankObj.getRankList()
                rankList = rankList[actRankRes.minRank-1:actRankRes.maxRank]
                for playerInfo in rankList:
                    pid = playerInfo.get("id", 0)
                    rank = playerInfo.get("rank", 0)
                    content = mailRes.content % (actRankRes.rankName, str(rank))
                    if pid:
                        Game.rpc_mail_mgr.sendPersonMail(pid, mailRes.title, content, actRankRes.reward, push=False)

        rankObj.activityReward = []
        rankObj.clear()


    def _activity_reward(self):
        serverInfo = Game.rpc_server_info.GetServerInfo()
        openDay = get_days(serverInfo.get("opentime", 0))+ 1
        for actRankRes in Game.res_mgr.res_actRank.values():
            activityRes = Game.res_mgr.res_activity.get(actRankRes.actId)
            if not activityRes:
                continue
            rankType = constant.MAP_ACT_RANK_MOD_TYPE.get(activityRes.type)
            if not rankType:
                continue
            rankObj = self.ranks.get(rankType)
            if not rankObj:
                continue
            activityReward = rankObj.getActivityReward()
            if openDay - 1 >= activityRes.openDayRange[1] and actRankRes.id not in activityReward:
                activityReward.append(actRankRes.id)
                rankObj.setActivityReward(activityReward)
                mailRes = Game.res_mgr.res_mail.get(constant.MAIL_ID_RANK_REWRAD, None)
                rankList = rankObj.getRankList()
                rankList = rankList[actRankRes.minRank-1:actRankRes.maxRank]
                for playerInfo in rankList:
                    pid = playerInfo.get("id", 0)
                    rank = playerInfo.get("rank", 0)
                    content = mailRes.content % (activityRes.name, str(rank))
                    if pid:
                        Game.rpc_mail_mgr.sendPersonMail(pid, mailRes.title, content, actRankRes.reward, push=False)

    def _activity_reward_heti(self):

        rankObj = self.ranks.get(constant.RANK_HETI)

        mailRes = Game.res_mgr.res_mail.get(constant.MAIL_ID_RANK_REWRAD_HETI, None)

        rankList = rankObj.getRankList()

        for playerInfo in rankList:
            playerInfo["reward"]=0
            pid = playerInfo.get("id", 0)
            rank = playerInfo.get("rank", 0)
            content = mailRes.content % str(rank)
            if pid:
                res=Game.res_mgr.res_hetiReward.get(rank,None)
                if res:
                    playerInfo["reward"]=1
                    Game.rpc_mail_mgr.sendPersonMail(pid, mailRes.title, content, res.reward, push=False)
        
        rankObj.SetSnapshot()
        rankObj.clear()


    def _activity_reward_kfkh(self):
        serverInfo = Game.rpc_server_info.GetServerInfo()
        openDay = get_days(serverInfo.get("opentime", 0))+ 1
        
        for actRankRes in Game.res_mgr.res_actKfkh.values():
            activityRes = Game.res_mgr.res_activity.get(actRankRes.actId)
            if not activityRes:
                continue

            if activityRes.openDayRange[1]!=openDay-1:
                continue
    
            rankType = constant.KFKH_ACT_RANK_MOD_TYPE.get(actRankRes.type,None)
            if not rankType:
                continue
            rankObj = self.ranks.get(rankType)
            if not rankObj:
                continue

            if not actRankRes.minRank:
                continue

        
            

            
            rankList = rankObj.getRankList()

            rankList = rankList[actRankRes.minRank-1:actRankRes.maxRank]
            for playerInfo in rankList:
                pid = playerInfo.get("id", 0)
                rank = playerInfo.get("rank", 0)

                playerInfo["reward"]=0
                

                mailRes={}
                if actRankRes.type==constant.KFKH_RANK_TYPE_7001:
                    if playerInfo["sortEle"][0]<actRankRes.value:
                        continue
                    mailRes = Game.res_mgr.res_mail.get(constant.MAIL_ID_KFKH_RANK_7001, None)
                elif actRankRes.type==constant.KFKH_RANK_TYPE_7002:
                    if playerInfo["sortEle"][0]<actRankRes.value:
                        continue
                    mailRes = Game.res_mgr.res_mail.get(constant.MAIL_ID_KFKH_RANK_7002, None)


                elif actRankRes.type==constant.KFKH_RANK_TYPE_7006:
                    if playerInfo["sortEle"][0]<actRankRes.value:
                        continue
                    mailRes = Game.res_mgr.res_mail.get(constant.MAIL_ID_KFKH_RANK_7006, None)

                elif actRankRes.type==constant.KFKH_RANK_TYPE_7008:
                    if playerInfo["sortEle"][0]<actRankRes.value:
                        continue
                    mailRes = Game.res_mgr.res_mail.get(constant.MAIL_ID_KFKH_RANK_7008, None)
                else:
                    continue

                content = mailRes.content % str(rank)
                if pid:
                    playerInfo["reward"]=1
                    Game.rpc_mail_mgr.sendPersonMail(pid, mailRes.title, content, actRankRes.reward, push=False)
            
            rankObj.SetSnapshot()

    def CleanRankReward(self):
        for rank in self.ranks.values():
            if rank:
                rank.setActivityReward([])

    def _frame_stop(self):
        if self._cal_loop_task:
            self._cal_loop_task.kill(block=False)
            self._cal_loop_task = None

        if self._save_loop_task:
            self._save_loop_task.kill(block=False)
            self._save_loop_task = None

        if self._reward_loop_task:
            self._reward_loop_task.kill(block=False)
            self._reward_loop_task = None

        self.cal(log=1)
        self.save(forced=True, no_let=True)

    def updateRank(self, data, now):
        for type, players in data.items():
            gRank = self.ranks.get(type, None)
            if gRank:
                gRank.updatePlayers(players)

        if now:
            try:
                self.cal()
                self.sendToLogic()
            except:
                log.log_except()            

    def _calLoop(self):
        """定时结算排行榜"""
        stime = 60
        logCounter = 1
        while True:
            sleep(stime)
            try:
                self.cal(log=int(logCounter/5))
                self.sendToLogic()
            except:
                log.log_except()

            if logCounter == 5:
                logCounter = 1
            else:
                logCounter += 1

    def _saveLoop(self):
        stime = 10 * 60
        while True:
            sleep(stime)
            try:
                self.save()
            except:
                log.log_except()

    def cal(self, log=0):
        for rank in self.ranks.values():
            if rank:
                rank.cal(log=log)

    def save(self, forced=False, no_let=False):
        for rank in self.ranks.values():
            if rank:
                rank.save(forced=forced, no_let=no_let)

        self.daxiaRanks.save(forced=forced, no_let=no_let)

    def sendToLogic(self):
        sendData = self.getRankData()

        if sendData:
            for appName in self.app_pids:
                logic = Game.get_service(appName, SubRankMgr._rpc_name_)
                logic.acceptRankData(sendData, _no_result=True)

    def getRankData(self):
        for x in range(10):
            if self.isLoading:
                sleep(1)
            else:
                break

        rankData = {}
        for rank in self.ranks.values():
            if rank:
                ranking = rank.getRankList()
                if ranking:
                    rankData[rank.type] = ranking
                else:
                    if constant.RANK_HETI==rank.type:
                        rankData[rank.type] = []
        return rankData

    def GetSnapshot(self,type):
        gRank = self.ranks.get(type, None)
        if not gRank:
            return []
        
        return gRank.GetSnapshot()
        
    def upDaxiaKill(self, daxiaId, iTime, playerInfo):
        """xx大侠排行"""
        self.daxiaRanks.upDaxiaKill(daxiaId, iTime, playerInfo)

    def getDaxiaRank(self, daxiaId):
        return self.daxiaRanks.getDaxiaRank(daxiaId)

    def setDaxiaRankReward(self, daxiaId, pid):
        return self.daxiaRanks.setDaxiaRankReward(daxiaId, pid)

    def get_cost_rank_reward_time(self, rankType):
        rankObj = self.ranks.get(rankType)
        if not rankObj:
            return 0
        return rankObj.cost_rank_reward_time

    def get_charge_rank_reward_time(self, rankType):
        rankObj = self.ranks.get(rankType)
        if not rankObj:
            return 0
        return rankObj.charge_rank_reward_time

    def get_charge_rank_reward_time_hefu(self, rankType):
        rankObj = self.ranks.get(rankType)
        if not rankObj:
            return 0
        return rankObj.getcharge_rank_reward_timeHefu()

    def get_catchpet_rank_reward_time_hefu(self, rankType):
        rankObj = self.ranks.get(rankType)
        if not rankObj:
            return 0
        return rankObj.getcatchpet_rank_reward_timeHefu()

class DaxiaRank(utility.DirtyFlag):
    DATA_CLS = ModelDaxiaRank

    def __init__(self):
        utility.DirtyFlag.__init__(self)
        self.daxiaRanks = {}  # daxiaId : []

        self.data = None
        self.save_cache = {}

    def save(self, forced=False, no_let=False):
        self.data.save(Game.store, forced=forced, no_let=no_let)

    def load(self):
        self.data = self.DATA_CLS.load(Game.store, self.DATA_CLS.TABLE_KEY)
        if not self.data:
            self.data = self.DATA_CLS()
        else:
            self.load_from_dict(self.data.dataDict)

        self.data.set_owner(self)

    def to_save_dict(self, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            self.save_cache = {}
            self.save_cache["daxiaRanks"] = []
            for daxiaId, data in self.daxiaRanks.items():
                self.save_cache["daxiaRanks"].append({"daxiaId":daxiaId, "data":data})

        return self.save_cache

    def load_from_dict(self, data):        
        daxiaRanks = data.get("daxiaRanks", [])
        for one in daxiaRanks:
            daxiaId = one.get("daxiaId", 0)
            data = one.get("data", [])
            if daxiaId:
                self.daxiaRanks[daxiaId] = data

    def upDaxiaKill(self, daxiaId, iTime, playerInfo):
        """xx大侠排行"""
        rankdata = self.daxiaRanks.setdefault(daxiaId, [])
        if len(rankdata) < 20:
            rankdata.append([iTime, playerInfo])
            self.markDirty()

    def getDaxiaRank(self, daxiaId):
        return self.daxiaRanks.get(daxiaId, [])

    def setDaxiaRankReward(self, daxiaId, pid):
        rankdata = self.daxiaRanks.setdefault(daxiaId, [])
        rankIndex = 0
        for index, one in enumerate(rankdata):
            playerInfo = one[1]
            if playerInfo['rid'] == pid:
                rankIndex = index + 1
                self.markDirty()
                break
        return rankIndex, rankdata


class GRank(utility.DirtyFlag):
    DATA_CLS = ModelRank

    def __init__(self, type):
        utility.DirtyFlag.__init__(self)
        self.type = type
        self.players = {}  # pid : PlayerInfo
        self.ranking = []  # 当前排名 playerInfo
        self.rankingCopy = []  # 当前排名 playerInfo Copy
        self.activityReward = []

        self.cost_rank_reward = 0 #消费排行 是否发奖
        self.cost_rank_reward_time = 0  # 消费排行 最后一次发奖时间
        self.charge_rank_reward = 0 #充值排行 是否发奖
        self.charge_rank_reward_time = 0 #充值排行 最后一次发奖时间
        self.mymergetime = 0 #

        self.data = None
        self.save_cache = {}
        
        self.mergeData = MergeData(self)


    def getcharge_rank_rewardHefu(self):
        return self.mergeData.Query("charge_rank_rewardHefu", 0)

    def setcharge_rank_rewardHefu(self,v):
        self.mergeData.Set("charge_rank_rewardHefu", v)
    
    def getcharge_rank_reward_timeHefu(self):
        return self.mergeData.Query("charge_rank_reward_timeHefu", [])
        
    def setcharge_rank_reward_timeHefu(self,v):
        self.mergeData.Set("charge_rank_reward_timeHefu", v)

    def getcatchpet_rank_rewardHefu(self):
        return self.mergeData.Query("catchpet_rank_rewardHefu", 0)

    def setcatchpet_rank_rewardHefu(self,v):
        self.mergeData.Set("catchpet_rank_rewardHefu", v)
    
    def getcatchpet_rank_reward_timeHefu(self):
        return self.mergeData.Query("catchpet_rank_reward_timeHefu", [])
        
    def setcatchpet_rank_reward_timeHefu(self,v):
        self.mergeData.Set("catchpet_rank_reward_timeHefu", v)

    def markDirty(self):
        utility.DirtyFlag.markDirty(self)
        self.data.modify()

    def to_save_dict(self, forced=False):
        


        if self.isDirty() or forced or not self.save_cache:
            self.save_cache = {}
            self.save_cache["ranking"] = self.ranking
            self.save_cache["rankingCopy"] = self.rankingCopy
            self.save_cache["activityReward"] = self.activityReward
            self.save_cache["cost_rank_reward"] = self.cost_rank_reward
            self.save_cache["cost_rank_reward_time"] = self.cost_rank_reward_time
            self.save_cache["charge_rank_reward"] = self.charge_rank_reward
            self.save_cache["charge_rank_reward_time"] = self.charge_rank_reward_time
            self.save_cache["mymergetime"] = self.mymergetime

            self.save_cache["mergeData"] = self.mergeData.to_save_bytes()
        
        return self.save_cache

    def load_from_dict(self, data):
        self.mergeData.load_from_dict(data.get("mergeData", ""))

        self.activityReward = data.get("activityReward", [])
        self.ranking = data.get("ranking", [])
        self.rankingCopy = data.get("rankingCopy", [])
        self.cost_rank_reward = data.get("cost_rank_reward", 0)
        self.cost_rank_reward_time = data.get("cost_rank_reward_time", 0)
        self.charge_rank_reward = data.get("charge_rank_reward", 0)
        self.charge_rank_reward_time = data.get("charge_rank_reward_time", 0)


        self.mymergetime = data.get("mymergetime", 0)

        serverInfo = Game.rpc_server_info.GetServerInfo()
        mergetime=serverInfo.get("mergetime", 0)       

        if mergetime and (self.type==constant.RANK_TYPE_CHARGE_HEFU or self.type==constant.RANK_TYPE_CHARGE_HEFU):
            if mergetime!=self.mymergetime:
                print("=====rank=clean===",self.type)
                self.mymergetime=mergetime
                self.markDirty()
                
                self.activityReward = []
                self.ranking = []
                self.rankingCopy = []
                self.cost_rank_reward = 0
                self.cost_rank_reward_time = 0
                self.charge_rank_reward = 0
                self.charge_rank_reward_time = 0

        for player in self.ranking:
            id = player.get("id", 0)
            if id:
                self.players[id] = player

        # 起服排序，适配合服
        self.cal(log=1)

    def getActivityReward(self):
        return self.activityReward

    def clear(self):
        self.players.clear()
        del self.ranking[:]
        self.markDirty()

    def setActivityReward(self, activityReward):
        self.activityReward = activityReward
        self.markDirty()

    def cal(self, log=0):
        # 消费排行 # 充值排行
        if self.type == constant.RANK_TYPE_COST or self.type == constant.RANK_TYPE_CHARGE or self.type == constant.RANK_TYPE_CHARGE_HEFU or self.type == constant.RANK_TYPE_CATCHPET_HEFU:
            serverInfo = Game.rpc_server_info.GetServerInfo()
            resAct = Game.res_mgr.res_activity.get(constant.ACTIVITY_COST_RANK)
            if resAct.isOpen(serverInfo):
                self.cost_rank_reward = 0
                self.markDirty()

                #排行榜保留2天
                if self.cost_rank_reward_time and int(time()) - self.cost_rank_reward_time > 3600*24*2:
                    self.players = {}  # pid : PlayerInfo
                    self.ranking = []  # 当前排名 playerInfo
                    self.rankingCopy = []  # 当前排名 playerInfo Copy
                    self.activityReward = []

                    self.cost_rank_reward = 0  # 消费排行 是否发奖
                    self.cost_rank_reward_time = 0  # 消费排行 最后一次发奖时间
                    self.charge_rank_reward = 0  # 充值排行 是否发奖
                    self.charge_rank_reward_time = 0  # 充值排行 最后一次发奖时间


            resAct = Game.res_mgr.res_activity.get(constant.ACTIVITY_CHARGE_RANK)
            if resAct.isOpen(serverInfo):
                self.charge_rank_reward = 0
                self.markDirty()
                # 排行榜保留2天
                if self.charge_rank_reward_time and int(time()) - self.charge_rank_reward_time > 3600 * 24 * 2:
                    self.players = {}  # pid : PlayerInfo
                    self.ranking = []  # 当前排名 playerInfo
                    self.rankingCopy = []  # 当前排名 playerInfo Copy
                    self.activityReward = []

                    self.cost_rank_reward = 0  # 消费排行 是否发奖
                    self.cost_rank_reward_time = 0  # 消费排行 最后一次发奖时间
                    self.charge_rank_reward = 0  # 充值排行 是否发奖
                    self.charge_rank_reward_time = 0  # 充值排行 最后一次发奖时间


            resAct = Game.res_mgr.res_activity.get(constant.ACTIVITY_CHARGE_RANK_HEFU)
            if resAct.isOpen(serverInfo):
                self.setcharge_rank_rewardHefu(0)
                self.markDirty()
                # 排行榜保留2天
                if self.getcharge_rank_reward_timeHefu() and int(time()) - self.getcharge_rank_reward_timeHefu() > 3600 * 24 * 2:
                    self.players = {}  # pid : PlayerInfo
                    self.ranking = []  # 当前排名 playerInfo
                    self.rankingCopy = []  # 当前排名 playerInfo Copy
                    self.activityReward = []

                    self.cost_rank_reward = 0  # 消费排行 是否发奖
                    self.cost_rank_reward_time = 0  # 消费排行 最后一次发奖时间
                    self.setcharge_rank_rewardHefu(0) # 充值排行 是否发奖
                    self.setcharge_rank_reward_timeHefu(0)  # 充值排行 最后一次发奖时间

            resAct = Game.res_mgr.res_activity.get(constant.ACTIVITY_CATCHPET_RANK_HEFU)
            if resAct.isOpen(serverInfo):
                self.setcatchpet_rank_rewardHefu(0)
                self.markDirty()
                # 排行榜保留2天
                if self.getcatchpet_rank_reward_timeHefu() and int(time()) - self.getcatchpet_rank_reward_timeHefu() > 3600 * 24 * 2:
                    self.players = {}  # pid : PlayerInfo
                    self.ranking = []  # 当前排名 playerInfo
                    self.rankingCopy = []  # 当前排名 playerInfo Copy
                    self.activityReward = []

                    self.cost_rank_reward = 0  # 消费排行 是否发奖
                    self.cost_rank_reward_time = 0  # 消费排行 最后一次发奖时间
                    self.setcatchpet_rank_rewardHefu(0) # 充值排行 是否发奖
                    self.setcatchpet_rank_reward_timeHefu(0)  # 充值排行 最后一次发奖时间


        ranking = list(self.players.values())
        ranking.sort(key=cmp_to_key(self._comp))

        ranking, out = ranking[:constant.RANK_SIZE], ranking[constant.RANK_SIZE:]
        for x in range(len(ranking)):
            ranking[x]["rank"] = x+1

        # log.info("cal_rank %s %s", self.type, ranking)
        # 清理落榜玩家
        for player in out:
            self.players.pop(player.get("id", 0))

        self.ranking = ranking
        if log:
            Game.glog.log2File("rank", "%s|%s" % (self.type, self.ranking))

        self.markDirty()

    def save(self, forced=False, no_let=False):
        self.data.save(Game.store, forced=forced, no_let=no_let)

    def load(self):
        self.data = self.DATA_CLS.load(Game.store, self.type)
        if not self.data:
            self.data = self.DATA_CLS()
        else:
            self.load_from_dict(self.data.dataDict)

        self.data.setOwner(self)

    @staticmethod
    def _comp(x, y):
        xEle = x.get("sortEle", [])
        yEle = y.get("sortEle", [])
        if not xEle or not yEle:
            return 0

        xLen = len(xEle)
        yLen = len(yEle)

        minLen = xLen if xLen <= yLen else yLen
        for idx in range(minLen):
            if xEle[idx] < yEle[idx]:
                return 1

            if xEle[idx] > yEle[idx]:
                return -1

        return 0


    def getRankList(self):
        return self.ranking
    
    def SetSnapshot(self):
        self.rankingCopy=copy.deepcopy(self.ranking)
        self.markDirty()

    def GetSnapshot(self):
        retval=[]
        for v in self.rankingCopy:
            if "reward" not in v or not v["reward"]:
                break
            retval.append(v)

        return retval

    def updatePlayers(self, players):
        for pid, player in players.items():
            self.players[pid] = player


class SubRankMgr(object):
    _rpc_name_ = "rpc_sub_rank_mgr"

    def __init__(self):
        self.ranks = {}
        self.lastCalTime = 0
        self._loop_task = None
        self.wee_lv_rank = [] #0点 等级榜

    def getRank(self, type):
        rank = self.ranks.get(type, None)
        if not rank:
            rank = Rank(type)
            self.ranks[type] = rank

        return rank

    def _loop(self):
        """定时同步数据到GRankMgr"""
        stime = 60
        while True:
            sleep(stime)
            try:
                self.sendToGlobal()
            except:
                log.log_except()

    def sendToGlobal(self,now=0):
        data = {}
        for rank in self.ranks.values():
            data[rank.type] = rank.getPlayers()
            rank.cleanPlayers()

        if data:
            Game.rpc_global_rank_mgr.updateRank(data, now, _no_result=True)

    def acceptRankData(self, rankData):
        for type, ranking in rankData.items():
            rank = self.getRank(type)
            if rank:
                rank.updateRankList(ranking)

        self.lastCalTime = int(time())

    def uploadRank(self, type, player):
        rank = self.getRank(type)
        if rank:
            rank.uploadRank(player)

        if type==constant.RANK_HETI:
            self.sendToGlobal(1)

    def start(self):
        rankData = Game.rpc_global_rank_mgr.getRankData()
        self.acceptRankData(rankData)

        self._loop_task = spawn(self._loop)
        self.event_wee_hours()
        Game.sub(msg_define.MSG_WEE_HOURS, self.event_wee_hours)
        self.event_half_hours()
        Game.sub(msg_define.MSG_HALF_HOURS, self.event_half_hours)

    def stop(self):
        if self._loop_task:
            self._loop_task.kill(block=False)
            self._loop_task = None

        self.sendToGlobal()
        Game.unsub(msg_define.MSG_WEE_HOURS, self.event_wee_hours)
        Game.unsub(msg_define.MSG_HALF_HOURS, self.event_half_hours)

    def getRankList(self, type):
        rank = self.getRank(type)
        return rank.getRankList()

    def getRankobj(self, type):
        return self.getRank(type)

    def event_wee_hours(self):
        self.wee_lv_rank = self.getRankList(constant.RANK_TYPE_LV)
    
    def SetAtk(self,fa):
        rpc_boss = get_rpc_boss()
        if rpc_boss:
            print('kfboss SetAtk',fa)
            rpc_boss.kfbossSetAtk(config.serverNo,fa)

    def event_half_hours(self):
        falist = self.getRankList(constant.RANK_TYPE_FA)

        atk3=0
        icount = 0
        for one in falist:
            if 3 == icount:
                break
            icount += 1

            pid = one.get("id", 0)
            # atk3+=v["fight"]
            proxy = get_rpc_player(pid)
            if not proxy:
                continue
            atk3+=proxy.getAtk()


        if atk3<30000:
            atk3=30000
        if icount==0:
            icount=1


        atk=int(atk3/icount)
        spawn(self.SetAtk,atk)



    def getMyRank(self, type, pid):
        rank = self.getRank(type)
        return rank.getMyRank(pid)

    def getLastCalTime(self):
        return self.lastCalTime


class Rank(object):
    def __init__(self, type):
        self.type = type
        self.players = {}
        self.minEle = []
        self.rankList = []
        self.rankListCopy = []

    def uploadRank(self, player):
        id = player.get("id", 0)
        sortEle = player.get("sortEle", [])

        if not id or not sortEle:
            return False

        self.players[id] = player
        return True

    def getPlayers(self):
        return self.players

    def cleanPlayers(self):
        self.players = {}

    def updateRankList(self, rankList):
        if rankList:
            self.rankList = rankList
        else:
            if self.type==constant.RANK_HETI:
                self.rankList = []
                self.minEle = []

    def getRankList(self):
        return self.rankList

    def GetSnapshot(self):
        if self.type==constant.RANK_HETI:
            self.rankListCopy=Game.rpc_global_rank_mgr.GetSnapshot(self.type)
        else:
            if not self.rankListCopy:
                self.rankListCopy=Game.rpc_global_rank_mgr.GetSnapshot(self.type)

        retval=[]
        for v in self.rankListCopy:
            if not v.get("reward"):
                break
            retval.append(v)
        return retval


    def getMyRank(self, pid):
        for player in self.rankList:
            if player.get("id", 0) == pid:
                return player.get("rank", 0)
        return 0

    def getMyRankByList(self, pid, List):
        for player in List:
            if player.get("id", 0) == pid:
                return player.get("rank", 0)
        return 0

    def getMyRankBySnapshot(self, pid):
        rankListCopy = self.GetSnapshot()
        for player in rankListCopy:
            if player.get("id", 0) == pid:
                return player.get("rank", 0)
        return 0




