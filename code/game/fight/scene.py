#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import uuid

from corelib.message import observable
from corelib.frame import Game
from game.define import constant, msg_define

from game.fight.team import FightMonsterTeam, FightPlayerTeam
from game.fight.actions import FightActions

@observable
class BaseFight(object):
    def __init__(self, iType):
        self.id = str(uuid.uuid1())
        self.type = iType #战斗类型
        self.maxRound = 5

        self.redTeam = None
        self.blueTeam = None
        self.battlelog = {} #战报
        self.actionList = [] #行动列表

        self.curRound = 0 #当前回合
        self.uid_count = 0
        self.speed_change = 0

        self.sub(msg_define.MSG_FIGHT_SPEED_CHANGE, self.event_speed_change)

    def event_speed_change(self):
        self.speed_change = 1

    def iterFightInsUid(self, head):
        self.uid_count += 1
        return "%s_%s"%(head, self.uid_count)

    def SetRounds(self, rounds):
        self.maxRound = rounds

    def doFight(self):
        """开始战斗"""
        # t1 = time.time()
        #基础信息
        log_base = self.battlelog.setdefault("base", {})
        log_base["id"] = self.id # 战报id
        log_base["type"] = self.type # 战斗类型
        log_base["fb"] = getattr(self, "barrId", 0)# 副本id
        log_base["maxRds"] = self.maxRound #最大回合
        log_base["team"] = []
        redData = self.redTeam.to_client() # 队伍数据---红
        log_base["team"].append(redData)
        blueData = self.blueTeam.to_client()  # 队伍数据---蓝
        log_base["team"].append(blueData)

        #战斗相关
        log_wave = self.battlelog.setdefault("wave", [])

        curRedIndex = 1
        curBlueIndex = 1
        for i in range(5): # 3v3 最多打5波
            red = self.redTeam.waves.get(curRedIndex)
            blue = self.blueTeam.waves.get(curBlueIndex)
            if not red:
                curRedIndex += 1
                continue
            if not blue:
                curBlueIndex += 1
                continue

            log_one = {}
            #公共数据
            log_common = log_one.setdefault("common", {})
            log_common["no"] = i+1
            log_common["t1"] = red.uid
            log_common["t2"] = blue.uid
            #战斗开始前
            log_one["before"] = self.doBefore(red, blue)
            #回合行动
            log_rounds = self.doRounds(red, blue)
            if log_rounds.get("lostCamp", 0) == constant.FIGHT_TEAM_RED:
                curRedIndex += 1
            if log_rounds.get("lostCamp", 0) == constant.FIGHT_TEAM_BLUE:
                curBlueIndex += 1
            log_rounds.pop("lostCamp", 0)
            log_one["rounds"] = log_rounds.pop("rounds", [])
            #战斗结束
            log_one["end"] = self.doEnd(red, blue)

            log_wave.append(log_one)

        #战斗结算
        log_end = self.battlelog.setdefault("end", {})
        winerList = log_end.setdefault("winerList", [])
        if curRedIndex > 3: #红方队伍用尽
            winerList.append(self.blueTeam.pid)
        elif curBlueIndex > 3: #蓝方队伍用尽
            winerList.append(self.redTeam.pid)

        # t2 = time.time()
        # Game.glog.log2File("doFight", "%s|%s" % (t2 - t1, self.iType))
        return self.battlelog

    def initActionList(self, red, blue):
        all_first = [] #优先行动列表
        all_normal = [] #普通行动列表

        for fighter in red.position.values():
            if fighter.status.first_round == self.curRound:
                all_first.append(fighter)
            else:
                all_normal.append(fighter)

        for fighter in blue.position.values():
            if fighter.status.first_round == self.curRound:
                all_first.append(fighter)
            else:
                all_normal.append(fighter)

        all_first.sort(key=lambda x:x.attr.getSpeed(), reverse=True)
        all_normal.sort(key=lambda x: x.attr.getSpeed(), reverse=True)

        self.actionList = []
        self.actionList.extend(all_first)
        self.actionList.extend(all_normal)

        self.speed_change = 0
        return self.actionList

    def doBefore(self, red, blue):
        #清除所有buff
        for fighter in red.position.values():
            fighter.buff.cleanAll()
        for fighter in blue.position.values():
            fighter.buff.cleanAll()

        log_before = FightActions(constant.FIGHT_DO_TYPE_CONCURRENCE)
        self.safe_pub(msg_define.MSG_FIGHT_WAVE_INIT, log_before)

        return log_before.to_client()

    def doRounds(self, red, blue):
        log_rounds = {}
        log_rounds["rounds"] = []

        for index in range(self.maxRound):
            iRound = index + 1
            log_one_rounds = {}
            log_one_rounds["no"] = iRound

            self.curRound = iRound
            #回合前
            beforelog = self.beforeOneRound(red, blue)
            log_one_rounds["bf"] = beforelog
            #回合中
            inglog = self.doOneRound(red, blue)
            log_one_rounds["ing"] = inglog
            #回合后
            afterlog = self.afterOneRound()
            log_one_rounds["end"] = afterlog

            log_rounds["rounds"].append(log_one_rounds)

            # 每回合末判定某方是否全部死亡
            if red.isAllDead():
                log_rounds["lostCamp"] = constant.FIGHT_TEAM_RED
                break
            if blue.isAllDead():
                log_rounds["lostCamp"] = constant.FIGHT_TEAM_BLUE
                break

        #回合打完还未分出胜负，进攻方失败
        if not log_rounds.get("lostCamp"):
            log_rounds["lostCamp"] = constant.FIGHT_TEAM_RED
        return log_rounds

    def beforeOneRound(self, red, blue):
        beforelog = []
        # =================================== #神器行动阶段================================================
        beforelog_act1 = FightActions(constant.FIGHT_DO_TYPE_CONCURRENCE)


        log_act = beforelog_act1.to_client()
        if log_act:
            beforelog.append(log_act)

        # =================================== #buff生效阶段================================================
        beforelog_buff1 = FightActions(constant.FIGHT_DO_TYPE_CONCURRENCE)


        #回合启动类buff触发(如持续回血
        self.safe_pub(msg_define.MSG_FIGHT_BEFORE_ROUND_1, beforelog_buff1)

        # 回合启动类被动技能触发
        self.safe_pub(msg_define.MSG_FIGHT_BEFORE_ROUND_2, beforelog_buff1)

        log_act = beforelog_buff1.to_client()
        if log_act:
            beforelog.append(log_act)

        # =================================== #buff清算阶段================================================
        beforelog_buff2 = FightActions(constant.FIGHT_DO_TYPE_CONCURRENCE)


        #清算buff
        for fighter in self.actionList:
            fighter.buff.cal_life_round(beforelog_buff2)

        log_act = beforelog_buff2.to_client()
        if log_act:
            beforelog.append(log_act)

        #=================================== #回合前-重算================================================
        #清算技能CD
        for fighter in self.actionList:
            fighter.skill.cd_skill()

        #根据速度排出手顺序
        self.initActionList(red, blue)

        return beforelog

    def doOneRound(self, red, blue):
        log_oneRound = []

        for fighter in self.actionList:
            #=================================== #行动启动阶段================================================
            #行动启动阶段--自身被动触发
            inglog_start1 = FightActions(constant.FIGHT_DO_TYPE_CONCURRENCE)

            self.safe_pub(msg_define.MSG_FIGHT_DO_ROUND_BF_1, inglog_start1)

            log_act = inglog_start1.to_client()
            if log_act:
                log_oneRound.append(log_act)

            # =================================== #行动执行阶段================================================
            # 是否死亡
            if not fighter.status.is_dead:
                inglog_ing1 = FightActions(constant.FIGHT_DO_TYPE_ORDER)

                #选择技能
                curSkill = fighter.skill.getActionSkill()
                #是否受到硬控(无法行动、晕眩、冰冻)
                if fighter.status.hard_control():
                    #todo:添加硬控表现

                    fighter.skill.add_cd(curSkill)
                else:
                    #是否有不能释放主动技能的debuff(沉默、混乱、离间)
                    if fighter.status.soft_control():
                        # todo:添加软控表现

                        fighter.skill.add_cd(curSkill)

                        curSkill = fighter.skill.normal

                    #buff影响后续流程
                    #是否影响目标选择----混乱、离间

                    #多段伤害
                    #选择目标
                    curSkill.execSkill(constant.FIGHT_ACT_POINT_1, red, blue, inglog_ing1)



                    #攻击后
                    curSkill.execSkill(constant.FIGHT_ACT_POINT_2, red, blue, inglog_ing1)

                log_act = inglog_ing1.to_client()
                if log_act:
                    log_oneRound.append(log_act)


            # =================================== #行动结束阶段================================================
            inglog_end1 =  FightActions(constant.FIGHT_DO_TYPE_CONCURRENCE)

            self.safe_pub(msg_define.MSG_FIGHT_DO_ROUND_END_1, inglog_end1)

            log_act = inglog_end1.to_client()
            if log_act:
                log_oneRound.append(log_act)

            if self.speed_change:
                self.initActionList(red, blue)

        return log_oneRound

    def afterOneRound(self):
        afterlog = []

        return afterlog

    def doEnd(self, red, blue):
        log_end = {}

        return log_end


