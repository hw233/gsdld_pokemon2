#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import time

from gevent import sleep

from corelib import log, spawn

class TimeMemCache(object):
    """ 缓存，使用过期式gc """
    gc_time = 10 #最小间隔
    gc_max_time = 30 #定时清理时间
    def __init__(self, size=100, default_timeout=30, name=''):
        self.name = name
        self.size = size
        self._caches = {}
        self._times = {}
        self._gc_time = 0
        self._gcing = False
        self.default_timeout = default_timeout
        self.total = self.hit = self.miss = 0

    def __str__(self):
        return '%s(name=%s, size=%d)' % (self.__class__.__name__, self.name, len(self._caches))

    def update(self, kw, timeout=None):
        for k, v in kw.items():
            self.set(k, v, timeout = timeout)

    def clear(self):
        self._caches.clear()
        self._times.clear()
        self._gc_time = 0
        self.total = self.hit = self.miss = 0

    def set(self, key, value, timeout=None):
        """ timeout:过期时间(单位秒),如果为0，不过期 """
        if timeout is None or timeout < 0:
            timeout = self.default_timeout
        if timeout > 0:
            timeout = time.time() + abs(timeout)
            self._times[key] = timeout
        self._caches[key] = (value, timeout)
        if len(self._caches) > self.size and \
            self._gc_time + self.gc_time < time.time():
            log.warning('TimeMemCache缓存(%s-%s)不足，开始清理缓存', self.name, len(self._caches))
            spawn(self.gc)
            #sleep(0.01)
        return value

    def _gc_simple(self, times):
        times.sort()
        cur_time = time.time()
        for time_key in times:
            if time_key[0] > cur_time:
                break
            self._caches.pop(time_key[1], None)
            self._times.pop(time_key[1], None)

    def _gc_big(self):
        """ 大数据优化 """
        slice_count = 200
        keys = list(self._times.keys())
        while keys:
            sub_keys, keys = keys[:slice_count], keys[slice_count:]
            times = [(self._times[key], key) for key in sub_keys if key in self._times]
            self._gc_simple(times)
            sleep(0.02)

    def gc(self):
        if self._gcing:
            return
        if self._gc_time + self.gc_time > time.time():
            return
        self._gcing = True
        try:
            self._gc_time = time.time()
            count = len(self._caches)
            if count <= 500:
                times = [(timeout, key) for key, timeout in self._times.items()]
                self._gc_simple(times)
            else:
                self._gc_big()
        finally:
            self._gcing = False

    def get(self, key, default=None, add_time = None):
        """  """
        if self._gc_time + self.gc_max_time < time.time():
#            log.debug('TimeMemCache(%s)缓存(%s)定时清理',
#                    self.name, len(self._caches))
            #定时清理
            spawn(self.gc)

        self.total += 1
        try:
            cache = self._caches[key]
        except KeyError:
            self.miss += 1
            return default
        timeout = cache[1]
        if add_time:
            value = cache[0]
            self.set(key, value, add_time)
        if timeout and time.time() >= timeout:
            self.delete(key)
            return default
        self.hit += 1
        return cache[0]

    def delete(self, key):
        rs = self._caches.pop(key, None)
        self._times.pop(key, None)
        return rs[0] if rs else None




