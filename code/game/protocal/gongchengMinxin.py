#!/usr/bin/env python
# -*- coding:utf-8 -*-
import random
import copy
from game.define import errcode, constant, msg_define
from game import Game
from game.common import utility
import config
from grpc import DictExport, DictItemProxy, get_proxy_by_addr
from corelib import gtime
import time
from game.mgr.guild import get_rpc_guild
import os

class GongchengRpcMixin(object):
    if 0:
        from game.core import player as player_md
        player = player_md.Player()

    def rc_gongchengQuanmingReward(self):
        gongchengActiveSerNum = Game.res_mgr.res_common.get("gongchengActiveSerNum")
        if not gongchengActiveSerNum:
            return 0, errcode.EC_NORES

        if config.serverNo not in Game.res_mgr.res_List_kuafuServerNo:
            return 0, errcode.EC_NORES
        
        idx=Game.res_mgr.res_List_kuafuServerNo.index(config.serverNo)
        startidx=(idx+1)-gongchengActiveSerNum.i
        if startidx<0:
            startidx=0

        slist=Game.res_mgr.res_List_kuafuServerNo[startidx:startidx+gongchengActiveSerNum.i]

        from game.mgr.room import get_rpc_gongcheng
        rpc_gongcheng = get_rpc_gongcheng()
        if not rpc_gongcheng:
            return 0, errcode.EC_GETD_RPC_ROOM_FAIL

        iOpenServiceDay = self.player.base.GetServerOpenDay()  # 开服天数
        t = self.player.base.GetServerOpenTime()  # 开服时间戳


        for k,v in Game.res_mgr.res_gongchengActive.items():
            if v.lastDay:
                if v.lastDayRank and v.openDay<=iOpenServiceDay<v.openDay+v.lastDay and v.openDay+v.lastDayRank<=iOpenServiceDay:

                    data=rpc_gongcheng.gongchengQuanmingRank()

                    newdata={}
    

                    ymds=[]
                    for x in range(v.lastDayRank):
                        tt=t+ (x+v.openDay-1)  *3600*24
                        ymd=gtime.getYYYYMMDDbyT(tt)
                        ymds.append(ymd)
                    

                    bestGuild={}
                    
                    for x in data:
                        if x["d"] in ymds:
                            for kk,vv in x["s"].items():
                                if kk in slist:


                                    newdata[kk]=newdata.get(kk,{"sno":kk,"list":[],"gnum":0,"score":0})
                                    newdata[kk]["score"]+=vv["score"]

                                    for kkk,vvv in vv["ghid"].items():

                                        bestGuild[kkk]=bestGuild.get(kkk,{"sno":kkk,"name":vvv["name"],"score":0})
                                        bestGuild[kkk]["score"]+=vvv["score"]
                                        
                                        

                                        # 去重计算工会数量
                                        if kkk not in newdata[kk]["list"]:
                                            newdata[kk]["list"].append(kkk)
                                            newdata[kk]["gnum"]+=1
                                        
                    bgs=list(newdata.values())
                    bgs = sorted(bgs, key=lambda fff: fff["score"], reverse=True)
                    if not len(bgs):
                        return 0, errcode.EC_GONGCHENG_QUANMING_NORANK #



                    if k in self.player.gongcheng.isRankRewardList:
                        return 0, errcode.EC_GONGCHENG_QUANMING_ALREADY #
                    
                    self.player.gongcheng.gongchengisRankReward(k)

                    reward=v.reward2
                    if bgs[0]["sno"]==config.serverNo:
                        reward=v.reward1
                    

                    respBag = self.player.bag.add(reward, constant.ITEM_ADD_GONGCHENG_QUANMING_RANK, wLog=True)

                    dUpdate = self.player.packRespBag(respBag)
                    dUpdate["gongcheng"] = self.player.gongcheng.to_init_data()
                    resp = {
                        "allUpdate": dUpdate,
                    }
                    return 1, resp

        


        return 0, errcode.EC_GONGCHENG_QUANMING_NOOPEN #


    def rc_gongchengQuanmingRank(self):

        #同步攻城任务数据
        self.rc_gongchengGetData()

        gongchengActiveSerNum = Game.res_mgr.res_common.get("gongchengActiveSerNum")
        if not gongchengActiveSerNum:
            return 0, errcode.EC_NORES

        if config.serverNo not in Game.res_mgr.res_List_kuafuServerNo:
            return 0, 15
        
        idx=Game.res_mgr.res_List_kuafuServerNo.index(config.serverNo)
        startidx=(idx+1)-gongchengActiveSerNum.i
        if startidx<0:
            startidx=0

        slist=Game.res_mgr.res_List_kuafuServerNo[startidx:startidx+gongchengActiveSerNum.i]

        from game.mgr.room import get_rpc_gongcheng
        rpc_gongcheng = get_rpc_gongcheng()
        if not rpc_gongcheng:
            return 0, errcode.EC_GETD_RPC_ROOM_FAIL

        iOpenServiceDay = self.player.base.GetServerOpenDay()  # 开服天数
        t = self.player.base.GetServerOpenTime()  # 开服时间戳


        for k,v in Game.res_mgr.res_gongchengActive.items():
            if v.lastDay:
                if v.lastDayRank and v.openDay<=iOpenServiceDay<v.openDay+v.lastDay:

                    data=rpc_gongcheng.gongchengQuanmingRank()

                    newdata={}
                    bestGuildName=""
                    bestGuildScore=0

                    ymds=[]
                    for x in range(v.lastDayRank):
                        tt=t+ (x+v.openDay-1)  *3600*24
                        ymd=gtime.getYYYYMMDDbyT(tt)
                        ymds.append(ymd)
                    

                    bestGuild={}
                    
                    for x in data:
                        if x["d"] in ymds:
                            for kk,vv in x["s"].items():
                                if kk in slist:


                                    newdata[kk]=newdata.get(kk,{"list":[],"gnum":0,"score":0})
                                    newdata[kk]["score"]+=vv["score"]

                                    for kkk,vvv in vv["ghid"].items():

                                        bestGuild[kkk]=bestGuild.get(kkk,{"name":vvv["name"],"score":0})
                                        bestGuild[kkk]["score"]+=vvv["score"]
                                        
                                        

                                        # 去重计算工会数量
                                        if kkk not in newdata[kk]["list"]:
                                            newdata[kk]["list"].append(kkk)
                                            newdata[kk]["gnum"]+=1
                                        
                    bgs=list(bestGuild.values())
                    bgs = sorted(bgs, key=lambda fff: fff["score"], reverse=True)
                    if len(bgs):
                        bestGuildName=bgs[0]["name"]
                        bestGuildScore=bgs[0]["score"]

                    return 1,{"serverNo":config.serverNo,"rank":newdata,"bestGuildName":bestGuildName,"bestGuildScore":bestGuildScore}

        


        return 1,{"serverNo":config.serverNo,"rank":{},"bestGuildName":"","bestGuildScore":0}



    def rc_gongchengGetData(self):


        from game.mgr.room import get_rpc_gongcheng
        rpc_gongcheng = get_rpc_gongcheng()
        if not rpc_gongcheng:
            return 0, errcode.EC_GETD_RPC_ROOM_FAIL

        self.player.gongcheng.enter()

        data = self.player.getGongchengInfo()
        import app
        rrv = rpc_gongcheng.hello(5,self.player.id,config.serverNo,app.addr,self.player.name,data,0,0)
        if not rrv:
            return 0, errcode.EC_CALL_RPC_ROOM_FAIL

        rrv = rpc_gongcheng.getByServerNo(5,config.serverNo)
        if not rrv:
            return 0, errcode.EC_CALL_RPC_ROOM_FAIL

        ghid=self.player.guild.GetGuildId()
        ghname = ""
        ghcolor = 0
        ghlv = 0
        guildRpc = get_rpc_guild(ghid)
        if guildRpc:
            ghname = guildRpc.getName()
            ghcolor = guildRpc.getColor()
            ghlv = guildRpc.GetLevel()
        if ghid==0:
            return 0, errcode.EC_NO_GUILD

        fdata=self.player.GetFightData()
        pdata=self.player.GetAllPetData()
        rrv3=rpc_gongcheng.gongchengFightData(self.player.id,fdata,pdata,ghid,ghname,ghcolor,ghlv,self.player.gongcheng.serverNo)
        if not rrv3:
            return 0, errcode.EC_CALL_RPC_ROOM_FAIL
        if rrv3["err"]!=0:
            return 0, rrv3["err"]

        rrv2=rpc_gongcheng.gongchengGetAllTeam(self.player.id)
        
        if not rrv2:
            return 0, errcode.EC_CALL_RPC_ROOM_FAIL
        if rrv2["err"]!=0:
            return 0, rrv2["err"]

        # a=bytearray(os.urandom(100*1024))
        # rrv["common"]["xxyy"]=a

        # retval={"list":rrv["v"],"common":rrv["common"],"team":rrv2["team"],"myteam":rrv2["myteam"]}
        retval={"list":[],"common":rrv["common"],"team":rrv2["team"],"myteam":rrv2["myteam"]}

        # 同步攻城任务数据
        self.player.gongcheng.rsyncRpcGongchengTaskData()

        return 1,retval

    def rc_gongchengExit(self):

        self.player.gongcheng.exit()

        dUpdate = {}
        dUpdate["gongcheng"] = self.player.gongcheng.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        return 1,resp

