#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from copy import copy
from collections import defaultdict as dd
from collections import Hashable
from functools import partial

import grpc
from corelib import log

__all__ = [
        'Broker',
        'sub',
        'unsub',
        'pub',
        'declare',
        'retract',
        'get_declarations',
        'has_declaration',
        ]


class Broker(object):
    def __init__(self):
        self.safe_type = True
        self._router = dd(list)
#        self._board = {}

    def clear(self):
        self._router.clear()

    def sub(self, topic, func, data=None, front = False):
        assert isinstance(topic, Hashable)
        assert callable(func) or hasattr(func, '__call__')
        key = (func, data)
        if key in self._router[topic]:
            return
        if front:
            self._router[topic].insert(0, key)
        else:
            self._router[topic].append(key)
#        if topic in self._board:
#            a, kw = self._board[topic]
#            func(*a, **kw)

    def unsub(self, topic, func, data=None):
        assert isinstance(topic, Hashable)
        assert callable(func) or hasattr(func, '__call__')
        if topic not in self._router:
            return
        try:
            self._router[topic].remove((func, data))
        except ValueError:
            if len(self._router[topic]) > 100:
                log.warning('Broker.unsub(%s, %s) may remove error!!!', self, topic)
            pass

    def has_sub(self, topic):
        return topic in self._router and self._router[topic]

    def pub(self, topic, *a, **kw):
        assert isinstance(topic, Hashable)
        if topic not in self._router:
            return
        key_data = '_data'
        removed = []
        for func, data in copy(self._router[topic]):
            if func:
                try:
                    if data:
                        kw[key_data] = data
                        try:
                            func(*a, **kw)
                        finally:
                            kw.pop(key_data)
                    else:
                        func(*a, **kw)
                except Exception as err:
                    rs = self._except_fix(func, err)
                    if rs == 0:
                        raise
                    elif rs == -1:
                        removed.append((func, data))
            else:
                removed.append((func, data))
        for i in removed:
            try:
                self._router[topic].remove(i)
            except ValueError:
                pass

    def _except_fix(self, func, err):
        """
        @result:
            1: ok,错误处理
            0: 未处理
            -1: 移除

        """
        if isinstance(func, grpc.RpcProxy):
            return -1
        if self.safe_type:  # 安全模式,
            log.log_except()
            return 1
        return 0


def observable(cls, is_cls=False):
    t = cls.__init__

    def __init__(self, *a, **kw):
        self._message_broker = Broker()
        t(self, *a, **kw)

    def clear(self):
        self._message_broker.clear()
    cls_clear = classmethod(clear)

    def sub(self, *a, **kw):
        self._message_broker.sub(*a, **kw)
    cls_sub = classmethod(sub)

    def rpc_sub(self, func, topic, *a, **kw):
        kw.pop('_pickle', None)
        kw.pop('_proxy', None)
        self._message_broker.sub(topic, func, *a, **kw)
    cls_rpc_sub = classmethod(rpc_sub)

    def rpc_unsub(self, func, topic, data=None, _proxy=True):
        self._message_broker.unsub(topic, func, data=data)
    cls_rpc_unsub = classmethod(rpc_unsub)

    def unsub(self, *a, **kw):
        self._message_broker.unsub(*a, **kw)
    cls_unsub = classmethod(unsub)

    def pub(self, *a, **kw):
        self._message_broker.pub(*a, **kw)
    cls_pub = classmethod(pub)

    def safe_pub(self, *a, **kw):
        try:
            self._message_broker.pub(*a, **kw)
        except Exception:
            log.log_except()
    cls_safe_pub = classmethod(safe_pub)

    def has_sub(self, *a, **kw):
        return self._message_broker.has_sub(*a, **kw)
    cls_has_sub = classmethod(has_sub)

#    def declare(self, *a, **kw):
#        self._message_broker.declare(*a, **kw)
#
#    def retract(self, *a, **kw):
#        self._message_broker.retract(*a, **kw)
#
#    def get_declarations(self, *a, **kw):
#        self._message_broker.get_declarations(*a, **kw)
#
#    def has_declaration(self, *a, **kw):
#        self._message_broker.has_declaration(*a, **kw)

    if is_cls:
        cls._message_broker = Broker()
        cls.message_clear = cls_clear
        cls.sub = cls_sub
        cls.rpc_sub = cls_rpc_sub
        cls.rpc_unsub = cls_rpc_unsub
        cls.unsub = cls_unsub
        cls.pub = cls_pub
        cls.safe_pub = cls_safe_pub
        cls.has_sub = cls_has_sub
    else:
        setattr(cls, '__init__', __init__)
        for k, v in dict(
                message_clear = clear,
                sub = sub,
                rpc_sub=rpc_sub,
                rpc_unsub=rpc_unsub,
                unsub = unsub,
                pub = pub,
                safe_pub = safe_pub,
                has_sub = has_sub,
                #declare = declare,
                #retract = retract,
                #get_declarations = get_declarations,
                #has_declaration = has_declaration,
                ).items():
            assert not hasattr(cls, k)
            setattr(cls, k, v)
    return cls

observable_cls = partial(observable, is_cls=True)

_broker = Broker()
sub = _broker.sub
unsub = _broker.unsub
pub = _broker.pub
#declare = _broker.declare
#retract = _broker.retract
#get_declarations = _broker.get_declarations
#has_declaration = _broker.has_declaration

if __name__ == '__main__':
    def greet(name):
        print('hello, %s.'%name)

    sub('greet', greet)
    pub('greet', 'lai')
    pub('greet', 'smallfish')
    pub('greet', 'guido')
    unsub('greet', greet)
    unsub('not existed', greet)
    pub('greet', 'world')
    print('*' * 30)
    sub('greet', greet)
#    declare('greet', 'world')
#    assert get_declarations()

    def greet2(name):
        print('hello, %s. greet2'%name)

    sub('greet', greet2)

    pub('greet', 'spring')

#    retract('greet')

    def greet3(name):
        print('hello, %s. greet3'%name)

    sub('greet', greet3)

    print('*' * 30)
    def greet4(name):
        print('hello, %s. greet4'%name)
        unsub('greet', greet4)
    sub('greet', greet4, front = True)
    pub('greet', 'lv')
    pub('greet', 'ma')

    print('*' * 30)
    class Foo(object):
        def foo(self, ctx, name):
            print('Foo.foo, hello %s.'%name)

    foo = Foo()
    sub('lai', foo.foo)
    pub('lai', 'lai')

