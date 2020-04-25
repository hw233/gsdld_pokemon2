#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os
from os.path import join, exists
import time
import logging
import ujson
from logging import (ERROR, config)

from corelib import log
from game import Game
from game.define import constant

import config
import math

class GameLogger(object):
    def __init__(self):
        import app
        self.appname = app.name

    def log2File(self, sLogName, sText, flag=0):
        # 转换成localtime
        time_local = time.localtime(time.time())
        # 转换成新的时间格式(2016-05-05 20:28:54)
        dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
        # engine.C_Log2File("%s/%s/%s/%s.log"%(config.serverNo, self.appname, sLogName, sLogName),
        #                   "%s|%s|%s|%s"%(dt, config.serverNo, self.appname, sText),
        #                   flag)
        # print("%s/%s/%s/%s.log"%(config.serverNo, self.appname, sLogName, sLogName),
        #                   "%s|%s|%s|%s"%(dt, config.serverNo, self.appname, sText),
        #                   flag)

    def packLogin(self, player):
        return
        self.log2File("playerLogin", ("%s|"*7).rstrip("|") % (
            player.id,
            player.name,
            player.base.lv,
            player.base.fa,
            player.vip.vipExp,
            player.data.loginTime,
            player.data.loginNum
        ), flag=1)


    def packLogout(self, player):
        return
        self.log2File("playerLogout", ("%s|"*7).rstrip("|") % (
            player.id,
            player.name,
            player.base.lv,
            player.base.fa,
            player.vip.vipExp,
            player.data.loginTime,
            player.data.loginNum
        ), flag=1)

    def packDaoGuan(self, player):
        passList = player.daoguan.GetPassList()

        self.log2File("playerDaoGuan", ("%s|"*7).rstrip("|")  % (
            player.id,
            player.name,
            player.base.lv,
            player.base.fa,
            player.vip.vipExp,
            len(passList), # 道馆通关数量
            passList, # 已通关道馆ID，json字符串即可
        ), flag=1)


    def packDaylyPVP(self, player):
        self.log2File("playerDaylyPVP", ("%s|"*11).rstrip("|") % (
            player.id,
            player.name,
            player.base.lv,
            player.base.fa,
            player.vip.vipExp,
            player.daylypvp.GetTodayDoChallengeNum(), # 当天发起挑战次数
            player.daylypvp.GetTodayChallengeWinNum(), # 当天击败对手 / 人
            player.daylypvp.GetTodayChallengeMaxWin(),# 当天最高连胜
            player.daylypvp.GetTodayBeChallengeNum(),# 当天被抢次数
            player.daylypvp.GetTodayRevengeWin(),# 当天复仇成功次数
            player.daylypvp.GetLastWeekRank(),# 上周跨服排名名次
        ), flag=1)
        
class LogErrorHandler(logging.Handler):
    appname = ''

    def __init__(self):
        logging.Handler.__init__(self)
        import app
        self.appname = app.name
        self.formatter = logging.Formatter(log.shortformat, log.shortdatefmt)

    def emit(self, record):
        sText =  self.format(record)
        Game.glog.log2File("LogErrorHandler", sText)

def createLogErrorHandler():
    r = LogErrorHandler()
    r.setLevel(ERROR)
    logging.root.addHandler(r)


#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
