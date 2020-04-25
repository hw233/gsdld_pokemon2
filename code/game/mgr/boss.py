#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import time
import datetime

from game.common import utility
from game.define import constant

from game.models.boss import ModelQmBoss, ModelYwBoss, ModelSsjBoss

from corelib.frame import Game, MSG_FRAME_STOP
from corelib import spawn, spawn_later
from gevent import sleep

class QmBossMgr(utility.DirtyFlag):
    """ 全民boss管理器"""
    _rpc_name_ = 'rpc_qmboss_mgr'
    def __init__(self):
        utility.DirtyFlag.__init__(self)
        self.data = None
        self.boss = {} #{bossid:obj}

        self.save_cache = {}  # 存储缓存

        self._loop_task = None
        Game.sub(MSG_FRAME_STOP, self._frame_stop)

    def start(self):
        self.data = ModelQmBoss.load(Game.store, ModelQmBoss.TABLE_KEY)
        if not self.data:
            self.data = ModelQmBoss()
        self.data.set_owner(self)
        self.load_from_dict(self.data.dataDict)

        self._loop_task = spawn(self._loop)

    def _frame_stop(self):
        if self._loop_task:
            self._loop_task.kill(block=False)
            self._loop_task = None
        for bossobj in self.boss.values():
            bossobj.uninit()
        self.data.save(Game.store, forced=True, no_let=True)

    def _loop(self):
        stime = 60*30
        while 1:
            sleep(stime)
            try:
                self.data.save(Game.store)
            except Exception as err:
                Game.glog.log2File("QmBossMgr_loopError", err)

    # 存库数据
    def to_save_dict(self, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            self.save_cache = {}
            self.save_cache["boss"] = []
            for bossobj in self.boss.values():
                self.save_cache["boss"].append(bossobj.to_save_dict(forced=forced))
        return self.save_cache

    # 读库数据初始化
    def load_from_dict(self, data):
        boss = data.get("boss", [])
        for one in boss:
            res = Game.res_mgr.res_qmBoss.get(one["id"], None)
            if res:
                qmboss = QmBoss(res, data=one, owner=self)
                self.boss[qmboss.id] = qmboss
            else:
                Game.glog.log2File("QmBossLoadNotFindError", "%s|%s" % (one["bossid"], one))

        #没有数据的boss从资源表初始化
        for bossid, res in Game.res_mgr.res_qmBoss.items():
            if self.boss.get(bossid):
                continue
            mstRes = Game.res_mgr.res_monster.get(res.mstId)
            if not mstRes:
                continue
            qmboss = QmBoss(res, owner=self)
            qmboss.init_hp(mstRes)
            self.boss[bossid] = qmboss

    # 	全民boss列表(bossList, [json])
    # 		全民bossid(id, int)
    # 		当前血量(curHp, int)
    # 		总血量(maxHp, int)
    # 		争夺人数(num, int)
    # 		状态(status, int)0=未击杀 1=已击杀
    # 		重生时间戳(time, int)
    def GetAllBossInfo(self):
        bossList = []
        for bossobj in self.boss.values():
            one = bossobj.to_client_info()
            bossList.append(one)

        print("qmboss:",bossList)
        return bossList

    def GetTZInfo(self, id, pid):
        bossobj = self.boss.get(id)
        if not bossobj:
            return {}
        return bossobj.GetTZInfo(pid)

    # 请求争夺人数(qmBossFighterNum)
    # 请求
    # 	全民bossid(id, int)
    # 返回
    # 	争夺列表(fighters, [json])
    # 		名次(rank, int)
    # 		玩家名称(name, string)
    # 		伤害(hurt, int)
    def GetFighterData(self, id):
        bossobj = self.boss.get(id)
        if not bossobj:
            return []
        return bossobj.GetFighterData()

    # 请求击杀列表(qmBossKillRecord)
    # 请求
    # 	全民bossid(id, int)
    # 返回
    # 	击杀列表(killList, [json])
    # 		击杀时间戳(time, int)
    # 		玩家名称(name, string)
    # 		战力(fa, int)
    def GetKillList(self, id):
        bossobj = self.boss.get(id)
        if not bossobj:
            return []
        return bossobj.GetKillList()

    def FightBoss(self, id, atkInfo, reborn=0):
        bossobj = self.boss.get(id)
        if not bossobj:
            return 0
        if not reborn and bossobj.status == 1:
            return 0
        if reborn and bossobj.status == 1:
            bossobj.reBorn()
        bossobj.beHurt(atkInfo)
        return bossobj.status

class QmBoss(utility.DirtyFlag):
    def __init__(self, res, data=None, owner=None):
        utility.DirtyFlag.__init__(self)
        self.id = res.id # 全民bossid(id, int)
        self.curHp = 0 # 当前血量(curHp, int)
        self.maxHp = 0 # 总血量(maxHp, int)
        self.status = 0 # 状态(status, int)0=未击杀 1=已击杀
        self.time = 0 # 重生时间戳(time, int)
        self.fighterData = {} # 争夺列表	{pid:玩家名称(name, int) 伤害(hurt, int) pid, fa}
        self.killList = [] # 击杀列表  玩家id(pid, int) 击杀时间戳(time, int) 玩家名称(name, string) 战力(fa, int)

        self.save_cache = {}  # 存储缓存

        self.reborn_timer = None

        if owner:
            self.set_owner(owner)
        if data:
            self.load_from_dict(data)


    def init_hp(self, mstRes):
        hp = mstRes.attr.get(constant.ATTR_HP, 0)
        self.curHp = hp
        self.maxHp = hp
        self.markDirty()

    def uninit(self):
        if self.reborn_timer:
            self.reborn_timer.kill(block=False)
            self.reborn_timer = None

    def markDirty(self):
        utility.DirtyFlag.markDirty(self)
        if self.owner:
            self.owner.markDirty()

    def set_owner(self, owner):
        self.owner = owner

    # 存库数据
    def to_save_dict(self, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            self.save_cache = {}
            self.save_cache["id"] = self.id
            self.save_cache["curHp"] = self.curHp
            self.save_cache["maxHp"] = self.maxHp
            self.save_cache["status"] = self.status
            self.save_cache["time"] = self.time
            self.save_cache["killList"] = self.killList

            self.save_cache["fighterData"] = []
            for data in self.fighterData.values():
                self.save_cache["fighterData"].append(data)
        return self.save_cache

    # 读库数据初始化
    def load_from_dict(self, data):
        self.id = data.get("id", 0) # 全民bossid(id, int)
        self.curHp = data.get("curHp", 0)  # 当前血量(curHp, int)
        self.maxHp = data.get("maxHp", 0) # 总血量(maxHp, int)
        self.status = data.get("status", 0)  # 状态(status, int)0=未击杀 1=已击杀
        self.time = data.get("time", 0) # 重生时间戳(time, int)
        self.killList = data.get("killList", [])  # 击杀列表  击杀时间戳(time, int) 玩家名称(name, string) 战力(fa, int)

        fighterData = data.get("fighterData", [])  # 争夺列表 玩家名称(name, int) 伤害(hurt, int)
        for one in fighterData:
            self.fighterData[one["pid"]] = one

        # 要对离线再回来的时间差进行处理
        if self.time:
            now = int(time.time())
            if now >= self.time:
                self.reSet()
            else:
                interval = self.time - now
                self.reborn_timer = spawn_later(interval, self.reBorn)

    def beHurt(self, atkInfo):
        """被攻击"""
        #已击杀
        if self.status:
            return
        # 更新争夺列表
        pid = atkInfo.get("pid", 0)
        name = atkInfo.get("name", 0)
        fa = atkInfo.get("fa", 0)
        hurt = atkInfo.get("hurt", 0)
        data = self.fighterData.get(pid)
        if data:
            data["hurt"] = data["hurt"] + hurt
        else:
            one = dict(name=name, hurt=hurt, pid=pid, fa=fa)
            self.fighterData[pid] = one
        #修改boss血量
        self.curHp -= hurt
        if self.curHp <= 0:
            self.beKill(pid, name, fa)
        self.markDirty()

    def beKill(self, pid, name, fa):
        now = int(time.time())
        if self.reborn_timer:
            self.reborn_timer.kill(block=False)
            self.reborn_timer = None
        res = Game.res_mgr.res_qmBoss.get(self.id)
        if res:
            self.time = now + res.cdtime
            self.reborn_timer = spawn_later(res.cdtime, self.reBorn)
        #设置击杀状态
        self.status = 1
        # 更新击杀列表 玩家id(pid, int) 击杀时间戳(time, int) 玩家名称(name, string) 战力(fa, int)
        one = dict(pid=pid, name=name, fa=fa, time=now)
        self.killList.insert(0, one)
        self.killList = self.killList[:5] #只保留最近5条
        # 调用所有逻辑服 通知玩家boss被击杀
        for addr, logic in Game.rpc_logic_game:
            if logic:
                logic.QmBossBeKill(self.id, self.time, _no_result=True)
        #发排名邮件奖励
        fighters = self.GetFighterData()
        for fighter in fighters:
            pid = fighter.get("pid", 0)
            rank = fighter.get("rank", 0)
            self.sendQmBossKillRankingReward(pid, self.id, rank)

    def sendQmBossKillRankingReward(self, pid, bossId, myRank):
        """发放全民boss击杀排行榜奖励"""
        resQmBoss = Game.res_mgr.res_qmBoss.get(bossId)

        if not resQmBoss:
            Game.glog.log2File("sendQmBossKillRankingReward_Err", "%s|%s|%s|%s" % (pid, bossId, myRank, "res_qmBoss"))
            return
        rankfirstReward = Game.res_mgr.res_reward.get(resQmBoss.rankfirstReward)
        if not rankfirstReward:
            Game.glog.log2File("sendQmBossKillRankingReward_Err", "%s|%s|%s|%s" % (pid, bossId, myRank, "res_reward"))
            return
        rankReward = Game.res_mgr.res_reward.get(resQmBoss.rankReward)
        if not rankReward:
            Game.glog.log2File("sendQmBossKillRankingReward_Err", "%s|%s|%s|%s" % (pid, bossId, myRank, "res_reward"))
            return
        if myRank == 1:
            dReward = rankfirstReward.doReward()
        else:
            dReward = rankReward.doReward()

        monsterRes = Game.res_mgr.res_monster.get(resQmBoss.mstId, None)
        if not monsterRes:
            Game.glog.log2File("sendQmBossKillRankingReward_Err", "%s|%s|%s|%s" % (pid, bossId, myRank, "res_qmBoss"))
            return

        #调用邮件接口发送邮件
        if myRank == 1:
            mailRes = Game.res_mgr.res_mail.get(constant.MAIL_ID_BOSS_KILL_REWARD, None)
        else:
            mailRes = Game.res_mgr.res_mail.get(constant.MAIL_ID_BOSS_PART_REWARD, None)
        if not mailRes:
            Game.glog.log2File("sendQmBossKillRankingReward_Err", "%s|%s|%s|%s" % (pid, bossId, myRank, "res_qmBoss"))
            return

        content = mailRes.content % monsterRes.name

        Game.rpc_mail_mgr.sendPersonMail(pid, mailRes.title, content, dReward, push=False)

    def reBorn(self):
        self.reSet()
        # 调用所有逻辑服 通知玩家boss复活
        for addr, logic in Game.rpc_logic_game:
            if logic:
                logic.QmBossReBorn(self.id, _no_result=True)
        if self.reborn_timer:
            self.reborn_timer.kill(block=False)
            self.reborn_timer = None

    def reSet(self):
        """重置"""
        self.time = 0
        self.fighterData = {}
        self.status = 0
        res = Game.res_mgr.res_qmBoss.get(self.id)
        if res:
            mstRes = Game.res_mgr.res_monster.get(res.mstId)
            if mstRes:
                self.init_hp(mstRes)
        self.markDirty()

    def to_client_info(self):
        resp = {}
        resp["id"] = self.id
        resp["curHp"] = self.curHp
        resp["maxHp"] = self.maxHp
        num = len(self.fighterData)
        if num > 5:
            num = 5 #只显示5个
        resp["num"] = num
        resp["status"] = self.status
        resp["time"] = self.time
        return resp

    # 	争夺列表(fighters, [json])
    # 		名次(rank, int)
    # 		玩家名称(name, string)
    # 		伤害(hurt, int)
    def GetFighterData(self):
        fighterData = list(self.fighterData.values())
        fighterData.sort(key=lambda x:x.get("hurt", 0), reverse=True)
        fighterData = fighterData[:5]
        fighters = []
        for index, data in enumerate(fighterData):
            one = {}
            one["pid"] = data.get("pid", 0)
            one["rank"] = index + 1
            one["name"] = data.get("name", "")
            one["hurt"] = data.get("hurt", 0)
            fighters.append(one)
        return fighters

    # 	击杀列表(killList, [json])
    # 		击杀时间戳(time, int)
    # 		玩家名称(name, string)
    # 		战力(fa, int)
    def GetKillList(self):
        return self.killList

    def GetTZInfo(self, pid):
        myData = self.fighterData.get(pid, {})
        myHurt = myData.get("hurt", 0)
        fighters = self.GetFighterData()
        bossInfo = self.to_client_info()
        bossInfo["fighters"] = fighters
        bossInfo["myHurt"] = myHurt
        return bossInfo


class YwBossMgr(utility.DirtyFlag):
    """ 野外Boss管理器"""
    _rpc_name_ = 'rpc_ywboss_mgr'
    def __init__(self):
        utility.DirtyFlag.__init__(self)
        self.data = None
        self.boss = {}  # {bossid:obj}

        self.save_cache = {}  # 存储缓存

        self._loop_task = None

        self.runaway_timer = None #逃跑定时器
        self.refresh_timer = None #刷新定时器

        Game.sub(MSG_FRAME_STOP, self._frame_stop)

    def start(self):
        self.data = ModelYwBoss.load(Game.store, ModelYwBoss.TABLE_KEY)
        if not self.data:
            self.data = ModelYwBoss()
        self.data.set_owner(self)
        self.load_from_dict(self.data.dataDict)

        self._loop_task = spawn(self._loop)

        resInterval = Game.res_mgr.res_common.get("ywBossInterval")
        resRunaway = Game.res_mgr.res_common.get("ywBossRunaway")
        #到下一个 xx:25 xx:55
        now = int(time.time())
        next_runaway = resInterval.i - (now % resInterval.i) - (resInterval.i - resRunaway.i)
        if next_runaway <= 60:
            next_runaway = 60 #预留10秒钟起服
        # 到下一个 xx:00 xx:30
        next_refresh = resInterval.i - (now % resInterval.i)
        if next_runaway <= 15 and next_runaway > next_refresh:
            next_refresh = next_runaway + 3 #时序问题处理
        self.runaway_timer = spawn_later(next_runaway, self.runaway)  # 逃跑定时器 xx:25 xx:55
        self.refresh_timer = spawn_later(next_refresh, self.refresh)  # 刷新定时器 xx:00 xx:30

    def _frame_stop(self):
        if self._loop_task:
            self._loop_task.kill(block=False)
            self._loop_task = None
        if self.runaway_timer:
            self.runaway_timer.kill(block=False)
            self.runaway_timer = None
        if self.refresh_timer:
            self.refresh_timer.kill(block=False)
            self.refresh_timer = None

        self.data.save(Game.store, forced=True, no_let=True)

    def _loop(self):
        stime = 60*30
        while 1:
            sleep(stime)
            try:
                self.data.save(Game.store)
            except Exception as err:
                Game.glog.log2File("YwBossMgr_loopError", err)

    # 存库数据
    def to_save_dict(self, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            self.save_cache = {}
            self.save_cache["boss"] = []
            for bossobj in self.boss.values():
                self.save_cache["boss"].append(bossobj.to_save_dict(forced=forced))
        return self.save_cache

    # 读库数据初始化
    def load_from_dict(self, data):
        boss = data.get("boss", [])
        for one in boss:
            res = Game.res_mgr.res_ywBoss.get(one["id"], None)
            if res:
                ywboss = YwBoss(res, data=one, owner=self)
                self.boss[ywboss.id] = ywboss
            else:
                Game.glog.log2File("YwBossLoadNotFindError", "%s|%s" % (one["bossid"], one))

        #没有数据的boss从资源表初始化
        for bossid, res in Game.res_mgr.res_ywBoss.items():
            if self.boss.get(bossid):
                continue
            mstRes = Game.res_mgr.res_monster.get(res.mstId)
            if not mstRes:
                continue
            ywboss = YwBoss(res, owner=self)
            ywboss.init_hp(mstRes)
            self.boss[bossid] = ywboss

    def runaway(self):
        """逃跑"""
        runawayKeys = []
        # 刷新boss
        for bossobj in self.boss.values():
            if bossobj.status == 1:
                rs = bossobj.runaway()
                if rs:
                    runawayKeys.append(bossobj.id)
        # 逃跑通知
        n = datetime.datetime.now()
        resStTime = Game.res_mgr.res_common.get("ywBossStTime")
        resEndTime = Game.res_mgr.res_common.get("ywBossEndTime")
        if resEndTime.i > resStTime.i: #不跨天
            if n.hour in range(resStTime.i, resEndTime.i): #活动时间内才推送通知
                # 调用所有逻辑服 通知玩家boss逃跑
                for addr, logic in Game.rpc_logic_game:
                    if logic:
                        logic.YwBossRunaway(runawayKeys, _no_result=True)
        else: #跨天
            if n.hour in range(0, resEndTime.i) or n.hour in range(resStTime.i, 24):
                # 调用所有逻辑服 通知玩家boss逃跑
                for addr, logic in Game.rpc_logic_game:
                    if logic:
                        logic.YwBossRunaway(runawayKeys, _no_result=True)
        if self.runaway_timer:
            self.runaway_timer.kill(block=False)
            self.runaway_timer = None
        # 到下一个 xx:25 xx:55
        resInterval = Game.res_mgr.res_common.get("ywBossInterval")
        resRunaway = Game.res_mgr.res_common.get("ywBossRunaway")
        now = int(time.time())
        next_runaway = resInterval.i - (now % resInterval.i) - (resInterval.i - resRunaway.i) + resInterval.i
        self.runaway_timer = spawn_later(next_runaway, self.runaway)  # 逃跑定时器 xx:00 xx:30

    def refresh(self):
        """刷新"""
        refreshKeys = []
        #刷新boss
        for bossobj in self.boss.values():
            rs = bossobj.refresh()
            if rs:
                refreshKeys.append(bossobj.id)
        # 刷新通知
        n = datetime.datetime.now()
        resStTime = Game.res_mgr.res_common.get("ywBossStTime")
        resEndTime = Game.res_mgr.res_common.get("ywBossEndTime")
        if resEndTime.i > resStTime.i:  # 不跨天
            if n.hour in range(resStTime.i, resEndTime.i):  # 活动时间内才推送通知
                # 调用所有逻辑服 通知玩家boss刷新
                for addr, logic in Game.rpc_logic_game:
                    if logic:
                        logic.YwBossRefresh(refreshKeys, _no_result=True)
        else:  # 跨天
            if n.hour in range(0, resEndTime.i) or n.hour in range(resStTime.i, 24):
                # 调用所有逻辑服 通知玩家boss刷新
                for addr, logic in Game.rpc_logic_game:
                    if logic:
                        logic.YwBossRefresh(refreshKeys, _no_result=True)
        if self.refresh_timer:
            self.refresh_timer.kill(block=False)
            self.refresh_timer = None
        # 到下一个 xx:00 xx:30
        resInterval = Game.res_mgr.res_common.get("ywBossInterval")
        now = int(time.time())
        next_refresh = resInterval.i - (now % resInterval.i)
        self.refresh_timer = spawn_later(next_refresh, self.refresh)  # 刷新定时器 xx:00 xx:30

    # 	野外Boss列表(ywBossList, [json])
    # 		野外BossId(id, int)
    # 		状态(status, int)1=已刷新 2=已逃跑 3=已击杀
    def GetAllBossInfo(self):
        bossList = []
        for bossobj in self.boss.values():
            one = bossobj.to_client_info()
            bossList.append(one)
        return bossList

    # 	野外BossId(id, int)
    # 	当前血量(curHp, int)
    # 	总血量(maxHp, int)
    # 	占领者id(rid, int)
    # 	占领者性别(sex, int)
    # 	占领者名称(name, string)
    # 	占领结束时间戳(time, int)
    def GetBossInfo(self, id):
        bossobj = self.boss.get(id)
        if not bossobj:
            return {}
        return bossobj.to_detail_info()

    def FightBoss(self, id, atkInfo):
        bossobj = self.boss.get(id)
        if not bossobj:
            return 0
        if bossobj.status != 1:
            return 0
        bossobj.beHurt(atkInfo)
        return bossobj.status

    def occupyBoss(self, id, atkInfo, rid):
        bossobj = self.boss.get(id)
        if not bossobj:
            return
        bossobj.occupy(atkInfo, rid)

    def CheckYwBossTZ(self, pid, id):
        for bossobj in self.boss.values():
            if bossobj.id == id:
                continue
            if bossobj.rid == pid:
                return 0, {}
        bossobj = self.boss.get(id)
        if not bossobj:
            return 0, {}
        return 1, bossobj.to_detail_info()

class YwBoss(utility.DirtyFlag):
    def __init__(self, res, data=None, owner=None):
        utility.DirtyFlag.__init__(self)
        self.id = res.id  # 野外BossId(id, int)
        self.curHp = 0  # 当前血量(curHp, int)
        self.maxHp = 0  # 总血量(maxHp, int)
        self.status = 1  # 状态(status, int)1=已刷新 2=已逃跑 3=已击杀
        self.refreshTime = 0 # 上一次刷新时间

        self.rid = 0 # 占领者id(rid, int)
        self.sex = 0 # 占领者性别(sex, int)
        self.name = "" # 占领者名称(name, string)
        self.fa = 0 # 占领者战力(fa, int)
        self.portrait = 0 # 占领者头像
        self.headframe = 0 # 占领者头像框

        self.time = 0 # 占领结束时间戳(time, int)

        self.save_cache = {}  # 存储缓存

        self.occupier_timer = None #占领者计时器

        if owner:
            self.set_owner(owner)
        if data:
            self.load_from_dict(data)

    def init_hp(self, mstRes):
        hp = mstRes.attr.get(constant.ATTR_HP, 0)
        self.curHp = hp
        self.maxHp = hp
        self.markDirty()

    def markDirty(self):
        utility.DirtyFlag.markDirty(self)
        if self.owner:
            self.owner.markDirty()

    def set_owner(self, owner):
        self.owner = owner

    # 存库数据
    def to_save_dict(self, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            self.save_cache = {}
            self.save_cache["id"] = self.id
            self.save_cache["curHp"] = self.curHp
            self.save_cache["maxHp"] = self.maxHp
            self.save_cache["status"] = self.status
        return self.save_cache

    # 读库数据初始化
    def load_from_dict(self, data):
        self.id = data.get("id", 0)  # 野外BossId(id, int)
        self.curHp = data.get("curHp", 0)  # 当前血量(curHp, int)
        self.maxHp = data.get("maxHp", 0)  # 总血量(maxHp, int)
        self.status = data.get("status", 1)  # 状态(status, int)1=已刷新 2=已逃跑 3=已击杀

        # 要对离线再回来的时间差进行处理
        res = Game.res_mgr.res_ywBoss.get(self.id)
        if res:
            mstRes = Game.res_mgr.res_monster.get(res.mstId)
            if mstRes:
                now = int(time.time())
                if now - self.refreshTime > res.interval:
                    self.refreshTime = now
                    self.status = 1
                    self.init_hp(mstRes)
                    self.markDirty()

    # 	野外Boss列表(ywBossList, [json])
    # 		野外BossId(id, int)
    # 		状态(status, int)1=已刷新 2=已逃跑 3=已击杀
    def to_client_info(self):
        resp = {}
        resp["id"] = self.id
        resp["status"] = self.status
        return resp

    # 	野外BossId(id, int)
    # 	当前血量(curHp, int)
    # 	总血量(maxHp, int)
    # 	占领者id(rid, int)
    # 	占领者性别(sex, int)
    # 	占领者名称(name, string)
    # 	占领结束时间戳(time, int)
    def to_detail_info(self):
        #玩家离线清除
        if self.rid:
            from game.mgr.player import get_rpc_player
            player = get_rpc_player(self.rid, offline=False)
            if not player:
                if self.occupier_timer:
                    self.occupier_timer.kill(block=False)
                    self.occupier_timer = None

                self.rid = 0  # 占领者id(rid, int)
                self.sex = 0  # 占领者性别(sex, int)
                self.name = ""  # 占领者名称(name, string)
                self.fa = 0  # 占领者战力(fa, int)
                self.portrait = 0  # 占领者头像
                self.headframe = 0  # 占领者头像框
                self.time = 0  # 占领结束时间戳(time, int)

        resp = {}
        resp["id"] = self.id
        resp["curHp"] = self.curHp
        resp["maxHp"] = self.maxHp
        resp["rid"] = self.rid
        resp["sex"] = self.sex
        resp["name"] = self.name
        resp["time"] = self.time
        resp["status"] = self.status
        resp["portrait"] = self.portrait
        resp["headframe"] = self.headframe
        return resp

    # 	占领者id(rid, int)
    # 	占领者性别(sex, int)
    # 	占领者名称(name, string)
    def occupy(self, atkInfo, rid):
        """占领"""
        #防止异步问题，如果占领者已经变更
        if rid != self.rid:
            return
        self.rid = atkInfo.get("pid", 0)  # 占领者id(rid, int)
        self.sex = atkInfo.get("sex", 0)  # 占领者性别(sex, int)
        self.name = atkInfo.get("name", "")  # 占领者名称(name, string)
        self.fa = atkInfo.get("fa", 0)  # 占领者战力(fa, int)
        self.portrait = atkInfo.get("portrait", 0) # 占领者头像
        self.headframe = atkInfo.get("headframe", 0) # 占领者头像框

        if self.occupier_timer:
            self.occupier_timer.kill(block=False)
            self.occupier_timer = None
        resBoss = Game.res_mgr.res_ywBoss.get(self.id)
        if resBoss:
            self.time = int(time.time()) + resBoss.occupy
            self.occupier_timer = spawn_later(resBoss.occupy, self.beKill, atkInfo)
        self.markDirty()

    def beHurt(self, atkInfo):
        """被攻击"""
        if not self.rid:
            self.occupy(atkInfo, self.rid)

        hurt = atkInfo.get("hurt", 0)
        #修改boss血量
        self.curHp -= hurt
        if self.curHp <= 0:
            self.beKill(atkInfo, isTimeout=0)
        self.markDirty()

    def beKill(self, atkInfo, isTimeout=1):
        self.rid = 0  # 占领者id(rid, int)
        self.sex = 0  # 占领者性别(sex, int)
        self.name = ""  # 占领者名称(name, string)
        self.fa = 0  # 占领者战力(fa, int)
        self.portrait = 0  # 占领者头像
        self.headframe = 0  # 占领者头像框
        self.time = 0  # 占领结束时间戳(time, int)
        self.status = 3

        if isTimeout: #占坑到时间击杀
            pid = atkInfo.get("pid", 0)
            # 给击杀者发放奖励
            from game.mgr.player import get_rpc_player
            killer = get_rpc_player(pid, offline=False)
            if killer:
                killer.sendYwBossKillReward(self.id, _no_result=True)
        # 调用所有逻辑服 通知玩家boss被击杀
        for addr, logic in Game.rpc_logic_game:
            if logic:
                logic.YwBossBeKill(self.id, _no_result=True)
        self.markDirty()

        if self.occupier_timer:
            self.occupier_timer.kill(block=False)
            self.occupier_timer = None

    def runaway(self):
        """逃跑"""
        res = Game.res_mgr.res_ywBoss.get(self.id)
        if not res:
            return False
        if res.spec:
            time_local = time.localtime(time.time())
            dt = time.strftime("%H:%M:00", time_local)
            isOK = 0
            for data in res.refresh:
                if data[1] == dt:
                    isOK = 1
            if not isOK:
                return False

        self.status = 2
        self.rid = 0  # 占领者id(rid, int)
        self.sex = 0  # 占领者性别(sex, int)
        self.name = ""  # 占领者名称(name, string)
        self.fa = 0  # 占领者战力(fa, int)
        self.portrait = 0  # 占领者头像
        self.headframe = 0  # 占领者头像框
        self.time = 0  # 占领结束时间戳(time, int)
        self.markDirty()

        if self.occupier_timer:
            self.occupier_timer.kill(block=False)
            self.occupier_timer = None
        return True

    def refresh(self):
        """刷新"""
        res = Game.res_mgr.res_ywBoss.get(self.id)
        if not res:
            return False
        if res.spec:
            time_local = time.localtime(time.time())
            dt = time.strftime("%H:%M:00", time_local)
            isOK = 0
            for data in res.refresh:
                if data[0] == dt:
                    isOK = 1
            if not isOK:
                return False

        now = int(time.time())
        self.rid = 0  # 占领者id(rid, int)
        self.sex = 0  # 占领者性别(sex, int)
        self.name = ""  # 占领者名称(name, string)
        self.fa = 0  # 占领者战力(fa, int)
        self.portrait = 0  # 占领者头像
        self.headframe = 0  # 占领者头像框
        self.time = 0  # 占领结束时间戳(time, int)
        self.status = 1  # 状态(status, int)1=已刷新 2=已逃跑 3=已击杀
        self.refreshTime = now  # 上一次刷新时间
        res = Game.res_mgr.res_ywBoss.get(self.id)
        if res:
            mstRes = Game.res_mgr.res_monster.get(res.mstId)
            if mstRes:
                self.init_hp(mstRes)
        self.markDirty()

        if self.occupier_timer:
            self.occupier_timer.kill(block=False)
            self.occupier_timer = None
        return True

class SsjBossMgr(utility.DirtyFlag):
    """ 生死劫Boss管理器"""
    _rpc_name_ = 'rpc_ssjboss_mgr'
    def __init__(self):
        utility.DirtyFlag.__init__(self)
        self.data = None
        self.firstKill = {} #{ssjId:{names:[], round:1, time:0} 全服首杀队伍 首杀者名字 首杀回合数 首杀时间戳
        self.minKill = {}#{ssjId:{names:[], round:1, time:0} 最少回合队伍 名字 最少回合数 最少回合击杀时间戳

        self.save_cache = {}  # 存储缓存

        self._loop_task = None

        Game.sub(MSG_FRAME_STOP, self._frame_stop)

    def start(self):
        self.data = ModelSsjBoss.load(Game.store, ModelSsjBoss.TABLE_KEY)
        if not self.data:
            self.data = ModelSsjBoss()
        self.data.set_owner(self)
        self.load_from_dict(self.data.dataDict)

        self._loop_task = spawn(self._loop)

    def _frame_stop(self):
        if self._loop_task:
            self._loop_task.kill(block=False)
            self._loop_task = None
        self.data.save(Game.store, forced=True, no_let=True)

    def _loop(self):
        stime = 60*30
        while 1:
            sleep(stime)
            try:
                self.data.save(Game.store)
            except Exception as err:
                Game.glog.log2File("SsjBossMgr_loopError", err)

    # 存库数据
    def to_save_dict(self, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            self.save_cache = {}
            self.save_cache["firstKill"] = {}
            for k, v in self.firstKill.items():
                self.save_cache["firstKill"][str(k)] = v

            self.save_cache["minKill"] = {}
            for k, v in self.minKill.items():
                self.save_cache["minKill"][str(k)] = v
        return self.save_cache

    # 读库数据初始化
    def load_from_dict(self, data):
        firstKill = data.get("firstKill", {})
        for k, v in firstKill.items():
            self.firstKill[int(k)] = v

        minKill = data.get("minKill", {})
        for k, v in minKill.items():
            self.minKill[int(k)] = v

    # 	全服首杀队伍名称列表(firstNames, [string]) 首杀者名字
    # 	首杀回合数(firstRounds, int)
    # 	首杀时间戳(firstTime, int)
    # 	最少回合队伍名称列表(minNames, [string]) 名字
    # 	最少回合数(minRounds, int)
    # 	最少回合击杀时间戳(minTime, int)
    def GetBossInfo(self, ssjId):
        resp = {}
        firstKill = self.firstKill.get(ssjId, {})
        minKill = self.minKill.get(ssjId, {})
        resp["firstNames"] = firstKill.get("names", [])
        resp["firstRounds"] = firstKill.get("round", 0)
        resp["firstTime"] = firstKill.get("time", 0)
        resp["minNames"] = minKill.get("names", [])
        resp["minRounds"] = minKill.get("round", 0)
        resp["minTime"] = minKill.get("time", 0)
        return resp

    def ReportFight(self, FightInfo):
        now = int(time.time())
        ssjId = FightInfo.get("ssjId", 0)
        round = FightInfo.get("round", 0)
        names = FightInfo.get("names", [])
        firstData = self.firstKill.get(ssjId)
        if firstData is None:
            self.firstKill[ssjId] = {"names":names, "round":round, "time":now}
            self.markDirty()
            # 调用所有逻辑服 通知玩家boss被击杀  全服首杀
            res = Game.res_mgr.res_ssjBoss.get(ssjId)
            mailRes = Game.res_mgr.res_mail.get(constant.MAIL_ID_SSJ_FIRST, None)
            
            ssjGrade1 = Game.res_mgr.res_common.get("ssjGrade1")
            ssjGrade2 = Game.res_mgr.res_common.get("ssjGrade2")

            # 全服邮件奖励
            gradeText = ssjGrade1.s
            if res.grade == 2:
                gradeText = ssjGrade2.s

            content = mailRes.content % (",".join(names), gradeText, res.group, res.lv)
            Game.rpc_mail_mgr.sendPublicMail(mailRes.title, content, res.firstReward)
            onlines = Game.rpc_player_mgr.get_online_ids()
            for pid in onlines:
                Game.rpc_mail_mgr.getNewPublicMail(pid)
        else:
            if len(firstData) == 0:
                self.firstKill[ssjId] = {"names": names, "round": round, "time": now}
                self.markDirty()

        minKill = self.minKill.get(ssjId, {})
        if round < minKill.get("round", 999):
            self.minKill[ssjId] = {"names": names, "round": round, "time": now}
            self.markDirty()









