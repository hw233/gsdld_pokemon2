#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from store.driver import *

#====================   游戏数据库定义 ===============================
#类名定义
TN_P_PLAYER = 'player'
TN_S_SINGLETON = 'singleton'
TN_R_RANK = "rank"
TN_R_CROSS_RANK = "crossrank"
TN_M_MAIL = "mail"
TN_F_FRIEND = "friend"
TN_G_GUILD = "guild"
TN_G_GONGCHENGPLAYER = "gongchengplayer"
TN_G_GONGCHENGTEAM = "gongchengteam"
TN_T_TXDY_PLAYER = "txdyplayer"
TN_T_TXDY_FIGHTLOG = "txdyfightlog"
TN_L_LEVEL_CONTEST_GROUP = "levelcontestgroup"
TN_G_GROUP_PK_GROUP = "grouppkgroup"
TN_G_GROUP_PK_PLAYER = "grouppkplayer"
TN_G_GROUP_PK_FIGHTLOG = "grouppkfightlog"


#类与表名关系 (tablename, key, indexs, autoInc)
GAME_MONGO_CLS_INFOS = {
    TN_P_PLAYER: (TN_P_PLAYER, 'id', [('account',{}), ('name',{})], True),
    TN_S_SINGLETON: (TN_S_SINGLETON, 'id', [], False),
    TN_R_RANK: (TN_R_RANK, 'id', [], False),
    TN_R_CROSS_RANK: (TN_R_CROSS_RANK, 'id', [], True),
    TN_M_MAIL: (TN_M_MAIL, 'id', [], False),
    TN_G_GUILD: (TN_G_GUILD, 'id', [('name',{'unique':True})], True),
    TN_F_FRIEND: (TN_F_FRIEND, 'id', [], True),
    TN_G_GONGCHENGPLAYER: (TN_G_GONGCHENGPLAYER, 'id', [], True),
    TN_G_GONGCHENGTEAM: (TN_G_GONGCHENGTEAM, 'id', [], True),
    TN_T_TXDY_PLAYER: (TN_T_TXDY_PLAYER, 'id', [], True),
    TN_T_TXDY_FIGHTLOG: (TN_T_TXDY_FIGHTLOG, 'id', [], True),
    TN_L_LEVEL_CONTEST_GROUP: (TN_L_LEVEL_CONTEST_GROUP, 'id', [], True),
    TN_G_GROUP_PK_GROUP: (TN_G_GROUP_PK_GROUP, 'id', [], True),
    TN_G_GROUP_PK_PLAYER: (TN_G_GROUP_PK_PLAYER, 'id', [], True),
    TN_G_GROUP_PK_FIGHTLOG: (TN_G_GROUP_PK_FIGHTLOG, 'id', [], True),
}

GAME_CLS_INFOS = {
    MONGODB_ID: GAME_MONGO_CLS_INFOS,
}
#====================   游戏数据库定义 end ===============================


#====================   资源数据库定义 ===============================
RES_MONGO_CLS_INFOS = {

}

RES_CLS_INFOS = {
    MONGODB_ID: RES_MONGO_CLS_INFOS,
}
#====================   游戏数据库定义  end===============================

#gconfig key 列表
GF_ACCESS_IP = 'access_ip' #admin access ip re



#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

