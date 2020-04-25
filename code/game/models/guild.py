#!/usr/bin/env python
# -*- coding:utf-8 -*-
from game.define.store_define import TN_G_GUILD
from store.store import StoreObj


class ModelGuild(StoreObj):
    """公会数据"""
    TABLE_NAME = TN_G_GUILD

    def init(self):
        self.id = 0  # 帮会id
        self.name = ""  # 帮会名称
        self.color = 0  # 颜色
        self.level = 0  # 帮会等级
        self.exp = 0  # 帮会资金
        self.masterId = 0  # 帮主id
        self.masterName = ""  # 帮主名称
        self.notice = ""  # 帮会公告
        self.autoEnter = 0  # 是否自动入帮(autoEnter, int)
        self.autoFa = 0  # 自动入帮战力(autoFa, int)
        self.logs = []  # 帮会记录(time, name, type)
        self.members = [] # 帮会成员 {pid:info}

        self.clcleDayBytes = ""  # 天周期数据

    def to_save_dict(self, copy=False, forced=False):
        return self.owner.to_save_dict(forced=forced)

    def setOwner(self, owner):
        self.owner = owner

    def save(self, store, forced=False, no_let=False):
        StoreObj.save(self, store, forced=forced, no_let=no_let)
        self.owner.cleanDirty()

    def to_init_dict(self):
        resp = {}
        resp["id"] = self.id
        resp["name"] = self.name
        resp["color"] = self.color
        resp["level"] = self.level
        resp["exp"] = self.exp
        resp["masterId"] = self.masterId
        resp["masterName"] = self.masterName
        resp["notice"] = self.notice
        resp["autoEnter"] = self.autoEnter
        resp["autoFa"] = self.autoFa
        resp["logs"] = self.logs
        resp["members"] = self.members
        return resp