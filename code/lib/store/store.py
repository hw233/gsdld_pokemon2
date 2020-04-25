#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from weakref import WeakKeyDictionary

from gevent import sleep, joinall
from gevent.pool import Pool
from gevent.queue import Queue

from corelib import spawn, log
from .driver import get_driver

#排序
ASCENDING = 1
DESCENDING = -1


class StoreObj(object):
    TABLE_NAME = None
    KEY_NAME = 'id'

    @classmethod
    def new_dict(cls, **kw):
        """ 新字典 """
        new = cls()
        new.update(kw)
        return new.to_save_dict()

    @classmethod
    def new_from_list(cls, dict_list, chk_func=None):
        """ 从字典列表创建对象列表 """
        return [cls(adict=d) for d in dict_list if chk_func is None or chk_func(d)]

    def __init__(self, adict=None):
        self.init()
        if adict is not None:
            self.update(adict)
        self.modified = False

    def __getstate__(self):
        return self.to_save_dict()

    def __setstate__(self, data):
        for key, value in data.items():
            setattr(self, key, value)

    def init(self):
        self.id = None

    def modify(self):
        self.modified = True

    def update(self, adict):
        """ 更新 """
        if not adict:
            return
        for k, v in adict.items():
            setattr(self, k, v)
        self.modified = True

    def to_save_dict(self, copy=False, forced=False):
        raise NotImplementedError("StoreObj func to_save_dict not found")

    def copy_from(self, dataobj):
        self.update(dataobj.to_save_dict())

    @classmethod
    def load(cls, store, key, check=False):
        if check and not store.has(cls.TABLE_NAME, key):
            return
        adict = store.load(cls.TABLE_NAME, key)
        if adict:
            obj = cls(adict=adict)
            return obj

    @classmethod
    def load_ex(cls, store, querys):
        alist = store.query_loads(cls.TABLE_NAME, querys)
        if not alist:
            return
        if len(alist) > 1:
            log.error('[StoreObj]load_ex repeat error:%s- querys:%s', cls.TABLE_NAME, querys)
        obj = cls(adict=alist[0])
        return obj

    def save(self, store, forced=False, no_let=False):
        """ 保存 """
        if getattr(self, self.KEY_NAME, None) is None:
            key = store.insert(self.TABLE_NAME, self.to_save_dict())
            setattr(self, self.KEY_NAME, key)
        elif forced or self.modified:
            store.save(self.TABLE_NAME, self.to_save_dict(forced=forced), no_let=no_let)
        self.modified = False

    @classmethod
    def saves(cls, store, objs, filter=None):
        """ 批量保存 """
        news, mods = [], []
        for o in objs:
            if filter is not None and not filter(o):
                continue
            if o.id is None:
                news.append(o)
            elif o.modified:
                mods.append(o.to_save_dict())
        if news:
            map(lambda o: o.save(store), news)
        if mods:
            store.saves(cls.TABLE_NAME, mods)

    def delete(self, store):
        """ 删除 """
        if self.id is None:
            return
        store.delete(self.TABLE_NAME, self.id)


def wrap_get(func):
    """ 包装store，将数据请求转发到store;
    """
    def _func(self, *args, **kw):
        store_func = getattr(self.store, func.func_name)
        return self._get(store_func, *args, **kw)
    _func.obj_func = func
    return _func


class Store(object):
    """ 存储类 """
    STORE_INFOS = None
    INITDBS = tuple()

    def __init__(self):
        if 0:
            from .mongodb import MongoDriver
            self.store = MongoDriver()
        self.store = None
        self.stoped = False

    def init(self, url, **dbkw):
        self.db_name = url.split('/')[-1]
        self.url = url
        self.store = get_driver(url, **dbkw)
        cls_infos = self.STORE_INFOS[self.store.engine_name]
        self._set_lets = WeakKeyDictionary()
        if not self.store.init_cls_infos(cls_infos):
            raise ValueError('store have init!')
        if 0:
            from .mongodb import MongoDriver
            self.store = MongoDriver()

    def start(self):
        pass

    def stop(self):
        """ 停止,必须保证异步的任务已经全部完成 """
        self.stoped = True
        lets = list(self._set_lets.keys())
        joinall(lets)
        log.warning('[store](%s) stop complete!', self.db_name)
        return True

    def _get(self, store_func, *args, **kw):
        """ 包装store，将数据请求转发到store; """
        return store_func(*args, **kw)

    def _set(self, store_func, *args, **kw):
        """ 包装store，将数据请求转发到store; """
        if self.stoped:
            raise ValueError('[store](%s) has stoped!'  % self.db_name)
        let = spawn(store_func, *args, **kw)
        self._set_lets[let] = 0
        return let

    def insert(self, tname, values):
        """ 新增,返回key """
        kn = self.store.get_key(tname)
        kv = self._get(self.store.insert, tname, values)
        return kv

    def inserts(self, tname, values_list):
        """ 批量新增,返回key """
        return self._get(self.store.inserts, tname, values_list)

    def save(self, tname, values, no_let=False):
        """ 保存,values必须包含key """
        if no_let:
            self.store.save(tname, values)
        else:
            self._set(self.store.save, tname, values)

    def saves(self, tname, values_list):
        """ 批量修改 """
        self._set(self.store.saves, tname, values_list)

    def has(self, tname, key):
        return self._get(self.store.has, tname, key)

    def load(self, tname, key):
        return self._get(self.store.load, tname, key)

    def loads(self, tname, keys):
        return [self.load(tname, key) for key in keys]

    def load_all(self, tname, sort_by=None):
        return self.values(tname, None, None, sort_by=sort_by)

    def query_loads(self, tname, querys, limit=0, sort_by=None, skip=0):
        return self.loads(tname, self.store.iter_keys(tname, querys, limit=limit, sort_by=sort_by, skip=skip))

    def load_tables(self, tnames, querys):
        """加载多个表"""
        rs = []
        for tname in tnames:
            rs.append(self.query_loads(tname, querys))
        return rs

    def clear(self, tname):
        self._get(self.store.clear, tname)

    def delete(self, tname, key):
        self._set(self.store.delete, tname, key)

    def deletes(self, tname, keys=None):
        if keys is None:
            self.clear(tname)
            return
        for key in keys:
            self.delete(tname, key)

    def query_deletes(self, tname, querys):
        """ 根据条件，删除一批数据 """
        self.deletes(tname, self.store.iter_keys(tname, querys))

    def update(self, tname, key, values):
        self._set(self.store.update, tname, key, values)

    @wrap_get
    def count(self, tname, querys):
        """ 根据条件，获取结果数量 """
        pass

    def values(self, tname, columns, querys, limit=0, sort_by=None, skip=0):
        """ 根据名称列表，获取表的数据, 返回的是tuple """
        return list(self._get(self.store.iter_values,
            tname, columns, querys, limit=limit, sort_by=sort_by, skip=skip))

    @wrap_get
    def execute(self, statement, params=None):
        """ 高级模式:根据不同后台执行sql或者js(mongodb) """
        pass

    @wrap_get
    def map_reduce(self, tname, map, reduce, out=None, inline=1, full_response=False, **kwargs):
        """ mongodb的map_reduce """
        pass

    def initdb(self, tables=None):
        """ 清除数据库 """
        if tables is None:
            tables = self.INITDBS
        self.store.initdb(tables)

    def dump(self, dump_path):
        """ 备份数据库 """
        pass

    def restore(self, dump_path):
        """ 恢复数据库 """
        pass
