#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from game.common import utility
from game.define import constant, errcode
from game import Game
from game.models.commonres import ModelCommonres
from corelib import spawn, log
from gevent import sleep
from corelib.frame import MSG_FRAME_STOP
from game.core.cycleData import CycleDay
from corelib.gtime import get_days, custom_today_time
from corelib import spawn, spawn_later
import random
from corelib import gtime
import time

# from dateutil import parser

lobbyTime = 1*3600

class CommonresMgr(utility.DirtyFlag):
    _rpc_name_ = "rpc_commonres_mgr"
    DATA_CLS = ModelCommonres

    def __init__(self):
        utility.DirtyFlag.__init__(self)

        self.reborn_timer = None
        
        self.tuangouCheatTime = Game.res_mgr.res_common.get("tuangouCheatTime")
        self.tuangouCheatRandTime = Game.res_mgr.res_common.get("tuangouCheatRandTime")
        self.tuangouCheatRandNum = Game.res_mgr.res_common.get("tuangouCheatRandNum")
        self.tuangouCheatStopTime = Game.res_mgr.res_common.get("tuangouCheatStopTime")
        

        self.cycleData = CycleDay(self)

        self.JJnum = {}  #进阶数量统计 
        self.zhuanpanmsg = []  #转盘消息 [[resid,name,poolid]]
        self.redpacket = {}  #红包 {key:obj}
        self.baishiList = {}  #拜师列表 玩家id为key
        self.ChengzhangjijinNum = 0 #成长基金购买人数
        self.redpacketindex = 0 #全局红包index
        self.loop_ChengzhangjijinNum_timer = None

        self.data = None
        self.save_cache = {}

        self._save_loop_task = None
        Game.sub(MSG_FRAME_STOP, self._frame_stop)
        
        # self.time2Count()

    # def time2Count(self):

    #     if self.reborn_timer:

    #         currHour = gtime.current_hour()
    #         if currHour not in self.tuangouCheatStopTime.arrayint1:
    #             self.addChargeNumByNum(random.randint(1, self.tuangouCheatRandNum.i))

    #         self.reborn_timer.kill(block=False)
    #         self.reborn_timer = None

    #     r=random.randint(0, self.tuangouCheatRandTime.i)

    #     self.reborn_timer = spawn_later((self.tuangouCheatTime.i+r)*60, self.time2Count)
    
    def markDirty(self):
        utility.DirtyFlag.markDirty(self)
        self.data.modify()

    def start(self):
        self.data = self.DATA_CLS.load(Game.store, self.DATA_CLS.TABLE_KEY)
        if not self.data:
            self.data = self.DATA_CLS()
        else:
            self.load_from_dict(self.data.dataDict)

        self.data.set_owner(self)

        self._save_loop_task = spawn(self._saveLoop)
        self.loop_ChengzhangjijinNum_timer = spawn(self.ChengzhangjijinNum_loop)

    def ChengzhangjijinNum_loop(self):
        num = random.randint(1,2)
        self.ChengzhangjijinNum += num
        self.markDirty()

    def _frame_stop(self):
        if self._save_loop_task:
            self._save_loop_task.kill(block=False)
            self._save_loop_task = None

        if self.reborn_timer:
            self.reborn_timer.kill(block=False)
            self.reborn_timer = None

        if self.loop_ChengzhangjijinNum_timer:
            self.loop_ChengzhangjijinNum_timer.kill(block=False)
            self.loop_ChengzhangjijinNum_timer = None

        self.save(forced=True, no_let=True)

    def _saveLoop(self):
        stime = 10 * 60
        while True:
            sleep(stime)
            try:
                self.save()
            except:
                log.log_except()

    def save(self, forced=False, no_let=False):
        self.data.save(Game.store, forced=forced, no_let=no_let)

    def load_from_dict(self, data):
        self.ChengzhangjijinNum = data.get("ChengzhangjijinNum", 0)
        self.redpacketindex = data.get("redpacketindex", 0)
        self.JJnum = data.get("JJnum", {})
        self.zhuanpanmsg = data.get("zhuanpanmsg", [])
        self.redpacket = data.get("redpacket", {})
        baishiList = data.get("baishiList", [])
        for k in baishiList:
            if (k["time"]+lobbyTime)>time.time(): #19/4/22 子博提出需求 从7*24改成1
                self.baishiList[k["id"]]=k
        self.cycleData.load_from_dict(data.get("cycleData", ""))

    def to_save_dict(self, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            self.save_cache = {}
            self.save_cache["ChengzhangjijinNum"] = self.ChengzhangjijinNum
            self.save_cache["redpacketindex"] = self.redpacketindex
            self.save_cache["JJnum"] = self.JJnum
            self.save_cache["zhuanpanmsg"] = self.zhuanpanmsg
            self.save_cache["redpacket"] = self.redpacket
            baishiList=[]
            for kk,vv in self.baishiList.items():
                baishiList.append(vv)
            self.save_cache["baishiList"] = baishiList
            self.save_cache["cycleData"] = self.cycleData.to_save_bytes()
        return self.save_cache

    def addChengzhangjijinNum(self):
        self.ChengzhangjijinNum += 1
        self.markDirty()
        for addr, logic in Game.rpc_logic_game:
            if logic:
                logic.broadcastChengzhangjijinNum(self.ChengzhangjijinNum, _no_result=True)

    def getChengzhangjijinNum(self):
        return self.ChengzhangjijinNum

    def addChargeNum(self):
        self.addChargeNumByNum(1)

    def addChargeNumByNum(self,num):
        v = self.getChargeNum()
        self.cycleData.Set("crChargeNum", v+num)

        resAct = Game.res_mgr.res_activity.get(constant.ACTIVITY_TUANGOU)
        serverInfo = Game.rpc_server_info.GetServerInfo()
        if resAct.isOpen(serverInfo):
            for addr, logic in Game.rpc_logic_game:
                if logic:
                    logic.crChargeNum(v+num, _no_result=True)
        return v

    def getChargeNum(self):
        return self.cycleData.Query("crChargeNum", 0)


    def getRedpackIsSet(self):
        return self.cycleData.Query("RedpackIsSet", 0)
    
    def setRedpackIsSet(self):
        return self.cycleData.Set("RedpackIsSet", 1)

    def addJJnum(self,type,lv):
        lvs = self.JJnum.get(type,{})
        num = lvs.get(lv,0)

        num+=1

        lvs[lv]=num
        self.JJnum[type]=lvs

        self.markDirty()

        resAct = Game.res_mgr.res_activity.get(constant.ACTIVITY_QMJJ)
        serverInfo = Game.rpc_server_info.GetServerInfo()
        openDay = get_days(serverInfo.get("opentime", 0))+ 1

        currtype = -1
        for kk,vv in Game.res_mgr.res_qmjj.items():
            if vv.day==openDay:
                currtype = vv.type
                break

        # print("3333333",currtype,type,lv,resAct,serverInfo,resAct.isOpen(serverInfo),str(currtype)==type)

        if str(currtype)==type:
            if resAct.isOpen(serverInfo):
                for addr, logic in Game.rpc_logic_game:
                    if logic:
                        logic.crJJnum(self.getJJnum(type), _no_result=True)

        return num


    def getJJnum(self,type):
        # if type == "15":
        #     return {"lv": [], "num": []}

        lvs = self.JJnum.get(type,{})
        
        lv = []
        num = []
        for kk,vv in lvs.items():
            lv.append(int(kk))
            num.append(vv)
        obj = {"lv":lv,"num":num}
        
        return obj

    def shituBaishi(self,id,name,sex,lv,fa,vipLv,portrait,headframe):
        self.baishiList[id]={"time":time.time(),"id":id,"name":name,"sex":sex,"lv":lv,"fa":fa,"vipLv":vipLv,"portrait":portrait,"headframe":headframe}
        self.markDirty()
        return {}

    def shituGetBaishi(self):
        baishiList = []
        for kk,vv in self.baishiList.items():
            if (vv["time"]+lobbyTime)>time.time(): #19/4/22 子博提出需求 从7*24改成1
                baishiList.append(vv)
        return baishiList

    def shituBaishiRemove(self,id):
        self.baishiList.pop(id,{})
        self.markDirty()



    def makerp(self,total,n):
        x=[random.random() for i in range(n)]
        e=[int(i/sum(x)*(total-n))+1 for i in x]           #每人留一分,剩余随机分，用四舍五入可能会超过总数
        re=total-sum(e)
        u=[random.randint(0,n-1) for i in range(re)]     #截断取整剩的零头再随机给各人1分
        for i in range(re):            
            e[u[i]]+=1
        return e

    def getRedpacket(self):
        isset=self.getRedpackIsSet()
        if not isset:
            self.setRedpackIsSet()
            self.markDirty()

            delk=[]
            nt=time.time()
            for k,v in self.redpacket.items():
                if not v["uid"]: #清除系统
                    delk.append(k)
                elif len(v["uids"])>=v["able"]: #清除已抢完
                    delk.append(k)
                elif v["startTime"]+3600*24*3<nt: #清除3天前的红包
                    delk.append(k)

            for k in delk:
                del self.redpacket[k]

            resAct = Game.res_mgr.res_activity.get(constant.ACTIVITY_CHINESENEWYEAR_REDPACKET)
            serverInfo = Game.rpc_server_info.GetServerInfo()
            if resAct.isOpen(serverInfo):

                for k,v in Game.res_mgr.res_redpacket.items():
                    # x=parser.parse(k)
                    # ts=time.mktime(x.timetuple())
                    ts=custom_today_time(k)
                    for _ in range(v.times):
                        self.redpacketindex+=1
                        self.redpacket[str(self.redpacketindex)]={
                            "startTime":ts,
                            "type":v.type,
                            "num":v.num,
                            "able":v.able,
                            "uid":0,
                            "uids":[],
                            "e":self.makerp(v.num,v.able),
                        }
                    

        return self.redpacket

        

    def pickRedpacket(self,uid,key):
        
        v=self.redpacket.get(key,None)
        if not v:
            return None, errcode.EC_NOFOUND

        if len(v["uids"])>=v["able"]:
            return None, errcode.EC_REDPACKET_IS_EMPTY

        if not v["e"]:
            return None, errcode.EC_REDPACKET_IS_EMPTY

        if v["startTime"]>time.time():
            return None, errcode.EC_REDPACKET_IS_EMPTY

        for one in v["uids"]:
            if one["uid"]==uid:
                return None, errcode.EC_REDPACKET_IS_GET

        self.markDirty()

        num=v["e"].pop()
        v["uids"].append({"uid":uid,"num":num})

        return {"num":num,"type":v["type"]},0

    def sendRedpacket(self,uid,index,type,num,able):
        
        self.redpacket[str(uid)+"_"+str(index)]={
            "startTime":time.time(),
            "type":type,
            "num":num,
            "able":able,
            "uid":uid,
            "uids":[],
            "e":self.makerp(num,able),
        }

        self.markDirty()
        return self.redpacket

    def zhuanpanAddMsg(self,resid,name,poolid):
        self.zhuanpanmsg.append([resid,name,poolid])
        self.markDirty()

    def zhuanpanGetMsg(self,resid):
        x=[]
        for v in self.zhuanpanmsg:
            if v[0]==resid:
                x.append({"name":v[1],"poolid":v[2]})

        return x