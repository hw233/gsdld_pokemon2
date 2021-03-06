#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from game.define.store_define import TN_S_SINGLETON
from store.store import StoreObj


class ModelDaylyPVP(StoreObj):
    """日常pvp数据"""
    TABLE_NAME = TN_S_SINGLETON
    TABLE_KEY = "daylyPVP"

    def set_owner(self, owner):
        self.owner = owner

    def init(self):
        self.id = self.TABLE_KEY    # 键
        self.dataDict = {}          # 数据

    def to_save_dict(self, copy=False, forced=False):
        save = {}
        save["id"] = self.id
        save["dataDict"] = self.owner.to_save_dict(forced=forced)
        return save

    def save(self, store, forced=False, no_let=False):
        StoreObj.save(self, store, forced=forced, no_let=no_let)
        self.owner.cleanDirty()