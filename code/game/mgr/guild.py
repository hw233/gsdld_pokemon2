#!/usr/bin/env python
# -*- coding:utf-8 -*-
import time
import random

from gevent import sleep
from game.common import utility
from grpc import DictExport, DictItemProxy, get_proxy_by_addr
from corelib import log, spawn

from corelib.frame import Game, MSG_FRAME_STOP
from game.models.guild import ModelGuild
from game.core.cycleData import CycleDay

from game.define import constant, errcode

def get_rpc_guild(guildId):
    rs = Game.rpc_guild_mgr.init_guild(guildId)
    if not rs:
        return
    addr = Game.rpc_guild_mgr.get_addr()
    proxy = get_proxy_by_addr(addr, GuildMgr._rpc_name_, DictItemProxy)
    proxy.dict_name = 'alls'
    proxy.key = guildId
    return proxy

class GuildMgr(DictExport):
    """公会管理器"""
    _rpc_name_ = 'rpc_guild_mgr'

    def __init__(self):
        self.alls = {}  # {gid: guild}

        Game.sub(MSG_FRAME_STOP, self._frame_stop)

        self._loop_task = None

    def printGuildMemory(self):
        import sys
        size_alls = sys.getsizeof(self.alls)
        Game.glog.log2File("GuildMemory", "%s|%s\n" % (len(self.alls), size_alls))

    def start(self):
        self._loop_task = spawn(self._saveLoop)

        table_name, key_name = Game.store.store.cls_infos[ModelGuild.TABLE_NAME][:2]
        table = Game.store.store.get_table(table_name)
        # 起服的时候先加载 20个帮会进来填充
        for one in table.aggregate([{"$sample":{"size": 20}}]):
            guildId = one.get("_id", 0)
            self.init_guild(guildId)

    def _frame_stop(self):
        if self._loop_task:
            self._loop_task.kill(block=False)
            self._loop_task = None

        for guild in self.alls.values():
            if not guild:
                continue
            try:
                guild.save(forced=True, no_let=True)
            except:
                log.log_except()

    def _saveLoop(self):
        stime = 5 * 60
        while True:
            sleep(stime)
            for guild in self.alls.values():
                if not guild:
                    continue
                try:
                    guild.save()
                    sleep()
                except:
                    log.log_except()

    def init_guild(self, guildId):
        if guildId in self.alls:
            return True
        guild = Guild(guildId)
        rs = guild.load()
        if rs:
            self.alls[guildId] = guild
        return rs

    def deleteGuild(self, guildId):
        obj = self.alls.pop(guildId, None)
        if obj:
            obj.deleteGuild()

    def CreateGuild(self, name, lv, playerInfo):
        """创建公会"""
        playerInfo["job"] = constant.GUILD_MEMBER_TYPE_1 #1 = 帮主 2 = 副帮主 3 = 成员
        dataDict = Guild.to_create_dict(name, lv, playerInfo)
        data = dict(name=name, dataDict=dataDict)
        try:
            guildId = Game.store.insert(Guild.DATA_CLS.TABLE_NAME, data)
        except:
            return 0, errcode.EC_GUILD_CREATE_FAIL
        guild = Guild(guildId)
        guild.data = guild.DATA_CLS()
        guild.data.setOwner(guild)
        dataDict["id"] = guildId
        guild.load_from_dict(dataDict)
        self.alls[guildId] = guild
        return 1, guildId

    def getGuildList(self, pid):
        resp = []
        keys = list(self.alls.keys())
        iLen = len(keys)
        if iLen > 20:
            iLen = 20
        keys = random.sample(keys, iLen)
        for guildId in keys:
            guildobj = self.alls.get(guildId)
            data = guildobj.to_show_dict()
            applyDict = guildobj.GetApplyDict()
            data["status"] = 1 if pid in applyDict else 0
            resp.append(data)
        return resp

    def receive_gongcheng(self, data):
        atkWin = data.get("AtkWin", [])
        for one in atkWin:
            guildId = one.get("ATKghid", 0)
            guildobj = self.alls.get(guildId)
            if guildobj:
                guildobj = Guild(guildId)
                rs = guildobj.load()
                if rs:
                    guildobj.broadcast_gongcheng_atkwin()

        defWin = data.get("DefWin", [])
        for one in defWin:
            guildId = one.get("DEFghid", 0)
            guildobj = self.alls.get(guildId)
            if guildobj:
                guildobj = Guild(guildId)
                rs = guildobj.load()
                if rs:
                    guildobj.broadcast_gongcheng_defwin()

