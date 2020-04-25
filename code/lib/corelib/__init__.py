#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import sys
# if sys.argv[-1] == 'subgame_debug' and 'wingdbstub' not in sys.modules:
#     raise ValueError('wingide mush import before corelib')

try:
    #gevent fix
    from corelib.geventfix import gevent_monkey
    gevent_monkey()

    #exception_fix
    from corelib.exception import exception_fix
    exception_fix()

    #log
    from corelib import log

    #grpc setting
    from grpc import rpc
    rpc.use_logging = True
    rpc.RECONNECT_TIMEOUT = 5
    rpc.HEARTBEAT_TIME = 1 * 60
    rpc.log_except = log.log_except

    #引用
    from corelib.geventfix import spawn_later, spawn, spawns
    from corelib.common import uninit, iter_id_func, get_md5, uuid
    from corelib.gtime import custom_today_ts


except ImportError as e:
    print(str(e))
    import sys
    sys.exit(1)




#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