# 创建队伍(gongchengTeamCreate)
# 	请求
# 		队伍(team, [宠物id])
# 	返回
    def rc_gongchengTeamCreate(self,team):
        # 宠物互斥
        petList = copy.deepcopy(team)
        rs = self.player.pet.checkSpecMutex(petList)
        if not rs:
            return 0, errcode.EC_PET_MUTEX_LIMIT

        from game.mgr.room import get_rpc_gongcheng
        rpc_gongcheng = get_rpc_gongcheng()
        if not rpc_gongcheng:
            return 0, errcode.EC_GETD_RPC_ROOM_FAIL
        
        rrv = rpc_gongcheng.gongchengTeamCreate(self.player.id,team)
        if not rrv:
            return 0, errcode.EC_GONGCHENG_ERR
        if rrv["err"]!=0:
            return 0, rrv["err"]
        


        return 1,{"team":rrv["team"]}


# 解除队伍(gongchengTeamDestroy)
# 	请求
# 		队伍(team, string)
# 	返回
    def rc_gongchengTeamDestroy(self,team,reborn):

        from game.mgr.room import get_rpc_gongcheng
        rpc_gongcheng = get_rpc_gongcheng()
        if not rpc_gongcheng:
            return 0, errcode.EC_GETD_RPC_ROOM_FAIL

        respBag = {}
        if reborn:
            res = Game.res_mgr.res_common.get("gongchengReborn")
            respBag = self.player.bag.costItem(res.arrayint2, constant.ITEM_COST_GONGCHENG_REBORN, wLog=True)
            if not respBag.get("rs", 0):
                return 0, errcode.EC_KFBOSS_REVIVE_NOT_ENOUGH

        rrv = rpc_gongcheng.gongchengTeamDestroy(self.player.id,team,reborn)
        if not rrv:
            return 0, errcode.EC_GONGCHENG_ERR
        if rrv["err"]!=0:
            return 0, rrv["err"]

        dUpdate = self.player.packRespBag(respBag)
        resp = {
            "team":team,
            "allUpdate": dUpdate,
        }
        return 1, resp

    def rc_gongchengSend(self,team,city,atk):


        from game.mgr.room import get_rpc_gongcheng
        rpc_gongcheng = get_rpc_gongcheng()
        if not rpc_gongcheng:
            return 0, errcode.EC_GETD_RPC_ROOM_FAIL
        
        rrv = rpc_gongcheng.gongchengSend(self.player.id,team,city,atk)
        if not rrv:
            return 0, errcode.EC_GONGCHENG_ERR
        if rrv["err"]!=0:
            return 0, rrv["err"]
        self.player.safe_pub(msg_define.MSG_GUILD_WAR_SEND)
        return 1,{}

