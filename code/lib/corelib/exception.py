#!/usr/bin/env python3
# -*- coding:utf-8 -*-

def exception_fix():
    """ 修正异常的继承 """
    try:
        import bson
        bson.errors.BSONError.__bases__ = (Exception, )
        from pymongo import errors as mongo_errors
        mongo_errors.PyMongoError.__bases__ = (Exception, )
    except ImportError:
        pass

class GameError(Exception): pass