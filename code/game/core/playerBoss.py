#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import time

from game.common import utility
from game.define import msg_define

from corelib.frame import Game
from corelib import spawn_later

from game.core.cycleData import CycleDay

# boss模块(bossInfo, json)
# 个人boss(grBoss, json)
# 	boss列表(bossList, [json])
# 		个人bossId(id, int)
# 		今日已挑战次数(num, int)
# 		是否首通(first, int)
# 			0=未首通 1=已首通
# 		今日是否已击杀(kill, int)
# 			0=未击杀 1=已击杀
# 全民boss(qmBoss, json)
# 	剩余挑战次数(num, int)
# 	下次恢复时间戳(time, int)
# 	boss提醒列表(remind, [int])
# 		全民bossid
# 生死劫(ssjBoss, json)
# 	章节数据(allData, [json])
# 		配置表id(id, int)
# 		是否已首通(firstFinish, int)
# 		今天是否已通关(finish, int)
# 	今日剩余协助次数(num, int)

#角色Boss
class PlayerBoss(utility.DirtyFlag):
    def __init__(self, owner):
        utility.DirtyFlag.__init__(self)
        self.owner = owner  # 拥有者
        self.grBoss = {} #个人boss {个人bossId:{是否首通:0}}
        self.qmBoss = {} #{num:1, remind:[], time:0}
        self.ssjBoss = {} #{配置表id: {是否首通:0}}

        self.cycleDay = CycleDay(self)

        self.save_cache = {} #存储缓存

        self.qmboss_num_timer = None #全民boss挑战次数恢复计时器

    def SetGrBossTodayTZ(self, id, num):
        """个人boss 今日已挑战次数"""
        grBossTodayTZ = self.cycleDay.Query("grTZ", {})
        grBossTodayTZ[id] = num
        self.cycleDay.Set("grTZ", grBossTodayTZ)

    def GetGrBossTodayTZ(self, id):
        """个人boss 今日已挑战次数"""
        grBossTodayTZ = self.cycleDay.Query("grTZ", {})
        return grBossTodayTZ.get(id, 0)

    def SetGrBossTodayKill(self, id):
        """个人boss 今日是否已击杀"""
        grBossTodayKill = self.cycleDay.Query("grKill", {})
        grBossTodayKill[id] = 1
        self.cycleDay.Set("grKill", grBossTodayKill)

    def GetGrBossTodayKill(self, id):
        """个人boss 今日是否已击杀"""
        grBossTodayKill = self.cycleDay.Query("grKill", {})
        return grBossTodayKill.get(id, 0)

    def SetYwBossTodayTZ(self, num):
        """野外boss 今日已挑战次数"""
        self.cycleDay.Set("ywTZ", num)

    def GetYwBossTodayTZ(self):
        """野外boss 今日已挑战次数"""
        return self.cycleDay.Query("ywTZ", 0)

    def SetYwBossLastTZTime(self, iTime):
        """野外boss 今日最后一次挑战时间"""
        self.cycleDay.Set("ywLastTZ", iTime)

    def GetYwBossLastTZTime(self):
        """野外boss 今日最后一次挑战时间"""
        return self.cycleDay.Query("ywLastTZ", 0)

    def SetSsjBossTodayKill(self, id):
        """生死劫 今日是否已击杀"""
        ssjBossTodayKill = self.cycleDay.Query("ssjKill", {})
        ssjBossTodayKill[id] = 1
        self.cycleDay.Set("ssjKill", ssjBossTodayKill)

    def GetSsjBossTodayKill(self, id):
        """生死劫 今日是否已击杀"""
        ssjBossTodayKill = self.cycleDay.Query("ssjKill", {})
        return ssjBossTodayKill.get(id, 0)

    def SetSsjBossTodayHelp(self, num):
        """生死劫 今日已协助次数"""
        self.cycleDay.Set("ssjHelp", num)

    def GetSsjBossTodayHelp(self):
        """生死劫 今日已协助次数"""
        return self.cycleDay.Query("ssjHelp", 0)

    def markDirty(self):
        utility.DirtyFlag.markDirty(self)
        if self.owner:
            self.owner.markDirty()

    def uninit(self):
        if self.qmboss_num_timer:
            self.qmboss_num_timer.kill(block=False)
            self.qmboss_num_timer = None

    #存库数据
    def to_save_dict(self, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            self.save_cache = {}
            if self.cycleDay.data:
                self.save_cache["cycleDay"] = self.cycleDay.to_save_bytes()

            if self.grBoss:
                self.save_cache["grBoss"] = {}  # 个人boss {个人bossId:{是否首通:0}}
                for k, v in self.grBoss.items():
                    self.save_cache[str(k)] = v

            if self.qmBoss:
                self.save_cache["qmBoss"] = self.qmBoss  #{num:1, remind:[], time:0}

            if self.ssjBoss:
                self.save_cache["ssjBoss"] = {}  # {配置表id: {是否首通:0}}
                for k, v in self.ssjBoss.items():
                    self.save_cache[str(k)] = v

        return self.save_cache

    #读库数据初始化
    def load_from_dict(self, data):
        self.cycleDay.load_from_dict(data.get("cycleDay", ""))

        grBoss = data.get("grBoss", {})  # {个人bossId:{是否首通:0}}
        for k, v in grBoss.items():
            self.grBoss[int(k)] = v

        self.qmBoss = data.get("qmBoss", {})  #{num:1, remind:[], time:0}

        ssjBoss = data.get("ssjBoss", {})  # {配置表id: {是否首通:0}}
        for k, v in ssjBoss.items():
            self.ssjBoss[int(k)] = v

        #处理初始化次数
        resQmBossTzCnt = Game.res_mgr.res_common.get("qmBossTzCnt")
        if not self.qmBoss:
            self.addQmBossTZ(resQmBossTzCnt.i)
        # 处理全民boss离线增加的挑战次数
        now = int(time.time())
        resQmBossCD = Game.res_mgr.res_common.get("qmBossCD")
        qmBossTZ = self.GetQmBossTZ()
        if qmBossTZ < resQmBossTzCnt.i:
            iNextTime = self.GetQmBossTime()
            if not iNextTime:
                iNextTime = now + resQmBossCD.i
                self.SetQmBossTime(iNextTime)
                self.qmboss_num_timer = spawn_later(resQmBossCD.i, self.addQmBossTZ, 1)
            else:
                if iNextTime > now: #还没到时间
                    idelay = iNextTime - now
                    self.qmboss_num_timer = spawn_later(idelay, self.addQmBossTZ, 1)
                else: #到时间了
                    self.addQmBossTZ(1) #增加一次
                    #然后再判断 次数是否满了
                    qmBossTZ = self.GetQmBossTZ()
                    if qmBossTZ >= resQmBossTzCnt.i:
                        return
                    #次数没满的情况下 判断超过多个周期
                    iOffLine = now - iNextTime
                    iAdd = int(iOffLine/resQmBossCD.i)
                    if iAdd:
                        self.addQmBossTZ(iAdd)
                        qmBossTZ = self.GetQmBossTZ()
                        #如果还是没满，启动定时器
                        if qmBossTZ < resQmBossTzCnt.i:
                            idelay = resQmBossCD.i - iOffLine%resQmBossCD.i
                            iNextTime = now + idelay
                            self.SetQmBossTime(iNextTime)
                            self.qmboss_num_timer = spawn_later(idelay, self.addQmBossTZ, 1)

    #登录初始化下发数据
    def to_init_data(self):
        init_data = {}
        grBoss = {}
        bossList = []
        for grBossId, data in self.grBoss.items():
            one = {}
            one['id'] = grBossId
            one['num'] = self.GetGrBossTodayTZ(grBossId)
            one['first']  = data.get("first", 0)
            one['kill'] = self.GetGrBossTodayKill(grBossId)
            bossList.append(one)
        grBoss['bossList'] = bossList
        init_data['grBoss'] = grBoss

        qmBoss = {}
        qmBoss['num'] = self.qmBoss.get("num", 0)
        qmBoss['time'] = self.qmBoss.get("time", 0)
        qmBoss['remind'] = self.qmBoss.get("remind", [])
        init_data['qmBoss'] = qmBoss

        ssjBoss = {}
        allData = []
        for ssjBossId, data in self.ssjBoss.items():
            one = {}
            one['id'] = ssjBossId
            one['firstFinish'] = data.get("first", 0)
            one['finish'] = self.GetSsjBossTodayKill(ssjBossId)
            allData.append(one)
        ssjBoss['allData'] = allData
        res = Game.res_mgr.res_common.get("ssjBossHelpNum")
        ssjBoss['num'] = res.i - self.GetSsjBossTodayHelp()
        init_data['ssjBoss'] = ssjBoss
        return init_data

    #零点更新的数据
    def to_wee_hour_data(self):
        return self.to_init_data()

    def IsGrBossFirst(self, id):
        """个人boss是否已首通"""
        data = self.grBoss.get(id, {})
        return data.get("first", 0)

    def to_grboss_data(self, idList):
        update_data = {}
        grBoss = {}
        bossList = []
        for id in idList:
            data = self.grBoss.get(id, {})
            if data:
                one = {}
                one['id'] = id
                one['num'] = self.GetGrBossTodayTZ(id)
                one['first'] = data.get("first", 0)
                one['kill'] = self.GetGrBossTodayKill(id)
                bossList.append(one)
        grBoss['bossList'] = bossList
        update_data['grBoss'] = grBoss
        return update_data

    def SetGrBossFirst(self, id):
        data = self.grBoss.setdefault(id, {})
        data["first"] = 1
        self.markDirty()

    def addQmBossTZ(self, add):
        num = self.qmBoss.get("num", 0) #{num:1, remind:[], time:0}
        num += add
        resQmBossTzCnt = Game.res_mgr.res_common.get("qmBossTzCnt")
        if num >= resQmBossTzCnt.i:
            if self.qmboss_num_timer:
                self.qmboss_num_timer.kill(block=False)
                self.qmboss_num_timer = None
            self.SetQmBossTime(0)
            num = resQmBossTzCnt.i
        else:
            now = int(time.time())
            if now >= self.GetQmBossTime() and self.qmboss_num_timer:
                self.qmboss_num_timer.kill(block=False)
                self.qmboss_num_timer = None
                resQmBossCD = Game.res_mgr.res_common.get("qmBossCD")
                self.qmboss_num_timer = spawn_later(resQmBossCD.i, self.addQmBossTZ, 1)
                self.SetQmBossTime(now + resQmBossCD.i)

        self.qmBoss["num"] = num
        self.markDirty()

    def delQmBossTZ(self, dele):
        num = self.qmBoss.get("num", 0)  # {num:1, remind:[], time:0}
        num -= dele
        resQmBossCD = Game.res_mgr.res_common.get("qmBossCD")
        if not self.qmboss_num_timer:
            self.qmboss_num_timer = spawn_later(resQmBossCD.i, self.addQmBossTZ, 1)
            now = int(time.time())
            self.SetQmBossTime(now + resQmBossCD.i)
        self.qmBoss["num"] = num
        self.markDirty()

    def GetQmBossTZ(self):
        return self.qmBoss.get("num", 0)

    def GetQmBossRemind(self):
        return self.qmBoss.get("remind", [])

    def SetQmBossRemind(self, remind):
        self.qmBoss["remind"] = remind
        self.markDirty()

    def GetQmBossTime(self):
        return self.qmBoss.get("time", 0)

    def SetQmBossTime(self, iTime):
        self.qmBoss["time"] = iTime
        self.markDirty()

    def getSsjBossFirstNum(self):
        iTotal = 0
        for _id, data in self.ssjBoss.items():
            if data.get("first", 0):
                iTotal += 1
        return iTotal

    def GetSsjBossFirst(self, id):
        """生死劫boss是否已首通"""
        data = self.ssjBoss.get(id, {})
        return data.get("first", 0)

    def SetSsjBossFirst(self, id):
        """生死劫boss是否已首通"""
        data = self.ssjBoss.setdefault(id, {})
        data["first"] = 1
        self.markDirty()

    def to_ssjboss_data(self, idList):
        update_data = {}
        ssjBoss = {}
        allData = []
        for id in idList:
            data = self.ssjBoss.get(id, {})
            if data:
                one = {}
                one['id'] = id
                one['firstFinish'] = self.GetSsjBossFirst(id)
                one['finish'] = self.GetSsjBossTodayKill(id)
                allData.append(one)

        ssjBoss['allData'] = allData

        res = Game.res_mgr.res_common.get("ssjBossHelpNum")
        ssjBoss['num'] = res.i - self.GetSsjBossTodayHelp()
        update_data['ssjBoss'] = ssjBoss
        return update_data



