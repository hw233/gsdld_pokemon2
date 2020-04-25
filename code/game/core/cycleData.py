#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import pickle

from game.common import utility
from game import Game

class CycleBase(utility.DirtyFlag):
    def __init__(self, owner, keepCyc=1):
        utility.DirtyFlag.__init__(self)
        self.owner = owner  # 拥有者
        self.keepCyc = keepCyc #保存多少个周期的数据
        self.data = {} #{cycNo:json}

    #存库数据
    def to_save_bytes(self, forced=False):
        return pickle.dumps(self.data)

    #读库数据初始化
    def load_from_dict(self, data):
        if not data:
            return
        data = pickle.loads(data)
        lCycNo = list(data.keys())
        lCycNo.sort()
        for iCycNo in lCycNo:
            if self.getCycleNo() >= iCycNo + self.keepCyc:
                del data[iCycNo]
                self.markDirty()
            else:
                break
        self.data = data

    def markDirty(self):
        utility.DirtyFlag.markDirty(self)
        if self.owner:
            self.owner.markDirty()

    #iWhichCyc的值范围 0=当前周期 -1=上一个周期 -2=上两个周期 以此类推
    def Query(self, key, default=0, iWhichCyc=0, iCycNo=0):
        if not iCycNo:
            iCycNo = self.getCycleNo() + iWhichCyc
        return self.data.get(iCycNo, {}).get(key, default)

    def Set(self, key, value, iCycNo=0, iWhichCyc=0):
        if not iCycNo:
            iCycNo = self.getCycleNo() + iWhichCyc
        dCyc = self.data.setdefault(iCycNo, {})
        dCyc[key] = value
        self.markDirty()

    def Delete(self, key):
        iCycNo = self.getCycleNo()
        if iCycNo in self.data and key in self.data[iCycNo]:
            del self.data[iCycNo][key]
            self.markDirty()

#自定义周期数据
class CycleCustom(CycleBase):
    def __init__(self, owner, callback, keepCyc=1):
        CycleBase.__init__(self, owner, keepCyc=keepCyc)
        self.callback = callback
 
    def getCycleNo(self):
        return self.callback()

#天周期数据
class CycleDay(CycleBase):
    def getCycleNo(self):
        return utility.GetDayNo()

#周周期数据
class CycleWeek(CycleBase):
    def getCycleNo(self):
        return utility.GetWeekNo()

#月周期数据
class CycleMonth(CycleBase):
    def getCycleNo(self):
        return utility.GetMonthNo()

#小时周期数据
class CycleHour(CycleBase):
    def getCycleNo(self):
        return utility.GetHourNo()


class ActivityData(utility.DirtyFlag):
    def __init__(self, owner):
        utility.DirtyFlag.__init__(self)
        self.owner = owner  # 拥有者
        self.data = {} #{key:{data:data,CycleNo:CycleNo,actid:actid}} 

    #存库数据
    def to_save_bytes(self, forced=False):
        return pickle.dumps(self.data)

    #读库数据初始化
    def load_from_dict(self, data):
        if not data:
            return
        data = pickle.loads(data)

        dellist=[]
        for k,v in data.items():
            res = Game.res_mgr.res_activity.get(v["actid"])
            if res and v["CycleNo"]!=res.CycleNo:
                dellist.append(k)
                

        for k in dellist:
            del data[k]
            self.markDirty() 
           
        self.data = data

    def markDirty(self):
        utility.DirtyFlag.markDirty(self)
        if self.owner:
            self.owner.markDirty()


    #iWhichCyc的值范围 0=当前周期 -1=上一个周期 -2=上两个周期 以此类推
    def Query(self, key, default=0):

        data=self.data.get(key, None)
        if not data:
            return default        

        res = Game.res_mgr.res_activity.get(data["actid"])
        if not res:
            return default

        if data["CycleNo"]!=res.CycleNo:
            del self.data[key]
            self.markDirty()
            return default

        return data["data"]

    def Set(self, key, value, actid):
        res = Game.res_mgr.res_activity.get(actid)
        self.data[key]={"data":value,"CycleNo":res.CycleNo,"actid":actid}
        self.markDirty()

    def Delete(self, key):
        del self.data[key]
        self.markDirty()

