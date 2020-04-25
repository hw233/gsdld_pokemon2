#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from game.common import utility
from game.define import constant
from game import Game
import random
import time
from corelib.gtime import cur_day_hour_time
from game.core.cycleData import CycleDay

# 副本(fubenInfo,json)
# 	材料副本(clbz,[json])
# 		副本id(fubenId,int)
# 			只会发已通关
# 		今日已挑战次数(challengeNum,int)
# 	龙王宝藏(lwbz,[json])
# 		已通关列表(passLevel,[json])
# 			关卡id(levelId,int)
# 			星数(star,int)
# 			每日挖宝状态(dailyStatus,int)
# 		藏宝图id(baotuId,int)
# 		宝箱状态(starReward,[int])
# 	小雷音寺(xlys,json)
# 		关卡id(levelId,int)
# 	天庭试炼(ttsl,[json])
# 		关卡id(levelId,int)
# 		宝箱状态(rewardStatus,int)
# 		每日挑战状态(dailyStatus,int)

class PlayerFuben(utility.DirtyFlag):
    def __init__(self, owner):
        utility.DirtyFlag.__init__(self)
        self.owner = owner
        self.clfbSuccessCount = 0   # 材料副本胜利次数
        self.clfbFightNum = {}      #材料副本胜利次数 {fbid:num}
        self.clfbId = []            # 材料副本通关id
        self.lwbz = {}              # baotuId:Cangbaotu 神秘宝藏
        self.lwbzRewardNum = 0      #领取龙王宝藏星级奖励次数
        self.xlysMaxLevelId = 0     # 小雷音寺最大关卡id 古代遗迹
        self.ttslMaxLevelId = 0     # 天庭试炼最大通关关卡id 精灵试炼
        self.ttslRewardStatus = {}        # 关卡id：宝箱状态
        self.cycleDay = CycleDay(self)

        self.save_cache = {}

    def markDirty(self):
        utility.DirtyFlag.markDirty(self)
        if self.owner:
            self.owner.markDirty()

    def to_save_dict(self, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            self.save_cache = {}
            self.save_cache["cycleDay"] = self.cycleDay.to_save_bytes()

            self.save_cache["clfbSuccessCount"] = self.clfbSuccessCount
            self.save_cache["lwbzRewardNum"] = self.lwbzRewardNum
            
            self.save_cache["clfbId"] = self.clfbId
            self.save_cache["lwbz"] = []
            for baozang in self.lwbz.values():
                self.save_cache["lwbz"].append(baozang.to_save_dict(forced=forced))

            self.save_cache["xlysMaxLevelId"] = self.xlysMaxLevelId
            self.save_cache["ttslMaxLevelId"] = self.ttslMaxLevelId
            self.save_cache["ttslRewardStatus"] = []
            for k, v in self.ttslRewardStatus.items():
                self.save_cache["ttslRewardStatus"].append({"levelId": k, "status": v})

            self.save_cache["clfbFightNum"] = []
            for k, v in self.clfbFightNum.items():
                self.save_cache["clfbFightNum"].append({"fbid": k, "num": v})
            
        return self.save_cache

    def load_from_dict(self, data):
        self.cycleDay.load_from_dict(data.get("cycleDay", ""))
        self.clfbSuccessCount = data.get("clfbSuccessCount", 0)
        self.lwbzRewardNum = data.get("lwbzRewardNum", 0)
        lwbz = data.get("lwbz", [])
        for one in lwbz:
            cangbaotu = Cangbaotu(0, data=one, owner=self.owner)
            self.lwbz[cangbaotu.baotuId] = cangbaotu

        self.xlysMaxLevelId = data.get("xlysMaxLevelId", 0)
        self.ttslMaxLevelId = data.get("ttslMaxLevelId", 0)
        self.clfbId = data.get("clfbId", [])
        ttslRewardStatus = data.get("ttslRewardStatus", [])
        for v in ttslRewardStatus:
            levelId = v.get("levelId", 0)
            status = v.get("status", 0)
            if levelId > 0:
                self.ttslRewardStatus[levelId] = status

        clfbFightNum = data.get("clfbFightNum", [])
        for v in clfbFightNum:
            fbid = v.get("fbid", 0)
            num = v.get("num", 0)
            self.clfbFightNum[fbid] = num


    def to_init_data(self):
        init_data = {}
        init_data["clbz"] = []
        for k in self.clfbId:
            init_data["clbz"].append({"fubenId": k, "challengeNum": self.getClbzChanllengeNum(k)})

        init_data["lwbz"] = []
        for one in self.lwbz.values():
            init_data["lwbz"].append(one.to_init_data())

        init_data["xlys"] = {"maxLevelId": self.xlysMaxLevelId}
        init_data["ttsl"] = {}
        init_data["ttsl"]["maxLevelId"] = self.ttslMaxLevelId
        init_data["ttsl"]["todayMaxLevelId"] = self.getTtslTodayMaxLevelId()
        init_data["ttsl"]["rewardStatus"] = []
        for k, v in self.ttslRewardStatus.items():
            init_data["ttsl"]["rewardStatus"].append({"levelId": k, "status": v})
        
        init_data["XlysBuffCanBuy"]=self.getXlysBuffCanBuy()
        init_data["XlysBuff"]=self.getXlysBuff()

        return init_data

    def to_wee_hour_data(self):
        return self.to_init_data()

    def clfbGetInfo(self):
        resp = {}
        resp["clbz"] = []
        for k in self.clfbId:
            num = self.getClbzChanllengeNum(k)
            resp["clbz"].append({"fubenId": k, "challengeNum": num})
        return resp

    def getClbzChanllengeNum(self, fubenId):
        # 今日0点
        time_0 = cur_day_hour_time(hour=0)
        # 今日12点
        time_12 = cur_day_hour_time(hour=12)
        # 今日19点
        time_19 = cur_day_hour_time(hour=19)
        # 当前时间
        time_now = int(time.time())

        clbzTime = self.cycleDay.Query("clbzChanllengeTime", {})
        clbz = self.cycleDay.Query("clbzChanllengeNum", {})
        keys = list(clbzTime.keys())
        for fid in keys:
            lasttime = clbzTime.get(fid, 0)

            if lasttime < time_0:
                clbz[fid] = 0
            elif time_0 <= lasttime <= time_12 and time_12 <= time_now:
                clbz[fid] = 0
            elif time_12 <= lasttime <= time_19 and time_19 <= time_now:
                clbz[fid] = 0
        self.cycleDay.Set("clbzChanllengeNum", clbz)
        return clbz.get(fubenId, 0)

    def setClbzChanllengeNum(self, fubenId, num):
        clbz = self.cycleDay.Query("clbzChanllengeNum", {})
        clbz[fubenId] = num
        self.cycleDay.Set("clbzChanllengeNum", clbz)

        clbzTime = self.cycleDay.Query("clbzChanllengeTime", {})
        clbzTime[fubenId] = int(time.time())
        self.cycleDay.Set("clbzChanllengeTime", clbzTime)

    def getXlysBuffCanBuy(self):
        l=self.cycleDay.Query("XlysBuffCanBuy", [])
        if not l:
            l=list(Game.res_mgr.res_xlysBuff.keys())
            # random.shuffle(l)
            # l=l[:3]
            l=random.sample(l,3)
            self.cycleDay.Set("XlysBuffCanBuy", l)
        return l

    def getXlysBuff(self):
        v=self.cycleDay.Query("XlysBuff", {})

        for k in Game.res_mgr.res_xlysBuff.keys():
            if k not in v:
                v[k]={"per":0,"count":0}
        
        self.cycleDay.Set("XlysBuff", v)

        return v

    def addXlysBuff(self, key):

        res = Game.res_mgr.res_xlysBuff.get(key, None)

        buff=self.getXlysBuff()

        buff[key]["per"]+=res.per
        buff[key]["count"]+=1

        self.cycleDay.Set("XlysBuff", buff)

    def getClbzChanllengeNumTotal(self):
        return self.cycleDay.Query("clbzChanllengeTotalNum", 0)

    def setClbzChanllengeNumTotal(self, num):
        self.cycleDay.Set("clbzChanllengeTotalNum", num)

    def getCangbaotu(self, baotuId):
        cangbaotu = self.lwbz.get(baotuId, None)
        if not cangbaotu:
            cangbaotu = Cangbaotu(baotuId, None, self.owner)
            self.lwbz[baotuId] = cangbaotu

        return cangbaotu

    def getLwbzUnChallengeLevel(self):
        unList = []
        keys = list(self.lwbz.keys())
        keys.sort()
        for key in keys:
            cangbaotu = self.lwbz.get(key)
            isbreak, resp = cangbaotu.getUnChallengeLevel()
            unList.extend(resp)
            if isbreak:
                break
        return unList

    def addClbfId(self, fubenId):
        if fubenId in self.clfbId:
            return

        self.clfbId.append(fubenId)

    def getXlysMaxLevelId(self):
        return self.xlysMaxLevelId

    def setXlysMaxLevelId(self, levelId):
        self.xlysMaxLevelId = levelId
        self.markDirty()

    def getTtslMaxLevelId(self):
        return self.ttslMaxLevelId

    def setTtslMaxLevelId(self, levelId):
        self.ttslMaxLevelId = levelId
        self.markDirty()

    def getTtslTodayMaxLevelId(self):
        ttslDailyToday = self.cycleDay.Query("ttslDailyToday", 0)
        return ttslDailyToday

    def setTtslTodayMaxLevelId(self, levelId):
        self.cycleDay.Set("ttslDailyToday", levelId)

    def getTtslRewardStatus(self, levelId):
        return self.ttslRewardStatus.get(levelId, 0)

    def markTtslRewardStatus(self, levelId):
        self.ttslRewardStatus[levelId] = 1

    def getLwbzTotalStar(self):
        totalStar = 0
        for cangbaotu in self.lwbz.values():
            totalStar += cangbaotu.getTotalStar()

        return totalStar

    def IncClfbSuccessCount(self):
        self.clfbSuccessCount += 1
        self.markDirty()

    def getClfbSuccessCount(self):
        return self.clfbSuccessCount

    def IncLwbzRewardNum(self):
        self.lwbzRewardNum += 1
        self.markDirty()

    def getLwbzRewardNum(self):
        return self.lwbzRewardNum

    def getClfbFightNum(self, fbId):
        return self.clfbFightNum.get(fbId, 0)

    def IncClfbFightNum(self, fbId):
        iNum = self.clfbFightNum.get(fbId, 0)
        iNum += 1
        self.clfbFightNum[fbId] = iNum
        self.markDirty()

    def getLwbzMaxKey(self):
        """获取龙王宝藏最大通关id"""
        if not self.lwbz:
            return 0
        maxBaotuId = 0
        maxBaotuObj = None
        for BaotuId, BaotuObj in self.lwbz.items():
            if BaotuObj.passLevel and BaotuId > maxBaotuId:
                maxBaotuId = BaotuId
                maxBaotuObj = BaotuObj
        if maxBaotuObj:
            return max(list(maxBaotuObj.passLevel.keys()))
        else:
            return 0


class Cangbaotu(utility.DirtyFlag):
    def __init__(self, baotuId, data=None, owner=None):
        utility.DirtyFlag.__init__(self)
        self.baotuId = baotuId
        self.passLevel = {}         # levelId:star
        self.starReward = [0]*3     # 对应3星，6星，12星

        self.save_cache = {}

        if data:
            self.load_from_dict(data)
        if owner:
            self.set_owner(owner)

    def to_save_dict(self, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            self.save_cache = {}
            self.save_cache["baotuId"] = self.baotuId
            self.save_cache["starReward"] = self.starReward
            self.save_cache["passLevel"] = []
            for k, v in self.passLevel.items():
                self.save_cache["passLevel"].append({"levelId": k, "star": v})

        return self.save_cache

    def load_from_dict(self, data):
        self.baotuId = data.get("baotuId", 1)
        self.starReward = data.get("starReward", [])
        passLevel = data.get("passLevel", [])
        for v in passLevel:
            levelId = v.get("levelId", 0)
            star = v.get("star", 0)
            if levelId > 0 and star > 0:
                self.passLevel[levelId] = star

    def to_init_data(self):
        init_data = {}
        init_data["baotuId"] = self.baotuId
        init_data["starReward"] = self.starReward
        init_data["passLevel"] = []
        for k,v in self.passLevel.items():
            levelInfo = {"levelId": k, "star": v, "dailyStatus": self.getDailyStatus(k)}
            init_data["passLevel"].append(levelInfo)

        return init_data

    def set_owner(self, owner):
        self.ownerFuben = owner.fuben

    def markDirty(self):
        utility.DirtyFlag.markDirty(self)
        if self.ownerFuben:
            self.ownerFuben.markDirty()

    def getDailyStatus(self, levelId):
        cangbaotuDaliy = self.ownerFuben.owner.cycleDay.Query("cangbaotuDaliy", {})
        return cangbaotuDaliy.get(levelId, 0)

    def markDailyStatus(self, levelId):
        cangbaotuDaliy = self.ownerFuben.owner.cycleDay.Query("cangbaotuDaliy", {})
        cangbaotuDaliy[levelId] = 1
        self.ownerFuben.owner.cycleDay.Set("cangbaotuDaliy", cangbaotuDaliy)

    def getLevelStar(self, levelId):
        return self.passLevel.get(levelId, 0)

    def setLevelStar(self, levelId, star):
        self.passLevel[levelId] = star
        self.markDirty()

    def getUnChallengeLevel(self):
        unList = []
        cangbaotuDaliy = self.ownerFuben.owner.cycleDay.Query("cangbaotuDaliy", {})
        keys = list(self.passLevel.keys())
        keys.sort()
        isbreak = 0
        for levelId in keys:
            star = self.passLevel.get(levelId, 0)
            if star != constant.STAR_3:
                isbreak = 1
                break
            if not cangbaotuDaliy.get(levelId, 0) and star == constant.STAR_3:
                unList.append(levelId)
        return isbreak, unList

    def getTotalStar(self):
        totalStar = 0
        for star in self.passLevel.values():
            totalStar += star
        return totalStar

    def getStarRewardStatus(self, startId):
        if 1 <= startId <= 3:
            return self.starReward[startId-1]
        return 0

    def markStarRewardStatus(self, startId):
        if 1 <= startId <= 3:
            self.starReward[startId-1] = 1