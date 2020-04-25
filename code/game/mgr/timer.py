#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import time
from corelib import log, spawn
from game.define import constant, msg_define, store_define
from corelib.gtime import cur_day_hour_time, current_time, custom_today_ts
from gevent import sleep, Timeout
from game import Game


class Timer(object):
    def __init__(self):
        self.wee_hours = None
        self.half_hour = None
        self.tow_hours = None

    def start(self):
        self.wee_hours = spawn(self.wee_hours_task)
        self.half_hour = spawn(self.half_hour_task)
        self.tow_hours = spawn(self.tow_hours_task)

    def wee_hours_task(self):
        """凌晨定时任务"""
        while 1:
            next_time = cur_day_hour_time(hour=24)
            delay = next_time - current_time()
            if delay > 5 * 60:
                sleep(5 * 60)
            else:
                sleep(delay)
                Game.safe_pub(msg_define.MSG_WEE_HOURS)

    def half_hour_task(self):
        """半小时定时器"""
        next_time = 1800 - int(time.time()) % 1800
        sleep(next_time)

        while 1:
            Game.safe_pub(msg_define.MSG_HALF_HOURS)
            sleep(1800)

    def tow_hours_task(self):
        """两小时定时器"""
        next_time = 7200 - int(time.time()) % 7200
        sleep(next_time)

        while 1:
            Game.safe_pub(msg_define.MSG_TWO_HOURS)
            sleep(7200)
