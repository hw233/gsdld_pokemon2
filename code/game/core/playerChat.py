#!/usr/bin/env python
# -*- coding:utf-8 -*-

from game.common import utility
from game.define import constant
from corelib import spawn
from game import Game

class PlayerChat(utility.DirtyFlag):
    def __init__(self, owner):
        utility.DirtyFlag.__init__(self)
        self.owner = owner  # 拥有者
        self.chatData = {}
        self.noticeList = []

        self.save_cache = {}  # 存储缓存

    def markDirty(self):
        utility.DirtyFlag.markDirty(self)
        if self.owner:
            self.owner.markDirty()

    # 存库数据
    def to_save_dict(self, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            self.save_cache = {}
            self.save_cache["noticeList"] = self.noticeList
            self.save_cache["chatData"] = []
            for rid, data in self.chatData.items():
                self.save_cache["chatData"].append((rid, data))

        return self.save_cache

    # 读库数据初始化
    def load_from_dict(self, data):
        self.noticeList = data.get("noticeList", [])

        chatData = data.get("chatData", [])
        for one in chatData:
            rid = one[0]
            _data = one[1]
            self.chatData[rid] = _data

    # 登录初始化下发数据
    def to_init_data(self):
        init_data = {}
        init_data["noticeList"] = self.noticeList

        self.noticeList = []
        self.markDirty()
        return init_data

    def privateChatReceive(self, rid, chatinfo, content, sendTime):
        online = 0
        if Game.player_mgr.get_player(self.owner.id):
            online = 1
        if not online:
            self.noticeList.append(rid)

        chatData = self.chatData.setdefault(rid, {})
        chatinfo["lastTime"] = sendTime
        chatData['info'] = chatinfo
        chatlist = chatData.setdefault("chatlist", [])
        one = {
            "rid": rid,
            "content": content,
            "sendTime": sendTime
        }
        chatlist.append(one)
        if len(chatlist) > 50:
            chatlist.pop(0)
        self.markDirty()

    def privateChatSend(self, rid, chatinfo, content, sendTime):
        chatData = self.chatData.setdefault(rid, {})
        chatinfo["lastTime"] = sendTime
        chatData['info'] = chatinfo
        chatlist = chatData.setdefault("chatlist", [])
        one = {
            "rid": self.owner.id,
            "content": content,
            "sendTime": sendTime
        }
        chatlist.append(one)
        if len(chatlist) > 50:
            chatlist.pop(0)
        self.markDirty()

    def cleanPrivateChat(self, rid):
        self.chatData.pop(rid, None)
        self.markDirty()

    def getPrivateChatData(self, rid):
        chatData = self.chatData.get(rid, {})
        chatlist = chatData.get("chatlist", [])
        return chatlist

    def getPrivateChatList(self):
        keys = list(self.chatData.keys())
        onlines = Game.rpc_player_mgr.get_online_ids(pids=keys)
        chatList = []
        for rid, data in self.chatData.items():
            one = data.get("info", {})
            if rid in onlines:
                one["isOnline"] = 1
            else:
                one["isOnline"] = 0
            chatList.append(one)
        return chatList

