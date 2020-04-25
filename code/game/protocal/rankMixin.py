#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from game.define import errcode, constant
from game import Game
from game.common import utility
import time

class RankMixin(object):
    if 0:
        from game.core import player as player_md
        player = player_md.Player()

    # 排行榜请求(rankReq)
    #     请求(type, int)
    #         1 战力榜，2 等级榜，3宠物榜，4 仙侣榜，5 坐骑榜，6 翅膀榜，7天仙榜，8神兵榜，9法阵榜，10 仙位榜，11 通灵榜，12 兽魂榜，13 天女榜，14 仙器榜，15 花撵榜，16 灵气榜 17 龙王保藏榜 18 小雷音寺榜 19 天庭试炼榜
    #         请求个数(num, int))
    #     返回(rankData,json)
    #         我的排名(myRank,int)
    #             0 未上榜
    #         第一名形象(oneAvatar,json)
    #             角色数据(role, json)
    #                 角色名称(name, string)
    #                 角色外形列表(showList, [json])
    #                     模块类型(modeType, int)
    #                         1=坐骑 2=翅膀 7=天仙 8=神兵
    #                     幻化类型(imageType, int)
    #                         1=坐骑 2=坐骑皮肤 (其他模块通用)
    #                     幻化id(imageId, int)
    #                         根据类型读取不同的配置表
    #                 称号id(title, int)
    #                 时装id(fashion, int)
    #                 性别(sex, int)
    #                     0=? 1=男 2=女
    #                 套装id(outfit, int)
    #             宠物数据(pet,json)
    #                 宠物id(petId,int)
    #             仙侣数据(xl,json)
    #                 仙侣id(xlId,int)
    #             坐骑数据(horse,json)
    #                 幻化类型(imageType, int)
    #                     1=坐骑 2=坐骑皮肤 (其他模块通用)
    #                 幻化id(imageId, int)
    #                     根据类型读取不同的配置表
    #             翅膀数据(wing,json)
    #                 角色外形列表(showList, [json])
    #                     模块类型(modeType, int)
    #                         1=坐骑 2=翅膀  8=神兵
    #                     幻化类型(imageType, int)
    #                         1=坐骑 2=坐骑皮肤 (其他模块通用)
    #                     幻化id(imageId, int)
    #                         根据类型读取不同的配置表
    #             天仙数据(tx,json)
    #                 角色外形列表(showList, [json])
    #                     模块类型(modeType, int)
    #                         1=坐骑 2=翅膀 7=天仙 8=神兵
    #                     幻化类型(imageType, int)
    #                         1=坐骑 2=坐骑皮肤 (其他模块通用)
    #                     幻化id(imageId, int)
    #                         根据类型读取不同的配置表
    #             神兵数据(sb,json)
    #                 角色外形列表(showList, [json])
    #                     模块类型(modeType, int)
    #                         1=坐骑 2=翅膀  8=神兵
    #                     幻化类型(imageType, int)
    #                         1=坐骑 2=坐骑皮肤 (其他模块通用)
    #                     幻化id(imageId, int)
    #                         根据类型读取不同的配置表
    #             法阵数据(fz,json)
    #                 仙侣id(xlId,int)
    #                 法阵id(fzId,int)
    #             仙位数据(xw,json)
    #                 仙位id(xwId,int)
    #             通灵数据(tl,json)
    #                 宠物id(petId,int)
    #                 通灵id(tlId,int)
    #             兽魂数据(sh,json)
    #                 宠物id(petId,int)
    #                 兽魂id(shId,int)
    #             天女数据(tn,json)
    #                 天女id(tnId,int)
    #             仙器数据(xq,json)
    #                 天女id(tnId,int)
    #             花撵数据(hn,json)
    #                 天女id(tnId,int)
    #             灵气数据(lq,json)
    #                 天女id(tnId,int)
    #         排行列表(rankList,[json])
    #             排名(rank,int)
    #             名字(name,string)
    #             等级(lv,int)
    #             战力(fight,int)
    #             vip(vip,int)
    #                 0 无vip
    #         上一次更新时间戳(time, int)
    #         类型(type, int)
    def rc_rankReq(self, type, num):
        # rankobj = Game.sub_rank_mgr.getRankobj(type)
        # if not rankobj:
        #     return 0, errcode.EC_RANK_NOT_FIND
        # rankList = rankobj.getRankList()
        # myRank = rankobj.getMyRank(self.player.id)
        myRank=1

        firstInfo = {}
        # if rankList:
        #     firstPid = rankList[0].get("id", 0)
        #     firstPlayer = get_rpc_player(firstPid)
        #     if firstPlayer:
        #         firstInfo = firstPlayer.getRankShow()

        rRankList = []
        # for info in rankList[:num]:
        #     one = self.player.rank.packToClient(type, info)
        #     rRankList.append(one)

        t= time.time()
        
        resp = {
            "myRank": myRank,
            "oneAvatar": firstInfo,
            "rankList": rRankList,
            # "time": Game.sub_rank_mgr.getLastCalTime(),
            "time": t,
            "type": type,
        }

        # print("=============",resp["myRank"])
        return 1, resp

    # #获取排行榜角色信息
    # #     请求
    # #         角色id(rid, int))
    # #     返回
    # #         角色信息(playerInfo,int)
    # def rc_getRankPlayerInfo(self, rid):
    #     rpcplayer = get_rpc_player(rid)
    #     playerInfo = {}
    #     if rpcplayer:
    #         playerInfo = rpcplayer.getRankShow()

    #     resp = {
    #         "playerInfo": playerInfo,
    #     }
    #     return 1, resp


    # # 开服狂欢排行榜请求(kfkhrankReq) 同 排行榜请求(rankReq)
    # def rc_kfkhrankReq(self, type, num):
    #     rankobj = Game.sub_rank_mgr.getRankobj(type)
    #     if not rankobj:
    #         return 0, errcode.EC_RANK_NOT_FIND


    #     configType = constant.KFKH_ACT_RANK_MOD_TYPE_R.get(type,None)
    #     if not configType:
    #         return 0, errcode.EC_RANK_NOT_FIND

    #     myRank={}
    #     rankList = rankobj.GetSnapshot()
    #     if not rankList:
    #         rankList = rankobj.getRankList()

    #         res={}
    #         for actRankRes in Game.res_mgr.res_actKfkh.values():
    #             if actRankRes.type==configType:
    #                 res=actRankRes
    #                 break
    #         if not res:
    #             return 0, errcode.EC_RANK_NOT_FIND

    #         newrankList=[]
    #         for playerInfo in rankList:
    #             if playerInfo["sortEle"][0]<actRankRes.value:
    #                 break
    #             newrankList.append(playerInfo)
            

    #         myRank = rankobj.getMyRankByList(self.player.id, newrankList)

    #         rankList=newrankList
    #     else:
    #         myRank = rankobj.getMyRankBySnapshot(self.player.id)

    #     firstInfo = {}
    #     if rankList:
    #         firstPid = rankList[0].get("id", 0)
    #         firstPlayer = get_rpc_player(firstPid)
    #         if firstPlayer:
    #             firstInfo = firstPlayer.getRankShow()

    #     rRankList = []
    #     for info in rankList[:num]:
    #         one = self.player.rank.packToClient(type, info)
    #         rRankList.append(one)

    #     resp = {
    #         "myRank": myRank,
    #         "oneAvatar": firstInfo,
    #         "rankList": rRankList,
    #         "time": Game.sub_rank_mgr.getLastCalTime(),
    #         "type": type,
    #     }
    #     return 1, resp

    # # 跨服排行榜请求(crossRankReq)
    # # CROSS_RANK_TYPE_PET_WATER = 1  # 水系宠物
    # # CROSS_RANK_TYPE_PET_LIGHT = 2  # 光系宠物
    # # CROSS_RANK_TYPE_PET_GRASS = 3  # 草系宠物
    # # CROSS_RANK_TYPE_PET_DARK = 4  # 暗系宠物
    # # CROSS_RANK_TYPE_PET_FIRE = 5  # 火系宠物
    # # CROSS_RANK_TYPE_PET_BEST = 6  # 最强宠物
    # def rc_crossRankReq(self, type):
    #     rankobj = Game.sub_cross_rank_mgr.getRank(type)
    #     if not rankobj:
    #         return 0, errcode.EC_RANK_NOT_FIND

    #     myRank = 0
    #     myInfo = {}
    #     rRankList = []
    #     for info in rankobj.getRankList():
    #         one = self.player.rank.packCrossUpload(type, info)
    #         rRankList.append(one)

    #         if info.get("id", 0) == self.player.id:
    #             myRank = info.get("rank", 0)
    #             myInfo = one

    #     #宠物战力  上榜的话用榜数据，否则用自家保存的数据
    #     if type == constant.CROSS_RANK_TYPE_PET_WATER: # 水系最高战力
    #         if myInfo:
    #             myFa = myInfo.get("fight", 0) #self.player.attr.max_water_fa
    #             myPet = myInfo.get("petInfo", {}).get("id", 0) #self.player.attr.max_water_fa_petId
    #         else:
    #             myFa = self.player.attr.max_water_fa
    #             myPet = self.player.attr.max_water_fa_petId
    #     elif type == constant.CROSS_RANK_TYPE_PET_FIRE: # 火系最高战力
    #         if myInfo:
    #             myFa = myInfo.get("fight", 0) #self.player.attr.max_fire_fa
    #             myPet = myInfo.get("petInfo", {}).get("id", 0) #self.player.attr.max_fire_fa_petId
    #         else:
    #             myFa = self.player.attr.max_fire_fa
    #             myPet = self.player.attr.max_fire_fa_petId
    #     elif type == constant.CROSS_RANK_TYPE_PET_GRASS: # 草系最高战力
    #         if myInfo:
    #             myFa = myInfo.get("fight", 0) #self.player.attr.max_grass_fa
    #             myPet = myInfo.get("petInfo", {}).get("id", 0) #self.player.attr.max_grass_fa_petId
    #         else:
    #             myFa = self.player.attr.max_grass_fa
    #             myPet = self.player.attr.max_grass_fa_petId
    #     elif type == constant.CROSS_RANK_TYPE_PET_LIGHT: # 光系最高战力
    #         if myInfo:
    #             myFa = myInfo.get("fight", 0) #self.player.attr.max_light_fa
    #             myPet = myInfo.get("petInfo", {}).get("id", 0) #self.player.attr.max_light_fa_petId
    #         else:
    #             myFa = self.player.attr.max_light_fa
    #             myPet = self.player.attr.max_light_fa_petId
    #     elif type == constant.CROSS_RANK_TYPE_PET_DARK: # 暗系最高战力
    #         if myInfo:
    #             myFa = myInfo.get("fight", 0) #self.player.attr.max_dark_fa
    #             myPet = myInfo.get("petInfo", {}).get("id", 0) #self.player.attr.max_dark_fa_petId
    #         else:
    #             myFa = self.player.attr.max_dark_fa
    #             myPet = self.player.attr.max_dark_fa_petId
    #     elif type == constant.CROSS_RANK_TYPE_PET_BEST:  # 最强宠物最高战力
    #         if myInfo:
    #             myFa = myInfo.get("fight", 0) #self.player.attr.max_best_fa
    #             myPet = myInfo.get("petInfo", {}).get("id", 0) #self.player.attr.max_best_fa_petId
    #         else:
    #             myFa = self.player.attr.max_best_fa
    #             myPet = self.player.attr.max_best_fa_petId
    #     elif type == constant.CROSS_RANK_TYPE_PET_WATER_HEFU: # 水系最高战力
    #         if myInfo:
    #             myFa = myInfo.get("fight", 0) #self.player.attr.max_water_fa
    #             myPet = myInfo.get("petInfo", {}).get("id", 0) #self.player.attr.max_water_fa_petId
    #         else:
    #             myFa = self.player.attr.max_water_fa
    #             myPet = self.player.attr.max_water_fa_petId
    #     elif type == constant.CROSS_RANK_TYPE_PET_FIRE_HEFU: # 火系最高战力
    #         if myInfo:
    #             myFa = myInfo.get("fight", 0) #self.player.attr.max_fire_fa
    #             myPet = myInfo.get("petInfo", {}).get("id", 0) #self.player.attr.max_fire_fa_petId
    #         else:
    #             myFa = self.player.attr.max_fire_fa
    #             myPet = self.player.attr.max_fire_fa_petId
    #     elif type == constant.CROSS_RANK_TYPE_PET_GRASS_HEFU: # 草系最高战力
    #         if myInfo:
    #             myFa = myInfo.get("fight", 0) #self.player.attr.max_grass_fa
    #             myPet = myInfo.get("petInfo", {}).get("id", 0) #self.player.attr.max_grass_fa_petId
    #         else:
    #             myFa = self.player.attr.max_grass_fa
    #             myPet = self.player.attr.max_grass_fa_petId
    #     elif type == constant.CROSS_RANK_TYPE_PET_LIGHT_HEFU: # 光系最高战力
    #         if myInfo:
    #             myFa = myInfo.get("fight", 0) #self.player.attr.max_light_fa
    #             myPet = myInfo.get("petInfo", {}).get("id", 0) #self.player.attr.max_light_fa_petId
    #         else:
    #             myFa = self.player.attr.max_light_fa
    #             myPet = self.player.attr.max_light_fa_petId
    #     elif type == constant.CROSS_RANK_TYPE_PET_DARK_HEFU: # 暗系最高战力
    #         if myInfo:
    #             myFa = myInfo.get("fight", 0) #self.player.attr.max_dark_fa
    #             myPet = myInfo.get("petInfo", {}).get("id", 0) #self.player.attr.max_dark_fa_petId
    #         else:
    #             myFa = self.player.attr.max_dark_fa
    #             myPet = self.player.attr.max_dark_fa_petId
    #     elif type == constant.CROSS_RANK_TYPE_PET_BEST_HEFU:  # 最强宠物最高战力
    #         if myInfo:
    #             myFa = myInfo.get("fight", 0) #self.player.attr.max_best_fa
    #             myPet = myInfo.get("petInfo", {}).get("id", 0) #self.player.attr.max_best_fa_petId
    #         else:
    #             myFa = self.player.attr.max_best_fa
    #             myPet = self.player.attr.max_best_fa_petId
    #     else:
    #         myFa = 0
    #         myPet = 0

    #     resp = {
    #         "myRank": myRank,
    #         "rankList": rRankList,
    #         "type": type,
    #         "myFa": myFa,
    #         "myPet": myPet,
    #     }
    #     return 1, resp

    # #获取跨服排行基础数据
    # def rc_crossRankBaseInfo(self):
    #     ranks = []
    #     for rankobj in Game.sub_cross_rank_mgr.ranks.values():
    #         data = {}
    #         data["type"] = rankobj.type
    #         data["startTime"] = rankobj.startTime
    #         data["endTime"] = rankobj.endTime
    #         ranks.append(data)

    #     resp = {}
    #     resp["ranks"] = ranks
    #     return 1, resp





