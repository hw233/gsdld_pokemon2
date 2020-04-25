#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import time
import datetime
import config

from game.common import utility
from game.define import msg_define, constant

from corelib.frame import Game

# from game.mgr.task import CreatTask
from corelib import spawn
from game.core.cycleData import CycleDay, CycleWeek


#角色任务信息
class PlayerTask(utility.DirtyFlag):
    def __init__(self, owner):
        utility.DirtyFlag.__init__(self)
        self.owner = owner  # 拥有者
        self.maintask = None   #主线任务
        self.passMainId = 0 #已通关主线任务
        self.guild_act_tasks = {} #{任务id:obj}   #帮会活跃任务
        self.shitu_tasks = {} #{任务id:obj}   #师徒任务
        self.guild_act_reward_tasks = {} #{任务id:obj}   #帮会活跃奖励任务
        self.xyll_tasks = {} #{任务id:obj}   #西游历练任务
        self.rchy_tasks = {} #{任务id:obj}   #日常活跃任务
        self.zhoumolibaotasks = {} #{任务id:obj}   #周末礼包任务
        self.Renwudajihuantasks = {} #{任务id:obj}   #任务大集换
        self.RenwudajihuanIndex = {} #{index:taskid}   #任务大集换  index与任务id关系= "1","2","3","4","5",
        self.Renwudajihuan2tasks = {} #{任务id:obj}   #任务大集换
        self.Renwudajihuan2Index = {} #{index:taskid}   #任务大集换  index与任务id关系= "1","2","3","4","5",
        self.alreadyOpenTaskId = []  # 已开放的系统功能体验id
        self.open_tasks = {} #{任务id:obj}   #功能开放体验任务
        self.alreadyGetRewardOpenTaskId = []  # 已领取完成奖励的系统功能体验id
        self.alreadyGetOpenRewardOpenTaskId = []  # 已领取开启奖励的系统功能体验id
        self.activityMonster_tasks = {} #{任务id:obj}  神宠超梦活动前置任务
        self.thanksgivingDay_tasks = {} # {任务id:obj}  感恩节任务
        self.levelContest_tasks = {} # {任务id:obj}  段位赛任务
        self.maze_tasks = {} # {任务id:obj}  迷宫任务
        self.gongcheng_tasks = {} #{任务id:obj}  攻城任务
        self.zhuanpan_tasks = {} #{任务id:obj}  转盘任务
        self.new_kfkh_tasks = {}  # {任务id:obj}  新开服狂欢(和全民攻城一样的功能)


        self.passMainIdDict = {}

        self.cycleDay = CycleDay(self, keepCyc=2)
        self.cycleWeek = CycleWeek(self)

        self.save_cache = {} #存储缓存


    #帮会活跃任务
    def GetGuildActTask(self, taskId):
        guildActTasks = self.cycleDay.Query("guildActTasks", {})
        return guildActTasks.get(taskId, {})

    def SetGuildActTask(self, taskId, taskInfo):
        guildActTasks = self.cycleDay.Query("guildActTasks", {})
        guildActTasks[taskId] = taskInfo
        self.cycleDay.Set("guildActTasks", guildActTasks)

    #师徒任务
    def GetShituTask(self, taskId):
        shituTasks = self.cycleDay.Query("shituTasks", {})
        return shituTasks.get(taskId, {})

    def SetShituTask(self, taskId, taskInfo):
        shituTasks = self.cycleDay.Query("shituTasks", {})
        shituTasks[taskId] = taskInfo
        self.cycleDay.Set("shituTasks", shituTasks)

    #帮会活跃奖励
    def GetGuildActRewardTask(self, taskId):
        guildActRewardTasks = self.cycleDay.Query("guildActRewardTasks", {})
        return guildActRewardTasks.get(taskId, {})

    def SetGuildActRewardTask(self, taskId, taskInfo):
        guildActRewardTasks = self.cycleDay.Query("guildActRewardTasks", {})
        guildActRewardTasks[taskId] = taskInfo
        self.cycleDay.Set("guildActRewardTasks", guildActRewardTasks)

    #西游历练任务
    def GetXyllTask(self, taskId, iWhichCyc=0):
        xyllTasks = self.cycleDay.Query("xyllTasks", {}, iWhichCyc=iWhichCyc)
        return xyllTasks.get(taskId, {})

    def SetXyllTask(self, taskId, taskInfo, iWhichCyc=0):
        xyllTasks = self.cycleDay.Query("xyllTasks", {}, iWhichCyc=iWhichCyc)
        xyllTasks[taskId] = taskInfo
        self.cycleDay.Set("xyllTasks", xyllTasks, iWhichCyc=iWhichCyc)

    # 日常活跃任务
    def GetRchyTask(self, taskId):
        rchyTasks = self.cycleDay.Query("rchyTasks", {})
        return rchyTasks.get(taskId, {})

    def SetRchyTask(self, taskId, taskInfo):
        rchyTasks = self.cycleDay.Query("rchyTasks", {})
        rchyTasks[taskId] = taskInfo
        self.cycleDay.Set("rchyTasks", rchyTasks)

    def SetZhoumolibaoTask(self, taskId, taskInfo):
        zhoumolibaoTasks = self.cycleWeek.Query("zhoumolibaoTasks", {})
        zhoumolibaoTasks[taskId] = taskInfo
        self.cycleWeek.Set("zhoumolibaoTasks", zhoumolibaoTasks)

    def SetRenwudajihuanTask(self, taskId, taskInfo):
        RenwudajihuanTasks = self.cycleDay.Query("RenwudajihuanTasks", {})
        RenwudajihuanTasks[taskId] = taskInfo
        self.cycleDay.Set("RenwudajihuanTasks", RenwudajihuanTasks)

    def SetRenwudajihuan2Task(self, taskId, taskInfo):
        RenwudajihuanTasks = self.cycleDay.Query("Renwudajihuan2Tasks", {})
        RenwudajihuanTasks[taskId] = taskInfo
        self.cycleDay.Set("Renwudajihuan2Tasks", RenwudajihuanTasks)

    #日常活跃日奖励
    def GetRchyDayReward(self):
        return self.cycleDay.Query("rchyDayReward", [])

    def SetRchyDayReward(self, dayReward):
        self.cycleDay.Set("rchyDayReward", dayReward)

    #日常活跃日累计
    def GetRchyDayTotal(self):
        return self.cycleDay.Query("rchyDayTotal", 0)

    def SetRchyDayTotal(self, num):
        self.cycleDay.Set("rchyDayTotal", num)

    #日常活跃周奖励
    def GetRchyWeekReward(self):
        return self.cycleWeek.Query("rchyWeekReward", [])

    def SetRchyWeekReward(self, weekReward):
        self.cycleWeek.Set("rchyWeekReward", weekReward)

    #日常活跃周累计
    def GetRchyWeekTotal(self):
        return self.cycleWeek.Query("rchyWeekTotal", 0)

    def SetRchyWeekTotal(self, num):
        self.cycleWeek.Set("rchyWeekTotal", num)


    def markDirty(self):
        utility.DirtyFlag.markDirty(self)
        if self.owner:
            self.owner.markDirty()

    #存库数据
    def to_save_dict(self, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            self.save_cache = {}
            if self.maintask:
                self.save_cache["maintask"] = self.maintask.to_save_dict()
            self.save_cache["passMainId"] = self.passMainId
            self.save_cache["alreadyOpenTaskId"] = self.alreadyOpenTaskId
            self.save_cache["alreadyGetRewardOpenTaskId"] = self.alreadyGetRewardOpenTaskId
            self.save_cache["alreadyGetOpenRewardOpenTaskId"] = self.alreadyGetOpenRewardOpenTaskId
            self.save_cache["RenwudajihuanIndex"] = self.RenwudajihuanIndex
            self.save_cache["Renwudajihuan2Index"] = self.Renwudajihuan2Index
            self.save_cache["cycleDay"] = self.cycleDay.to_save_bytes()
            self.save_cache["cycleWeek"] = self.cycleWeek.to_save_bytes()

            self.save_cache["opentask"] = []
            for taskId, taskobj in self.open_tasks.items():
                self.save_cache["opentask"].append(taskobj.to_save_dict())

            self.save_cache["activityMonster_tasks"] = []
            for taskId, taskobj in self.activityMonster_tasks.items():
                self.save_cache["activityMonster_tasks"].append(taskobj.to_save_dict())

            self.save_cache["thanksgivingDay_tasks"] = []
            for taskId, taskobj in self.thanksgivingDay_tasks.items():
                self.save_cache["thanksgivingDay_tasks"].append(taskobj.to_save_dict())

            self.save_cache["gongcheng_tasks"] = []
            for taskId, taskobj in self.gongcheng_tasks.items():
                self.save_cache["gongcheng_tasks"].append(taskobj.to_save_dict())

            self.save_cache["special_pet_tasks"] = []
            for taskId, taskobj in self.special_pet_tasks.items():
                self.save_cache["special_pet_tasks"].append(taskobj.to_save_dict())

            self.save_cache["zhuanpan_tasks"] = []
            for taskId, taskobj in self.zhuanpan_tasks.items():
                self.save_cache["zhuanpan_tasks"].append(taskobj.to_save_dict())

            self.save_cache["new_kfkh_tasks"] = []
            for taskId, taskobj in self.new_kfkh_tasks.items():
                self.save_cache["new_kfkh_tasks"].append(taskobj.to_save_dict())

            self.save_cache["levelContest_tasks"] = []
            for taskId, taskobj in self.levelContest_tasks.items():
                self.save_cache["levelContest_tasks"].append(taskobj.to_save_dict())

            self.save_cache["maze_tasks"] = []
            for taskId, taskobj in self.maze_tasks.items():
                self.save_cache["maze_tasks"].append(taskobj.to_save_dict())

        return self.save_cache

    #读库数据初始化
    def load_from_dict(self, data):
        maintask = data.get("maintask", {})
        self.passMainId = data.get("passMainId", 0)
        self.alreadyOpenTaskId = data.get("alreadyOpenTaskId", [])  # 已开放的系统功能体验id
        self.alreadyGetRewardOpenTaskId = data.get("alreadyGetRewardOpenTaskId", []) # 已领取奖励的系统功能体验id
        self.alreadyGetOpenRewardOpenTaskId = data.get("alreadyGetOpenRewardOpenTaskId", [])  # 已领取开启奖励的系统功能体验id
        self.RenwudajihuanIndex = data.get("RenwudajihuanIndex", {})  # 已领取开启奖励的系统功能体验id
        self.Renwudajihuan2Index = data.get("Renwudajihuan2Index", {})  # 已领取开启奖励的系统功能体验id
        self.cycleDay.load_from_dict(data.get("cycleDay", ""))
        self.cycleWeek.load_from_dict(data.get("cycleWeek", ""))

        self.initMainTasks(maintask)
        self.initGuildActTasks()
        self.initShituTasks()
        self.initGuildActRewardTasks()
        self.initXyllTasks()
        self.initRchyTasks()
        # self.initZhoumolibaoTasks()
        self.initRenwudajihuanTasks()
        self.initRenwudajihuan2Tasks()
        open_task_data = data.get("opentask", [])
        self.initOpenTasks(open_task_data)
        activityMonster_tasks = data.get("activityMonster_tasks", [])  # {任务id:obj}  神宠超梦活动前置任务
        self.initActivityMonsterTasks(activityMonster_tasks)
        thanksgivingDay_tasks = data.get("thanksgivingDay_tasks", [])
        self.initThanksgivingDayTasks(thanksgivingDay_tasks)
        gongcheng_tasks = data.get("gongcheng_tasks", [])
        self.initGongchengTasks(gongcheng_tasks)
        special_pet_tasks = data.get("special_pet_tasks", [])
        self.initSpecPetTasks(special_pet_tasks)
        zhuanpan_tasks = data.get("zhuanpan_tasks", [])
        self.initZhuanpanTasks(zhuanpan_tasks)
        new_kfkh_tasks = data.get("new_kfkh_tasks", [])
        self.initNewKfkhTasks(new_kfkh_tasks)
        levelContest_tasks = data.get("levelContest_tasks", [])
        self.initLevelContestTasks(levelContest_tasks)
        maze_tasks = data.get("maze_tasks", [])
        self.initMazeTasks(maze_tasks)

    def initPassMainTaskList(self):
        iTaskId = 400001
        if self.passMainId:
            while iTaskId != self.passMainId:
                res = Game.res_mgr.res_task.get(iTaskId)
                if res:
                    self.passMainIdDict[iTaskId] = 1
                    iTaskId = res.nextId
                else:
                    break
            self.passMainIdDict[self.passMainId] = 1

    def AppendOpenTaskId(self, openTaskId):
        res = Game.res_mgr.res_openTask.get(openTaskId)
        if not res:
            return
        self.alreadyOpenTaskId.append(openTaskId)
        for taskId in res.taskList:
            taskInfo = {"taskId": taskId}
            taskRes, taskobj = CreatTask(taskId, self, taskInfo)
            if not taskobj:
                continue
            self.open_tasks[taskId] = taskobj
        self.markDirty()
        #推送更新数据
        dUpdate = {}
        dUpdate["taskInfo"] = self.to_init_data(all=1)
        spawn(self.owner.call, "roleAllUpdate", {"allUpdate": dUpdate}, noresult=True)

    def AppendActivityMonsterTaskId(self, activityMonsterId):
        res = Game.res_mgr.res_actMonster.get(activityMonsterId)
        if not res:
            return

        for taskId in res.taskList:
            if taskId in self.activityMonster_tasks:
                continue
            taskInfo = {"taskId": taskId}
            taskRes, taskobj = CreatTask(taskId, self, taskInfo)
            if not taskobj:
                continue
            self.activityMonster_tasks[taskId] = taskobj
        self.markDirty()
        # #推送更新数据
        # dUpdate = {}
        # dUpdate["taskInfo"] = self.to_init_data(all=1)
        # spawn(self.owner.call, "roleAllUpdate", {"allUpdate": dUpdate}, noresult=True)

    def AppendThanksgivingDayTaskId(self, thanksgivingDayId):
        res = Game.res_mgr.res_thanksgivingDayTask.get(thanksgivingDayId)
        if not res:
            return

        for taskId in res.taskList:
            if taskId in self.thanksgivingDay_tasks:
                continue
            taskInfo = {"taskId": taskId}
            taskRes, taskobj = CreatTask(taskId, self, taskInfo)
            if not taskobj:
                continue
            self.thanksgivingDay_tasks[taskId] = taskobj
        self.markDirty()

    def AppendGongchengTaskId(self, gongchengId):
        res = Game.res_mgr.res_gongchengTask.get(gongchengId)
        if not res:
            return

        for taskId in res.taskList:
            if taskId in self.gongcheng_tasks:
                continue
            taskInfo = {"taskId": taskId}
            taskRes, taskobj = CreatTask(taskId, self, taskInfo)
            if not taskobj:
                continue
            self.gongcheng_tasks[taskId] = taskobj
        self.markDirty()

    def AppendSpecPetTaskId(self, petSpecialTaskId):
        res = Game.res_mgr.res_petSpecialTask.get(petSpecialTaskId)
        if not res:
            return

        for taskId in res.taskList:
            if taskId in self.special_pet_tasks:
                continue
            taskInfo = {"taskId": taskId}
            taskRes, taskobj = CreatTask(taskId, self, taskInfo)
            if not taskobj:
                continue
            self.special_pet_tasks[taskId] = taskobj
        self.markDirty()

    def AppendZhuanpanTaskId(self, zhuanpanId):
        res = Game.res_mgr.res_cycleNiudan.get(zhuanpanId)
        if not res:
            return

        for taskId in res.taskList:
            if taskId in self.zhuanpan_tasks:
                continue
            taskInfo = {"taskId": taskId}
            taskRes, taskobj = CreatTask(taskId, self, taskInfo)
            if not taskobj:
                continue
            self.zhuanpan_tasks[taskId] = taskobj
        self.markDirty()

    def AppendNewKfkhTaskId(self, newKfkhId):
        res = Game.res_mgr.res_newKfkhTask.get(newKfkhId)
        if not res:
            return

        for taskId in res.taskList:
            if taskId in self.new_kfkh_tasks:
                continue
            taskInfo = {"taskId": taskId}
            taskRes, taskobj = CreatTask(taskId, self, taskInfo)
            if not taskobj:
                continue
            self.new_kfkh_tasks[taskId] = taskobj
        self.markDirty()

    def AppendLevelContestTasks(self):
        taskList = Game.res_mgr.res_group_task.get(constant.TASK_GROUP_12, [])

        for taskRes in taskList:
            taskId = taskRes.id
            if taskId in self.levelContest_tasks:
                continue
            taskInfo = {"taskId": taskId}
            taskRes, taskobj = CreatTask(taskId, self, taskInfo)
            if not taskobj:
                continue
            self.levelContest_tasks[taskId] = taskobj
        self.markDirty()

    def AppendMazeTasks(self, mazeNo):
        mazeRes = Game.res_mgr.res_maze.get(mazeNo)
        if not mazeRes:
            return

        for taskRes in mazeRes.taskList:
            taskId = taskRes.id
            if taskId in self.maze_tasks:
                continue
            taskInfo = {"taskId": taskId}
            taskRes, taskobj = CreatTask(taskId, self, taskInfo)
            if not taskobj:
                continue
            self.maze_tasks[taskId] = taskobj
        self.markDirty()

    def AppendMazeTaskById(self, taskId):
        taskInfo = {"taskId": taskId}
        taskRes, taskobj = CreatTask(taskId, self, taskInfo)
        if not taskobj:
            return
        self.maze_tasks[taskId] = taskobj
        self.markDirty()

    def checkOpenTask(self):
        for openId, openRes in Game.res_mgr.res_open.items():
            if openRes.openTaskId:
                self.owner.checkOpenLimit(openId)

    def GetPassMainTaskDict(self):
        return self.passMainIdDict

    def GetPassMainId(self):
        return self.passMainId

    def SetPassMainId(self, passId):
        self.passMainId = passId
        self.passMainIdDict[passId] = 1
        self.markDirty()

    def GetAlreadyGetRewardOpenTaskId(self):
        return self.alreadyGetRewardOpenTaskId

    def SetAlreadyGetRewardOpenTaskId(self, alreadyGetRewardOpenTaskId):
        self.alreadyGetRewardOpenTaskId = alreadyGetRewardOpenTaskId
        self.markDirty()

    def GetAlreadyGetOpenRewardOpenTaskId(self):
        return self.alreadyGetOpenRewardOpenTaskId

    def SetAlreadyGetOpenRewardOpenTaskId(self, alreadyGetOpenRewardOpenTaskId):
        self.alreadyGetOpenRewardOpenTaskId = alreadyGetOpenRewardOpenTaskId
        self.markDirty()

    #登录初始化下发数据
    def to_init_data(self, all=0):
        resp = {}
        resp["mainTask"] = self.maintask.to_save_dict()
        if all:
            resp["alreadyOpenTaskId"] = self.alreadyOpenTaskId
            resp["alreadyGetRewardOpenTaskId"] = self.alreadyGetRewardOpenTaskId
            resp["alreadyGetOpenRewardOpenTaskId"] = self.alreadyGetOpenRewardOpenTaskId
            resp["openTaskData"] = self.to_OpenTasks_data()
            resp["activityMonsterTaskData"] = self.to_activityMonsterTasks_data()
            resp["zhoumolibaoTaskData"] = self.to_ZhoumolibaoTasks_data()
            resp["RenwudajihuanTaskData"] = self.to_RenwudajihuanTasks_data()
            resp["Renwudajihuan2TaskData"] = self.to_Renwudajihuan2Tasks_data()
            resp["thanksgivingDayTaskData"] = self.to_thanksgivingDayTasks_data()
            resp["levelContestTaskData"] = self.to_LevelContestTasks_data()
            resp["mazeTaskData"] = self.to_MazeTasks_data()
            resp["gongchengTaskData"] = self.to_gongchengTasks_data()
            resp["zhuanpanTaskData"] = self.to_zhuanpanTasks_data()
            resp["specPetTaskData"] = self.to_specPetTasks_data()

        
            resp["RenwudajihuanIndex"] = self.RenwudajihuanIndex
            resp["Renwudajihuan2Index"] = self.Renwudajihuan2Index
        
        return resp

    def to_wee_hour_data(self):
        return self.to_init_data(all=1)

    def cleanOpenTask(self, openTaskId):
        openTaskRes = Game.res_mgr.res_openTask.get(openTaskId)
        if not openTaskRes:
            return
        #所有任务必须完成才可领取
        for taskId in openTaskRes.taskList:
            taskobj = self.open_tasks.pop(taskId, None)
            if taskobj:
                taskobj.uninit()

    def cleanActivityMonsterTask(self, activityMonsterId):
        res = Game.res_mgr.res_actMonster.get(activityMonsterId)
        if not res:
            return
        for taskId in res.taskList:
            taskobj = self.activityMonster_tasks.pop(taskId, None)
            if taskobj:
                taskobj.uninit()

    def cleanThanksgivingDayTask(self):
        for taskId, taskobj in self.thanksgivingDay_tasks.items():
            taskobj.uninit()
        self.thanksgivingDay_tasks = {}
        self.markDirty()

    def cleanThanksgivingDayTaskById(self, thanksgivingDayId):
        res = Game.res_mgr.res_thanksgivingDayTask.get(thanksgivingDayId)
        if not res:
            return
        for taskId in res.taskList:
            taskobj = self.thanksgivingDay_tasks.pop(taskId, None)
            if taskobj:
                taskobj.uninit()

    def cleanGongchengTask(self):
        for taskId, taskobj in self.gongcheng_tasks.items():
            taskobj.uninit()
        self.gongcheng_tasks = {}
        self.markDirty()

    def cleanSpecPetTask(self):
        for taskId, taskobj in self.special_pet_tasks.items():
            taskobj.uninit()
        self.special_pet_tasks = {}
        self.markDirty()

    def cleanZhuanpanTask(self):
        for taskId, taskobj in self.zhuanpan_tasks.items():
            taskobj.uninit()
        self.zhuanpan_tasks = {}
        self.markDirty()

    def cleanGongchengById(self, gongchengId):
        res = Game.res_mgr.res_gongchengTask.get(gongchengId)
        if not res:
            return
        for taskId in res.taskList:
            taskobj = self.gongcheng_tasks.pop(taskId, None)
            if taskobj:
                taskobj.uninit()

    def cleanSpecPetById(self, petSpecialTaskId):
        res = Game.res_mgr.res_petSpecialTask.get(petSpecialTaskId)
        if not res:
            return
        for taskId in res.taskList:
            taskobj = self.special_pet_tasks.pop(taskId, None)
            if taskobj:
                taskobj.uninit()

    def cleanZhuanpanById(self, zhuanpanId):
        res = Game.res_mgr.res_cycleNiudan.get(zhuanpanId)
        if not res:
            return
        for taskId in res.taskList:
            taskobj = self.zhuanpan_tasks.pop(taskId, None)
            if taskobj:
                taskobj.uninit()

    def cleanNewKfhkTask(self):
        for taskId, taskobj in self.new_kfkh_tasks.items():
            taskobj.uninit()
        self.new_kfkh_tasks = {}
        self.markDirty()

    def cleanNewKfkhById(self, newKfkhId):
        res = Game.res_mgr.res_newKfkhTask.get(newKfkhId)
        if not res:
            return
        for taskId in res.taskList:
            taskobj = self.new_kfkh_tasks.pop(taskId, None)
            if taskobj:
                taskobj.uninit()

    def cleanLevelContestTask(self):
        for taskId, taskobj in self.levelContest_tasks.items():
            taskobj.uninit()
        self.levelContest_tasks = {}
        self.markDirty()

    def cleanAllMazeTask(self):
        for taskId, taskobj in self.maze_tasks.items():
            taskobj.uninit()
        self.maze_tasks = {}
        self.markDirty()

    def cleanMazeTaskById(self, taskId):
        taskobj = self.maze_tasks.pop(taskId, None)
        if taskobj:
            taskobj.uninit()
            self.markDirty()

    def uninit(self):
        if self.maintask:
            self.maintask.uninit()
        for taskId, taskobj in self.shitu_tasks.items():
            taskobj.uninit()
        for taskId, taskobj in self.guild_act_tasks.items():
            taskobj.uninit()
        for taskId, taskobj in self.guild_act_reward_tasks.items():
            taskobj.uninit()
        for taskId, taskobj in self.xyll_tasks.items():
            taskobj.uninit()
        for taskId, taskobj in self.rchy_tasks.items():
            taskobj.uninit()
        for taskId, taskobj in self.zhoumolibaotasks.items():
            taskobj.uninit()
        for taskId, taskobj in self.Renwudajihuantasks.items():
            taskobj.uninit()
        for taskId, taskobj in self.Renwudajihuan2tasks.items():
            taskobj.uninit()
        for taskId, taskobj in self.open_tasks.items():
            taskobj.uninit()
        for taskId, taskobj in self.activityMonster_tasks.items():
            taskobj.uninit()
        for taskId, taskobj in self.thanksgivingDay_tasks.items():
            taskobj.uninit()
        for taskId, taskobj in self.levelContest_tasks.items():
            taskobj.uninit()
        for taskId, taskobj in self.maze_tasks.items():
            taskobj.uninit()
        for taskId, taskobj in self.gongcheng_tasks.items():
            taskobj.uninit()
        for taskId, taskobj in self.special_pet_tasks.items():
            taskobj.uninit()
        for taskId, taskobj in self.zhuanpan_tasks.items():
            taskobj.uninit()

    def initMainTasks(self, maintask):
        #主线任务
        if not maintask:
            maintask = {"taskId":400001}
            self.markDirty()
        taskId = maintask.get("taskId", 0)
        taskRes, taskobj = CreatTask(taskId, self, maintask)
        if not taskobj:
            return
        self.maintask = taskobj

    def checkNextMainTask(self):
        if not self.maintask:
            return
        mainId = self.maintask.getTaskId()
        taskRes = Game.res_mgr.res_task.get(mainId)
        if not taskRes:
            return
        nextRes = Game.res_mgr.res_task.get(taskRes.nextId)
        if not nextRes:
            return

        if mainId == self.passMainId:
            maintask = {"taskId":nextRes.id}
            _, taskobj = CreatTask(nextRes.id, self, maintask, no_happen=True)
            if taskobj:
                self.maintask = taskobj
                self.markDirty()

        if taskRes.type == constant.TASK_TYPE_36:
            self.maintask.num = taskRes.num
            self.maintask.finish = 1
            self.maintask.markDirty()

    def initGuildActTasks(self):
        # 帮会活跃任务
        guild_act_tasks = self.cycleDay.Query("guildActTasks", {})
        if not guild_act_tasks: #隔天从新初始化
            resTasks = Game.res_mgr.res_group_task.get(constant.TASK_GROUP_1, [])
            for res in resTasks:
                guild_act_tasks[res.id] = {"taskId": res.id}
            self.cycleDay.Set("guildActTasks", guild_act_tasks)
        if self.owner.guild.GetGuildId():
            for taskId, taskobj in self.guild_act_tasks.items():
                taskobj.uninit()
            for taskId, taskInfo in guild_act_tasks.items():
                taskRes, taskobj = CreatTask(taskId, self, taskInfo)
                if not taskobj:
                    continue
                self.guild_act_tasks[taskId] = taskobj

    def to_GuildActTasks_data(self):
        guild_act_tasks = self.cycleDay.Query("guildActTasks", {})
        if not guild_act_tasks:  # 隔天从新初始化
            self.initGuildActTasks()
        resp = []
        for taskId, taskobj in self.guild_act_tasks.items():
            one = taskobj.to_save_dict()
            resp.append(one)
        return resp

    def uninitShituTasks(self):
        for taskId, taskobj in self.shitu_tasks.items():
            taskobj.reset()
            taskobj.uninit()
            
    def initShituTasks(self):
        # 师徒任务
        shitu_tasks = self.cycleDay.Query("shituTasks", {})
        if not shitu_tasks: #隔天从新初始化
            resTasks = Game.res_mgr.res_group_task.get(constant.TASK_GROUP_5, [])
            for res in resTasks:
                shitu_tasks[res.id] = {"taskId": res.id}
            self.cycleDay.Set("shituTasks", shitu_tasks)
        if self.owner.shitu.id:
            for taskId, taskInfo in shitu_tasks.items():
                taskRes, taskobj = CreatTask(taskId, self, taskInfo)
                if not taskobj:
                    continue
                self.shitu_tasks[taskId] = taskobj

    def to_ShituTasks_data(self):
        shitu_tasks = self.cycleDay.Query("shituTasks", {})
        if not shitu_tasks:  # 隔天从新初始化
            self.initShituTasks()
        resp = []
        for taskId, taskobj in self.shitu_tasks.items():
            one = taskobj.to_save_dict()
            resp.append(one)
        return resp

    def initGuildActRewardTasks(self):
        # 帮会活跃奖励
        guild_act_reward_tasks = self.cycleDay.Query("guildActRewardTasks", {})
        if not guild_act_reward_tasks: #隔天从新初始化
            resTasks = Game.res_mgr.res_group_task.get(constant.TASK_GROUP_2, [])
            for res in resTasks:
                guild_act_reward_tasks[res.id] = {"taskId": res.id}
            self.cycleDay.Set("guildActRewardTasks", guild_act_reward_tasks)
        if self.owner.guild.GetGuildId():
            for taskId, taskobj in self.guild_act_reward_tasks.items():
                taskobj.uninit()
            for taskId, taskInfo in guild_act_reward_tasks.items():
                taskRes, taskobj = CreatTask(taskId, self, taskInfo)
                if not taskobj:
                    continue
                self.guild_act_reward_tasks[taskId] = taskobj

    def to_GuildActRewardTasks_data(self):
        guild_act_reward_tasks = self.cycleDay.Query("guildActRewardTasks", {})
        if not guild_act_reward_tasks:  # 隔天从新初始化
            self.initGuildActRewardTasks()
        resp = []
        for taskId, taskobj in self.guild_act_reward_tasks.items():
            one = taskobj.to_save_dict()
            resp.append(one)
        return resp

    def initXyllTasks(self):
        # 西游历练任务
        xyll_tasks = self.cycleDay.Query("xyllTasks", {})
        if not xyll_tasks: #隔天从新初始化
            resTasks = Game.res_mgr.res_group_task.get(constant.TASK_GROUP_3, [])
            for res in resTasks:
                xyll_tasks[res.id] = {"taskId": res.id}
            self.cycleDay.Set("xyllTasks", xyll_tasks)
        for taskId, taskInfo in xyll_tasks.items():
            taskRes, taskobj = CreatTask(taskId, self, taskInfo)
            if not taskobj:
                continue
            self.xyll_tasks[taskId] = taskobj

    def to_XyllTasks_data(self):
        xyll_tasks = self.cycleDay.Query("xyllTasks", {})
        if not xyll_tasks:  # 隔天从新初始化
            self.initXyllTasks()
        resp = []
        for taskId, taskobj in self.xyll_tasks.items():
            one = taskobj.to_save_dict()
            resp.append(one)
        return resp

    def to_XyllTasks_find_data(self):
        """西游历练找回"""
        resp = {}
        xyllTasks = self.cycleDay.Query("xyllTasks", {}, iWhichCyc=-1)
        if not xyllTasks: #初始化
            resTasks = Game.res_mgr.res_group_task.get(constant.TASK_GROUP_3, [])
            for res in resTasks:
                xyllTasks[res.id] = {"taskId": res.id}
            self.cycleDay.Set("xyllTasks", xyllTasks, iWhichCyc=-1)

        for taskId, taskInfo in xyllTasks.items():
            if taskInfo.get("find", 0) or taskInfo.get("finish", 0):
                continue
            resp[taskId] = taskInfo
        return resp

    def initRchyTasks(self):
        # 日常活跃任务
        rchy_tasks = self.cycleDay.Query("rchyTasks", {})
        if not rchy_tasks:  # 隔天从新初始化
            resTasks = Game.res_mgr.res_group_task.get(constant.TASK_GROUP_7, [])
            for res in resTasks:
                rchy_tasks[res.id] = {"taskId": res.id}
            self.cycleDay.Set("rchyTasks", rchy_tasks)
        for taskId, taskInfo in rchy_tasks.items():
            taskRes, taskobj = CreatTask(taskId, self, taskInfo)
            if not taskobj:
                continue
            self.rchy_tasks[taskId] = taskobj

    def to_RchyTasks_data(self):
        rchy_tasks = self.cycleDay.Query("rchyTasks", {})
        if not rchy_tasks:  # 隔天从新初始化
            self.initRchyTasks()
        resp = []
        for taskId, taskobj in self.rchy_tasks.items():
            one = taskobj.to_save_dict()
            resp.append(one)
        return resp

    def uninitZhoumolibaoTasks(self):
        # 周末活动
        for taskId, taskobj in self.zhoumolibaotasks.items():
            taskobj.uninit()

    def initZhoumolibaoTasks(self):
        # 周末活动
        zhoumolibaotasks = self.cycleWeek.Query("zhoumolibaoTasks", {})
        
        if not zhoumolibaotasks:  # 隔周从新初始化
            resTasks = Game.res_mgr.res_group_task.get(constant.TASK_GROUP_11, [])
            for res in resTasks:
                zhoumolibaotasks[res.id] = {"taskId": res.id}
            self.cycleWeek.Set("zhoumolibaoTasks", zhoumolibaotasks)
        
        for taskId, taskInfo in zhoumolibaotasks.items():
            taskRes, taskobj = CreatTask(taskId, self, taskInfo)
            if not taskobj:
                continue
            self.zhoumolibaotasks[taskId] = taskobj

    def to_ZhoumolibaoTasks_data(self):
        zhoumolibaotasks = self.cycleWeek.Query("zhoumolibaoTasks", {})
        
        if not zhoumolibaotasks:  # 隔周从新初始化
            resTasks = Game.res_mgr.res_group_task.get(constant.TASK_GROUP_11, [])
            for res in resTasks:
                zhoumolibaotasks[res.id] = {"taskId": res.id}
            self.cycleWeek.Set("zhoumolibaoTasks", zhoumolibaotasks)

        resp = []
        for taskId, taskobj in self.zhoumolibaotasks.items():
            one = taskobj.to_save_dict()
            resp.append(one)
        return resp

    def uninitRenwudajihuanTasks(self):
        for taskId, taskobj in self.Renwudajihuantasks.items():
            taskobj.uninit()
 
    def uninitRenwudajihuan2Tasks(self):
        for taskId, taskobj in self.Renwudajihuan2tasks.items():
            taskobj.uninit()
 
    def initRenwudajihuanTasks(self):
        Renwudajihuantasks = self.cycleDay.Query("RenwudajihuanTasks", {})
        
        today=str(datetime.date.today())
        
        resRenwu = Game.res_mgr.res_renwudajihuan.get(today)

        if not Renwudajihuantasks and resRenwu:

            while True:
                rid=utility.Choice(resRenwu.task1)
                if rid not in Renwudajihuantasks:
                    res = Game.res_mgr.res_task.get(rid, None)
                    Renwudajihuantasks[res.id] = {"taskId": res.id}
                    self.cycleDay.Set("RenwudajihuanTasks", Renwudajihuantasks)
                    self.RenwudajihuanIndex["1"]=res.id
                    break
            while True:
                rid=utility.Choice(resRenwu.task2)
                if rid not in Renwudajihuantasks:
                    res = Game.res_mgr.res_task.get(rid, None)
                    Renwudajihuantasks[res.id] = {"taskId": res.id}
                    self.cycleDay.Set("RenwudajihuanTasks", Renwudajihuantasks)
                    self.RenwudajihuanIndex["2"]=res.id
                    break
            while True:
                rid=utility.Choice(resRenwu.task3)
                if rid not in Renwudajihuantasks:
                    res = Game.res_mgr.res_task.get(rid, None)
                    Renwudajihuantasks[res.id] = {"taskId": res.id}
                    self.cycleDay.Set("RenwudajihuanTasks", Renwudajihuantasks)
                    self.RenwudajihuanIndex["3"]=res.id
                    break
            while True:
                rid=utility.Choice(resRenwu.task4)
                if rid not in Renwudajihuantasks:
                    res = Game.res_mgr.res_task.get(rid, None)
                    Renwudajihuantasks[res.id] = {"taskId": res.id}
                    self.cycleDay.Set("RenwudajihuanTasks", Renwudajihuantasks)
                    self.RenwudajihuanIndex["4"]=res.id
                    break
            while True:
                rid=utility.Choice(resRenwu.task5)
                if rid not in Renwudajihuantasks:
                    res = Game.res_mgr.res_task.get(rid, None)
                    Renwudajihuantasks[res.id] = {"taskId": res.id}
                    self.cycleDay.Set("RenwudajihuanTasks", Renwudajihuantasks)
                    self.RenwudajihuanIndex["5"]=res.id
                    break
            self.markDirty()
            
            

        
        for taskId, taskInfo in Renwudajihuantasks.items():
            taskRes, taskobj = CreatTask(taskId, self, taskInfo)
            if not taskobj:
                continue
            self.Renwudajihuantasks[taskId] = taskobj

    def initRenwudajihuan2Tasks(self):
        Renwudajihuantasks = self.cycleDay.Query("Renwudajihuan2Tasks", {})
        
        today=str(datetime.date.today())
        
        resRenwu = Game.res_mgr.res_renwudajihuan2.get(today)

        if not Renwudajihuantasks and resRenwu:

            while True:
                rid=utility.Choice(resRenwu.task1)
                if rid not in Renwudajihuantasks:
                    res = Game.res_mgr.res_task.get(rid, None)
                    Renwudajihuantasks[res.id] = {"taskId": res.id}
                    self.cycleDay.Set("Renwudajihuan2Tasks", Renwudajihuantasks)
                    self.Renwudajihuan2Index["1"]=res.id
                    break
            while True:
                rid=utility.Choice(resRenwu.task2)
                if rid not in Renwudajihuantasks:
                    res = Game.res_mgr.res_task.get(rid, None)
                    Renwudajihuantasks[res.id] = {"taskId": res.id}
                    self.cycleDay.Set("Renwudajihuan2Tasks", Renwudajihuantasks)
                    self.Renwudajihuan2Index["2"]=res.id
                    break
            while True:
                rid=utility.Choice(resRenwu.task3)
                if rid not in Renwudajihuantasks:
                    res = Game.res_mgr.res_task.get(rid, None)
                    Renwudajihuantasks[res.id] = {"taskId": res.id}
                    self.cycleDay.Set("Renwudajihuan2Tasks", Renwudajihuantasks)
                    self.Renwudajihuan2Index["3"]=res.id
                    break
            while True:
                rid=utility.Choice(resRenwu.task4)
                if rid not in Renwudajihuantasks:
                    res = Game.res_mgr.res_task.get(rid, None)
                    Renwudajihuantasks[res.id] = {"taskId": res.id}
                    self.cycleDay.Set("Renwudajihuan2Tasks", Renwudajihuantasks)
                    self.Renwudajihuan2Index["4"]=res.id
                    break
            while True:
                rid=utility.Choice(resRenwu.task5)
                if rid not in Renwudajihuantasks:
                    res = Game.res_mgr.res_task.get(rid, None)
                    Renwudajihuantasks[res.id] = {"taskId": res.id}
                    self.cycleDay.Set("Renwudajihuan2Tasks", Renwudajihuantasks)
                    self.Renwudajihuan2Index["5"]=res.id
                    break
            self.markDirty()
            
            

        
        for taskId, taskInfo in Renwudajihuantasks.items():
            taskRes, taskobj = CreatTask(taskId, self, taskInfo)
            if not taskobj:
                continue
            self.Renwudajihuan2tasks[taskId] = taskobj

    def to_RenwudajihuanTasks_data(self):
        Renwudajihuantasks = self.cycleDay.Query("RenwudajihuanTasks", {})
   
        today=str(datetime.date.today())
        
        resRenwu = Game.res_mgr.res_renwudajihuan.get(today)

        if not Renwudajihuantasks and resRenwu:

            while True:
                rid=utility.Choice(resRenwu.task1)
                if rid not in Renwudajihuantasks:
                    res = Game.res_mgr.res_task.get(rid, None)
                    Renwudajihuantasks[res.id] = {"taskId": res.id}
                    self.cycleDay.Set("RenwudajihuanTasks", Renwudajihuantasks)
                    self.RenwudajihuanIndex["1"]=res.id
                    break
            while True:
                rid=utility.Choice(resRenwu.task)
                if rid not in Renwudajihuantasks:
                    res = Game.res_mgr.res_task.get(rid, None)
                    Renwudajihuantasks[res.id] = {"taskId": res.id}
                    self.cycleDay.Set("RenwudajihuanTasks", Renwudajihuantasks)
                    self.Renwudajihuan2Index["2"]=res.id
                    break
            while True:
                rid=utility.Choice(resRenwu.task3)
                if rid not in Renwudajihuantasks:
                    res = Game.res_mgr.res_task.get(rid, None)
                    Renwudajihuantasks[res.id] = {"taskId": res.id}
                    self.cycleDay.Set("RenwudajihuanTasks", Renwudajihuantasks)
                    self.RenwudajihuanIndex["3"]=res.id
                    break
            while True:
                rid=utility.Choice(resRenwu.task4)
                if rid not in Renwudajihuantasks:
                    res = Game.res_mgr.res_task.get(rid, None)
                    Renwudajihuantasks[res.id] = {"taskId": res.id}
                    self.cycleDay.Set("RenwudajihuanTasks", Renwudajihuantasks)
                    self.RenwudajihuanIndex["4"]=res.id
                    break
            while True:
                rid=utility.Choice(resRenwu.task5)
                if rid not in Renwudajihuantasks:
                    res = Game.res_mgr.res_task.get(rid, None)
                    Renwudajihuantasks[res.id] = {"taskId": res.id}
                    self.cycleDay.Set("RenwudajihuanTasks", Renwudajihuantasks)
                    self.RenwudajihuanIndex["5"]=res.id
                    break
            self.markDirty()

        resp = []
        for taskId, taskobj in self.Renwudajihuantasks.items():
            one = taskobj.to_save_dict()
            resp.append(one)
        return resp

    def to_Renwudajihuan2Tasks_data(self):
        Renwudajihuantasks = self.cycleDay.Query("Renwudajihuan2Tasks", {})
   
        today=str(datetime.date.today())
        
        resRenwu = Game.res_mgr.res_renwudajihuan2.get(today)

        if not Renwudajihuantasks and resRenwu:

            while True:
                rid=utility.Choice(resRenwu.task1)
                if rid not in Renwudajihuantasks:
                    res = Game.res_mgr.res_task.get(rid, None)
                    Renwudajihuantasks[res.id] = {"taskId": res.id}
                    self.cycleDay.Set("Renwudajihuan2Tasks", Renwudajihuantasks)
                    self.Renwudajihuan2Index["1"]=res.id
                    break
            while True:
                rid=utility.Choice(resRenwu.task2)
                if rid not in Renwudajihuantasks:
                    res = Game.res_mgr.res_task.get(rid, None)
                    Renwudajihuantasks[res.id] = {"taskId": res.id}
                    self.cycleDay.Set("Renwudajihuan2Tasks", Renwudajihuantasks)
                    self.Renwudajihuan2Index["2"]=res.id
                    break
            while True:
                rid=utility.Choice(resRenwu.task3)
                if rid not in Renwudajihuantasks:
                    res = Game.res_mgr.res_task.get(rid, None)
                    Renwudajihuantasks[res.id] = {"taskId": res.id}
                    self.cycleDay.Set("Renwudajihuan2Tasks", Renwudajihuantasks)
                    self.Renwudajihuan2Index["3"]=res.id
                    break
            while True:
                rid=utility.Choice(resRenwu.task4)
                if rid not in Renwudajihuantasks:
                    res = Game.res_mgr.res_task.get(rid, None)
                    Renwudajihuantasks[res.id] = {"taskId": res.id}
                    self.cycleDay.Set("Renwudajihuan2Tasks", Renwudajihuantasks)
                    self.Renwudajihuan2Index["4"]=res.id
                    break
            while True:
                rid=utility.Choice(resRenwu.task5)
                if rid not in Renwudajihuantasks:
                    res = Game.res_mgr.res_task.get(rid, None)
                    Renwudajihuantasks[res.id] = {"taskId": res.id}
                    self.cycleDay.Set("Renwudajihuan2Tasks", Renwudajihuantasks)
                    self.Renwudajihuan2Index["5"]=res.id
                    break
            self.markDirty()

        resp = []
        for taskId, taskobj in self.Renwudajihuan2tasks.items():
            one = taskobj.to_save_dict()
            resp.append(one)
        return resp

    def addRchyExp(self, num):
        rchyDayExp = self.GetRchyDayTotal()
        rchyDayExp += num
        self.SetRchyDayTotal(rchyDayExp)

        rchyWeekExp = self.GetRchyWeekTotal()
        rchyWeekExp += num
        self.SetRchyWeekTotal(rchyWeekExp)

        self.owner.safe_pub(msg_define.MSG_RCHY_CHANGE, num)

        spawn(self.owner.call, "PushRchy", {"dayExp":rchyDayExp, "weekExp":rchyWeekExp}, noresult=True)

    def initOpenTasks(self, open_task_data):
        # 功能开放体验任务
        for taskInfo in open_task_data:
            taskId = taskInfo.get("taskId", 0)
            taskRes, taskobj = CreatTask(taskId, self, taskInfo)
            if not taskobj:
                continue
            self.open_tasks[taskId] = taskobj

    def to_OpenTasks_data(self):
        resp = []
        for taskId, taskobj in self.open_tasks.items():
            one = taskobj.to_save_dict()
            resp.append(one)
        return resp


    def initActivityMonsterTasks(self, activityMonster_tasks):
        # 神宠超梦活动前置任务
        for taskInfo in activityMonster_tasks:
            taskId = taskInfo.get("taskId", 0)
            taskRes, taskobj = CreatTask(taskId, self, taskInfo)
            if not taskobj:
                continue
            self.activityMonster_tasks[taskId] = taskobj


    def to_activityMonsterTasks_data(self):
        resp = []
        for taskId, taskobj in self.activityMonster_tasks.items():
            one = taskobj.to_save_dict()
            resp.append(one)
        return resp


    def initThanksgivingDayTasks(self, thanksgivingDay_tasks):
        # 感恩节任务
        for taskInfo in thanksgivingDay_tasks:
            taskId = taskInfo.get("taskId", 0)
            taskRes, taskobj = CreatTask(taskId, self, taskInfo)
            if not taskobj:
                continue
            self.thanksgivingDay_tasks[taskId] = taskobj

    def to_thanksgivingDayTasks_data(self):
        resp = []
        for taskId, taskobj in self.thanksgivingDay_tasks.items():
            one = taskobj.to_save_dict()
            resp.append(one)
        return resp

    def initGongchengTasks(self, gongcheng_tasks):
        # 全民攻城任务
        for taskInfo in gongcheng_tasks:
            taskId = taskInfo.get("taskId", 0)
            taskRes, taskobj = CreatTask(taskId, self, taskInfo)
            if not taskobj:
                continue
            self.gongcheng_tasks[taskId] = taskobj

    def to_gongchengTasks_data(self):
        resp = []
        for taskId, taskobj in self.gongcheng_tasks.items():
            one = taskobj.to_save_dict()
            resp.append(one)
        return resp



    def to_specPetTasks_data(self):
        resp = []
        for taskId, taskobj in self.special_pet_tasks.items():
            one = taskobj.to_save_dict()
            resp.append(one)
        return resp

    def initZhuanpanTasks(self, zhuanpan_tasks):
        # 转盘任务
        for taskInfo in zhuanpan_tasks:
            taskId = taskInfo.get("taskId", 0)
            taskRes, taskobj = CreatTask(taskId, self, taskInfo)
            if not taskobj:
                continue
            self.zhuanpan_tasks[taskId] = taskobj

    def to_zhuanpanTasks_data(self):
        resp = []
        for taskId, taskobj in self.zhuanpan_tasks.items():
            one = taskobj.to_save_dict()
            resp.append(one)
        return resp

    def initNewKfkhTasks(self, new_kfkh_tasks):
        #新开服狂欢(和全民攻城一样的功能)
        for taskInfo in new_kfkh_tasks:
            taskId = taskInfo.get("taskId", 0)
            taskRes, taskobj = CreatTask(taskId, self, taskInfo)
            if not taskobj:
                continue
            self.new_kfkh_tasks[taskId] = taskobj

    def to_newKfkhTasks_data(self):
        resp = []
        for taskId, taskobj in self.new_kfkh_tasks.items():
            one = taskobj.to_save_dict()
            resp.append(one)
        return resp

    def initLevelContestTasks(self, levelContest_tasks):
        # 段位赛任务
        for taskInfo in levelContest_tasks:
            taskId = taskInfo.get("taskId", 0)
            taskRes, taskobj = CreatTask(taskId, self, taskInfo)
            if not taskobj:
                continue
            self.levelContest_tasks[taskId] = taskobj


    def to_LevelContestTasks_data(self):
        resp = []
        for taskId, taskobj in self.levelContest_tasks.items():
            one = taskobj.to_save_dict()
            resp.append(one)
        return resp


    def initMazeTasks(self, maze_tasks):
        # 迷宫任务
        for taskInfo in maze_tasks:
            taskId = taskInfo.get("taskId", 0)
            taskRes, taskobj = CreatTask(taskId, self, taskInfo)
            if not taskobj:
                continue
            self.maze_tasks[taskId] = taskobj


    def to_MazeTasks_data(self):
        resp = []
        for taskId, taskobj in self.maze_tasks.items():
            one = taskobj.to_save_dict()
            resp.append(one)
        return resp