class ActivityCycleData(utility.DirtyFlag):
    def __init__(self, owner):
        utility.DirtyFlag.__init__(self)
        self.owner = owner  # 拥有者
        self.data = {} #{key:{data:data,CycleNo:CycleNo,fid:fid,actid:actid}} 

    #存库数据
    def to_save_bytes(self, forced=False):
        return pickle.dumps(self.data)

    #读库数据初始化
    def load_from_dict(self, data):
        if not data:
            return
        data = pickle.loads(data)

        dellist=[]
        for k,v in data.items():
            res = Game.res_mgr.res_activity.get(v["actid"])
            serverInfo = Game.rpc_server_info.GetServerInfo()
            fid=res.getCycleFuncIDresid(serverInfo)
            if res and (v["CycleNo"]!=res.CycleNo or v["fid"]!=fid):
                dellist.append(k)
                

        for k in dellist:
            del data[k]
            self.markDirty() 
           
        self.data = data

    def markDirty(self):
        utility.DirtyFlag.markDirty(self)
        if self.owner:
            self.owner.markDirty()


    #iWhichCyc的值范围 0=当前周期 -1=上一个周期 -2=上两个周期 以此类推
    def Query(self, key, default=0):

        data=self.data.get(key, None)
        if not data:
            return default        

        res = Game.res_mgr.res_activity.get(data["actid"])
        if not res:
            return default

        serverInfo = Game.rpc_server_info.GetServerInfo()
        fid=res.getCycleFuncIDresid(serverInfo)
        if data["CycleNo"]!=res.CycleNo or data["fid"]!=fid:
            del self.data[key]
            self.markDirty()
            return default

        return data["data"]

    def Set(self, key, value, actid):
        res = Game.res_mgr.res_activity.get(actid)
        serverInfo = Game.rpc_server_info.GetServerInfo()
        fid=res.getCycleFuncIDresid(serverInfo)
        self.data[key]={"data":value,"CycleNo":res.CycleNo,"fid":fid,"actid":actid}
        self.markDirty()

    def Delete(self, key):
        del self.data[key]
        self.markDirty()




class MergeData(utility.DirtyFlag):
    def __init__(self, owner):
        utility.DirtyFlag.__init__(self)
        self.owner = owner  # 拥有者
        self.data = {} #{key:{data:data,CycleNo:CycleNo,actid:actid}} 

    #存库数据
    def to_save_bytes(self, forced=False):
        return pickle.dumps(self.data)

    #读库数据初始化
    def load_from_dict(self, data):
        if not data:
            return
        data = pickle.loads(data)

        dellist=[]
        for k,v in data.items():
                        
            serverInfo = Game.rpc_server_info.GetServerInfo()
            mergetime=serverInfo.get("mergetime", 0)        
            # print("==================",mergetime,v["CycleNo"])
            
            if v["CycleNo"]!=mergetime:
                dellist.append(k)
                

        for k in dellist:
            del data[k]
            self.markDirty() 
           
        self.data = data

    def markDirty(self):
        utility.DirtyFlag.markDirty(self)
        if self.owner:
            self.owner.markDirty()


    #iWhichCyc的值范围 0=当前周期 -1=上一个周期 -2=上两个周期 以此类推
    def Query(self, key, default=0):

        data=self.data.get(key, None)
        if not data:
            return default        
        
        serverInfo = Game.rpc_server_info.GetServerInfo()
        mergetime=serverInfo.get("mergetime", 0)        
        
        # print("==================",mergetime,data["CycleNo"])

        if data["CycleNo"]!=mergetime:
            del self.data[key]
            self.markDirty()
            return default

        return data["data"]

    def Set(self, key, value):
        
        serverInfo = Game.rpc_server_info.GetServerInfo()
        mergetime=serverInfo.get("mergetime", 0)        
        # print("==================",mergetime)

        self.data[key]={"data":value,"CycleNo":mergetime}
        self.markDirty()

    def Delete(self, key):
        del self.data[key]
        self.markDirty()
