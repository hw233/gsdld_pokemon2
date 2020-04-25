#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from functools import cmp_to_key
from game import Game
import time
from corelib.frame import MSG_FRAME_STOP, MSG_ALL_LOGIC_START
from game.define import constant
from game.models.exam import ModelExam
from corelib import spawn, spawn_later, custom_today_ts, log
from gevent import sleep, event
from game.common import utility
import random
import copy

class ExamMgr(utility.DirtyFlag):
    _rpc_name_ = "rpc_exam_mgr"
    DATA_CLS = ModelExam

    def __init__(self):
        utility.DirtyFlag.__init__(self)

        self.lastFirst = ""         # 上期头名
        self.questions = []         # 当期题库
        self.players = {}           # 玩家数据
        self.ranking = []           # 排行榜
        self.startTimePoint = []    # 每题开始时间点
        self.nextOpenTime = 0       # 下期开始时间
        self.status = False         # 活动状态
        self.answerInterval = 12    # 每题答题时长
        self.readyInterval = 5      # 每题准备时长

        self.data = None
        self.save_cache = {}

        self._save_loop_task = None
        self._openTimer = None
        self._calTime = None
        self._closeTimer = None
        Game.sub(MSG_ALL_LOGIC_START, self._all_logic_start)
        Game.sub(MSG_FRAME_STOP, self._frame_stop)

    def markDirty(self):
        utility.DirtyFlag.markDirty(self)
        self.data.modify()

    def start(self):
        self.data = self.DATA_CLS.load(Game.store, self.DATA_CLS.TABLE_KEY)
        if not self.data:
            self.data = self.DATA_CLS()
        else:
            self.load_from_dict(self.data.dataDict)

        self.data.set_owner(self)

        examIntervalRes = Game.res_mgr.res_common.get("examInterval", None)
        if examIntervalRes:
            self.answerInterval = examIntervalRes.i

        examReadyIntervalRes = Game.res_mgr.res_common.get("examReadyInterval", None)
        if examReadyIntervalRes:
            self.readyInterval = examReadyIntervalRes.i

    def reset(self):
        self.questions = []
        self.startTimePoint = []

        now = int(time.time())
        todayOpenTs = custom_today_ts(12, 0, 0)

        # 初始下期活动开始时间
        self.nextOpenTime = todayOpenTs
        if now > todayOpenTs:
            self.nextOpenTime += 3600*24

        # 初始化题库
        self.questions = random.sample(list(Game.res_mgr.res_examQuestionPool.keys()), constant.QUESTION_NUM)

        # 初始化每题开始时间
        for x in range(constant.QUESTION_NUM):
            self.startTimePoint.append(self.nextOpenTime + x * (self.answerInterval+self.readyInterval))

        interval = self.nextOpenTime - now
        self._openTimer = spawn_later(interval-5, self.open)

    def _all_logic_start(self):
        self.reset()
        self._save_loop_task = spawn(self._saveLoop)

    def _frame_stop(self):
        if self._save_loop_task:
            self._save_loop_task.kill(block=False)
            self._save_loop_task = None

        self.save(forced=True, no_let=True)

    def _saveLoop(self):
        stime = 30 * 60
        while True:
            sleep(stime)
            try:
                self.save()
            except:
                log.log_except()

    def save(self, forced=False, no_let=False):
        self.data.save(Game.store, forced=forced, no_let=no_let)

    def open(self):
        self.players = {}
        self.ranking = []

        self.status = True
        self.nextOpenTime += 3600 * 24

        # 发开始公告
        for addr, logic in Game.rpc_logic_game:
            if logic:
                logic.sendSystemTemplateMSG(1116, [])

        closeTime = (self.answerInterval+self.readyInterval) * constant.QUESTION_NUM - self.readyInterval + 1
        self._closeTimer = spawn_later(closeTime+5, self.close)

        calTime = self.startTimePoint[0] + (self.answerInterval+self.readyInterval-2) - (time.time())
        self.calTimer = spawn_later(calTime, self.cal, 1)

    def cal(self, index):
        ranking = list(self.players.values())
        ranking.sort(key=cmp_to_key(self._comp))

        print("cal exam rank ", ranking, int(time.time()))
        for k in range(len(ranking)):
            ranking[k]["rank"] = k+1

        self.ranking = ranking
        index += 1
        calTime = self.startTimePoint[index] + (self.answerInterval+self.readyInterval-2) - (time.time())

        if self.status and index < constant.QUESTION_NUM-1:
            self.calTimer = spawn_later(calTime, self.cal, index)

    @staticmethod
    def _comp(x, y):
        xPoint = x.get("score", 0)
        yPoint = y.get("score", 0)
        xUseTime = x.get("useTime", 0)
        yUseTime = x.get("useTime", 0)

        if xPoint < yPoint:
            return 1

        if xPoint > yPoint:
            return -1

        if xUseTime > yUseTime:
            return 1

        if xUseTime < yUseTime:
            return -1

        return 0

    def close(self):
        # 计算最终排名
        ranking = list(self.players.values())
        ranking.sort(key=cmp_to_key(self._comp))

        threePlayer = []
        for k in range(len(ranking)):
            if k < 3:
                threePlayer.append(ranking[k].get("name", ""))

        self.ranking = ranking

        count = len(self.ranking)
        if count > 0:
            self.lastFirst = self.ranking[0].get("name", "")

        commonPlayer = self.ranking[3:]
        # 幸运玩家
        luckyPlayer = []
        examLuckyCount = 3
        examLuckyCountRes = Game.res_mgr.res_common.get("examLuckyCount", None)
        if examLuckyCountRes:
            examLuckyCount = examLuckyCountRes.i

        if len(commonPlayer) <= examLuckyCount:
            luckyPlayer = commonPlayer
        else:
            luckyPlayer = random.sample(commonPlayer, examLuckyCount)

        self.status = False

        sleep(3)

        # 发幸运玩家公告
        for addr, logic in Game.rpc_logic_game:
            if logic:
                for lucky in luckyPlayer:
                    logic.sendSystemTemplateMSG(1118, [lucky.get("name", "")])

        # 发得奖公告
        for addr, logic in Game.rpc_logic_game:
            if logic:
                if len(threePlayer) == 1:
                    logic.sendSystemTemplateMSG(1119, threePlayer)
                elif len(threePlayer) == 2:
                    logic.sendSystemTemplateMSG(1120, threePlayer)
                elif len(threePlayer) == 3:
                    logic.sendSystemTemplateMSG(1117, threePlayer)

        Game.glog.log2File("examResult", "%s|%s" % (threePlayer, luckyPlayer))

        # 发奖励
        luckyRewardRes = Game.res_mgr.res_common.get("examLuckyReward", None)
        from game.mgr.player import get_rpc_player
        for x in range(len(self.ranking)):
            rank = x + 1
            player = self.ranking[x]
            reward = {}
            rewardRes = None
            maxRank = len(Game.res_mgr.res_examRankReward)
            if rank <= maxRank:
                rewardRes = Game.res_mgr.res_examRankReward.get(rank, None)
            else:
                rewardRes = Game.res_mgr.res_examRankReward.get(maxRank, None)

            if not rewardRes:
                continue

            reward = copy.deepcopy(rewardRes.reward)

            if player in luckyPlayer and luckyRewardRes:
                for k, v in luckyRewardRes.arrayint2.items():
                    reward.setdefault(k, 0)
                    reward[k] += v

            pid = player.get("pid", 0)
            if pid:
                playerRpc = get_rpc_player(pid, offline=False)
                mailRes = Game.res_mgr.res_mail.get(constant.MAIL_ID_EXAM_REWARD, None)
                content = mailRes.content % str(rank)
                if playerRpc:
                    rs = playerRpc.sendExamReward(rank, player.get("score", 0), reward)
                    if not rs:
                        Game.rpc_mail_mgr.sendPersonMail(pid, mailRes.title, content, reward)
                else:
                    Game.rpc_mail_mgr.sendPersonMail(pid, mailRes.title, content, reward)

        self.reset()
        self.markDirty()

    def load_from_dict(self, data):
        self.lastFirst = data.get("lastFirst", [])
        for player in self.ranking:
            self.players[player.pid] = player

    def to_save_dict(self, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            self.save_cache["lastFirst"] = self.lastFirst
        return self.save_cache

    def updatePlayer(self, pid, name, fa, point, useTime):
        if pid in self.players:
            player = self.players[pid]
            player["pid"] = pid
            player["name"] = name
            player["fa"] = fa
            player["score"] += point
            player["useTime"] += useTime
        else:
            self.players[pid] = {
                "pid": pid,
                "name": name,
                "fa": fa,
                "score": point,
                "useTime": useTime,
            }

    def getExamInfo(self):
        return self.questions, self.startTimePoint

    def getPlayerInfo(self, pid):
        return self.players.get(pid, None)

    def getRanking(self, size):
        return self.ranking[:size]

    def getStatus(self):
        return self.status

    def getLastFirst(self):
        return self.lastFirst