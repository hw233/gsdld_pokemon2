#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import random
import copy

from game import Game
from game.common import utility
from game.res.resdefine import ResEffect as ResEffectBase

class ResEffect(ResEffectBase):

    def init(self):
        if not self.target:
            self.target_tp = 0
            self.target_num = []
            self.target_scope = []
            return

        ls = self.target.split("|")
        if len(ls) == 1:  #选择自己
            self.target_tp = int(ls[0])
            self.target_num = [(1,1)]
            self.target_scope = []
        else:
            self.target_tp = int(ls[0])

            target_num = ls[1]
            target_num = target_num.split(";")
            self.target_num = []
            for one in target_num:
                _tmp = one.split("_")
                if len(_tmp) == 1:
                    self.target_num.append((int(_tmp[0]), 1))
                else:
                    self.target_num.append((int(_tmp[0]), int(_tmp[1])))

            scope = ls[2]
            scope = scope.split("_")
            self.target_scope = []
            for one in scope:
                self.target_scope.append(int(one))






