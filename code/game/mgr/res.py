#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import ujson
import os
import config
import copy
from collections import UserDict
import pickle
import msgpack

from corelib import log
from corelib.frame import Game

from game.res.resdefine import *
from game.res.ResCommon import ResCommon
from game.res.ResReward import ResReward
from game.res.ResActivity import ResActivity
from game.res.ResBarrierwaves import ResBarrierwaves
from game.res.ResEffect import ResEffect

class ResDict(UserDict):
    def __init__(self, name, *args, **kwargs):
        UserDict.__init__(self, *args, **kwargs)
        self.name = name

    def get(self, key, default=None, notfind2log=True):
        val = UserDict.get(self, key, default=default)
        return val

class ResMgr(object):
    def __init__(self):
        self.res_roleinit = ResDict("res_roleinit")  # 角色初始化表 {id:obj}
        self.res_mapSub = ResDict("res_mapSub") # 地图-关卡 {id:obj}
        self.res_mapWorld = ResDict("res_mapWorld") # 地图-世界 {id:obj}
        self.res_mapObject = ResDict("res_mapObject") # 地图-物件 {id:obj}
        self.res_common = ResDict("res_common") # 全局表 {id:obj}
        self.res_totem = ResDict("res_totem") # 图腾表 {id:obj}
        self.res_totemBj = ResDict("res_totemBj")   # 图腾暴击表 {id:obj}
        self.res_totemRan = ResDict("res_totemRan")  # 图腾随机暴击表 {id:obj}
        self.res_reward = ResDict("res_reward") #奖励表 {id:obj}
        self.res_rescueSystem = ResDict("res_rescueSystem") #救援表 {id:obj}
        self.res_rescueReward = ResDict("res_rescueReward") #救援奖励表 {id:obj}
        self.res_rescueTask = ResDict("res_rescueTask") #救援任务表 {id:obj}
        self.res_rewardpool = ResDict("res_rewardpool") #奖池 {id:obj}
        self.res_item = ResDict("res_item") #道具表 {id:obj}
        self.res_vip = ResDict("res_vip") #vip {id:obj}
        self.res_pet = ResDict("res_pet") #宠物表 {id:obj}reward
        self.res_petlv = ResDict("res_petlv") #宠物等级表 {id:obj}
        self.res_petwash = ResDict("res_petwash") #宠物洗练表 {id:obj}
        self.res_petwashpool = ResDict("res_petwashpool") # 宠物洗练池子 petwashpool
        self.res_petwashstar = ResDict("res_petwashstar") #宠物洗练星级表 {id:obj}
        self.res_petevolve = ResDict("res_petevolve") # 宠物进化
        self.res_petalbum = ResDict("res_petalbum") # 宠物图鉴
        self.res_petrelationship1 = ResDict("res_petrelationship1")  # 宠物连协
        self.res_petrelationship2 = ResDict("res_petrelationship2")  # 宠物队伍加成
        self.res_petrelationship3 = ResDict("res_petrelationship3")  # 宠物羁绊
        self.res_mail = ResDict("res_mail")  # 邮件模板表 {id:obj}
        self.res_marry = ResDict("res_marry")    # 结婚档次
        self.res_marryGift = ResDict("res_marryGift")    # 结婚礼金
        self.res_marryPower = ResDict("res_marryPower")    # 结婚亲密度增长消耗
        self.res_marryLv = ResDict("res_marryLv")    # 结婚亲密度等级
        self.res_house = ResDict("res_house")   # 房子
        self.res_examQuestionPool = ResDict("res_examQuestionPool")  # 题库
        self.res_examAnswerPoint = ResDict("res_examAnswerPoint")    # 答题分数
        self.res_examRankReward = ResDict("res_examRankReward")     # 答题排行奖励
        self.res_grBoss = ResDict("res_grBoss")   # 个人boss表 {id:obj}
        self.res_qmBoss = ResDict("res_qmBoss")  # 全民boss表 {id:obj}
        self.res_ywBoss = ResDict("res_ywBoss")  # 野外boss表 {id:obj}
        self.res_ssjBoss = ResDict("res_ssjBoss")  # 生死劫boss表 {id:obj}
        self.res_chenghao = ResDict("title")  # 称号表 {id:obj}
        self.res_myhead = ResDict("myhead")  # 头像表 {id:obj}
        self.res_niudanSystem = ResDict("niudanSystem")  # 扭蛋系统 {id:obj}
        self.res_niudanPool = ResDict("niudanPool")  # 扭蛋池 {id:obj}
        self.res_niudanXianshi = ResDict("niudanXianshi")  # 扭蛋限时 {id:obj}
        self.res_niudanFuhua = ResDict("niudanFuhua")  # 扭蛋孵化 {id:obj}
        self.res_niudanZhenying = ResDict("niudanZhenying")  # 扭蛋阵营 {id:obj}
        self.res_monster = ResDict("res_monster")  # 怪物表 {id:obj}
        self.res_barrier = ResDict("res_barrier")  # 副本表 {id:obj}
        self.res_barrierwaves = ResDict("res_barrierwaves")  # 怪物布阵
        self.res_cycle = ResDict("res_cycle")  # 周期表 {id:obj}
        self.res_charge = ResDict("res_charge")  # 充值表 {id:obj}
        self.res_chargeQuick = ResDict("res_chargeQuick")  # 充值快速作战表 {id:obj}
        self.res_chargeMonth = ResDict("res_chargeMonth")  # 充值月表 {id:obj}
        self.res_chargeDaily = ResDict("res_chargeDaily")  # 充值日常表 {id:obj}
        self.res_chargeSent = ResDict("res_chargeSent")  # 充值派遣表 {id:obj}
        self.res_activity = ResDict("res_activity")  # 活动表 {id:obj}
        self.res_skill = ResDict("res_skill")  # 技能表 {id:obj}
        self.res_effect = ResDict("res_effect")  # 技能效果表 {id:obj}
        self.res_shopConst = ResDict("res_shopConst")  # 商店系统表 {id:obj}
        self.res_shopGroup = ResDict("res_shopGroup")  # 商店组表 {id:obj}
        self.res_shopQuick = ResDict("res_shopQuick")  # 商店快速购买表 {id:obj}
        self.res_zhuanpanSystem = ResDict("res_zhuanpanPool")  # 转盘系统表 {id:obj}
        self.res_zhuanpanPool = ResDict("res_zhuanpanPool")  # 转盘池表 {id:obj}
        self.res_attrbute = ResDict("res_attrbute")  # 属性定义表 {id:obj}
        self.res_equip = ResDict("res_equip")  # 装备表 {id:obj}
        self.res_encounter = ResDict("res_encounter")  # 遭遇战
        self.res_pavilion = ResDict("res_pavilion")  # 道馆表
        self.res_open = ResDict("res_open")  # open表
        self.res_clfb = ResDict("res_clfb")   # 材料副本表 {id:obj}
        self.res_lwbz = ResDict("res_lwbz")   # 龙王宝藏表 {id:obj}
        self.res_lwbzStarReward = ResDict("res_lwbzStarReward")   # 龙王宝藏星数奖励表 {id:obj}
        self.res_xlys = ResDict("res_xlys")   # 小雷音寺表 {id:obj}
        self.res_xlysBuff = ResDict("res_xlysBuff")   # 小雷音寺buff表 {id:obj}
        self.res_zhudaoxunliReward = ResDict("zhudaoxunliReward") # 诸岛巡礼奖励
        self.res_zhudaoxunliDay = ResDict("zhudaoxunliDay") # 诸岛巡礼周期
        self.res_pvploot = ResDict("res_pvploot")  # 日常pvp连胜奖励
        self.res_pvprank = ResDict("res_pvprank")  # 日常pvp排行奖励
        self.res_pvpmatch = ResDict("res_pvpmatch")  # 日常pvp抢夺匹配
        self.res_kuafuServerNo = ResDict("res_kuafuServerNo") # 跨服配置 {id:obj}
        self.res_kuafuMap = ResDict("kuafuMap")   # 跨服映射
        self.res_kuafuGroup = ResDict("kuafuGroup")   # 跨服分组
        self.res_level = ResDict("res_level")  # 角色等级表 {id:obj}
        self.res_hetiReward = ResDict("hetiReward")   # 合体奖励表 {id:obj}
        self.res_hetiMake = ResDict("hetiMake")   # 合体宠物规则 {id:obj}
        self.res_hetiEvo = ResDict("hetiEvo")   # 合体进化等级配置 {id:obj}
        self.res_gongchengPersonrRank = ResDict("gongchengPersonrRank")   # 攻城个人榜 {id:obj}
        self.res_gongchengGangRank = ResDict("gongchengGangRank")   # 攻城公会帮 {id:obj}
        self.res_gongcheng = ResDict("gongcheng")   # 攻城 {id:obj}
        self.res_gongchengLoginReward = ResDict("res_gongchengLoginReward")  # 攻城登陆天数
        self.res_gongchengLimitReward = ResDict("res_gongchengLimitReward")  # 攻城限购礼包
        self.res_gongchengTask = ResDict("res_gongchengTask")  # 攻城任务页签
        self.res_gongchengShop = ResDict("res_gongchengShop")  # 攻城商店
        self.res_gongchengActive = ResDict("res_gongchengActive")  # 攻城活动
        self.res_guildlv = ResDict("res_guildlv")  # 帮会等级表 guildlv
        self.res_guildSx = ResDict("res_guildSx")  # 帮会上香表 guildSx
        self.res_guildSxBar = ResDict("res_guildSxBar")  # 帮会上香进度表 guildSxBar
        self.res_guildSkill = ResDict("res_guildSkill")  # 帮会技能表 guildSkill
        self.res_guildAct = ResDict("res_guildAct")  # 帮会活跃表 guildAct
        self.res_guildTask = ResDict("res_guildTask")  # 帮会任务表 guildTask
        self.res_guildBarr = ResDict("res_guildBarr")  # 帮会副本表 guildBarr
        self.res_yabiao = ResDict("yabiaoreward")   # 押镖表 {id:obj}
        self.res_diaoyu = ResDict("diaoyureward")   # 钓鱼奖励表 {id:obj}
        self.res_diaoyurank = ResDict("diaoyurank")   # 钓鱼排行奖励表 {id:obj}

        #预处理的各种数据
        self.res_poslv_totem = ResDict("res_poslv_totem") #{(pos, lv):obj}
        self.res_random_totem = []  # [(id，num)...]
        self.res_qalv_petlv = ResDict("res_qalv_petlv")  # 宠物等级
        self.res_idlv_petevolve = ResDict("res_idlv_petevolve")  # 宠物进化
        self.res_typeneed_petalbum = ResDict("res_typeneed_petalbum") #宠物图鉴
        self.res_typelv_petalbum = ResDict("res_typelv_petalbum") #宠物图鉴
        self.res_type_petalbum = ResDict("res_type_petalbum") #宠物图鉴
        self.res_marry_house_attr = ResDict("res_marry_house_attr") # 房子种类阶数属性
        self.res_result_useTime_answerPoint = ResDict("res_result_useTime_answerPoint") # 答题得分
        self.res_group_rewardpool = ResDict("res_group_rewardpool") # 奖池
        self.res_idlv_skill = ResDict("res_idlv_skill")  # {(大类skillId, lv):obj}
        self.res_idstar_petwash = ResDict("res_idstar_petwash")  # {(petid, star):obj}
        self.res_group_subtype_skills_petwashpool = ResDict("res_group_subtype_skills_petwashpool") #洗练分类
        self.res_passId_encounter = ResDict("res_passId_encounter") #遭遇战
        self.res_group_order_effect = ResDict("res_group_order_effect") #技能效果
        self.res_fa_pvpmatch = ResDict("res_fa_pvpmatch") #日常pvp抢夺
        self.res_hetiMakeDict = ResDict("res_hetiMakeDict")
        self.res_type_guildTask = ResDict("res_type_guildTask") #公会任务 {type:[obj]}
        self.res_poslv_guildSkill = ResDict("res_poslv_guildSkill")  # 公会技能 {(pos, lv):obj}
        self.res_typeApet = []
        self.res_typeBpet = []
        self.res_typeCpet = []
        self.res_List_kuafuServerNo = []
        self.res_no2id_kuafuMap = ResDict("no2id_kuafuMap")   #

    def parse(self, load_dict, cls, res_dict, keyType=int, prepareFunc=None):
        res_dict.clear()
        resData = load_dict.pop(cls.RES_TABLE, {})
        for key, oneData in resData.items():
            try:
                resobj = cls()
                resobj.load_from_json(oneData)
                res_dict[keyType(key)] = resobj
            except Exception as resErr:
                log.log_except('res_load_err:%s, %s, %s', resErr, key, oneData)
        if prepareFunc:
            prepareFunc()

    def load(self):
        self.loadByNames()

    def loadByNames(self, names=[]):
        res_file = "res.json"
        res_path = os.path.join(config.res_path, res_file)
        with open(res_path, 'r', encoding='utf-8') as load_f:
            load_dict = ujson.load(load_f)

        if not names or ResMail.RES_TABLE in names:
            self.parse(load_dict, ResMail, self.res_mail)  # 邮件模板表 mail

        if not names or ResSkill.RES_TABLE in names:
            self.parse(load_dict, ResSkill, self.res_skill, prepareFunc=self.init_skill)  # 技能表 skill

        if not names or ResEffect.RES_TABLE in names:
            self.parse(load_dict, ResEffect, self.res_effect, prepareFunc=self.init_effect)  # 技能效果表 skill

        if not names or ResShopConst.RES_TABLE in names:
            self.parse(load_dict, ResShopConst, self.res_shopConst)  # 商店系统表 shopConst

        if not names or ResShopGroup.RES_TABLE in names:
            self.parse(load_dict, ResShopGroup, self.res_shopGroup)  # 商店组表 shopGroup

        if not names or ResShopQuick.RES_TABLE in names:
            self.parse(load_dict, ResShopQuick, self.res_shopQuick)  # 商店快熟购买表 shopQuick

        if not names or ResRoleinit.RES_TABLE in names:
            self.parse(load_dict, ResRoleinit, self.res_roleinit, keyType=str)  # 角色初始化表 roleinit

        if not names or ResMapSub.RES_TABLE in names:
            self.parse(load_dict, ResMapSub, self.res_mapSub)  # 地图-关卡 mapSub

        if not names or ResMapWorld.RES_TABLE in names:
            self.parse(load_dict, ResMapWorld, self.res_mapWorld)  # 地图-世界 mapWorld

        if not names or ResMapObject.RES_TABLE in names:
            self.parse(load_dict, ResMapObject, self.res_mapObject)  # 地图-物件 mapObject

        if not names or ResCommon.RES_TABLE in names:
            self.parse(load_dict, ResCommon, self.res_common, keyType=str)  # 全局表 common

        if not names or ResTotems.RES_TABLE in names:
            self.parse(load_dict, ResTotems, self.res_totem, prepareFunc=self.init_totem)  # 图腾表 totems

        if not names or ResTotemBj.RES_TABLE in names:
            self.parse(load_dict, ResTotemBj, self.res_totemBj)  # 图腾暴击表 totemBj)

        if not names or ResTotemRan.RES_TABLE in names:
            self.parse(load_dict, ResTotemRan, self.res_totemRan, prepareFunc=self.init_totemRanom)  # 图腾随机暴击表 totemRan

        if not names or ResReward.RES_TABLE in names:
            self.parse(load_dict, ResReward, self.res_reward)  # 奖励表 reward

        if not names or ResRescueSystem.RES_TABLE in names:
            self.parse(load_dict, ResRescueSystem, self.res_rescueSystem)  # 救援表 rescueSystem

        if not names or ResRescueReward.RES_TABLE in names:
            self.parse(load_dict, ResRescueReward, self.res_rescueReward)  # 救援奖励表 rescueReward

        if not names or ResRescueTask.RES_TABLE in names:
            self.parse(load_dict, ResRescueTask, self.res_rescueTask)  # 救援奖励表 rescueTask

        if not names or ResRewardpool.RES_TABLE in names:
            self.parse(load_dict, ResRewardpool, self.res_rewardpool, prepareFunc=self.init_rewardpool)  # 奖池
        
        if not names or ResItem.RES_TABLE in names:
            self.parse(load_dict, ResItem, self.res_item)  # 道具表 item

        if not names or ResVip.RES_TABLE in names:
            self.parse(load_dict, ResVip, self.res_vip)  # vip vip

        if not names or ResPet.RES_TABLE in names:
            self.parse(load_dict, ResPet, self.res_pet)  # 宠物表 pet

        if not names or ResPetlv.RES_TABLE in names:
            self.parse(load_dict, ResPetlv, self.res_petlv, prepareFunc=self.init_res_petlv)  # 宠物等级表 petlv

        if not names or ResPetevolve.RES_TABLE in names: #宠物进化
            self.parse(load_dict, ResPetevolve, self.res_petevolve, prepareFunc=self.init_petevolve)

        if not names or ResPetwash.RES_TABLE in names:
            self.parse(load_dict, ResPetwash, self.res_petwash, prepareFunc=self.init_petwash)  # 宠物洗练表 petwash

        if not names or ResPetwashstar.RES_TABLE in names:
            self.parse(load_dict, ResPetwashstar, self.res_petwashstar)  # 宠物洗练星级表 petwashstar

        if not names or ResPetwashpool.RES_TABLE in names:
            self.parse(load_dict, ResPetwashpool, self.res_petwashpool, prepareFunc=self.init_petwashpool)  # 宠物洗练池子 petwashpool

        if not names or ResPetalbum.RES_TABLE in names: #宠物图鉴
            self.parse(load_dict, ResPetalbum, self.res_petalbum, prepareFunc=self.init_petalbum)

        if not names or ResPetrelationship1.RES_TABLE in names: #宠物连协
            self.parse(load_dict, ResPetrelationship1, self.res_petrelationship1)

        if not names or ResPetrelationship2.RES_TABLE in names: #宠物队伍加成
            self.parse(load_dict, ResPetrelationship2, self.res_petrelationship2)

        if not names or ResPetrelationship3.RES_TABLE in names: #宠物羁绊
            self.parse(load_dict, ResPetrelationship3, self.res_petrelationship3)

        if not names or ResMarry.RES_TABLE in names:
            self.parse(load_dict, ResMarry, self.res_marry)

        if not names or ResMarryGift.RES_TABLE in names:
            self.parse(load_dict, ResMarryGift, self.res_marryGift)

        if not names or ResMarryPower.RES_TABLE in names:
            self.parse(load_dict, ResMarryPower, self.res_marryPower)

        if not names or ResMarryLv.RES_TABLE in names:
            self.parse(load_dict, ResMarryLv, self.res_marryLv)

        if not names or ResHouse.RES_TABLE in names:
            self.parse(load_dict, ResHouse, self.res_house, prepareFunc=self.init_marry_house_attr)

        if not names or ResExamQuestionPool.RES_TABLE in names:
            self.parse(load_dict, ResExamQuestionPool, self.res_examQuestionPool)

        if not names or ResExamAnswerPoint.RES_TABLE in names:
            self.parse(load_dict, ResExamAnswerPoint, self.res_examAnswerPoint, prepareFunc=self.init_result_useTime_answerPoint)

        if not names or ResExamRankReward.RES_TABLE in names:
            self.parse(load_dict, ResExamRankReward, self.res_examRankReward)

        if not names or ResGrBoss.RES_TABLE in names:
            self.parse(load_dict, ResGrBoss, self.res_grBoss)  # 个人boss表 grBoss

        if not names or ResQmBoss.RES_TABLE in names:
            self.parse(load_dict, ResQmBoss, self.res_qmBoss)  # 全民boss表 qmBoss

        if not names or ResYwBoss.RES_TABLE in names:
            self.parse(load_dict, ResYwBoss, self.res_ywBoss)  # 野外boss表 ywBoss

        if not names or ResSsjBoss.RES_TABLE in names:
            self.parse(load_dict, ResSsjBoss, self.res_ssjBoss)  # 生死劫boss表 ssjBoss

        if not names or ResTitle.RES_TABLE in names:
            self.parse(load_dict, ResTitle, self.res_chenghao)  # 称号表 title)

        if not names or ResMyhead.RES_TABLE in names:
            self.parse(load_dict, ResMyhead, self.res_myhead)  # 头像表

        if not names or ResNiudanSystem.RES_TABLE in names:
            self.parse(load_dict, ResNiudanSystem, self.res_niudanSystem)  # 扭蛋系统

        if not names or ResMonster.RES_TABLE in names:
            self.parse(load_dict, ResMonster, self.res_monster)  # 怪物表 monster

        if not names or ResBarrier.RES_TABLE in names:
            self.parse(load_dict, ResBarrier, self.res_barrier)  # 副本表 barrier

        if not names or ResBarrierwaves.RES_TABLE in names:
            self.parse(load_dict, ResBarrierwaves, self.res_barrierwaves, prepareFunc=self.init_barrierwaves)  # 怪物布阵
            
        if not names or ResNiudanPool.RES_TABLE in names:
            self.parse(load_dict, ResNiudanPool, self.res_niudanPool)  # 扭蛋奖

        if not names or ResNiudanXianshi.RES_TABLE in names:
            self.parse(load_dict, ResNiudanXianshi, self.res_niudanXianshi)  # 扭蛋限时

        if not names or ResNiudanFuhua.RES_TABLE in names:
            self.parse(load_dict, ResNiudanFuhua, self.res_niudanFuhua)  # 扭蛋孵化

        if not names or ResNiudanZhenying.RES_TABLE in names:
            self.parse(load_dict, ResNiudanZhenying, self.res_niudanZhenying)  # 扭蛋阵营

        if not names or ResCycle.RES_TABLE in names:
            self.parse(load_dict, ResCycle, self.res_cycle)  # 周期表

        if not names or ResCharge.RES_TABLE in names:
            self.parse(load_dict, ResCharge, self.res_charge)  # 充值表

        if not names or ResChargeQuick.RES_TABLE in names:
            self.parse(load_dict, ResChargeQuick, self.res_chargeQuick)  # 充值快速作战表

        if not names or ResChargeMonth.RES_TABLE in names:
            self.parse(load_dict, ResChargeMonth, self.res_chargeMonth)  # 充值月表

        if not names or ResChargeDaily.RES_TABLE in names:
            self.parse(load_dict, ResChargeDaily, self.res_chargeDaily)  # 充值日常表

        if not names or ResChargeSent.RES_TABLE in names:
            self.parse(load_dict, ResChargeSent, self.res_chargeSent)  # 充值派遣表

        if not names or ResActivity.RES_TABLE in names:
            self.parse(load_dict, ResActivity, self.res_activity)  # 活动表
        
        if not names or ResZhuanpanSystem.RES_TABLE in names:
            self.parse(load_dict, ResZhuanpanSystem, self.res_zhuanpanSystem)  # 转盘系统
        
        if not names or ResZhuanpanPool.RES_TABLE in names:
            self.parse(load_dict, ResZhuanpanPool, self.res_zhuanpanPool)  # 转盘池

        if not names or ResAttrbute.RES_TABLE in names:
            self.parse(load_dict, ResAttrbute, self.res_attrbute, keyType=str)  # 属性定义表 attrbute

        if not names or ResEquip.RES_TABLE in names:
            self.parse(load_dict, ResEquip, self.res_equip)  # 装备表 equip

        if not names or ResEncounter.RES_TABLE in names:
            self.parse(load_dict, ResEncounter, self.res_encounter, prepareFunc=self.init_encounter)

        if not names or ResPavilion.RES_TABLE in names:
            self.parse(load_dict, ResPavilion, self.res_pavilion)

        if not names or ResOpen.RES_TABLE in names:
            self.parse(load_dict, ResOpen, self.res_open)  # open表 open

        if not names or ResClfb.RES_TABLE in names:
            self.parse(load_dict, ResClfb, self.res_clfb)  # 材料副本表 clfb
        
        if not names or ResLwbz.RES_TABLE in names:
            self.parse(load_dict, ResLwbz, self.res_lwbz)  # 龙王宝藏表 lwbz
        
        if not names or ResLwbzStarReward.RES_TABLE in names:
            self.parse(load_dict, ResLwbzStarReward, self.res_lwbzStarReward)  # 龙王宝藏星数奖励表 lwbzStarReward
        
        if not names or ResXlys.RES_TABLE in names:
            self.parse(load_dict, ResXlys, self.res_xlys)  # 小雷音寺表  xlys
        
        if not names or ResXlysBuff.RES_TABLE in names:
            self.parse(load_dict, ResXlysBuff, self.res_xlysBuff, keyType=str)  # 小雷音寺Buff表  xlysBuff

        if not names or ResZhudaoxunliReward.RES_TABLE in names:
            self.parse(load_dict, ResZhudaoxunliReward, self.res_zhudaoxunliReward)   # 诸岛巡礼奖励
        
        if not names or ResZhudaoxunliDay.RES_TABLE in names:
            self.parse(load_dict, ResZhudaoxunliDay, self.res_zhudaoxunliDay)   # 诸岛周期

        if not names or ResPvploot.RES_TABLE in names:
            self.parse(load_dict, ResPvploot, self.res_pvploot)

        if not names or ResPvprank.RES_TABLE in names:
            self.parse(load_dict, ResPvprank, self.res_pvprank)

        if not names or ResPvpmatch.RES_TABLE in names:
            self.parse(load_dict, ResPvpmatch, self.res_pvpmatch, prepareFunc=self.init_pvpmatch)

        if not names or ResKuafuServerNo.RES_TABLE in names:
            self.parse(load_dict, ResKuafuServerNo, self.res_kuafuServerNo, keyType=str, prepareFunc=self.init_kuafuServerNo)  # 跨服配置 kuafuServerNo

        if not names or ResKuafuMap.RES_TABLE in names:
            self.parse(load_dict, ResKuafuMap, self.res_kuafuMap, prepareFunc=self.init_kuafuMap)  # 跨服对应表
        
        if not names or ResKuafuGroup.RES_TABLE in names:
            self.parse(load_dict, ResKuafuGroup, self.res_kuafuGroup)  # 跨服分组

        if not names or ResLevel.RES_TABLE in names:
            self.parse(load_dict, ResLevel, self.res_level)  # 角色等级表 level

        if not names or ResHetiReward.RES_TABLE in names:
            self.parse(load_dict, ResHetiReward, self.res_hetiReward)  # 合体奖励表 hetiReward)

        if not names or ResHetiMake.RES_TABLE in names:
            self.parse(load_dict, ResHetiMake, self.res_hetiMake, prepareFunc=self.init_hetiMake)  # 合体宠物规则

        if not names or ResHetiEvo.RES_TABLE in names:
            self.parse(load_dict, ResHetiEvo, self.res_hetiEvo, prepareFunc=self.init_hetiEvo)  # 合体进化等级

        if not names or ResGongchengPersonrRank.RES_TABLE in names:
            self.parse(load_dict, ResGongchengPersonrRank, self.res_gongchengPersonrRank)  # 攻城个人排行 gongchengPersonrRank
        
        if not names or ResGongchengGangRank.RES_TABLE in names:
            self.parse(load_dict, ResGongchengGangRank, self.res_gongchengGangRank)  # 攻城公会排行 gongchengGangRank
        
        if not names or ResGongcheng.RES_TABLE in names:
            self.parse(load_dict, ResGongcheng, self.res_gongcheng)  # 攻城 gongcheng

        if not names or ResGongchengLoginReward.RES_TABLE in names:
            self.parse(load_dict, ResGongchengLoginReward, self.res_gongchengLoginReward)

        if not names or ResGongchengLimitReward.RES_TABLE in names:
            self.parse(load_dict, ResGongchengLimitReward, self.res_gongchengLimitReward)

        if not names or ResGongchengTask.RES_TABLE in names:
            self.parse(load_dict, ResGongchengTask, self.res_gongchengTask)

        if not names or ResGongchengShop.RES_TABLE in names:
            self.parse(load_dict, ResGongchengShop, self.res_gongchengShop)

        if not names or ResGongchengActive.RES_TABLE in names:
            self.parse(load_dict, ResGongchengActive, self.res_gongchengActive)

        if not names or ResGuildlv.RES_TABLE in names:
            self.parse(load_dict, ResGuildlv, self.res_guildlv)  # 帮会等级表 guildlv
        
        if not names or ResGuildSx.RES_TABLE in names:
            self.parse(load_dict, ResGuildSx, self.res_guildSx)  # 帮会上香表 guildSx
        
        if not names or ResGuildSxBar.RES_TABLE in names:
            self.parse(load_dict, ResGuildSxBar, self.res_guildSxBar)  # 帮会上香进度表 guildSxBar
        
        if not names or ResGuildSkill.RES_TABLE in names:
            self.parse(load_dict, ResGuildSkill, self.res_guildSkill, prepareFunc=self.init_guildSkill)  # 帮会技能表 guildSkill
        
        if not names or ResGuildAct.RES_TABLE in names:
            self.parse(load_dict, ResGuildAct, self.res_guildAct)  # 帮会活跃表 guildAct
        
        if not names or ResGuildTask.RES_TABLE in names:
            self.parse(load_dict, ResGuildTask, self.res_guildTask, prepareFunc=self.init_guildTask)  # 帮会任务表 guildTask
        
        if not names or ResGuildBarr.RES_TABLE in names:
            self.parse(load_dict, ResGuildBarr, self.res_guildBarr)  # 帮会副本表 guildBarr

        if not names or ResYabiaoreward.RES_TABLE in names:
            self.parse(load_dict, ResYabiaoreward, self.res_yabiao)  # 押镖

        if not names or ResDiaoyureward.RES_TABLE in names:
            self.parse(load_dict, ResDiaoyureward, self.res_diaoyu)  # 钓鱼表 diaoyu)
        
        if not names or ResDiaoyurank.RES_TABLE in names:
            self.parse(load_dict, ResDiaoyurank, self.res_diaoyurank)  # 钓鱼排行表 diaoyurank)

    ########################
    ########################
    ########################

    def init_hetiEvo(self):

        self.res_typeApet = []
        self.res_typeBpet = []
        self.res_typeCpet = []

        for k,v in self.res_hetiEvo.items():

            if 1==len(v.petIds):
                self.res_typeApet.append(k)
            elif 2==len(v.petIds):
                self.res_typeBpet.append(k)
            elif 3==len(v.petIds):
                self.res_typeCpet.append(k)

    def init_hetiMake(self):
        self.res_hetiMakeDict.clear()

        keys=list(self.res_hetiMake.keys())
        keys.sort()
        for key in keys:
            
            obj=self.res_hetiMake[key]

            level=self.res_hetiMakeDict.get(obj.level,{},notfind2log=False)
            ver=level.get(obj.ver,[])
            
            ver.append(obj.match)

            level[obj.ver]=ver
            self.res_hetiMakeDict[obj.level] = level

    def init_barrierwaves(self):
        for obj in self.res_barrierwaves.values():
            obj.getRelation()

    def init_encounter(self):
        self.res_passId_encounter.clear()
        for obj in self.res_encounter.values():
            key = obj.passId
            self.res_passId_encounter[key] = obj

    def init_petwashpool(self):
        self.res_group_subtype_skills_petwashpool.clear()
        for obj in self.res_petwashpool.values():
            group = self.res_group_subtype_skills_petwashpool.setdefault(obj.group, {})
            skillRes = Game.res_mgr.res_skill.get(obj.skill)
            if skillRes:
                one_type = group.setdefault(skillRes.subType, [])
                one_type.append((obj.skill, obj.rate))
                group[skillRes.subType] = one_type
                self.res_group_subtype_skills_petwashpool[obj.group] = group

    def init_petwash(self):
        self.res_idstar_petwash.clear()
        for obj in self.res_petwash.values():
            key = (obj.petId, obj.star)
            self.res_idstar_petwash[key] = obj

    def init_skill(self):
        self.res_idlv_skill.clear()
        for obj in self.res_skill.values():
            key = (obj.skillId, obj.level)
            self.res_idlv_skill[key] = obj

    def init_effect(self):
        self.res_group_order_effect.clear()
        for obj in self.res_effect.values():
            obj.init()
            key = (obj.group, obj.order)
            self.res_group_order_effect[key] = obj

    def init_rewardpool(self):
        self.res_group_rewardpool.clear()
        for obj in self.res_rewardpool.values():
            group = self.res_group_rewardpool.setdefault(obj.group, [])
            group.append((obj.id, obj.rate))
            self.res_group_rewardpool[obj.group] = group

    def init_result_useTime_answerPoint(self):
        self.res_result_useTime_answerPoint.clear()
        for obj in self.res_examAnswerPoint.values():
            for x in range(obj.interval):
                key = (obj.correct, x+1)
                if not key in self.res_result_useTime_answerPoint:
                    self.res_result_useTime_answerPoint[key] = obj.point

    def init_marry_house_attr(self):
        self.res_marry_house_attr.clear()
        for house in self.res_house.values():
            self.res_marry_house_attr[(1, house.id)] = house.common
            self.res_marry_house_attr[(2, house.id)] = house.high
            self.res_marry_house_attr[(3, house.id)] = house.luxury

    def init_petalbum(self):
        self.res_typeneed_petalbum.clear()
        self.res_typelv_petalbum.clear()
        self.res_type_petalbum.clear()
        for obj in self.res_petalbum.values():
            key = (obj.eleType, obj.need)
            self.res_typeneed_petalbum[key] = obj

            key = (obj.eleType, obj.lv)
            self.res_typelv_petalbum[key] = obj

            type_petalbum = self.res_type_petalbum.setdefault(obj.eleType, [])
            type_petalbum.append(obj)
            self.res_type_petalbum[obj.eleType] = type_petalbum

    def init_totem(self):
        self.res_poslv_totem.clear()
        for obj in self.res_totem.values():
            key = (obj.pos, obj.level)
            self.res_poslv_totem[key] = obj

    def init_totemRanom(self):
        self.res_random_totem = []
        for obj in self.res_totemRan.values():
            value = (obj.id, obj.num)
            self.res_random_totem.append(value)

    def init_petevolve(self):
        self.res_idlv_petevolve.clear()
        for obj in self.res_petevolve.values():
            key = (obj.petId, obj.evolveLv)
            self.res_idlv_petevolve[key] = obj

    def init_res_petlv(self):
        self.res_qalv_petlv.clear()
        for obj in self.res_petlv.values():
            key = (obj.quality, obj.lv)
            self.res_qalv_petlv[key] = obj


    def init_pvpmatch(self):
        self.res_fa_pvpmatch.clear()
        keys = list(self.res_pvpmatch.keys())
        keys.sort()

        data_500 = {}
        data_50 = {}
        data_5 = {}

        start_5 = 0
        start_50 = 0
        start_500 = 0
        end_5 = 0
        end_50 = 0
        end_500 = 0

        index = 0
        for key in keys:
            index += 1

            obj = self.res_pvpmatch.get(key)
            data_5[(obj.startVal, obj.endVal)] = obj
            if index%5 == 1:
                start_5 = obj.startVal
            if index % 50 == 1:
                start_50 = obj.startVal
            if index % 500 == 1:
                start_500 = obj.startVal

            if index%5 == 0:
                end_5 = obj.endVal
                data_50[(start_5, end_5)] = data_5
                data_5 = {}
            if index % 50 == 0:
                end_50 = obj.endVal
                data_500[(start_50, end_50)] = data_50
                data_50 = {}
            if index % 500 == 0:
                end_500 = obj.endVal
                self.res_fa_pvpmatch[(start_500, end_500)] = data_500
                data_500 = {}
            else:
                if index == len(keys):
                    end_500 = obj.endVal
                    self.res_fa_pvpmatch[(start_500, end_500)] = data_500
                    data_500 = {}

    def init_kuafuServerNo(self):
        self.res_List_kuafuServerNo=[]
        v=self.res_kuafuServerNo.get(config.serverNo,None)
        if not v:
            return
        
        keys = list(self.res_kuafuServerNo.keys())
        
        keyss=[]
        for k in keys:
            keyss.append(int('9'+k))

        keyss.sort()
        
        keys=[]
        for k in keyss:
            a=str(k)
            keys.append(a[1:])

        # print('===',v.type,keys)


        for key in keys:
            vv=self.res_kuafuServerNo.get(key)
            if vv and vv.type==v.type:
                # print('=====',key,vv.type)
                self.res_List_kuafuServerNo.append(key)

    def init_kuafuMap(self):
        self.res_no2id_kuafuMap.clear()
        for obj in self.res_kuafuMap.values():
            self.res_no2id_kuafuMap[obj.serverNo] = obj.id

    def init_guildTask(self):
        self.res_type_guildTask.clear()
        for obj in self.res_guildTask.values():
            type_guildTask = self.res_type_guildTask.setdefault(obj.type, [])
            type_guildTask.append(obj)

    def init_guildSkill(self):
        self.res_poslv_guildSkill.clear()
        for obj in self.res_guildSkill.values():
            key = (obj.skillId, obj.lv)
            self.res_poslv_guildSkill[key] = obj
