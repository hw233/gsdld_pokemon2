#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import time
import functools

from gevent import (spawn as old_spawn, spawn_later as old_spawn_later,
                    joinall, getcurrent, GreenletExit, sleep)
from gevent.pywsgi import WSGIHandler

from corelib import log

def gevent_monkey():
    """ 修正monkey方法，修正threading过早加载问题，补充部分未考虑到的补丁 """
    global time_sleep
    from gevent import monkey
    import time
    time_sleep = time.sleep
    monkey.patch_all()


class Http10WSGIHandler(WSGIHandler):
    def __init__(self, socket, address, server, rfile=None, timeout=60*5):
        super(Http10WSGIHandler, self).__init__(socket, address, server, rfile=None)
        self.close_task = spawn_later(timeout, self.close_socket)

    def handle_one_response(self):
        try:
            return WSGIHandler.handle_one_response(self)
        finally:
            self.close_connection = True
            self.close_task.kill()
            self.close_task = None

    def close_socket(self):
        from gevent import socket
        if getattr(self, 'socket', None) is not None:
            try:
                log.warning('Http10WSGIHandler %s socket close', self.client_address)
                self.socket._sock.close()
                self.socket.close()
            except socket.error:
                pass

_greenlets = {}
_globals = {}
def reg_global_for_let(global_obj, let=None):
    if let is None:
        let = getcurrent()
    _globals[let] = global_obj

def un_reg_global_for_let(let=None):
    if let is None:
        let = getcurrent()
    _globals.pop(let, None)

def un_reg_global(global_obj, disconnect_func=None):
    items = _globals.items()
    for k, v in items:
        if v == global_obj:
            _globals.pop(k)
            if disconnect_func is not None:
                disconnect_func(k)

def get_global():
    return _globals.get(getcurrent(), None)


def _spawn_enter(obj, func, *args, **kw):
    global _globals, _greenlets
    #防止在game对象stoped后，才运行的微线程启动
    if obj is not None and getattr(obj, 'stoped', False):
        log.error('******global(%s) have stoped, _spawn_enter(%s) no start*****', obj, func)
        return
    cur_let = getcurrent()
    _greenlets[cur_let] = None
    if obj is not None:
        #log.debug('****_spawn_enter.begin:%s-%s-%s', func.func_name, id(cur_let), len(_globals))
        reg_global_for_let(obj, let=cur_let)
    try:
        func(*args, **kw)
    except GreenletExit:
        log.error("[GreenletExit cur_let(%s) obj(%s) func(%s) args(%s) kw(%s)", cur_let, obj, func, args, kw)
    except Exception:
        log.log_except()
    finally:
        un_reg_global_for_let(cur_let)
        _greenlets.pop(cur_let, None)
        #log.debug('****_spawn_enter.finally:%s-%s-%s', func.func_name, id(cur_let), len(_globals))

def spawn(func, *args, **kw):
    obj = get_global()
    let = old_spawn(_spawn_enter, obj, func, *args, **kw)
    return let

def spawn_later(sec, func, *args, **kw):
    obj = get_global()
    let = old_spawn_later(sec, _spawn_enter, obj, func, *args, **kw)
    return let

def spawns(func, argss, timeout=-1):
    """ 启动多个线程，默认会等待,timeout=0不等待 """
    if not argss:
        return
    tasks = []
    for args in argss:
        tasks.append(spawn(func, *args))
    if timeout < 0:
        joinall(tasks)
    elif timeout > 0:
        joinall(tasks, timeout=timeout)
    return tasks
