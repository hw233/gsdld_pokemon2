#!/usr/bin/env python
# -*- coding:utf-8 -*-
import random
import time

from game.define import errcode, constant, msg_define
from game import Game

from corelib import log

class ChatRpcMixin(object):
    if 0:
        from game.core import player as player_md
        player = player_md.Player()

    # 发送世界聊天(sendWorldMSG)
    # 请求
	#   聊天内容(content,string)
    # 返回
    # 全服广播(worldMSGNotice)
	#   玩家id(rid,int)
	#   聊天内容(content,string)
    def rc_sendWorldMSG(self, content, type=0):

        if self.player.isShutup():
            return

        if type==0:
            for addr, logic in Game.rpc_logic_game:
                if logic:
                    logic.sendWorldMSG(self.player.id, content)
        elif type==2:
            from game.mgr.room import get_rpc_diaoyu
            rpc_diaoyu = get_rpc_diaoyu()
            if not rpc_diaoyu:
                return 0, errcode.EC_GETD_RPC_ROOM_FAIL
            
            rrv = rpc_diaoyu.msg(2,self.player.id,content)
            if not rrv:
                return 0, errcode.EC_CALL_RPC_ROOM_FAIL
        elif type==3:
            from game.mgr.room import get_rpc_wakuang
            rpc_wakuang = get_rpc_wakuang()
            if not rpc_wakuang:
                return 0, errcode.EC_GETD_RPC_ROOM_FAIL
            
            data = self.player.zudui.getTeamInfo(0)
            rrv = rpc_wakuang.msg(3,data["id"],content)
            if not rrv:
                return 0, errcode.EC_CALL_RPC_ROOM_FAIL
        elif type==4:
            from game.mgr.room import get_rpc_boss
            rpc_boss = get_rpc_boss()
            if not rpc_boss:
                return 0, errcode.EC_GETD_RPC_ROOM_FAIL
            
            rrv = rpc_boss.msg(4,self.player.id,content)
            if not rrv:
                return 0, errcode.EC_CALL_RPC_ROOM_FAIL

        elif type==5:
            from game.mgr.room import get_rpc_gongcheng
            rpc_gongcheng = get_rpc_gongcheng()
            if not rpc_gongcheng:
                return 0, errcode.EC_GETD_RPC_ROOM_FAIL
            rrv = rpc_gongcheng.msg(5,self.player.id,content)
            if not rrv:
                return 0, errcode.EC_CALL_RPC_ROOM_FAIL
        elif type==6:
            from game.mgr.room import get_rpc_jiujiyishou
            rpc_jiujiyishou = get_rpc_jiujiyishou()
            if not rpc_jiujiyishou:
                return 0, errcode.EC_GETD_RPC_ROOM_FAIL
            rrv = rpc_jiujiyishou.msg(6,self.player.id,content)
            if not rrv:
                return 0, errcode.EC_CALL_RPC_ROOM_FAIL

        # 抛事件
        self.player.safe_pub(msg_define.MSG_SEND_WORLD_MSG)

        return 1, {}


    # 发送私聊(privateChatSend)
    # 请求
    #     玩家id(rid,int)
    #     聊天内容(content,string)
    # 返回
    #     玩家id(rid,int)
    #     聊天内容(content,string)
    #     时间(sendTime, int)
    def rc_privateChatSend(self, rid, content):
        sendTime = int(time.time())
        info = self.player.toChatInfo()
        from game.mgr.player import get_rpc_player
        rpc_player = get_rpc_player(rid)
        chatinfo = rpc_player.privateChatReceive(self.player.id, info, content, sendTime)

        self.player.chat.privateChatSend(rid, chatinfo, content, sendTime)

        resp = {}
        resp["rid"] = rid
        resp["content"] = content
        resp["sendTime"] = sendTime
        return 1, resp

    # 获取私聊列表(getPrivateChatList)
    # 请求
    # 返回
    #     私聊玩家列表(chatList, [json])
    #         玩家id(rid,int)
    #         名称(name, string)
    #         性别(sex, int)
    #             0=? 1=男 2=女
    #         等级(lv, int)
    #         vip等级(vipLv, int)
    #         战力(fa, int)
    #         是否在线(isOnline, int)
    def rc_getPrivateChatList(self):
        chatList = self.player.chat.getPrivateChatList()

        resp = {
            "chatList": chatList
        }
        return 1, resp

    # 获取私聊数据(getPrivateChatData)
    # 请求
    #     玩家id(rid,int)
    # 返回
    #     玩家id(rid,int)
    #     内容列表(contentList)
    #         玩家id(rid,int)
    #         聊天内容(content,string)
    #         时间(sendTime, int)
    def rc_getPrivateChatData(self, rid):
        contentList = self.player.chat.getPrivateChatData(rid)

        resp = {
            "rid": rid,
            "contentList": contentList
        }
        return 1, resp


    # 清除玩家私聊(cleanPrivateChat)
    # 请求
    #     玩家id(rid,int)
    # 返回
    #     玩家id(rid,int)
    def rc_cleanPrivateChat(self, rid):
        self.player.chat.cleanPrivateChat(rid)

        resp = {"rid":rid}
        return 1, resp


    # 发送小助手聊天(sendHelperChat)
    # 请求
    #     聊天内容(content,string)
    # 返回
    #     聊天内容(content,string)
    #     时间(sendTime, int)
    def rc_sendHelperChat(self, content):
        Game.glog.log2File("rc_sendHelperChat", "%s|%s|%s" % (self.player.id, self.player.name, content))

        resp = {
            "content": content,
            "sendTime": int(time.time())
        }
        return 1, resp