# 创建队伍(gongchengTeamCreate)
# 	请求
# 		队伍(team, [宠物id])
# 	返回
    def rc_gongchengTeamCreateSend(self,team,city,atk):
        # 宠物互斥
        petList = copy.deepcopy(team)
        rs = self.player.pet.checkSpecMutex(petList)
        if not rs:
            return 0, errcode.EC_PET_MUTEX_LIMIT


        from game.mgr.room import get_rpc_gongcheng
        rpc_gongcheng = get_rpc_gongcheng()
        if not rpc_gongcheng:
            return 0, errcode.EC_GETD_RPC_ROOM_FAIL
        
        rrv = rpc_gongcheng.gongchengTeamCreate(self.player.id,team)
        if not rrv:
            return 0, errcode.EC_GONGCHENG_ERR
        if rrv["err"]!=0:
            return 0, rrv["err"]


        rrv1 = rpc_gongcheng.gongchengSend(self.player.id,rrv["teamid"],city,atk)
        if not rrv1:
            return 0, errcode.EC_GONGCHENG_ERR
        if rrv1["err"]!=0:
            
            rpc_gongcheng.gongchengTeamDestroy(list(self.player.id,rrv["team"].keys()),False)
            
            return 0, rrv1["err"]

        self.player.safe_pub(msg_define.MSG_GUILD_WAR_SEND)
        return 1,{"team":rrv["team"]}



    def rc_gongchengGetPlayer(self,players):


        from game.mgr.room import get_rpc_gongcheng
        rpc_gongcheng = get_rpc_gongcheng()
        if not rpc_gongcheng:
            return 0, errcode.EC_GETD_RPC_ROOM_FAIL
        
        rrv = rpc_gongcheng.gongchengGetPlayer(self.player.id,players)
        if not rrv:
            return 0, errcode.EC_GONGCHENG_ERR
        if rrv["err"]!=0:
            return 0, rrv["err"]



        return 1,{"data":rrv["data"]}


    # 弃城操作
    # 一天只能弃1次城，有是否弃城的提示面板进行询问
    def rc_gongchengGiveup(self,cityid):


        from game.mgr.room import get_rpc_gongcheng
        rpc_gongcheng = get_rpc_gongcheng()
        if not rpc_gongcheng:
            return 0, errcode.EC_GETD_RPC_ROOM_FAIL
        
        rrv = rpc_gongcheng.gongchengGiveup(self.player.id,cityid)
        if not rrv:
            return 0, errcode.EC_GONGCHENG_ERR
        if rrv["err"]!=0:
            return 0, rrv["err"]

        guildId = self.player.guild.GetGuildId()
        if not guildId:
            return 0, errcode.EC_NO_GUILD
        rpc_guild = get_rpc_guild(guildId)
        if not rpc_guild:
            return 0, errcode.EC_NOT_FOUND_GUILD

        rpc_guild.GiveupCity()

        dUpdate = {}
        dUpdate["guildInfo"] = self.player.guild.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        return 1,resp


    def rc_gongchengLogList(self,city):


        from game.mgr.room import get_rpc_gongcheng
        rpc_gongcheng = get_rpc_gongcheng()
        if not rpc_gongcheng:
            return 0, errcode.EC_GETD_RPC_ROOM_FAIL
        
        rrv = rpc_gongcheng.gongchengLogList(self.player.id,city)
        if not rrv:
            return 0, errcode.EC_GONGCHENG_ERR
        if rrv["err"]!=0:
            return 0, rrv["err"]



        return 1,{"data":rrv["data"]}


    def rc_gongchengHistory(self):


        from game.mgr.room import get_rpc_gongcheng
        rpc_gongcheng = get_rpc_gongcheng()
        if not rpc_gongcheng:
            return 0, errcode.EC_GETD_RPC_ROOM_FAIL
        
        guildId = self.player.guild.GetGuildId()
        rrv = rpc_gongcheng.gongchengHistory(self.player.id,guildId)
        if not rrv:
            return 0, errcode.EC_GONGCHENG_ERR
        if rrv["err"]!=0:
            return 0, rrv["err"]



        return 1,{"data":rrv["data"]}

    def rc_gongchengLogData(self,fightlog):


        from game.mgr.room import get_rpc_gongcheng
        rpc_gongcheng = get_rpc_gongcheng()
        if not rpc_gongcheng:
            return 0, errcode.EC_GETD_RPC_ROOM_FAIL
        
        rrv = rpc_gongcheng.gongchengLogData(self.player.id,fightlog)
        if not rrv:
            return 0, errcode.EC_GONGCHENG_ERR
        if rrv["err"]!=0:
            return 0, rrv["err"]



        return 1,{"fightLog":rrv["fightlog"]}


