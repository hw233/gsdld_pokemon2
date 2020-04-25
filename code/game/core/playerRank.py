#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import time

from game.common import utility
from game.define import constant, msg_define
from corelib.frame import Game, spawn

#角色属性
class PlayerRank(utility.DirtyFlag):
    def __init__(self, owner):
        utility.DirtyFlag.__init__(self)
        self.owner = owner  # 拥有者

        self.crossRankGetList = []  # 跨服排行榜达标奖励已领取列表

        self.save_cache = {} #存储缓存


    def markDirty(self):
        utility.DirtyFlag.markDirty(self)
        if self.owner:
            self.owner.markDirty()

    #存库数据
    def to_save_dict(self, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            self.save_cache = {}
            self.save_cache["crossRankGetList"] = self.crossRankGetList
        return self.save_cache

    #读库数据初始化
    def load_from_dict(self, data):
        self.crossRankGetList = data.get("crossRankGetList", [])  # 跨服排行榜达标奖励已领取列表

    #登录初始化下发数据
    def to_init_data(self):
        init_data = {}
        init_data["crossRankGetList"] = self.crossRankGetList
        return init_data

    def to_wee_hour_data(self):
        return self.to_init_data()

    def do_login(self):
        #更新所有的榜
        self.uploadRank(constant.RANK_TYPE_LV)

    def uninit(self):
        pass

    def checkBestPetCrossRank(self, bestData):
        now = int(time.time())
        for actRankRes in Game.res_mgr.res_actCrossRankReward.values():
            if actRankRes.minRank:
                continue
            rankobj = Game.sub_cross_rank_mgr.getRank(actRankRes.type)
            if not rankobj:
                continue

            if rankobj.endTime < now:
                continue

            if actRankRes.type in self.crossRankGetList:
                continue

            if actRankRes.type == constant.CROSS_RANK_TYPE_PET_WATER:
                mailRes = Game.res_mgr.res_mail.get(constant.MAIL_ID_CROSS_NONE_1, None)
                value = self.owner.attr.max_water_fa
            elif actRankRes.type == constant.CROSS_RANK_TYPE_PET_LIGHT:
                mailRes = Game.res_mgr.res_mail.get(constant.MAIL_ID_CROSS_NONE_2, None)
                value = self.owner.attr.max_light_fa
            elif actRankRes.type == constant.CROSS_RANK_TYPE_PET_GRASS:
                mailRes = Game.res_mgr.res_mail.get(constant.MAIL_ID_CROSS_NONE_3, None)
                value = self.owner.attr.max_grass_fa
            elif actRankRes.type == constant.CROSS_RANK_TYPE_PET_DARK:
                mailRes = Game.res_mgr.res_mail.get(constant.MAIL_ID_CROSS_NONE_4, None)
                value = self.owner.attr.max_dark_fa
            elif actRankRes.type == constant.CROSS_RANK_TYPE_PET_FIRE:
                mailRes = Game.res_mgr.res_mail.get(constant.MAIL_ID_CROSS_NONE_5, None)
                value = self.owner.attr.max_fire_fa
            elif actRankRes.type == constant.CROSS_RANK_TYPE_PET_BEST:
                mailRes = Game.res_mgr.res_mail.get(constant.MAIL_ID_CROSS_NONE_6, None)
                value = self.owner.attr.max_best_fa
            elif actRankRes.type == constant.CROSS_RANK_TYPE_PET_WATER_HEFU:
                mailRes = Game.res_mgr.res_mail.get(constant.MAIL_ID_CROSS_NONE_1_HEFU, None)
                value = self.owner.attr.max_water_fa
            elif actRankRes.type == constant.CROSS_RANK_TYPE_PET_LIGHT_HEFU:
                mailRes = Game.res_mgr.res_mail.get(constant.MAIL_ID_CROSS_NONE_2_HEFU, None)
                value = self.owner.attr.max_light_fa
            elif actRankRes.type == constant.CROSS_RANK_TYPE_PET_GRASS_HEFU:
                mailRes = Game.res_mgr.res_mail.get(constant.MAIL_ID_CROSS_NONE_3_HEFU, None)
                value = self.owner.attr.max_grass_fa
            elif actRankRes.type == constant.CROSS_RANK_TYPE_PET_DARK_HEFU:
                mailRes = Game.res_mgr.res_mail.get(constant.MAIL_ID_CROSS_NONE_4_HEFU, None)
                value = self.owner.attr.max_dark_fa
            elif actRankRes.type == constant.CROSS_RANK_TYPE_PET_FIRE_HEFU:
                mailRes = Game.res_mgr.res_mail.get(constant.MAIL_ID_CROSS_NONE_5_HEFU, None)
                value = self.owner.attr.max_fire_fa
            elif actRankRes.type == constant.CROSS_RANK_TYPE_PET_BEST_HEFU:
                mailRes = Game.res_mgr.res_mail.get(constant.MAIL_ID_CROSS_NONE_6_HEFU, None)
                value = self.owner.attr.max_best_fa
            else:
                continue

            if value >= actRankRes.value:
                if actRankRes.type not in self.crossRankGetList:
                    self.crossRankGetList.append(actRankRes.type)
                    self.markDirty()
                content = mailRes.content
                Game.rpc_mail_mgr.sendPersonMail(self.owner.id, mailRes.title, content, actRankRes.reward)


    def uploadRank(self, rankType, data={}):
        return
        rankInfo = self.packUpload(rankType, data)
        Game.sub_rank_mgr.uploadRank(rankType, rankInfo)

    def packUpload(self, rankType, data):
        player = self.owner

        info = {}
        info["rid"] = self.owner.id
        info["name"] = self.owner.name
        info["fa"] = self.owner.base.fa
        info["lv"] = self.owner.base.lv
        info["sex"] = self.owner.base.sex
        info["vip"] = self.owner.vip.GetVipLv(),
        info["portrait"] = self.owner.myhead.getPortrait()
        info["headframe"] = self.owner.myhead.getHeadframe()

        resp = {}
        resp["id"] = player.id
        resp["info"] = info


        if rankType == constant.RANK_TYPE_FA: # 战力榜
            resp["sortEle"] = [self.owner.base.fa, self.owner.base.lv]
        elif rankType == constant.RANK_TYPE_PET_ALBUM: # 宠物图鉴榜
            resp["sortEle"] = [self.owner.pet.getAllAlbumNum(), self.owner.base.fa]
        elif rankType == constant.RANK_HETI: # 合体
            resp["sortEle"] = [self.owner.heti.GetHetiTodayScore(), self.owner.heti.GetHetiTodayGold()]
        elif rankType == constant.RANK_TYPE_MAP:  # 地图关卡排行榜
            resp["sortEle"] = [self.owner.map.passSubId, self.owner.base.fa]
        elif rankType == constant.RANK_TYPE_LV:  # 等级排行榜
            resp["sortEle"] = [self.owner.base.lv, self.owner.map.passSubId, self.owner.base.fa]
        elif rankType == constant.RANK_TYPE_CATCHPET_HEFU:  # 抓宠大赛积分排行 - 合服
            score = data.get("score", 0)
            resp["sortEle"] = [score, ]
        elif rankType == constant.RANK_TYPE_LWBZ:  # 龙王宝藏榜
            totalStar = self.owner.fuben.getLwbzTotalStar()
            resp["sortEle"] = [totalStar, self.owner.base.fa]
        elif rankType == constant.RANK_TYPE_COST:  # 消费排行
            resp["sortEle"] = [self.owner.charge.costRankDiamond, ]
        elif rankType == constant.RANK_TYPE_NEWYEAR_CHARGE:  # 元旦充值排行
            resp["sortEle"] = [self.owner.charge.newYearChargeValue, ]
        elif rankType == constant.RANK_TYPE_CHARGE:  # 充值排行
            resp["sortEle"] = [self.owner.charge.chargeRankDiamond, ]
        elif rankType == constant.RANK_TYPE_CHARGE_HEFU:  # 元旦充值排行 - 合服
            hefud = data.get("hefud", 0)
            resp["sortEle"] = [hefud, ]
        elif rankType == constant.RANK_TYPE_XLYS:  # 小雷音寺榜
            levelId = data.get("levelId", 0)
            resp["sortEle"] = [levelId, self.owner.base.fa]
        elif rankType == constant.RANK_TYPE_TTSL:  # 天庭试炼榜
            levelId = data.get("levelId", 0)
            resp["sortEle"] = [levelId, self.owner.base.fa]


        elif rankType == constant.RANK_TYPE_TX: # 天仙榜
            fa = data.get("fa", 0)
            lv = player.attrModule7.GetLv()
            resp["sortEle"] = [fa, lv]
        elif rankType == constant.RANK_TYPE_SQ: # 神兵榜
            fa = data.get("fa", 0)
            lv = player.attrModule8.GetLv()
            resp["sortEle"] = [fa, lv]


        elif rankType == constant.RANK_TYPE_PET_QA_FA:  # 所有激活宠物按种族值换算继承后的战力榜
            fa = data.get("fa", 0)
            lv = player.base.GetLv()
            resp["sortEle"] = [fa, lv]

        elif rankType == constant.RANK_TYPE_ATTR_FA: # 属性池子战力榜
            fa = data.get("fa", 0)
            lv = player.base.GetLv()
            resp["sortEle"] = [fa, lv]
        return resp


    def packToClient(self, rankType, playerInfo):
        resp = {}
        pid = playerInfo.get("id", 0)
        rank = playerInfo.get("rank", 0)
        baseInfo = playerInfo.get("info", {})
        sortEle = playerInfo.get("sortEle", [])

        resp["pid"] = pid
        resp["rank"] = rank
        resp["name"] = baseInfo.get("name", "")
        resp["vip"] = baseInfo.get("vip", 0)
        resp["sex"] = baseInfo.get("sex", 0)
        resp["portrait"] = baseInfo.get("portrait", 0)
        resp["headframe"] = baseInfo.get("headframe", 0)
        if not pid or not baseInfo or not sortEle:
            return resp
        if rankType == constant.RANK_TYPE_FA: # 战力榜
            resp["fight"] = sortEle[0]
            resp["lv"] = sortEle[1]
        elif rankType == constant.RANK_TYPE_LV: # 等级榜
            if len(sortEle) == 2:
                resp["lv"] = sortEle[0]
                resp["barr"] = 1
                resp["fight"] = sortEle[1]
            else:
                resp["lv"] = sortEle[0]
                resp["barr"] = sortEle[1]
                resp["fight"] = sortEle[2]
        elif rankType == constant.RANK_TYPE_PET: # 宠物榜
            resp["fight"] = sortEle[0]
            resp["lv"] = sortEle[1]
        elif rankType == constant.RANK_TYPE_TX: # 天仙榜
            resp["fight"] = sortEle[0]
            resp["lv"] = sortEle[1]
        elif rankType == constant.RANK_TYPE_SQ: # 神兵榜
            resp["fight"] = sortEle[0]
            resp["lv"] = sortEle[1]

        elif rankType == constant.RANK_TYPE_LWBZ: # 龙王宝藏榜
            resp["star"] = sortEle[0]
            resp["fight"] = sortEle[1]
        elif rankType == constant.RANK_TYPE_XLYS: # 小雷音寺榜
            resp["barr"] = sortEle[0]
            resp["fight"] = sortEle[1]
        elif rankType == constant.RANK_TYPE_TTSL: # 天庭试炼榜
            resp["barr"] = sortEle[0]
            resp["fight"] = sortEle[1]
        elif rankType == constant.RANK_TYPE_MAP: # 地图关卡排行榜
            resp["barr"] = sortEle[0]
            resp["fight"] = sortEle[1]

        elif rankType == constant.RANK_TYPE_PET_ALBUM: # 宠物图鉴榜
            resp["num"] = sortEle[0]
            resp["fight"] = sortEle[1]
            resp["lv"] = baseInfo.get("lv", 0)


        elif rankType == constant.RANK_TYPE_PET_QA_FA:  # 所有激活宠物按种族值换算继承后的战力榜
            resp["fight"] = sortEle[0]
            resp["lv"] = baseInfo.get("lv", 0)
        elif rankType == constant.RANK_HETI: # 合体
            resp["score"] = sortEle[0]
            resp["gold"] = sortEle[1]
        elif rankType == constant.RANK_TYPE_ATTR_FA: # 属性池子战力榜
            resp["fight"] = sortEle[0]
            resp["lv"] = baseInfo.get("lv", 0)
        elif rankType == constant.RANK_TYPE_COST: # 消费排行
            resp["score"] = sortEle[0]
        elif rankType == constant.RANK_TYPE_CHARGE: # 充值排行
            resp["score"] = sortEle[0]
        elif rankType == constant.RANK_TYPE_NEWYEAR_CHARGE: # 元旦充值排行
            resp["score"] = sortEle[0]
        elif rankType == constant.RANK_TYPE_CHARGE_HEFU: # 充值排行
            resp["score"] = sortEle[0]
        elif rankType == constant.RANK_TYPE_CATCHPET_HEFU: # 抓宠排行
            resp["score"] = sortEle[0]
        return resp


    def uploadCrossRank(self, rankType, data={}):
        return
        cross_rank = Game.sub_cross_rank_mgr.getRank(rankType)
        if cross_rank:
            rankInfo = self.packCrossUpload(rankType, data)
            cross_rank.uploadRank(rankInfo)

    def packCrossUpload(self, rankType, data):
        player = self.owner
        fa = data.get("fa", 0)
        petId = data.get("petId", 0)

        info = {}
        info["rid"] = self.owner.id
        info["name"] = self.owner.name
        info["fa"] = self.owner.base.fa
        info["lv"] = self.owner.base.lv
        info["sex"] = self.owner.base.sex
        info["vip"] = self.owner.vip.GetVipLv(),
        info["portrait"] = self.owner.myhead.getPortrait()
        info["headframe"] = self.owner.myhead.getHeadframe()


        resp = {}
        resp["id"] = player.id
        resp["info"] = info
        if petId:
            pet = player.pet.getPet(petId)
            if pet:
                resp["petInfo"] = pet.packInfo()
                resp["roleAttr"] = player.attr.to_init_data()

        if rankType == constant.CROSS_RANK_TYPE_PET_WATER: # 水系宠物
            resp["sortEle"] = [fa, ]
        elif rankType == constant.CROSS_RANK_TYPE_PET_LIGHT: # 光系宠物
            resp["sortEle"] = [fa, ]
        elif rankType == constant.CROSS_RANK_TYPE_PET_GRASS: # 草系宠物
            resp["sortEle"] = [fa, ]
        elif rankType == constant.CROSS_RANK_TYPE_PET_DARK: # 暗系宠物
            resp["sortEle"] = [fa, ]
        elif rankType == constant.CROSS_RANK_TYPE_PET_FIRE: # 火系宠物
            resp["sortEle"] = [fa, ]
        elif rankType == constant.CROSS_RANK_TYPE_PET_BEST: # 最强宠物
            resp["sortEle"] = [fa, ]
        elif rankType == constant.CROSS_RANK_TYPE_PET_WATER_HEFU: # 水系宠物
            resp["sortEle"] = [fa, ]
        elif rankType == constant.CROSS_RANK_TYPE_PET_LIGHT_HEFU: # 光系宠物
            resp["sortEle"] = [fa, ]
        elif rankType == constant.CROSS_RANK_TYPE_PET_GRASS_HEFU: # 草系宠物
            resp["sortEle"] = [fa, ]
        elif rankType == constant.CROSS_RANK_TYPE_PET_DARK_HEFU: # 暗系宠物
            resp["sortEle"] = [fa, ]
        elif rankType == constant.CROSS_RANK_TYPE_PET_FIRE_HEFU: # 火系宠物
            resp["sortEle"] = [fa, ]
        elif rankType == constant.CROSS_RANK_TYPE_PET_BEST_HEFU: # 最强宠物
            resp["sortEle"] = [fa, ]
        elif rankType == constant.CROSS_RANK_TYPE_NEWYEAR_CHARGE: # 元旦充值排行
            resp["sortEle"] = [self.owner.charge.newYearChargeValue, ]

        return resp


    def packCrossToClient(self, rankType, playerInfo):
        resp = {}
        pid = playerInfo.get("id", 0)
        rank = playerInfo.get("rank", 0)
        baseInfo = playerInfo.get("info", {})
        sortEle = playerInfo.get("sortEle", [])
        petInfo = playerInfo.get("petInfo", {})
        roleAttr = playerInfo.get("roleAttr", {})

        resp["pid"] = pid
        resp["rank"] = rank
        resp["name"] = baseInfo.get("name", "")
        resp["vip"] = baseInfo.get("vip", 0)
        resp["sex"] = baseInfo.get("sex", 0)
        resp["portrait"] = baseInfo.get("portrait", 0)
        resp["headframe"] = baseInfo.get("headframe", 0)
        if petInfo:
            resp["petInfo"] = petInfo
            resp["roleAttr"] = roleAttr

        if not pid or not baseInfo or not sortEle:
            return resp

        if rankType == constant.CROSS_RANK_TYPE_PET_WATER: # 水系宠物
            resp["fight"] = sortEle[0]
        elif rankType == constant.CROSS_RANK_TYPE_PET_LIGHT: # 光系宠物
            resp["fight"] = sortEle[0]
        elif rankType == constant.CROSS_RANK_TYPE_PET_GRASS: # 草系宠物
            resp["fight"] = sortEle[0]
        elif rankType == constant.CROSS_RANK_TYPE_PET_DARK: # 暗系宠物
            resp["fight"] = sortEle[0]
        elif rankType == constant.CROSS_RANK_TYPE_PET_FIRE: # 火系宠物
            resp["fight"] = sortEle[0]
        elif rankType == constant.CROSS_RANK_TYPE_PET_BEST: # 最强宠物
            resp["fight"] = sortEle[0]
        elif rankType == constant.CROSS_RANK_TYPE_PET_WATER_HEFU: # 水系宠物
            resp["fight"] = sortEle[0]
        elif rankType == constant.CROSS_RANK_TYPE_PET_LIGHT_HEFU: # 光系宠物
            resp["fight"] = sortEle[0]
        elif rankType == constant.CROSS_RANK_TYPE_PET_GRASS_HEFU: # 草系宠物
            resp["fight"] = sortEle[0]
        elif rankType == constant.CROSS_RANK_TYPE_PET_DARK_HEFU: # 暗系宠物
            resp["fight"] = sortEle[0]
        elif rankType == constant.CROSS_RANK_TYPE_PET_FIRE_HEFU: # 火系宠物
            resp["fight"] = sortEle[0]
        elif rankType == constant.CROSS_RANK_TYPE_PET_BEST_HEFU: # 最强宠物
            resp["fight"] = sortEle[0]
        elif rankType == constant.CROSS_RANK_TYPE_NEWYEAR_CHARGE: # 元旦充值排行
            resp["score"] = sortEle[0]
        return resp







