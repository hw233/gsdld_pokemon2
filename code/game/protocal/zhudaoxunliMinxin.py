#!/usr/bin/env python
# -*- coding:utf-8 -*-
import random
import copy
from game.define import errcode, constant
from game import Game
from game.common import utility
import time
from gevent import sleep

class ZhudaoxunliRpcMixin(object):
    if 0:
        from game.core import player as player_md
        player = player_md.Player()


    def rc_zhudaoxunliInit(self):

        if not self.player.zhudaoxunli.time:
            self.player.zhudaoxunli.time=time.time()
            self.player.zhudaoxunli.markDirty()

        dUpdate = {}
        dUpdate["zhudaoxunli"] = self.player.zhudaoxunli.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp
    
    def rc_zhudaoxunliBuyScore(self,num):

        if not self.player.zhudaoxunli.time:
            return 0,errcode.EC_ZHUDAOXUNLI_NOTOPEN

        zhudaoxunliBuy = Game.res_mgr.res_common.get("zhudaoxunliBuy")
        if not zhudaoxunliBuy:
            return 0, errcode.EC_NORES

        cost={}
        for k,v in zhudaoxunliBuy.arrayint2.items():
            cost[k]=v*num
        

        respBag = self.player.bag.costItem(cost, constant.ITEM_COST_ZHUDAOXUNLI_BUYSOCRE, wLog=True)
        if not respBag.get("rs", 0):
            return 0, errcode.EC_NOT_ENOUGH

        self.player.zhudaoxunli.addscore(num*zhudaoxunliBuy.i)

        dUpdate = self.player.packRespBag(respBag)
        dUpdate["zhudaoxunli"] = self.player.zhudaoxunli.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp

    def rc_zhudaoxunliReward(self,resid):

        if not self.player.zhudaoxunli.time:
            return 0,errcode.EC_ZHUDAOXUNLI_NOTOPEN

        res = Game.res_mgr.res_zhudaoxunliReward.get(resid)
        if not res:
            return 0, errcode.EC_NORES

        d=None
        for v in self.player.zhudaoxunli.data:
            if v["qihao"]==res.qihao:
                d=v
                break

        if not d:
            return 0, errcode.EC_NORES

        if d["score"]<res.need:
            return 0,errcode.EC_ZHUDAOXUNLI_NONEED

        if res.id in d["reward"]:
            return 0,errcode.EC_ZHUDAOXUNLI_ALREADY

        respBag = self.player.bag.add(res.reward, constant.ITEM_ADD_ZHUDAOXUNLI_REWARD, wLog=True)


        self.player.zhudaoxunli.setreward(res.qihao,res.id)

        dUpdate = self.player.packRespBag(respBag)
        dUpdate["zhudaoxunli"] = self.player.zhudaoxunli.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp


    def rc_zhudaoxunliRewardVip(self,resid):

        if not self.player.zhudaoxunli.time:
            return 0,errcode.EC_ZHUDAOXUNLI_NOTOPEN

        res = Game.res_mgr.res_zhudaoxunliReward.get(resid)
        if not res:
            return 0, errcode.EC_NORES

        d=None
        for v in self.player.zhudaoxunli.data:
            if v["qihao"]==res.qihao:
                d=v
                break

        if not d:
            return 0, errcode.EC_NORES

        if not d["isVip"]:
            return 0,errcode.EC_ZHUDAOXUNLI_NOVIP

        if d["score"]<res.need:
            return 0,errcode.EC_ZHUDAOXUNLI_NONEED

        if res.id in d["rewardVip"]:
            return 0,errcode.EC_ZHUDAOXUNLI_ALREADY

        respBag = self.player.bag.add(res.rewardVip, constant.ITEM_ADD_ZHUDAOXUNLI_REWARD, wLog=True)

        self.player.zhudaoxunli.setrewardVip(res.qihao,res.id)

        dUpdate = self.player.packRespBag(respBag)
        dUpdate["zhudaoxunli"] = self.player.zhudaoxunli.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        return 1, resp

