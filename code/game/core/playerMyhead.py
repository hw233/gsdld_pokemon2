#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from game.common import utility
from game.define import constant, msg_define
from game import Game
import time

# 时装(myheadInfo, json)
# 	已经激活id(active, [int])
# 	使用中id(use, int)
class PlayerMyhead(utility.DirtyFlag):
    def __init__(self, owner):
        utility.DirtyFlag.__init__(self)
        self.owner = owner  # 拥有者
        self.type1use = 0 #使用中id
        self.type2use = 0 #使用中id
        self.active = [] #激活列表
        self.save_cache = {} #存储缓存


    def markDirty(self):
        utility.DirtyFlag.markDirty(self)
        if self.owner:
            self.owner.markDirty()

    #存库数据
    def to_save_dict(self, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            self.save_cache = {}
            if self.type1use:
                self.save_cache["type1use"] = self.type1use
            if self.type2use:
                self.save_cache["type2use"] = self.type2use
            if self.active:
                self.save_cache["active"] = self.active
        return self.save_cache

    #读库数据初始化
    def load_from_dict(self, data):
        self.type1use = data.get("type1use", 0) 
        self.type2use = data.get("type2use", 0) 
        self.active = data.get("active", [])

    #登录初始化下发数据
    def to_init_data(self):
        init_data = {}
        init_data["type1use"] = self.type1use
        init_data["type2use"] = self.type2use
        init_data["active"] = self.active

        init_data["fa1"] = self.owner.attr.getModFa(constant.PKM2_FA_TYPE_12)
        init_data["fa2"] = self.owner.attr.getModFa(constant.PKM2_FA_TYPE_13)

        return init_data

    def recalAttr(self):
        total1 = {} #头像
        total2 = {} #边框
        # 激活列表
        for one in self.active:
            id = one.get("id", 0)
            res = Game.res_mgr.res_chenghao.get(id)
            if res:
                if res.type == 1:
                    for name, iNum in res.attr.items():
                        total1[name] = total1.get(name, 0) + iNum
                if res.type == 2:
                    for name, iNum in res.attr.items():
                        total2[name] = total2.get(name, 0) + iNum

        if total1:
            self.owner.attr.addAttr(total1, constant.PKM2_FA_TYPE_12, constant.PKM2_ATTR_CONTAINER_GLOBAL)
        if total2:
            self.owner.attr.addAttr(total2, constant.PKM2_FA_TYPE_13, constant.PKM2_ATTR_CONTAINER_GLOBAL)

    def activeMyhead(self, id, endtime):
        res = Game.res_mgr.res_myhead.get(id)
        if not res:
            return False

        t = int(time.time())
        if endtime==0:
            endtime=t+630720000

        for x in self.active:
            if x["id"]==id:
                return False

        self.active.append({"id":id,"endtime":endtime})

        if res.type==1:
            self.owner.attr.addAttr(res.attr, constant.PKM2_FA_TYPE_12, constant.PKM2_ATTR_CONTAINER_GLOBAL)
            self.type1use=id
        elif res.type==2:
            self.owner.attr.addAttr(res.attr, constant.PKM2_FA_TYPE_13, constant.PKM2_ATTR_CONTAINER_GLOBAL)
            self.type2use=id

        self.markDirty()
        return True

    def useMyhead(self,id):
        if -1==id:
            self.type1use=0
            self.markDirty()
            return
        if -2==id:
            self.type2use=0
            self.markDirty()
            return
        
        res = Game.res_mgr.res_myhead.get(id)
        if not res:
            return

        if res.type==1:
            self.type1use=id
        elif res.type==2:
            self.type2use=id

        self.markDirty()
    
    def uninit(self):
        pass
    
    def Flash(self):
        t = int(time.time())
        delid=[]
        for x in self.active:
            if x["endtime"]<=t:
                delid.append(x["id"])

        for did in delid:
            res = Game.res_mgr.res_myhead.get(did)
            if res:
                if res.type==1:
                    self.owner.attr.delAttr(res.attr, constant.PKM2_FA_TYPE_12, constant.PKM2_ATTR_CONTAINER_GLOBAL)
                elif res.type==2:
                    self.owner.attr.delAttr(res.attr, constant.PKM2_FA_TYPE_13, constant.PKM2_ATTR_CONTAINER_GLOBAL)
                

            for xid in range(len(self.active)):
                if self.active[xid]["id"]==did:
                    del self.active[xid]
                    break
        
        found1=True
        found2=True
        if self.type1use:
            found1=False
        if self.type2use:
            found2=False

        for x in self.active:
            if x["id"]==self.type1use:
                found1=True
            if x["id"]==self.type2use:
                found2=True
        

        if not found1:
            self.type1use=0
        if not found2:
            self.type2use=0


        self.markDirty()


    def getPortrait(self):
        return self.type1use

    def getHeadframe(self):
        return self.type2use


