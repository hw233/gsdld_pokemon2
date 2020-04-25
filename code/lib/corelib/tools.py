#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os, sys
import time
import socket
import urllib
from functools import partial, wraps

from gevent import sleep

from corelib import spawn_later, spawn
from corelib import log


class Timer(object):
    def __init__(self, verbose=False):
        self.verbose = verbose

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        self.end = time.time()
        self.secs = self.end - self.start
        self.msecs = self.secs * 1000  # millisecs
        if self.verbose:
            log.info('elapsed time: %f ms', self.msecs)

def analyze_mem():
    """ 内存分析 """
    import gc, sys
    d = {}
    objects = gc.get_objects()
    print('gc objects size:', len(objects))
    for o in objects:
        o_type = type(o)
        if o_type in d:
            data = d[o_type]
        else:
            data = [0, 0, sys.getsizeof(0)]
        data[0] += 1
        data[1] += data[2]
        d[o_type] = data
    lmem = [[v, k] for k, v in d.items()]
    lmem.sort()

    return lmem, d


def get_quit_players():
    from game.player import Player
    refs = Player._wrefs
    return [p for p in refs.values() if p.quited]

def froot(id, roots=None, rels=None):
    if roots is None:
        roots = []
        rels = []
    if isinstance(id, int):
        obj = fo1(id)
    else:
        obj = id
    if obj in rels or obj in roots:
        return
    rels.append(obj)
    for p in fp1(id):
        pid = p.address
        if p in rels or p in roots:
            continue
        if p.num_parents == 0:
            roots.append(p)
            continue
        froot(p.address, roots, rels)
    return roots#, rels

def meliae_dump(file_path):
    """ 内存分析
辅助函数：
objs = om.objs
ft=lambda tname: [o for o in objs.values() if o.type_str == tname]
fp=lambda id: [objs.get(rid) for rid in objs.get(id).parents]
fr=lambda id: [objs.get(rid) for rid in objs.get(id).children]
#exec 'def fp1(id):\n obj = fo1(id)\n return fp(obj)'
exec 'def fps(obj, rs=None):\n    if rs is None:\n        rs = []\n    if len(rs) > 2000:\n        return rs\n    if obj is not None and obj not in rs:\n        rs.append(obj)\n        for p in fr(obj):\n            fps(p, rs=rs)\n    return rs'
exec 'def fps1(obj, rs=None):\n    if rs is None:\n        rs = []\n    if len(rs) > 2000:\n        return rs\n    if obj is not None and obj not in rs:\n        if obj.num_parents == 0:\n                rs.append(obj)\n        for p in fp(obj):\n            fps(p, rs=rs)\n    return rs'
fo=lambda id: objs.get(id)

运行时辅助：
import gc
get_objs = lambda :dict([(id(o), o) for o in gc.get_objects()])
fid = lambda oid: [o for o in gc.get_objects() if (id(o) == oid)]
fr = lambda o: gc.get_referents(o)
fp = lambda o: gc.get_referrers(o)
"""
    import gc
    gc.collect()
    from meliae import scanner
    scanner.dump_all_objects(file_path)

def profile(duration=60, profile=None, trace_obj=None):
    """ 性能分析 """
    import os
    from . import gevent_profiler, common

    if gevent_profiler._attach_expiration is not None:
        return False, 'profile has running!\n'

    start_time = common.strftime('%y%m%d-%H%M%S')
    if profile is None:
        save_path = os.path.join(os.environ['ROOT_PATH'], 'log')
        profile = os.path.join(save_path, 'profile-%s.profile' % start_time)
    gevent_profiler.set_summary_output(profile)
    gevent_profiler._attach_duration = duration

    if trace_obj:
        gevent_profiler.set_trace_output(trace_obj)
        gevent_profiler.enable_trace_output(True)
    else:
        gevent_profiler.set_trace_output(None)
        gevent_profiler.enable_trace_output(False)

    gevent_profiler.attach()
    return True, 'profile start:%s\n' % start_time


_dead_checker = None

def start_dead_check():
    global _dead_checker
    if _dead_checker:
        return True
    _dead_checker = DeadChecker()
    _dead_checker.start()
    return True

class DeadCheckError(Exception):
    pass

class DeadChecker(object):
    """ 进程挂起的检查类 """
    DEAD_TIME = 60
    def __init__(self):
        self._hb_task = None


    def start(self):
        self._hb_time = time.time()
        sys.settrace(self._globaltrace)
        self._hb_task = spawn(self._heartbeat)


    def _heartbeat(self):
        while True:
            self._hb_time = time.time()
            sleep(1)

    def _globaltrace(self, frame, event, arg):
        return self._localtrace

    def _localtrace(self, frame, event, arg):
        if time.time() - self._hb_time > self.DEAD_TIME:
            log.log_stack('dead check')
            raise DeadCheckError
        return self._localtrace


########################
########################