# 个人排行榜(gongchengRankPerson)
# 	请求
# 		上期(pre, int) 1 上期
# 	返回
# 		榜单(data, map[string]json)
# 			名字(name, json)
# 			分数(score, int)
# 			公会名字(ghname, string) 
# 公会排行榜(gongchengRankGuild)
# 	请求
# 		上期(pre, int) 1 上期
# 	返回
# 		榜单(data, map[string]json)
# 			公会名字(name, json)
# 			分数(score, int)

    def rc_gongchengRankPerson(self,pre):


        from game.mgr.room import get_rpc_gongcheng
        rpc_gongcheng = get_rpc_gongcheng()
        if not rpc_gongcheng:
            return 0, errcode.EC_GETD_RPC_ROOM_FAIL
        
        rrv = rpc_gongcheng.gongchengRankPerson(self.player.id,pre)
        if not rrv:
            return 0, errcode.EC_GONGCHENG_ERR
        if rrv["err"]!=0:
            return 0, rrv["err"]



        return 1,{"data":rrv["data"]}

    def rc_gongchengRankGuild(self,pre):


        from game.mgr.room import get_rpc_gongcheng
        rpc_gongcheng = get_rpc_gongcheng()
        if not rpc_gongcheng:
            return 0, errcode.EC_GETD_RPC_ROOM_FAIL
        
        rrv = rpc_gongcheng.gongchengRankGuild(self.player.id,pre)
        if not rrv:
            return 0, errcode.EC_GONGCHENG_ERR
        if rrv["err"]!=0:
            return 0, rrv["err"]



        return 1,{"data":rrv["data"]}

    def rc_gongchengTag(self,city):


        from game.mgr.room import get_rpc_gongcheng
        rpc_gongcheng = get_rpc_gongcheng()
        if not rpc_gongcheng:
            return 0, errcode.EC_GETD_RPC_ROOM_FAIL
        
        rrv = rpc_gongcheng.gongchengTag(self.player.id,city)
        if not rrv:
            return 0, errcode.EC_GONGCHENG_ERR
        if rrv["err"]!=0:
            return 0, rrv["err"]



        return 1,{}

    def rc_gongchengCleanTag(self,city):


        from game.mgr.room import get_rpc_gongcheng
        rpc_gongcheng = get_rpc_gongcheng()
        if not rpc_gongcheng:
            return 0, errcode.EC_GETD_RPC_ROOM_FAIL
        
        rrv = rpc_gongcheng.gongchengCleanTag(self.player.id,city)
        if not rrv:
            return 0, errcode.EC_GONGCHENG_ERR
        if rrv["err"]!=0:
            return 0, rrv["err"]



        return 1,{}

    # 宣战操作
    # 
    def rc_gongchengWar(self,city):


        from game.mgr.room import get_rpc_gongcheng
        rpc_gongcheng = get_rpc_gongcheng()
        if not rpc_gongcheng:
            return 0, errcode.EC_GETD_RPC_ROOM_FAIL
        
        rrv = rpc_gongcheng.gongchengWar(self.player.id,city)
        if not rrv:
            return 0, errcode.EC_GONGCHENG_ERR
        if rrv["err"]!=0:
            return 0, rrv["err"]

        guildId = self.player.guild.GetGuildId()
        if not guildId:
            return 0, errcode.EC_NO_GUILD
        rpc_guild = get_rpc_guild(guildId)
        if not rpc_guild:
            return 0, errcode.EC_NOT_FOUND_GUILD

        from game.mgr.player import get_rpc_player
        nowtime=time.time()
        members = rpc_guild.getMembers()
        for one in members:
            rid = one.get("rid", 0)
            if not rid:
                continue
            
            # isRobot = one.get("isRobot", 1)
            # if isRobot:
            #     continue

            rpc_player = get_rpc_player(rid)
            if not rpc_player:
                continue
            rpc_player.gongchengNotiyGuild(city,True,nowtime)

        rpc_guild.WarCity()

        dUpdate = {}
        dUpdate["guildInfo"] = self.player.guild.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        return 1,resp
