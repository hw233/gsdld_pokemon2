#!/usr/bin/env python
# -*- coding:utf-8 -*-
import time
import random
import pickle
import ujson

from gevent import sleep

from game.common import utility
from game.models.room import ModelRoom
from game.core.cycleData import CycleDay
from game.define import constant, errcode, msg_define

from grpc import DictExport, DictItemProxy, get_proxy_by_addr

from corelib import log, spawn, gtime

from corelib.frame import Game, MSG_FRAME_STOP

import config
import copy

from game.define.store_define import TN_G_GONGCHENGPLAYER, TN_G_GONGCHENGTEAM



# from game import Game
    

def get_rpc_room(playTogether):

    if 3==int(config.serverNo[0:2]) and not hasattr(config, "p3cross"):
        print('test common room yabiao')
        addr = Game.rpc_room_mgr_common.get_addr()
        proxy = get_proxy_by_addr(addr, RoomMgrCommon._rpc_name_)
        return proxy

    serverInfo = Game.rpc_server_info.GetServerInfo()
    openDay = gtime.get_days(serverInfo.get("opentime", 0))+ 1
    
    startD = Game.res_mgr.res_activity.get(constant.ACTIVITY_YABIAO).openDayRange[0]
    if openDay<startD:
        addr = Game.rpc_room_mgr_common.get_addr()
        proxy = get_proxy_by_addr(addr, RoomMgrCommon._rpc_name_)
        return proxy

    if hasattr(config, "room_addr"):
        proxy = get_proxy_by_addr(config.room_addr, RoomMgr._rpc_name_)
        return proxy
    else:
        addr = Game.rpc_room_mgr_common.get_addr()
        proxy = get_proxy_by_addr(addr, RoomMgrCommon._rpc_name_)
        return proxy


def get_rpc_diaoyu():

    if 3==int(config.serverNo[0:2]) and not hasattr(config, "p3cross"):
        print('test common room diaoyu')
        addr = Game.rpc_room_mgr_common.get_addr()
        proxy = get_proxy_by_addr(addr, RoomMgrCommon._rpc_name_)
        return proxy

    if hasattr(config, "diaoyu_addr"):
        proxy = get_proxy_by_addr(config.diaoyu_addr, RoomMgr._rpc_name_)
        return proxy
    else:
        addr = Game.rpc_room_mgr_common.get_addr()
        proxy = get_proxy_by_addr(addr, RoomMgrCommon._rpc_name_)
        return proxy

def get_rpc_wakuang():

    if 3==int(config.serverNo[0:2]) and not hasattr(config, "p3cross"):
        print('test common room wakuang')
        addr = Game.rpc_room_mgr_common.get_addr()
        proxy = get_proxy_by_addr(addr, RoomMgrCommon._rpc_name_)
        return proxy

    if hasattr(config, "wakuang_addr"):
        proxy = get_proxy_by_addr(config.wakuang_addr, RoomMgr._rpc_name_)
        return proxy
    else:
        addr = Game.rpc_room_mgr_common.get_addr()
        proxy = get_proxy_by_addr(addr, RoomMgrCommon._rpc_name_)
        return proxy

def get_rpc_boss():

    if 3==int(config.serverNo[0:2]) and not hasattr(config, "p3cross"):
        print('test common room boss')
        addr = Game.rpc_room_mgr_common.get_addr()
        proxy = get_proxy_by_addr(addr, RoomMgrCommon._rpc_name_)
        return proxy

    serverInfo = Game.rpc_server_info.GetServerInfo()
    openDay = gtime.get_days(serverInfo.get("opentime", 0))+ 1
    
    kfbossWorldDay = Game.res_mgr.res_common.get("kfbossWorldDay")
    if openDay<kfbossWorldDay.i:
        addr = Game.rpc_room_mgr_common.get_addr()
        proxy = get_proxy_by_addr(addr, RoomMgrCommon._rpc_name_)
        return proxy

    if hasattr(config, "boss_addr"):
        proxy = get_proxy_by_addr(config.boss_addr, RoomMgr._rpc_name_)
        return proxy
    else:
        addr = Game.rpc_room_mgr_common.get_addr()
        proxy = get_proxy_by_addr(addr, RoomMgrCommon._rpc_name_)
        return proxy

def get_rpc_gongcheng():

    if 3==int(config.serverNo[0:2]) and not hasattr(config, "p3cross"):
        print('test common room gongcheng')
        addr = Game.rpc_room_mgr_common.get_addr()
        proxy = get_proxy_by_addr(addr, RoomMgrCommon._rpc_name_)
        return proxy

    if hasattr(config, "gongcheng_addr"):
        proxy = get_proxy_by_addr(config.gongcheng_addr, RoomMgr._rpc_name_)
        return proxy
    else:
        addr = Game.rpc_room_mgr_common.get_addr()
        proxy = get_proxy_by_addr(addr, RoomMgrCommon._rpc_name_)
        return proxy

def get_rpc_jiujiyishou():

    if 3==int(config.serverNo[0:2]) and not hasattr(config, "p3cross"):
        print('test common room jiujiyishou')
        addr = Game.rpc_room_mgr_common.get_addr()
        proxy = get_proxy_by_addr(addr, RoomMgrCommon._rpc_name_)
        return proxy

    if hasattr(config, "jiujiyishou_addr"):
        proxy = get_proxy_by_addr(config.jiujiyishou_addr, RoomMgr._rpc_name_)
        return proxy
    else:
        addr = Game.rpc_room_mgr_common.get_addr()
        proxy = get_proxy_by_addr(addr, RoomMgrCommon._rpc_name_)
        return proxy
        
