#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import sys
import datetime
import random
import uuid as uuid_md
import hashlib
import base64

from corelib import log


def import1(name):
    mname, name = name.rsplit('.', 1)
    __import__(mname)
    md = sys.modules[mname]
    return getattr(md, name)


def uuid():
    """ 32位uuid """
    return uuid_md.uuid4().hex


def uninit(obj, name):
    try:
        o = getattr(obj, name)
    except AttributeError:
        return
    try:
        if o is not None and hasattr(o, 'uninit'):
            o.uninit()
    except:
        log.log_except()
    setattr(obj, name, None)

def make_key(name):
    i = random.randint(0, 99999)
    return hashlib.md5('%s-%s' % (name, i)).hexdigest()

def get_md5(name, base64fmt=False, digest=False):
    md5 = hashlib.md5(str(name))
    if digest:
        data = md5.digest()
    else:
        data = md5.hexdigest()
    if base64fmt:
        return base64.encodestring(data)
    return data

def get_token(key, fmt='%y%m%d%H%M'):
    """ 获取管理令牌 """
    d = datetime.datetime.now()
    return hashlib.md5(key + d.strftime('%y%m%d%H%M')).digest()


def copy_attributes(from_object, to_object, names):
    """ 复制属性从一个对象到另外一个对象 """
    for name in names:
        value = getattr(from_object, name)
        setattr(to_object, name, value)


def iter_id_func(start=1, end = sys.maxsize - 1000, loop=True):
    """ 类似itertools.count,不过有最大值限制，如果超过最大值，将返回从start开始 """
    _id = start
    while 1:
        yield _id
        _id += 1
        if _id >= end:
            if loop:
                _id = start
            else:
                raise StopIteration('iter_id function arrive the end(%s) but loop==False' % end)

class IterId(object):
    def __init__(self, start = 1, end = sys.maxsize - 1000, loop = True):
        self.start = start
        self.end = end
        self.loop = loop
        self._cur_id = start

    def next(self):
        if self._cur_id >= self.end:
            if self.loop:
                self._cur_id = self.start
            else:
                raise StopIteration('iter_id function arrive the end(%s) but loop==False' % self.end)
        else:
            self._cur_id += 1
        return self._cur_id

def iter_cls_base(cls):
    """ 只支持单继承或多继承的第一个基类 """
    while cls is not None:
        yield cls
        cls = cls.__base__




#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