class PVEFight(BaseFight):
    """pve战斗"""
    def __init__(self, iType):
        BaseFight.__init__(self, iType)
        self.barrId = 0  # 副本id

    def init_data(self, playerData, barrId):
        self.redTeam = FightPlayerTeam(self, constant.FIGHT_TEAM_RED, playerData)
        monsterData = self.get_data_by_barrId(barrId)
        self.blueTeam = FightMonsterTeam(self, constant.FIGHT_TEAM_BLUE, monsterData)
        self.barrId = barrId
        # 总回合数
        if self.barrId:
            barrRes = Game.res_mgr.res_barrier.get(self.barrId)
            if barrRes:
                self.maxRound = barrRes.maxRound
        return True

    def get_data_by_barrId(self, barrId):
        monsterData = {}
        barrRes = Game.res_mgr.res_barrier.get(barrId)
        if not barrRes:
            return monsterData

        #第1波
        posRes1 = Game.res_mgr.res_barrierwaves.get(barrRes.monster1)
        if posRes1:
            wave1 = monsterData.setdefault(1, {})
            position1 = {}
            for pos in constant.ALL_BATTLE_POS:
                monster_id = getattr(posRes1, "pos%s"%pos, 0)
                position1[pos] = monster_id
            wave1["position"] = position1
            wave1["relation"] = posRes1.getRelation()

        # 第2波
        posRes2 = Game.res_mgr.res_barrierwaves.get(barrRes.monster2)
        if posRes2:
            wave2 = monsterData.setdefault(2, {})
            position2 = {}
            for pos in constant.ALL_BATTLE_POS:
                monster_id = getattr(posRes2, "pos%s"%pos, 0)
                position2[pos] = monster_id
            wave2["position"] = position2
            wave2["relation"] = posRes2.getRelation()

        # 第3波
        posRes3 = Game.res_mgr.res_barrierwaves.get(barrRes.monster3)
        if posRes3:
            wave3 = monsterData.setdefault(3, {})
            position3 = {}
            for pos in constant.ALL_BATTLE_POS:
                monster_id = getattr(posRes3, "pos%s"%pos, 0)
                position3[pos] = monster_id
            wave3["position"] = position3
            wave3["relation"] = posRes3.getRelation()

        return monsterData



Map_fight_type = {
    constant.FIGHT_TYPE_100: PVEFight, # 挂机Boss = 100,
}