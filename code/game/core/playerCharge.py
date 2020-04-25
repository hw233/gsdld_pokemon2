#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from game.common import utility
from game.define import msg_define, constant
from game import Game
import config
from corelib import spawn_later, log, spawn
import copy
import time
import math
from corelib.gtime import getZeroTime, zero_day_time, current_time


class PlayerCharge(utility.DirtyFlag):
    def __init__(self, owner):
        utility.DirtyFlag.__init__(self)
        self.owner = owner  # 拥有者

        self.dontuse = 0 #不要用这个模块存东西
     
        self.save_cache = {} #存储缓存


    def markDirty(self):
        utility.DirtyFlag.markDirty(self)
        if self.owner:
            self.owner.markDirty()

    #存库数据
    def to_save_dict(self, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            self.save_cache = {}

            self.save_cache["dontuse"] = self.dontuse


        return self.save_cache

    #读库数据初始化
    def load_from_dict(self, data):
        self.dontuse = data.get("dontuse", 0)

         

    #登录初始化下发数据
    def to_init_data(self):


        init_data = {}
        
        init_data["dontuse"] = self.dontuse

        return init_data
    
    def to_wee_hour_data(self):
        return self.to_init_data()


    #充值
    def charge(self,id,rmb, test=False):


        Game.glog.log2File("charge_begin", "%s|%s|%s" % (self.owner.id, id, rmb))
        res = Game.res_mgr.res_charge.get(id)
        if not res:
            return constant.CHARGE_INSIDE_ERR_NOT_FOUND_ID        
        
        if test:
            rmb=res.rmb

        
        if res.rmb!=rmb:
            return constant.CHARGE_INSIDE_ERR_RMB



        modresAll = getattr(Game.res_mgr, "res_%s" % res.type, None)
        if not modresAll:
            return constant.CHARGE_INSIDE_ERR_MODRES

        modres = modresAll.get(res.typeid)
        if not modres:
            return constant.CHARGE_INSIDE_ERR_MODRESID        

        moddef = getattr(self, "%s" % res.type, None)
        if not moddef:
            return constant.CHARGE_INSIDE_ERR_MODDEF


        Game.glog.log2File("charge_process", "%s|%s|%s" % (self.owner.id, id, rmb))

        self.owner.vip.addExp(res.exp)

        dUpdate=moddef(modres,res.rmb)

        dUpdate["vipInfo"] = self.owner.vip.to_init_data()

        spawn(self.owner.call, "PushCharge", {"id":id,"allUpdate": dUpdate}, noresult=True)
        
        if not test:
            Game.glog.log2File("playerPay", "%s|%s|%s|%s|%s" % (self.owner.id, self.owner.name, int(time.time()),rmb, id), flag=1)
        
        self.markDirty()
        return constant.CHARGE_INSIDE_OK

    def chargeDaily(self,res,rmb):

        print("===chargeDaily===",res.id,rmb)


        reward=self.owner.chargeDaily.getreward(res)

        respBag = self.owner.bag.add(reward, constant.ITEM_ADD_CHARGE, wLog=True, mail=True)


        # 打包返回信息
        dUpdate = self.owner.packRespBag(respBag)

        
        dUpdate["chargeDaily"] = self.owner.chargeDaily.to_init_data()


        return dUpdate

    def chargeMonth(self,res,rmb):
        dUpdate={}

        print("===chargeMonth===",res.id,rmb)
        
        return dUpdate

    def chargeQuick(self,res,rmb):

        print("===chargeQuick===",res.id,rmb)

        
        respBag = self.owner.bag.add(res.reward, constant.ITEM_ADD_CHARGE, wLog=True, mail=True)



        # 打包返回信息
        dUpdate = self.owner.packRespBag(respBag)


        
        zt=zero_day_time()
        
        self.owner.map.ChargeEndTime[res.id]=zt+res.day*3600*24
        self.owner.map.markDirty()
        
        
        dUpdate["map"] = self.owner.map.to_init_data()

        return dUpdate

    def chargeSent(self,res,rmb):

        print("===chargeSent===",res.id,rmb)

        
        respBag = self.owner.bag.add(res.reward, constant.ITEM_ADD_CHARGE, wLog=True, mail=True)



        # 打包返回信息
        dUpdate = self.owner.packRespBag(respBag)


        
        zt=zero_day_time()
        
        self.owner.rescue.ChargeEndTime[res.id]=zt+res.day*3600*24
        self.owner.rescue.markDirty()
        
        
        dUpdate["rescue"] = self.owner.rescue.to_init_data()

        return dUpdate



    def uninit(slef):
        pass