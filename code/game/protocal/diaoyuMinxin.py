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

class DiaoyuRpcMixin(object):
    if 0:
        from game.core import player as player_md
        player = player_md.Player()

    def rc_diaoyuGetData(self):

        resAct = Game.res_mgr.res_activity.get(constant.ACTIVITY_DIAOYU)
        serverInfo = self.player.base.GetServerInfo()
        if not resAct.isOpen(serverInfo):
            return 0, errcode.EC_DIAOYU_NOTOPEN

        from game.mgr.room import get_rpc_diaoyu
        rpc_diaoyu = get_rpc_diaoyu()
        if not rpc_diaoyu:
            return 0, errcode.EC_GETD_RPC_ROOM_FAIL

        data = self.player.getDiaoyuInfo()
        import app
        rrv = rpc_diaoyu.hello(2,self.player.id,config.serverNo,app.addr,self.player.name,data,0,1)
        if not rrv:
            return 0, errcode.EC_CALL_RPC_ROOM_FAIL

        rrv = rpc_diaoyu.get(2,self.player.id)
        if not rrv:
            return 0, errcode.EC_CALL_RPC_ROOM_FAIL

        # 抛事件
        self.player.safe_pub(msg_define.MSG_JOIN_DIAOYU)
        if not self.player.cycleDay.Query("todayHasJoinDiaoyu", 0):
            self.player.safe_pub(msg_define.MSG_ACTIVITY_KF_JOIN)
            self.player.cycleDay.Set("todayHasJoinDiaoyu", 1)

        return 1,rrv["v"]

    def rc_diaoyuExit(self):
        respBag = self.player.diaoyu.exitdiaoyu()
        dUpdate = self.player.packRespBag(respBag)
        dUpdate["diaoyu"] = self.player.diaoyu.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp

    def rc_diaoyuChange(self,roomid):

        from game.mgr.room import get_rpc_diaoyu
        rpc_diaoyu = get_rpc_diaoyu()
        if not rpc_diaoyu:
            return 0, errcode.EC_GETD_RPC_ROOM_FAIL


        rrv = rpc_diaoyu.changeRoom(2,self.player.id,roomid)
        if not rrv:
            return 0, errcode.EC_DIAOYU_CHANGEROOM_ERR

        return 1,{"roomid":rrv["roomid"]}

    def rc_diaoyuStatus(self,status):

        self.player.diaoyu.status = status
        
        from game.mgr.room import get_rpc_diaoyu
        rpc_diaoyu = get_rpc_diaoyu()
        if not rpc_diaoyu:
            return 0, errcode.EC_GETD_RPC_ROOM_FAIL

        data = self.player.getDiaoyuInfo()

        rrv = rpc_diaoyu.update(2,self.player.id,data)
        if not rrv:
            return 0, errcode.EC_DIAOYU_STATUSERR

        
        return 1,{}

    def rc_diaoyudiaoyu(self):

        resAct = Game.res_mgr.res_activity.get(constant.ACTIVITY_DIAOYU)
        serverInfo = self.player.base.GetServerInfo()
        if not resAct.isOpen(serverInfo):
            return 0, errcode.EC_DIAOYU_NOTOPEN

        q = self.player.diaoyu.getFish()
        if not q:
            return 0, errcode.EC_DIAOYU_DIAOYU_NOABLE
        
        from game.mgr.room import get_rpc_diaoyu
        rpc_diaoyu = get_rpc_diaoyu()
        if not rpc_diaoyu:
            return 0, errcode.EC_GETD_RPC_ROOM_FAIL

        data = self.player.getDiaoyuInfo()

        rrv = rpc_diaoyu.updateNoBroadcast(2,self.player.id,data)
        if not rrv:
            return 0, errcode.EC_DIAOYU_DIAOYUERR

        
        dUpdate = {}
        
        dUpdate["diaoyu"] = self.player.diaoyu.to_init_data()


        resp = {
            "allUpdate": dUpdate,
            "id": q
        }

        return 1, resp

    def rc_diaoyuReward(self,quality):
        respBag = self.player.diaoyu.diaoyuReward(quality)
        dUpdate = self.player.packRespBag(respBag)
        dUpdate["diaoyu"] = self.player.diaoyu.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp

    def rc_diaoyuGetUser(self,id):
        

        from game.mgr.room import get_rpc_diaoyu
        rpc_diaoyu = get_rpc_diaoyu()
        if not rpc_diaoyu:
            return 0, errcode.EC_GETD_RPC_ROOM_FAIL

        rrv = rpc_diaoyu.getOneByServerNo(2,config.serverNo,id)
        if not rrv:
            return 0, errcode.EC_CALL_RPC_ROOM_FAIL
        

        # print("1111111111",config.serverNo,id,rrv)

        data = rrv["v"]



        if len(data)==0:
            return 0, errcode.EC_DIAOYU_NOFOUNDONE
        
        
        
        resp = {}
        resp["data"] = data[0]

        return 1, resp

    def rc_diaoyuRob(self,id,quality):
        diaoyuCatchNum = Game.res_mgr.res_common.get("diaoyuCatchNum")
        if not diaoyuCatchNum:
            return 0, errcode.EC_NORES

        diaoyuRobNum = Game.res_mgr.res_common.get("diaoyuRobNum")
        if not diaoyuRobNum:
            return 0, errcode.EC_NORES

        diaoyuXdayReward = Game.res_mgr.res_common.get("diaoyuXdayReward")
        if not diaoyuXdayReward:
            return 0, errcode.EC_NORES

        if self.player.diaoyu.getDiaoyuRob()>=diaoyuRobNum.i:
            return 0, errcode.EC_DIAOYU_ROB_USEUP

        

        from game.mgr.room import get_rpc_diaoyu
        rpc_diaoyu = get_rpc_diaoyu()
        if not rpc_diaoyu:
            return 0, errcode.EC_GETD_RPC_ROOM_FAIL

        rrv = rpc_diaoyu.getOneByServerNo(2,config.serverNo,id)
        if not rrv:
            return 0, errcode.EC_CALL_RPC_ROOM_FAIL
        
        data = rrv["v"]

        if len(data)==0:
            return 0, errcode.EC_DIAOYU_NOFOUNDONE

        if quality not in data[0]["data"]["yulou"]:
            return 0, errcode.EC_DIAOYU_NOFOUNDONEFISH
        
        res = Game.res_mgr.res_diaoyu.get(quality)
        if not res:
            return 0, errcode.EC_NORES
        
        if diaoyuCatchNum.i<=data[0]["data"]["catch"]:
            return 0, errcode.EC_DIAOYU_ROB_LIMIT

        from game.mgr.logicgame import LogicGame
        proxy = get_proxy_by_addr(data[0]["addr"], LogicGame._rpc_name_)
        if not proxy:
            return 0, errcode.EC_GETD_LOGIC_PROXY_ERR

        fdata = self.player.GetFightData()

        historydata={"id":self.player.id,"name":self.player.name,"quality":quality,"redhp":self.player.diaoyu.hp}

        resp  = proxy.diaoyuRob(self.player.id,data[0],fdata,historydata)
        if not resp:
            return 0, errcode.EC_CALL_LOGIC_PROXY_ERR

        redhp = resp["redhp"]
        self.player.diaoyu.sethp(redhp)

        fightResult = resp["fightLog"]["result"].get("win", 0)
        if fightResult:

            self.player.diaoyu.robFishOk(quality)
            self.player.diaoyu.addDiaoyuRob()

            myhistory = {"id":data[0]["id"],"name":data[0]["name"],"quality":quality}
            self.player.diaoyu.addHistory(2,myhistory)

            iOpenDay = self.player.base.GetServerOpenDay()
            reward = copy.deepcopy(res.reward)
            if iOpenDay>=diaoyuXdayReward.i:
                reward=copy.deepcopy(res.reward2)

            respBag = self.player.bag.add(reward, constant.ITEM_ADD_DIAOYU_ROBREWARD, wLog=True)
        else:
            self.player.safe_pub(msg_define.MSG_XIANSHITUISONGLIBAO_DIAOYU_F)
            myhistory = {"id":data[0]["id"],"name":data[0]["name"],"quality":quality}
            self.player.diaoyu.addHistory(3,myhistory)
            respBag = {}

        dUpdate = self.player.packRespBag(respBag)
        dUpdate["diaoyu"] = self.player.diaoyu.to_init_data()
        resp["allUpdate"] = dUpdate
        return 1, resp

    def rc_diaoyuRank(self):

        resp = {}



        from game.mgr.room import get_rpc_diaoyu
        rpc_diaoyu = get_rpc_diaoyu()
        if not rpc_diaoyu:
            return 0, errcode.EC_GETD_RPC_ROOM_FAIL


        resp = rpc_diaoyu.getRankList(self.player.id)
        if not resp:
            return 0, errcode.EC_DIAOYU_CHANGEROOM_ERR
        
        # resp["list"]=[]
        # resp["rank"]=666
        # resp["score"]=999

        return 1,resp