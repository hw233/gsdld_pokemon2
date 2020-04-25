#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import time

from game.common import utility
from game.define import msg_define

from game import Game
from corelib import gtime
from game.define import constant
from game.core.cycleData import CycleDay

#角色vip信息
class PlayerVip(utility.DirtyFlag):
    def __init__(self, owner):
        utility.DirtyFlag.__init__(self)
        self.owner = owner  # 拥有者
        self.vip = 0 #vip等级
        self.vipExp = 0 #vip经验
        self.vipGetList = [] #已经领取列表
        self.monthCard = 0 #月卡过期时间 
        self.weekCard = 0 #周卡过期时间 
        self.onlineExpExtra = 0 #在线挂机额外增加百分比 经验
        self.onlineGoldExtra = 0 #在线挂机额外增加百分比 金币
        self.monthCardReward = [] #月卡领奖列表
        self.weekCardReward = [] #周卡领奖列表
        self.monthCardBagExt = False #月卡扩容
        self.battleJumpNum = 0 # 战斗跳过次数
        self.zhizunCardFlag = 0 #至尊卡标识
        self.timeFinish = [] #vip前3级免费领取

        self.cycleDay = CycleDay(self)

        self.save_cache = {} #存储缓存


    def markDirty(self):
        utility.DirtyFlag.markDirty(self)
        if self.owner:
            self.owner.markDirty()

    #今日已领取跳过次数的等级
    def GetTodayBattleJumpNumLV(self):
        return self.cycleDay.Query("todayBattleJumpNumLV", [])

    def SetTodayBattleJumpNumLV(self, lvs):
        self.cycleDay.Set("todayBattleJumpNumLV", lvs)

    #今日已领取至尊卡奖励标识
    def GetTodayZhiZunRewardFlag(self):
        return self.cycleDay.Query("todayZhiZunRewardFlag", 0)

    def SetTodayZhiZunRewardFlag(self, flag):
        self.cycleDay.Set("todayZhiZunRewardFlag", flag)

    #存库数据
    def to_save_dict(self, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            self.save_cache = {}

            self.save_cache["cycleDay"] = self.cycleDay.to_save_bytes()

            self.save_cache["vip"] = self.vip
            self.save_cache["vipExp"] = self.vipExp
            self.save_cache["monthCard"] = self.monthCard
            self.save_cache["weekCard"] = self.weekCard
            self.save_cache["onlineExpExtra"] = self.onlineExpExtra
            self.save_cache["onlineGoldExtra"] = self.onlineGoldExtra
            self.save_cache["monthCardReward"] = self.monthCardReward
            self.save_cache["weekCardReward"] = self.weekCardReward
            self.save_cache["monthCardBagExt"] = self.monthCardBagExt
            self.save_cache["vipGetList"] = self.vipGetList
            self.save_cache["battleJumpNum"] = self.battleJumpNum
            self.save_cache["zhizunCardFlag"] = self.zhizunCardFlag
            self.save_cache["timeFinish"] = self.timeFinish
            

        return self.save_cache

    #读库数据初始化
    def load_from_dict(self, data):
        
        self.cycleDay.load_from_dict(data.get("cycleDay", ""))

        self.vip = data.get("vip", 0)  # vip等级
        self.vipExp = data.get("vipExp", 0)  # vip经验
        self.monthCard = data.get("monthCard", 0)  # 月卡
        self.weekCard = data.get("weekCard", 0)  # 周卡
        self.onlineExpExtra = data.get("onlineExpExtra", 0)  # 
        self.onlineGoldExtra = data.get("onlineGoldExtra", 0)  # 
        self.monthCardReward = data.get("monthCardReward", [])  # 月卡领奖列表
        self.weekCardReward = data.get("weekCardReward", [])  # 周卡领奖列表
        self.monthCardBagExt = data.get("monthCardBagExt", 0)  # 月卡扩容
        self.vipGetList = data.get("vipGetList", [])  # 已经领取列表
        self.battleJumpNum = data.get("battleJumpNum", 0)  # 战斗跳过次数
        self.zhizunCardFlag = data.get("zhizunCardFlag", 0)  # 至尊卡标识
        self.timeFinish = data.get("timeFinish", [])  # vip倒计时免费领取


        ilen = len(self.timeFinish)
        keys = list(Game.res_mgr.res_vip.keys())
        keys.sort()
        for lv in keys:
            vipRes = Game.res_mgr.res_vip.get(lv)
            if lv > ilen:
                self.timeFinish.append(vipRes.rewardTime)
            if lv in self.vipGetList:
                self.timeFinish[lv - 1] = 0
        
    #登录初始化下发数据
    def to_init_data(self):
        init_data = {}
        init_data["vip"] = self.vip
        init_data["vipExp"] = self.vipExp
        init_data["monthCard"] = self.monthCard
        init_data["weekCard"] = self.weekCard
        init_data["onlineExpExtra"] = self.onlineExpExtra
        init_data["onlineGoldExtra"] = self.onlineGoldExtra
        init_data["vipGetList"] = self.vipGetList
        init_data["vipDayRewardGetList"] = self.GetVIPDayRewardList()
        init_data["battleJumpNum"] = self.battleJumpNum
        init_data["zhizunCardFlag"] = self.zhizunCardFlag
        init_data["timeFinish"] = self.timeFinish


        init_data["todayZhiZunRewardFlag"] = self.GetTodayZhiZunRewardFlag()
        self.markDirty()
        return init_data

    def to_wee_hour_data(self):
        self.init_battleJumpNum()
        return self.to_init_data()


    def init_battleJumpNum(self, checkMax=True):
        has_get = self.GetTodayBattleJumpNumLV()
        if self.vip in has_get:
            return
        vipRes = Game.res_mgr.res_vip.get(self.vip, None)
        if not vipRes:
            return
        has_get.append(self.vip)
        if vipRes.battleJumpNum != -1:
            self.battleJumpNum += vipRes.battleJumpNum
            if self.battleJumpNum > vipRes.battleJumpNum*2 and checkMax:
                self.battleJumpNum = vipRes.battleJumpNum*2
        else:
            self.battleJumpNum = -1

        self.SetTodayBattleJumpNumLV(has_get)
        self.markDirty()

    def getBattleJumpNum(self):
        return self.battleJumpNum

    def setBattleJumpNum(self, num):
        self.battleJumpNum = num
        self.markDirty()

    def GetVipLv(self):
        return self.vip

    def onlineExpExtraAdd(self,v):
        self.onlineExpExtra+=v
        self.markDirty()
    
    def onlineGoldExtraAdd(self,v):
        self.onlineGoldExtra+=v
        self.markDirty()

    def getOnlineExpExtra(self):
        return self.onlineExpExtra

    def getOnlineGoldExtra(self):
        return self.onlineGoldExtra

    def SetVipLv(self, viplv):
        for v in range(self.vip+1,viplv+1):
            self.vip = v
            
            #抛出角色升级消息
            self.owner.safe_pub(msg_define.MSG_ROLE_VIPLV_UPGRADE, self.vip)
            #抛出change
            self.owner.safe_pub(msg_define.MSG_ROLE_XLV_UPGRADE)

            self.markDirty()

            self.init_battleJumpNum(checkMax=False)

    def isMonthCard(self):
        t = int(time.time())
        if self.monthCard<t:
            return 0
        return 1
    
    def addMonthCard30day(self):
        t = int(time.time())
        if self.monthCard<t:
            self.monthCard = t+60*60*24*30
        else:
            self.monthCard += 60*60*24*30
        sd = 0
        if len(self.monthCardReward)!=0:
            sd = self.monthCardReward[-1]
        nd = gtime.getIntArrayYYYYMMDD(30,sd)
        self.monthCardReward.extend(nd)
        self.markDirty()
    
    def addWeekCard7day(self):
        t = int(time.time())
        if self.weekCard<t:
            self.weekCard = t+60*60*24*7
        else:
            self.weekCard += 60*60*24*7
        sd = 0
        if len(self.weekCardReward)!=0:
            sd = self.weekCardReward[-1]
        nd = gtime.getIntArrayYYYYMMDD(7,sd)
        self.weekCardReward.extend(nd)
        self.markDirty()

    def addzZhiZunCardAllday(self):
        self.owner.bag.addSize(100)
        self.zhizunCardFlag = 1
        self.markDirty()

    def GetBuyQmBossTz(self):
        # 全民boss今日已购买挑战次数(qmBossTz, int)
        return self.cycleDay.Query("qmBossTodayBuyTZ", 0)

    def SetBuyQmBossTz(self, num):
        # 全民boss今日已购买挑战次数(qmBossTz, int)
        self.cycleDay.Set("qmBossTodayBuyTZ", num)

    def GetVIPDayRewardList(self):
        # vip每日奖励领取列表
        return self.cycleDay.Query("VIPDayRewardList", [])

    def SetVIPDayRewardList(self, ls):
        # vip每日奖励领取列表
        self.cycleDay.Set("VIPDayRewardList", ls)

    
    def vipRewardMonth(self):
        nt = gtime.getYYYYMMDD()
        nt = int(nt)

        if len(self.monthCardReward)==0:
            return False

        if self.monthCardReward[0]!=nt:
            return False

        self.monthCardReward.pop(0)
        self.markDirty()
        return True

    def vipRewardWeek(self):
        nt = gtime.getYYYYMMDD()
        nt = int(nt)

        if len(self.weekCardReward)==0:
            return False

        if self.weekCardReward[0]!=nt:
            return False

        self.weekCardReward.pop(0)
        self.markDirty()
        return True

    def updateRewardTime(self):
        now = int(time.time())
        iloginTime = self.owner.data.GetLoginTime()
        passtime = now - iloginTime
        for i in range(len(self.timeFinish)):
            self.timeFinish[i] = self.timeFinish[i] - passtime
            if self.vip > 3 and self.vip > i+1:
                self.timeFinish[i] = 0
            if self.timeFinish[i] < 0:
                self.timeFinish[i] = 0
        self.markDirty()

    # 0==可以领取 1未到达 2以领取 3时间未到
    def vipReward(self,lv):
        if self.vip<lv:
            return 1
        if lv in self.vipGetList:
            return 2
        if len(self.timeFinish) >= lv and self.timeFinish[lv-1]:
            if self.vip > 3 and self.vip > lv:
                return 0
            now = int(time.time())
            iloginTime = self.owner.data.GetLoginTime()
            passtime = now - iloginTime
            if self.timeFinish[lv-1] - passtime <= 0:
                return 0
            else:
                return 3
        return 0

    def setVipReward(self,lv):
        self.vipGetList.append(lv)
        self.markDirty()

    def addExp(self,exp):
        self.vipExp += exp
        
        while True:

            res = Game.res_mgr.res_vip.get(self.vip)
            if not res:
                Game.glog.log2File("VIP_ADDEXP_NOTFOUND_RES", "%s|%s" % (self.owner.id, self.vip))
                break

            if self.vipExp>=res.exp:
                resN = Game.res_mgr.res_vip.get(self.vip+1)
                # self.owner.bag.addSize(res.addbag)
                if resN:
                    self.SetVipLv(self.vip + 1)
                else:
                    break
            else:
                break


        self.markDirty()



    # 角色下线时要做的清理操作
    def uninit(self):
        pass