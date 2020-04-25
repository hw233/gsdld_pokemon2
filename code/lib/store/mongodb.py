#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os
from os import path

from urllib.parse import urlparse
import functools
import inspect
import glob

from bson.code import Code
from bson import BSON
import pymongo
from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure

from corelib import log
from .driver import MONGODB_ID, DRIVERS
from .errors import ConnectionError

import config
from corelib.frame import Game

pymongo_ver = pymongo.version[0]

#类与表名关系 (tablename, key, indexs, autoInc)
##CLS_INFOS = {
##    #'Player': ('Player', 'uid', [('user_name', {}), ], False)
##}
TAB_IDX = 0
KEY_IDX = 1
AUTO_INC_IDX = 3
PARAMS_IDX = 4
AUTO_INC_TABLE = '_auto_inc_'


def id2_id(obj):
    if isinstance(obj, (list, tuple)):
        return [id2_id(v) for v in obj]
    if isinstance(obj, dict):
        return dict([(id2_id(k), id2_id(v)) for k, v in obj.items()])
    if obj == 'id':
        return '_id'
    return obj


def init_indexs(store, info):
    """ 检查、创建索引 """
    table_name, key, indexs, autoInc = info[:PARAMS_IDX]
    table = store.get_table(table_name)
    for index in indexs:
        if isinstance(index, (tuple, list)):
            key_or_list, kwargs = index
        else:
            key_or_list, kwargs = index, {}
        table.ensure_index(key_or_list, **kwargs)
    #创建自增字段记录
    if autoInc:
        inc = store.get_table(AUTO_INC_TABLE)
        if inc.find_one({'name':table_name}) is None:
            inc.save({'name':table_name, 'id':0})


def auto_inc(store, table_name, count=1):
    """ 获取自增值 """
    inc = store.get_table(AUTO_INC_TABLE)
    v = inc.find_and_modify(query={'name':table_name}, update={'$inc':{'id':count}}, new=True)
    return int(v['id'])


class BaseProc(object):
    @classmethod
    def get_proc(cls, tname):
        return getattr(cls, tname) if hasattr(cls, tname) else cls.simple


class SaveProc(BaseProc):
    """ 保存(新增或者更新) """
    @staticmethod
    def simple(store, tname, values):
        """ 简单保存,保存序列化字典 """
        table_name, key_name = store.cls_infos[tname][:2]
        data = values.copy()
        _id = data.pop(key_name, None)
        if _id is None:
            if not store.cls_infos[tname][AUTO_INC_IDX]:
                raise KeyError
            _id = auto_inc(store, table_name)
            if tname == "player":
                _id = int(str(_id) + config.serverNo)
            values[key_name] = _id
            insert = 1
        else:
            insert = 0
        data['_id'] = _id
        table = store.get_table(table_name)
        if insert:
            Game.glog.log2File("dbOperbefore", "insert|%s|%s" % (table_name, _id))
            rs = table.insert(data, manipulate=False)#, w=1, j=True)
            Game.glog.log2File("dbOper", "insert|%s|%s|%s" % (table_name, rs, data))
            #log.debug('[****%s]%s, result=%s', tname, data, rs)
        else:
            #upsert:if the record(s) do not exist, insert one
            Game.glog.log2File("dbOperbefore", "update|%s|%s" % (table_name, _id))
            table.update({'_id':_id}, data, manipulate=False, upsert=True)#, w=1)
            Game.glog.log2File("dbOper", "update|%s|%s" % (table_name, data))
        return _id

    @staticmethod
    def multi(store, tname, objs, insert):
        """ 批量保存,只支持批量新增或者批量修改,不要混新增和修改 """
        table_name, key_name = store.cls_infos[tname][:2]
        l = len(objs)
        if insert:
            max_id = auto_inc(store, tname, count=l)
            ids = list(range(max_id-l+1, max_id+1).__iter__())

        datas = []
        for i, values in enumerate(objs):
            data = values.copy()
            _id = data.pop(key_name, None)
            if insert:
                _id = ids.next()
                _id = int(str(_id) + config.serverNo)
                values[key_name] = _id
            data['_id'] = _id
            datas.append(data)

        table = store.get_table(table_name)
        if insert:
            return table.insert(datas, manipulate=False)#, w=1, j=True)
        else:
            for d in datas:
                table.update({'_id':d['_id']}, d, manipulate=False, upsert=True)#, w=1)
            return None


