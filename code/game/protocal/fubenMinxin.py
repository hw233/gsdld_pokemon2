#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from game.define import errcode, constant, msg_define
from game import Game
from game.common import utility
import copy
import random

class FubenRpcMixin(object):
    if 0:
        from game.core import player as player_md
        player = player_md.Player()

    # 挑战(clfbChallenge)
    #     请求
    #         材料副本id(id, int)
    #     返回
    #         主动推送刷新(allUpdate, json)
    #             游戏模型 - 货币
    #             游戏模型 - 角色背包
    #             游戏模型 - 角色属性
    #             游戏模型 - 角色基础 - 战力
    #         战报(fightLog, json)
    #         材料副本id(id, int)
    #         当日已挑战次数(challengeNum, int)
    def rc_clfbChallenge(self, fubenId):
        res = Game.res_mgr.res_clfb.get(fubenId, None)
        if not res:
            return 0, errcode.EC_NORES

        lv = self.player.base.GetLv()
        if lv < res.openLv:
            return 0, errcode.EC_CLFB_LEVEL_TOO_LOW

        num = self.player.fuben.getClbzChanllengeNum(fubenId)
        if num >= res.freeCount:
            return 0, errcode.EC_CLFB_ALREADY_CHALLENGE
        #按等级获取副本
        barrierId = 0
        for data in res.barrierId:
            startLv = data[0]
            endLv = data[1]
            if startLv <= self.player.base.GetLv() <= endLv:
                barrierId = data[2]

        barrierRes = Game.res_mgr.res_barrier.get(barrierId)
        if not barrierRes:
            return 0, errcode.EC_NORES

        rewardRes = Game.res_mgr.res_reward.get(barrierRes.rewardId)
        if not rewardRes:
            return 0, errcode.EC_NORES

        fightobj = Game.fight_mgr.createFight(constant.FIGHT_TYPE_190)
        rs = fightobj.init_by_barrId(self.player, barrierRes.id)
        if not rs:
            return 0, errcode.EC_INIT_BARR_FAIL

        respBag = {}
        fightLog = fightobj.doFight()
        fightResult = fightLog["result"].get("win", 0)
        if fightResult:
            dReward = rewardRes.doReward()
            respBag = self.player.bag.add(dReward, constant.ITEM_ADD_CLFB_REWARD, wLog=True)

            self.player.fuben.setClbzChanllengeNum(fubenId, num+1)
            self.player.fuben.IncClfbSuccessCount()
            self.player.fuben.IncClfbFightNum(fubenId)

            iTotal = self.player.fuben.getClbzChanllengeNumTotal()
            self.player.fuben.setClbzChanllengeNumTotal(iTotal + 1)
            # 抛事件
            self.player.safe_pub(msg_define.MSG_PASS_CLFB, fubenId)

        # 抛事件
        self.player.safe_pub(msg_define.MSG_CLFB_FIGHT)
        self.player.fuben.addClbfId(fubenId)
        dRole = {}
        dRole["roleBase"] = self.player.base.to_init_data()
        dRole["roleAttr"] = self.player.attr.to_update_data()

        dUpdate = self.player.packRespBag(respBag)
        dUpdate["role"] = dRole
        resp = {
            "fightLog": fightLog,
            "allUpdate": dUpdate,
            "fubenId": fubenId,
            "challengeNum": num+fightResult,
        }
        return 1, resp


    # 扫荡(clfbSweep)
    #     请求
    #         材料副本id(id,int)
    #     返回
    #         主动推送刷新(allUpdate,json)
    #             游戏模型-货币
    #             游戏模型-角色背包
    #             游戏模型-角色属性
    #             游戏模型-角色基础-战力
    #         材料副本id(id,int)
    #         当日已挑战次数(challengeNum, int)
    def rc_clfbSweep(self, fubenId):
        res = Game.res_mgr.res_clfb.get(fubenId, None)
        if not res:
            return 0, errcode.EC_NORES

        vipLv = self.player.vip.GetVipLv()
        vipRes = Game.res_mgr.res_vip.get(vipLv, None)
        if not vipRes:
            return 0, errcode.EC_NORES

        # maxSweepCount = res.freeCount + res.baseSweepCount + vipRes.clbzSweepCount
        maxSweepCount = res.freeCount + vipRes.clbzSweepCount

        lv = self.player.base.GetLv()
        num = self.player.fuben.getClbzChanllengeNum(fubenId)
        if num >= maxSweepCount:
            return 0, errcode.EC_CLFB_SWEEP_MAX_TIMES

        if num == 0 and lv < res.sweepLv:
            return 0, errcode.EC_CLFB_SWEEP_LEVEL_TOO_LOW

        #按等级获取副本
        barrierId = 0
        for data in res.barrierId:
            startLv = data[0]
            endLv = data[1]
            if startLv <= self.player.base.GetLv() <= endLv:
                barrierId = data[2]

        barrierRes = Game.res_mgr.res_barrier.get(barrierId)
        if not res:
            return 0, errcode.EC_NORES

        rewardRes = Game.res_mgr.res_reward.get(barrierRes.rewardId)
        if not rewardRes:
            return 0, errcode.EC_NORES

        dReward = rewardRes.doReward()
        # if num > 0:  # 非每日首次不得绑钻
        #     dReward[3] = 0

        respBag = self.player.bag.add(dReward, constant.ITEM_ADD_CLFB_REWARD, wLog=True)

        self.player.fuben.setClbzChanllengeNum(fubenId, num+1)
        self.player.fuben.IncClfbSuccessCount()
        self.player.fuben.IncClfbFightNum(fubenId)

        iTotal = self.player.fuben.getClbzChanllengeNumTotal()
        self.player.fuben.setClbzChanllengeNumTotal(iTotal + 1)
        # 抛事件
        self.player.safe_pub(msg_define.MSG_PASS_CLFB, fubenId)
        # 抛事件
        self.player.safe_pub(msg_define.MSG_CLFB_FIGHT)

        dRole = {}
        dRole["roleBase"] = self.player.base.to_init_data()
        dRole["roleAttr"] = self.player.attr.to_update_data()

        dUpdate = self.player.packRespBag(respBag)
        dUpdate["role"] = dRole
        resp = {
            "allUpdate": dUpdate,
            "fubenId": fubenId,
            "challengeNum": num + 1,
        }
        return 1, resp

    # 一键扫荡(clfbOneKeySweep)
    #     请求
    #        扫荡材料副本id列表(fubenIdList, [int])
    #     返回
    #         主动推送刷新(allUpdate, json)
    #             游戏模型 - 货币
    #             游戏模型 - 角色背包
    #             游戏模型 - 角色属性
    #             游戏模型 - 角色基础 - 战力
    #
    #         扫荡材料副本id列表(fubenIdList, [int])
    #         当日已挑战次数列表(challengeNumList, [int])
    def rc_clfbOneKeySweep(self, fubenIdList):
        vipLv = self.player.vip.GetVipLv()
        vipRes = Game.res_mgr.res_vip.get(vipLv, None)
        if not vipRes:
            return 0, errcode.EC_NORES

        sweepIdList = []
        sweepIdNum = []
        lv = self.player.base.GetLv()

        respBag = {}
        for fubenId in fubenIdList:
            res = Game.res_mgr.res_clfb.get(fubenId, None)
            if not res:
                return 0, errcode.EC_NORES

            maxSweepCount = res.freeCount + vipRes.clbzSweepCount

            if lv < res.sweepLv:  # 等级不够
               continue

            num = self.player.fuben.getClbzChanllengeNum(res.fubenId)
            if num >= maxSweepCount:  # 已达最大次数
                continue

            sweepIdList.append(res.fubenId)
            sweepIdNum.append(num+1)
             #按等级获取副本
            barrierId = 0
            for data in res.barrierId:
                startLv = data[0]
                endLv = data[1]
                if startLv <= self.player.base.GetLv() <= endLv:
                    barrierId = data[2]

            barrierRes = Game.res_mgr.res_barrier.get(barrierId)
            if not res:
                return 0, errcode.EC_NORES

            rewardRes = Game.res_mgr.res_reward.get(barrierRes.rewardId)
            if not rewardRes:
                return 0, errcode.EC_NORES

            dReward = rewardRes.doReward()
            # if num > 0:     # 非每日首次不得绑钻
            #     dReward[3] = 0

            respBag1 = self.player.bag.add(dReward, constant.ITEM_ADD_CLFB_REWARD, wLog=True)
            respBag = self.player.mergeRespBag(respBag, respBag1)

            self.player.fuben.setClbzChanllengeNum(res.fubenId, num+1)
            self.player.fuben.IncClfbSuccessCount()
            self.player.fuben.IncClfbFightNum(res.fubenId)

            iTotal = self.player.fuben.getClbzChanllengeNumTotal()
            self.player.fuben.setClbzChanllengeNumTotal(iTotal + 1)
            # 抛事件
            self.player.safe_pub(msg_define.MSG_PASS_CLFB, res.fubenId)
            # 抛事件
            self.player.safe_pub(msg_define.MSG_CLFB_FIGHT)

        dRole = {}
        dRole["roleBase"] = self.player.base.to_init_data()
        dRole["roleAttr"] = self.player.attr.to_update_data()

        dUpdate = self.player.packRespBag(respBag)
        dUpdate["role"] = dRole
        resp = {
            "allUpdate": dUpdate,
            "fubenIdList": sweepIdList,
            "fubenIdNum": sweepIdNum,
        }
        return 1, resp

    # 请求材料副本数据(clfbGetInfo)
    #     请求
    #     返回
    #         材料副本列表(clbz, [json])
    #               副本id(fubenId, int)
    #               副本挑战次数(challengeNum, int)
    def rc_clfbGetInfo(self):
        resp = self.player.fuben.clfbGetInfo()
        return 1, resp

    # 挑战(lwbzChallenge)
    #     请求
    #         关卡id(id,int)
    #     返回
    #         主动推送刷新(allUpdate,json)
    #             游戏模型-货币
    #             游戏模型-角色背包
    #             游戏模型-角色属性
    #             游戏模型-角色基础-战力
    #         战报(fightLog, json)
    #         关卡id(id,int)
    #         星数(star,int)
    def rc_lwbzChallenge(self, levelId):
        res = Game.res_mgr.res_lwbz.get(levelId, None)
        if not res:
            return 0, errcode.EC_NORES

        cangbaotu = self.player.fuben.getCangbaotu(res.baotuId)
        levelStatus = cangbaotu.getDailyStatus(levelId)

        barrierRes = Game.res_mgr.res_barrier.get(res.barrierId)
        if not barrierRes:
            return 0, errcode.EC_NORES

        rewardRes = Game.res_mgr.res_reward.get(barrierRes.rewardId)
        if not rewardRes:
            return 0, errcode.EC_NORES

        starRes = None
        if res.type == 1:
            starRes = Game.res_mgr.res_common.get("LwbzNoramlStarJudge", {})
        elif res.type == 2:
            starRes = Game.res_mgr.res_common.get("LwbzHardStarJudge", {})

        if not starRes:
            return 0, errcode.EC_NORES

        starJudge = starRes.arrayint2

        fightobj = Game.fight_mgr.createFight(constant.FIGHT_TYPE_191)
        rs = fightobj.init_by_barrId(self.player, barrierRes.id)
        if not rs:
            return 0, errcode.EC_INIT_BARR_FAIL

        fightLog = fightobj.doFight()
        fightResult = fightLog["result"].get("win", 0)
        useRound = fightLog.get("useRound", 0)

        respBag = {}
        if fightResult:
            oldStar = cangbaotu.getLevelStar(levelId)
            resReward = rewardRes.doReward()
            reward = copy.deepcopy(resReward)
            if not oldStar:
                for k, v in barrierRes.firstReward.items():
                    if k in reward:
                        reward[k] = reward[k]+v
                    else:
                        reward[k] = v

            if not levelStatus:
                respBag = self.player.bag.add(reward, constant.ITEM_ADD_LWBZ_REWARD, wLog=True)
                cangbaotu.markDailyStatus(levelId)

            # 计算星数
            newStar = 0
            roundList = list(starJudge.values())
            roundList.sort()

            round = 0
            for r in roundList:
                if useRound <= r:
                    round = r
                    break

            for k, v in starJudge.items():
                if v == round:
                    newStar = k
                    break

            if newStar > oldStar:
                cangbaotu.setLevelStar(levelId, newStar)
                self.player.rank.uploadRank(constant.RANK_TYPE_LWBZ)
        else:
            self.player.safe_pub(msg_define.MSG_XIANSHITUISONGLIBAO_LWBZ_F)
        # 抛事件
        self.player.safe_pub(msg_define.MSG_PASS_LWBZ)

        # import ujson
        # Game.glog.log2File("testLwbzChallenge", "%s" % ujson.dumps(fightLog))

        dRole = {}
        dRole["roleBase"] = self.player.base.to_init_data()
        dRole["roleAttr"] = self.player.attr.to_update_data()

        dUpdate = self.player.packRespBag(respBag)
        dUpdate["role"] = dRole
        resp = {
            "fightLog": fightLog,
            "allUpdate": dUpdate,
            "levelId": levelId,
            "star": cangbaotu.getLevelStar(levelId),
        }
        return 1, resp

    # 一键挑战(lwbzOneKeyChallenge)
    #     请求
    #     返回
    #         主动推送刷新(allUpdate,json)
    #             游戏模型-货币
    #             游戏模型-角色背包
    #             游戏模型-角色属性
    #             游戏模型-角色基础-战力
    def rc_lwbzOneKeyChallenge(self):
        vipLv = self.player.vip.GetVipLv()
        vipRes = Game.res_mgr.res_vip.get(vipLv, None)
        if not vipRes:
            return 0, errcode.EC_NORES
        if not vipRes.lwbzOneKey:
            return 0, errcode.EC_LWBZ_SWEEP_VIP_LIMIT

        unChallengeLevel = self.player.fuben.getLwbzUnChallengeLevel()

        reward = {}
        for levelId in unChallengeLevel:
            res = Game.res_mgr.res_lwbz.get(levelId, None)
            if not res:
                return 0, errcode.EC_NORES

            barrierRes = Game.res_mgr.res_barrier.get(res.barrierId)
            if not barrierRes:
                return 0, errcode.EC_NORES

            rewardRes = Game.res_mgr.res_reward.get(barrierRes.rewardId)
            if not rewardRes:
                return 0, errcode.EC_NORES

            resReward = rewardRes.doReward()

            for k, v in resReward.items():
                if k in reward:
                    reward[k] = reward[k] + v
                else:
                    reward[k] = v

            # 抛事件
            self.player.safe_pub(msg_define.MSG_PASS_LWBZ)

        for levelId in unChallengeLevel:
            res = Game.res_mgr.res_lwbz.get(levelId, None)
            cangbaotu = self.player.fuben.getCangbaotu(res.baotuId)
            cangbaotu.markDailyStatus(levelId)

        respBag = self.player.bag.add(reward, constant.ITEM_ADD_LWBZ_REWARD, wLog=True)

        dRole = {}
        dRole["roleBase"] = self.player.base.to_init_data()
        dRole["roleAttr"] = self.player.attr.to_update_data()

        dUpdate = self.player.packRespBag(respBag)
        dUpdate["role"] = dRole
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp

    # 领取星数宝箱(lwbzGetStarReward)
    #     请求
    #         星数id(startId,int)
    #             1，2，3
    #     返回
    #         主动推送刷新(allUpdate,json)
    #             游戏模型-货币
    #             游戏模型-角色背包
    #             游戏模型-角色属性
    #             游戏模型-角色基础-战力
    def rc_lwbzGetStarReward(self, starId, baotuId):
        res = Game.res_mgr.res_lwbzStarReward.get(baotuId, None)
        if not res:
            return 0, errcode.EC_NORES

        cangbaotu = self.player.fuben.getCangbaotu(baotuId)
        totalStar = cangbaotu.getTotalStar()

        if starId < 1 or starId > 4:
            return 0, errcode.EC_LWBZ_UNKNOWN_STARID

        targetStar = 0
        if starId == 1:
            targetStar = 6
        elif starId == 2:
            targetStar = 12
        elif starId == 3:
            targetStar = 18

        if totalStar < targetStar:
            return 0, errcode.EC_LWBZ_STAR_NO_ENOUGH

        status = cangbaotu.getStarRewardStatus(starId)
        if status:
            return 0, errcode.EC_LWBZ_STAR_REWARD_ALREADY_OPEN

        reward = res.reward.get(starId, None)
        if not reward:
            return 0, errcode.EC_NORES

        cangbaotu.markStarRewardStatus(starId)

        respBag = self.player.bag.add(reward, constant.ITEM_ADD_LWBZ_REWARD, wLog=True)

        self.player.fuben.IncLwbzRewardNum()
        # 抛事件
        self.player.safe_pub(msg_define.MSG_GET_LWBZ_STAR_REWARD)

        dRole = {}
        dRole["roleBase"] = self.player.base.to_init_data()
        dRole["roleAttr"] = self.player.attr.to_update_data()

        dUpdate = self.player.packRespBag(respBag)
        dUpdate["role"] = dRole
        resp = {
            "allUpdate": dUpdate,
            "starId": starId,
            "baotuId": baotuId,
        }
        return 1, resp

    def rc_xlysBuyBuff(self,key):

        canbuy=self.player.fuben.getXlysBuffCanBuy()
        if key not in canbuy:
            return 0, errcode.EC_XLYS_BUFF_BUY

        res=Game.res_mgr.res_xlysBuff.get(key,None)
        if not res:
            return 0, errcode.EC_NORES
        
        buff=self.player.fuben.getXlysBuff()

        xlysBuffLimitRes = Game.res_mgr.res_common.get("xlysBuffLimit")
        if not xlysBuffLimitRes:
            return 0, errcode.EC_NORES

        iTotal = 0
        for val in buff.values():
            iTotal += val.get("count", 0)

        if iTotal >= xlysBuffLimitRes.i:
            return 0, errcode.EC_TIMES_FULL

        count=buff[key]["count"]

        costl=len(res.cost)
        
        if count>=costl:
            count=costl-1
        
        cost={}
        cost[res.cost[count][0]]=res.cost[count][1]

        respBag = self.player.bag.costItem(cost, constant.ITEM_COST_XLYS_BUFF, wLog=True)
        if not respBag.get("rs", 0):
            return 0, errcode.EC_COST_ERR

        self.player.fuben.addXlysBuff(key)

        dUpdate = self.player.packRespBag(respBag)
        dUpdate["fubenInfo"]=self.player.fuben.to_init_data()
        resp = {

            "allUpdate": dUpdate,
        }
        return 1, resp

    # 挑战(xlysChallenge)
    #     请求
    #         关卡id(id,int)
    #     返回
    #         主动推送刷新(allUpdate,json)
    #             游戏模型-货币
    #             游戏模型-角色背包
    #             游戏模型-角色属性
    #             游戏模型-角色基础-战力
    #         战报(fightLog, json)
    #         关卡id(id,int)
    def rc_xlysChallenge(self, levelId):
        oldLevelId = self.player.fuben.getXlysMaxLevelId()
        if levelId != oldLevelId + 1:
            return 0, errcode.EC_XLYS_LEVEL_ERROR

        res = Game.res_mgr.res_xlys.get(levelId, None)
        if not res:
            return 0, errcode.EC_NORES

        barrierRes = Game.res_mgr.res_barrier.get(res.barrierId)
        if not barrierRes:
            return 0, errcode.EC_NORES

        rewardRes = Game.res_mgr.res_reward.get(barrierRes.rewardId)
        if not rewardRes:
            return 0, errcode.EC_NORES

        fightobj = Game.fight_mgr.createFight(constant.FIGHT_TYPE_192)
        rs = fightobj.init_by_barrId(self.player, barrierRes.id)
        if not rs:
            return 0, errcode.EC_INIT_BARR_FAIL

        buff=self.player.fuben.getXlysBuff()
        fightobj.enhanceRedTeamPer(buff)

        respBag = {}
        fightLog = fightobj.doFight()
        fightResult = fightLog["result"].get("win", 0)
        if fightResult:
            dReward = rewardRes.doReward()
            respBag = self.player.bag.add(dReward, constant.ITEM_ADD_XLYS_REWARD, wLog=True)
            self.player.fuben.setXlysMaxLevelId(levelId)

            self.player.rank.uploadRank(constant.RANK_TYPE_XLYS, {"levelId": levelId})
        else:
            self.player.safe_pub(msg_define.MSG_XIANSHITUISONGLIBAO_XLYS_F)
        # 抛事件
        self.player.safe_pub(msg_define.MSG_PASS_XLYS)

        dRole = {}
        dRole["roleBase"] = self.player.base.to_init_data()
        dRole["roleAttr"] = self.player.attr.to_update_data()

        dUpdate = self.player.packRespBag(respBag)
        dUpdate["role"] = dRole
        resp = {
            "allUpdate": dUpdate,
            "fightLog": fightLog,
            "levelId": levelId,
        }
        return 1, resp

    # 挑战(ttslChallenge)
    #     请求
    #         关卡id(id,int)
    #     返回
    #         主动推送刷新(allUpdate,json)
    #             游戏模型-货币
    #             游戏模型-角色背包
    #             游戏模型-角色属性
    #             游戏模型-角色基础-战力
    #         战报(fightLog, json)
    #         关卡id(id,int)
    def rc_ttslChallenge(self, levelId):
        todayMaxlevelId = self.player.fuben.getTtslTodayMaxLevelId()

        if levelId != todayMaxlevelId + 1:
            return 0, errcode.EC_TTSL_LEVEL_ERROR

        res = Game.res_mgr.res_ttsl.get(levelId, None)
        if not res:
            return 0, errcode.EC_NORES


        barrierRes = Game.res_mgr.res_barrier.get(res.barrierId)
        if not barrierRes:
            return 0, errcode.EC_NORES

        rewardRes = Game.res_mgr.res_reward.get(barrierRes.rewardId)
        if not rewardRes:
            return 0, errcode.EC_NORES

        fightobj = Game.fight_mgr.createFight(constant.FIGHT_TYPE_193)
        rs = fightobj.init_by_barrId(self.player, barrierRes.id)
        if not rs:
            return 0, errcode.EC_INIT_BARR_FAIL

        respBag = {}
        fightLog = fightobj.doFight()
        fightResult = fightLog["result"].get("win", 0)
        if fightResult:
            dReward = rewardRes.doReward()
            respBag = self.player.bag.add(dReward, constant.ITEM_ADD_TTSL_REWARD, wLog=True)

            self.player.fuben.setTtslTodayMaxLevelId(levelId)
            maxLevelId = self.player.fuben.getTtslMaxLevelId()
            if levelId > maxLevelId:
                self.player.fuben.setTtslMaxLevelId(levelId)

                self.player.rank.uploadRank(constant.RANK_TYPE_TTSL, {"levelId": levelId})
        else:
            self.player.safe_pub(msg_define.MSG_XIANSHITUISONGLIBAO_TTSL_F)

        self.player.safe_pub(msg_define.MSG_PASS_TTSL)

        dRole = {}
        dRole["roleBase"] = self.player.base.to_init_data()
        dRole["roleAttr"] = self.player.attr.to_update_data()

        dUpdate = self.player.packRespBag(respBag)
        dUpdate["role"] = dRole
        resp = {
            "allUpdate": dUpdate,
            "fightLog": fightLog,
            "levelId": levelId,
        }
        return 1, resp

    # 一键挑战(ttslOneKeyChallenge)
    #     请求
    #     返回
    #         主动推送刷新(allUpdate,json)
    #             游戏模型-货币
    #             游戏模型-角色背包
    #             游戏模型-角色属性
    #             游戏模型-角色基础-战力
    def rc_ttslOneKeyChallenge(self):
        maxLevelId = self.player.fuben.getTtslMaxLevelId()
        todayMaxlevelId = self.player.fuben.getTtslTodayMaxLevelId()

        reward = {}
        for levelId in range(todayMaxlevelId+1, maxLevelId+1):
            res = Game.res_mgr.res_ttsl.get(levelId, None)
            if not res:
                return 0, errcode.EC_NORES

            barrierRes = Game.res_mgr.res_barrier.get(res.barrierId)
            if not barrierRes:
                return 0, errcode.EC_NORES

            rewardRes = Game.res_mgr.res_reward.get(barrierRes.rewardId)
            if not rewardRes:
                return 0, errcode.EC_NORES

            resReward = rewardRes.doReward()

            for k, v in resReward.items():
                if k in reward:
                    reward[k] = reward[k] + v
                else:
                    reward[k] = v

            self.player.safe_pub(msg_define.MSG_PASS_TTSL)

        self.player.fuben.setTtslTodayMaxLevelId(maxLevelId)
        respBag = self.player.bag.add(reward, constant.ITEM_ADD_TTSL_REWARD, wLog=True)

        dRole = {}
        dRole["roleBase"] = self.player.base.to_init_data()
        dRole["roleAttr"] = self.player.attr.to_update_data()

        dUpdate = self.player.packRespBag(respBag)
        dUpdate["role"] = dRole
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp

    # 领取关卡宝箱(ttslGetLevelReward)
    #     请求
    #         关卡id(levelId,int)
    #     返回
    #         主动推送刷新(allUpdate,json)
    #             游戏模型-货币
    #             游戏模型-角色背包
    #             游戏模型-角色属性
    #             游戏模型-角色基础-战力
    def rc_ttslGetLevelReward(self, levelId):
        maxLevelId = self.player.fuben.getTtslMaxLevelId()
        if levelId > maxLevelId:
            return 0, errcode.EC_TTSL_LEVEL_ERROR

        res = Game.res_mgr.res_ttsl.get(levelId, None)
        if not res:
            return 0, errcode.EC_NORES

        if not res.firstReward:
            return 0, errcode.EC_TTSL_LEVEL_ERROR

        status = self.player.fuben.getTtslRewardStatus(levelId)
        if status:
            return 0, errcode.EC_TTSL_LEVEL_REWARD_ALREADY_OPEN

        self.player.fuben.markTtslRewardStatus(levelId)

        respBag = self.player.bag.add(res.firstReward, constant.ITEM_ADD_TTSL_REWARD, wLog=True)

        dRole = {}
        dRole["roleBase"] = self.player.base.to_init_data()
        dRole["roleAttr"] = self.player.attr.to_update_data()

        dUpdate = self.player.packRespBag(respBag)
        dUpdate["role"] = dRole
        resp = {
            "allUpdate": dUpdate,
            "levelId": levelId,
        }
        return 1, resp