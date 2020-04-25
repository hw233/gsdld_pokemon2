#!/usr/bin/env python
# -*- coding:utf-8 -*-
import config
from game.common import utility
from game.define import constant, msg_define
from game import Game
import time
from random import randint
from corelib import spawn_later, log, spawn
import copy
import random
import ujson
import config

class PlayerGongcheng(utility.DirtyFlag):
    def __init__(self, owner):
        utility.DirtyFlag.__init__(self)
        self.owner = owner  # 拥有者
        self.time = 0 #上次退出时间
        self.isRankRewardList = [] #全民排行领奖id
        self.waratk = {} #宣战时间  str(cityid):time
        self.wardef = {} #被宣战时间  str(cityid):time

        self.save_cache = {} #存储缓存
        self.serverNo=""

        self.gongchengTaskData = {}
        
        # self.owner.sub(msg_define.MSG_ROLE_XLV_UPGRADE, self.event_lv_uprade)
    def enter(self):
        self.time=0

        # from game.mgr.room import get_rpc_gongcheng
        # rpc_gongcheng = get_rpc_gongcheng()
        # if rpc_gongcheng:
        #     pass

        self.markDirty()

    def markDirty(self):
        utility.DirtyFlag.markDirty(self)
        if self.owner:
            self.owner.markDirty()

    #存库数据
    def to_save_dict(self, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            self.save_cache = {}
            self.save_cache["time"] = self.time
            self.save_cache["isRankRewardList"] = self.isRankRewardList
            self.save_cache["waratk"] = self.waratk
            self.save_cache["wardef"] = self.wardef
        return self.save_cache

    #读库数据初始化
    def load_from_dict(self, data):
        self.time = data.get("time", 0)
        self.isRankRewardList = data.get("isRankRewardList", [])
        self.waratk = data.get("waratk", {})
        self.wardef = data.get("wardef", {})
        if self.waratk==0:
            self.waratk={}
        if self.wardef==0:
            self.wardef={}

    #登录初始化下发数据
    def to_init_data(self):
        self.serverNo=config.serverNo
        init_data = {}
        init_data["time"] = self.time
        
        iOpenServiceDay = self.owner.base.GetServerOpenDay()  # 开服天数

        isRankReward=1
        for k,v in Game.res_mgr.res_gongchengActive.items():
            if v.lastDay:
                if v.lastDayRank and v.openDay<=iOpenServiceDay<v.openDay+v.lastDay:
                    if k not in self.isRankRewardList:
                        isRankReward=0
                    break
        

        init_data["isRankReward"] = isRankReward
        init_data["waratk"] = self.waratk
        init_data["wardef"] = self.wardef
        
        return init_data

    def gongchengisRankReward(self,id):
        self.isRankRewardList.append(id)
        self.markDirty()

    # def roomMsg(self,msgtype,data):
    #     # if msgtype=="bye":
    #     #     spawn(self.owner.call, "gongchengExitPush", data["id"], noresult=True)
    #     # elif msgtype=="update":
    #     #     spawn(self.owner.call, "gongchengStatusPush", {"list":data}, noresult=True)
    #     # elif msgtype=="hello":
    #     #     spawn(self.owner.call, "gongchengEntetPush", {"list":data}, noresult=True)
    #
    #     if msgtype=="gmsg":
    #         spawn(self.owner.call, "gongchengMsgPush", {"list":data}, noresult=True)
    
    def uninit(self):
        # self.owner.unsub(msg_define.MSG_ROLE_XLV_UPGRADE, self.event_lv_uprade)
        pass

    def getTaskData(self):
        return self.gongchengTaskData

    def setTaskData(self, data):
        occupationCity = data.pop("occupationCity", {})
        occupationData = {}
        for cid, ghid in occupationCity.items():
            if ghid !=0 and ghid == self.owner.guild.GetGuildId():
                res = Game.res_mgr.res_gongcheng.get(int(cid))
                if int(res.BuildImg) in occupationData:
                    occupationData[int(res.BuildImg)] += 1
                else:
                    occupationData[int(res.BuildImg)] = 1

        self.gongchengTaskData = data
        self.occupationData = occupationData
        self.owner.safe_pub(msg_define.MSG_GET_GONGCHENG_TASK_DATA)

    def rsyncRpcGongchengTaskData(self):
        from game.mgr.room import get_rpc_gongcheng
        rpc_gongcheng = get_rpc_gongcheng()
        # if rpc_gongcheng:
        #     taskList = list(self.owner.task.gongcheng_tasks.keys())
        #     data = rpc_gongcheng.rsyncRpcGongchengTaskData(self.owner.id, taskList, config.serverNo)
        #     self.setTaskData(data)
    
    def exit(self):

        if self.time==0:
            
            self.time=time.time()
            self.markDirty()

            from game.mgr.room import get_rpc_gongcheng
            rpc_gongcheng = get_rpc_gongcheng()
            if rpc_gongcheng:
                rpc_gongcheng.bye(5,self.owner.id)

    def gongchengCount(self):

        from game.mgr.room import get_rpc_gongcheng
        rpc_gongcheng = get_rpc_gongcheng()
        if rpc_gongcheng:
            rpc_gongcheng.gongchengGuildCountScore()
            rpc_gongcheng.gongchengGuildReward()

    def gongchengNew(self):

        from game.mgr.room import get_rpc_gongcheng
        rpc_gongcheng = get_rpc_gongcheng()
        if rpc_gongcheng:
            rpc_gongcheng.gongchengNew()


    def gongchengMsg(self):

        from game.mgr.room import get_rpc_gongcheng
        rpc_gongcheng = get_rpc_gongcheng()
        if rpc_gongcheng:
            rpc_gongcheng.gongchengMsg(self.owner.id)

    def gongchengFucknpc(self):

        from game.mgr.room import get_rpc_gongcheng
        rpc_gongcheng = get_rpc_gongcheng()
        if rpc_gongcheng:
            rpc_gongcheng.gongchengFucknpc(self.owner.id)

    def gongchengNotiyGuild(self,cityid,atk,nowtime):
        if atk:
            self.waratk[str(cityid)]=nowtime
        else:
            self.wardef[str(cityid)]=nowtime

        self.markDirty()

        dUpdate={}
        dUpdate["gongcheng"]=self.to_init_data()

        spawn(self.owner.call, "PushGongcheng", {"allUpdate": dUpdate}, noresult=True)