class Guild(utility.DirtyFlag):
    """公会"""
    DATA_CLS = ModelGuild

    @staticmethod
    def to_create_dict(name, lv, playerInfo):
        dataDict = {
            "name": name,
            "level": lv,
            "masterId": playerInfo.get("rid", 0),
            "masterName": playerInfo.get("name", ''),
            "members": [playerInfo],
        }
        return dataDict

    def __init__(self, guildId):
        utility.DirtyFlag.__init__(self)
        self.id = guildId #帮会id
        self.name = "" #帮会名称
        self.color = 0 #颜色
        self.mainCity = 0 #主城
        self.level = 0 #帮会等级
        self.exp = 0  # 帮会资金
        self.masterId = 0 #帮主id
        self.masterName = "" #帮主名称
        self.notice = "" #帮会公告
        self.members = {} #帮会成员 {pid:info}
        self.autoEnter = 0 # 是否自动入帮(autoEnter, int)
        self.autoFa = 0 # 自动入帮战力(autoFa, int)
        self.logs = [] #帮会记录(time, name, type)

        self.cycleDay = CycleDay(self)  # 天周期数据

        #帮会boss
        self.bossHp = 0

        self.data = None
        self.save_cache = {}  # 存储缓存

    def getName(self):
        return self.name

    def getColor(self):
        
        if 0==self.color:
            self.color=1
        
        return self.color

    def addLog(self, args, logType):
        now = int(time.time())
        guildLog = (now, args, logType)
        self.logs.append(guildLog)  # 1=加入帮会 2=退出帮会 3=被踢 4=升职 5=降职 6=禅让
        self.logs = self.logs[:20]

    def addExp(self, add):
        self.exp += add
        #判断是否升级
        guildlvRes = Game.res_mgr.res_guildlv.get(self.level)
        nextRes = Game.res_mgr.res_guildlv.get(self.level+1)
        if nextRes and guildlvRes and self.exp >= guildlvRes.fund:
            self.exp -=  guildlvRes.fund
            self.level += 1
        self.markDirty()
        return self.exp, self.level

    def GetLevel(self):
        return self.level

    def SetName(self, name):
        self.name = name
        self.markDirty()

    def SetColor(self, color):
        self.color = color
        self.markDirty()

    def SetNotice(self, notice):
        self.notice = notice
        self.markDirty()

    # 申请列表 {pid:info}  每日清理
    def GetApplyDict(self):
        return self.cycleDay.Query("guildApplyDict", {})

    def SetApplyDict(self, applyDict):
        self.cycleDay.Set("guildApplyDict", applyDict)

    # 帮会上香日志 每日清理
    def GetSXLogs(self):
        return self.cycleDay.Query("guildSXLogs", [])

    def SetSXLogs(self, logs):
        self.cycleDay.Set("guildSXLogs", logs)

    #帮会香火值进度 每日清0
    def GetSXProgress(self):
        return self.cycleDay.Query("guildSXProgress", 0)

    def SetSXProgress(self, num):
        self.cycleDay.Set("guildSXProgress", num)

    #帮会上香次数 每日清0
    def GetSXNum(self):
        return self.cycleDay.Query("guildSXNum", 0)

    def SetSXNum(self, num):
        self.cycleDay.Set("guildSXNum", num)

    def markDirty(self):
        utility.DirtyFlag.markDirty(self)
        self.data.modify()

    def to_save_dict(self, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            self.save_cache = {}
            self.save_cache["id"] = self.id
            self.save_cache["name"] = self.name
            self.save_cache["color"] = self.color
            self.save_cache["mainCity"] = self.mainCity
            self.save_cache["level"] = self.level
            self.save_cache["exp"] = self.exp
            self.save_cache["masterId"] = self.masterId
            self.save_cache["masterName"] = self.masterName
            self.save_cache["notice"] = self.notice
            self.save_cache["autoEnter"] = self.autoEnter
            self.save_cache["autoFa"] = self.autoFa
            self.save_cache["logs"] = self.logs

            self.save_cache["members"] = []
            for member in self.members.values():
                self.save_cache["members"].append(member.to_save_dict())

            self.save_cache['clcleDayBytes'] = self.cycleDay.to_save_bytes()  # 天周期数据

        return self.save_cache

    def load_from_dict(self, data):
        self.id = data.get("id", 0)  # 帮会id
        self.name = data.get("name", "")  # 帮会名称
        self.color = data.get("color", 0)  # color
        self.mainCity = data.get("mainCity", 0)  # mainCity
        self.level = data.get("level", 0)  # 帮会等级
        self.exp = data.get("exp", 0)  # 帮会资金
        self.masterId = data.get("masterId", 0)  # 帮主id
        self.masterName = data.get("masterName", "")  # 帮主名称
        self.notice = data.get("notice", "")  # 帮会公告
        self.autoEnter = data.get("autoEnter", 0)  # 是否自动入帮(autoEnter, int)
        self.autoFa = data.get("autoFa", 0)  # 自动入帮战力(autoFa, int)
        self.logs = data.get("logs", [])  # 帮会记录(time, name, type)

        members = data.get("members", [])
        for one in members:
            member = GuildMember(self, one)
            self.members[member.pid] = member  # 帮会成员 {pid:info}

    def save(self, forced=False, no_let=False):
        self.data.save(Game.store, forced=forced, no_let=no_let)

    def load(self):
        self.data = self.DATA_CLS.load(Game.store, self.id)
        if not self.data:
            return False
        else:
            self.load_from_dict(self.data.to_init_dict())
            self.cycleDay.load_from_dict(self.data.clcleDayBytes)
        self.data.setOwner(self)
        return True

    def deleteGuild(self):
        self.data.delete(Game.store)

    def to_openUI_dict(self):
        resp = {}
        resp["id"] = self.id
        resp["notice"] = self.notice
        resp["bzName"] = self.masterName
        resp["exp"] = self.exp
        resp["num"] = len(self.members)
        return resp

    def to_show_dict(self):
        resp = {}
        resp["guildId"] = self.id
        resp["name"] = self.name
        resp["color"] = self.color
        resp["mainCity"] = self.mainCity
        resp["bzName"] = self.masterName
        resp["guildLv"] = self.level
        resp["num"] = len(self.members)
        resp["fa"] = self.autoFa
        return resp

    def update_playerInfo(self, playerInfo):
        pid = playerInfo.get("rid", 0)
        member = self.members.get(pid)
        if member:
            member.update_playerInfo(playerInfo)
        #做帮主选举检测
        self.choiceMaster()

    # 让位
    # 1）帮主3天（配置吧）不上线
    # 会让位给在线的副帮主（战力最高的）
    # 如果都不在线，则让给最近一次上线的副帮主
    #
    # 如果没有副帮主，让给在线战力最高的玩家
    # 如果都不在线，则让给最近一次上线的玩家
    def choiceMaster(self):
        oldmaster = self.members.get(self.masterId)
        if oldmaster.time <= 0:
            return

        iChoice = 0
        now = int(time.time())
        if now - oldmaster.time >= 3600*24*2:
            iChoice = 1
        if not iChoice:
            return
        #重新选举
        newmaster = None
        deputy = None
        normal = None
        for member in self.members.values():
            if member.GetJob == constant.GUILD_MEMBER_TYPE_1:
                newmaster = member
            elif member.GetJob == constant.GUILD_MEMBER_TYPE_2:
                if not deputy:
                    deputy = member
                else:
                    if deputy.time == 0 and member.time == 0:
                        deputy = deputy if deputy.fa >= member.fa else member
                    else:
                        if member.time == 0:
                            deputy = member
                        else:
                            deputy = deputy if deputy.time >= member.time else member
            else:
                if not normal:
                    normal = member
                else:
                    if normal.time == 0 and member.time == 0:
                        normal = normal if normal.fa >= member.fa else member
                    if member.time == 0:
                        normal = member
                    else:
                        normal = normal if normal.time >= member.time else member
        if deputy:
            newmaster = deputy
        else:
            if normal:
                newmaster = normal

        oldmaster.SetJob(constant.GUILD_MEMBER_TYPE_3)
        newmaster.SetJob(constant.GUILD_MEMBER_TYPE_1)

        self.masterId = newmaster.pid
        self.masterName = newmaster.name
        self.markDirty()

    def exitGuild(self, pid):
        # 2）帮主需要让位才出可以退出帮会
        member = self.members.get(pid)
        if not member:
            return 0, errcode.EC_NO_GUILD
        if len(self.members) > 1:
            if member.GetJob == constant.GUILD_MEMBER_TYPE_1:
                return 0, errcode.EC_GUILD_MASTER_EXIT
        self.members.pop(pid)
        if len(self.members) <= 0:
            Game.rpc_guild_mgr.deleteGuild(self.id)
        # 记录帮会日志
        self.addLog((member.name,), constant.GUILD_LOG_TYPE_2)
        self.markDirty()
        return 1, None


    def GetGiveupCity(self):
        return self.cycleDay.Query("GiveupCity", 0)

    def SetGiveupCity(self):
        self.cycleDay.Set("GiveupCity", self.GetGiveupCity()+1)

    def GetWarCity(self):
        return self.cycleDay.Query("WarCity", 0)

    def SetWarCity(self):
        self.cycleDay.Set("WarCity", self.GetWarCity()+1)

    #玩家登陆要下发的数据
    def to_init_data(self, pid):
        init_data = {}
        init_data["guildId"] = self.id
        init_data["name"] = self.name
        init_data["color"] = self.color
        init_data["mainCity"] = self.mainCity
        init_data["lv"] = self.level
        member = self.members.get(pid)
        if member:
            red = 1 if member.GetJob() != constant.GUILD_MEMBER_TYPE_3 and len(self.GetApplyDict()) else 0
            job = member.GetJob()
            bgCoin = member.GetBgCoin()
        else:
            red = 0
            job = constant.GUILD_MEMBER_TYPE_3
            bgCoin = 0
        init_data["red"] = red
        init_data["job"] = job
        init_data["bgCoin"] = bgCoin
        init_data["sxBar"] = self.GetSXProgress()
        init_data["sxNum"] = self.GetSXNum()
        init_data["GiveupCity"] = self.GetGiveupCity()
        init_data["WarCity"] = self.GetWarCity()
        return init_data

    #申请加入帮会 0=取消 1=申请
    def enterGuild(self, type, playerInfo):
        guildlvRes = Game.res_mgr.res_guildlv.get(self.level)
        if not guildlvRes:
            return 0, errcode.EC_NORES
        if len(self.members) >= guildlvRes.peoplenum:
            return 0, errcode.EC_GUILD_MEMBER_MAX
        pid = playerInfo.get("rid", 0)
        applyDict = self.GetApplyDict()
        if type == 1:
            if pid in applyDict:
                return 0, errcode.EC_GUILD_HAS_APPLY
            # 如果有设置 自动入帮战力，自动入帮
            fa = playerInfo.get("fa", 0)
            if self.autoEnter and fa >= self.autoFa:
                self.addMember(playerInfo)
                from game.mgr.player import get_rpc_player
                rpc_player = get_rpc_player(pid)
                rpc_player.sendEnterGuild(self.id, _no_result=1)
            else:
                applyDict[pid] = playerInfo
                self.SetApplyDict(applyDict)
                self.markDirty()
                # 推送给帮会管理
                guildInfo = {"red": 1}
                from game.mgr.player import get_rpc_player
                for member in self.members.values():
                    if member.GetJob() != constant.GUILD_MEMBER_TYPE_3 and member.time == 0:
                        rpc_player = get_rpc_player(member.pid, offline=False)
                        if rpc_player:
                            rpc_player.sendGuildRed(guildInfo, _no_result=1)
        else:
            if pid not in applyDict:
                return 0, errcode.EC_GUILD_NOT_APPLY
            applyDict.pop(pid)
            self.SetApplyDict(applyDict)
            self.markDirty()
        return 1, None

    def addMember(self, playerInfo):
        member = GuildMember(self, playerInfo)
        self.members[member.pid] = member  # 帮会成员 {pid:info}
        member.SetJob(constant.GUILD_MEMBER_TYPE_3) #成员
        #记录帮会日志
        name = playerInfo.get("name", "")
        self.addLog((name,), constant.GUILD_LOG_TYPE_1)
        self.markDirty()

    def respGuild(self, myId, pid, type):
        member = self.members.get(myId)
        if not member:
            return 0, errcode.EC_NO_GUILD
        if member.GetJob() == constant.GUILD_MEMBER_TYPE_3:
            return 0, errcode.EC_GUILD_OPER_LIMIT
        applyDict = self.GetApplyDict()
        if pid not in applyDict:
            return 0, errcode.EC_GUILD_NOT_APPLY
        playerInfo = applyDict.pop(pid)
        self.SetApplyDict(applyDict)
        if type == 1:
            guildlvRes = Game.res_mgr.res_guildlv.get(self.level)
            if not guildlvRes:
                return 0, errcode.EC_NORES
            #人数满员
            if len(self.members) >= guildlvRes.peoplenum:
                return 0, errcode.EC_GUILD_MEMBER_MAX
            #已经加入公会
            from game.mgr.player import get_rpc_player
            rpc_player = get_rpc_player(pid)
            if rpc_player.isInGuild():
                return 0, errcode.EC_GUILD_HAS_JOIN

            self.addMember(playerInfo)
            rpc_player.sendEnterGuild(self.id, _no_result=1)
            # 推送给帮会管理
            guildInfo = {"red": 1 if len(self.GetApplyDict()) else 0}
            for member in self.members.values():
                if member.GetJob() != constant.GUILD_MEMBER_TYPE_3 and member.time == 0:
                    rpc_player = get_rpc_player(member.pid, offline=False)
                    if rpc_player:
                        rpc_player.sendGuildRed(guildInfo, _no_result=1)

        self.markDirty()
        return 1, len(self.members)

    def guildOper(self, myId, pid, type):
        # 1=禅让 2=升职 3=降职 4=踢出
        if type not in (constant.GUILD_OPER_TYPE_1, constant.GUILD_OPER_TYPE_2,
                        constant.GUILD_OPER_TYPE_3, constant.GUILD_OPER_TYPE_4):
            return 0, errcode.EC_GUILD_OPER_LIMIT
        my = self.members.get(myId)
        member = self.members.get(pid)
        if not my or not member:
            return 0, errcode.EC_NO_GUILD
        if my.GetJob() == constant.GUILD_MEMBER_TYPE_3:
            return 0, errcode.EC_GUILD_OPER_LIMIT
        if type in (constant.GUILD_OPER_TYPE_1, constant.GUILD_OPER_TYPE_2, constant.GUILD_OPER_TYPE_3)\
                and my.GetJob() != constant.GUILD_MEMBER_TYPE_1:
            return 0, errcode.EC_GUILD_OPER_LIMIT
        if type == constant.GUILD_OPER_TYPE_4 and my.GetJob() not in (constant.GUILD_MEMBER_TYPE_1, constant.GUILD_MEMBER_TYPE_2):
            return 0, errcode.EC_GUILD_OPER_LIMIT
        if type == constant.GUILD_OPER_TYPE_4 and member.GetJob() != constant.GUILD_MEMBER_TYPE_3:
            return 0, errcode.EC_GUILD_OPER_LIMIT
        if type == constant.GUILD_OPER_TYPE_2:
            guildlvRes = Game.res_mgr.res_guildlv.get(self.level)
            if not guildlvRes:
                return 0, errcode.EC_NORES
            #副帮主人数限制
            iNum = 0
            for one in self.members.values():
                if one.GetJob() == constant.GUILD_MEMBER_TYPE_2:
                    iNum += 1
            if iNum >= guildlvRes.deputybossnum:
                return 0, errcode.EC_GUILD_DEPUTY_MAX_NUM

        logType = 0
        # 1=禅让
        if type == constant.GUILD_OPER_TYPE_1:
            self.masterId = member.pid
            self.masterName = member.name
            my.SetJob(constant.GUILD_MEMBER_TYPE_3)
            member.SetJob(constant.GUILD_MEMBER_TYPE_1)
            logType = constant.GUILD_LOG_TYPE_6
        elif type == constant.GUILD_OPER_TYPE_2: #2=升职
            member.SetJob(constant.GUILD_MEMBER_TYPE_2)
            logType = constant.GUILD_LOG_TYPE_4
        elif type == constant.GUILD_OPER_TYPE_3: #3=降职
            member.SetJob(constant.GUILD_MEMBER_TYPE_3)
            logType = constant.GUILD_LOG_TYPE_5
        elif type == constant.GUILD_OPER_TYPE_4: #4=踢出
            self.members.pop(pid)
            logType = constant.GUILD_LOG_TYPE_3
        #同步
        guildInfo = {}
        guildInfo["red"] = 1 if member.GetJob() != constant.GUILD_MEMBER_TYPE_3 and len(self.GetApplyDict()) else 0
        guildInfo["job"] = member.GetJob()
        from game.mgr.player import get_rpc_player
        rpc_player = get_rpc_player(pid)
        rpc_player.sendGuildOperPush(type, guildInfo, _no_result=1)
        if type == constant.GUILD_OPER_TYPE_1:
            myGuildInfo = {}
            myGuildInfo["red"] = 1 if my.GetJob() != constant.GUILD_MEMBER_TYPE_3 and len(self.GetApplyDict()) else 0
            myGuildInfo["job"] = my.GetJob()
            from game.mgr.player import get_rpc_player
            my_rpc_player = get_rpc_player(myId)
            my_rpc_player.sendGuildOperPush(type, myGuildInfo, _no_result=1)
        # 记录帮会日志
        if logType:
            if logType == constant.GUILD_LOG_TYPE_3:
                self.addLog((member.name, my.name), logType)
            else:
                self.addLog((member.name,), logType)
        self.markDirty()
        return 1, len(self.members)

    def changeName(self, pid, name):
        member = self.members.get(pid)
        if member.GetJob() != constant.GUILD_MEMBER_TYPE_1:
            return 0, errcode.EC_GUILD_OPER_LIMIT

        self.SetName(name)
        return 1, None

    def GiveupCity(self):
        # member = self.members.get(pid)
        # if member.GetJob() != constant.GUILD_MEMBER_TYPE_1:
        #     return 0, errcode.EC_GUILD_OPER_LIMIT

        self.SetGiveupCity()
        return 1, None

    def WarCity(self):
        # member = self.members.get(pid)
        # if member.GetJob() != constant.GUILD_MEMBER_TYPE_1:
        #     return 0, errcode.EC_GUILD_OPER_LIMIT

        self.SetWarCity()
        return 1, None

    def changeColor(self, pid, color):
        member = self.members.get(pid)
        if member.GetJob() != constant.GUILD_MEMBER_TYPE_1:
            return 0, errcode.EC_GUILD_OPER_LIMIT

        self.SetColor(color)
        return 1, None

    def fixNotice(self, pid, notice):
        member = self.members.get(pid)
        if member.GetJob() != constant.GUILD_MEMBER_TYPE_1:
            return 0, errcode.EC_GUILD_OPER_LIMIT
        self.SetNotice(notice)
        return 1, None

    def Add_BgCoin(self, pid, num):
        member = self.members.get(pid)
        if not member:
            return
        bgCoin = member.GetBgCoin()
        bgCoin += num
        member.SetBgCoin(bgCoin)

    def getLogs(self):
        return self.logs

    def getMembers(self):
        resp = []
        for member in self.members.values():
            resp.append(member.to_save_dict())
        return resp

    def getApplyData(self):
        applyDict = self.GetApplyDict()
        resp = {
            "enterList": list(applyDict.values()),
            "autoEnter": self.autoEnter,
            "autoFa": self.autoFa,
        }
        return resp

    def fixAutoEnter(self, pid, autoEnter, autoFa):
        member = self.members.get(pid)
        if member.GetJob() != constant.GUILD_MEMBER_TYPE_1:
            return 0, errcode.EC_GUILD_OPER_LIMIT
        self.autoEnter = autoEnter
        self.autoFa = autoFa
        self.markDirty()
        return 1, None

    def getSxList(self):
        return self.GetSXLogs()

    def guildSx(self, pid, sxId):
        member = self.members.get(pid)
        if not member:
            return 0, errcode.EC_NO_GUILD
        guildlvRes = Game.res_mgr.res_guildlv.get(self.level)
        if not guildlvRes:
            return 0, errcode.EC_NORES
        sxRes = Game.res_mgr.res_guildSx.get(sxId)
        if not sxRes:
            return 0, errcode.EC_NORES
        iSxNum = self.GetSXNum()
        if iSxNum >= guildlvRes.guildSxNum:
            return 0, errcode.EC_GUILD_SX_MAX_NUM
        #增加上香次数
        iSxNum += 1
        self.SetSXNum(iSxNum)
        #增加香火值
        iProgress = self.GetSXProgress()
        iProgress += sxRes.addNum
        if iProgress > guildlvRes.sxMaxNum:
            iProgress = guildlvRes.sxMaxNum
        self.SetSXProgress(iProgress)
        #增加帮会资金
        self.addExp(sxRes.addExp)
        #上香日志
        logs = self.GetSXLogs()
        now = int(time.time())
        logs.append({"time":now, "name":member.name, "id":sxId})
        self.SetSXLogs(logs)
        self.markDirty()
        #同步所有人香火值
        from game.mgr.player import get_rpc_player
        guildInfo = {
            "sxBar": iProgress,
            "sxNum": iSxNum,
        }
        for pid, member in self.members.items():
            if member.time:
                continue
            rpc_player = get_rpc_player(pid)
            if rpc_player:
                rpc_player.sendGuildSxPush(guildInfo, _no_result=1)
        return 1, (iProgress, iSxNum)

    def GetSxInfo(self):
        resp = {
            "sxNum": self.GetSXNum(),
            "sxBar": self.GetSXProgress(),
        }
        return resp

    def enterGuildScene(self):
        keys = list(self.members.keys())
        iLen = len(keys)
        if iLen > 3:
            iLen = 3
        keys = random.sample(keys, iLen)
        return keys

    def broadcast_gongcheng_atkwin(self):
        from game.mgr.player import get_rpc_player
        for pid in self.members.keys():
            rpc_player = get_rpc_player(pid)
            if rpc_player:
                rpc_player.broadcast_gongcheng_atkwin(_no_result=1)

    def broadcast_gongcheng_defwin(self):
        from game.mgr.player import get_rpc_player
        for pid in self.members.keys():
            rpc_player = get_rpc_player(pid)
            if rpc_player:
                rpc_player.broadcast_gongcheng_defwin(_no_result=1)

class GuildMember(utility.DirtyFlag):
    """公会成员"""
    def __init__(self, owner, data):
        utility.DirtyFlag.__init__(self)
        self.owner = owner  # 拥有者
        self.pid = 0 # 角色id(rid, int)
        self.name = "" # 角色名字(name, string)
        self.fa = 0 # 战力(fa, int)
        self.time = 0 # 最后一次离线时间戳(time, int) 0 = 在线
        self.sex = 0 # 性别(sex, int)0 =? 1 = 男 2 = 女
        self.portrait = 0 #
        self.headframe = 0 # 
        self.job = 0 # 职位(job, int)1 = 帮主 2 = 副帮主 3 = 成员
        self.bgCoin = 0 # 对当前帮会的累计贡献(bgCoin, int)
        self.lv = 0 #等级

        self.save_cache = {}  # 存储缓存

        self.load_from_dict(data)

    def update_playerInfo(self, data):
        self.pid = data.get("rid", 0)  # 角色id(rid, int)
        self.name = data.get("name", "")  # 角色名字(name, string)
        self.fa = data.get("fa", 0)  # 战力(fa, int)
        self.time = data.get("time", 0)  # 最后一次离线时间戳(time, int) 0 = 在线
        self.sex = data.get("sex", 0)  # 性别(sex, int)0 =? 1 = 男 2 = 女
        self.portrait = data.get("portrait", 0)  # 
        self.headframe = data.get("headframe", 0)  # 
        self.lv = data.get("lv", 0) #等级
        self.markDirty()

    def GetJob(self):
        return self.job

    def SetJob(self, job):
        self.job = job
        self.markDirty()

    def GetBgCoin(self):
        return self.bgCoin

    def SetBgCoin(self, num):
        self.bgCoin = num
        self.markDirty()

    def markDirty(self):
        utility.DirtyFlag.markDirty(self)
        if self.owner:
            self.owner.markDirty()

    def to_save_dict(self, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            self.save_cache = {}
            self.save_cache["rid"] = self.pid
            self.save_cache["name"] = self.name
            self.save_cache["fa"] = self.fa
            self.save_cache["time"] = self.time
            self.save_cache["sex"] = self.sex
            self.save_cache["portrait"] = self.portrait
            self.save_cache["headframe"] = self.headframe
            self.save_cache["job"] = self.job
            self.save_cache["bgCoin"] = self.bgCoin
            self.save_cache["lv"] = self.lv
        return self.save_cache

    def load_from_dict(self, data):
        self.pid = data.get("rid", 0) # 角色id(rid, int)
        self.name = data.get("name", "") # 角色名字(name, string)
        self.fa = data.get("fa", 0) # 战力(fa, int)
        self.time = data.get("time", 0) # 最后一次离线时间戳(time, int) 0 = 在线
        self.sex = data.get("sex", 0) # 性别(sex, int)0 =? 1 = 男 2 = 女
        self.portrait = data.get("portrait", 0) #
        self.headframe = data.get("headframe", 0) # 
        self.job = data.get("job", 0) # 职位(job, int)1 = 帮主 2 = 副帮主 3 = 成员
        self.bgCoin = data.get("bgCoin", 0) # 对当前帮会的累计贡献(bgCoin, int)
        self.lv = data.get("lv", 0)  # 等级


