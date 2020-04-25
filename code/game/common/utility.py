#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import sys
import os
import time
import traceback
import random

from requests import Session
from functools import partial

gtStandardTime = (2018,6,4,0,0,0,0,0,0) # 2018-06-04 00:00:00
giStandardTime = int(time.mktime(gtStandardTime))

def GetMinNo(t=0): #时间戳：分钟序号
    if not t:
        t = int(time.time())
    return int((t-giStandardTime)/60+1)

def GetHourNo(t=0): #时间戳：小时序号
    if not t:
        t = int(time.time())
    return int((t-giStandardTime)/3600+1)

def GetDayNo(t=0): #时间戳：天序号
    if not t:
        t = int(time.time())
    return int((t-giStandardTime)/3600/24+1)

def GetWeekNo(t=0): #时间戳：周序号
    if not t:
        t = int(time.time())
    return int((t-giStandardTime)/3600/24/7+1)

def GetMonthNo(t=0): #时间戳：月序号
    if not t:
        t = int(time.time())
    curTime = time.localtime(t)
    return (curTime[0]-gtStandardTime[0])*12+(curTime[1]-gtStandardTime[1]) +1


def Choice(lRand): #[(id, rate), (id, rate)]
    iTotal = 0
    for one in lRand:
        iTotal += one[1]
    if iTotal <= 0:
        return
    iNum = random.randint(1, iTotal)
    tmp = 0
    for one in lRand:
        tmp += one[1]
        if tmp >= iNum:
            return one[0]

def ChoiceValue(lRand): #[(id, rate, value), (id, rate, value)]
    iTotal = 0
    for one in lRand:
        iTotal += one[1]
    if iTotal <= 0:
        return
    iNum = random.randint(1, iTotal)
    tmp = 0
    for one in lRand:
        tmp += one[1]
        if tmp >= iNum:
            return one[0],one[2]

def ChoiceReturn(lRand): #[(id, rate), (id, rate)]
    iTotal = 0
    for one in lRand:
        iTotal += one[1]
    iNum = random.randint(1, iTotal)
    tmp = 0
    for one in lRand:
        tmp += one[1]
        if tmp >= iNum:
            return one

def ChoiceReturnAll(lRand): #[(rate, ...), (rate, ...)]
    iTotal = 0
    for one in lRand:
        iTotal += one[0]
    iNum = random.randint(1, iTotal)
    tmp = 0
    for one in lRand:
        tmp += one[0]
        if tmp >= iNum:
            return one

class DirtyFlag(object):
    def __init__(self):
        self.dirty = False

    def isDirty(self):
        return self.dirty

    def markDirty(self):
        self.dirty = True

    def cleanDirty(self):
        self.dirty = False

class AsyncRequest(object):
    """ Asynchronous request.

    Accept same parameters as ``Session.request`` and some additional:

    :param session: Session which will do request
    :param callback: Callback called on response.
                     Same as passing ``hooks={'response': callback}``
    """
    def __init__(self, method, url, **kwargs):
        #: Request method
        self.method = method
        #: URL to request
        self.url = url
        #: Associated ``Session``
        self.session = kwargs.pop('session', None)
        if self.session is None:
            self.session = Session()

        callback = kwargs.pop('callback', None)
        if callback:
            kwargs['hooks'] = {'response': callback}

        #: The rest arguments for ``Session.request``
        self.kwargs = kwargs
        #: Resulting ``Response``
        self.response = None

    def send(self, **kwargs):
        """
        Prepares request based on parameter passed to constructor and optional ``kwargs```.
        Then sends request and saves response to :attr:`response`

        :returns: ``Response``
        """
        merged_kwargs = {}
        merged_kwargs.update(self.kwargs)
        merged_kwargs.update(kwargs)
        try:
            self.response = self.session.request(self.method,
                                                self.url, **merged_kwargs)
        except Exception as e:
            self.exception = e
            self.traceback = traceback.format_exc()
        return self

# Shortcuts for creating AsyncRequest with appropriate HTTP method
get = partial(AsyncRequest, 'GET')
options = partial(AsyncRequest, 'OPTIONS')
head = partial(AsyncRequest, 'HEAD')
post = partial(AsyncRequest, 'POST')
put = partial(AsyncRequest, 'PUT')
patch = partial(AsyncRequest, 'PATCH')
delete = partial(AsyncRequest, 'DELETE')


def detailtrace():
  retStr = ""
  curindex=0
  f = sys._getframe()
  f = f.f_back    # first frame is detailtrace, ignore it
  while hasattr(f, "f_code"):
    co = f.f_code
    retStr = "%s(%s:%s)->"%(os.path.basename(co.co_filename),
         co.co_name,
         f.f_lineno) + retStr
    f = f.f_back
  return retStr


def getRandomName(num):
    namelist = [
        "Martin","Wilson","Walker","Lewis","Allen",
        "Taylor","King","Davis","Johnson",
        "Lee","Jackson","Moore","Young","Harris","Ward",
        "Bishop","Harper","Wheeler","Grant","West","Alexander",
        "Scott","Warren","Kevin","Carroll","Rupert","Powell",
        "Hunter","Campbell","Porter","Phillips","Henry",
        "Baker","Oliver","Peterson","Gordon","Carlos",
        "Ray","Nelson","Knight","Franklin",
        "Howard","Murray","Ross","Ford","Murphy","Mitchell","Dunn",
        "Webb","Dick","Sophie","Taylor","Olivia","Isabella","Emma",
        "Mary","Ava","Lee","Natasha","Frederica","Alexander","Jeanne",
        "Larissa","Kelley","Edith","Lilith","Kelly","Sophia","Riley",
        "Jordan","Hunter","Khaleesi","Isla","Harper","Duncan","Rose",
        "Ray","Tami","Samantha","Sofia","Avery","May","Terry","Chloe",
        "Valentine","Arthur","Natalie","Casey","Quinn","Rosa","Joyce","Lora",
        "Ashley","Roxanne","Haley","Whitney","Alison","Christian","Cameron","Blake",
    ]
    resp = []
    for i in range(num):
        one = random.choice(namelist)
        resp.append(one)
        namelist.remove(one)
    return resp

def obj2list(o):
    l=[]
    for k,v in o.items():
        l.append({"k":k,"v":v})
    return l

def list2obj(l):
    o={}
    for v in l:
        o[v["k"]]=v["v"]
    return o


def obj2json(o):
    d={}
    for k,v in o.items():
        d[str(k)] = v
    return d

def json2obj(d):
    o={}
    for k, v in d.items():
        o[int(k)] = v
    return o


def lazy_save_cache(sf,name,save_cache):
    n=getattr(sf,name)

    if n:
        save_cache[name]=n






# def is_UTF_8(str):
#     remain = 0         #剩余byte数
#     for x in range(len(str)):
#         if remain == 0:
#             if (ord(str[x]) & 0x80) == 0x00:
#                 remain = 0
#             elif (ord(str[x]) & 0xE0) == 0xC0:
#                 remain = 1
#             elif (ord(str[x]) & 0xF0) == 0xE0:
#                 remain = 2
#             elif(ord(str[x]) & 0xF8) == 0xF0:
#                 remain = 3
#             else:
#                 return False
#         else:
#             if not ((ord(str[x]) & 0xC0) == 0x80):
#                 return False
#             remain = remain - 1
#     if remain == 0: 	    #最后如果remain不等于零，可能没有匹配完整
#         return True
#     else:
#         return False
















