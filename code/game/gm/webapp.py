#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import sys
import web
import ujson

from corelib import log
from game import Game

from game.mgr.player import get_rpc_player
from game.define import constant, msg_define
import app

import config
web.config['debug'] = False #disable autoreload
apps = web.auto_application()

game_url = '/api/gm'
charge_url = '/api/charge'
mail_url = "/api/mail"
server_url = "/api/server"

AES = 1

_aes_encrypt = None
def aes_encrypt(data):
    global _aes_encrypt
    if _aes_encrypt is None:
        from corelib.aes import new_aes_encrypt
        key = config.GM_AESKEY
        if key is not None:
            _aes_encrypt = new_aes_encrypt(key)
        else:
            log.warning('*****client AES key no found!')
            return data
    return _aes_encrypt(data)

def encode_json(data):
    """ 加密数据 """
    data = ujson.dumps(data)
    if not AES:
        return data
    return aes_encrypt(str(data))

def _wrap_permissions(func):
    def _func(*args, **kw):
        try:
            data = web.input(_method='GET')
            user, password = data.get('user'), data.get('password')
            if not user or not password:
                return
            if config.gm_users.get(user) != password:
                return
            return func(*args, **kw)
        except:
            log.log_except()
        return ''
    return _func

class UserPlayers(apps.page):
    """ 获取玩家列表
    http://172.16.40.2:8008/api/game/userPlayers?sns=1&sid=399367642
    """
    path = '%s/%s' % (game_url, 'userPlayers')

    @_wrap_permissions
    def GET(self):
        data = web.input(_method='GET')
        sns, sid = int(data.get('sns', 0)), data.get('sid')
        if not (sns and sid):
            return ''
        return sns, sid

class Charge(apps.page):
    """ 获取玩家列表
    http://127.0.0.1:18003/api/charge/charge?uid=玩家id&cid=商品id&rmb=xxx
    """
    path = '%s/%s' % (charge_url, 'charge')

    @_wrap_permissions
    def GET(self):
        data = web.input(_method='GET')
        uid, cid, rmb, test = int(data.get('uid', "0")), int(data.get('cid', "0")), int(data.get('rmb', "0")), int(data.get('test', '0'))

        print(uid, cid, rmb, test)

        player = get_rpc_player(uid)
        if not player:
            return constant.CHARGE_INSIDE_ERR_NOTFOUND_PLAYER


        return ujson.dumps({"result":player.charge2player(cid,rmb, test)})

class SendMail(apps.page):
    """ 发送邮件
    http://127.0.0.1:18003/api/mail/send
    """

    path = '%s/%s' % (mail_url, "send")

    @_wrap_permissions
    def POST(self):
        dataJson = web.data()
        data = ujson.loads(dataJson)
        playerIdList = data.get("player_id_list", "")
        playerNameList = data.get("player_name_list", "")
        title = data.get("title", "")
        content = data.get("content", "")
        attachment = data.get("attachment", "")
        show = data.get("show", False)
        jsonStr = data.get("json_str", "")
        print(jsonStr)

        jreward = {}
        if jsonStr:
            jreward = eval(jsonStr)
            if not type(jreward) is dict:
                return ujson.dumps({"result": constant.SENDMAIL_CODE_2})

        if not playerIdList or not playerNameList or not title or not content:
            return ujson.dumps({"result": constant.SENDMAIL_CODE_2})

        if not attachment:
            attachment = {}
        else:
            attachment = eval(attachment)
            if not type(attachment) is dict:
                return ujson.dumps({"result": constant.SENDMAIL_CODE_2})

            for k, v in attachment.items():
                try:
                    ik = int(k)
                    iv = int(v)
                    attachment.pop(k)
                    attachment[ik] = iv
                except:
                    return ujson.dumps({"result": constant.SENDMAIL_CODE_2})

        if playerIdList == "*" and playerNameList == "*":
            Game.rpc_mail_mgr.sendPublicMail(title, content, attachment, show=show)
        else:
            playerIdList = playerIdList.split(";")
            for playerId in playerIdList:
                if len(playerId) < 5:
                    continue

                try:
                    pid = int(playerId)
                    Game.rpc_mail_mgr.sendPersonMail(pid, title, content, attachment, show=show)
                except:
                    log.log_except()


        print(jreward)
        for k, v in jreward.items():
            for kk, vv in attachment.items():
                try:
                    ikk = int(kk)
                    ivv = int(vv)
                    v.pop(kk)
                    v[ikk] = ivv
                except:
                    log.log_except()

            try:
                pid = int(k)
                Game.rpc_mail_mgr.sendPersonMail(pid, title, content, v, show=False, push=False)
            except:
                log.log_except()

        return ujson.dumps({"result": constant.SENDMAIL_CODE_1})


