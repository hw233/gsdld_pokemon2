#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import time
import random

from game.define import errcode, constant, msg_define
from game import Game

from corelib import log
from game.fight import createFight

class BossMixin(object):
    if 0:
        from game.core import player as player_md
        player = player_md.Player()

    # 挑战(grBossTZ)
    # 请求
    # 	个人bossid(id, int)
    # 返回
    # 	主动推送刷新(allUpdate, json)
    # 		游戏模型-货币
    # 		游戏模型-角色基础-经验
    # 		游戏模型-boss模块
    # 			个人boss(grBoss, json)
    # 				boss列表(bossList, [json]) #只推送更新的
    # 					个人bossId(id, int)
    # 					今日已挑战次数(num, int)
    # 					是否首通(first, int)0=未首通 1=已首通
    # 					是否已击杀(kill, int)0=未击杀 1=已击杀
    # 		游戏模型-角色背包
    # 	战报(fightLog, json)
    def rc_grBossTZ(self, id):
        bossRes = Game.res_mgr.res_grBoss.get(id)
        if not bossRes:
            return 0, errcode.EC_NORES
        barrRes = Game.res_mgr.res_barrier.get(bossRes.fbId)
        if not barrRes:
            return 0, errcode.EC_NORES
        mstRes = Game.res_mgr.res_monster.get(bossRes.mstId)
        if not mstRes:
            return 0, errcode.EC_NORES
        rewardRes = Game.res_mgr.res_reward.get(barrRes.rewardId)
        if not rewardRes:
            return 0, errcode.EC_NORES
        #判断人物的等级是否大于怪
        iLv = self.player.base.GetLv()
        if iLv < mstRes.level:
            return 0, errcode.EC_GRBOSS_LV_NOT_ENOUGH
        iKill = self.player.boss.GetGrBossTodayKill(id)
        if iKill:
            return 0, errcode.EC_GRBOSS_HAS_KILL
        
        # fightobj = Game.fight_mgr.createFight(constant.FIGHT_TYPE_200)
        # rs = fightobj.init_by_barrId(self.player, barrRes.id)
        # if not rs:
        #     return 0, errcode.EC_INIT_BARR_FAIL
        iNum = self.player.boss.GetGrBossTodayTZ(id)
        if iNum >= barrRes.num: #一天只能挑战一次
            return 0, errcode.EC_GRBOSS_NUM_NOT_ENOUGH

        # fightLog = fightobj.doFight()
        
        fightobj = createFight(constant.FIGHT_TYPE_100)
        rs = fightobj.init_data(self.player.GetFightData(constant.BATTLE_ARRAY_TYPE_NORMAL), 100000)
        if not rs:
            return 0, errcode.EC_INIT_BARR_FAIL
        fightLog = fightobj.doFight()
        log_end = fightLog.get("end", {})
        winerList = log_end.get("winerList", [])
        fightResult = 1 if self.player.id in winerList else 0


        respBag = {}
        if fightResult:
            iNum += 1
            self.player.boss.SetGrBossTodayTZ(id, iNum)
            #设置击杀
            self.player.boss.SetGrBossTodayKill(id)
            # 奖励判断是否已首通
            dReward = rewardRes.doReward()
            if not self.player.boss.IsGrBossFirst(id):
                dReward.update(barrRes.firstReward) #首通奖励
                self.player.boss.SetGrBossFirst(id)
                respBag = self.player.bag.add(dReward, constant.ITEM_ADD_GRBOSS_REWARD, wLog=True)
        # 抛事件
        self.player.safe_pub(msg_define.MSG_GR_BOSS)
        # 打包返回信息
        dUpdate = self.player.packRespBag(respBag)
        dUpdate["bossInfo"] = self.player.boss.to_grboss_data([id])
        resp = {
            "fightLog": fightLog,
            "allUpdate": dUpdate,
        }
        return 1, resp


    # 扫荡(grBossSD)
    # 请求
    # 	个人bossid(id, int)
    # 返回
    # 	主动推送刷新(allUpdate, json)
    # 		游戏模型-货币
    # 		游戏模型-角色基础-经验
    # 		游戏模型-boss模块
    # 			个人boss(grBoss, json)
    # 				boss列表(bossList, [json]) 只推送更新的
    # 					个人bossId(id, int)
    # 					今日已挑战次数(num, int)
    # 					是否首通(first, int)0=未首通 1=已首通
    # 					是否已击杀(kill, int)0=未击杀 1=已击杀
    # 		游戏模型-角色背包
    def rc_grBossSD(self, id):
        bossRes = Game.res_mgr.res_grBoss.get(id)
        if not bossRes:
            return 0, errcode.EC_NORES
        barrRes = Game.res_mgr.res_barrier.get(bossRes.fbId)
        if not barrRes:
            return 0, errcode.EC_NORES
        mstRes = Game.res_mgr.res_monster.get(bossRes.mstId)
        if not mstRes:
            return 0, errcode.EC_NORES
        rewardRes = Game.res_mgr.res_reward.get(barrRes.rewardId)
        if not rewardRes:
            return 0, errcode.EC_NORES
        #没有首通的不允许扫荡
        if not self.player.boss.IsGrBossFirst(id):
            return 0, errcode.EC_GRBOSS_NOT_KILLED
        #判断人物的等级是否大于怪
        iLv = self.player.base.GetLv()
        if iLv < mstRes.level:
            return 0, errcode.EC_GRBOSS_LV_NOT_ENOUGH
        iKill = self.player.boss.GetGrBossTodayKill(id)
        if iKill:
            return 0, errcode.EC_GRBOSS_HAS_KILL
        #设置挑战次数
        iNum = self.player.boss.GetGrBossTodayTZ(id)
        if iNum >= 1:  # 一天只能挑战一次
            return 0, errcode.EC_GRBOSS_NUM_NOT_ENOUGH
        iNum += 1
        self.player.boss.SetGrBossTodayTZ(id, iNum)
        #设置击杀
        self.player.boss.SetGrBossTodayKill(id)
        #击杀奖励
        dReward = rewardRes.doReward()
        respBag = self.player.bag.add(dReward, constant.ITEM_ADD_GRBOSS_REWARD, wLog=True)
        # 抛事件
        self.player.safe_pub(msg_define.MSG_GR_BOSS)
        # 打包返回信息
        dUpdate = self.player.packRespBag(respBag)
        dUpdate["bossInfo"] = self.player.boss.to_grboss_data([id])
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp

    # 一键扫荡(grBossOneKeySD)
    # 请求
    # 返回
    # 	主动推送刷新(allUpdate, json)
    # 		游戏模型-货币
    # 		游戏模型-角色基础-经验
    # 		游戏模型-boss模块
    # 			个人boss(grBoss, json)
    # 				boss列表(bossList, [json]) 只推送更新的
    # 					个人bossId(id, int)
    # 					今日已挑战次数(num, int)
    # 					是否首通(first, int)0=未首通 1=已首通
    # 					是否已击杀(kill, int)0=未击杀 1=已击杀
    # 		游戏模型-角色背包
    def rc_grBossOneKeySD(self):
        vipLv = self.player.vip.GetVipLv()
        vipRes = Game.res_mgr.res_vip.get(vipLv, None)
        if not vipRes:
            return 0, errcode.EC_NORES
        if not vipRes.grBossOneKey:
            return 0, errcode.EC_GR_BOSS_SWEEP_VIP_LIMIT

        keys = list(Game.res_mgr.res_grBoss.keys())
        keys.sort()
        respBag = {}
        resp_keys = []
        for id in keys:
            bossRes = Game.res_mgr.res_grBoss.get(id)
            if not bossRes:
                continue
            barrRes = Game.res_mgr.res_barrier.get(bossRes.fbId)
            if not barrRes:
                continue
            mstRes = Game.res_mgr.res_monster.get(bossRes.mstId)
            if not mstRes:
                continue
            rewardRes = Game.res_mgr.res_reward.get(barrRes.rewardId)
            if not rewardRes:
                continue
            # 没有首通的不允许扫荡
            if not self.player.boss.IsGrBossFirst(id):
                continue
            # 判断人物的等级是否大于怪
            iLv = self.player.base.GetLv()
            if iLv < mstRes.level:
                continue
            iKill = self.player.boss.GetGrBossTodayKill(id)
            if iKill:
                continue
            # 设置挑战次数
            iNum = self.player.boss.GetGrBossTodayTZ(id)
            if iNum >= 1:  # 一天只能挑战一次
                continue
            iNum += 1
            self.player.boss.SetGrBossTodayTZ(id, iNum)
            # 设置击杀
            self.player.boss.SetGrBossTodayKill(id)
            # 击杀奖励
            dReward = rewardRes.doReward()
            respBag1 = self.player.bag.add(dReward, constant.ITEM_ADD_GRBOSS_REWARD, wLog=True)
            respBag = self.player.mergeRespBag(respBag, respBag1)
            resp_keys.append(id)
            # 抛事件
            self.player.safe_pub(msg_define.MSG_GR_BOSS)
        # 打包返回信息
        dUpdate = self.player.packRespBag(respBag)
        dUpdate["bossInfo"] = self.player.boss.to_grboss_data(resp_keys)
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp

    # 打开主界面(qmBossOpenUI)
    # 请求
    # 返回
    # 	全民boss列表(bossList, [json])
    # 		全民bossid(id, int)
    # 		当前血量(curHp, int)
    # 		总血量(maxHp, int)
    # 		争夺人数(num, int)
    # 		状态(status, int)0=未击杀 1=已击杀
    # 		重生时间戳(time, int)
    def rc_qmBossOpenUI(self):
        bossList = Game.rpc_qmboss_mgr.GetAllBossInfo()
        resp = {
            "bossList": bossList,
        }
        return 1, resp

    # 刷新挑战次数(qmBossRefreNum)
    # 请求
    # 返回
    # 	剩余挑战次数(num, int)
    # 	下次恢复时间戳(time, int)
    def rc_qmBossRefreNum(self):
        num = self.player.boss.GetQmBossTZ()
        iTime = self.player.boss.GetQmBossTime()
        resp = {
            "num": num,
            "time": iTime,
        }
        return 1, resp

    # 购买挑战次数(qmBossBuyNum)
    # 请求
    # 返回
    # 	主动推送刷新(allUpdate, json)
    # 		游戏模型-vip模块
    # 			全民boss已购买挑战次数(qmBossTz, int)
    # 		游戏模型-boss模块
    # 			全民boss(qmBoss, json)
    # 				剩余挑战次数(num, int)
    # 				下次恢复时间戳(time, int)
    # 		游戏模型-货币
    def rc_qmBossBuyNum(self):
        resQmBossTzCnt = Game.res_mgr.res_common.get("qmBossTzCnt")
        resQmBossBuyNum = Game.res_mgr.res_common.get("qmBossBuyNum")
        resQmBossTzPirce = Game.res_mgr.res_common.get("qmBossTzPirce")
        if not resQmBossTzCnt or not resQmBossBuyNum or not resQmBossTzPirce:
            return 0, errcode.EC_NORES
        iVipLv = self.player.vip.GetVipLv()
        vipRes = Game.res_mgr.res_vip.get(iVipLv)
        if not vipRes:
            return 0, errcode.EC_NORES
        iBuyCnt = self.player.vip.GetBuyQmBossTz()
        if iBuyCnt >= vipRes.qmBossTz:
            return 0, errcode.EC_QMBOSS_BUY_CNT_LIMIT
        iNum = self.player.boss.GetQmBossTZ()
        if iNum >= resQmBossTzCnt.i: #已经是满的，不需要
            return 0, errcode.EC_QMBOSS_NUM_FULL
        dCost = resQmBossTzPirce.arrayint2
        # 扣道具
        respBag = self.player.bag.costItem(dCost, constant.ITEM_COST_QMBOSS_BUY, wLog=True)
        if not respBag.get("rs", 0):
            return 0, errcode.EC_QMBOSS_BUY_NOT_ENOUGH
        self.player.boss.addQmBossTZ(resQmBossBuyNum.i)
        self.player.vip.SetBuyQmBossTz(iBuyCnt+1)
        # 打包返回信息
        dUpdate = self.player.packRespBag(respBag)
        dUpdate["bossInfo"] = {"qmBoss":dict(num=self.player.boss.GetQmBossTZ(), time=self.player.boss.GetQmBossTime())}
        dUpdate["vipInfo"] = dict(qmBossTz=self.player.vip.GetBuyQmBossTz())
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp

    # 请求争夺人数(qmBossFighterNum)
    # 请求
    # 	全民bossid(id, int)
    # 返回
    # 	争夺列表(fighters, [json])
    # 		名次(rank, int)
    # 		玩家名称(name, string)
    # 		伤害(hurt, int)
    def rc_qmBossFighterNum(self, id):
        fighters = Game.rpc_qmboss_mgr.GetFighterData(id)
        resp = {
            "fighters": fighters,
        }
        return 1, resp

    # 请求击杀列表(qmBossKillRecord)
    # 请求
    # 	全民bossid(id, int)
    # 返回
    # 	击杀列表(killList, [json])
    # 		击杀时间戳(time, int)
    # 		玩家名称(name, string)
    # 		战力(fa, int)
    def rc_qmBossKillRecord(self, id):
        killList = Game.rpc_qmboss_mgr.GetKillList(id)
        resp = {
            "killList": killList,
        }
        return 1, resp

    # boss提醒设置(qmBossSetNotice)
    # 请求
    # 	提醒列表(NoticeList, [int])
    # 		全民bossid
    # 	注意：发上来的服务器置1提醒，剩下的全部清0
    # 返回
    def rc_qmBossSetNotice(self, NoticeList):
        self.player.boss.SetQmBossRemind(NoticeList)
        return 1, None

    # 挑战(qmBossTZ)
    # 请求
    # 	全民bossid(id, int)
    # 返回
    # 	自己的伤害(hurt, int)
    # 	争夺列表(fighters, [json])
    # 		名次(rank, int)
    # 		玩家名称(name, int)
    # 		伤害(hurt, int)
    # 	战报(fightLog, json)
    # 注意：挑战之后主动请求界面数据
    def rc_qmBossTZ(self, id):
        resQmBoss = Game.res_mgr.res_qmBoss.get(id)
        if not resQmBoss:
            return 0, errcode.EC_NORES
        barrRes = Game.res_mgr.res_barrier.get(resQmBoss.fbId)
        if not barrRes:
            return 0, errcode.EC_NORES
        tzRewardRes = Game.res_mgr.res_reward.get(resQmBoss.tzReward)
        if not tzRewardRes:
            return 0, errcode.EC_NORES
        killRewardRes = Game.res_mgr.res_reward.get(resQmBoss.killReward)
        if not killRewardRes:
            return 0, errcode.EC_NORES
        iTZNum = self.player.boss.GetQmBossTZ()
        if iTZNum <= 0:
            return 0, errcode.EC_QMBOSS_TZ_NOT_ENOUGH
        #异步获取boss数据
        bossInfo = Game.rpc_qmboss_mgr.GetTZInfo(id, self.player.id)
        if not bossInfo:
            return 0, errcode.EC_QMBOSS_NOT_FIND
        status = bossInfo.get("status", 0)
        if status:
            return 0, errcode.EC_QMBOSS_HAS_KILL
        # fightobj = Game.fight_mgr.createFight(constant.FIGHT_TYPE_201)
        # rs = fightobj.init_by_barrId(self.player, barrRes.id)
        # if not rs:
        #     return 0, errcode.EC_INIT_BARR_FAIL
        #扣除挑战次数
        self.player.boss.delQmBossTZ(1)
        #修改怪物血量
        # curHp = bossInfo.get("curHp", 0)
        # fightobj.fix_monster_hp({resQmBoss.mstId:curHp})
        #战斗
        # fightLog = fightobj.doFight(logMstId=resQmBoss.mstId)

        fightobj = createFight(constant.FIGHT_TYPE_100)
        rs = fightobj.init_data(self.player.GetFightData(constant.BATTLE_ARRAY_TYPE_NORMAL), 100000)
        if not rs:
            return 0, errcode.EC_INIT_BARR_FAIL
        fightLog = fightobj.doFight()
        log_end = fightLog.get("end", {})
        winerList = log_end.get("winerList", [])
        fightResult = 1 if self.player.id in winerList else 0

        
        #同步数据
        # hurt = curHp - fightLog.get("mstData", {}).get(constant.ATTR_HP, 0)
        hurt=999
        fightInfo = {
            "pid" : self.player.id,
            "name" : self.player.name,
            "fa" : self.player.base.fa,
            "portrait": self.player.myhead.getPortrait(),  # 头像
            "headframe": self.player.myhead.getHeadframe(),  # 头像框
            "hurt" : hurt
        }
        #是否击杀由远端精确控制
        isKill = Game.rpc_qmboss_mgr.FightBoss(id, fightInfo)
        if isKill: #击杀
            print("=============kill qmboss====")
            mailRes = Game.res_mgr.res_mail.get(constant.MAIL_ID_BOSS_KILL_REWARD_LK, None)
            Game.rpc_mail_mgr.sendPersonMail(self.player.id, mailRes.title, mailRes.content, resQmBoss.lkmailReward, push=False)

            dReward = killRewardRes.doReward()
        else:
            dReward = tzRewardRes.doReward()

        respBag = self.player.bag.add(dReward, constant.ITEM_ADD_QMBOSS_REWARD, wLog=True)

        # 抛事件
        self.player.safe_pub(msg_define.MSG_QM_BOSS)
        # 打包返回信息
        dUpdate = self.player.packRespBag(respBag)
        #全民boss 看到的都是挑战成功
        # fightLog["result"]={}
        # fightLog["end"]["win"] = 1
        fightLog["end"]["winerList"] = [self.player.id]
        resp = {
            "id": id,
            "hurt": bossInfo.get("myHurt", 0),
            "fighters": bossInfo.get("fighters", []),
            "fightLog": fightLog,
            "allUpdate": dUpdate,
        }
        return 1, resp

    # 复活并挑战(qmBossFHandTZ)
    # 请求
    # 	全民bossid(id, int)
    # 返回
    # 	自己的伤害(hurt, int)
    # 	争夺列表(fighters, [json])
    # 		名次(rank, int)
    # 		玩家名称(name, int)
    # 		伤害(hurt, int)
    # 	战报(fightLog, json)
    # 	主动推送刷新(allUpdate, json)
    # 		游戏模型-货币
    # 		游戏模型-角色背包
    # 		游戏模型-角色基础-经验
    # 注意：挑战之后主动请求界面数据
    def rc_qmBossFHandTZ(self, id):
        # 全民boss是否可复活 vip 控制
        iVipLv = self.player.vip.GetVipLv()
        vipRes = Game.res_mgr.res_vip.get(iVipLv)
        if not vipRes:
            return 0, errcode.EC_NORES
        if not vipRes.qmBossFh:
            return 0, errcode.EC_QMBOSS_REBORN_LIMIT

        resQmBoss = Game.res_mgr.res_qmBoss.get(id)
        if not resQmBoss:
            return 0, errcode.EC_NORES
        if not resQmBoss.relive: #不可复活
            return 0, errcode.EC_QMBOSS_REBORN_LIMIT
        barrRes = Game.res_mgr.res_barrier.get(resQmBoss.fbId)
        if not barrRes:
            return 0, errcode.EC_NORES
        tzRewardRes = Game.res_mgr.res_reward.get(resQmBoss.tzReward)
        if not tzRewardRes:
            return 0, errcode.EC_NORES
        killRewardRes = Game.res_mgr.res_reward.get(resQmBoss.killReward)
        if not killRewardRes:
            return 0, errcode.EC_NORES
        monsterRes = Game.res_mgr.res_monster.get(resQmBoss.mstId)
        if not monsterRes:
            return 0, errcode.EC_NORES
        iTZNum = self.player.boss.GetQmBossTZ()
        if iTZNum <= 0:
            return 0, errcode.EC_QMBOSS_TZ_NOT_ENOUGH
        # 异步获取boss数据
        bossInfo = Game.rpc_qmboss_mgr.GetTZInfo(id, self.player.id)
        if not bossInfo:
            return 0, errcode.EC_QMBOSS_NOT_FIND
        status = bossInfo.get("status", 0)
        if not status:
            return 0, errcode.EC_QMBOSS_ALIVE
        # fightobj = Game.fight_mgr.createFight(constant.FIGHT_TYPE_201)
        # rs = fightobj.init_by_barrId(self.player, barrRes.id)
        # if not rs:
        #     return 0, errcode.EC_INIT_BARR_FAIL
        #复活材料判断
        # 扣道具
        respBag = self.player.bag.costItem(resQmBoss.cost1, constant.ITEM_COST_QMBOSS_REBORN, wLog=True)
        if not respBag.get("rs", 0):
            # 扣道具
            respBag1 = self.player.bag.costItem(resQmBoss.cost2, constant.ITEM_COST_QMBOSS_REBORN, wLog=True)
            respBag = self.player.mergeRespBag(respBag, respBag1)
            if not respBag1.get("rs", 0):
                return 0, errcode.EC_QMBOSS_REBORN_NOT_ENOUGH
        #扣除挑战次数
        self.player.boss.delQmBossTZ(1)
        #战斗
        # fightLog = fightobj.doFight(logMstId=resQmBoss.mstId)
        #同步数据

        fightobj = createFight(constant.FIGHT_TYPE_100)
        rs = fightobj.init_data(self.player.GetFightData(constant.BATTLE_ARRAY_TYPE_NORMAL), 100000)
        if not rs:
            return 0, errcode.EC_INIT_BARR_FAIL
        fightLog = fightobj.doFight()
        log_end = fightLog.get("end", {})
        winerList = log_end.get("winerList", [])
        fightResult = 1 if self.player.id in winerList else 0

        # curHp = monsterRes.attr.get(constant.ATTR_HP, 0)
        # hurt = curHp - fightLog.get("mstData", {}).get(constant.ATTR_HP, 0)
        curHp = monsterRes.attr.get(constant.ATTR_HP, 0)
        hurt = curHp - fightLog.get("mstData", {}).get(constant.ATTR_HP, 0)
        fightInfo = {
            "pid" : self.player.id,
            "name" : self.player.name,
            "fa" : self.player.base.fa,
            "portrait": self.player.myhead.getPortrait(),  # 头像
            "headframe": self.player.myhead.getHeadframe(),  # 头像框
            "hurt" : hurt
        }
        #是否击杀由远端精确控制
        isKill = Game.rpc_qmboss_mgr.FightBoss(id, fightInfo, reborn=1)
        if isKill: #击杀

            print("=============kill qmboss=2===")
            mailRes = Game.res_mgr.res_mail.get(constant.MAIL_ID_BOSS_KILL_REWARD_LK, None)
            Game.rpc_mail_mgr.sendPersonMail(self.player.id, mailRes.title, mailRes.content, resQmBoss.lkmailReward, push=False)

            dReward = killRewardRes.doReward()
        else:
            dReward = tzRewardRes.doReward()


        respBag2 = self.player.bag.add(dReward, constant.ITEM_ADD_QMBOSS_REWARD, wLog=True)
        respBag = self.player.mergeRespBag(respBag, respBag2)

        # 抛事件
        self.player.safe_pub(msg_define.MSG_QM_BOSS)
        # 打包返回信息
        dUpdate = self.player.packRespBag(respBag)
        # 全民boss 看到的都是挑战成功
        fightLog["result"]["win"] = 1
        fightLog["result"]["winerList"] = [self.player.id]
        resp = {
            "hurt": bossInfo.get("myHurt", 0),
            "killList": bossInfo.get("fighters", []),
            "fightLog": fightLog,
            "allUpdate": dUpdate,
        }
        return 1, resp

    # 打开野外Boss主界面(ywBossOpenUI)
    # 请求
    # 返回
    # 	野外Boss列表(ywBossList, [json])
    # 		野外BossId(id, int)
    # 		状态(status, int)1=已刷新 2=已逃跑 3=已击杀
    def rc_ywBossOpenUI(self):
        bossList = Game.rpc_ywboss_mgr.GetAllBossInfo()
        resp = {
            "ywBossList": bossList,
        }
        return 1, resp

    # 进入野外Boss详情界面(ywBossInfo)
    # 请求
    # 	野外BossId(id, int)
    # 返回
    # 	野外BossId(id, int)
    # 	当前血量(curHp, int)
    # 	总血量(maxHp, int)
    # 	占领者id(rid, int)
    # 	占领者性别(sex, int)
    # 	占领者名称(name, string)
    # 	占领结束时间戳(time, int)
    # 	野外Boss今日已挑战次数(todayNum, int)
    # 	野外Boss今日最后一次挑战时间(LastTime, int)
    def rc_ywBossInfo(self, id):
        resp = Game.rpc_ywboss_mgr.GetBossInfo(id)
        resp["todayNum"] = self.player.boss.GetYwBossTodayTZ()
        resp["LastTime"] = self.player.boss.GetYwBossLastTZTime()
        resp["id"] = id
        return 1, resp

    # 野外Boss挑战(ywBossTZ)
    # 请求
    # 	野外BossId(id, int)
    # 	是否花元宝清除cd(clean, int)
    # 返回
    # 	野外BossId(id, int)
    # 	当前血量(curHp, int)
    # 	总血量(maxHp, int)
    # 	占领者id(rid, int)
    # 	占领者性别(sex, int)
    # 	占领者名称(name, string)
    # 	占领结束时间戳(time, int)
    # 	状态(status, int)1=已刷新 2=已逃跑 3=已击杀
    # 	战报(fightLog, json)
    # 	主动推送刷新(allUpdate, json)
    # 		游戏模型-货币
    # 		游戏模型-角色基础-经验
    # 		游戏模型-角色背包
    def rc_ywBossTZ(self, id, clean):
        resYwBoss = Game.res_mgr.res_ywBoss.get(id)
        if not resYwBoss:
            return 0, errcode.EC_NORES
        barrRes = Game.res_mgr.res_barrier.get(resYwBoss.fbId)
        if not barrRes:
            return 0, errcode.EC_NORES
        rewardRes = Game.res_mgr.res_reward.get(barrRes.rewardId)
        if not rewardRes:
            return 0, errcode.EC_NORES
        monsterRes = Game.res_mgr.res_monster.get(resYwBoss.mstId)
        if not monsterRes:
            return 0, errcode.EC_NORES
        #等级不够
        iLv = self.player.base.GetLv()
        if iLv < monsterRes.level:
            return 0, errcode.EC_YWBOSS_LV_LIMIT
        rs, bossInfo = Game.rpc_ywboss_mgr.CheckYwBossTZ(self.player.id, id)
        if not rs:
            return 0, errcode.EC_YWBOSS_HAS_OCCUPY
        status = bossInfo.get("status", 0)
        if status != 1: #1=已刷新
            return 0, errcode.EC_YWBOSS_STATUS_ERR
        resYwBossFreeNum = Game.res_mgr.res_common.get("ywBossFreeNum") # 野外boss免CD挑战次数
        resYwBossCdArr = Game.res_mgr.res_common.get("ywBossCdArr") # 野外boss免CD次数之后的挑战CD(分钟)
        resYwBossCleanCdCost = Game.res_mgr.res_common.get("ywBossCleanCdCost") # 野外boss清除1分钟cd消耗钻石
        if not resYwBossFreeNum and not resYwBossCdArr and not resYwBossCleanCdCost:
            return 0, errcode.EC_NORES
        iTodayNum = self.player.boss.GetYwBossTodayTZ()
        dCost = {}
        if iTodayNum >= resYwBossFreeNum.i:
            cdNum = iTodayNum + 1 - resYwBossFreeNum.i
            cdTime = resYwBossCdArr.arrayint2.get(cdNum)
            if not cdTime:
                maxKey = max(list(resYwBossCdArr.arrayint2.keys()))
                cdTime = resYwBossCdArr.arrayint2.get(maxKey)
            now = int(time.time())
            iLastTZTime = self.player.boss.GetYwBossLastTZTime()
            passTime = now - iLastTZTime
            needTime = cdTime*60 - passTime
            if needTime > 0:
                if clean:
                    dCost[constant.CURRENCY_BINDGOLD] = resYwBossCleanCdCost.i * int((needTime/60 + 1))
                else:
                    return 0, errcode.EC_YWBOSS_CD
        respBag = {}
        # 高级boss挑战需要挑战令，失去归属权时不返还挑战令
        # 归属权是自己时候再次挑战不消耗令
        rid = bossInfo.get("rid", 0)
        if rid != self.player.id:
            dCost.update(resYwBoss.cost)
            # 扣道具
            respBag1 = self.player.bag.costItem(dCost, constant.ITEM_COST_YWBOSS_FIGHT, wLog=True)
            respBag = self.player.mergeRespBag(respBag, respBag1)
            if not respBag1.get("rs", 0):
                return 0, errcode.EC_YWBOSS_FIGHT_NOT_ENOUGH
        #有占领者
        bossStatus = 0
        other = None
        if rid and rid != self.player.id:
            from game.mgr.player import get_rpc_player
            # fightobj = Game.fight_mgr.createFight(constant.FIGHT_TYPE_204)
            # other = get_rpc_player(rid)
            # if not other:
            #     return 0, errcode.EC_INIT_BARR_FAIL
            # rs = fightobj.init_players(self.player, other)
            # if not rs:
            #     return 0, errcode.EC_INIT_BARR_FAIL
            # fightobj.SetRounds(30)
            # fightLog = fightobj.doFight()
            fightobj = createFight(constant.FIGHT_TYPE_100)
            rs = fightobj.init_data(self.player.GetFightData(constant.BATTLE_ARRAY_TYPE_NORMAL), 100000)
            if not rs:
                return 0, errcode.EC_INIT_BARR_FAIL
            fightLog = fightobj.doFight()
            log_end = fightLog.get("end", {})
            winerList = log_end.get("winerList", [])
            fightResult = 1 if self.player.id in winerList else 0

            if fightResult:
                fightInfo = {
                    "pid": self.player.id,  # 占领者id(rid, int)
                    "sex": self.player.base.GetSex(),  # 占领者性别(sex, int)
                    "name": self.player.name,  # 占领者名称(name, string)
                    "fa": self.player.base.fa, # 占领者战力(fa, int)
                    "portrait": self.player.myhead.getPortrait(), #占领者头像
                    "headframe": self.player.myhead.getHeadframe(), #占领者头像框
                }
                Game.rpc_ywboss_mgr.occupyBoss(id, fightInfo, rid)
        else: #无占领者
            # fightobj = Game.fight_mgr.createFight(constant.FIGHT_TYPE_202)
            # rs = fightobj.init_by_barrId(self.player, barrRes.id)
            # if not rs:
            #     return 0, errcode.EC_INIT_BARR_FAIL
            # 修改怪物血量
            # curHp = bossInfo.get("curHp", 0)
            # fightobj.fix_monster_hp({resYwBoss.mstId: curHp})
            # 战斗
            # fightLog = fightobj.doFight(logMstId=resYwBoss.mstId)

            fightobj = createFight(constant.FIGHT_TYPE_100)
            rs = fightobj.init_data(self.player.GetFightData(constant.BATTLE_ARRAY_TYPE_NORMAL), 100000)
            if not rs:
                return 0, errcode.EC_INIT_BARR_FAIL
            fightLog = fightobj.doFight()
            log_end = fightLog.get("end", {})
            winerList = log_end.get("winerList", [])
            fightResult = 1 if self.player.id in winerList else 0

            # 同步数据
            # hurt = curHp - fightLog.get("mstData", {}).get(constant.ATTR_HP, 0)
            hurt=999
            fightInfo = {
                "pid": self.player.id,  # 占领者id(rid, int)
                "sex": self.player.base.GetSex(),  # 占领者性别(sex, int)
                "name": self.player.name,  # 占领者名称(name, string)
                "fa": self.player.base.fa, # 占领者战力(fa, int)
                "portrait": self.player.myhead.getPortrait(),  # 占领者头像
                "headframe": self.player.myhead.getHeadframe(),  # 占领者头像框
                "hurt": hurt
            }
            # 是否击杀由远端精确控制
            bossStatus = Game.rpc_ywboss_mgr.FightBoss(id, fightInfo)
        isKill = 0
        if bossStatus == 3:
            isKill = 1
        # 打包返回信息
        bossInfo = Game.rpc_ywboss_mgr.GetBossInfo(id)
        #直接击杀奖励
        if isKill:
            respBag2 = self.player.sendYwBossKillReward(id, isTimeout=0)
            respBag = self.player.mergeRespBag(respBag, respBag2)

        dUpdate = self.player.packRespBag(respBag)
        resp = {
            "id": bossInfo.get("id", 0),
            "curHp": bossInfo.get("curHp", 0),
            "maxHp": bossInfo.get("maxHp", 0),
            "rid": bossInfo.get("rid", 0),
            "sex": bossInfo.get("sex", 0),
            "name": bossInfo.get("name", ''),
            "time": bossInfo.get("time", 0),
            "status": bossInfo.get("status", 0),
            "fightLog": fightLog,
            "allUpdate": dUpdate,
            "todayNum": self.player.boss.GetYwBossTodayTZ(),
            "LastTime": self.player.boss.GetYwBossLastTZTime(),
        }
        #同步给另外一个玩家
        if other:
            other.sendYwBossTZ(resp, _no_result=True)
        return 1, resp

    # 查看生死劫记录(ssjBossRecord)
    # 请求
    # 	生死劫配置表id(id, int)
    # 返回
    # 	全服首杀队伍名称列表(firstNames, [string]) 首杀者名字
    # 	首杀回合数(firstRounds, int)
    # 	首杀时间戳(firstTime, int)
    # 	最少回合队伍名称列表(minNames, [string]) 名字
    # 	最少回合数(minRounds, int)
    # 	最少回合击杀时间戳(minTime, int)
    def rc_ssjBossRecord(self, id):
        resp = Game.rpc_ssjboss_mgr.GetBossInfo(id)
        return 1, resp

    # 挑战(ssjBossTZ)
    # 请求
    # 	生死劫配置表id(id, int)
    # 	队伍id(teamId, int)
    # 返回
    # 全队推送(ssjBossTZNotice)只推送真人，机器人过滤
    # 	生死劫配置表id(id, int)
    # 	战报(fightLog, json)
    # 	主动推送刷新(allUpdate, json)
    # 		游戏模型-货币
    # 		游戏模型-角色基础-经验
    # 		游戏模型-角色背包
    # 		游戏模型-boss模块
    # 			生死劫(ssjBoss, json)
    # 				章节数据(allData, [json])
    # 					配置表id(id, int)
    # 					是否已首通(firstFinish, int)
    # 					今天是否已通关(finish, int)
    # 				今日剩余协助次数(num, int)
    def rc_ssjBossTZ(self, id, teamId):
        ssjRes = Game.res_mgr.res_ssjBoss.get(id)
        if not ssjRes:
            return 0, errcode.EC_NORES
        barrRes = Game.res_mgr.res_barrier.get(ssjRes.fbId)
        if not barrRes:
            return
        #前置关卡必须通关
        if id != 1 and not self.player.boss.GetSsjBossFirst(id -1):
            return 0, errcode.EC_SSJBOSS_BARR_LIMIT
        # 是否开启
        if not self.player.checkOpenLimit(constant.SSJ_BOSS_OPEN_ID):
            return 0, errcode.EC_NOLEVEL
        # if self.player.boss.GetSsjBossTodayKill(id):
        #     return 0, errcode.EC_SSJBOSS_HAS_KILLED
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

        # fightobj = Game.fight_mgr.createFight(constant.FIGHT_TYPE_203)
        # rs = fightobj.init_by_barrId(ssjRes.fbId, player1=self.player, player2=players[0][0], player3=players[1][0])
        # if not rs:
        #     return 0, errcode.EC_INIT_BARR_FAIL
        # fightLog = fightobj.doFight()
        # Game.glog.log2File("AttackHandle", "44444|%s"%fightLog)

        fightobj = createFight(constant.FIGHT_TYPE_100)
        rs = fightobj.init_data(self.player.GetFightData(constant.BATTLE_ARRAY_TYPE_NORMAL), 100000)
        if not rs:
            return 0, errcode.EC_INIT_BARR_FAIL
        fightLog = fightobj.doFight()
        log_end = fightLog.get("end", {})
        winerList = log_end.get("winerList", [])
        fightResult = 1 if self.player.id in winerList else 0

        self.player.ssjBossTZNotice(id, fightLog, self.player.id)

        #机器人不推送
        for playerData in players:
            if playerData[1]:
                continue
            playerData[0].ssjBossTZNotice(id, fightLog, self.player.id, _no_result=True)
        #解散队伍
        Game.rpc_team_mgr.DeleteTeam(teamId)
        fightResult = fightLog["result"].get("win", 0)
        if fightResult:
            #上传生死劫结果
            FightInfo = {}
            FightInfo["ssjId"] = id
            FightInfo["round"] = fightLog.get("useRound", 999)
            FightInfo["names"] = names
            Game.rpc_ssjboss_mgr.ReportFight(FightInfo)
        else:
            self.player.safe_pub(msg_define.MSG_XIANSHITUISONGLIBAO_SSJ_F)

        # import ujson
        # Game.glog.log2File("testSsjBossTZ", "%s" % ujson.dumps(fightLog))
        #抛事件
        self.player.safe_pub(msg_define.MSG_SSJ_BOSS)
        return 1, None

    # 扫荡(ssjBossSD)
    # 请求
    # 	生死劫配置表id(id, int)
    # 返回
    # 	生死劫配置表id(id, int)
    # 	主动推送刷新(allUpdate, json)
    # 		游戏模型-货币
    # 		游戏模型-角色基础-经验
    # 		游戏模型-角色背包
    # 		游戏模型-boss模块
    # 			生死劫(ssjBoss, json)
    # 				章节数据(allData, [json])
    # 					配置表id(id, int)
    # 					是否已首通(firstFinish, int)
    # 					今天是否已通关(finish, int)
    # 				今日剩余协助次数(num, int)
    def rc_ssjBossSD(self, id):
        ssjRes = Game.res_mgr.res_ssjBoss.get(id)
        if not ssjRes:
            return 0, errcode.EC_NORES
        # 关卡必须通关
        if not self.player.boss.GetSsjBossFirst(id):
            return 0, errcode.EC_SSJBOSS_BARR_LIMIT
        # 是否开启
        if not self.player.checkOpenLimit(constant.SSJ_BOSS_OPEN_ID):
            return 0, errcode.EC_NOLEVEL
        if self.player.boss.GetSsjBossTodayKill(id):
            return 0, errcode.EC_SSJBOSS_HAS_KILLED
        barrRes = Game.res_mgr.res_barrier.get(ssjRes.fbId)
        if not barrRes:
            return 0, errcode.EC_NORES
        rewardRes = Game.res_mgr.res_reward.get(barrRes.rewardId)
        if not rewardRes:
            return 0, errcode.EC_NORES
        self.player.boss.SetSsjBossTodayKill(id)
        dReward = rewardRes.doReward()

        respBag = self.player.bag.add(dReward, constant.ITEM_ADD_SSJBOSS_REWARD, wLog=True)
        # 抛事件
        self.player.safe_pub(msg_define.MSG_SSJ_BOSS)
        # 打包返回信息
        dUpdate = self.player.packRespBag(respBag)
        dUpdate["bossInfo"] = self.player.boss.to_ssjboss_data([id])
        resp = {
            "id": id,
            "allUpdate": dUpdate,
        }
        return 1, resp

    # 一键扫荡(ssjBossOnekeySD)
    # 请求
    # 返回
    # 	主动推送刷新(allUpdate, json)
    # 		游戏模型-货币
    # 		游戏模型-角色基础-经验
    # 		游戏模型-角色背包
    # 		游戏模型-boss模块
    # 			生死劫(ssjBoss, json)
    # 				章节数据(allData, [json])
    # 					配置表id(id, int)
    # 					是否已首通(firstFinish, int)
    # 					今天是否已通关(finish, int)
    # 				今日剩余协助次数(num, int)
    def rc_ssjBossOnekeySD(self):
        keys = list(Game.res_mgr.res_ssjBoss.keys())
        keys.sort()
        respBag = {}
        resp_keys = []
        for id in keys:
            ssjRes = Game.res_mgr.res_ssjBoss.get(id)
            if not ssjRes:
                continue
            # 关卡必须通关
            if not self.player.boss.GetSsjBossFirst(id):
                continue
            if self.player.boss.GetSsjBossTodayKill(id):
                continue
            barrRes = Game.res_mgr.res_barrier.get(ssjRes.fbId)
            if not barrRes:
                continue
            rewardRes = Game.res_mgr.res_reward.get(barrRes.rewardId)
            if not rewardRes:
                continue
            self.player.boss.SetSsjBossTodayKill(id)
            dReward = rewardRes.doReward()

            respBag1 = self.player.bag.add(dReward, constant.ITEM_ADD_SSJBOSS_REWARD, wLog=True)
            respBag = self.player.mergeRespBag(respBag, respBag1)
            # 抛事件
            self.player.safe_pub(msg_define.MSG_SSJ_BOSS)

            resp_keys.append(id)
        # 打包返回信息
        dUpdate = self.player.packRespBag(respBag)
        dUpdate["bossInfo"] = self.player.boss.to_ssjboss_data(resp_keys)
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp










