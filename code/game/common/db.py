#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from gevent.lock import RLock

from corelib import log
from store.store import Store
from game.define.store_define import *
import config


class GameStore(Store):
    STORE_INFOS = GAME_CLS_INFOS

    def init(self, url, **dbkw):
        self.pool_get_size = dbkw.pop('pool_get_size', 10)
        self.pool_set_size = dbkw.pop('pool_set_size', 10)
        super(GameStore, self).init(url, **dbkw)

def new_game_store():
    #游戏库
    store = GameStore()
    # config.db_params["socketTimeoutMS"] = 10000
    config.db_params["maxIdleTimeMS"] = 10000
    config.db_params["maxPoolSize"] = 10
    store.init(config.db_engine, **config.db_params)
    store.start()
    return store



#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
