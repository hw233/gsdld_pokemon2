#!/usr/bin/env python3
# -*- coding:utf-8 -*-


#排序定义
ASCENDING = 1  # 升序
DESCENDING = -1  # 降序

#查询逻辑定义
OP_AND = '$and'
OP_OR = '$or'
OP_NOT = '$not'
OP_NOR = '$nor'

#字段操作定义
FOP_IN = '$in'
FOP_GT = '$gt'
FOP_LT = '$lt'
FOP_GTE = '$gte'
FOP_LTE = '$lte'
FOP_NE = '$ne'
FOP_NIN = '$nin'

#bool值
INT_TRUE = 1
INT_FALSE = 0

DRIVERS = {}
_drivers = {}
MONGODB_ID = 'mongodb'


def get_driver(db_engine, **dbkw):
    global _drivers
    if db_engine in _drivers:
        return _drivers[db_engine]
    _create = dbkw.pop('create_db', False)
    if db_engine.startswith("%s://" % MONGODB_ID):
        from . import mongodb #导入模块
        cls = DRIVERS[MONGODB_ID]
        store = cls()
        if _create:
            store.create(db_engine, dbkw)
        store.init(db_engine, **dbkw)
    else:
        raise ValueError('db_engine(%s) not found' % db_engine)
    _drivers[db_engine] = store
    return store

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
