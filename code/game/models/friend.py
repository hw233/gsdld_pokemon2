#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from game.define.store_define import TN_F_FRIEND
from store.store import StoreObj


class ModelFriend(StoreObj):
    """服务器数据"""
    TABLE_NAME = TN_F_FRIEND

    def init(self):
        self.id = 0
        self.dataDict = {}  # 数据

    def to_save_dict(self, copy=False, forced=False):
        save = {}
        save["id"] = self.owner.pid
        save["dataDict"] = self.owner.to_save_dict(forced=forced)
        return save

    def setOwner(self, owner):
        self.owner = owner

    def save(self, store, forced=False, no_let=False):
        StoreObj.save(self, store, forced=forced, no_let=no_let)
        self.owner.cleanDirty()
