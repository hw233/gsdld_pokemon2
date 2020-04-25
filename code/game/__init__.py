#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from corelib import spawn
from corelib.frame import Game, MSG_FRAME_START

from game.define import msg_define, store_define
from game.common.gateway import GateWayMgr
from game.mgr.res import ResMgr
from game.mgr.condition import ConditionMgr


def public_init():
    """ 初始化rpc功能模块  """
    from game.common.db import new_game_store
    store = new_game_store()
    Game.store = store
    #日志
    from game.mgr.logger import GameLogger
    Game.glog = GameLogger()
    from game.mgr.logger import createLogErrorHandler
    createLogErrorHandler()


#-------------- app_room  --------------------
def init_app_room():
    public_init()

    Game.res_mgr = ResMgr()
    Game.res_mgr.load()

    #注册开始消息
    Game.sub(MSG_FRAME_START, start_room)
    #初始化rpc功能模块
    from game.mgr.timer import Timer
    Game.timer = Timer()

    #战斗
    Game.fight_mgr = FightMgr()

    from game.mgr.room import RoomMgr
    rpc_room_mgr = RoomMgr()

    from game.mgr.daylyPVP import DaylyPVPMgr
    rpc_dayly_pvp_mgr = DaylyPVPMgr()

    from game.mgr.txdy import TxdyMgr
    rpc_txdy_mgr = TxdyMgr()

    from game.mgr.globalData import GlobalDataMgr
    rpc_globalData_mgr = GlobalDataMgr()

    from game.mgr.crossRank import CrossRankMgr
    rpc_cross_rank_mgr = CrossRankMgr()

    from game.mgr.levelContest import LevelContestMgr
    rpc_level_contest_mgr = LevelContestMgr()

    from game.mgr.groupPK import GroupPKMgr
    rpc_grouppk_mgr = GroupPKMgr()

    return rpc_room_mgr, rpc_dayly_pvp_mgr, rpc_txdy_mgr, rpc_cross_rank_mgr, rpc_level_contest_mgr, rpc_grouppk_mgr, rpc_globalData_mgr

def start_room():
    Game.unsub(MSG_FRAME_START, start_room)
    Game.timer.start()
    Game.rpc_room_mgr.start()
    Game.rpc_dayly_pvp_mgr.start()
    Game.rpc_txdy_mgr.start()
    Game.rpc_globalData_mgr.start()
    Game.rpc_cross_rank_mgr.start()
    Game.rpc_level_contest_mgr.start()
    Game.rpc_grouppk_mgr.start()



#-------------- app_room end --------------------

#-------------- app_common  --------------------
def init_app_common():
    public_init()

    Game.res_mgr = ResMgr()
    Game.res_mgr.load()

    Game.condition_mgr = ConditionMgr()

    #注册开始消息
    Game.sub(MSG_FRAME_START, start_common)
    #时间管理
    from game.mgr.timer import Timer
    Game.timer = Timer()
    #初始化rpc功能模块
    from game.mgr.player import GPlayerMgr
    rpc_player_mgr = GPlayerMgr()
    #服务器信息
    from game.mgr.server import ServerInfo
    rpc_server_info = ServerInfo()
    #好友管理
    from game.mgr.friend import FriendMgr
    rpc_friend_mgr = FriendMgr()
    # 邮箱
    from game.mgr.mail import MailMgr
    rpc_mail_mgr = MailMgr()
    #答题管理
    from game.mgr.exam import ExamMgr
    rpc_exam_mgr = ExamMgr()
    #全民boss
    from game.mgr.boss import QmBossMgr
    rpc_qmboss_mgr = QmBossMgr()
    #野外boss
    from game.mgr.boss import YwBossMgr
    rpc_ywboss_mgr = YwBossMgr()
    # 生死劫boss
    from game.mgr.boss import SsjBossMgr
    rpc_ssjboss_mgr = SsjBossMgr()
    #服务器公共资源管理
    from game.mgr.commonres import CommonresMgr
    rpc_commonres_mgr = CommonresMgr()
    #房间管理-本地
    from game.mgr.room import RoomMgrCommon
    rpc_room_mgr_common = RoomMgrCommon()
    #日常pvp-本地
    from game.mgr.daylyPVP import DaylyPVPMgrCommon
    rpc_dayly_pvp_mgr_common = DaylyPVPMgrCommon()
    #帮会管理
    from game.mgr.guild import GuildMgr
    rpc_guild_mgr = GuildMgr()



    return rpc_player_mgr, rpc_server_info, rpc_friend_mgr, rpc_mail_mgr, rpc_exam_mgr, \
           rpc_qmboss_mgr, rpc_ywboss_mgr, rpc_ssjboss_mgr, rpc_commonres_mgr, \
           rpc_dayly_pvp_mgr_common, rpc_room_mgr_common, rpc_guild_mgr
               

def start_common():
    Game.unsub(MSG_FRAME_START, start_common)
    #gateway
    Game.gateway = GateWayMgr(Game.rpc_player_mgr)
    Game.app.register(Game.gateway)


    Game.timer.start()
    Game.rpc_player_mgr.start()
    Game.rpc_server_info.start()
    Game.rpc_friend_mgr.start()
    Game.rpc_mail_mgr.start()
    Game.rpc_exam_mgr.start()
    Game.rpc_qmboss_mgr.start()
    Game.rpc_ywboss_mgr.start()
    Game.rpc_ssjboss_mgr.start()
    Game.rpc_commonres_mgr.start()
    Game.rpc_dayly_pvp_mgr_common.start()
    Game.rpc_room_mgr_common.start()
    Game.rpc_guild_mgr.start()


    
#-------------- app_player end --------------------

#-------------- app_logic --------------------
def init_app_logic():
    public_init()

    Game.res_mgr = ResMgr()
    Game.res_mgr.load()

    Game.condition_mgr = ConditionMgr()

    #注册开始消息
    Game.sub(MSG_FRAME_START, start_logic)
    #初始化rpc功能模块
    from game.mgr.logicgame import LogicGame
    Game.logic_game = LogicGame()
    #玩家管理器
    from game.mgr.player import SubPlayerMgr
    Game.player_mgr = SubPlayerMgr()
    Game.logic_game.stop_mgrs.append(Game.player_mgr)

    return Game.logic_game, Game.player_mgr


def start_logic():
    Game.unsub(MSG_FRAME_START, start_logic)
    #gateway
    Game.gateway = GateWayMgr(Game.player_mgr)
    Game.app.register(Game.gateway)
    #游戏类
    Game.logic_game.start()


#-------------- app_logic end --------------------


#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
