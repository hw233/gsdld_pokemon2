# -*- coding:utf-8 -*-

from game.define import errcode, constant, msg_define
from game import Game
from game.common import utility
import time
import copy
import random

class ExamMixin(object):
    if 0:
        from game.core import player as player_md
        player = player_md.Player()

    # 获取问题(getQuestion)
    # 	请求
    # 		第几题(num, int)
    # 	返回
    # 		问题id(qid, int)
    # 		当前分数(score, int)
    # 		当前排行(rank, int)
    def rc_getQuestion(self, num):
        if num < 0 or num > 20:
            return 0, errcode.EC_PARAMS_ERR

        status = Game.rpc_exam_mgr.getStatus()
        if not status:
            return 0, errcode.EC_CLOSE

        questions, startTimePoint = self.player.exam.getExamInfo()
        if num == 1 or not questions or not startTimePoint:
            questions, startTimePoint = Game.rpc_exam_mgr.getExamInfo()
            random.shuffle(questions)
            self.player.exam.setExamInfo(questions, startTimePoint)

        playerExamInfo = Game.rpc_exam_mgr.getPlayerInfo(self.player.id)

        score, rank = 0, 0
        if playerExamInfo:
            score = playerExamInfo.get("score", 0)
            rank = playerExamInfo.get("rank", 0)

        if len(questions) < constant.QUESTION_NUM:
            return 0, errcode.EC_CLOSE

        # 抛事件
        self.player.safe_pub(msg_define.MSG_JOIN_EXAM)

        resp = {
            "qid": questions[num-1],
            "score": score,
            "rank": rank,
            "ranking": Game.rpc_exam_mgr.getRanking(5),
        }

        return 1, resp

    # 答题(answerQuestion)
    # 	请求
    # 		第几题(num, int)
    # 		答题(answer, int)
    # 	返回
    # 		是否正确(correct, int)
    def rc_answerQuestion(self, num, answer):
        if num < 0 or num > 20:
            return 0, errcode.EC_PARAMS_ERR

        now = int(time.time())
        questions, startTimePoint = self.player.exam.getExamInfo()
        if not questions or not startTimePoint:
            questions, startTimePoint = Game.rpc_exam_mgr.getExamInfo()
            self.player.exam.setExamInfo(questions, startTimePoint)

        qid = questions[num-1]
        startPoint = startTimePoint[num-1]
        if now < startPoint:
            return 0, errcode.EC_PARAMS_ERR

        qRes = Game.res_mgr.res_examQuestionPool.get(qid, None)
        if not qRes:
            return 0, errcode.EC_NORES

        correct = 0
        if qRes.correct == answer:
            correct = 1

        useTime = now - startPoint
        if useTime > 10:
            useTime = 10

        if useTime == 0:
            useTime = 1

        point = Game.res_mgr.res_result_useTime_answerPoint.get((correct, useTime), 0)
        self.player.exam.incAnswerTimes()

        pid = self.player.id
        name = self.player.name
        fa = self.player.base.fa

        Game.rpc_exam_mgr.updatePlayer(pid, name, fa, point, useTime, _no_result=1)

        resp = {
            "correct": correct,
            "point": point,
        }

        return 1, resp

    # 获取排行榜(getExamRank)
    # 	请求
    # 	返回
    # 		排行榜前20(ranking, [json])
    # 			名字(name, string)
    # 			分数(score, int)
    # 			战力(fa, int)
    def rc_getExamRank(self):
        resp = {
            "ranking": Game.rpc_exam_mgr.getRanking(20),
        }

        return 1, resp


    # 获取活动大厅信息(getActivityLobbyInfo)
    # 	请求
    # 	返回
    # 		答题信息(examInfo, json)
    # 			上期第一名(lastFirst, string)
    def rc_getActivityLobbyInfo(self):
        examInfo = {}
        examInfo["lastFirst"] = Game.rpc_exam_mgr.getLastFirst()

        resp = {
            "examInfo": examInfo,
        }

        return 1, resp