class LoadProc(BaseProc):
    """ 加载 """
    @staticmethod
    def init_values(key_name, obj):
        obj[key_name] = obj.pop('_id')
        return obj

    @staticmethod
    def simple(store, tname, key):
        """ 简单加载,加载序列化字典 """
        Game.glog.log2File("dbLoadbefore", "find_one|%s|%s" % (tname, key))
        table_name, key_name = store.cls_infos[tname][:2]
        table = store.get_table(table_name)
        obj = table.find_one(key)
        Game.glog.log2File("dbLoad", "find_one|%s|%s" % (tname, key))
        if not obj:
            return obj
        return LoadProc.init_values(key_name, obj)

    @staticmethod
    def iter_values(store, tname, columns, querys, limit=0, sort_by=None, skip=0):
        """ 根据名称列表，获取表的数据, 返回的是Cursor, [{}, {}, ...] """
        table_name, key_name = store.cls_infos[tname][:2]
        table = store.get_table(table_name)
        querys = store.tran_querys(tname, querys)
        init_values = LoadProc.init_values
        if pymongo_ver == '3':
            rs = table.find(filter=querys, projection=columns, limit=limit, sort=id2_id(sort_by), skip=skip)
        else:
            rs = table.find(spec=querys, fields=columns, limit=limit, sort=id2_id(sort_by), skip=skip)
        for values in rs:
            yield init_values(key_name, values)

    @staticmethod
    def has(store, tname, key):
        """ 判断是否存在 """
        Game.glog.log2File("dbHasbefore", "find|%s|%s" % (tname, key))
        table_name, key_name = store.cls_infos[tname][:2]
        table = store.get_table(table_name)
        c = table.find({'_id':key}).count()
        Game.glog.log2File("dbHas", "find|%s|%s" % (tname, key))
        return c



class DelProc(BaseProc):
    """ 删除 """
    @staticmethod
    def simple(store, tname, key):
        table_name, key_name = store.cls_infos[tname][:2]
        table = store.get_table(table_name)
        table.remove(key)

def wrap_exit(func):
    @functools.wraps(func)
    def _func(self, *args, **kw):
        self.__enter__()
        try:
            return func(self, *args, **kw)
        except ConnectionFailure as e:
            log.log_except('args(%s) kw(%s)', args, kw)
            raise ConnectionError(str(e))
        except Exception as e:
            log.log_except('args(%s) kw(%s)', args, kw)
        finally:
            self.__exit__()
    _func.store = 1 #标示是数据库操作接口
    args = inspect.getargspec(func)
    if len(args.args) > 1 and args.args[1] == 'tname':
        _func.tname = 1
    return _func


