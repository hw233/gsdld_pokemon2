#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import ujson
import time

from corelib.frame import spawn, Game, log
from game.define import constant, msg_define

class ChatLogicRpc(object):
    if 0:
        from game.mgr import logicgame as logic_md
        logic = logic_md.LogicGame()

    def sendWorldMSG(self, pid, content):
        """世界聊天广播"""
        resp = dict(rid=pid, content=content)
        Game.player_mgr.broadcast("worldMSGNotice", resp)

        d = ujson.loads(content)
        rid = d.get("rid", 0)
        name = d.get("name", '')
        vip = d.get("vip", 0)
        msg = d.get("msg", {}).get("msg", '')
        isMsg = d.get("isMsg", 0)
        if isMsg:
            Game.glog.log2File("PlayerWorldMSG", "%s|%s|%s|%s" % (rid, name, vip, msg))
        return True

    def sendSystemMSG(self, content):
        resp = dict(content=content)
        Game.player_mgr.broadcast("sendSystemMSG", resp)
        return True

    def sendSystemTemplateMSG(self, id, args):
        resp = dict(id=id, args=args)
        Game.player_mgr.broadcast("sendSystemTemplateMSG", resp)
        return True