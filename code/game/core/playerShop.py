#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import random
import time

from game.common import utility
from game.define import msg_define, constant

from corelib.frame import Game
from corelib import spawn, spawn_later, gtime

import config
import copy

from game.core.cycleData import CycleDay, CycleWeek, CycleMonth


class PlayerShop(utility.DirtyFlag):
    def __init__(self, owner):
        utility.DirtyFlag.__init__(self)
        self.owner = owner  # 拥有者

        self.cycleDay = CycleDay(self)
        self.cycleWeek = CycleWeek(self)
        self.cycleMonth = CycleMonth(self)

        self.constID2UseFreeNumAndTime={} #外面免费重置时间 {constID:{"Num":??,"Time":??}} 次数， 刷新时间   #####有恢复时间那个
        self.shopdata={} #{xx商店系统id:[商店表id]}
        self.ConstTypeIdxX={} #{resid:{idx:??}} 是否需要刷新




        self.save_cache = {} #存储缓存


    def markDirty(self):
        utility.DirtyFlag.markDirty(self)
        if self.owner:
            self.owner.markDirty()

    #存库数据
    def to_save_dict(self, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            self.save_cache = {}

            self.save_cache["cycleDay"] = self.cycleDay.to_save_bytes()
            self.save_cache["cycleWeek"] = self.cycleWeek.to_save_bytes()
            self.save_cache["cycleMonth"] = self.cycleMonth.to_save_bytes()

            self.save_cache["constID2UseFreeNumAndTime"] = utility.obj2list(self.constID2UseFreeNumAndTime)
            self.save_cache["shopdata"] = utility.obj2list(self.shopdata)

            self.save_cache["ConstTypeIdxX"] = self.ConstTypeIdxX


            



        return self.save_cache

    #读库数据初始化
    def load_from_dict(self, data):

        self.cycleDay.load_from_dict(data.get("cycleDay", ""))
        self.cycleWeek.load_from_dict(data.get("cycleWeek", ""))
        self.cycleMonth.load_from_dict(data.get("cycleMonth", ""))

        self.constID2UseFreeNumAndTime = utility.list2obj(data.get("constID2UseFreeNumAndTime", []))
        self.shopdata = utility.list2obj(data.get("shopdata", []))

        self.ConstTypeIdxX = data.get("ConstTypeIdxX", {})

    def getgroupid(self,group):

        

        pool=[]
        for k,v in Game.res_mgr.res_shopGroup.items():
            if v.group==group:
                value = (k, v.w)
                pool.append(value)

        resid=utility.Choice(pool)


        res=Game.res_mgr.res_shopGroup.get(resid)


        dd=self.getGroupID2BuyNum(res.refCycle)

        dd[resid]=0

        self.setGroupID2BuyNum(res.refCycle,dd)

        

        return resid

    def getshopdata(self):
        
        myshopdata={}
        nt=time.time()

        for k,v in Game.res_mgr.res_shopConst.items():

            myids=self.shopdata.setdefault(k,[])
            if len(myids)>len(v.manualgroup):
                myids=myids[len(v.manualgroup)]
                self.shopdata[k]=myids
            elif len(myids)<len(v.manualgroup):
                myids.extend( [0]* (len(v.manualgroup)-len(myids)) )
            
            for idx in range(len(v.manualgroup)):
                norefresh=self.getConstTypeIdx(k,idx,v.dayRefersh[idx])

                if not norefresh:
                    self.setConstTypeIdx(k,idx,v.dayRefersh[idx])
                    myids[idx]=self.getgroupid(v.manualgroup[idx])

            cliData=[]

            for gid in myids:
                gres=Game.res_mgr.res_shopGroup.get(gid)
                
                dd=self.getGroupID2BuyNum(gres.refCycle)
                one={"id":gid,"buynum":dd.get(gid,0)}
                cliData.append(one)


            myshopdata[k]=cliData
                



            if v.freeRecover and v.freeRefersh:
                x=self.constID2UseFreeNumAndTime.setdefault(k,{"Num":0,"Time":time.time()})

                while v.freeRefersh-x["Num"] != v.freeRefersh and x["Time"]+v.freeRecover<=nt:
                    x["Time"]+=v.freeRecover
                    x["Num"]-=1
                    if x["Num"]<0:
                        x["Num"]=0

        return myshopdata

    #登录初始化下发数据
    def to_init_data(self):

        init_data = {}

        
        init_data["shopdata"]=self.getshopdata()
                

        init_data["RefreshFreeNum"]=self.getRefreshFreeNum()
        init_data["RefreshCostNum"]=self.getRefreshCostNum()
        init_data["RefreshEndTime"]=self.getRefreshEndTime()



        self.markDirty()

        return init_data


    def getRefreshEndTime(self):
        xxx={}
        for k,v in Game.res_mgr.res_shopConst.items():
            if v.panelRefersh==1:
                xxx[k]=int(gtime.cur_day_hour_time(24))
            elif v.panelRefersh==2:
                xxx[k]=gtime.getNextMonday()
            elif v.panelRefersh==3:
                xxx[k]=gtime.getNextMonthFirstDay()
            else:
                xxx[k]=0
        return xxx


    def getRefreshCostNum(self):
        xxx={}
        for k,v in Game.res_mgr.res_shopConst.items():
            if not v.costRefersh:
                xxx[k]={"refershnum":0,"nexttime":0}
            else:
                dd=self.getConstID2CostByDay()
                x=dd.get(k,0)
                zero_day_time = int(gtime.cur_day_hour_time(24))
                xxx[k]={"refershnum":x,"nexttime":zero_day_time} #v.costRefersh-x

        return xxx


    def CostRefreshFreeNum(self,resid):

        v=Game.res_mgr.res_shopConst.get(resid)
        k=resid


        if v.freeRecover:

            x=self.constID2UseFreeNumAndTime.get(k)

            if v.freeRefersh-x["Num"] == v.freeRefersh:
                x["Time"]=time.time()
            
            x["Num"]+=1

            # print("!!!freeRecover!!!",self.constID2UseFreeNumAndTime)

            

        else:
            dd=self.getConstID2FreeByDay()
            x=dd.get(k,0)
            x+=1
            dd[k]=x
            self.setConstID2FreeByDay(dd)
            # print("!!!not freeRecover!!!",dd)


    def CostRefreshCostNum(self,resid):

        # v=Game.res_mgr.res_shopConst.get(resid)
        k=resid



        dd=self.getConstID2CostByDay()
        x=dd.get(k,0)
        x+=1
        dd[k]=x
        self.setConstID2CostByDay(dd)
        # print("!!!not costRecover!!!",dd)


    def getRefreshFreeNum(self):
        xxx={}
        for k,v in Game.res_mgr.res_shopConst.items():
            if not v.freeRefersh:
                xxx[k]={"refershnum":0,"nexttime":0}
            else:
                if v.freeRecover:
                    x=self.constID2UseFreeNumAndTime.get(k)

                    tt=0
                    if v.freeRefersh-x["Num"] != v.freeRefersh:
                        tt=x["Time"]+v.freeRecover
                    
                    xxx[k]={"refershnum":x["Num"],"nexttime":tt} #v.freeRefersh-x["Num"]
                else:
                    dd=self.getConstID2FreeByDay()
                    x=dd.get(k,0)
                    zero_day_time = int(gtime.cur_day_hour_time(24))
                    xxx[k]={"refershnum":x,"nexttime":zero_day_time} #v.freeRefersh-x

        return xxx

    #零点更新的数据
    def to_wee_hour_data(self):
        return self.to_init_data()


    # 角色下线时要做的清理操作
    def uninit(self):
        pass
    
    #商品已购买次数
    def getGroupID2BuyNum(self, type):

        if type==1:
            return self.cycleDay.Query("GroupID2BuyNum"+str(type),{})
        elif type==2:
            return self.cycleWeek.Query("GroupID2BuyNum"+str(type),{})
        elif type==3:
            return self.cycleMonth.Query("GroupID2BuyNum"+str(type),{})
        else:
            # 不限购
            
            return {}

    def setGroupID2BuyNum(self, type, v):

        if type==1:
            self.cycleDay.Set("GroupID2BuyNum"+str(type), v)
        elif type==2:
            self.cycleWeek.Set("GroupID2BuyNum"+str(type), v)
        elif type==3:
            self.cycleMonth.Set("GroupID2BuyNum"+str(type), v)
        else:
            # 不限购
            pass
        
    
    #外面已经免费刷新次数
    def getConstID2FreeByDay(self):
        return self.cycleDay.Query("ConstID2FreeByDay",{})

    def setConstID2FreeByDay(self, v):
        self.cycleDay.Set("ConstID2FreeByDay", v)

    #外面已经收费刷新次数
    def getConstID2CostByDay(self):
        return self.cycleDay.Query("ConstID2CostByDay",{})

    def setConstID2CostByDay(self, v):
        self.cycleDay.Set("ConstID2CostByDay", v)

    def manualRefresh(self,res):
        for idx in range(len(res.mRefersh)):
            if res.mRefersh[idx]:
                self.cleanConstTypeIdx(res.id,idx,res.dayRefersh[idx])

    
    #是否需要不重置数据 1=不重置 0=重置
    def getConstTypeIdx(self, resid, idx, type):

        if type==1:
            return self.cycleDay.Query("ConstTypeIdx"+str(resid).zfill(4)+"_"+str(idx).zfill(4),0)
        elif type==2:
            return self.cycleWeek.Query("ConstTypeIdx"+str(resid).zfill(4)+"_"+str(idx).zfill(4),0)
        elif type==3:
            return self.cycleMonth.Query("ConstTypeIdx"+str(resid).zfill(4)+"_"+str(idx).zfill(4),0)
        else:
            # 不自动刷新
            x=self.ConstTypeIdxX.setdefault(str(resid),{})
            self.markDirty()
            return x.setdefault(str(idx),0)


    def setConstTypeIdx(self, resid, idx, type):

        if type==1:
            self.cycleDay.Set("ConstTypeIdx"+str(resid).zfill(4)+"_"+str(idx).zfill(4), 1)
        elif type==2:
            self.cycleWeek.Set("ConstTypeIdx"+str(resid).zfill(4)+"_"+str(idx).zfill(4), 1)
        elif type==3:
            self.cycleMonth.Set("ConstTypeIdx"+str(resid).zfill(4)+"_"+str(idx).zfill(4), 1)
        else:
            # 不自动刷新
            x=self.ConstTypeIdxX.setdefault(str(resid),{})
            x[str(idx)]=1
            self.markDirty()


    def cleanConstTypeIdx(self, resid, idx, type):

        if type==1:
            self.cycleDay.Set("ConstTypeIdx"+str(resid).zfill(4)+"_"+str(idx).zfill(4), 0)
        elif type==2:
            self.cycleWeek.Set("ConstTypeIdx"+str(resid).zfill(4)+"_"+str(idx).zfill(4), 0)
        elif type==3:
            self.cycleMonth.Set("ConstTypeIdx"+str(resid).zfill(4)+"_"+str(idx).zfill(4), 0)
        else:
            # 不自动刷新
            x=self.ConstTypeIdxX.setdefault(str(resid),{})
            x[str(idx)]=0
            self.markDirty()