class MongoDriver(object):
    engine_name = MONGODB_ID

    def __init__(self):
        if 0:
            from pymongo import database
            self._conn = pymongo.MongoClient()
            self._db = database.Database()
        self._conn = None
        self._db = None
        self.cls_infos = None
        self.url = None
        self.dbkw = None
        self.tables = {}

    def init_cls_infos(self, cls_infos):
        if self.cls_infos == cls_infos:
            return True
        if self.cls_infos is not None:
            return False
        self.tables.clear()
        self.cls_infos = cls_infos
        with self:
            for k, info in self.cls_infos.items():
                try:
                    init_indexs(self, info)
                except:
                    log.log_except('info:%s', info)
                    raise
        return True

    def init(self, url, **dbkw):
        """
         url: mongodb://jhy:123456@192.168.0.110/jhy
        """
        assert self._conn is None, 'already had server'
        self.url = url
        self.dbkw = dbkw
        self.timeout = dbkw.get('timeout', None)
        urler = urlparse(url)
        try:

            params = {} if pymongo_ver == '3' else dict(use_greenlets=True)
            params.update(self.dbkw)
            if self.timeout:
                params['socketTimeoutMS'] = self.timeout * 1000
            # self._conn = pymongo.MongoClient(url, **params)
            # dbname = urler.path[1:]
            # 先登录admin数据库 再切换
            pre, dbname = url.rsplit('/', 1)
            self._conn = pymongo.MongoClient('%s/admin' % pre, **params)
            self._db = getattr(self._conn, dbname)
            if urler.username:
                self.username = urler.username
                self.pwd = urler.password
        except pymongo.errors.AutoReconnect:
            log.error('连接mongoDB(%s:%s)失败', urler.hostname, urler.port)
            raise

    def __enter__(self):
        """  """
        return self

    def __exit__(self, *args):
        if pymongo_ver != '3':
            self._conn.end_request()

    def create(self, db_engine, dbkw):
        """ 创建数据库 """
        #先登录admin数据库,再进行创建操作
        admin = MongoDriver()
        pre, name = db_engine.rsplit('/', 1)
        admin.init('%s/admin' % pre, **dbkw)
        db = getattr(admin._conn, name)
        db.add_user(admin.username, admin.pwd, read_only=False)

    def initdb(self, tables):
        """ 清除数据库 """
        tables = set(tables)
        with self:
            for tname in tables:
                table = self.get_table(self.cls_infos[tname][TAB_IDX])
                table.drop()

    @classmethod
    def register(cls):
        """ 注册到store中 """
        DRIVERS[MONGODB_ID] = cls

    def get_table(self, item):
        """ 返回pymongo.Collection对象 """
        try:
            return self.tables[item]
        except KeyError:
            self.tables[item] = Collection(self._db, item)
            return self.tables[item]

    def get_key(self, tname):
        """ 获取key字段名 """
        return self.cls_infos[tname][KEY_IDX]

    def tran_querys(self, tname, querys):
        if not querys:
            return
        key = self.get_key(tname)
        if key in querys:
            querys['_id'] = querys.pop(key)
        return querys

    def iter_values(self, tname, columns, querys, limit=0, sort_by=None, skip=0):
        """ 根据名称列表，获取表的数据, 返回的是Cursor, [{}, {}, ...] """
        return LoadProc.iter_values(self, tname, columns, querys, limit=limit, sort_by=id2_id(sort_by), skip=skip)

    def iter_keys(self, tname, querys, limit=0, sort_by=None, skip=0):
        """
          - `sort` (optional): a list of (key, direction) pairs
            specifying the sort order for this query. See
            :meth:`~pymongo.cursor.Cursor.sort` for details.
        """
        key = self.get_key(tname)
        for v in LoadProc.iter_values(self, tname, [], querys, limit=limit, sort_by=id2_id(sort_by), skip=skip):
            yield v[key]

    @wrap_exit
    def save(self, tname, values):
        func = SaveProc.get_proc(tname)
        return func(self, tname, values)

    insert = save

    @wrap_exit
    def saves(self, tname, values_list):
        """ 批量保存,values必须包含key """
        return SaveProc.multi(self, tname, values_list, 0)

    @wrap_exit
    def inserts(self, tname, values_list):
        """ 批量新增,values必须包含key """
        return SaveProc.multi(self, tname, values_list, 1)

    @wrap_exit
    def has(self, tname, key):
        return LoadProc.has(self, tname, key)

    @wrap_exit
    def load(self, tname, key):
        func = LoadProc.get_proc(tname)
        return func(self, tname, key)

    @wrap_exit
    def delete(self, tname, key):
        if key is None:#防止清除所有数据
            return
        func = DelProc.get_proc(tname)
        return func(self, tname, key)

    @wrap_exit
    def clear(self, tname):
        """ 清除所有数据 """
        table = self.get_table(self.cls_infos[tname][TAB_IDX])
        table.remove()

    @wrap_exit
    def update(self, tname, key, values):
        """ 更新部分数据 """
        if key is None:
            raise ValueError('update error:(%s, %s, %s)' % (tname, key, values))
        table = self.get_table(self.cls_infos[tname][TAB_IDX])
        table.update({"_id": key}, {"$set": values})

    @wrap_exit
    def count(self, tname, querys):
        """ 根据条件，获取结果数量 """
        querys = self.tran_querys(tname, querys)
        table = self.get_table(self.cls_infos[tname][TAB_IDX])
        return table.find(spec=querys).count()

    @wrap_exit
    def execute(self, statement, params=None):
        return self._db.eval(statement, *params)

    @wrap_exit
    def map_reduce(self, tname, map, reduce, out=None, inline=1, full_response=False, **kwargs):
        table = self.get_table(self.cls_infos[tname][TAB_IDX])
        if inline:
            return table.inline_map_reduce(map, reduce, full_response=full_response, **kwargs)
        assert out is not None, ValueError('out mush not None if not inline')
        return table.map_reduce(map, reduce, out, full_response=full_response, **kwargs)

    def dump(self, dump_path):
        """ 备份数据库 """
        # print('mongodb dump')
        if not path.exists(dump_path):
            os.mkdir(dump_path)
        names = self._db.collection_names()
        print(names)
        for n in names:
            if n.startswith('system.'):
                continue
            table_name = path.join(dump_path, n)
            print('table:' + n)
            table = self.get_table(n)
            docs = [doc for doc in table.find()]
            indexs = table.index_information()
            d = BSON.encode(dict(data=docs, indexs=indexs))
            with open(table_name, 'wb') as f:
                f.write(d)

    def restore(self, dump_path, exclude=None):
        """ 恢复数据库 """
        for fp in glob.glob(path.join(dump_path, '*')):
            n = path.basename(fp)
            if exclude and n in exclude:
                continue
            with open(fp, 'rb') as f:
                d = BSON(f.read()).decode()
            table = self.get_table(n)
            table.drop()
            docs = d['data']
            if docs:
                table.insert(docs)
                print('resotre:'+n)


MongoDriver.register()

copy_collection = u"""
function (){
    db.getCollection('%s').find().forEach(function (x){db.getCollection('%s').insert(x)});
}
"""

sum_map = Code(
u"""
function (){
    b = this.value.damage != null
    tb = db.getCollection('setting.logon.telcom-广东区-八月十五.players')
    f = tb.find({'_id':this._id})
    if (b && f.count() != 0) {
        r = f.next();
        emit(this._id, {'value':this.value, 'chl_name':r.value.chl_name});
    } else {
        emit('', '');
    }
}
""")

sum_reduce = Code(
u"""
function (key, emits){
    return emits[0];
}
""")