class RoomMgr(utility.DirtyFlag):

    _rpc_name_ = 'rpc_room_mgr'
    DATA_CLS = ModelRoom

    def makeContent(self,type,rid,msg):

        data={"rid":rid,"showName":True,"name":"","vip":"0","isMsg":1,"msg":{"ct":4,"g":0,"mt":2,"msg":msg},"msgType":str(type)}
        # data={"ct":4,"g":0,"mt":2,"msg":msg}
        
        s = ujson.dumps(data)
        return s

    def __init__(self):



        utility.DirtyFlag.__init__(self)


        self.data = None
        self.save_cache = {}

        self.score = {}  #钓鱼月-分数
        self.dealmm = "" #钓鱼月-已经处理过的月份

        self.bossScoreDay={} #boss-服务器得分 key=gid val={gid,groupkey,score,addr,[pid],ghname,sid} //gid=工会id
        self.bossScoreDayPrior={} #boss-上期服务器得分 key=gid val={gid,groupkey,score,addr,[pid],ghname,sid} //gid=工会id
        self.bossScoreDayDeal="" #boss-处理过的日期

        self.serverScoreDay={} #挖矿-服务器得分 key=sid val={sid,score,addr,[pid]}
        self.serverScoreDayDeal="" #挖矿-处理过的日期
        self.serverScoreMonth={} #挖矿月-服务器得分 key=sid val={sid,score,addr,[pid]}
        self.serverScoreMonthDeal="" #挖矿月-处理过的月期

        self.serverScoreGongchengTime=0 #攻城周期-处理时间点

        self.groupkeyData = {} #分组数据 {groupkey:{??}}
        self.gongchengAct = [] #攻城全球活动 [{"d":yyyymmdd,"s":{}}]
        
        self.type_sid__groupkey={} #通过【type】【sid】找到groupkey

        ###############################
        self.group={} # key = groupkey value=obj{id:{"id","addr","data"} } 服务器内分组
        self.typeid2groupkey={} #key = type+"-"+id  value=groupkey 通过【type+"-"+id】找到groupkey
        ###############################

        ###############################
        self.gongchengPlayer={}
        self.gongchengTeam={}
        self.fightlog={}
        self.fightlogid=0
        self.gongchengteamid=0
        ###############################

        self.cycleData = CycleDay(self)

        self._save_loop_task = None
        Game.sub(MSG_FRAME_STOP, self._frame_stop)

    def cPickleIDDATAencode(self,org):
        cp={}
        cp["id"]=org["id"]
        cp["data"]=pickle.dumps(org)
        return cp

    def cPickleIDDATAdecode(self,cpd):
        org=pickle.loads(cpd["data"])
        return org


    def start(self):

        self.data = self.DATA_CLS.load(Game.store, self.DATA_CLS.TABLE_KEY)
        if not self.data:
            self.data = self.DATA_CLS()
        else:
            self.load_from_dict(self.data.dataDict)

        self.data.set_owner(self)

        self._save_loop_task = spawn(self._saveLoop)

        self.initRoom()

        spawn(self.sendRewardDiaoyuMonth)
        spawn(self.sendRewardWakuangMonth)
        
        spawn(self.sendRewardWakuang) #3
        spawn(self.sendRewardKfboss) #4

        spawn(self.sendRewardGongcheng) #5

        

        # room_dayReset = False
        # try:
        #     room_dayReset = config.room_dayReset
        # except:
        #     room_dayReset = False
        
        # if room_dayReset:
        
        Game.sub(msg_define.MSG_WEE_HOURS, self.event_player_wee_hours)
        Game.sub(msg_define.MSG_TEN_PM, self.event_player_ten_pm)

        print('common room start ...')

    def event_player_ten_pm(self):
        pass

        

    def event_player_wee_hours(self):
        
        # 合服特殊处理
        # self.delsid(1)
        # self.addsid(1)

        self.delsid(2)
        self.addsid(2)

        self.gongchengGuildReward()
        self.gongchengGuildCountScore()

    def delsid(self,type):
        for groupkey in self.type_sid__groupkey[type].values():
            self.group.pop(groupkey,None)

            dellist=[]
            for k,v in self.typeid2groupkey.items():
                if v==groupkey:
                    dellist.append(k)

            for v in dellist:
                del self.typeid2groupkey[v]
            
        self.type_sid__groupkey[type]={}
        self.markDirty()


    # groupkey 构成: id+自增(0~x)
    def addsid(self,type):
        print('room -------------',type)
        self.type_sid__groupkey[type]=self.type_sid__groupkey.get(type,{})
        
        for id, obj in Game.res_mgr.res_kuafuGroup.items():
            if obj.type!=type:
                continue
            
            random.shuffle(obj.sid)

            for sid in obj.sid:
                if sid in self.type_sid__groupkey[type]:
                    continue

                # waitIdSidNum.append((id,sid,obj.num,))
                gks={} # groupkey:num
                nkid=0 # 新groupkey的x
                for groupkey in self.type_sid__groupkey[type].values():
                    perfix=str(id)+'-'
                    if not groupkey.startswith(perfix):
                        continue
                    
                    gks[groupkey]=gks.get(groupkey,0)+1

                    x=int(groupkey[len(perfix):])
                    if x<nkid:
                        continue
                    nkid=x+1


                groupkey=""
                for k,v in gks.items():
                    if v<obj.num:
                        groupkey=k
                        break
                
                if not groupkey:
                    groupkey=str(id)+'-'+str(nkid)
                
                self.type_sid__groupkey[type][sid]=groupkey
                    
                print('room (sid,groupkey)',sid,groupkey)

        print('room -------------')
        self.markDirty()

    def initRoom(self):
        
        # TODO remove this code
        # self.type_sid__groupkey={}
        # self.groupkeyData={}
        
        for v in range(6):
            type=v+1
            self.addsid(type)

        # print('-------------',self.type_sid__groupkey)
        self.markDirty()




    def _frame_stop(self):
        if self._save_loop_task:
            self._save_loop_task.kill(block=False)
            self._save_loop_task = None



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

        self.score = data.get("score", {})
        self.dealmm = data.get("dealmm", "")

        serverScoreDay = data.get("serverScoreDay", [])
        for v in serverScoreDay:
            self.serverScoreDay[v["sid"]]=v

        self.serverScoreDayDeal = data.get("serverScoreDayDeal", "")

        bossScoreDay = data.get("bossScoreDay", [])
        for v in bossScoreDay:
            self.bossScoreDay[v["gid"]]=v

        bossScoreDayPrior = data.get("bossScoreDayPrior", [])
        for v in bossScoreDayPrior:
            self.bossScoreDayPrior[v["gid"]]=v

        self.bossScoreDayDeal = data.get("bossScoreDayDeal", "")

        serverScoreMonth = data.get("serverScoreMonth", [])
        for v in serverScoreMonth:
            self.serverScoreMonth[v["sid"]]=v
            
        self.serverScoreMonthDeal = data.get("serverScoreMonthDeal", "")
        self.serverScoreGongchengTime = data.get("serverScoreGongchengTime", 0)
        self.gongchengteamid = data.get("gongchengteamid", 0)
        
        self.groupkeyData = data.get("groupkeyData", {})
        self.gongchengAct = data.get("gongchengAct", [])

        type_sid__groupkey = data.get("type_sid__groupkey", None)
        if type_sid__groupkey:
            self.type_sid__groupkey=pickle.loads(type_sid__groupkey)
        
 
        self.cycleData.load_from_dict(data.get("cycleData", ""))
        


    def to_save_dict(self, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            self.save_cache = {}

            self.save_cache["score"] = self.score
            self.save_cache["dealmm"] = self.dealmm
            
            serverScoreDay = []
            for kk, vv in self.serverScoreDay.items():
                serverScoreDay.append(vv)
            self.save_cache["serverScoreDay"] = serverScoreDay
            
            self.save_cache["serverScoreDayDeal"] = self.serverScoreDayDeal
            
            bossScoreDay = []
            for kk, vv in self.bossScoreDay.items():
                bossScoreDay.append(vv)
            self.save_cache["bossScoreDay"] = bossScoreDay
            
            bossScoreDayPrior = []
            for kk, vv in self.bossScoreDayPrior.items():
                bossScoreDayPrior.append(vv)
            self.save_cache["bossScoreDayPrior"] = bossScoreDayPrior
            
            self.save_cache["bossScoreDayDeal"] = self.bossScoreDayDeal
            
            serverScoreMonth = []
            for kk, vv in self.serverScoreMonth.items():
                serverScoreMonth.append(vv)
            self.save_cache["serverScoreMonth"] = serverScoreMonth

            self.save_cache["serverScoreMonthDeal"] = self.serverScoreMonthDeal
            self.save_cache["serverScoreGongchengTime"] = self.serverScoreGongchengTime
            self.save_cache["gongchengteamid"] = self.gongchengteamid


                        
            self.save_cache["groupkeyData"] = self.groupkeyData
            self.save_cache["gongchengAct"] = self.gongchengAct

            self.save_cache["type_sid__groupkey"] = pickle.dumps(self.type_sid__groupkey)
            
            self.save_cache["cycleData"] = self.cycleData.to_save_bytes()

        return self.save_cache


    def markDirty(self):
        utility.DirtyFlag.markDirty(self)
        self.data.modify()

    


    def no2id(self,no):
        return Game.res_mgr.res_no2id_kuafuMap[no]

    def getgroup(self,groupkey):
        t = time.time()
        retv = []
        for key in self.group[groupkey].keys():
            if self.group[groupkey][key]["endtime"]!=0 and self.group[groupkey][key]["endtime"] < t:
                del self.group[groupkey][key]
            else:
                if self.group[groupkey][key]["show"]:
                    retv.append(self.group[groupkey][key])

        return retv

    def findRoomId(self,groupkey):

        RoomMaxPeople = Game.res_mgr.res_common.get("RoomMaxPeople")

        rl = self.getRoomData(groupkey)

        for rlid in range(len(rl)):
            if rl[rlid]<RoomMaxPeople.i:
                return rlid

        print('error, check config RoomMaxNumBase',RoomMaxPeople.i,rl)
        return 0

    def getRoomData(self,groupkey):
        RoomMaxNumBase = Game.res_mgr.res_common.get("RoomMaxNumBase")

        l = len(self.group[groupkey])

        maxid = -int((-l/RoomMaxNumBase.i))
        
        rl = [0] * (maxid+1)

        for v in self.group[groupkey].values():
            if v["roomid"]<len(rl):
                rl[v["roomid"]]=rl[v["roomid"]]+1
        
        return rl
    
    def changeRoom(self,type,id,roomid):
        groupkey = self.typeid2groupkey.get(str(type)+"-"+str(id),"")
        if not groupkey:
            return {"v":False}
        
        rl = self.getRoomData(groupkey)
        if roomid>=len(rl):
            return {"roomid":self.group[groupkey][id]["roomid"]}
        
        RoomMaxPeople = Game.res_mgr.res_common.get("RoomMaxPeople")
        if rl[roomid]>=RoomMaxPeople.i:
            return {"roomid":self.group[groupkey][id]["roomid"]}
        
        self.group[groupkey][id]["roomid"]=roomid

        self.groupMsg(groupkey,"update",self.group[groupkey][id])
        return {"roomid":self.group[groupkey][id]["roomid"]}
    
    def hello(self,type,id,serverNo,addr,name,data,endtime,miniroom):

        addr=tuple(addr)

        # 进入前先退出之前房间
        if (str(type)+"-"+str(id)) in self.typeid2groupkey:
            self.bye(type,id)

        # 获取服务器id和组id
        sid=self.no2id(serverNo)
        # print('1111111',self.type_sid__groupkey,type,sid,id,serverNo)
        groupkey=self.type_sid__groupkey[type][sid]

        # 如果没这个组就创建这个组
        if groupkey not in self.group:
            self.group[groupkey]={}
   
        rid = 0
        if miniroom:
            rid = self.findRoomId(groupkey)


        # 进入这个组
        gdata={"sid":sid,"data":data,"endtime":endtime,"roomid":rid,
            "type":type,"id":id,"addr":addr,"name":name,"show":True}

        # 广播
        self.groupMsg(groupkey,"hello",gdata)
        
        self.group[groupkey][id]=gdata

        # 记录个人进入的组id
        self.typeid2groupkey[str(type)+"-"+str(id)] = groupkey

        if type==4:

            kfbossHpBase = Game.res_mgr.res_common.get("kfbossHpBase")
            kfbossShieldBase = Game.res_mgr.res_common.get("kfbossShieldBase")
            kfbossNokillBase = Game.res_mgr.res_common.get("kfbossNokillBase")

            sdata = self.groupkeyData.get(groupkey,{})
            self.groupkeyData[groupkey]=sdata

            bossid=sdata.get("bossid",0)
            if not bossid:
  

                bosslist=sdata.get("bosslist",[])
                sdata["bosslist"]=bosslist

                if len(bosslist)==0:
                    for i in range(len(Game.res_mgr.res_kfBoss)):
                        bosslist.append(i+1)
                
                    if self._rpc_name_=='rpc_room_mgr':
                        random.shuffle(bosslist)
                        print('new boss list by shuffle')
                    else:
                        print('new boss list no shuffle')


                bosshp = sdata.get("bosshp",0)
                bossAtk = sdata.get("bossAtk",1000000)
                if bosshp:
                    bossAtk = int(bossAtk*kfbossNokillBase.i/100)
                

                #动态血盾            
                sdata["kfbossMaxHp"]=int(bossAtk*kfbossHpBase.i/100)
                sdata["bosshp"]=sdata["kfbossMaxHp"]
                sdata["kfbossShieldMax"]=int(bossAtk*kfbossShieldBase.i/100)

                sdata["box"]={} #箱子id:开箱人id 空为没人开
                sdata["boxid"]=0 #箱子id计数器 用来生成箱子id
                sdata["kfbossLastP"]=100 #上次生成盾的百分点
                sdata["kfbossShield"]=0 #盾量

                sdata["bossid"]=bosslist[0] #bossid
                bosslist.pop(0) #boss列表弹出
                
                
                
                print('new boss sdata',sdata)

        return True

    def bye(self,type,id,noticmyself=False):


        # 清除个人纪录
        groupkey = self.typeid2groupkey.pop(str(type)+"-"+str(id),"")

        if groupkey in self.group:
            # 离开组
            if not noticmyself:
                v = self.group[groupkey].pop(id,None)
                if v:
                    self.groupMsg(groupkey,"bye",v)
            else:
                if id in self.group[groupkey]:
                    self.groupMsg(groupkey,"bye",self.group[groupkey][id])
                    self.group[groupkey].pop(id,None)
        return True
    
    def msg(self,type,id,content):
        groupkey = self.typeid2groupkey.get(str(type)+"-"+str(id),"")
        if not groupkey:
            return {"v":False}
        data = {}
        data["rid"] = id
        data["content"] = content
        data["type"] = type

        self.groupMsg(groupkey,"msg",data)
        d = ujson.loads(content)
        rid = d.get("rid", 0)
        name = d.get("name", '')
        vip = d.get("vip", 0)
        msg = d.get("msg", {}).get("msg", '')
        isMsg = d.get("isMsg", 0)
        if isMsg:
            print("PlayerWorldMSG", "%s|%s|%s|%s" % (rid, name, vip, msg))
            Game.glog.log2File("PlayerWorldMSG", "%s|%s|%s|%s" % (rid, name, vip, msg))
        return {"v":True}

    def hide(self,type,id):
        groupkey = self.typeid2groupkey.get(str(type)+"-"+str(id),"")
        if not groupkey:
            return {"v":False}
        self.group[groupkey][id]["show"]=False
        self.groupMsg(groupkey,"bye",self.group[groupkey][id])
        return {"v":True}
    
    def show(self,type,id):
        groupkey = self.typeid2groupkey.get(str(type)+"-"+str(id),"")
        if not groupkey:
            return {"v":False}
        self.group[groupkey][id]["show"]=True
        self.groupMsg(groupkey,"hello",self.group[groupkey][id])
        return {"v":True}

    def update(self,type,id,data):
        groupkey = self.typeid2groupkey.get(str(type)+"-"+str(id),"")
        if not groupkey:
            return {"v":False}
        self.group[groupkey][id]["data"]=data
        self.groupMsg(groupkey,"update",self.group[groupkey][id])
        return {"v":True}

    def updateNoBroadcast(self,type,id,data):
        groupkey = self.typeid2groupkey.get(str(type)+"-"+str(id),"")
        if not groupkey:
            return {"v":False}
        self.group[groupkey][id]["data"]=data
        # self.groupMsg(groupkey,"update",self.group[groupkey][id])
        return {"v":True}

    def get(self,type,id):
        
        groupkey = self.typeid2groupkey.get(str(type)+"-"+str(id),"")
        if groupkey not in self.group:
            return {"v":[]}
        
        return {"v":self.getgroup(groupkey)}

    def getByServerNo(self,type,serverNo):
        # 获取服务器id和组id
        sid=self.no2id(serverNo)
        
        groupkey=self.type_sid__groupkey[type][sid]
        if groupkey not in self.group:
            return {"v":[],"common":{}}

        return {"v":self.getgroup(groupkey),"common":self.groupkeyData.get(groupkey,{})}

    def getOne(self,type,id,otherid):
        
        groupkey = self.typeid2groupkey.get(str(type)+"-"+str(id),"")
        if groupkey not in self.group:
            return {"v":[]}
        if otherid not in self.group[groupkey]:
            return {"v":[]}
        return {"v":[self.group[groupkey][otherid]]}

    def getOneByServerNo(self,type,serverNo,otherid):
        
        # 获取服务器id和组id
        sid=self.no2id(serverNo)
        groupkey=self.type_sid__groupkey[type][sid]
        if groupkey not in self.group:
            return {"v":[]}
        if otherid not in self.group[groupkey]:
            return {"v":[]}
        return {"v":[self.group[groupkey][otherid]]}


    def getSvrList(self,type,serverNo):
        sid=self.no2id(serverNo)
        groupkey=self.type_sid__groupkey[type][sid]

        s = []
        for kk,vv in self.type_sid__groupkey[type].items():
            if vv==groupkey:
                s.append(kk)
        
        s.sort()
        
        return {"sid":sid,"s":s}


    
    def groupMsg(self,groupkey,msgtype,data):
        if groupkey in self.group:
            addr2fid={}
            for fid, obj in self.group[groupkey].items():
                if obj["addr"] not in addr2fid:
                    addr2fid[obj["addr"]]=[]
                addr2fid[obj["addr"]].append(fid)


            for addr, fids in addr2fid.items():
                self.pushMsg(addr,msgtype,fids,data)
    
    def pushMsg(self,addr,msgtype,ids,data):
        from game.mgr.logicgame import LogicGame
        proxy = get_proxy_by_addr(addr, LogicGame._rpc_name_)
        if proxy:
            st=time.time()
            try:
                proxy.roomMsg(msgtype,ids,data, _no_result=True)
                et=time.time()
                if et-st>3:
                    print("roomMsg.usingtime", "%s|%s|%s|%s|%s" % (msgtype,ids,et-st,addr,data))
                    Game.glog.log2File("roomMsg.usingtime", "%s|%s|%s|%s|%s" % (msgtype,ids,et-st,addr,data))
            except Exception as e:
                et=time.time()
                print("proxy.roomMsg.fail", "%s|%s|%s|%s|%s|%s" % (msgtype,ids,et-st,addr,e,data))
                Game.glog.log2File("proxy.roomMsg.fail", "%s|%s|%s|%s|%s|%s" % (msgtype,ids,et-st,addr,e,data))
    
    def getGroupkeyByTypeSid(self,type,sid):
        return self.type_sid__groupkey[type].get(sid,None)



    #########################################################
    #########################################################
    #########################################################


    # 钓鱼 每月发奖
    def sendRewardDiaoyuMonth(self):

        sleep(60)

        while True:


            mm = gtime.getMM()
            nt = gtime.getDD()
            if mm!=self.dealmm and "01"==nt:

                print("reward sendRewardDiaoyuMonth")
                
                self.dealmm=mm

                rank = sorted(list(self.score.values()), key=lambda data:data["score"], reverse=True)
                for index in range(len(rank)):
                    if 10000==index:
                        break
                    print("reward index:",index,rank[index]["id"])
                    success = False
                    from game.mgr.logicgame import LogicGame
                    proxy = get_proxy_by_addr(rank[index]["addr"], LogicGame._rpc_name_)

                    success=False
                    
                    if proxy:
                        
                        try:
                            proxy.diaoyuRank(index,rank[index], _no_result=True)
                            success = True
                        except:
                            success = False
                    print("reward index:",index,success)
                print("reward done")

                self.score = {}
                self.markDirty()
            
            sleep(60)

    # 挖矿 活动结束发奖
    def sendRewardWakuang(self):

        sleep(60)

        resAct = Game.res_mgr.res_activity.get(constant.ACTIVITY_WAKUANG)

        while True:



            nt = gtime.getDD()
            
            if not resAct.isOpenNoServerInfo() and nt!=self.serverScoreDayDeal and self.serverScoreDay:
                
                print("reward sendRewardWakuang")

                for groupkey in self.group.keys():
                    print("dayReward groupkey:",groupkey)
                    s = []
                    for kk,vv in self.type_sid__groupkey[3].items():
                        if vv==groupkey:
                            s.append(kk)
                    gscore=[]
                    for ss in s:
                        ScoreDay = self.serverScoreDay.get(ss,None)
                        if ScoreDay:
                            gscore.append(ScoreDay)
                    

                    rank = sorted(gscore, key=lambda data:data["score"], reverse=True)
                    for index in range(len(rank)):


                        print("dayReward index:",index,rank[index]["pid"])
                        success = False
                        from game.mgr.logicgame import LogicGame
                        proxy = get_proxy_by_addr(rank[index]["addr"], LogicGame._rpc_name_)
                        success=False
                        if proxy:
                            
                            try:
                                proxy.wakuangRankDay(index,rank[index], _no_result=True)
                                success = True
                            except:
                                success = False
                        print("dayReward index:",index,success)
                print("dayReward done")

               
                self.serverScoreDayDeal = nt
                self.serverScoreDay = {}

                self.delsid(3)
                self.addsid(3)

                self.markDirty()
            
            sleep(60)

    # kfboss奖励内部
    def bossReward(self,nt):

        print("reward bossReward")

        for groupkey in self.group.keys():
            print("bossReward groupkey:",groupkey)

            gscore=[]
            for v in self.bossScoreDay.values():
                if v["groupkey"]==groupkey:
                    gscore.append(v)
            

            rank = sorted(gscore, key=lambda data:data["score"], reverse=True)
            rewardpid=[]
            for index in range(len(rank)):


                print("bossReward index:",index,rank[index]["pid"])
                success = False
                from game.mgr.logicgame import LogicGame
                proxy = get_proxy_by_addr(rank[index]["addr"], LogicGame._rpc_name_)
                success=False
                if proxy:
                    
                    try:
                        for x in rank[index]["pid"][:]:
                            if x in rewardpid:
                                rank[index]["pid"].remove(x)
                            else:
                                rewardpid.append(x)
                        
                        proxy.kfbossRank(index,rank[index], _no_result=True)
                        success = True
                    except:
                        success = False
                print("bossReward index:",index,success)
        
        print("bossReward done")

        self.bossScoreDayPrior=copy.deepcopy(self.bossScoreDay)
        self.bossScoreDayDeal = nt
        self.bossScoreDay = {}

        for sid,groupkey in self.type_sid__groupkey[4].items():
            xx=self.groupkeyData.get(groupkey,{})
            if not xx:
                continue
            bossid = xx.get("bossid",0)
            if not bossid:
                continue
            self.groupkeyData[groupkey]["bossid"]=0


        self.delsid(4)
        self.addsid(4)

        self.markDirty()


    # 攻城 活动结束发奖
    def sendRewardGongcheng(self):

        
        groupkeys=[]
        for sid,groupkey in self.type_sid__groupkey[5].items():
            if groupkey not in groupkeys:
                groupkeys.append(groupkey)
        
        self.gongchengCheckTime(groupkeys) #检查发奖 这里是为了保障endtime有值 因为特殊的清空功能所以独立
        self.gongchengCheckData(groupkeys) #初始化数据避免加载保持
        self.gongchengLoad(groupkeys) #加载数据

        while True:
            self.gongchengCheckTime(groupkeys) #检查发奖 因为特殊的清空功能所以独立
            self.gongchengCheckData(groupkeys) #初始化数据 因为上面是独立的

            st=time.time()
            self.gongchengCheckFight(groupkeys) #检查战斗
            et=time.time()
            if et-st>3:
                print("gongchengCheckFight.usingtime", "%s|%s" % (groupkeys,et-st,))
                Game.glog.log2File("gongchengCheckFight.usingtime", "%s|%s" % (groupkeys,et-st,))

            
            sleep(1)

    # kfboss 活动结束发奖
    def sendRewardKfboss(self):

        sleep(60)

        resAct = Game.res_mgr.res_activity.get(constant.ACTIVITY_KFBOSS)

        while True:

            nt = gtime.getDD()
            
            if not resAct.isOpenNoServerInfo() and nt!=self.bossScoreDayDeal and self.bossScoreDay:
                self.bossReward(nt)
            
            sleep(60)

    # 挖矿 每月发奖
    def sendRewardWakuangMonth(self):

        sleep(60)

        while True:



            mm = gtime.getMM()
            nt = gtime.getDD()
            if mm!=self.serverScoreMonthDeal and "01"==nt:
                
                print("reward sendRewardWakuangMonth")

                rank = sorted(list(self.serverScoreMonth.values()), key=lambda data:data["score"], reverse=True)
                for index in range(len(rank)):


                    print("monthReward index:",index,rank[index]["pid"])
                    success = False
                    from game.mgr.logicgame import LogicGame
                    proxy = get_proxy_by_addr(rank[index]["addr"], LogicGame._rpc_name_)
                    success=False
                    if proxy:
                        
                        try:
                            proxy.wakuangRankMonth(index,rank[index], _no_result=True)
                            success = True
                        except:
                            success = False
                    print("monthReward index:",index,success)
                print("monthReward done")
               
                self.serverScoreMonthDeal = mm
                self.serverScoreMonth = {}
                
                self.markDirty()
            
            sleep(60)



    def getScore(self,id):
        id=str(id)
        obj = self.score.get(id,{"score":0})
        return obj["score"]
    
    def addScore(self,id,addr,name,serverNo,v):
        id=str(id)
        addr=tuple(addr)
        
        sid=self.no2id(serverNo)
        
        obj = self.score.get(id,{"score":0})
        self.score[id] = {"id":int(id),"score":obj["score"]+v,"addr":addr,"name":name,"sid":sid}
        self.markDirty()
        
    def setScore(self,id,addr,name,serverNo,v):
        id=str(id)
        addr=tuple(addr)
        
        sid=self.no2id(serverNo)
        
        self.score[id] = {"id":int(id),"score":v,"addr":addr,"name":name,"sid":sid}
        self.markDirty()


    
    def getRankList(self,id):
        rank = sorted(list(self.score.values()), key=lambda data:data["score"], reverse=True)
        n = len(Game.res_mgr.res_diaoyurank)
        resprank = rank[:n]
        resp = {}
        resp["list"] = resprank
        
        id=str(id)
        obj = self.score.get(id,{"score":0})
        resp["score"] = obj["score"]
        resp["sid"] = obj.get("sid",0)

        r = 0
        for index in range(len(rank)):
            if rank[index]["id"]==int(id):
                r = index+1
                break
        resp["rank"] = r
        return resp



    def GetServerScoreDay(self,type,serverNo):
        sid=self.no2id(serverNo)
        groupkey=self.type_sid__groupkey[type][sid]

        s = []
        for kk,vv in self.type_sid__groupkey[type].items():
            if vv==groupkey:
                s.append(kk)
        
        s.sort()

        score=[]
        for ss in s:
            ScoreDay = self.serverScoreDay.get(ss,{"score":0})
            score.append(ScoreDay["score"])

        
        return {"score":score}

    def GetServerScoreMonth(self,type,serverNo):
        sid=self.no2id(serverNo)
        groupkey=self.type_sid__groupkey[type][sid]

        s = []
        for kk,vv in self.type_sid__groupkey[type].items():
            s.append(kk)


        score=[]
        for kk,vv in self.serverScoreMonth.items():
            one={}
            one["sid"]=kk
            one["score"]=vv["score"]
            score.append(one)

        
        return {"sid":sid,"score":score}


    def AddServerScore(self,type,serverNo,score,addr,pids):
        sid=self.no2id(serverNo)
        ScoreDay = self.serverScoreDay.get(sid,{"score":0,"pid":[]})
        ScoreMonth = self.serverScoreMonth.get(sid,{"score":0,"pid":[]})

        ScoreDay["score"]+=score
        ScoreMonth["score"]+=score

        ScoreDay["addr"]=addr
        ScoreMonth["addr"]=addr
        
        for pid in pids:
            if pid not in ScoreDay["pid"]:
                ScoreDay["pid"].append(pid)
            
            if pid not in ScoreMonth["pid"]:
                ScoreMonth["pid"].append(pid)
            
        ScoreDay["sid"]=sid
        ScoreMonth["sid"]=sid
        self.serverScoreDay[sid]=ScoreDay
        self.serverScoreMonth[sid]=ScoreMonth

        self.markDirty()

    def GetBossRank(self,serverNo):
        sid=self.no2id(serverNo)
        groupkey=self.type_sid__groupkey[4][sid]

        s = []
        for vv in self.bossScoreDay.values():
            if vv["groupkey"]==groupkey:
                s.append(vv)
        return {"score":s}

    def GetBossRankPrior(self,serverNo):
        sid=self.no2id(serverNo)
        groupkey=self.type_sid__groupkey[4][sid]

        s = []
        for vv in self.bossScoreDayPrior.values():
            if vv["groupkey"]==groupkey:
                s.append(vv)

        
        return {"score":s}


    #########################################################
    #########################################################
    #########################################################

    # def ranksort(self,a,b):
    #     if a["score"]==a["score"]:
    #         return 0
    #     elif a["score"]>a["score"]:
    #         return 1
    #     else:
    #         return -1

    # def shuffle(self,type):
        
    #     sid={}
    #     for id, obj in Game.res_mgr.res_kuafuGroup.items():
    #         if obj.type==type:
    #             # objsid = copy.deepcopy(obj.sid)
    #             # while objsid
    #             #     if len(objsid) >= obj.num
    #             #         onegr = random.sample(objsid,obj.num)
    #             #         del objsid by onegr
    #             #     elif
    #             #         onegr = []
    #             #         onegr.extend(objsid)
    #             #         sid = []



    #             random.shuffle(obj.sid)
    #             n=0
    #             nn=0
    #             for xid in obj.sid:
                    
    #                 n+=1
    #                 if n>obj.num:
    #                     nn+=1
    #                     n=1
                    
    #                 sid[xid]=str(id)+'-'+str(nn)
                
    #     return sid


    #######################################
    #######################################
    #######################################
    #######################################

    def kfbossSetAtk(self,serverNo,Atk):
        sid=self.no2id(serverNo)
        
        groupkey=self.getGroupkeyByTypeSid(4,sid)
        if not groupkey:
            return
        
        sdata = self.groupkeyData.get(groupkey,{})
        self.groupkeyData[groupkey]=sdata
        
        bossAtkNo=sdata.get("bossAtkNo",{})
        sdata["bossAtkNo"]=bossAtkNo
        bossAtkNo[serverNo]=Atk

        n=len(bossAtkNo)
        tot=0
        for k,v in bossAtkNo.items():
            tot+=v
        
        # pac=tot/n
        pac=tot
            
        
        sdata["bossAtk"]=pac

        # print('bossAtk',sdata["bossAtk"],bossAtkNo)

        self.markDirty()

    def kfbossUnBox(self,id,boxid,serverNo):
        sid=self.no2id(serverNo)
        resp={}
        resp["err"]=0
        groupkey = self.typeid2groupkey.get(str(4)+"-"+str(id),"")
        if groupkey not in self.group:
            resp["err"]=errcode.EC_KFBOSS_NOTIN
            return resp
        
        v = self.groupkeyData[groupkey]["box"].get(boxid,None)
        if v==None:
            resp["err"]=errcode.EC_KFBOSS_BOXNOFOUND
            return resp
        
        if v==id:
            self.groupkeyData[groupkey]["box"][boxid]=""


        gmsg={}
        
        addboxid={}
        addboxid[boxid]=""
        gmsg["addbox"]=addboxid
        gmsg["type"]=4

        self.groupMsg(groupkey,"gmsg",gmsg)
        
        self.markDirty()

        return resp

    def kfbossBox(self,id,boxid,serverNo):
        sid=self.no2id(serverNo)
        resp={}
        resp["err"]=0
        groupkey = self.typeid2groupkey.get(str(4)+"-"+str(id),"")
        if groupkey not in self.group:
            resp["err"]=errcode.EC_KFBOSS_NOTIN
            return resp
        
        v = self.groupkeyData[groupkey]["box"].get(boxid,None)
        if v==None:
            resp["err"]=errcode.EC_KFBOSS_BOXNOFOUND
            return resp
        
        if v=="":
            self.groupkeyData[groupkey]["box"][boxid]=id
        
        resp["fightplayer"]=v
        
        self.markDirty()

        gmsg={}
        
        addboxid={}
        addboxid[boxid]=id
        gmsg["addbox"]=addboxid
        gmsg["type"]=4

        self.groupMsg(groupkey,"gmsg",gmsg)


        return resp

    def kfbossBoxOpen(self,id,boxid,serverNo):
        sid=self.no2id(serverNo)
        resp={}
        resp["err"]=0
        groupkey = self.typeid2groupkey.get(str(4)+"-"+str(id),"")
        if groupkey not in self.group:
            resp["err"]=errcode.EC_KFBOSS_NOTIN
            return resp
        
        v = self.groupkeyData[groupkey]["box"].get(boxid,None)
        if v==None:
            resp["err"]=errcode.EC_KFBOSS_BOXNOFOUND
            return resp
        
        self.groupkeyData[groupkey]["box"].pop(boxid,None)
        
        bossid = self.groupkeyData[groupkey].get("bossid",0)
        if not bossid:
            resp["err"]==errcode.EC_KFBOSS_BOSSNOBORN
            return resp
        resp["bossid"]=bossid
        
        self.markDirty()

        gmsg={}
        
        gmsg["delbox"]=boxid
        gmsg["type"]=4

        self.groupMsg(groupkey,"gmsg",gmsg)

        return resp
    
    def kfbossAgain(self,serverNo):
        print('kfbossAgain')
        self.bossReward("")
        self.markDirty()

        
    def kfboss(self,id,ghid,ghname,addr,serverNo,fightData):
        addr=tuple(addr)
        ghid=str(ghid)
        sid=self.no2id(serverNo)

        resp={}
        resp["err"]=0
        groupkey = self.typeid2groupkey.get(str(4)+"-"+str(id),"")
        if groupkey not in self.group:
            resp["err"]=errcode.EC_KFBOSS_NOTIN
            return resp
        
        curHp = self.groupkeyData[groupkey].get("bosshp",1)
        maxHp = self.groupkeyData[groupkey].get("kfbossMaxHp",1)
        shield = self.groupkeyData[groupkey].get("kfbossShield",0)
        shieldMax = self.groupkeyData[groupkey].get("kfbossShieldMax",1)
        bossid = self.groupkeyData[groupkey].get("bossid",0)
        if not bossid:
            resp["err"]==errcode.EC_KFBOSS_BOSSNOBORN
            return resp

        kfbossLastP = self.groupkeyData[groupkey].get("kfbossLastP",100) # 上一次生成盾的百分点

        if 0==curHp:
            resp["err"]=errcode.EC_KFBOSS_BOSSDEAD
            return resp

        resKfBoss = Game.res_mgr.res_kfBoss.get(bossid)
        if not resKfBoss:
            resp["err"]=errcode.EC_NORES
            return resp
        barrRes = Game.res_mgr.res_barrier.get(resKfBoss.fbId)
        if not barrRes:
            resp["err"]=errcode.EC_NORES
            return resp
        
        fightobj = Game.fight_mgr.createFight(constant.FIGHT_TYPE_240)
        rs = fightobj.init_by_barrId_by_fightData(fightData, barrRes.id)
        if not rs:
            resp["err"]=errcode.EC_INIT_BARR_FAIL
            return resp

        #修改最大护盾
        # fightobj.fix_monster_maxshield({resKfBoss.mstId:shieldMax})

        #修改最大血量
        # fightobj.fix_monster_maxhp({resKfBoss.mstId:maxHp})

        #设置盾
        # fightobj.fix_monster_shield({resKfBoss.mstId:shield})
        
        #设置血
        # fightobj.fix_monster_hp({resKfBoss.mstId:curHp})

        Game.glog.log2File("kfboos_setget", "set %s|%s|%s" % (groupkey,curHp,shield,))

        dfix={resKfBoss.mstId:{constant.ATTR_HP:curHp,constant.ATTR_SHIELD:shield,constant.ATTR_MAXHP:maxHp,constant.ATTR_MAXSHIELD:shieldMax,}}
        fightobj.FixMonsterAttr(dfix)
        #1回合后秒人
        fightobj.FixMonsterAttrWithRound({resKfBoss.mstId:{"round":1,"atk":random.randint(7999999999999, 9999999999999),"add_targetNum":10}})
        #战斗
        fightLog = fightobj.doFight(logMstId=resKfBoss.mstId)
        # Game.glog.log2File("testkfbossFight", "%s" % ujson.dumps(fightLog))

        #获取当前血
        
        # nowHp = fightLog.get("mstData", {}).get(constant.ATTR_HP, 0)   
        # if nowHp<0:
        #     nowHp=0
        
        # nowShield = 0

        # 获取当前盾
        # nowShield = fightLog.get("mstData", {}).get(constant.ATTR_SHIELD, 0)   

        ma=fightobj.GetMonsterAttr(resKfBoss.mstId)
        
        nowHp=ma[constant.ATTR_HP]
        if nowHp<0:
            nowHp=0

        nowShield=ma[constant.ATTR_SHIELD]
        if nowShield<0:
            nowShield=0

        if nowHp == 0:
            Game.glog.log2File("kfboosBekilled", "%s|%s|%s|%s|%s|%s" % (bossid, barrRes.id, fightData, fightLog, dfix, ma))
        Game.glog.log2File("kfboos_setget", "get %s|%s|%s" % (groupkey,nowHp,nowShield,))

        hurt = curHp - nowHp
        hurt+=shield-nowShield

        p = int(nowHp*100/maxHp)

        addbox={}
        breakShield=False
        if shield and nowShield==0:
            
            breakShield=True

            boxnum=random.randrange(resKfBoss.min,resKfBoss.max+1)
            
            for i in range(boxnum):
                boxid=str(self.groupkeyData[groupkey]["boxid"])

                addbox[boxid]=""

                self.groupkeyData[groupkey]["boxid"]+=1

        if nowHp==0:

            boxnum=random.randrange(resKfBoss.min,resKfBoss.max+1)
            
            for i in range(boxnum):
                boxid=str(self.groupkeyData[groupkey]["boxid"])

                addbox[boxid]=""

                self.groupkeyData[groupkey]["boxid"]+=1

        #盾产生的百分点 0=没产生
        gmsgShield=0

        if nowHp:
            for i in range(len(resKfBoss.makeShield),0,-1):
                if resKfBoss.makeShield[i-1] < kfbossLastP: #找到下一个盾点
                    
                    if nowShield==0 and p<=resKfBoss.makeShield[i-1]: #如果没盾状态下并且当前血量小于的等于盾点 => 生成盾
                        
                        self.groupkeyData[groupkey]["kfbossLastP"]=resKfBoss.makeShield[0] #初始化盾点

                        for ii in range(len(resKfBoss.makeShield)):
                            if resKfBoss.makeShield[ii]<p:
                                self.groupkeyData[groupkey]["kfbossLastP"]=resKfBoss.makeShield[ii+1]
                                

                        nowShield=shieldMax #满盾
                        gmsgShield = self.groupkeyData[groupkey]["kfbossLastP"] #设置盾点

                        break

                
        


        ghdata=self.bossScoreDay.get(ghid,{"gid":ghid,"groupkey":groupkey,"score":0,"addr":addr,"pid":[],"ghname":ghname,"sid":sid})
        ghdata["score"]+=hurt
        if id not in ghdata["pid"]:
            ghdata["pid"].append(id)

        self.bossScoreDay[ghid]=ghdata

        #####################################################
        
        self.groupkeyData[groupkey]["bosshp"]=nowHp
        self.groupkeyData[groupkey]["kfbossShield"]=nowShield
        self.groupkeyData[groupkey]["box"].update(addbox)

        self.markDirty()

        #####################################################

        gmsg={}
        
        if addbox:
            gmsg["addbox"]=addbox
        
        gmsg["bosshp"]=self.groupkeyData[groupkey]["bosshp"]
        gmsg["kfbossShield"]=self.groupkeyData[groupkey]["kfbossShield"]
        gmsg["shieldP"]=gmsgShield
        
        gmsg["type"]=4

        # print('-----------',gmsg)
        self.groupMsg(groupkey,"gmsg",gmsg)

        #####################################################
 
        resp["hurt"]=hurt
        resp["fightLog"]=fightLog
        resp["bossid"]=bossid
        resp["breakShield"]=breakShield
        resp["kill"]=nowHp==0

        return resp
    
    #######################################
    #######################################
    #######################################
    #######################################

    def gongchengFightData(self,id,fdata,pdata,ghid,ghname,ghcolor,ghlv=1,serverNo=""):
        

        resp={}
        resp["err"]=0

        groupkey = self.typeid2groupkey.get(str(5)+"-"+str(id),"")
        if not groupkey:
            resp["err"]=errcode.EC_GETD_GROUPKEYFAIL
            return resp

        gongchengPlayer = self.gongchengPlayerGet(id)
        if not gongchengPlayer:
            gongchengPlayer = {"myteam":{}}

        self.gongchengPlayer[id]=gongchengPlayer

        self.gongchengPlayer[id]["id"]=id
        self.gongchengPlayer[id]["fdata"]=fdata
        self.gongchengPlayer[id]["pdata"]=pdata
        self.gongchengPlayer[id]["ghid"]=ghid
        self.gongchengPlayer[id]["ghname"]=ghname
        self.gongchengPlayer[id]["ghcolor"]=ghcolor
        self.gongchengPlayer[id]["ghlv"]=ghlv
        self.gongchengPlayer[id]["serverNo"]=serverNo
        
        self.gongchengPlayer[id]["data"]=self.group[groupkey][id]["data"]
        self.gongchengPlayer[id]["addr"]=self.group[groupkey][id]["addr"]
        self.gongchengPlayer[id]["name"]=self.group[groupkey][id]["name"]

        self.gongchengPlayer[id].setdefault("gongchengTaskData", {})

        Game.store.save(TN_G_GONGCHENGPLAYER, self.cPickleIDDATAencode(self.gongchengPlayer[id]))

        # TODO 刷新team数据

        return resp
        

    def rsyncRpcGongchengTaskData(self, pid, taskList, serverNo):
        old = self.gongchengPlayer.setdefault(pid, {"myteam":{}}).get("gongchengTaskData", {})

        gongchengTaskData = {}
        for taskId in taskList:
            gongchengTaskData[taskId] = old.get(taskId, {})

        self.gongchengPlayer[pid]["gongchengTaskData"] = gongchengTaskData

        # TASK_TYPE_80 = 80  # 80=攻城战击败xx个对手
        # self.num = data.get("winNum", 0)

        # TASK_TYPE_81 = 81  # 81=攻城战中与玩家对战x次
        # self.num = data.get("fightWithPlayerNum", 0)

        # TASK_TYPE_85 = 85  # 85=攻城战同时占领N个X型城市
        # data.get("occupationCity", {})
        data = self.getByServerNo(5, serverNo)
        cityData = data.get("common", {}).get("city", {})
        occupationCity = {}
        for cid, oneData in cityData.items():
            occupationCity[cid] = oneData.get("ghid")

        resp = copy.deepcopy(gongchengTaskData)
        resp["occupationCity"] = occupationCity
        return resp


# (team, map[队伍id]json)
# 	队伍宠物(pets, [json])
# 		宠物id(id, int)
# 		宠物进化等级(evolveLv, int)
# 		宠物hp(hp, int)
# 		宠物最大血量(maxhp, int)
# 		宠物战力(fa, int)
# 	锁定状态(lock, int)0不锁定 。 锁定状态下不可调动（如果死亡可以复活。本场出战过就锁定）
# 	归属玩家id(pid, int)
# 	归属工会id(ghid, int)
# 	归属颜色(ghcolor, int)
# 	归属名(ghname, string)
    def gongchengTeamDataMake(self,id,data,team,name,addr):
        xx={
            "pets":[],
            "lock":0,
            "pid":id,
            "ghid":data["ghid"],
            "ghname":data["ghname"],
            "ghcolor":data["ghcolor"],
            "ghlv":data["ghlv"],
            "serverNo":"",

            "addr":addr,
            "name":name,
        }
        pserverNo=data.get("serverNo",None)
        if pserverNo:
            xx["serverNo"]=pserverNo

        hp=data["fdata"]["attr"]["hp"]

        petIndex = 0

        iRATE = 1000.0 * 1000
        for t in team:
            
            for p in data["pdata"]:
                if t==p["id"]:
                    petIndex+=1
                    one={}

                    one["id"] = p["id"]
                    one["name"] = p["name"]
                    one["mainSkill"] = p["mainSkill"]
                    one["skills"] = p["skills"]

                    one["status"] = petIndex
                    one["evolveLv"] = p["evolveLv"]
                    one["talentLv"] = p["talentLv"]
                    one["talentSkillLv"] = p["talentSkillLv"]

                    # one["hp"] = hp
                    resEvolveLv = Game.res_mgr.res_idlv_petevolve.get((p["id"], p["evolveLv"]))
                    one["maxhp"] = int(hp  * resEvolveLv.attrValue * resEvolveLv.hpRate/iRATE)
                    one["fa"] = 0 # TODO

                    xx["pets"].append(one)
                    break

        return xx
    
    def gongchengTeamCreate(self,id,team):
        resp={}
        resp["err"]=0

        team=team[:6]
        team=list(set(team))

        groupkey = self.typeid2groupkey.get(str(5)+"-"+str(id),"")
        if not groupkey:
            resp["err"]=errcode.EC_GETD_GROUPKEYFAIL
            return resp



        pdata=self.gongchengPlayerGet(id)
        if not pdata:
            resp["err"]=errcode.EC_GONGCHENG_NOTFOUNDDATA
            return resp

        for x in team:

            found=False

            for v in pdata["pdata"]:
                if x==v["id"]:
                    found=True
                    break

            
            # 检查宠物id是否已经编队
            for teampets in pdata["myteam"].values():
                if x in teampets:
                    resp["err"]=errcode.EC_GONGCHENG_PEIHASTEAM
                    return resp

            if not found:
                resp["err"]=errcode.EC_GONGCHENG_NOTFOUNDPET
                return resp

        teamid=str(self.gongchengteamid)
        self.gongchengteamid+=1

        
        
        self.gongchengPlayer[id]["myteam"][teamid]=team


        name=self.group[groupkey][id]["name"]
        addr=self.group[groupkey][id]["addr"]


        self.markDirty()

        teamdata=self.gongchengTeamDataMake(id,pdata,team,name,addr)
        teamdata["id"]=teamid

        resp["team"]={teamid:teamdata}
        resp["teamid"]=teamid


        Game.store.save(TN_G_GONGCHENGPLAYER, self.cPickleIDDATAencode(self.gongchengPlayer[id]))


        Game.store.save(TN_G_GONGCHENGTEAM, teamdata)

        return resp




    def gongchengTeamDestroy(self,id,teams,rebron):
        resp={}
        resp["err"]=0

        groupkey = self.typeid2groupkey.get(str(5)+"-"+str(id),"")
        if not groupkey:
            resp["err"]=errcode.EC_GETD_GROUPKEYFAIL
            return resp

        if id not in self.gongchengPlayer:
            resp["err"]=errcode.EC_GONGCHENG_NOTFOUNDPLAYER
            return resp

        for team in teams:
            if team not in self.gongchengPlayer[id]["myteam"]:
                resp["err"]=errcode.EC_GONGCHENG_NOTFOUNDTEAM
                return resp

            teamdata=self.gongchengTeam.get(team,None)
            if (not rebron) and teamdata and teamdata["lock"]:
                resp["err"]=errcode.EC_GONGCHENG_PETISLOCK
                return resp

        gmsg={
            "changecity":{},
            "delteam":[],
            "type":5,
        }

        for team in teams:
                
            self.gongchengPlayer[id]["myteam"].pop(team,None)
            
            hasOnCity=self.gongchengTeam.pop(team,None)
            
            if hasOnCity:
                
                for cityid,cityobj in self.groupkeyData[groupkey]["city"].items():
                    found=False
                    for teamid in cityobj["atk"]:
                        if teamid==team:
                            cityobj["atk"].remove(teamid)
                            found=True
                            break
                    if found:
                        break
                    found=False
                    for teamid in cityobj["def"]:
                        if teamid==team:
                            cityobj["def"].remove(teamid)
                            found=True
                            break
                    if found:
                        break

                gmsg["changecity"][cityid]=self.groupkeyData[groupkey]["city"][cityid]
                gmsg["delteam"].append(team)

                
            

        self.groupMsg(groupkey,"gmsg",gmsg)

        # TODO 删除 gongchengTeam 可不删除

        Game.store.save(TN_G_GONGCHENGPLAYER, self.cPickleIDDATAencode(self.gongchengPlayer[id]))


        self.markDirty()

        return resp


    def gongchengSend(self,id,team,city,atk):
        resp={}
        resp["err"]=0

        groupkey = self.typeid2groupkey.get(str(5)+"-"+str(id),"")
        if not groupkey:
            resp["err"]=errcode.EC_GETD_GROUPKEYFAIL
            return resp

        if id not in self.gongchengPlayer:
            resp["err"]=errcode.EC_GONGCHENG_NOTFOUNDPLAYER
            return resp

        if team not in self.gongchengPlayer[id]["myteam"]:
            resp["err"]=errcode.EC_GONGCHENG_NOTFOUNDTEAM
            return resp
        
        if city not in self.groupkeyData[groupkey]["city"]:
            resp["err"]=errcode.EC_GONGCHENG_NOTFOUNDCITY
            return resp
        
        pdata=self.gongchengPlayerGet(id)
        if not pdata:
            resp["err"]=errcode.EC_GONGCHENG_NOTFOUNDDATA
            return resp


        for cityid,cityobj in self.groupkeyData[groupkey]["city"].items():
            
            for teamid in cityobj["atk"]:
                if teamid==team:
                    resp["err"]=errcode.EC_GONGCHENG_TEAMISSEND
                    return resp

            for teamid in cityobj["def"]:
                if teamid==team:
                    resp["err"]=errcode.EC_GONGCHENG_TEAMISSEND
                    return resp
        
        cityobj=self.groupkeyData[groupkey]["city"][city]
        res=Game.res_mgr.res_gongcheng[int(city)]

        
        if res.isDeclarewar and atk:
            if not cityobj["guildonly"]:
                # cityobj["guildonly"]=pdata["ghid"]
                resp["err"]=errcode.EC_GONGCHENG_NEEDWAR
                return resp
            else:
                if cityobj["guildonly"]!=pdata["ghid"]:
                    resp["err"]=errcode.EC_GONGCHENG_BIGCITYLOCK
                    return resp
        
        if atk:
            cityobj["guildonlytime"]=0

        if pdata["ghid"] not in cityobj["atkghid"]:
            cityobj["atkghid"].append(pdata["ghid"])

        self.groupkeyData[groupkey]["guildScore"][str(pdata["ghid"])]=self.groupkeyData[groupkey]["guildScore"].get(str(pdata["ghid"]),{"name":pdata["ghname"],"addr":pdata["addr"],"score":0,"pids":[]})
        if id not in self.groupkeyData[groupkey]["guildScore"][str(pdata["ghid"])]["pids"]:
            self.groupkeyData[groupkey]["guildScore"][str(pdata["ghid"])]["pids"].append(id)

        nt = gtime.getYYYYMMDD()
        if 0==len(self.gongchengAct):
            self.gongchengAct.append({"d":nt,"s":{}})
        
        if self.gongchengAct[-1]["d"]!=nt:
            self.gongchengAct.append({"d":nt,"s":{}})
        
        gongchengActiveDay = Game.res_mgr.res_common.get("gongchengActiveDay")
        self.gongchengAct=self.gongchengAct[-gongchengActiveDay.i:]


        pserverNo=pdata.get("serverNo",None)
        if pserverNo:
            ss=self.gongchengAct[-1]["s"].get(pserverNo,{"ghid":{},"score":0})
            self.gongchengAct[-1]["s"][pserverNo]=ss
            ghscore=ss["ghid"].get(str(pdata["ghid"]),{"score":0,"name":pdata["ghname"]})
            ss["ghid"][str(pdata["ghid"])]=ghscore

                
        if atk:
            self.groupkeyData[groupkey]["city"][city]["atk"].append(team)
        else:
            self.groupkeyData[groupkey]["city"][city]["def"].append(team)

        name=self.group[groupkey][id]["name"]
        addr=self.group[groupkey][id]["addr"]

        self.gongchengTeam[team]=self.gongchengTeamDataMake(id,pdata,pdata["myteam"][team],name,addr)

        gmsg={}

        gmsg["changecity"]={city:self.groupkeyData[groupkey]["city"][city]}
        gmsg["changeteam"]={team:self.gongchengTeam[team]}

        
        gmsg["type"]=5

        self.groupMsg(groupkey,"gmsg",gmsg)

        self.markDirty()

        return resp

    def gongchengGetAllTeam(self,id): 
        resp={}
        resp["err"]=0

        groupkey = self.typeid2groupkey.get(str(5)+"-"+str(id),"")
        if not groupkey:
            resp["err"]=errcode.EC_GETD_GROUPKEYFAIL
            return resp

        if id not in self.gongchengPlayer:
            resp["err"]=errcode.EC_GONGCHENG_NOTFOUNDPLAYER
            return resp

        pdata=self.gongchengPlayerGet(id)
        if not pdata:
            resp["err"]=errcode.EC_GONGCHENG_NOTFOUNDDATA
            return resp
        
        name=self.group[groupkey][id]["name"]
        addr=self.group[groupkey][id]["addr"]

        myteam={}
        for teamid,team in self.gongchengPlayer[id]["myteam"].items():
            if teamid in self.gongchengTeam:
                teamdata=self.gongchengTeam[teamid]
            else:
                teamdata=self.gongchengTeamDataMake(id,pdata,team,name,addr)
            
            myteam[teamid]=teamdata

        resp["team"]=self.gongchengTeam
        resp["myteam"]=myteam
        return resp
        

    def gongchengGetPlayer(self,id,players): 
        resp={}
        resp["err"]=0

        groupkey = self.typeid2groupkey.get(str(5)+"-"+str(id),"")
        if not groupkey:
            resp["err"]=errcode.EC_GETD_GROUPKEYFAIL
            return resp

        if id not in self.gongchengPlayer:
            resp["err"]=errcode.EC_GONGCHENG_NOTFOUNDPLAYER
            return resp


        
        data={}
        for id in players:
            pdata=self.gongchengPlayerGet(id)
            if not pdata:
                continue

            data[id]=pdata["data"]


        resp["data"]=data
        return resp

    #放弃城市
    # 在一整场进行中的大战斗不能弃城，飘字提示：正在战斗中无法弃城！
    def gongchengGiveup(self,id,cityid): 
        resp={}
        resp["err"]=0

        groupkey = self.typeid2groupkey.get(str(5)+"-"+str(id),"")
        if not groupkey:
            resp["err"]=errcode.EC_GETD_GROUPKEYFAIL
            return resp

        if id not in self.gongchengPlayer:
            resp["err"]=errcode.EC_GONGCHENG_NOTFOUNDPLAYER
            return resp
        
        city=str(cityid)

        if city not in self.groupkeyData[groupkey]["city"]:
            resp["err"]=errcode.EC_GONGCHENG_NOTFOUNDCITY
            return resp

        cityobj=self.groupkeyData[groupkey]["city"][city]

        if cityobj["lastAtkId"]:
            resp["err"]=errcode.EC_GONGCHENG_NOGIVEUP
            return resp

        nowtime=time.time()
        gongchengWarReadyTime = Game.res_mgr.res_common.get("gongchengWarReadyTime")
        gongchengDeclarewarTime = Game.res_mgr.res_common.get("gongchengDeclarewarTime")

        if cityobj["guildonly"]:
            guildonlytime=cityobj.get("guildonlytime",0)

            if nowtime-guildonlytime<gongchengWarReadyTime.i+gongchengDeclarewarTime.i:
                resp["err"]=errcode.EC_GONGCHENG_GIVEERRBYWAR
                return resp


        


        cityobj["ghid"]=0
        cityobj["ghcolor"]=0
        cityobj["ghname"]=""
        cityobj["serverNo"]=""


        

        cityobj["npcTime"]=nowtime
        cityobj["overStartTime"]=0
        cityobj["warStartTime"]=0
        cityobj["lastAtkId"]=""
        cityobj["pathTime1"]={"road":1,"time":0,"atkid":"","blue":""}
        cityobj["pathTime2"]={"road":2,"time":0,"atkid":"","blue":""}
        cityobj["pathTime3"]={"road":3,"time":0,"atkid":"","blue":""}
        # cityobj["atktime"]=nowtime
        cityobj["kill"]={}
        cityobj["guildonly"]=0
        cityobj["guildonlytime"]=0
        cityobj["guildonlyname"]=""
        
        gmsg={
            "changeteam":{},
            "delteam":[],
        }



        cityobj["npc"]=[]
        for v in Game.res_mgr.res_gongcheng[int(cityid)].fbIds:
            if "npc"+str(v) not in cityobj["npc"]:
                cityobj["npc"].append("npc"+str(v))


        for team in cityobj["def"]:
            t=self.gongchengTeam.get(team,None)
            if not t:
                continue
            
            for pet in t["pets"]:
                pet.pop("hp",None)
            t["lock"]=0
            gmsg["changeteam"][team]=t
                
            if self.gongchengTeam.pop(team,None):
                gmsg["delteam"].append(team)

        for team in cityobj["atk"]:         
            t=self.gongchengTeam.get(team,None)
            if not t:
                continue
            
            for pet in t["pets"]:
                pet.pop("hp",None)
            t["lock"]=0
            gmsg["changeteam"][team]=t

            if self.gongchengTeam.pop(team,None):
                gmsg["delteam"].append(team)

        cityobj["atk"]=[]
        cityobj["def"]=[]


        

        gmsg["changecity"]={city:cityobj}


        
        gmsg["type"]=5

        self.groupMsg(groupkey,"gmsg",gmsg)


        

        
        return resp


    def gongchengLogList(self,id,city): 

        resp={}
        resp["err"]=0

        groupkey = self.typeid2groupkey.get(str(5)+"-"+str(id),"")
        if not groupkey:
            resp["err"]=errcode.EC_GETD_GROUPKEYFAIL
            return resp

        if id not in self.gongchengPlayer:
            resp["err"]=errcode.EC_GONGCHENG_NOTFOUNDPLAYER
            return resp

        city=str(city)

        if city not in self.groupkeyData[groupkey]["city"]:
            resp["err"]=errcode.EC_GONGCHENG_NOTFOUNDCITY
            return resp

        resp["data"]=[]


        logids=list(self.fightlog.keys())
        logids.sort()
        for logid in logids:
            obj=self.fightlog[logid]
            if city==obj["cityid"] and obj["gk"]==groupkey:
                xx=copy.deepcopy(self.fightlog[logid])
                xx["fightlog"]=logid
                resp["data"].append(xx)
                
        
        
        return resp

    def gongchengLogData(self,id,fightlog): 
        resp={}
        resp["err"]=0

        groupkey = self.typeid2groupkey.get(str(5)+"-"+str(id),"")
        if not groupkey:
            resp["err"]=errcode.EC_GETD_GROUPKEYFAIL
            return resp

        if id not in self.gongchengPlayer:
            resp["err"]=errcode.EC_GONGCHENG_NOTFOUNDPLAYER
            return resp

        if fightlog not in self.fightlog:
            resp["err"]=errcode.EC_GONGCHENG_NOFOUNDLOG
            return resp
        
        resp["fightlog"]=self.fightlog[fightlog]["fightlog"]

        return resp


    def gongchengRankPerson(self,id,pre): 
        resp={}
        resp["err"]=0

        groupkey = self.typeid2groupkey.get(str(5)+"-"+str(id),"")
        if not groupkey:
            resp["err"]=errcode.EC_GETD_GROUPKEYFAIL
            return resp

        if id not in self.gongchengPlayer:
            resp["err"]=errcode.EC_GONGCHENG_NOTFOUNDPLAYER
            return resp

        
        resp["data"]=self.groupkeyData[groupkey]["personScore"]

        return resp

    def gongchengRankGuild(self,id,pre): 
        resp={}
        resp["err"]=0

        groupkey = self.typeid2groupkey.get(str(5)+"-"+str(id),"")
        if not groupkey:
            resp["err"]=errcode.EC_GETD_GROUPKEYFAIL
            return resp

        if id not in self.gongchengPlayer:
            resp["err"]=errcode.EC_GONGCHENG_NOTFOUNDPLAYER
            return resp

        
        resp["data"]=self.groupkeyData[groupkey]["guildScore"]

        return resp


    def gongchengTag(self,id,city): 
        resp={}
        resp["err"]=0

        groupkey = self.typeid2groupkey.get(str(5)+"-"+str(id),"")
        if not groupkey:
            resp["err"]=errcode.EC_GETD_GROUPKEYFAIL
            return resp

        if id not in self.gongchengPlayer:
            resp["err"]=errcode.EC_GONGCHENG_NOTFOUNDPLAYER
            return resp

        city=str(city)

        if city not in self.groupkeyData[groupkey]["city"]:
            resp["err"]=errcode.EC_GONGCHENG_NOTFOUNDCITY
            return resp

        
        cityobj=self.groupkeyData[groupkey]["city"][city]

        ghid=self.gongchengPlayer[id]["ghid"]

        if ghid not in cityobj["tagghid"]:
            
            cityobj["tagghid"].append(ghid)
            gmsg={}

            gmsg["changecity"]={city:self.groupkeyData[groupkey]["city"][city]}
            
            gmsg["type"]=5

            self.groupMsg(groupkey,"gmsg",gmsg)
        
        return resp



    def gongchengCleanTag(self,id,city): 
        resp={}
        resp["err"]=0

        groupkey = self.typeid2groupkey.get(str(5)+"-"+str(id),"")
        if not groupkey:
            resp["err"]=errcode.EC_GETD_GROUPKEYFAIL
            return resp

        if id not in self.gongchengPlayer:
            resp["err"]=errcode.EC_GONGCHENG_NOTFOUNDPLAYER
            return resp

        city=str(city)

        if city not in self.groupkeyData[groupkey]["city"]:
            resp["err"]=errcode.EC_GONGCHENG_NOTFOUNDCITY
            return resp

        
        cityobj=self.groupkeyData[groupkey]["city"][city]

        ghid=self.gongchengPlayer[id]["ghid"]

        if ghid in cityobj["tagghid"]:
            
            cityobj["tagghid"].remove(ghid)
            gmsg={}

            gmsg["changecity"]={city:self.groupkeyData[groupkey]["city"][city]}
            
            gmsg["type"]=5

            self.groupMsg(groupkey,"gmsg",gmsg)
        
        return resp




    def gongchengFightIdGet(self,cityobj,road):

        nowtime=time.time()
        gongchengFight = Game.res_mgr.res_common.get("gongchengFight")
        
        passatk=[]
        passblue=[]
        for v in range(3):
            x=v+1
            if x==road:
                continue
            roadid="pathTime"+str(x)

            if cityobj[roadid]["time"]+gongchengFight.i<=nowtime:
                continue
            
            if cityobj[roadid]["atkid"]:
                passatk.append(cityobj[roadid]["atkid"])
            if cityobj[roadid]["blue"]:
                passblue.append(cityobj[roadid]["blue"])


        atkid=""
        delatk=[]
        for team in cityobj["atk"]:
            t=self.gongchengTeam.get(team,None)
            if not t:
                delatk.append(team)
                continue

            if team in passatk:
                continue
            hp=0
            for pet in t["pets"]:
                hp+=pet.get("hp",1)
            if hp:
                atkid=team
                break

        for k in delatk:
            cityobj["atk"].remove(k)

        blue=""
        deldef=[]
        for team in cityobj["def"]:
            t=self.gongchengTeam.get(team,None)
            if not t:
                deldef.append(team)
                continue
            if team in passblue:
                continue
            hp=0
            for pet in t["pets"]:
                hp+=pet.get("hp",1)
            if hp:
                blue=team
                break
        
        for k in deldef:
            cityobj["def"].remove(k)

        if not blue:
            for team in cityobj["npc"]:
                if team in passblue:
                    continue
                blue=team
                break

        return atkid,blue

    def gongchengCityFight(self,cityid,cityobj,atkid,blue,gmsg,groupkey):
        
        win=0
        name1=""
        name2=""
        
        pveRounds = Game.res_mgr.res_common.get("pveRounds")
        pvpRounds = Game.res_mgr.res_common.get("pvpRounds")

        pid=self.gongchengTeam[atkid]["pid"]
        fightData=self.gongchengPlayer[pid]["fdata"]
        name1=self.gongchengPlayer[pid]["name"]
        fightData["petList"]=self.gongchengTeam[atkid]["pets"]

        #攻城任务
        gongchengTaskData = self.gongchengPlayer[pid].get("gongchengTaskData", {})

        if blue.startswith("npc"):

            barrRes = Game.res_mgr.res_barrier.get(blue[3:])
            if not barrRes:
                print("gongchengCityFight not found res_barrier", "%s" % (blue[3:],))
                Game.glog.log2File("gongchengCityFight not found res_barrier", "%s" % (blue[3:],))
                for pet in self.gongchengTeam[atkid]["pets"]:
                    pet["hp"]=0
                self.gongchengTeam[atkid]["lock"]=1
                gmsg["changeteam"][atkid]=self.gongchengTeam[atkid]
                return False,{},"",""
            
            fightobj = Game.fight_mgr.createFight(constant.FIGHT_TYPE_242)
            fightobj.SetRounds(pveRounds.i)
            
            rs=None
            try:
                rs = fightobj.init_by_barrId_by_fightData(fightData, barrRes.id)
            except:
                rs=None

            if not rs:
                print("gongchengCityFight init_by_barrId_by_fightData fail", "%s|%s|%s" % (blue[3:],fightData, barrRes.id,))
                Game.glog.log2File("gongchengCityFight init_by_barrId_by_fightData fail", "%s|%s|%s" % (blue[3:],fightData, barrRes.id,))
                for pet in self.gongchengTeam[atkid]["pets"]:
                    pet["hp"]=0
                self.gongchengTeam[atkid]["lock"]=1
                gmsg["changeteam"][atkid]=self.gongchengTeam[atkid]
                return False,{},"",""


            try:
                fightLog = fightobj.doFight()
            except:
                print("gongchengCityFight doFight fail", "%s|%s|%s" % (blue[3:],fightData, barrRes.id,))
                Game.glog.log2File("gongchengCityFight doFight fail", "%s|%s|%s" % (blue[3:],fightData, barrRes.id,))
                fightLog={}
            
            rhp=fightobj.GetRedPetHp()
 
 
            win = fightLog.get("result",{}).get("win", 0)

            if win:
                #打赢了记录任务次数  # 80=攻城战击败xx个对手
                for taskId in gongchengTaskData.keys():
                    gongchengTaskData[taskId]["winNum"] = gongchengTaskData[taskId].setdefault("winNum", 0) + 1
                
                self.groupkeyData[groupkey]["personScore"][str(pid)]=self.groupkeyData[groupkey]["personScore"].get(str(pid),{"name":self.gongchengPlayer[pid]["name"],"addr":self.gongchengPlayer[pid]["addr"],"score":0,"ghname":self.gongchengPlayer[pid]["ghname"],"pid":pid})
                self.groupkeyData[groupkey]["personScore"][str(pid)]["score"]+=1

                self.groupkeyData[groupkey]["guildScore"][str(self.gongchengPlayer[pid]["ghid"])]=self.groupkeyData[groupkey]["guildScore"].get(str(self.gongchengPlayer[pid]["ghid"]),{"name":"","addr":self.gongchengPlayer[pid]["addr"],"score":0,"pids":[pid]})
                self.groupkeyData[groupkey]["guildScore"][str(self.gongchengPlayer[pid]["ghid"])]["score"]+=1 #fix
                
                nt = gtime.getYYYYMMDD()
                if 0==len(self.gongchengAct):
                    self.gongchengAct.append({"d":nt,"s":{}})
                
                if self.gongchengAct[-1]["d"]!=nt:
                    self.gongchengAct.append({"d":nt,"s":{}})
                
                gongchengActiveDay = Game.res_mgr.res_common.get("gongchengActiveDay")
                self.gongchengAct=self.gongchengAct[-gongchengActiveDay.i:]

                pserverNo=self.gongchengPlayer[pid].get("serverNo",None)
                if pserverNo:
                    ss=self.gongchengAct[-1]["s"].get(pserverNo,{"ghid":{},"score":0})
                    self.gongchengAct[-1]["s"][pserverNo]=ss
                    ss["score"]+=1

                    ghscore=ss["ghid"].get(str(self.gongchengPlayer[pid]["ghid"]),{"score":0,"name":self.gongchengPlayer[pid]["ghname"]})
                    ss["ghid"][str(self.gongchengPlayer[pid]["ghid"])]=ghscore
                    ss["ghid"][str(self.gongchengPlayer[pid]["ghid"])]["score"]+=1



                cityobj["npc"].pop(0)
                
                pid=self.gongchengTeam[atkid]["pid"]
                cityobj["kill"][str(pid)]=cityobj["kill"].get(str(pid),{"name":self.gongchengTeam[atkid]["name"],"score":0,"atk":1,"addr":tuple(self.gongchengTeam[atkid]["addr"])})
                cityobj["kill"][str(pid)]["score"]+=1
                gmsg["changecity"][cityid]=cityobj

                for pet in self.gongchengTeam[atkid]["pets"]:
                    sethp=rhp.get(pet["id"],None)
                    if sethp==None:
                        print('eeeeeee setrhp',rhp,fightData["petList"])
                    else:
                        pet["hp"]=sethp
                
            else:
                for pet in self.gongchengTeam[atkid]["pets"]:
                    pet["hp"]=0

                
                

        else:
            pid=self.gongchengTeam[blue]["pid"]
            fightData2=self.gongchengPlayer[pid]["fdata"]
            name2=self.gongchengPlayer[pid]["name"]
            fightData2["petList"]=self.gongchengTeam[blue]["pets"]
            
            fightobj = Game.fight_mgr.createFight(constant.FIGHT_TYPE_243)
            fightobj.SetRounds(pvpRounds.i)
            
            rs=None
            try:
                rs = fightobj.init_players_by_data(fightData, fightData2)
            except:
                rs=None

            if not rs:
                print("gongchengCityFight init_players_by_data fail", "%s%s" % (fightData,fightData2))
                Game.glog.log2File("gongchengCityFight init_players_by_data fail", "%s%s" % (fightData,fightData2))
                for pet in self.gongchengTeam[atkid]["pets"]:
                    pet["hp"]=0
                self.gongchengTeam[atkid]["lock"]=1
                gmsg["changeteam"][atkid]=self.gongchengTeam[atkid]
                return False,{},"",""

            try:
                fightLog = fightobj.doFight()
            except:
                print("gongchengCityFight doFight fail", "%s%s" % (fightData,fightData2))
                Game.glog.log2File("gongchengCityFight doFight fail", "%s%s" % (fightData,fightData2))
                fightLog={}

            rhp=fightobj.GetRedPetHp()
            bhp=fightobj.GetBluePetHp()


            win = fightLog.get("result",{}).get("win", 0)

            # 记录任务次数  # 81=攻城战中与玩家对战x次
            for taskId in gongchengTaskData.keys():
                gongchengTaskData[taskId]["fightWithPlayerNum"] = gongchengTaskData[taskId].setdefault("fightWithPlayerNum", 0) + 1
            
            if win:
                # 打赢了记录任务次数  # 80=攻城战击败xx个对手
                for taskId in gongchengTaskData.keys():
                    gongchengTaskData[taskId]["winNum"] = gongchengTaskData[taskId].setdefault("winNum", 0) + 1
                
                self.groupkeyData[groupkey]["personScore"][str(pid)]=self.groupkeyData[groupkey]["personScore"].get(str(pid),{"name":self.gongchengPlayer[pid]["name"],"addr":self.gongchengPlayer[pid]["addr"],"score":0,"ghname":self.gongchengPlayer[pid]["ghname"],"pid":pid})
                self.groupkeyData[groupkey]["personScore"][str(pid)]["score"]+=1

                self.groupkeyData[groupkey]["guildScore"][str(self.gongchengPlayer[pid]["ghid"])]=self.groupkeyData[groupkey]["guildScore"].get(str(self.gongchengPlayer[pid]["ghid"]),{"name":"","addr":self.gongchengPlayer[pid]["addr"],"score":0,"pids":[pid]})
                self.groupkeyData[groupkey]["guildScore"][str(self.gongchengPlayer[pid]["ghid"])]["score"]+=1 # fix


                nt = gtime.getYYYYMMDD()
                if 0==len(self.gongchengAct):
                    self.gongchengAct.append({"d":nt,"s":{}})
                
                if self.gongchengAct[-1]["d"]!=nt:
                    self.gongchengAct.append({"d":nt,"s":{}})
                
                gongchengActiveDay = Game.res_mgr.res_common.get("gongchengActiveDay")
                self.gongchengAct=self.gongchengAct[-gongchengActiveDay.i:]

                pserverNo=self.gongchengPlayer[pid].get("serverNo",None)
                if pserverNo:
                    ss=self.gongchengAct[-1]["s"].get(pserverNo,{"ghid":{},"score":0})
                    self.gongchengAct[-1]["s"][pserverNo]=ss
                    ss["score"]+=1
                    ghscore=ss["ghid"].get(str(self.gongchengPlayer[pid]["ghid"]),{"score":0,"name":self.gongchengPlayer[pid]["ghname"]})
                    ss["ghid"][str(self.gongchengPlayer[pid]["ghid"])]=ghscore
                    ss["ghid"][str(self.gongchengPlayer[pid]["ghid"])]["score"]+=1

                for pet in self.gongchengTeam[atkid]["pets"]:
                    sethp=rhp.get(pet["id"],None)
                    if sethp==None:
                        print('eeeeeee setrhp',rhp,fightData["petList"])
                    else:
                        pet["hp"]=sethp
                        # print('===========win',pet["hp"],pet["maxhp"])

                for pet in self.gongchengTeam[blue]["pets"]:
                    pet["hp"]=0

                pid=self.gongchengTeam[atkid]["pid"]
                cityobj["kill"][str(pid)]=cityobj["kill"].get(str(pid),{"name":self.gongchengTeam[atkid]["name"],"score":0,"atk":1,"addr":tuple(self.gongchengTeam[atkid]["addr"])})
                cityobj["kill"][str(pid)]["score"]+=1

            else:

                pid=self.gongchengTeam[blue]["pid"]

                self.groupkeyData[groupkey]["personScore"][str(pid)]=self.groupkeyData[groupkey]["personScore"].get(str(pid),{"name":self.gongchengPlayer[pid]["name"],"addr":self.gongchengPlayer[pid]["addr"],"score":0,"ghname":self.gongchengPlayer[pid]["ghname"],"pid":pid})
                self.groupkeyData[groupkey]["personScore"][str(pid)]["score"]+=1

                nt = gtime.getYYYYMMDD()
                if 0==len(self.gongchengAct):
                    self.gongchengAct.append({"d":nt,"s":{}})
                
                if self.gongchengAct[-1]["d"]!=nt:
                    self.gongchengAct.append({"d":nt,"s":{}})
                
                gongchengActiveDay = Game.res_mgr.res_common.get("gongchengActiveDay")
                self.gongchengAct=self.gongchengAct[-gongchengActiveDay.i:]

                pserverNo=self.gongchengPlayer[pid].get("serverNo",None)
                if pserverNo:
                    ss=self.gongchengAct[-1]["s"].get(pserverNo,{"ghid":{},"score":0})
                    self.gongchengAct[-1]["s"][pserverNo]=ss
                    ss["score"]+=1
                    ghscore=ss["ghid"].get(str(self.gongchengPlayer[pid]["ghid"]),{"score":0,"name":self.gongchengPlayer[pid]["ghname"]})
                    ss["ghid"][str(self.gongchengPlayer[pid]["ghid"])]=ghscore
                    ss["ghid"][str(self.gongchengPlayer[pid]["ghid"])]["score"]+=1
                    
                for pet in self.gongchengTeam[blue]["pets"]:
                    sethp=bhp.get(pet["id"],None)
                    if sethp==None:
                        print('eeeeeee setbhp',rhp,fightData2["petList"])
                    else:
                        pet["hp"]=sethp
                        # print('===========fai',pet["hp"],pet["maxhp"])

                for pet in self.gongchengTeam[atkid]["pets"]:
                    pet["hp"]=0
                
                
                cityobj["kill"][str(pid)]=cityobj["kill"].get(str(pid),{"name":self.gongchengTeam[blue]["name"],"score":0,"atk":0,"addr":tuple(self.gongchengTeam[blue]["addr"])})
                cityobj["kill"][str(pid)]["score"]+=1

            


            self.gongchengTeam[blue]["lock"]=1
            gmsg["changeteam"][blue]=self.gongchengTeam[blue]
            gmsg["changecity"][cityid]=cityobj
            

        self.gongchengTeam[atkid]["lock"]=1
        gmsg["changeteam"][atkid]=self.gongchengTeam[atkid]
        
        self.markDirty()

        return win,fightLog,name1,name2

    def gongchengCheckFight(self,groupkeys):
        


        gongchengFight = Game.res_mgr.res_common.get("gongchengFight")
        gongchengNpcTime = Game.res_mgr.res_common.get("gongchengNpcTime")
        gongchengGameOver = Game.res_mgr.res_common.get("gongchengGameOver")
        gongchengCityNumLimit = Game.res_mgr.res_common.get("gongchengCityNumLimit")

        nowtime=time.time()
        for groupkey in groupkeys:
            gmsg={}

            gmsg["changecity"]={}
            gmsg["changeteam"]={}
            gmsg["fightCity"]={}
            gmsg["Count2AtkWin"]=[]
            gmsg["Count2DefWin"]=[]
            gmsg["AtkWin"]=[]
            gmsg["DefWin"]=[]
            gmsg["delteam"]=[]
            
            gmsg["type"]=5

            for cityid,cityobj in self.groupkeyData[groupkey]["city"].items():

                res=Game.res_mgr.res_gongcheng[int(cityid)]

                if cityobj["npcTime"]+gongchengNpcTime.i<=nowtime :
                    cityobj["npcTime"]=nowtime
                    
                    if len(cityobj["npc"])<len(Game.res_mgr.res_gongcheng[int(cityid)].fbIds):
                        for v in Game.res_mgr.res_gongcheng[int(cityid)].fbIds:
                            if "npc"+str(v) not in cityobj["npc"]:
                                cityobj["npc"].append("npc"+str(v))
                                gmsg["changecity"][cityid]=self.groupkeyData[groupkey]["city"][cityid]
                                break

                lastAtkId=""
                atkid,blue=self.gongchengFightIdGet(cityobj,1)
                if cityobj["pathTime1"]["time"]+gongchengFight.i<=nowtime and atkid and blue:
                    cityobj["pathTime1"]["time"]=nowtime
                    cityobj["pathTime1"]["atkid"]=atkid
                    cityobj["pathTime1"]["blue"]=blue
                    cityobj["lastAtkId"]=atkid

                    win,fightlog,name1,name2=self.gongchengCityFight(cityid,cityobj,atkid,blue,gmsg,groupkey)
                    gmsg["fightCity"][cityid]=gmsg["fightCity"].get(cityid,[])
                    self.fightlog[self.fightlogid]={"fightlog":fightlog,"name1":name1,"name2":name2,"win":win,"cityid":cityid,"gk":groupkey}
                    gmsg["fightCity"][cityid].append({"road":1,"atkid":atkid,"blue":blue,"win":win})
                    self.fightlogid+=1

                atkid,blue=self.gongchengFightIdGet(cityobj,2) 
                if cityobj["pathTime2"]["time"]+gongchengFight.i<=nowtime and atkid and blue:
                    cityobj["pathTime2"]["time"]=nowtime
                    cityobj["pathTime2"]["atkid"]=atkid
                    cityobj["pathTime2"]["blue"]=blue
                    cityobj["lastAtkId"]=atkid

                    win,fightlog,name1,name2=self.gongchengCityFight(cityid,cityobj,atkid,blue,gmsg,groupkey)
                    gmsg["fightCity"][cityid]=gmsg["fightCity"].get(cityid,[])
                    self.fightlog[self.fightlogid]={"fightlog":fightlog,"name1":name1,"name2":name2,"win":win,"cityid":cityid,"gk":groupkey}
                    gmsg["fightCity"][cityid].append({"road":2,"atkid":atkid,"blue":blue,"win":win})
                    self.fightlogid+=1

                loglimit=10
                logkey=list(self.fightlog.keys())
                logkey.sort(reverse=True)
                citylognum={}
                delx=[]
                for x in logkey:
                    citylognum[self.fightlog[x]["cityid"]]=citylognum.get(self.fightlog[x]["cityid"],0)
                    if citylognum[self.fightlog[x]["cityid"]]==10:
                        delx.append(x)
                    else:
                        citylognum[self.fightlog[x]["cityid"]]+=1
                    
                for x in delx:
                    self.fightlog.pop(x)

                atkid,blue=self.gongchengFightIdGet(cityobj,3)
                if cityobj["pathTime3"]["time"]+gongchengFight.i<=nowtime and atkid and blue:
                    cityobj["pathTime3"]["time"]=nowtime
                    cityobj["pathTime3"]["atkid"]=atkid
                    cityobj["pathTime3"]["blue"]=blue
                    cityobj["lastAtkId"]=atkid

                    win,fightlog,name1,name2=self.gongchengCityFight(cityid,cityobj,atkid,blue,gmsg,groupkey)
                    gmsg["fightCity"][cityid]=gmsg["fightCity"].get(cityid,[])
                    self.fightlog[self.fightlogid]={"fightlog":fightlog,"name1":name1,"name2":name2,"win":win,"cityid":cityid,"gk":groupkey}
                    gmsg["fightCity"][cityid].append({"road":3,"atkid":atkid,"blue":blue,"win":win})
                    self.fightlogid+=1

                if cityid in gmsg["fightCity"]:

                    cityobj["Count2DefWinTime"]=0
                    cityobj["Count2AtkWinTime"]=0

                    cityobj["overStartTime"]=0
                    if not cityobj["warStartTime"]:
                        cityobj["warStartTime"]=nowtime

                elif cityobj["warStartTime"]:

                    hp=0
                    delatk=[]
                    for team in cityobj["atk"]:        
                        t=self.gongchengTeam.get(team,None)
                        if not t:
                            delatk.append(team)
                            continue               
                        for pet in t["pets"]:
                            hp+=pet.get("hp",1)

                    for k in delatk:
                        cityobj["atk"].remove(k)

                    if not hp:
                        if not cityobj["overStartTime"]:
                            cityobj["overStartTime"]=nowtime
                            cityobj["Count2DefWinTime"]=nowtime
                            gmsg["Count2DefWin"].append(cityid)
                        if cityobj["overStartTime"]+gongchengGameOver.i<=nowtime:
                            
                            # TODO 守城成功
                            self.gongchengClearFightlog(cityid)

                            for pidstr,obj in cityobj["kill"].items():
                                addr=tuple(obj["addr"])
                                from game.mgr.logicgame import LogicGame
                                proxy = get_proxy_by_addr(addr, LogicGame._rpc_name_)
                                xxtype=constant.MAIL_ID_GONGCHENG_ATK_FAIL
                                if 0==obj["atk"]:
                                    xxtype+=1
                                success=False
                                st=time.time()
                                if proxy:
                                    try:
                                        proxy.gongchengCityReward(int(cityid),int(pidstr),xxtype,obj["score"], _no_result=True)
                                        success = True
                                    except:
                                        success = False

                                et=time.time()
                                if not success:
                                    print("gongchengCityReward time uing", "%s|%s" % (et-st,addr,))
                                    Game.glog.log2File("gongchengCityReward time uing", "%s|%s" % (et-st,addr,))
                                
                                print("city def success:",int(cityid),int(pidstr),xxtype,obj["score"],success)

                            if cityobj["guildonly"]:
                                self.gongchengAddHistory(groupkey,3,cityobj["guildonly"],int(cityid),cityobj["ghname"])

                            gmsg["DefWin"].append({"cityid":cityid,"DEFghid":cityobj["ghid"],"DEFghname":cityobj["ghname"],"ATKlistid":cityobj["atkghid"]})

                            # "npcTime":nowtime,
                            # "overStartTime":0,
                            # "warStartTime":0
                            # "lastAtkId":""
                            # "pathTime1":{"road":1,"time":0,"atkid":"","blue":""}, #上次战斗时间
                            # "pathTime2":{"road":2,"time":0,"atkid":"","blue":""}, #上次战斗时间
                            # "pathTime3":{"road":3,"time":0,"atkid":"","blue":""}, #上次战斗时间

                            # "npc":npc,
                            # "def":[],
                            # "atk":[],
                            # "ghid":0,
                            # "ghcolor":0,
                            # "ghname":"",
                            # "tagghid":[],
                            # "time":0,
                            # "atktime":0,

                            if res.level==3:
                                cityobj["npc"]=[]
                                for v in Game.res_mgr.res_gongcheng[int(cityid)].fbIds:
                                    if "npc"+str(v) not in cityobj["npc"]:
                                        cityobj["npc"].append("npc"+str(v))

                            cityobj["overStartTime"]=0
                            cityobj["warStartTime"]=0
                            cityobj["lastAtkId"]=""
                            cityobj["pathTime1"]={"road":1,"time":0,"atkid":"","blue":""}
                            cityobj["pathTime2"]={"road":2,"time":0,"atkid":"","blue":""}
                            cityobj["pathTime3"]={"road":3,"time":0,"atkid":"","blue":""}
                            cityobj["atktime"]=nowtime
                            cityobj["kill"]={}
                            cityobj["guildonly"]=0
                            cityobj["guildonlytime"]=0
                            cityobj["guildonlyname"]=""
                            cityobj["atkghid"]=[]

                            deldef=[]
                            for team in cityobj["def"]:      
                                t=self.gongchengTeam.get(team,None)
                                if not t:
                                    deldef.append(team)
                                    continue                 
                                for pet in t["pets"]:
                                    pet.pop("hp",None)
                                t["lock"]=0
                                gmsg["changeteam"][team]=t

                            for k in deldef:
                                cityobj["def"].remove(k)

                            for team in cityobj["atk"]:       
                                t=self.gongchengTeam.get(team,None)
                                if not t:
                                    continue
                                for pet in t["pets"]:
                                    pet.pop("hp",None)
                                t["lock"]=0
                                gmsg["changeteam"][team]=t

                                if self.gongchengTeam.pop(team,None):
                                    gmsg["delteam"].append(team)
                            
                            cityobj["atk"]=[]

                            gmsg["changecity"][cityid]=cityobj

                    elif 0==len(cityobj["npc"]):
                        hp=0
                        deldef=[]
                        for team in cityobj["def"]:   
                            t=self.gongchengTeam.get(team,None)
                            if not t:
                                deldef.append(team)
                                continue                    
                            for pet in t["pets"]:
                                hp+=pet.get("hp",1)
                        
                        for k in deldef:
                            cityobj["def"].remove(k)
                            
                        if not hp:
                            if not cityobj["overStartTime"]:
                                cityobj["overStartTime"]=nowtime
                                cityobj["Count2AtkWinTime"]=nowtime
                                gmsg["Count2AtkWin"].append(cityid)
                            if cityobj["overStartTime"]+gongchengGameOver.i<=nowtime:
                                
                                # TODO 攻城成功
                                self.gongchengClearFightlog(cityid)

                                for pidstr,obj in cityobj["kill"].items():
                                    addr=tuple(obj["addr"])
                                    from game.mgr.logicgame import LogicGame
                                    proxy = get_proxy_by_addr(addr, LogicGame._rpc_name_)
                                    xxtype=constant.MAIL_ID_GONGCHENG_ATK_SUCC
                                    if 0==obj["atk"]:
                                        xxtype+=1

                                    success=False
                                    st=time.time()
                                    if proxy:
                                        try:
                                            proxy.gongchengCityReward(int(cityid),int(pidstr),xxtype,obj["score"], _no_result=True)
                                            success = True
                                        except:
                                            success = False

                                    et=time.time()
                                    
                                    if not success:
                                        print("gongchengCityReward time uing", "%s|%s" % (et-st,addr,))
                                        Game.glog.log2File("gongchengCityReward time uing", "%s|%s" % (et-st,addr,))
                                    print("city atk success:",int(cityid),int(pidstr),xxtype,obj["score"],success)


                                
                                lastAtkId=cityobj["lastAtkId"]
                                if lastAtkId not in self.gongchengTeam:


                                    cityobj["npcTime"]=nowtime
                                    cityobj["overStartTime"]=0
                                    cityobj["warStartTime"]=0
                                    cityobj["lastAtkId"]=""
                                    cityobj["pathTime1"]={"road":1,"time":0,"atkid":"","blue":""}
                                    cityobj["pathTime2"]={"road":2,"time":0,"atkid":"","blue":""}
                                    cityobj["pathTime3"]={"road":3,"time":0,"atkid":"","blue":""}
                                    cityobj["atktime"]=nowtime
                                    cityobj["kill"]={}
                                    cityobj["guildonly"]=0
                                    cityobj["guildonlytime"]=0
                                    cityobj["guildonlyname"]=""
                                    cityobj["atkghid"]=[]
                                    
                                    cityobj["ghid"]=0
                                    cityobj["ghcolor"]=0
                                    cityobj["ghname"]=""
                                    cityobj["serverNo"]=""

                                    cityobj["npc"]=[]
                                    for v in Game.res_mgr.res_gongcheng[int(cityid)].fbIds:
                                        if "npc"+str(v) not in cityobj["npc"]:
                                            cityobj["npc"].append("npc"+str(v))


                                    
                                    for team in cityobj["def"]:     
                                        t=self.gongchengTeam.get(team,None)
                                        if not t:
                                            continue
                                        
                                        for pet in t["pets"]:
                                            pet.pop("hp",None)
                                        t["lock"]=0
                                        gmsg["changeteam"][team]=t

                                        if self.gongchengTeam.pop(team,None):
                                            gmsg["delteam"].append(team)

                                    for team in cityobj["atk"]:                    
                                        t=self.gongchengTeam.get(team,None)
                                        if not t:
                                            continue
                                        for pet in t["pets"]:
                                            pet.pop("hp",None)
                                        t["lock"]=0
                                        gmsg["changeteam"][team]=t

                                        if self.gongchengTeam.pop(team,None):
                                            gmsg["delteam"].append(team)
                                    
                                    cityobj["atk"]=[]
                                    cityobj["def"]=[]

                                    gmsg["changecity"][cityid]=cityobj

                                else:
                                    ghid=self.gongchengTeam[lastAtkId]["ghid"]
                                    ghcolor=self.gongchengTeam[lastAtkId]["ghcolor"]
                                    ghname=self.gongchengTeam[lastAtkId]["ghname"]
                                    ghlv=self.gongchengTeam[lastAtkId].get("ghlv",15)
                                    pserverNo=self.gongchengTeam[lastAtkId].get("serverNo",None)

                                    neighbor=False
                                    citycount=0
                                    citycountS=0
                                    citycountM=0
                                    citycountL=0
                                    for cityid1,cityobj1 in self.groupkeyData[groupkey]["city"].items():
                                        if cityobj1["ghid"]==ghid:
                                            citycount+=1
                                            res=Game.res_mgr.res_gongcheng[int(cityid1)]

                                            if res.level==1:
                                                citycountS+=1
                                            elif res.level==2:
                                                citycountM+=1
                                            elif res.level==3:
                                                citycountL+=1

                                            for v in res.near:
                                                if str(v) == cityid:
                                                    neighbor=True
                                                    break

                                    
                                    # "npcTime":nowtime,
                                    # "overStartTime":0,
                                    # "warStartTime":0
                                    # "lastAtkId":""
                                    # "pathTime1":{"road":1,"time":0,"atkid":"","blue":""}, #上次战斗时间
                                    # "pathTime2":{"road":2,"time":0,"atkid":"","blue":""}, #上次战斗时间
                                    # "pathTime3":{"road":3,"time":0,"atkid":"","blue":""}, #上次战斗时间

                                    # "npc":npc,
                                    # "def":[],
                                    # "atk":[],
                                    # "ghid":0,
                                    # "ghcolor":0,
                                    # "ghname":"",
                                    # "tagghid":[],
                                    # "time":0,
                                    # "atktime":0,
                                    res=Game.res_mgr.res_gongcheng[int(cityid)]
                                    if citycount==0 and res.level==3:
                                        citycount=999999

                                    ghlvlimit=0
                                    CityXNum=0
                                    res=Game.res_mgr.res_gongcheng[int(cityid)]
                                    resG=Game.res_mgr.res_guildlv[ghlv]
                                    if res.level==1:
                                        CityXNum=citycountS
                                        ghlvlimit=resG.CityS
                                    elif res.level==2:
                                        CityXNum=citycountM
                                        ghlvlimit=resG.CityM
                                    elif res.level==3:
                                        CityXNum=citycountL
                                        ghlvlimit=resG.CityL


                                    if ((not citycount) or neighbor) and citycount<gongchengCityNumLimit.i and CityXNum<ghlvlimit:

                                        self.gongchengAddHistory(groupkey,0,cityobj["ghid"],int(cityid),ghname)
                                        self.gongchengAddHistory(groupkey,1,ghid,int(cityid),cityobj["ghname"])

                                        gmsg["AtkWin"].append({"cityid":cityid,"ATKghid":ghid,"ATKghname":ghname,"DEFghid":cityobj["ghid"],"DEFghname":cityobj["ghname"],"ATKlistid":cityobj["atkghid"]})

                                        cityobj["ghid"]=ghid
                                        cityobj["ghcolor"]=ghcolor
                                        cityobj["ghname"]=ghname
                                        cityobj["time"]=nowtime
                                        
                                        if pserverNo:
                                            cityobj["serverNo"]=pserverNo

                                        

                                    else:

                                        self.gongchengAddHistory(groupkey,2,ghid,int(cityid),"")
                                        
                                        gmsg["DefWin"].append({"cityid":cityid,"DEFghid":cityobj["ghid"],"DEFghname":cityobj["ghname"],"ATKlistid":cityobj["atkghid"]})

                                    

                                    cityobj["npcTime"]=nowtime
                                    cityobj["overStartTime"]=0
                                    cityobj["warStartTime"]=0
                                    cityobj["lastAtkId"]=""
                                    cityobj["pathTime1"]={"road":1,"time":0,"atkid":"","blue":""}
                                    cityobj["pathTime2"]={"road":2,"time":0,"atkid":"","blue":""}
                                    cityobj["pathTime3"]={"road":3,"time":0,"atkid":"","blue":""}
                                    cityobj["atktime"]=nowtime
                                    cityobj["kill"]={}
                                    cityobj["guildonly"]=0
                                    cityobj["guildonlytime"]=0
                                    cityobj["guildonlyname"]=""
                                    cityobj["atkghid"]=[]
                                    

                                    cityobj["npc"]=[]
                                    for v in Game.res_mgr.res_gongcheng[int(cityid)].fbIds:
                                        if "npc"+str(v) not in cityobj["npc"]:
                                            cityobj["npc"].append("npc"+str(v))


                                    
                                    for team in cityobj["def"]:     
                                        t=self.gongchengTeam.get(team,None)
                                        if not t:
                                            continue
                                        
                                        for pet in t["pets"]:
                                            pet.pop("hp",None)
                                        t["lock"]=0
                                        gmsg["changeteam"][team]=t

                                        if self.gongchengTeam.pop(team,None):
                                            gmsg["delteam"].append(team)

                                    for team in cityobj["atk"]:                    
                                        t=self.gongchengTeam.get(team,None)
                                        if not t:
                                            continue
                                        for pet in t["pets"]:
                                            pet.pop("hp",None)
                                        t["lock"]=0
                                        gmsg["changeteam"][team]=t

                                        if self.gongchengTeam.pop(team,None):
                                            gmsg["delteam"].append(team)
                                    
                                    cityobj["atk"]=[]
                                    cityobj["def"]=[]

                                    gmsg["changecity"][cityid]=cityobj
                                




    
            if gmsg["changecity"] or gmsg["changeteam"] or gmsg["fightCity"] or gmsg["Count2AtkWin"] or gmsg["Count2DefWin"] or gmsg["AtkWin"] or gmsg["DefWin"] or gmsg["delteam"]:
                self.groupMsg(groupkey,"gmsg",gmsg)
                    
            if gmsg["AtkWin"]:
                for x in gmsg["AtkWin"]:
                    
                    res=Game.res_mgr.res_gongcheng[int(x["cityid"])]
                    info = res.gbinfo % (x["ATKghname"],)
                    infostr=self.makeContent(5,0,info)

                    data = {}
                    data["rid"] = 0
                    data["content"] = infostr
                    data["type"] = 5

                    self.groupMsg(groupkey,"msg",data)
                    
        self.markDirty()
                

                
    def gongchengClearFightlog(self,cityid):
        removelogid=[]
        for logid,log in self.fightlog.items():
            if log["cityid"]==cityid:
                removelogid.append(logid)
        
        for k in removelogid:
            self.fightlog.pop(k)
        
    def gongchengNew(self):

        groupkeys=[]
        for sid,groupkey in self.type_sid__groupkey[5].items():
            if groupkey not in groupkeys:
                groupkeys.append(groupkey)
        

        self.serverScoreGongchengTime=1
        self.gongchengCheckTime(groupkeys)
    
    def gongchengCheckTime(self,groupkeys):

        gongchengZhouqi = Game.res_mgr.res_common.get("gongchengZhouqi")

        nowtime=time.time()
        nexttime=gtime.zero_day_time()+24*60*60*gongchengZhouqi.i
        
        if self.serverScoreGongchengTime==0:
            
            self.serverScoreGongchengTime=nexttime
            self.markDirty()
            return

        
        if nowtime<self.serverScoreGongchengTime:
            return

        self.serverScoreGongchengTime=nexttime

        print('reward sendRewardGongcheng')

        from game.mgr.logicgame import LogicGame

        for groupkey in groupkeys:
            l=list(self.groupkeyData[groupkey]["personScore"].values())
            l.sort(key=lambda x:x['score'],reverse=True)
            
            print("reward personScore:")
            
            sendpids=[]

            for x in range(len(l)):
                
                if l[x]["pid"] in sendpids:
                    continue

                sendpids.append(l[x]["pid"])

                proxy = get_proxy_by_addr(l[x]["addr"], LogicGame._rpc_name_)
                success=False
                if proxy:

                    st = time.time()
                    try:
                        proxy.gongchengPersonScore(x,l[x]["pid"], _no_result=True)
                        success = True
                    except Exception as e:
                        success = False
                        et = time.time()
                        print("proxy.gongchengPersonScore.fail", "%s|%s|%s|%s|%s" % (
                            x, l[x]["pid"], et - st, l[x]["addr"], e))
                        Game.glog.log2File("proxy.gongchengPersonScore.fail",
                                           "%s|%s|%s|%s|%s" % (x,l[x]["pid"], et - st, l[x]["addr"], e))
                print("reward index:",x,success,l[x]["pid"])

            l=list(self.groupkeyData[groupkey]["guildScore"].values())
            l.sort(key=lambda x:x['score'],reverse=True)
            
            print("reward guildScore:")

            sendpids=[]

            for x in range(len(l)):
                
                l[x]["pids"]=list(set(l[x]["pids"]))

                for sendpid in sendpids:
                    if sendpid in l[x]["pids"]:
                        l[x]["pids"].remove(sendpid)

                
                sendpids.extend(l[x]["pids"])

                proxy = get_proxy_by_addr(l[x]["addr"], LogicGame._rpc_name_)
                success=False
                if proxy:

                    st = time.time()
                    try:
                        proxy.gongchengGuildScore(x,l[x]["pids"], _no_result=True)
                        success = True
                    except Exception as e:
                        success = False
                        et = time.time()
                        print("proxy.gongchengGuildScore.fail", "%s|%s|%s|%s|%s" % (
                            x, l[x]["pids"], et - st, l[x]["addr"], e))
                        Game.glog.log2File("proxy.gongchengGuildScore.fail",
                                           "%s|%s|%s|%s|%s" % (x,l[x]["pids"], et - st, l[x]["addr"], e))

                print("reward index:",x,success,l[x]["pids"])


        for groupkey in groupkeys:
            self.groupkeyData.pop(groupkey,None)


        self.gongchengPlayer={}
        self.gongchengTeam={}
        self.fightlog={}
        self.fightlogid=0
        self.gongchengteamid=0

        self.delsid(5)
        self.addsid(5)
        

        self.markDirty()

    def gongchengCheckData(self,groupkeys):

        for groupkey in groupkeys:

            nowtime=time.time()
            data=self.groupkeyData.get(groupkey,{})
            self.groupkeyData[groupkey]=data

            
            
            if data:
                
                endtime=data.get("endtime",0)

                if endtime+60<nowtime:
                    
                    data["endtime"]=self.serverScoreGongchengTime

                    Game.glog.log2File("gongchengCheckData.fix.endtime",
                    "%s|%s|%s|%s" % (endtime,nowtime,self.serverScoreGongchengTime,groupkey,))
                    
                    

            if data:
                continue
            
            data["endtime"]=self.serverScoreGongchengTime #结束时间
            # print('==========',data["endtime"])
            
            data["personScore"]={} #key=str(playerid) val={name,addr,score,ghname}
            data["guildScore"]={} #key=str(guildid) val={name,addr,score,pids}
            data["history"]=[] #obj={"x":类型 "t":时间,"g":我方公会id,"c":城市id,"n":对方公会名}
            # 0）	当自己公会被人占领时，				提示：	XXX占领了公会驻地【地点名】					
            # 1）	当自己公会占领城市时，				提示：	我方公会成功占领了【对方公会名】拥有的【城市名】					
            # 2）	当自己公会取得胜利没占领				提示：	占领失败：因未有与【城市名】相邻的据点					
            # 3）	当自己公会宣战后进攻城市没取得胜利				提示：	我方公会在与【对方公会名】争夺【城市名】中失利了					


            data["city"]={}
            for k,v in Game.res_mgr.res_gongcheng.items():
                npc=[]
                for fbId in v.fbIds:
                    npc.append("npc"+str(fbId))
                
                data["city"][str(k)]={
                    "npcTime":nowtime,
                    "overStartTime":0,
                    "warStartTime":0,
                    "lastAtkId":"",
                    "pathTime1":{"road":1,"time":0,"atkid":"","blue":""}, #上次战斗时间
                    "pathTime2":{"road":2,"time":0,"atkid":"","blue":""}, #上次战斗时间
                    "pathTime3":{"road":3,"time":0,"atkid":"","blue":""}, #上次战斗时间

                    "npc":npc,
                    "def":[],
                    "atk":[],
                    "ghid":0,
                    "ghcolor":0,
                    "ghname":"",
                    "tagghid":[],
                    "time":0,
                    "atktime":0,
                    "kill":{},
                    "guildonly":0,
                    "guildonlytime":0,
                    "guildonlyname":"",
                    "atkghid":[],

                    
                }


    def gongchengAddHistory(self,groupkey,x,g,c,n):
        msg={"x":x,"t":time.time(),"g":g,"c":c,"n":n}
        self.groupkeyData[groupkey]["history"].append(msg)
        if len(self.groupkeyData[groupkey]["history"])>100:
            self.groupkeyData[groupkey]["history"].pop(0)

    def gongchengHistory(self,id,ghid):

        resp={}
        resp["err"]=0

        groupkey = self.typeid2groupkey.get(str(5)+"-"+str(id),"")
        if not groupkey:
            resp["err"]=errcode.EC_GETD_GROUPKEYFAIL
            return resp

        if id not in self.gongchengPlayer:
            resp["err"]=errcode.EC_GONGCHENG_NOTFOUNDPLAYER
            return resp


        resp["data"]=[]


        for x in self.groupkeyData[groupkey]["history"]:
            if x["g"]==ghid:
                 resp["data"].append(x)
                
        
        
        return resp

    def gongchengTeamGet(self,teamid):
        x=self.gongchengTeam.get(teamid,None)
        if not x:
            
            x=Game.store.load(TN_G_GONGCHENGTEAM, teamid)
            if x:
                self.gongchengTeam[teamid]=x
        return x

    def gongchengPlayerGet(self,id):
        x=self.gongchengPlayer.get(id,{})
        if not x:
            x=Game.store.load(TN_G_GONGCHENGPLAYER, id)
            if x:
                x=self.cPickleIDDATAdecode(x)
                self.gongchengPlayer[id]=x
        return x

    def gongchengLoad(self,groupkeys):
        for groupkey in groupkeys:

            # TODO 关闭改代码 这里是为了兼容旧数据
            self.groupkeyData[groupkey]["history"]=self.groupkeyData[groupkey].get("history",[])

            for cityid,cityobj in self.groupkeyData[groupkey]["city"].items():

                removlist=[]
                for teamid in cityobj["atk"]:
                    data=self.gongchengTeamGet(teamid)
                    if not data:
                        removlist.append(teamid)
                        continue
                    data=self.gongchengPlayerGet(data["pid"])
                    if not data:
                        removlist.append(teamid)
                        continue
                for x in removlist:
                    cityobj["atk"].remove(x)
                
                removlist=[]
                for teamid in cityobj["def"]:
                    data=self.gongchengTeamGet(teamid)
                    if not data:
                        removlist.append(teamid)
                        continue
                    data=self.gongchengPlayerGet(data["pid"])
                    if not data:
                        removlist.append(teamid)
                        continue
                for x in removlist:
                    cityobj["def"].remove(x)

        self.markDirty()
    
    def gongchengMsg(self,id):
        resp={}
        resp["err"]=0

        groupkey = self.typeid2groupkey.get(str(5)+"-"+str(id),"")
        if not groupkey:
            resp["err"]=errcode.EC_GETD_GROUPKEYFAIL
            return resp

        x={"cityid":"1","ATKghname":"卡卡"}
        res=Game.res_mgr.res_gongcheng[int(x["cityid"])]
        info = res.gbinfo % (x["ATKghname"],)
        infostr=self.makeContent(5,0,info)


        data = {}
        data["rid"] = 0
        data["content"] = infostr
        data["type"] = 5

        print(data["content"])

        self.groupMsg(groupkey,"msg",data)


    
        return resp        


    def gongchengFucknpc(self,id):
        resp={}
        resp["err"]=0

        groupkey = self.typeid2groupkey.get(str(5)+"-"+str(id),"")
        if not groupkey:
            resp["err"]=errcode.EC_GETD_GROUPKEYFAIL
            return resp

        x={"cityid":"1","ATKghname":"卡卡"}
        res=Game.res_mgr.res_gongcheng[int(x["cityid"])]
        info = res.gbinfo % (x["ATKghname"],)
        infostr=self.makeContent(5,0,info)


        gmsg={
            "changecity":{},
            "type":5,
        }


        for cityid,cityobj in self.groupkeyData[groupkey]["city"].items():
            cityobj["npc"]=["npc600001"]

            gmsg["changecity"][cityid]=cityobj

        self.groupMsg(groupkey,"gmsg",gmsg)
        

    
        return resp      

    def gongchengGuildReward(self):

        for groupkey,data in self.groupkeyData.items():
            city = data.get("city",{})
            if not city:
                continue
            guildScore = data.get("guildScore",{})
            if not guildScore:
                continue

            for cityid,cityobj in city.items():
                if not cityobj["ghid"]:
                    continue


                
                if str(cityobj["ghid"]) not in guildScore:
                    continue

                res=Game.res_mgr.res_gongcheng[int(cityid)]

                addr=guildScore[str(cityobj["ghid"])]["addr"]
                pids=guildScore[str(cityobj["ghid"])]["pids"]

                from game.mgr.logicgame import LogicGame
                proxy = get_proxy_by_addr(addr, LogicGame._rpc_name_)
                success=False
                if proxy:

                    st = time.time()
                    try:
                        proxy.gongchengGuildReward(res.name,res.holdReward,pids, _no_result=True)
                        success = True
                    except Exception as e:
                        success = False
                        et = time.time()
                        print("proxy.gongchengGuildReward.fail", "%s|%s|%s|%s|%s|%s" % (
                            res.name, res.holdReward, pids, et - st, addr, e))
                        Game.glog.log2File("proxy.gongchengGuildReward.fail",
                                           "%s|%s|%s|%s|%s|%s" % (res.name,res.holdReward,pids, et - st, addr, e))
                
                print("gongchengGuildReward:",res.name,pids,success)

    def gongchengGuildCountScore(self):
        # for sid,groupkey in self.type_sid__groupkey[5].items():
        #     xx=self.groupkeyData.get(groupkey,{})
        #     if not xx:
        #         continue
        #     guildScore = xx.get("guildScore",{})
        #     if not guildScore:
        #         continue

        for groupkey,data in self.groupkeyData.items():
            city = data.get("city",{})
            if not city:
                continue
            guildScore = data.get("guildScore",{})
            if not guildScore:
                continue

            for cityid,cityobj in city.items():
                if not cityobj["ghid"]:
                    continue


                
                if str(cityobj["ghid"]) not in guildScore:
                    continue

                res=Game.res_mgr.res_gongcheng[int(cityid)]

                guildScore[str(cityobj["ghid"])]["score"]+=res.guildCitySocre


                nt = gtime.getYYYYMMDD()
                if 0==len(self.gongchengAct):
                    self.gongchengAct.append({"d":nt,"s":{}})
                
                if self.gongchengAct[-1]["d"]!=nt:
                    self.gongchengAct.append({"d":nt,"s":{}})
                
                gongchengActiveDay = Game.res_mgr.res_common.get("gongchengActiveDay")
                self.gongchengAct=self.gongchengAct[-gongchengActiveDay.i:]

                pserverNo=cityobj.get("serverNo",None)
                if pserverNo:
                    ss=self.gongchengAct[-1]["s"].get(pserverNo,{"ghid":{},"score":0})
                    self.gongchengAct[-1]["s"][pserverNo]=ss
                    ss["score"]+=res.guildCitySocre
                    ghscore=ss["ghid"].get(str(cityobj["ghid"]),{"score":0,"name":cityobj["ghname"]})
                    ss["ghid"][str(cityobj["ghid"])]=ghscore
                    ss["ghid"][str(cityobj["ghid"])]["score"]+=res.guildCitySocre

    def gongchengWar(self,id,city): 
        resp={}
        resp["err"]=0

        groupkey = self.typeid2groupkey.get(str(5)+"-"+str(id),"")
        if not groupkey:
            resp["err"]=errcode.EC_GETD_GROUPKEYFAIL
            return resp

        if id not in self.gongchengPlayer:
            resp["err"]=errcode.EC_GONGCHENG_NOTFOUNDPLAYER
            return resp

        city=str(city)

        if city not in self.groupkeyData[groupkey]["city"]:
            resp["err"]=errcode.EC_GONGCHENG_NOTFOUNDCITY
            return resp

        
        cityobj=self.groupkeyData[groupkey]["city"][city]

        nowtime=time.time()
        guildonlytime=cityobj.get("guildonlytime",0)

        if guildonlytime==0 and cityobj["guildonly"]:
            resp["err"]=errcode.EC_GONGCHENG_INWARING
            return resp

        gongchengWarReadyTime = Game.res_mgr.res_common.get("gongchengWarReadyTime")
        gongchengDeclarewarTime = Game.res_mgr.res_common.get("gongchengDeclarewarTime")
        
        if nowtime-guildonlytime<gongchengWarReadyTime.i+gongchengDeclarewarTime.i:
            resp["err"]=errcode.EC_GONGCHENG_INWARTIME
            return resp

        

        ghid=self.gongchengPlayer[id]["ghid"]
        ghname=self.gongchengPlayer[id]["ghname"]


        cityobj["guildonly"]=ghid
        cityobj["guildonlytime"]=nowtime
        cityobj["guildonlyname"]=ghname

        gmsg={}

        gmsg["changecity"]={city:self.groupkeyData[groupkey]["city"][city]}
        
        gmsg["type"]=5

        self.groupMsg(groupkey,"gmsg",gmsg)


        if not cityobj["ghid"]:
            return resp

        guildScore = self.groupkeyData[groupkey].get("guildScore",{})
        if not guildScore:
            return resp

        if str(cityobj["ghid"]) not in guildScore:
            return resp
        
        gs=guildScore[str(cityobj["ghid"])]
        
        addr=gs["addr"]
    
        from game.mgr.logicgame import LogicGame
        proxy = get_proxy_by_addr(addr, LogicGame._rpc_name_)
        success=False
        if proxy:

            st = time.time()
            try:
                proxy.gongchengNotiyGuild(cityobj["ghid"],city,False, _no_result=True)
                success = True
            except Exception as e:
                success = False
                et=time.time()
                print("proxy.gongchengNotiyGuild.fail", "%s|%s|%s|%s|%s" % (cityobj["ghid"],city,et-st,addr,e))
                Game.glog.log2File("proxy.gongchengNotiyGuild.fail", "%s|%s|%s|%s|%s" % (cityobj["ghid"],city,et-st,addr,e))
        
        print("gongchengNotiyGuild:",cityobj["ghid"],city,success)

        return resp

    #jiujiyishou##########################################################

    def jiujiyishouCreate(self,id,jiujiyishouId,pwd,fa,fa2,name):
        resp={}
        resp["err"]=0

        groupkey = self.typeid2groupkey.get(str(6)+"-"+str(id),"")
        if not groupkey:
            resp["err"]=errcode.EC_GETD_GROUPKEYFAIL
            return resp

        self.group[groupkey][id]["data"]["fa"]=fa
        self.group[groupkey][id]["data"]["fa2"]=fa2
        
        sdata = self.groupkeyData.get(groupkey,{"roomlist":{}})
        self.groupkeyData[groupkey]=sdata


        for k,v in sdata.items():
            for vv in v:

                if vv["ppid"]==id:
                    resp["err"]=errcode.EC_JIUJIYISHOU_ALREADYCREATE
                    return resp

                if vv["jpid"]==id:
                    resp["err"]=errcode.EC_JIUJIYISHOU_ALREADYJOIN
                    return resp

                

        xdata = sdata.get(str(jiujiyishouId),[])
        sdata[str(jiujiyishouId)]=xdata


        xdata.append({"ppid":id,"name":name,"pwd":pwd,"jpid":0,"jname":"","ct":time.time()})

        return resp

    def jiujiyishouJoin(self,id,ppid,pwd,fa,fa2,name):
        resp={}
        resp["err"]=0

        groupkey = self.typeid2groupkey.get(str(6)+"-"+str(id),"")
        if not groupkey:
            resp["err"]=errcode.EC_GETD_GROUPKEYFAIL
            return resp

        self.group[groupkey][id]["data"]["fa"]=fa
        self.group[groupkey][id]["data"]["fa2"]=fa2

        sdata = self.groupkeyData.get(groupkey,{"roomlist":{}})
        self.groupkeyData[groupkey]=sdata


        
        for k,v in sdata.items():
            for vv in v:

                if vv["ppid"]==id:
                    resp["err"]=errcode.EC_JIUJIYISHOU_ALREADYCREATE
                    return resp

                if vv["jpid"]==id:
                    resp["err"]=errcode.EC_JIUJIYISHOU_ALREADYJOIN
                    return resp

        found=False
        for k,v in sdata.items():
            for vv in v:
                if vv["ppid"]==ppid:
                    found=True
                    break
            if found:
                break

        
        if not found:
            resp["err"]=errcode.EC_JIUJIYISHOU_NOFOUND
            return resp
    
        if vv["jpid"]:
            resp["err"]=errcode.EC_JIUJIYISHOU_ALREADYFULL
            return resp

        if vv["pwd"]!=pwd:
            resp["err"]=errcode.EC_JIUJIYISHOU_BADPWD
            return resp
        
        vv["jpid"]=id
        vv["jname"]=name

        
        ppiddata=self.group[groupkey].get(ppid,None)
        if not ppiddata:
            resp["addr"]=None
            return resp

        resp["addr"]=ppiddata["addr"]
        return resp

    def jiujiyishouQuit(self,id):
        resp={}
        resp["err"]=0

        groupkey = self.typeid2groupkey.get(str(6)+"-"+str(id),"")
        if not groupkey:
            resp["err"]=errcode.EC_GETD_GROUPKEYFAIL
            return resp

        sdata = self.groupkeyData.get(groupkey,{"roomlist":{}})
        self.groupkeyData[groupkey]=sdata


        resp["addr"]=None
        resp["ppid"]=0
        for k,v in sdata.items():
            for vv in v:

                if vv["ppid"]==id:
                    if vv["jpid"]:
                        if self.group[groupkey].get(vv["jpid"],None):
                            resp["addr"]=self.group[groupkey][vv["jpid"]]["addr"]
                            resp["ppid"]=vv["jpid"]
                        vv["ppid"]=vv["jpid"]
                        vv["name"]=vv["jname"]
                        vv["jpid"]=0
                        vv["jname"]=""

                    else:
                        resp["addr"]=None
                        resp["ppid"]=0
                        v.remove(vv)

                    return resp

                if vv["jpid"]==id:
                    if self.group[groupkey].get(vv["ppid"],None):
                        resp["addr"]=self.group[groupkey][vv["ppid"]]["addr"]
                        resp["ppid"]=vv["ppid"]
                    vv["jpid"]=0
                    vv["jname"]=""
                    return resp

        resp["addr"]=None
        resp["ppid"]=0
        return resp



    def jiujiyishouPwd(self,id,pwd):
        resp={}
        resp["err"]=0

        groupkey = self.typeid2groupkey.get(str(6)+"-"+str(id),"")
        if not groupkey:
            resp["err"]=errcode.EC_GETD_GROUPKEYFAIL
            return resp

        sdata = self.groupkeyData.get(groupkey,{"roomlist":{}})
        self.groupkeyData[groupkey]=sdata


 
        for k,v in sdata.items():
            for vv in v:
                if vv["ppid"]==id:
                    vv["pwd"]=pwd
                    return resp
        return resp


    def jiujiyishouKick(self,id,ppid):
        resp={}
        resp["err"]=0

        groupkey = self.typeid2groupkey.get(str(6)+"-"+str(id),"")
        if not groupkey:
            resp["err"]=errcode.EC_GETD_GROUPKEYFAIL
            return resp


        sdata = self.groupkeyData.get(groupkey,{"roomlist":{}})
        self.groupkeyData[groupkey]=sdata

        resp["addr"]=None
        for k,v in sdata.items():
            for vv in v:

                if vv["ppid"]==id:
                    if vv["jpid"]!=ppid:
                        # resp["err"]=errcode.EC_JIUJIYISHOU_NOFOUND
                        resp["addr"]=None
                        return resp

                    if self.group[groupkey].get(ppid,None):
                        resp["addr"]=self.group[groupkey][ppid]["addr"]
                    vv["jpid"]=0
                    vv["jname"]=""
                    
                    return resp

        # resp["err"]=errcode.EC_JIUJIYISHOU_ISNOTMAIN
        
        return resp
    

    
    def jiujiyishouIn(self,id,jiujiyishouId,ppid):
        resp={}
        resp["err"]=0

        groupkey = self.typeid2groupkey.get(str(6)+"-"+str(id),"")
        if not groupkey:
            resp["err"]=errcode.EC_GETD_GROUPKEYFAIL
            return resp


        sdata = self.groupkeyData.get(groupkey,{"roomlist":{}})
        self.groupkeyData[groupkey]=sdata

        xdata = sdata.get(str(jiujiyishouId),[])
        sdata[str(jiujiyishouId)]=xdata

        found=False
        for vv in xdata:
            if vv["ppid"]==id:
                found=True
                break

        if not found:
            return resp

        
        if vv["jpid"]!=ppid:
            resp["err"]=errcode.EC_JIUJIYISHOU_NOFOUND
            return resp

        ppiddata=self.group[groupkey].get(ppid,None)
        if ppiddata:
            resp["addr"]=self.group[groupkey][ppid]["addr"]
        else:
            resp["addr"]=None

        xdata.remove(vv)

        return resp


    def jiujiyishouGetRoom(self,id,jiujiyishouId):
        resp={}
        resp["err"]=0

        groupkey = self.typeid2groupkey.get(str(6)+"-"+str(id),"")
        if not groupkey:
            resp["err"]=errcode.EC_GETD_GROUPKEYFAIL
            return resp


        sdata = self.groupkeyData.get(groupkey,{"roomlist":{}})
        self.groupkeyData[groupkey]=sdata

        xdata = sdata.get(str(jiujiyishouId),[])
        sdata[str(jiujiyishouId)]=xdata

        xxdata=[]
        for v in xdata:
            if v["jpid"]:
                continue
            xxdata.append(v)
        resp["roomlist"]=xxdata

        return resp
    
    def gongchengQuanmingRank(self):
        return self.gongchengAct

class RoomMgrCommon(RoomMgr):

    _rpc_name_ = 'rpc_room_mgr_common'
    