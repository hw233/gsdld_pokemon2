#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import time
from game.common import utility
from corelib.frame import Game
from game.define import constant, msg_define

from game.core.cycleData import CycleDay
# from game.mgr.task import CreatTask

class PlayerDaoGuan(utility.DirtyFlag):
    def __init__(self, owner):
        utility.DirtyFlag.__init__(self)
        self.owner = owner      # 拥有者
        self.area = 0           # 当前道馆所处地区
        self.pavilionData = {}  # 道馆数据 {1:obj}
        self.cycleDay = CycleDay(self)

        self.save_cache = {}

        # 监听角色升级
        self.owner.sub(msg_define.MSG_ROLE_XLV_UPGRADE, self.event_lv_uprade)

    def markDirty(self):
        utility.DirtyFlag.markDirty(self)
        if self.owner:
            self.owner.markDirty()

    def SetDaoGuanDayChallengeNum(self, num):
        """今日挑战次数"""
        self.cycleDay.Set("DaoGuanDayChallengeNum", num)

    def GetDaoGuanDayChallengeNum(self):
        """今日挑战次数"""
        return self.cycleDay.Query("DaoGuanDayChallengeNum", 0)

    def SetDaoGuanDayBuyChallengeNum(self, num):
        """今日购买挑战次数"""
        self.cycleDay.Set("DaoGuanDayBuyChallengeNum", num)

    def GetDaoGuanDayBuyChallengeNum(self):
        """今日购买挑战次数"""
        return self.cycleDay.Query("DaoGuanDayBuyChallengeNum", 0)

    def SetDaoGuanDaySweepList(self, data):
        """今日已扫荡列表"""
        self.cycleDay.Set("DaoGuanDaySweepList", data)

    def GetDaoGuanDaySweepList(self):
        """今日已扫荡列表"""
        return self.cycleDay.Query("DaoGuanDaySweepList", [])

    # 存库数据
    def to_save_dict(self, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            self.save_cache = {}
            self.save_cache["area"] = self.area
            self.save_cache["cycleDay"] = self.cycleDay.to_save_bytes()

            self.save_cache["pavilionData"] = []
            for obj in self.pavilionData.values():
                self.save_cache["pavilionData"].append(obj.to_save_dict())
        return self.save_cache

    #读库数据初始化
    def load_from_dict(self, data):
        self.area = data.get("area", 0)
        self.cycleDay.load_from_dict(data.get("cycleDay", ""))
        pavilionData = data.get("pavilionData", [])
        for oneData in pavilionData:
            did = oneData.get("id", 0)
            resPavilion = Game.res_mgr.res_pavilion.get(did)
            if not resPavilion:
                continue
            obj = DaoGuan(resPavilion, oneData, self)
            self.pavilionData[obj.id] = obj

    #登录初始化下发数据
    def to_init_data(self):
        init_data = {}
        init_data["area"] = self.area
        #打包给客户端是剩余次数
        init_data["dayChallengeNum"] = self.getHaveChallengeNum()
        init_data["dayBuyChallengeNum"] = self.GetDaoGuanDayBuyChallengeNum()
        init_data["daySweepList"] = self.GetDaoGuanDaySweepList()
        init_data["daoguanList"] = []
        for obj in self.pavilionData.values():
            init_data["daoguanList"].append(obj.to_init_data())
        return init_data

    #零点更新的数据
    def to_wee_hour_data(self):
        init_data = {}
        # 打包给客户端是剩余次数
        init_data["dayChallengeNum"] = self.getHaveChallengeNum()
        init_data["dayBuyChallengeNum"] = self.GetDaoGuanDayBuyChallengeNum()
        init_data["daySweepList"] = self.GetDaoGuanDaySweepList()
        return init_data

    def uninit(self):
        self.owner.unsub(msg_define.MSG_ROLE_XLV_UPGRADE, self.event_lv_uprade)

        for obj in self.pavilionData.values():
            obj.uninit()

    def event_lv_uprade(self):
        if 0==self.area:
            if self.owner.checkOpenLimit(constant.DAOGUAN_OPEN_ID):
                self.area = 1
                for resPavilion in Game.res_mgr.res_pavilion.values():
                    if resPavilion.area == self.area:
                        obj = DaoGuan(resPavilion, owner=self)
                        self.pavilionData[obj.id] = obj
                self.markDirty()

    def getPavilion(self, pavilionId):
        return self.pavilionData.get(pavilionId)

    def getHaveChallengeNum(self):
        """获取剩余挑战次数"""
        dRes = Game.res_mgr.res_common.get("daoguanChallengeNum")
        return (dRes.i + self.GetDaoGuanDayBuyChallengeNum()) - self.GetDaoGuanDayChallengeNum()

    def getArea(self):
        return self.area

    def setArea(self, area):
        self.area = area
        self.markDirty()

    def GetPassList(self):
        passList = []
        for resPavilion in Game.res_mgr.res_pavilion.values():
            if resPavilion.area < self.area:
                passList.append(resPavilion.id)
            elif resPavilion.area == self.area:
                obj = self.pavilionData.get(resPavilion.id)
                if obj and obj.firstFinish:
                    passList.append(resPavilion.id)
        return passList

    def enterNextArea(self):
        for obj in self.pavilionData.values():
            obj.uninit()
        self.pavilionData = {}
        self.area += 1
        for resPavilion in Game.res_mgr.res_pavilion.values():
            if resPavilion.area == self.area:
                obj = DaoGuan(resPavilion, owner=self)
                self.pavilionData[obj.id] = obj
        self.markDirty()

    def hasAllFinish(self):
        for pavilion in self.pavilionData.values():
            if not pavilion.firstFinish:
                return False
        return True

class DaoGuan(utility.DirtyFlag):
    def __init__(self, res, data=None, owner=None):
        utility.DirtyFlag.__init__(self)
        self.id = res.id
        self.taskData = {} #任务列表
        self.finishChallengeList = [] #已挑战副本列表
        self.firstFinish = 0 #是否已首通

        self.save_cache = {}  # 存储缓存

        if owner:
            self.set_owner(owner)

        if data:
            self.load_from_dict(data)
        else:
            self.init_task()

    def markDirty(self):
        utility.DirtyFlag.markDirty(self)
        if self.owner:
            self.owner.markDirty()

    def set_owner(self, owner):
        self.owner = owner

    def uninit(self):
        for obj in self.taskData.values():
            obj.uninit()

    def doFirstFinish(self):
        self.firstFinish = 1
        self.markDirty()

    # 存库数据
    def to_save_dict(self, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            self.save_cache = {}
            self.save_cache["id"] = self.id
            self.save_cache["finishChallengeList"] = self.finishChallengeList
            self.save_cache["firstFinish"] = self.firstFinish

            self.save_cache["taskData"] = []
            for obj in self.taskData.values():
                self.save_cache["taskData"].append(obj.to_save_dict())

        return self.save_cache

    # 读库数据初始化
    def load_from_dict(self, data):
        self.id = data.get("id", 0)
        self.finishChallengeList = data.get("finishChallengeList", [])  # 已挑战副本列表
        self.firstFinish = data.get("firstFinish", 0)  # 是否已首通

        # taskData = data.get("taskData", [])  # 任务列表
        # for oneData in taskData:
        #     taskId = oneData.get("taskId", 0)
        #     taskRes, taskobj = CreatTask(taskId, self, oneData)
        #     if not taskobj:
        #         continue
        #     self.taskData[taskId] = taskobj

    # 登录初始化下发数据
    def to_init_data(self):
        init_data = {}
        init_data["id"] = self.id
        init_data["taskInfo"] = [] #任务数据
        for obj in self.taskData.values():
            taskRes = Game.res_mgr.res_task.get(obj.taskId)
            if taskRes and obj.finish and obj.num != taskRes.num:
                obj.num = taskRes.num
                obj.markDirty()
            init_data["taskInfo"].append(obj.to_save_dict())
        init_data["finishChallengeList"] = self.finishChallengeList
        init_data["firstFinish"] = self.firstFinish

        return init_data

    def init_task(self):
        resPavilion = Game.res_mgr.res_pavilion.get(self.id)
        if not resPavilion:
            return
        # for taskId in resPavilion.unlockTask:
        #     data = {"taskId": taskId}
        #     taskRes, taskobj = CreatTask(taskId, self, data)
        #     if not taskobj:
        #         continue
        #     self.taskData[taskId] = taskobj

    def hasAllTaskFinish(self):
        for obj in self.taskData.values():
            if not obj.finish:
                return False
        return True

    def hasAllFinish(self):
        daoguanRes = Game.res_mgr.res_pavilion.get(self.id)
        if not daoguanRes:
            return False
        for barrId in daoguanRes.challengeList:
            if barrId not in self.finishChallengeList:
                return False
        return True

    def getFinishChallengeList(self):
        return self.finishChallengeList

    def setFinishChallengeList(self, ls):
        self.finishChallengeList = ls
        self.markDirty()


