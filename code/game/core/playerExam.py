# -*- coding:utf-8 -*-

from game.common import utility

class PlayerExam(utility.DirtyFlag):
    def __init__(self, owner):
        utility.DirtyFlag.__init__(self)
        self.owner = owner    # 拥有者
        self.answerTimes = 0
        self.questions = []
        self.startTimePoint = []

        self.save_cache = {}

    def markDirty(self):
        utility.DirtyFlag.markDirty(self)
        if self.owner:
            self.owner.markDirty()

    def to_save_dict(self, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            self.save_cache = {}
            if self.answerTimes:
                self.save_cache["answerTimes"] = self.answerTimes

        return self.save_cache

    def load_from_dict(self, data):
        self.answerTimes = data.get("answerTimes", 0)

    def uninit(self):
        pass

    def setExamInfo(self, questions, startTimePoint):
        self.questions = questions
        self.startTimePoint = startTimePoint

    def cleanExamInfo(self):
        self.questions = []
        self.startTimePoint = []

    def getExamInfo(self):
        return self.questions, self.startTimePoint

    def incAnswerTimes(self):
        self.answerTimes += 1
        self.markDirty()

    def getAnswerTimes(self):
        return self.answerTimes

