#!/usr/bin/env python
# -*- coding:utf-8 -*-
import random
import time

from corelib.gtime import current_hour

from game.define import errcode, constant, msg_define
from game import Game

from game.mgr.guild import get_rpc_guild, Guild
from corelib import log
from game.common import utility

from game.core.equip import CreatEquip
from game.core.item import CreatItem

class GuildRpcMixin(object):
    if 0:
        from game.core import player as player_md
        player = player_md.Player()

    # 打开帮会主界面(openGuildUI)
    # 请求
    #     帮会id(guildId, string)
    # 返回
    #     公告(notice, string) 做时间戳校验，客户端如果取到空不做处理
    #     帮主名称(bzName, string)
    #     帮会资金(exp, int)
    #     帮会人数(num, int)
    def rc_openGuildUI(self, guildId):
        rpc_guild = get_rpc_guild(guildId)
        if not rpc_guild:
            return 0, errcode.EC_NOT_FOUND_GUILD
        resp = rpc_guild.to_openUI_dict()
        return 1, resp

    # 创建帮会(createGuild)
    # 请求
    #     帮会名称(name, string)
    #     帮会等级(lv, int)
    # 返回
    #     主动推送刷新(allUpdate, json)
    #         游戏模型 - 帮会信息
    #         游戏模型 - 货币
    def rc_createGuild(self, name, lv):
        guildlvRes = Game.res_mgr.res_guildlv.get(lv)
        if not guildlvRes:
            return 0, errcode.EC_NORES
        createLvRes = Game.res_mgr.res_common.get("guildCreateLv", [])
        if not createLvRes:
            return 0, errcode.EC_NORES
        if lv not in createLvRes.arrayint1:
            return 0, errcode.EC_GUILD_CREATE_LV_ERR
        #vip限制
        iVip = self.player.vip.GetVipLv()
        if iVip < guildlvRes.vip:
            return 0, errcode.EC_GUILD_CREATE_VIP_LIMIT
        d = Game.store.query_loads(Guild.DATA_CLS.TABLE_NAME, dict(name=name))
        if d:
            return 0, errcode.EC_GUILD_NAME_REPET
        # 扣道具
        respBag = self.player.bag.costItem(guildlvRes.cost, constant.ITEM_COST_CREATE_GUILD, wLog=True)
        if not respBag.get("rs", 0):
            return 0, errcode.EC_GUILD_CREATE_NOT_ENOUGH
        #个人信息
        playerInfo = self.player.guild.to_guild_update()
        rs, guildId = Game.rpc_guild_mgr.CreateGuild(name, lv, playerInfo)
        if not rs:
            #返回扣除的材料
            self.player.bag.add(guildlvRes.cost, constant.ITEM_ADD_GUILD_CREATE_FAIL, wLog=True)
            return 0, errcode.EC_GUILD_CREATE_FAIL
        self.player.guild.SetGuildId(guildId)
        # self.player.task.initGuildActTasks()
        # self.player.task.initGuildActRewardTasks()
        # 抛事件
        self.player.safe_pub(msg_define.MSG_JOIN_GUILD)
        # 打包返回信息
        dUpdate = self.player.packRespBag(respBag)
        dUpdate["guildInfo"] = self.player.guild.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp

    # 申请/取消入帮(enterGuild)
    # 请求
    #     帮会id(guildId, string)
    #     类型(type, int)
    #         0=取消 1=申请
    # 返回
    #     帮会id(guildId, string)
    #     类型(type, int)
    #         0=未申请 1=已申请
    def rc_enterGuild(self, guildId, type):
        if self.player.guild.GetGuildId():
            return 0, errcode.EC_GUILD_HAS_JOIN
        rpc_guild = get_rpc_guild(guildId)
        if not rpc_guild:
            return 0, errcode.EC_NOT_FOUND_GUILD
        playerInfo = self.player.guild.to_guild_update()
        rs, err = rpc_guild.enterGuild(type, playerInfo)
        if not rs:
            return rs, err
        # 打包返回信息
        resp = {
            "guildId": guildId,
            "type": type,
        }
        return 1, resp

    # 帮会申请批复respGuild
    # 请求
    #     角色id(rid, int)
    #     类型(type, int)
    #         0=拒绝 1=同意
    # 返回
    #     角色id(rid, int)
    #     类型(type, int)
    #         0=拒绝 1=同意
    def rc_respGuild(self, rid, type):
        guildId = self.player.guild.GetGuildId()
        if not guildId:
            return 0, errcode.EC_NO_GUILD
        rpc_guild = get_rpc_guild(guildId)
        if not rpc_guild:
            return 0, errcode.EC_NOT_FOUND_GUILD
        rs, data = rpc_guild.respGuild(self.player.id, rid, type)
        if not rs:
            return rs, data
        # 打包返回信息
        resp = {
            "rid": rid,
            "type": type,
            "num": data,
        }
        return 1, resp

    # 帮会成员操作(guildOper)
    # 请求
    #     角色id(rid, int)
    #     类型(type, int)
    #         1=禅让 2=升职 3=降职 4=踢出
    # 返回
    #     角色id(rid, int)
    #     类型(type, int)
    #         1=禅让 2=升职 3=降职 4=踢出
    def rc_guildOper(self, rid, type):
        guildId = self.player.guild.GetGuildId()
        if not guildId:
            return 0, errcode.EC_NO_GUILD
        rpc_guild = get_rpc_guild(guildId)
        if not rpc_guild:
            return 0, errcode.EC_NOT_FOUND_GUILD
        rs, data = rpc_guild.guildOper(self.player.id, rid, type)
        if not rs:
            return  rs, data
        # 打包返回信息
        resp = {
            "rid": rid,
            "type": type,
            "num": data,
        }
        return 1, resp

    # 退出帮会(exitGuild)
    # 请求
    # 返回
    #     注意：客户端要清除帮会模块的本地数据
    def rc_exitGuild(self):
        guildId = self.player.guild.GetGuildId()
        if not guildId:
            return 0, errcode.EC_NO_GUILD
        rpc_guild = get_rpc_guild(guildId)
        if not rpc_guild:
            return 0, errcode.EC_NOT_FOUND_GUILD
        rs, err = rpc_guild.exitGuild(self.player.id)
        if not rs:
            return rs, err
        self.player.guild.SetGuildId(0)
        # 打包返回信息
        return 1, None

    # 帮会改名(guildChangeName)
    # 请求
    #     帮会名称(name, string)
    # 返回
    #     帮会名称(name, string)
    def rc_guildChangeName(self, name):
        guildId = self.player.guild.GetGuildId()
        if not guildId:
            return 0, errcode.EC_NO_GUILD
        rpc_guild = get_rpc_guild(guildId)
        if not rpc_guild:
            return 0, errcode.EC_NOT_FOUND_GUILD
        d = Game.store.query_loads(Guild.DATA_CLS.TABLE_NAME, dict(name=name))
        if d:
            return 0, errcode.EC_GUILD_NAME_REPET
        rs, err = rpc_guild.changeName(self.player.id, name)
        if not rs:
            return rs, err
        # 打包返回信息
        resp = {
            "name": name,
        }
        return 1, resp

    # 帮会改颜色(guildChangeColor)
    # 请求
    #     帮会名称(color, string)
    # 返回
    #     帮会名称(color, string)
    def rc_guildChangeColor(self, color):
        guildId = self.player.guild.GetGuildId()
        if not guildId:
            return 0, errcode.EC_NO_GUILD
        rpc_guild = get_rpc_guild(guildId)
        if not rpc_guild:
            return 0, errcode.EC_NOT_FOUND_GUILD

        rs, err = rpc_guild.changeColor(self.player.id, color)
        if not rs:
            return rs, err
        # 打包返回信息
        resp = {
            "color": color,
        }
        return 1, resp

    # 修改帮会公告(fixGuildNotice)
    # 请求
    #     帮会公告(notice, string)
    # 返回
    #     帮会公告(notice, string)
    def rc_fixGuildNotice(self, notice):
        guildId = self.player.guild.GetGuildId()
        if not guildId:
            return 0, errcode.EC_NO_GUILD
        rpc_guild = get_rpc_guild(guildId)
        if not rpc_guild:
            return 0, errcode.EC_NOT_FOUND_GUILD
        rs, err = rpc_guild.fixNotice(self.player.id, notice)
        if not rs:
            return rs, err
        # 打包返回信息
        resp = {
            "notice": notice,
        }
        return 1, resp

    # 查看帮会记录(getGuildRecord)
    # 请求
    # 返回
    #     记录列表(recordList, [json])
    #         类型(type, int)
    #             1=加入帮会 2=退出帮会 3=被踢 4=升职 5=降职 6=禅让
    #         参数(args, [string])
    #         时间戳(time, int)
    def rc_getGuildRecord(self):
        guildId = self.player.guild.GetGuildId()
        if not guildId:
            return 0, errcode.EC_NO_GUILD
        rpc_guild = get_rpc_guild(guildId)
        if not rpc_guild:
            return 0, errcode.EC_NOT_FOUND_GUILD
        logs = rpc_guild.getLogs()
        recordList = []
        for one in logs:
            iTime, args, type = one
            recordList.append({"type":type, "time":iTime, "args":args})
        # 打包返回信息
        resp = {
            "recordList": recordList,
        }
        return 1, resp

    # 请求帮会成员列表(getGuildMember)
    # 请求
    # 返回
    #     成员列表(roleList, [json])
    #         角色id(rid, int)
    #         角色名字(name, string)
    #         战力(fa, int)
    #         最后一次离线时间戳(time, int)
    #             0=在线
    #         性别(sex, int)
    #             0=? 1=男 2=女
    #         职位(job, int)
    #             1=帮主 2=副帮主 3=成员
    #         对当前帮会的累计贡献(bgCoin, int)
    def rc_getGuildMember(self):
        guildId = self.player.guild.GetGuildId()
        if not guildId:
            return 0, errcode.EC_NO_GUILD
        rpc_guild = get_rpc_guild(guildId)
        if not rpc_guild:
            return 0, errcode.EC_NOT_FOUND_GUILD
        roleList = rpc_guild.getMembers()
        # 打包返回信息
        resp = {
            "roleList": roleList,
        }
        return 1, resp

    # 查看帮会申请列表(getEnterGuild)
    # 请求
    # 返回
    #     申请列表(enterList, [json])
    #         角色id(rid, int)
    #         角色名字(name, string)
    #         战力(fa, int)
    #         性别(sex, int)
    #             0=? 1=男 2=女
    #         等级(lv, int)
    #     是否自动入帮(autoEnter, int)
    #     自动入帮战力(autoFa, int)
    def rc_getEnterGuild(self):
        guildId = self.player.guild.GetGuildId()
        if not guildId:
            return 0, errcode.EC_NO_GUILD
        rpc_guild = get_rpc_guild(guildId)
        if not rpc_guild:
            return 0, errcode.EC_NOT_FOUND_GUILD
        resp = rpc_guild.getApplyData()
        return 1, resp

    # 修改自动入帮条件(fixEnterGuild)
    # 请求
    #     是否自动入帮(autoEnter, int)
    #     自动入帮战力(autoFa, int)
    # 返回
    #     是否自动入帮(autoEnter, int)
    #     自动入帮战力(autoFa, int)
    def rc_fixEnterGuild(self, autoEnter, autoFa):
        guildId = self.player.guild.GetGuildId()
        if not guildId:
            return 0, errcode.EC_NO_GUILD
        rpc_guild = get_rpc_guild(guildId)
        if not rpc_guild:
            return 0, errcode.EC_NOT_FOUND_GUILD
        rs, err = rpc_guild.fixAutoEnter(self.player.id, autoEnter, autoFa)
        if not rs:
            return rs, err
        # 打包返回信息
        resp = {
            "autoEnter": autoEnter,
            "autoFa": autoFa,
        }
        return 1, resp

    # 查看帮会列表(getGuildList)
    # 请求
    # 返回
    #     帮会列表(guildList, [json])
    #         帮会id(guildId, string)
    #         帮会名称(name, string)
    #         帮主名称(bzName, string)
    #         帮会等级(guildLv, int)
    #         当前人数(num, int)
    #         需要战力(fa, int)
    #         是否已申请(status, int)
    #             0=未申请 1=已申请
    def rc_getGuildList(self):
        guildList = Game.rpc_guild_mgr.getGuildList(self.player.id)
        # 打包返回信息
        resp = {
            "guildList": guildList,
        }
        return 1, resp

    # 请求帮会上香记录(getGuildSxList)
    # 请求
    # 返回
    #     上香列表(sxList, [json])
    #         上香时间戳(time, int)
    #         上香人名字(name, string)
    #         上香id(id, int)
    def rc_getGuildSxList(self):
        guildId = self.player.guild.GetGuildId()
        if not guildId:
            return 0, errcode.EC_NO_GUILD
        rpc_guild = get_rpc_guild(guildId)
        if not rpc_guild:
            return 0, errcode.EC_NOT_FOUND_GUILD
        sxList = rpc_guild.getSxList()
        # 打包返回信息
        resp = {
            "sxList": sxList,
        }
        return 1, resp

    # 帮会上香(guildSx)
    # 请求
    #     上香id(id, int)
    # 返回
    #     帮会上香进度(sxBar, int)
    #         帮会每日清0
    #     帮会上香次数(sxNum, int)
    #         帮会每日清0
    #     本人今日是否已上香(finish, int)
    #         个人每日清0
    #         0=未上香 1=已上香
    # 同步给帮会在线的所有人
    #     帮会上香进度(sxBar, int)
    #         帮会每日清0
    #     帮会上香次数(sxNum, int)
    #         帮会每日清0
    def rc_guildSx(self, id):
        sxRes = Game.res_mgr.res_guildSx.get(id)
        if not sxRes:
            return 0, errcode.EC_NORES
        if self.player.guild.GetTodaySXFinish():
            return 0, errcode.EC_GUILD_TODAY_HAS_SX
        guildId = self.player.guild.GetGuildId()
        if not guildId:
            return 0, errcode.EC_NO_GUILD
        rpc_guild = get_rpc_guild(guildId)
        if not rpc_guild:
            return 0, errcode.EC_NOT_FOUND_GUILD
        # 扣道具
        respBag = self.player.bag.costItem(sxRes.cost, constant.ITEM_COST_GUILD_SX, wLog=True)
        if not respBag.get("rs", 0):
            return 0, errcode.EC_GUILD_SX_NOT_ENOUGH
        rs, data = rpc_guild.guildSx(self.player.id, id)
        if not rs:
            # 返回扣除的材料
            self.player.bag.add(sxRes.cost, constant.ITEM_ADD_GUILD_SX_FAIL, wLog=True)
            return rs, data
        sxBar, sxNum = data
        self.player.guild.SetTodaySXFinish(1)
        #上香奖励
        respBag1 = self.player.bag.add(sxRes.reward, constant.ITEM_ADD_GUILD_SX, wLog=True)
        respBag = self.player.mergeRespBag(respBag, respBag1)
        # 统计次数
        shangxiangNum = self.player.guild.GetShangxiangNum()
        shangxiangNum += 1
        self.player.guild.SetShangxiangNum(shangxiangNum)
        #抛事件
        self.player.safe_pub(msg_define.MSG_GUILD_SX)
        # 打包返回信息
        dUpdate = self.player.packRespBag(respBag)
        resp = {
            "sxBar": sxBar,
            "sxNum": sxNum,
            "finish": 1,
            "allUpdate": dUpdate,
        }
        return 1, resp

    # 领取帮会上香奖励(getGuildSxReward)
    # 请求
    #     上香奖励id(id, int)
    # 返回
    #     上香奖励已领取列表(getList, [int])
    def rc_getGuildSxReward(self, id):
        sxBarRes = Game.res_mgr.res_guildSxBar.get(id)
        if not sxBarRes:
            return 0, errcode.EC_NORES
        getList = self.player.guild.GetTodaySXGetList()
        if id in getList:
            return 0, errcode.EC_GUILD_TODAY_HAS_SX
        guildId = self.player.guild.GetGuildId()
        if not guildId:
            return 0, errcode.EC_NO_GUILD
        rpc_guild = get_rpc_guild(guildId)
        if not rpc_guild:
            return 0, errcode.EC_NOT_FOUND_GUILD
        sxInfo = rpc_guild.GetSxInfo()
        sxBar = sxInfo.get("sxBar", 0)
        if sxBar < sxBarRes.num:
            return 0, errcode.EC_GUILD_SX_REWARD_NOT_ENOUGH
        # 上香奖励
        respBag = self.player.bag.add(sxBarRes.reward, constant.ITEM_ADD_GUILD_SX_REWARD, wLog=True)
        getList.append(id)
        self.player.guild.SetTodaySXGetList(getList)
        # 打包返回信息
        dUpdate = self.player.packRespBag(respBag)
        resp = {
            "getList": getList,
            "allUpdate": dUpdate,
        }
        return 1, resp

    # 进入帮会地图(enterGuildScene)
    # 请求
    # 返回
    #     场景人员列表(roleList, [json])
    def rc_enterGuildScene(self):
        guildId = self.player.guild.GetGuildId()
        if not guildId:
            return 0, errcode.EC_NO_GUILD
        rpc_guild = get_rpc_guild(guildId)
        if not rpc_guild:
            return 0, errcode.EC_NOT_FOUND_GUILD
        roleList = []
        pids = rpc_guild.enterGuildScene()
        from game.mgr.player import get_rpc_player
        for pid in pids:
            rpc_player = get_rpc_player(pid)
            info = rpc_player.GetFightData()
            roleList.append(info)
        resp = {
            "roleList": roleList,
        }
        return 1, resp

    # 帮会采集(guildCj)
    # 请求
    # 返回
    #     主动推送刷新(allUpdate, json)
    #         游戏模型-帮会信息
    #             场景任务(taskList, [json])
    #                 任务表id(taskId, int)
    #                 当前进度(num, int)
    #                 是否已领取(status, int)
    #                     0=未领取 1=已领取
    #                 当前已刷新次数(refeNum, int)
    #             直推当前任务数据
    def rc_guildCj(self):
        guildId = self.player.guild.GetGuildId()
        if not guildId:
            return 0, errcode.EC_NO_GUILD
        info = self.player.guild.GetSceneTaskInfo(constant.GUILD_TASK_TYPE_1)
        taskId = info.get("taskId", 0)
        taskRes = Game.res_mgr.res_guildTask.get(taskId)
        if not taskRes:
            return 0, errcode.EC_NORES
        rewardRes = Game.res_mgr.res_reward.get(int(taskRes.arg2))
        if not rewardRes:
            return 0, errcode.EC_NORES
        guildTaskRewardTimeRes = Game.res_mgr.res_common.get("guildTaskRewardTime")
        if not guildTaskRewardTimeRes:
            return 0, errcode.EC_NORES
        iNum = info.get("num", 0)
        if iNum >= taskRes.condition:
            return 0, errcode.EC_GUILD_TASK_HAS_FINISH
        iHour = current_hour()
        iAdd = 1
        if guildTaskRewardTimeRes.arrayint1[0] <= iHour < guildTaskRewardTimeRes.arrayint1[1]:
            iAdd = 5
        info["num"] = iNum + iAdd
        if info["num"] >= taskRes.condition:
            info["num"] = taskRes.condition
        self.player.guild.SetSceneTaskInfo(constant.GUILD_TASK_TYPE_1, info)
        #采集奖励
        respBag = {}
        for i in range(iAdd):
            dReward = rewardRes.doReward()
            respBag1 = self.player.bag.add(dReward, constant.ITEM_ADD_GUILD_TASK, wLog=True)
            respBag = self.player.mergeRespBag(respBag, respBag1)
        #统计采集次数
        collectNum = self.player.guild.GetCollectNum()
        collectNum += iAdd
        self.player.guild.SetCollectNum(collectNum)
        # 抛事件
        self.player.safe_pub(msg_define.MSG_GUILD_COLLECT)

        # 打包返回信息

        dUpdate = self.player.packRespBag(respBag)
        dUpdate["guildInfo"] = {
            "scene": {"taskList": [info]}
        }
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp

    # 帮会打怪(guildKillMst)
    # 请求
    # 返回
    #     主动推送刷新(allUpdate, json)
    #         游戏模型-帮会信息
    #             场景任务(taskList, [json])
    #                 任务表id(taskId, int)
    #                 当前进度(num, int)
    #                 是否已领取(status, int)
    #                     0=未领取 1=已领取
    #                 当前已刷新次数(refeNum, int)
    #             直推当前任务数据
    def rc_guildKillMst(self):
        guildId = self.player.guild.GetGuildId()
        if not guildId:
            return 0, errcode.EC_NO_GUILD
        info = self.player.guild.GetSceneTaskInfo(constant.GUILD_TASK_TYPE_2)
        taskId = info.get("taskId", 0)
        taskRes = Game.res_mgr.res_guildTask.get(taskId)
        if not taskRes:
            return 0, errcode.EC_NORES
        rewardRes = Game.res_mgr.res_reward.get(int(taskRes.arg2))
        if not rewardRes:
            return 0, errcode.EC_NORES
        iNum = info.get("num", 0)
        if iNum >= taskRes.condition:
            return 0, errcode.EC_GUILD_TASK_HAS_FINISH
        guildTaskRewardTimeRes = Game.res_mgr.res_common.get("guildTaskRewardTime")
        if not guildTaskRewardTimeRes:
            return 0, errcode.EC_NORES
        #初始化副本
        fightobj = Game.fight_mgr.createFight(constant.FIGHT_TYPE_110)
        rs = fightobj.init_by_barrId(self.player, int(taskRes.arg1))
        if not rs:
            return 0, errcode.EC_INIT_BARR_FAIL
        fightLog = fightobj.doFight()
        fightResult = fightLog["result"].get("win", 0)
        #更新数据
        respBag = {}
        if fightResult:
            iHour = current_hour()
            iAdd = 1
            if guildTaskRewardTimeRes.arrayint1[0] <= iHour < guildTaskRewardTimeRes.arrayint1[1]:
                iAdd = 5
            info["num"] = iNum + iAdd
            if info["num"] >= taskRes.condition:
                info["num"] = taskRes.condition

            self.player.guild.SetSceneTaskInfo(constant.GUILD_TASK_TYPE_2, info)
            # 打怪奖励
            for i in range(iAdd):
                dReward = rewardRes.doReward()
                respBag1 = self.player.bag.add(dReward, constant.ITEM_ADD_GUILD_TASK, wLog=True)
                respBag = self.player.mergeRespBag(respBag, respBag1)
            # 统计次数
            monsterNum = self.player.guild.GetMonsterNum()
            monsterNum += iAdd
            self.player.guild.SetMonsterNum(monsterNum)
            # 抛事件
            self.player.safe_pub(msg_define.MSG_GUILD_MONSTER_KILL)
        # 打包返回信息
        dUpdate = self.player.packRespBag(respBag)
        dUpdate["guildInfo"] = {
            "scene": {"taskList": [info]}
        }
        resp = {
            "fightLog":fightLog,
            "allUpdate": dUpdate,
        }
        return 1, resp

    # 帮会任务一键完成(guildTaskOneKeyFinish)
    # 请求
    #     任务表id(taskId, int)
    # 返回
    #     主动推送刷新(allUpdate, json)
    #         游戏模型-帮会信息
    #             场景任务(taskList, [json])
    #                 任务表id(taskId, int)
    #                 当前进度(num, int)
    #                 是否已领取(status, int)
    #                     0=未领取 1=已领取
    #                 当前已刷新次数(refeNum, int)
    #             直推当前任务数据
    def rc_guildTaskOneKeyFinish(self, taskId):
        guildId = self.player.guild.GetGuildId()
        if not guildId:
            return 0, errcode.EC_NO_GUILD
        taskRes = Game.res_mgr.res_guildTask.get(taskId)
        if not taskRes:
            return 0, errcode.EC_NORES
        info = self.player.guild.GetSceneTaskInfo(taskRes.type)
        if not info:
            return 0, errcode.EC_GUILD_TASK_NOT_FOUND
        rewardRes = Game.res_mgr.res_reward.get(int(taskRes.arg2))
        if not rewardRes:
            return 0, errcode.EC_NORES
        iNum = info.get("num", 0)
        if iNum >= taskRes.condition:
            return 0, errcode.EC_GUILD_TASK_HAS_FINISH
        # 扣道具
        respBag = self.player.bag.costItem(taskRes.finishCost, constant.ITEM_COST_GUILD_TASK_FINISH, wLog=True)
        if not respBag.get("rs", 0):
            return 0, errcode.EC_GUILD_TASK_FINISH_NOT_ENOUGH
        # 更新数据
        iAdd = taskRes.condition - iNum
        info["num"] = taskRes.condition
        self.player.guild.SetSceneTaskInfo(taskRes.type, info)
        for i in range(iAdd):
            dReward = rewardRes.doReward()
            respBag1 = self.player.bag.add(dReward, constant.ITEM_ADD_GUILD_TASK, wLog=True)
            respBag = self.player.mergeRespBag(respBag, respBag1)

        if taskRes.type == constant.GUILD_TASK_TYPE_1:
            #统计采集次数
            collectNum = self.player.guild.GetCollectNum()
            collectNum += iAdd
            self.player.guild.SetCollectNum(collectNum)
            # 抛事件
            self.player.safe_pub(msg_define.MSG_GUILD_COLLECT)
        if taskRes.type == constant.GUILD_TASK_TYPE_2:
            # 统计次数
            monsterNum = self.player.guild.GetMonsterNum()
            monsterNum += iAdd
            self.player.guild.SetMonsterNum(monsterNum)
            # 抛事件
            self.player.safe_pub(msg_define.MSG_GUILD_MONSTER_KILL)

        # 打包返回信息
        dUpdate = self.player.packRespBag(respBag)
        dUpdate["guildInfo"] = {
            "scene": {"taskList": [info]}
        }
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp

    # 帮会任务重置(guildTaskReset)
    # 请求
    #     任务表id(taskId, int)
    # 返回
    #     主动推送刷新(allUpdate, json)
    #         游戏模型-帮会信息
    #             场景任务(taskList, [json])
    #                 任务表id(taskId, int)
    #                 当前进度(num, int)
    #                 是否已领取(status, int)
    #                     0=未领取 1=已领取
    #                 当前已刷新次数(refeNum, int)
    #             直推当前任务数据
    def rc_guildTaskReset(self, taskId):
        guildId = self.player.guild.GetGuildId()
        if not guildId:
            return 0, errcode.EC_NO_GUILD
        taskRes = Game.res_mgr.res_guildTask.get(taskId)
        if not taskRes:
            return 0, errcode.EC_NORES
        info = self.player.guild.GetSceneTaskInfo(taskRes.type)
        if not info:
            return 0, errcode.EC_GUILD_TASK_NOT_FOUND
        iVipLv = self.player.vip.GetVipLv()
        vipRes = Game.res_mgr.res_vip.get(iVipLv)
        if not vipRes:
            return 0, errcode.EC_NORES
        #刷新次数判断
        iRefeNum = info.get("refeNum", 0)
        if iRefeNum >= vipRes.guildTaskResetNum:
            return 0, errcode.EC_GUILD_TASK_RESET_MAX_NUM
        # 扣道具
        respBag = self.player.bag.costItem(taskRes.resetCost, constant.ITEM_COST_GUILD_TASK_RESET, wLog=True)
        if not respBag.get("rs", 0):
            return 0, errcode.EC_GUILD_TASK_RESET_NOT_ENOUGH
        # 更新数据
        info["num"] = 0
        info["status"] = 0
        info["refeNum"] = iRefeNum + 1
        self.player.guild.SetSceneTaskInfo(taskRes.type, info)
        # 打包返回信息
        dUpdate = self.player.packRespBag(respBag)
        dUpdate["guildInfo"] = {
            "scene": {"taskList": [info]}
        }
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp

    # 帮会任务奖励领取(guildTaskGetReward)
    # 请求
    #     任务表id(taskId, int)
    # 返回
    #     主动推送刷新(allUpdate, json)
    #         游戏模型-帮会信息
    #             场景任务(taskList, [json])
    #                 任务表id(taskId, int)
    #                 当前进度(num, int)
    #                 是否已领取(status, int)
    #                     0=未领取 1=已领取
    #                 当前已刷新次数(refeNum, int)
    #             直推当前任务数据
    def rc_guildTaskGetReward(self, taskId):
        guildId = self.player.guild.GetGuildId()
        if not guildId:
            return 0, errcode.EC_NO_GUILD
        taskRes = Game.res_mgr.res_guildTask.get(taskId)
        if not taskRes:
            return 0, errcode.EC_NORES
        info = self.player.guild.GetSceneTaskInfo(taskRes.type)
        if not info:
            return 0, errcode.EC_GUILD_TASK_NOT_FOUND
        if info["status"] == 1:
            return 0, errcode.EC_GUILD_TASK_REWARD_HAS_GET
        respBag = self.player.bag.add(taskRes.rewardArrayint2, constant.ITEM_ADD_GUILD_TASK, wLog=True)
        # 更新数据
        info["status"] = 1
        self.player.guild.SetSceneTaskInfo(taskRes.type, info)
        # 抛事件
        if taskRes.type == constant.GUILD_TASK_TYPE_1:
            self.player.safe_pub(msg_define.MSG_GUILD_SCENE_CJ)
        # 抛事件
        if taskRes.type == constant.GUILD_TASK_TYPE_2:
            self.player.safe_pub(msg_define.MSG_GUILD_SCENE_BARR)
        # 打包返回信息
        dUpdate = self.player.packRespBag(respBag)
        dUpdate["guildInfo"] = {
            "scene": {"taskList": [info]}
        }
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp


    # 帮会兑换(guildExchange)
    # 请求
    #     兑换索引(id, int) 0,1,2,3
    # 返回
    #     主动推送刷新(allUpdate, json)
    #         游戏模型-帮会信息
    #             直推当前兑换数据
    #             兑换id列表(exList, [json])
    #                 兑换id(exId, int)
    #                 状态(status, int)
    #                     0=未兑换 1=已兑换
    def rc_guildExchange(self, id):
        guildId = self.player.guild.GetGuildId()
        if not guildId:
            return 0, errcode.EC_NO_GUILD
        if id + 1 > len(self.player.guild.exList):
            return 0, errcode.EC_NORES
        exId, status = self.player.guild.exList[id]
        if status is None:
            return 0, errcode.EC_GUILD_EXCHANGE_NOT_FOUND
        if status == 1:
            return 0, errcode.EC_GUILD_EXCHANGE_HAS_BUY
        exRes = Game.res_mgr.res_exchange.get(exId)
        if not exRes:
            return 0, errcode.EC_NORES
        # 背包检测
        addEquip = {}
        if exRes.equipId:
            addEquip[exRes.equipId] = exRes.num
            iFree = self.player.bag.getFreeSize()
            if iFree < exRes.num:
                return 0, errcode.EC_BAG_FULL
        # 扣道具
        respBag = self.player.bag.costItem(exRes.cost, constant.ITEM_COST_GUILD_EXCHANGE, wLog=True)
        if not respBag.get("rs", 0):
            return 0, errcode.EC_GUILD_EXCHANGE_NOT_ENOUGH
        # 加道具
        additem = {}
        itemRes = None
        if exRes.itemId:
            itemRes, itemobj = CreatItem(exRes.itemId)
            for i in range(exRes.num):
                reward = itemobj.getReward()
                for iNo, iNum in reward.items():
                    if iNo in additem:
                        additem[iNo] += iNum
                    else:
                        additem[iNo] = iNum
        respBag1 = self.player.bag.add(additem, constant.ITEM_ADD_GUILD_EXCHANGE, wLog=True)
        respBag = self.player.mergeRespBag(respBag, respBag1)
        # 加装备
        equipobjs = []
        for equipNo, num in addEquip.items():
            for i in range(num):
                equipRes, equipobj = CreatEquip(equipNo)
                if not equipobj:
                    break
                equipobjs.append(equipobj)
        rs, _resp_equip = self.player.bag.addEquip(equipobjs, constant.ITEM_ADD_GUILD_EXCHANGE)
        respBag = self.player.mergeRespBag(respBag, {"equips": _resp_equip})
        #修改状态
        self.player.guild.exList[id] = (exId, 1)
        self.player.guild.markDirty()
        #抛事件
        if itemRes:
            self.player.safe_pub(msg_define.MSG_GUILD_EXCHANGE, itemRes.quality)
        # 打包返回信息
        dUpdate = self.player.packRespBag(respBag)
        dUpdate["guildInfo"] = {
            "scene": {
                "exList": self.player.guild.to_exchange_data()
            }
        }
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp

    # 帮会兑换免费刷新(guildFreeExRef)
    # 请求
    # 返回
    #     主动推送刷新(allUpdate, json)
    #         游戏模型 - 帮会信息
    #             兑换id列表(exList, [json])
    #                 兑换id(exId, int)
    #                 状态(status, int)
    #                 0 = 未兑换
    #                 1 = 已兑换
    def rc_guildFreeExRef(self):
        guildId = self.player.guild.GetGuildId()
        if not guildId:
            return 0, errcode.EC_NO_GUILD
        rpc_guild = get_rpc_guild(guildId)
        if not rpc_guild:
            return 0, errcode.EC_NOT_FOUND_GUILD
        iGuildLv = rpc_guild.GetLevel()
        guildlvRes = Game.res_mgr.res_guildlv.get(iGuildLv)
        if not guildlvRes:
            return 0, errcode.EC_NORES
        now = int(time.time())
        if now < self.player.guild.refTime:
            return 0, errcode.EC_GUILD_EX_FREE_REF_TIME_ERR
        self.player.guild.reSetRefTime()
        exList = []
        for i in range(4):
            exId = utility.Choice(guildlvRes.exchange)
            exList.append((exId, 0))
        self.player.guild.SetExList(exList)
        # 打包返回信息
        dUpdate = {}
        dUpdate["guildInfo"] = {
            "scene": {
                "refTime": self.player.guild.refTime,
                "exList": self.player.guild.to_exchange_data()
            }
        }
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp

    # 帮会兑换刷新(guildExRef)
    # 请求
    # 返回
    #     主动推送刷新(allUpdate, json)
    #         游戏模型-帮会信息
    #             兑换可刷新次数(exRefNum, int)
    #             兑换id列表(exList, [json])
    #                 兑换id(exId, int)
    #                 状态(status, int)
    #                     0=未兑换 1=已兑换
    #         游戏模型-货币
    def rc_guildExRef(self):
        guildId = self.player.guild.GetGuildId()
        if not guildId:
            return 0, errcode.EC_NO_GUILD
        rpc_guild = get_rpc_guild(guildId)
        if not rpc_guild:
            return 0, errcode.EC_NOT_FOUND_GUILD
        iGuildLv = rpc_guild.GetLevel()
        guildlvRes = Game.res_mgr.res_guildlv.get(iGuildLv)
        if not guildlvRes:
            return 0, errcode.EC_NORES
        guildRefCostRes = Game.res_mgr.res_common.get("guildRefCost")  # 帮会兑换刷新消耗
        guildRefNumRes = Game.res_mgr.res_common.get("guildRefNum")  # 帮会兑换每日可刷新次数
        if not guildRefCostRes or not guildRefNumRes:
            return 0, errcode.EC_NORES
        iTodayNum = self.player.guild.GetTodayExRefNum()
        if iTodayNum >= guildRefNumRes.i:
            return 0, errcode.EC_GUILD_EXCHANGE_REFESH_MAX
        # 扣道具
        respBag = self.player.bag.costItem(guildRefCostRes.arrayint2, constant.ITEM_COST_GUILD_EXCHANGE_REFE, wLog=True)
        if not respBag.get("rs", 0):
            return 0, errcode.EC_GUILD_EXCHANGE_REFE_NOT_ENOUGH
        iTodayNum += 1
        self.player.guild.SetTodayExRefNum(iTodayNum)
        exList = []
        for i in range(4):
            exId = utility.Choice(guildlvRes.exchange)
            exList.append((exId, 0))
        self.player.guild.SetExList(exList)
        # 打包返回信息
        dUpdate = self.player.packRespBag(respBag)
        dUpdate["guildInfo"] = {
            "scene":{
                "exRefNum": guildRefNumRes.i - iTodayNum,
                "exList": self.player.guild.to_exchange_data()
            }
        }
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp

    # 帮会活跃升级(guildActUp)
    # 请求
    # 返回
    #     主动推送刷新(allUpdate, json)
    #         游戏模型-帮会信息
    #             帮会活跃(act, json)
    #                 帮会活跃等级(actLv, int)
    #                 帮会活跃经验(actExp, int)
    #         游戏模型-货币
    #         游戏模型-角色背包-道具列表
    #         游戏模型-角色基础-战力
    #         游戏模型-角色属性
    def rc_guildActUp(self):
        guildId = self.player.guild.GetGuildId()
        if not guildId:
            return 0, errcode.EC_NO_GUILD
        iActLv = self.player.guild.GetActLv()
        actRes = Game.res_mgr.res_guildAct.get(iActLv)
        if not actRes:
            return 0, errcode.EC_NORES
        nextRes = Game.res_mgr.res_guildAct.get(iActLv + 1)
        if not nextRes:
            return 0, errcode.EC_NORES
        iActExp = self.player.guild.GetActExp()
        if iActExp < actRes.exp:
            return 0, errcode.EC_GUILD_ACT_UPGRADE_EXP_NOT_ENOUGH
        iActExp -= actRes.exp
        self.player.guild.SetActLv(iActLv + 1)
        self.player.guild.SetActExp(iActExp)

        respBag = self.player.bag.add(actRes.reward, constant.ITEM_ADD_GUILD_ACT_UPGRADE, wLog=True)
        resp_attr = []
        #删除旧属性
        self.player.attr.delAttr(actRes.attr, constant.FIGHTABILITY_TYPE_18)
        resp_attr.extend(list(actRes.attr.keys()))
        #添加新属性
        self.player.attr.addAttr(nextRes.attr, constant.FIGHTABILITY_TYPE_18)
        resp_attr.extend(list(nextRes.attr.keys()))
        # 战力重算
        self.player.attr.RecalFightAbility()
        # 打包返回信息
        resp_attr = set(resp_attr)

        dUpdate = self.player.packRespBag(respBag, fa=self.player.base.fa, roleAttr=resp_attr)
        dUpdate["guildInfo"] = {
            "act": {"actLv": self.player.guild.actLv, "actExp": self.player.guild.actExp}
        }
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp

    # 帮会今日活跃奖励领取(getGuildActReward)
    # 请求
    #     活跃任务id(id, int)
    # 返回
    #     主动推送刷新(allUpdate, json)
    #         游戏模型-帮会信息
    #             帮会活跃(act, json)
    #                 活跃每日奖励已领取列表(getList, [int])
    #                     当前任务数据
    #                     活跃任务id
    #         游戏模型-货币
    #         游戏模型-角色背包-道具列表
    # def rc_getGuildActReward(self, id):
    #     guildId = self.player.guild.GetGuildId()
    #     if not guildId:
    #         return 0, errcode.EC_NO_GUILD
    #     todayActGetList = self.player.guild.GetTodayActGetList()
    #     if id in todayActGetList:
    #         return 0, errcode.EC_GUILD_ACT_TASK_REWARD_HAS_GET
    #     taskRes = Game.res_mgr.res_task.get(id)
    #     if not taskRes:
    #         return 0, errcode.EC_NORES
    #     taskobj = self.player.task.guild_act_reward_tasks.get(id)
    #     if not taskobj:
    #         return 0, errcode.EC_GUILD_ACT_TASK_NOT_FIND
    #     if not taskobj.finish:
    #         return 0, errcode.EC_GUILD_ACT_TASK_NOT_FINISH
    #     if taskobj.GetGetReward():
    #         return 0, errcode.EC_GUILD_ACT_TASK_REWARD_HAS_GET
    #     taskobj.SetGetReward(1)
    #     todayActGetList.append(id)
    #     self.player.guild.SetTodayActGetList(todayActGetList)
    #     #发放奖励
    #     respBag = self.player.bag.add(taskRes.finishReward, constant.ITEM_ADD_GUILD_ACT_TASK, wLog=True)
    #     #统计次数
    #     actRewardNum = self.player.guild.GetActRewardNum()
    #     self.player.guild.SetActRewardNum(actRewardNum+1)
    #     # 抛事件
    #     self.player.safe_pub(msg_define.MSG_GET_GUILD_ACT_REWARD)
    #     #打包返回信息
    #     dUpdate = self.player.packRespBag(respBag)
    #     dUpdate["guildInfo"] = {
    #         "act": {"getList": todayActGetList}
    #     }
    #     resp = {
    #         "allUpdate": dUpdate,
    #     }
    #     return 1, resp

    # 帮会捐献(guildDonate)
    # 请求
    #     道具id(id, string)
    #     数量(num, int)
    # 返回
    #     主动推送刷新(allUpdate, json)
    #         游戏模型-角色背包-道具列表
    #     帮会资金(exp, int)
    def rc_guildDonate(self, id, num):
        guildId = self.player.guild.GetGuildId()
        if not guildId:
            return 0, errcode.EC_NO_GUILD
        rpc_guild = get_rpc_guild(guildId)
        if not rpc_guild:
            return 0, errcode.EC_NOT_FOUND_GUILD
        itemRes = Game.res_mgr.res_item.get(id)
        if not itemRes:
            return 0, errcode.EC_NORES
        dCost = {id: num}
        # 扣道具
        respBag = self.player.bag.costItem(dCost, constant.ITEM_COST_GUILD_DONATE, wLog=True)
        if not respBag.get("rs", 0):
            return 0, errcode.EC_GUILD_DONATE_NOT_ENOUGH
        iAddExp = int(itemRes.arg1)*num
        exp, level = rpc_guild.addExp(iAddExp)
        # 打包返回信息
        dUpdate = self.player.packRespBag(respBag)
        resp = {
            "allUpdate": dUpdate,
            "exp": exp,
            "level": level,
        }
        return 1, resp

    # 帮会技能升级(guildSkillUp)
    # 请求
    # 返回
    #     主动推送刷新(allUpdate, json)
    #         游戏模型-帮会信息
    #             帮会技能列表(skill, [json])
    #                 部位(pos, int)
    #                 等级(lv, int)
    #         游戏模型-货币
    #         游戏模型-角色基础-战力
    #         游戏模型-角色属性
    def rc_guildSkillUp(self):
        guildId = self.player.guild.GetGuildId()
        if not guildId:
            return 0, errcode.EC_NO_GUILD
        rpc_guild = get_rpc_guild(guildId)
        if not rpc_guild:
            return 0, errcode.EC_NOT_FOUND_GUILD
        iGuildLv = rpc_guild.GetLevel()
        guildlvRes = Game.res_mgr.res_guildlv.get(iGuildLv)
        if not guildlvRes:
            return 0, errcode.EC_NORES
        minPos = 0
        minLv = 0
        for pos in constant.ALL_GUILD_SKILL:
            if not minPos:
                minPos = pos
                minLv = self.player.guild.GetSkillLv(pos)
            else:
                if self.player.guild.GetSkillLv(pos) < minLv:
                    minPos = pos
                    minLv = self.player.guild.GetSkillLv(pos)
        if minLv >= guildlvRes.skillMax:
            return 0, errcode.EC_GUILD_SKILL_UP_LIMIT
        key = (minPos, minLv)
        guildSkillRes = Game.res_mgr.res_poslv_guildSkill.get(key)
        if not guildSkillRes:
            return 0, errcode.EC_NORES
        nextKey = (minPos, minLv+1)
        nextRes = Game.res_mgr.res_poslv_guildSkill.get(nextKey)
        if not nextRes:
            return 0, errcode.EC_NORES
        # 扣道具
        respBag = self.player.bag.costItem(guildSkillRes.cost, constant.ITEM_COST_GUILD_SKULL_UP, wLog=True)
        if not respBag.get("rs", 0):
            return 0, errcode.EC_GUILD_SKILL_UP_NOT_ENOUGH
        #修改等级
        self.player.guild.SetSkillLv(minPos, minLv+1)
        resp_attr = []
        # 删除旧属性
        self.player.attr.delAttr(guildSkillRes.attr, constant.FIGHTABILITY_TYPE_18)
        resp_attr.extend(list(guildSkillRes.attr.keys()))
        # 添加新属性
        self.player.attr.addAttr(nextRes.attr, constant.FIGHTABILITY_TYPE_18)
        resp_attr.extend(list(nextRes.attr.keys()))
        # 战力重算
        self.player.attr.RecalFightAbility()
        #统计次数
        skillUpNum = self.player.guild.GetSkillUpNum()
        self.player.guild.SetSkillUpNum(skillUpNum+1)
        # 抛事件
        self.player.safe_pub(msg_define.MSG_GUILD_SKILL_UPGRADE)

        # 打包返回信息
        dUpdate = self.player.packRespBag(respBag, fa=self.player.base.fa, roleAttr=set(resp_attr))
        dUpdate["guildInfo"] = {
            "skill": self.player.guild.to_skill_data()
        }
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp


    # 帮会副本挑战(guildBarrChallenge)
    # 请求
    #     帮会副本配置表id(id, int)
    #     队伍id(teamId, int)
    # 返回
    # 全队推送(guildBarrChallengeNotice)只推送真人，机器人过滤
    #     帮会副本配置表id(id, int)
    #     战报(fightLog, json)
    #     主动推送刷新(allUpdate, json)
    #         游戏模型-货币
    #         游戏模型-角色基础-经验
    #         游戏模型-角色背包
    #         游戏模型-帮会信息
    #             帮会副本(barr, json)
    #                 已协助次数(helpNum, int)
    #                 已挑战次数(fightNum, int)
    #                 已首通帮会id列表(firstKill, [int])
    def rc_guildBarrChallenge(self, id, teamId):
        guildId = self.player.guild.GetGuildId()
        if not guildId:
            return 0, errcode.EC_NO_GUILD
        resGuidlBarr = Game.res_mgr.res_guildBarr.get(id)
        if not resGuidlBarr:
            return 0, errcode.EC_NORES
        barrRes = Game.res_mgr.res_barrier.get(resGuidlBarr.barrId)
        if not barrRes:
            return 0, errcode.EC_NORES
        rpc_guild = get_rpc_guild(guildId)
        if not rpc_guild:
            return 0, errcode.EC_NOT_FOUND_GUILD
        iGuildLv = rpc_guild.GetLevel()
        if iGuildLv < resGuidlBarr.lv:
            return 0, errcode.EC_GUILD_BARR_LIMIT

        members = Game.rpc_team_mgr.GetTeamInfo(teamId)
        if not members:
            return 0, errcode.EC_TEAM_ERROR
        from game.mgr.player import get_rpc_player
        players = [(None, 1), (None, 1)]
        index = 0
        names = []
        for one in members:
            pid = one.get("rid", 0)
            if not pid:
                continue
            names.append(one.get("name", ""))
            if pid == self.player.id:
                if not one.get("main", 0):
                    return 0, errcode.EC_TEAM_NOT_MAIN
                else:
                    continue
            rpc_player = get_rpc_player(pid)
            if not rpc_player:
                continue
            players[index] = (rpc_player, one.get("isRobot", 1))
            index += 1
        fightobj = Game.fight_mgr.createFight(constant.FIGHT_TYPE_140)
        rs = fightobj.init_by_barrId(resGuidlBarr.barrId, player1=self.player, player2=players[0][0], player3=players[1][0])
        if not rs:
            return 0, errcode.EC_INIT_BARR_FAIL
        fightLog = fightobj.doFight()
        self.player.sendGuildBarrChallengeNotice(id, fightLog, self.player.id)

        pps=[]
        if players[0][0]:
            pps.extend(players[0][0].GetPetIDs())
        if players[1][0]:
            pps.extend(players[1][0].GetPetIDs())
        
        self.player.PostPartnerPets(pps,constant.FIGHT_TYPE_140)

        if players[0][0] and not players[0][1]:
            pps=self.player.GetPetIDs()
            if players[1][0]:
                pps.extend(players[1][0].GetPetIDs())
            players[0][0].PostPartnerPets(pps,constant.FIGHT_TYPE_140)

        if players[1][0] and not players[1][1]:
            pps=self.player.GetPetIDs()
            pps.extend(players[0][0].GetPetIDs())
            players[1][0].PostPartnerPets(pps,constant.FIGHT_TYPE_140)

        # 机器人不推送
        for playerData in players:
            if playerData[1]:
                continue
            playerData[0].sendGuildBarrChallengeNotice(id, fightLog, self.player.id, _no_result=True)
        # 解散队伍
        Game.rpc_team_mgr.DeleteTeam(teamId)
        # 抛事件
        self.player.safe_pub(msg_define.MSG_GUILD_BARR)
        return 1, None







