#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from corelib.frame import Game

class FightActions(object):
    """战斗动作组"""
    def __init__(self, type):
        self.type = type  #1=顺序 2=并发
        self.data = [] #动作列表

    def to_client(self):
        #打包数据给客户端
        resp = {}
        resp["t"] = self.type
        resp["d"] = []
        for one in self.data:
            resp["d"].append(one.to_client())
        return resp

    def add_action(self, action):
        self.data.append(action)

class Action(object):
    """战斗动作"""
    def __init__(self, fid, type):
        self.fid = fid  #战斗单位uid
        self.type = type #动作类型

        self.data = {} #动作参数

        self.next_actions = None #下一个动作

    def to_client(self):
        #打包数据给客户端
        resp = {}
        resp["fid"] = self.fid
        resp["t"] = self.type
        resp["d"] = self.data
        if self.next_actions:
            resp["nt"] = self.next_actions.to_client()
        return resp