class SyncServer(apps.page):
    """ 同步服务器数据
    http://127.0.0.1:18003/api/server/sync
    """

    path = '%s/%s' % (server_url, "sync")
    @_wrap_permissions
    def POST(self):
        dataJson = web.data()
        data = ujson.loads(dataJson)

        open_time = data.get("open_time", 0)
        if open_time <= 0:
            return ujson.dumps({"result": constant.SYNCSERVER_CODE_2})

        print(open_time)
        Game.rpc_server_info.SetServerOpenTime(open_time)

        return ujson.dumps({"result": constant.SYNCSERVER_CODE_1})


class Reload(apps.page):
    """ 热更新
    http://127.0.0.1:18003/api/server/reload
    """
    path = '%s/%s' % (server_url, "reload")
    @_wrap_permissions
    def POST(self):
        dataJson = web.data()
        data = ujson.loads(dataJson)

        pyStr = data.get("py", "")
        cfgStr = data.get("cfg", "")

        print(pyStr)
        if pyStr:
            app.frame.reload_modules(pyStr.split(";"))

        if cfgStr:
            Game.rpc_server_info.reloadConfig(cfgStr.split(";"))

            for _, logic in Game.rpc_logic_game:
                if logic:
                    logic.reloadConfig(cfgStr.split(";"))


        return ujson.dumps({"result": constant.SYNCSERVER_CODE_1})

class PlayerAction(apps.page):
    """ 封号
    http://127.0.0.1:18003/api/gm/player
    """
    path = '%s/%s' % (game_url, 'player')
    @_wrap_permissions
    def POST(self):
        dataJson = web.data()
        data = ujson.loads(dataJson)

        pid = int(data.get("pid", "0"))
        action = data.get("action", 0) # 1 封号 2解封号 3禁言 3解禁言

        print(pid, action)
        if pid:
            player = get_rpc_player(pid)
            if not player:
                return ujson.dumps({"result": constant.CHARGE_INSIDE_ERR_NOTFOUND_PLAYER})

            if action == 1:
                player.block()
            elif action == 2:
                player.unBlock()
            elif action == 3:
                player.shutup()
            elif action == 4:
                player.unShutup()

        return ujson.dumps({"result": constant.SYNCSERVER_CODE_1})

# 游戏监控(json):
# 1、游戏服状态监控(cpu_scene, cpu_glog, cpu_activity,
#    cpu_union, cpu_store=store进程cpu使用量;
# max_logics=最大逻辑进程数; logics=逻辑进程数; user=当前在线用户数; max_user=允许最大用户数);
class ServerStats(apps.page):
    """ 服务器运行信息
    """
    path = '%s/%s' % (game_url, 'serverstats')
    prefix = 'cpu_'

    @_wrap_permissions
    def GET(self):
        ret_val = {}
        logics = Game.rpc_logic_game.count
        max_logics = int(config.max_players / config.logic_players)
        user = Game.rpc_player_mgr.get_count()
        max_user = config.max_players
        ret_val.update({'logics': logics, 'max_logics': max_logics,
                        'user': user, 'max_user': max_user})

        return ujson.dumps(ret_val)

inited = 0
def init_app():
    global inited
    if inited:
        return
    inited = 1
    #游戏功能子进程,自己初始化sns

    log.info('app mapping:\n%s', '\n'.join(list(map(str, apps.mapping))))


def get_wsgi_app(*middleware):
    init_app()
    return apps.wsgifunc(*middleware)
