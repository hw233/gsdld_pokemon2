#!/usr/bin/env python
# -*- coding:utf-8 -*-

import time

from game.common import utility
from game.define import msg_define, switch_define

from corelib.frame import Game
from corelib.gtime import cur_day_hour_time, current_hour
from corelib import spawn

from game.core.cycleData import CycleDay

#角色公会信息
class PlayerGuild(utility.DirtyFlag):
    def __init__(self, owner):
        utility.DirtyFlag.__init__(self)

        self.cycleDay = CycleDay(self)

        self.owner = owner  # 拥有者
        self.guildId = 0 #公会id
        self.actLv = 0 #帮会活跃等级(actLv, int)
        self.actExp = 0 # 帮会活跃经验(actExp, int)
        self.skills = {}  # {pos:lv} 帮会技能列表(skill, [json]) 部位(pos, int) 等级(lv, int)
        self.exList = [] #[(exId, status)] 兑换id(exId, int) 状态(status, int) 0=未兑换 1=已兑换
        self.refTime = 0 #兑换下次刷新时间戳(refTime, int) #从0点开始每4小时刷新一下
        self.firstKill = [] #帮会副本已首通id列表

        self.monsterNum = 0 #帮会小怪击杀总次数
        self.collectNum = 0 #帮会采集总次数
        self.shangxiangNum = 0 #帮会上香总次数
        self.barrNum = 0 #历史帮会副本挑战总次数
        self.skillUpNum = 0 #帮会技能历史提升次数
        self.actRewardNum = 0 #领取公会活跃奖励次数

        self.save_cache = {} #存储缓存

    # 	场景任务(taskList, [json])
    # 		任务表id(taskId, int)
    # 		当前进度(num, int)
    # 		是否已领取(status, int)
    # 			0=未领取 1=已领取
    # 		当前已刷新次数(refeNum, int)
    def getSceneTaskInfo(self):
        taskList = []
        if not self.guildId:
            return taskList
        from game.mgr.guild import get_rpc_guild
        rpc_guild = get_rpc_guild(self.guildId)
        if not rpc_guild:
            return taskList
        guildLv = rpc_guild.GetLevel()
        for type, resList in Game.res_mgr.res_type_guildTask.items():
            info = self.GetSceneTaskInfo(type)
            if not info:
                for res in resList:
                    if res.minLv <= guildLv <= res.maxLv:
                        info = {"taskId":res.id, "num":0, "status":0, "refeNum":0}
                        break
                if info:
                    self.SetSceneTaskInfo(type, info)
            if info:
                taskList.append(info)
        return taskList

    #帮会场景任务信息
    def GetSceneTaskInfo(self, type):
        guildSceneTaskInfo = self.cycleDay.Query("guildSceneTaskInfo", {})
        return guildSceneTaskInfo.get(type, {})

    def SetSceneTaskInfo(self, type, info):
        guildSceneTaskInfo = self.cycleDay.Query("guildSceneTaskInfo", {})
        guildSceneTaskInfo[type] = info
        self.cycleDay.Set("guildSceneTaskInfo", guildSceneTaskInfo)

    #帮会兑换今日已刷新次数
    def GetTodayExRefNum(self):
        return self.cycleDay.Query("guildTodayExRefNum", 0)

    def SetTodayExRefNum(self, num):
        self.cycleDay.Set("guildTodayExRefNum", num)

    #今日活跃值(todayAct, int)
    def GetTodayAct(self):
        return self.cycleDay.Query("guildTodayAct", 0)

    def SetTodayAct(self, num):
        self.cycleDay.Set("guildTodayAct", num)
        spawn(self.owner.call, "guildTodayActPush", {"todayAct":num}, noresult=True)
        # 抛事件
        self.owner.safe_pub(msg_define.MSG_GUILD_TODAY_ACTEXP_CHANGE)

    #活跃每日奖励已领取列表(getList, [int])
    def GetTodayActGetList(self):
        return self.cycleDay.Query("guildTodayActGetList", [])

    def SetTodayActGetList(self, getList):
        self.cycleDay.Set("guildTodayActGetList", getList)

    # 	上香奖励已领取列表(getList, [int]) 上香任务id
    def GetTodaySXGetList(self):
        return self.cycleDay.Query("guildTodaySXGetList", [])

    def SetTodaySXGetList(self, getList):
        self.cycleDay.Set("guildTodaySXGetList", getList)

    # 本人今日是否已上香(finish, int) 0=未上香 1=已上香
    def GetTodaySXFinish(self):
        return self.cycleDay.Query("guildTodaySXFinish", 0)

    def SetTodaySXFinish(self, finish):
        self.cycleDay.Set("guildTodaySXFinish", finish)

    # 帮会副本 	今日已协助次数(helpNum, int)
    def GetTodayHelpNum(self):
        return self.cycleDay.Query("guildTodayHelpNum", 0)

    def SetTodayHelpNum(self, num):
        self.cycleDay.Set("guildTodayHelpNum", num)

    # 帮会副本	进入已挑战次数(fightNum, int)
    def GetTodayFightNum(self):
        return self.cycleDay.Query("guildTodayFightNum", 0)

    def SetTodayFightNum(self, num):
        self.cycleDay.Set("guildTodayFightNum", num)

    def markDirty(self):
        utility.DirtyFlag.markDirty(self)
        if self.owner:
            self.owner.markDirty()

    #存库数据
    def to_save_dict(self, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            self.save_cache = {}
            self.save_cache["cycleDay"] = self.cycleDay.to_save_bytes()
            self.save_cache["guildId"] = self.guildId
            self.save_cache["actLv"] = self.actLv
            self.save_cache["actExp"] = self.actExp
            self.save_cache["refTime"] = self.refTime
            self.save_cache["exList"] = self.exList
            self.save_cache["firstKill"] = self.firstKill
            self.save_cache["monsterNum"] = self.monsterNum
            self.save_cache["collectNum"] = self.collectNum
            self.save_cache["shangxiangNum"] = self.shangxiangNum
            self.save_cache["barrNum"] = self.barrNum
            self.save_cache["skillUpNum"] = self.skillUpNum
            self.save_cache["actRewardNum"] = self.actRewardNum

            self.save_cache["skills"] = []
            for pos, lv in self.skills.items():
                self.save_cache["skills"].append((pos, lv))

        return self.save_cache

    #读库数据初始化
    def load_from_dict(self, data):
        self.guildId = data.get("guildId", 0)  # 公会id
        self.actLv = data.get("actLv", 0) #帮会活跃等级(actLv, int)
        self.actExp = data.get("actExp", 0) # 帮会活跃经验(actExp, int)
        self.refTime = data.get("refTime", 0) #兑换下次刷新时间戳(refTime, int)
        self.exList = data.get("exList", []) # [(exId, status)] 兑换id(exId, int) 状态(status, int) 0=未兑换 1=已兑换
        self.firstKill = data.get("firstKill", []) #帮会副本已首通id列表
        self.monsterNum = data.get("monsterNum", 0) #帮会小怪击杀总次数
        self.collectNum = data.get("collectNum", 0) #帮会采集总次数
        self.shangxiangNum = data.get("shangxiangNum", 0) #帮会上香总次数
        self.barrNum = data.get("barrNum", 0)  # 历史帮会副本挑战总次数
        self.skillUpNum = data.get("skillUpNum", 0)  # 帮会技能历史提升次数
        self.actRewardNum = data.get("actRewardNum", 0)  # 领取公会活跃奖励次数
        self.cycleDay.load_from_dict(data.get("cycleDay", ""))

        skills = data.get("skills", [])
        for one in skills:
            pos, lv = one
            self.skills[pos] = lv  # {pos:lv} 帮会技能列表(skill, [json]) 部位(pos, int) 等级(lv, int)

    def reSetRefTime(self):
        tRefe = (0, 4, 8 ,12, 16, 20)
        iHour = current_hour()
        iNextHour = 0
        for refe in tRefe:
            if iHour < refe:
                iNextHour = refe
        if iNextHour == 0:
            iNextHour = 24
        self.refTime = int(cur_day_hour_time(iNextHour))
        self.markDirty()

    def GetMonsterNum(self): # 帮会小怪击杀总次数
        return self.monsterNum

    def SetMonsterNum(self, num): # 帮会小怪击杀总次数
        self.monsterNum = num
        self.markDirty()

    def GetSkillUpNum(self):  # 帮会技能历史提升次数
        return self.skillUpNum

    def SetSkillUpNum(self, num):  # 帮会技能历史提升次数
        self.skillUpNum = num
        self.markDirty()

    def GetActRewardNum(self):  # 领取公会活跃奖励次数
        return self.actRewardNum

    def SetActRewardNum(self, num):  # 领取公会活跃奖励次数
        self.actRewardNum = num
        self.markDirty()

    def GetCollectNum(self): # 帮会采集总次数
        return self.collectNum

    def SetCollectNum(self, num): # 帮会采集总次数
        self.collectNum = num
        self.markDirty()

    def GetShangxiangNum(self): # 帮会上香总次数
        return self.shangxiangNum

    def SetShangxiangNum(self, num): # 帮会上香总次数
        self.shangxiangNum = num
        self.markDirty()

    def GetBarrNum(self): # 历史帮会副本挑战总次数
        return self.barrNum

    def SetBarrNum(self, num): # 历史帮会副本挑战总次数
        self.barrNum = num
        self.markDirty()

    def GetGuildId(self):
        return self.guildId

    def SetGuildId(self, guildId):
        self.guildId = guildId
        self.markDirty()

    def GetActLv(self):
        return self.actLv

    def SetActLv(self, actLv):
        self.actLv = actLv
        self.markDirty()

    def GetActExp(self):
        return self.actExp

    def SetActExp(self, actExp):
        self.actExp = actExp
        self.markDirty()
        spawn(self.owner.call, "guildActInfoPush", {"actLv": self.actLv, "actExp":self.actExp}, noresult=True)

    def GetSkillLv(self, pos):
        return self.skills.get(pos, 0)

    def SetSkillLv(self, pos, lv):
        self.skills[pos] = lv
        self.markDirty()

    def SetExList(self, exList):
        self.exList = exList
        self.markDirty()

    def isBarrFirst(self, id):
        return 0 if id in self.firstKill else 1

    def addBarrFirst(self, id):
        if id not in self.firstKill:
            self.firstKill.append(id)
            self.markDirty()

    def to_skill_data(self):
        resp = []
        for pos, lv in self.skills.items():
            resp.append({"pos":pos, "lv":lv})
        return resp

    def Add_BgCoin(self, num):
        if not self.guildId:
            return
        from game.mgr.guild import get_rpc_guild
        rpc_guild = get_rpc_guild(self.guildId)
        if not rpc_guild:
            return
        rpc_guild.Add_BgCoin(self.owner.id, num)

    def init_exchange_data(self):
        if not self.guildId:
            return
        from game.mgr.guild import get_rpc_guild
        rpc_guild = get_rpc_guild(self.guildId)
        if not rpc_guild:
            return
        iGuildLv = rpc_guild.GetLevel()

        guildlvRes = Game.res_mgr.res_guildlv.get(iGuildLv)
        if not guildlvRes:
            return

        exList = []
        if guildlvRes.exchange:
            for i in range(4):
                exId = utility.Choice(guildlvRes.exchange)
                exList.append((exId, 0))
        self.SetExList(exList)

    def to_exchange_data(self):
        if self.guildId and not self.exList:
            self.init_exchange_data()
        resp = []
        for exId, status in self.exList:
            resp.append({"exId": exId, "status": status})
        return resp

    def to_barr_data(self):
        resp = {}
        resp["helpNum"] = self.GetTodayHelpNum(),
        resp["fightNum"] = self.GetTodayFightNum(),
        resp["firstKill"] = self.firstKill
        return resp

    #登录初始化下发数据
    def to_init_data(self):
        if self.guildId:
            if not self.refTime or int(time.time()) >= self.refTime:
                self.reSetRefTime()
                self.init_exchange_data()

        init_data = {}
        init_data["guildId"] = self.guildId
        init_data["sx"] = {
            "getList": self.GetTodaySXGetList(),
            "finish": self.GetTodaySXFinish(),
        }

        actTaskList = []
        # actTaskList.extend(self.owner.task.to_GuildActTasks_data())
        # actTaskList.extend(self.owner.task.to_GuildActRewardTasks_data())
        init_data["act"] = {
            "actLv": self.actLv,
            "actExp": self.actExp,
            "todayAct": self.GetTodayAct(),
            "getList": self.GetTodayActGetList(),
            "actTaskList": actTaskList, #帮会活跃任务列表 去任务模块拿
        }
        refNumRes = Game.res_mgr.res_common.get("guildRefNum")
        if refNumRes:
            exRefNum = refNumRes.i - self.GetTodayExRefNum()
        else:
            exRefNum = refNumRes.i
        init_data["scene"] = {
            "exList": self.to_exchange_data(),
            "exRefNum": exRefNum,
            "refTime": self.refTime,
            "taskList": self.getSceneTaskInfo(), #场景任务
        }
        skills = []
        for pos, lv in self.skills.items():
            skills.append({"pos":pos, "lv":lv})
        init_data["skill"] = skills
        init_data["barr"] = {
            "helpNum": self.GetTodayHelpNum(),
            "fightNum": self.GetTodayFightNum(),
            "firstKill": self.firstKill,
        }

        from game.mgr.guild import get_rpc_guild
        rpc_guild = get_rpc_guild(self.guildId)
        if rpc_guild:
            _init_data = rpc_guild.to_init_data(self.owner.id)
            init_data["sx"]["sxBar"] = _init_data.pop("sxBar")
            init_data["sx"]["sxNum"] = _init_data.pop("sxNum")
            init_data.update(_init_data)
        return init_data

    #零点更新的数据
    def to_wee_hour_data(self):
        return self.to_init_data()

    def to_guild_update(self):
        resp = {}
        resp["rid"] = self.owner.id  # 角色id(rid, int)
        resp["name"] = self.owner.name  # 角色名字(name, string)
        resp["fa"] = self.owner.base.fa # 战力(fa, int)
        resp["time"] = 0 # 最后一次离线时间戳(time, int) 0 = 在线
        resp["sex"] = self.owner.base.GetSex() # 性别(sex, int)0 =? 1 = 男 2 = 女
        resp["portrait"] = self.owner.myhead.getPortrait()
        resp["headframe"] = self.owner.myhead.getHeadframe()
        resp["lv"] = self.owner.base.GetLv() # 等级
        return resp

    def getGuildName(self):
        guildName = ''

        from game.mgr.guild import get_rpc_guild
        rpc_guild = get_rpc_guild(self.guildId)
        if rpc_guild:
            guildName = rpc_guild.getName()
        return guildName
