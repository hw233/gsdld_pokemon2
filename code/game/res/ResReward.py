#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import random
import copy

from game import Game
from game.common import utility
from game.res.resdefine import ResReward as ResRewardBase

class ResReward(ResRewardBase):

    def doReward(self, player=None):
        # return {}
        reward1 = self._doReward(self.cond1, self.type1, self.pool1, player=player)
        reward2 = self._doReward(self.cond2, self.type2, self.pool2, player=player)
        reward3 = self._doReward(self.cond3, self.type3, self.pool3, player=player)

        reward = {}
        for k, v in reward1.items():
            reward[k] = reward.get(k, 0) + v
        for k, v in reward2.items():
            reward[k] = reward.get(k, 0) + v
        for k, v in reward3.items():
            reward[k] = reward.get(k, 0) + v

        return reward


    def _doReward(self, cond, type, pool, player=None):
        reward = {}
        rs = Game.condition_mgr.check(cond, player=player)
        if not rs:
            return reward

        for one_group in pool:
            groupID, num, rate = one_group
            iLucky = random.randint(1, 100000)
            if rate < iLucky:
                continue

            rewardpool = Game.res_mgr.res_group_rewardpool.get(groupID)
            if num == 0: # 0表示全拿
                for rewardpoolID, rewardpoolRate in rewardpool:
                    rewardpoolRes = Game.res_mgr.res_rewardpool.get(rewardpoolID)
                    if rewardpoolRes:
                        reward[rewardpoolRes.itemNo] = reward.get(rewardpoolRes.itemNo, 0) + rewardpoolRes.num
            else:
                if type == 1: #奖池类型 1=id可重复2=id不可重复
                    for i in range(num):
                        rewardpoolID = utility.Choice(rewardpool)
                        rewardpoolRes = Game.res_mgr.res_rewardpool.get(rewardpoolID)
                        if rewardpoolRes:
                            reward[rewardpoolRes.itemNo] = reward.get(rewardpoolRes.itemNo, 0) + rewardpoolRes.num
                elif type == 2: #奖池类型 1=id可重复2=id不可重复
                    rewardpool = copy.deepcopy(rewardpool)
                    for i in range(num):
                        rewardpoolID, rewardpoolRate = utility.ChoiceReturn(rewardpool)
                        rewardpool.remove((rewardpoolID, rewardpoolRate))

                        rewardpoolRes = Game.res_mgr.res_rewardpool.get(rewardpoolID)
                        if rewardpoolRes:
                            reward[rewardpoolRes.itemNo] = reward.get(rewardpoolRes.itemNo, 0) + rewardpoolRes.num

        return reward










