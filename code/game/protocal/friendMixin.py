# -*- coding:utf-8 -*-

from game.define import errcode, constant, msg_define
from game import Game
from game.common import utility
import time
import copy
import random


class FriendMixin(object):
    if 0:
        from game.core import player as player_md
        player = player_md.Player()

    # 获取关注列表(getFollowList)
    # 	请求
    # 	返回
    # 		关注列表(followList, [json])
    # 			玩家id(pid, int)
    # 			角色名字(name, string)
    # 			战力(fa, int)
    # 			等级(lv, int)
    # 			vip等级(vip, int)
    # 			性别(sex, int)
    # 				0=? 1=男 2=女
    # 			在线状态(online, int)
    # 				0=不在线 1=在线
    # 			赠送状态(presentStatus, int)
    # 				0=未赠送 1=已赠送
    # 			是否粉丝(isFan, int)
    # 				0=否 1=是
    def rc_getFollowList(self):
        fl, num = Game.rpc_friend_mgr.getFollowList(self.player.id)
        resp = {
            "followList": fl,
            "presentNum": num,
        }

        return 1, resp

    # 获取粉丝列表(getFanList)
    # 	请求
    # 	返回
    # 		粉丝列表(fanList, [json])
    # 			玩家id(pid, int)
    # 			角色名字(name, string)
    # 			战力(fa, int)
    # 			等级(lv, int)
    # 			vip等级(vip, int)
    # 			性别(sex, int)
    # 				0=? 1=男 2=女
    # 			在线状态(online, int)
    # 				0=不在线 1=在线
    # 			接收状态(receiveStatus, int)
    # 				0=未接收 1=已接收
    # 			是否粉丝(isFan, int)
    # 				0=否 1=是
    # 			能否接收(canReceive, int)
    # 				0=不能 1=能
    def rc_getFanList(self):
        fl, num = Game.rpc_friend_mgr.getFanList(self.player.id)
        resp = {
            "fanList": fl,
            "receiveNum": num,
        }

        return 1, resp

    # 获取黑名单(getBlackList)
    #     请求
    #     返回
    #         黑名单(blackList, [json])
    #             玩家id(pid, int)
    #             角色名字(name, string)
    #             战力(fa, int)
    #             等级(lv, int)
    #             vip等级(vip, int)
    #             性别(sex, int)
    #                 0=? 1=男 2=女
    #             在线状态(online, int)
    #                 0=不在线 1=在线
    def rc_getBlackList(self):
        resp = {
            "blackList": Game.rpc_friend_mgr.getBlackList(self.player.id)
        }

        return 1, resp

    # 获取推荐列表(getRecommendList)
    # 	请求
    # 	返回
    # 		黑名单(recommendList, [json])
    # 			玩家id(pid, int)
    # 			角色名字(name, string)
    # 			战力(fa, int)
    # 			等级(lv, int)
    # 			vip等级(vip, int)
    # 			性别(sex, int)
    # 				0=? 1=男 2=女
    # 			在线状态(online, int)
    # 				0=不在线 1=在线
    def rc_getRecommendList(self):
        resp = {
            "recommendList": Game.rpc_friend_mgr.getRecommendList(self.player.id)
        }

        return 1, resp

    # 关注(addFollow)
    # 	请求
    # 		玩家id(pid, int)
    # 	返回
    # 		玩家id(pid, int)
    def rc_addFollow(self, pid):
        code, status = Game.rpc_friend_mgr.addFollow(self.player.id, pid)
        if code:
            return 0, code
        # 抛事件
        self.player.safe_pub(msg_define.MSG_ADD_FOLLOW_FRIEND)
        return 1, {"pid": pid, "presentStatus": status}

    # 取消关注(delFollow)
    # 	请求
    # 		玩家id(pid, int)
    # 	返回
    # 		玩家id(pid, int)
    def rc_delFollow(self, pid):
        code = Game.rpc_friend_mgr.delFollow(self.player.id, pid)
        if code:
            return 0, code

        return 1, {"pid": pid}

    # 拉入黑名单(addBlack)
    # 	请求
    # 		玩家id(pid, int)
    # 	返回
    # 		玩家id(pid, int)
    def rc_addBlack(self, pid):
        code = Game.rpc_friend_mgr.addBlack(self.player.id, pid)
        if code:
            return 0, code

        return 1, {"pid": pid}


    # 取消黑名单(delBlack)
    # 	请求
    # 		玩家id(pid, int)
    # 	返回
    # 		玩家id(pid, int)
    def rc_delBlack(self, pid):
        code = Game.rpc_friend_mgr.delBlack(self.player.id, pid)
        if code:
            return 0, code

        return 1, {"pid": pid}

    # 赠送(presentFollow)
    # 	请求
    # 		玩家id(pid, int)
    # 	返回
    # 		玩家id(pid, int)
    # 		赠送状态(presentStatus, int)
    # 			0=未发送 1=已发送
    def rc_presentFollow(self, pid):
        code = Game.rpc_friend_mgr.presentFollow(self.player.id, pid)
        if code:
            return 0, code
        # 抛事件
        self.player.safe_pub(msg_define.MSG_FRIEND_SEND)
        return 1, {"pid": pid}

    # 一键赠送(oneKeyPresentFollow)
    # 	请求
    # 	返回
    def rc_oneKeyPresentFollow(self):
        code = Game.rpc_friend_mgr.oneKeyPresentFollow(self.player.id)
        if code:
            return 0, code
        # 抛事件
        self.player.safe_pub(msg_define.MSG_FRIEND_SEND)
        return 1, None

    # 接收(receiveFan)
    # 	请求
    # 		玩家id(pid, int)
    # 	返回
    # 		主动推送刷新(allUpdate, json)
    # 			游戏模型-货币
    # 		玩家id(pid, int)
    # 		接收状态(receiveStatus, int)
    # 			0=未接收 1=已接收
    def rc_receiveFan(self, pid):
        code = Game.rpc_friend_mgr.receiveFan(self.player.id, pid)
        if code:
            return 0, code

        respBag = self.player.bag.add({constant.CURRENCY_FRIEND_COIN: 1}, constant.ITEM_ADD_FRIEND_RECEIVE, wLog=True)

        dUpdate = self.player.packRespBag(respBag)
        resp = {
            "allUpdate": dUpdate,
            "pid": pid,
        }
        return 1, resp

    # 一键接收(oneKeyReceiveFan)
    # 请求
    # 玩家id列表(pidList, [int])
    # 返回
    # 主动推送刷新(allUpdate, json)
    # 游戏模型 - 货币
    def rc_oneKeyReceiveFan(self, pidList):
        code, num = Game.rpc_friend_mgr.oneKeyReceiveFan(self.player.id, pidList)
        if code:
            return 0, code

        respBag = self.player.bag.add({constant.CURRENCY_FRIEND_COIN: num}, constant.ITEM_ADD_FRIEND_RECEIVE, wLog=True)

        dUpdate = self.player.packRespBag(respBag)
        resp = {
            "allUpdate": dUpdate,
        }

        return 1, resp

