#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import time
import weakref
import datetime
import functools

from gevent.event import Event
from gevent import  GreenletExit

from corelib import log
from corelib import spawn

now = datetime.datetime.now
timedelta = datetime.timedelta
date = datetime.date

import calendar

def time2date(t):
    return datetime.datetime.fromtimestamp(t)

def date2time(d):
    return time.mktime(d.timetuple())


def str2time(reabletime, fmt='%Y-%m-%d %H:%M:%S'):
    return int(time.mktime(time.strptime(reabletime, fmt)))


def time2str(t):
    d = datetime.datetime.fromtimestamp(t)
    return d.strftime('%Y-%m-%d %H:%M:%S')

def getDD():
    return datetime.datetime.today().strftime('%d')
def getMM():
    return datetime.datetime.today().strftime('%m')


def getYYYYMMDDbyT(t):
    d = datetime.datetime.fromtimestamp(t)
    return d.strftime('%Y%m%d')

def getYYYYMMDD():
    return datetime.datetime.today().strftime('%Y%m%d')

def getMMslashDD():
    return datetime.datetime.today().strftime('%m/%d')

def getYesterdayYYYYMMDD():
    yesterday = date.today() - timedelta(1)
    return yesterday.strftime('%Y%m%d')


def getIntArrayYYYYMMDD(days,startday=0):
    if startday==0:
        startday=int(date.today().strftime('%Y%m%d'))
    else:
        t = datetime.datetime.strptime(str(startday), '%Y%m%d')
        tt =  t + timedelta(1)
        startday = int(tt.strftime('%Y%m%d'))

    ss = str(startday)

    st = datetime.datetime.strptime(ss, '%Y%m%d')

    retv = []
    for i in range(days):
        x = st + timedelta(i)
        retv.append(int(x.strftime('%Y%m%d')))
    
    return retv

def getZeroTime(ts):
   return int(time.mktime(datetime.date.fromtimestamp(ts).timetuple()))

def parse_time(tstr, fmt):
    start, end = tstr.split(":")
    start = strptime(start, fmt)
    end = strptime(end, fmt)
    return start, end


def strftime(fmt='%Y-%m-%d %H:%M:%S', dtime=None):
    """ 获取时间字符串,dt参数是时间对象，如果为None，返回当前时间字符串 """
    if dtime is None:
        dtime = datetime.datetime.now()
    return dtime.strftime(fmt)


def strptime(stime, fmt='%Y-%m-%d %H:%M:%S'):
    """ 根据时间字符串，返回时间对象 """
    return datetime.datetime.strptime(stime, fmt)


def custom_today_time(timestr):
    """ 返回今天的指定时间 """
    time_local = time.localtime(time.time())
    dt = time.strftime("%Y-%m-%d", time_local)

    t = time.strptime(dt+" "+timestr, "%Y-%m-%d %H:%M:%S")
    return int(time.mktime(t))


def custom_today(hour=0, minute=0, second=0, days=0):
    """ 返回今天的指定时间 """
    n = datetime.datetime.now()
    return datetime.datetime(n.year, n.month, n.day + days, hour, minute, second)

def custom_today_ts(hour=0, minute=0, second=0):
    dt = custom_today(hour, minute, second)
    return int(time.mktime(dt.timetuple()))

def zero_day_time():
    """ 今天早上凌晨0点time """
    return int(time.mktime(now().date().timetuple()))


def cur_day_hour_time(hour=0):
    """
    今日的几点时间
    """
    z_t = zero_day_time()
    return z_t + 3600 * hour


def week_time(weekday, zero=1, delta=0):
    """ 根据指定的周几(week_day 1~7),返回本星期的具体时间,
    zero: 1 返回早上凌晨0点的time
    delta: 延迟周数
    """
    if zero:
        n = now().date()
    else:
        n = now()
    from game.define.constant import ONE_DAY_DELTA
    d = n + ONE_DAY_DELTA * ((weekday - 1 - n.weekday()) + 7 * delta)
    return time.mktime(d.timetuple())


def is_pass_day(aTime):
    """ 判断时间是否已过(超过凌晨十二点) """
    zero_time = time.mktime(now().date().timetuple())
    return aTime < zero_time


def is_pass_day_time(aTime):
    """ 判断时间是否是下一天(超过凌晨12点) """
    zero_time = time.mktime(now().date().timetuple()) + 86400
    return aTime >= zero_time


def current_time():
    """ 得到当前时间int形式 """
    return int(time.time())


def is_today(aTime):
    """判断时间是否当天"""
    now_zero = time.mktime(now().date().timetuple())
    next_zero = now_zero + 86400
    return now_zero <= aTime < next_zero


def is_yesterday(aTime):
    """判断时间是否昨天"""
    now_zero = time.mktime(now().date().timetuple())
    yt_zero = now_zero - 86400
    return yt_zero <= aTime < now_zero


def get_days(aTime):
    """ aTime距离今天相多少天 """
    now_zero = time.mktime(now().date().timetuple())
    if now_zero < aTime:
        return 0
    passday = int((now_zero - aTime)/86400)

    if (now_zero - aTime)%86400:
        passday += 1
    return passday

def current_hour():
    """ 获取当前小时 """
    n = datetime.datetime.now()
    return n.hour

def getNextMonday():
    """ 获取下周一 0点 时间戳 """
    today = datetime.date.today()
    oneday = datetime.timedelta(days = 1)
    m1 = calendar.MONDAY
    while today.weekday() != m1:
        today += oneday
    d = today.strftime('%Y/%m/%d')
    return time.mktime(datetime.datetime.strptime(d, "%Y/%m/%d").timetuple())

def getNextMonthFirstDay():
    """ 获取下月第一天 0点 时间戳 """
    days_in_month = lambda dt: calendar.monthrange(dt.year, dt.month)[1]
    today = date.today()
    nm = today.replace(day=1) + timedelta(days_in_month(today))
    d = nm.strftime('%Y/%m/%d')
    return time.mktime(datetime.datetime.strptime(d, "%Y/%m/%d").timetuple())

class TimerSet(object):
    """ 定时触发事件的管理类
    注意：每个小逻辑功能内部尽量不能做io，否则会影响其它功能
    用处：
        针对大量需要定时执行小量逻辑的功能，
            如：回血，回气，buff
        小逻辑功能，必须是使用yield方式实现的函数、方法，
            或者支持yield相关方法的对象
            next(): 第一次调用，返回下一次触发时间
            send(经过的时间):返回下一次触发时间
        备注：
            时间使用毫秒，
            如果需要停止，抛出StopIteration

        yield函数例子：
    def _test1():
        #间隔时间
        i_time = 500.0
        pass_time = i_time
        while 1:
            s_time = (i_time + i_time - pass_time)
            if s_time < 0:
                s_time = i_time
            pass_time = yield s_time
            #pass_time是从上一次到这次执行过去的时间
            #下面可以执行具体的逻辑

    """
    default_wait = 2 * 60
    max_seconds = 3600 * 24 * 100 #最大秒数
    max_error = 'TimerSet error: seconds(%%s) > max(%s)' % max_seconds
    def __init__(self, owner):
        if 0:
            self._pause_waiter = Event()
        self._loop_task = None
        self._timers = []
        self._yields = []
        self._waiter = Event()
        self._pause_waiter = None
        self.owner = weakref.ref(owner)

    def register(self, yield_func):
        self._yields.append(yield_func)
        self._waiter.set()

    def unregister(self, yield_func):
        if yield_func in self._yields:
            self._yields.remove(yield_func)
            return
        for index, (times, yfunc) in enumerate(self._timers):
            if yfunc == yield_func:
                self._timers.pop(index)
                return

    def update_later(self, yield_func, seconds):
        """ 更新某yield_func的调用时间，常配合call_later使用 """
        if yield_func in self._yields:
            return True
        for value in self._timers:
            times, yfunc = value
            if yfunc == yield_func:
                self._timers.remove(value)
                times = time.time() + seconds
                self._timers.append((times, yfunc))
                self._timers.sort()
                return True
        return False

    def call_later(self, seconds, func, *args, **kw):
        """ 延迟一段时间调用某函数，只调用一次 """
        #回调的时间太长啦
        if seconds > self.max_seconds:
            raise ValueError(self.max_error % seconds)
        @functools.wraps(func)
        def _yield_func():
            yield seconds * 1000.0
            try:
                spawn(func, *args, **kw)
            except Exception:
                log.log_except()
        yfunc = _yield_func()
        self.register(yfunc)
        return yfunc

    def call_loop(self, seconds, func, *args, **kw):
        """ 延迟一段时间循环调用某函数，持续调用,直到函数返回False """
        @functools.wraps(func)
        def _yield_func():
            params = [1, 0] #[是否结束, 是否正在执行]
            i_time = seconds * 1000.0 #1秒
            @functools.wraps(func)
            def _myfunc():
                try:
                    rs = func(*args, **kw)
                    params[0] = rs
                except Exception:
                    log.log_except()
                    params[0] = 0
                finally:
                    params[1] = 0

            while params[0]:
                yield i_time
                #回调的时间太长啦
                if seconds > self.max_seconds:
                    raise ValueError(self.max_error % seconds + ':func=%s' % func)
                    #启用微线程跑，防止阻塞本线程, _calling用于防止重复进入
                if params[0] and not params[1]:
                    params[1] = 1
                    spawn(_myfunc)
        yfunc = _yield_func()
        self.register(yfunc)
        return yfunc


    def empty(self):
        return not (len(self._timers) or len(self._yields))

    @property
    def stoped(self):
        return self._loop_task is None

    @property
    def owner_stoped(self):
        return self.owner() is None or\
               getattr(self.owner(), 'stoped', False)

    def start(self):
        if self.stoped:
            self._loop_task = spawn(self._loop)

    def stop(self):
        if not self.stoped:
            self._loop_task.kill(block=False)
            self._loop_task = None
            self._waiter.set()

    def clear(self):
        self._timers = []
        self._yields = []
        self._waiter.set()
        self.stop()

    def pause(self):
        if self._pause_waiter is None:
            self._pause_waiter = Event()
        self._pause_waiter.clear()

    def resume(self):
        if self._pause_waiter is None or self._pause_waiter.is_set():
            return
        self._pause_waiter.set()

    def _loop(self):
        while not (self.stoped or self.owner_stoped):
            if self._pause_waiter is not None:
                self._pause_waiter.wait(timeout=self.default_wait)

            cur_time = int(time.time() * 1000.0)
            #触发
            while len(self._timers):
                if self._timers[0][0] <= cur_time:
                    timer = self._timers.pop(0)
                    try:
                        next_time = timer[1].send(0) + cur_time
                        if next_time > cur_time:
                            #log.debug('****append:%s, %s', timer, next_time)
                            self._timers.append((next_time, timer[1]))
                        else:
                            raise ValueError('yield(%s) error: next_time <= cur_time' % str(timer[1]))
                    except StopIteration:
                        pass
                    except GreenletExit:
                        return
                    except Exception as e:
                        log.error('timer(%s) error:%s', timer[1], e)
                else:
                    break
                cur_time = int(time.time() * 1000.0)


            #处理新的功能
            for func in self._yields:
                try:
                    next_time = func.next() + cur_time
                    self._timers.append((next_time, func))
                except GreenletExit:
                    return
                except Exception as e:
                    log.error('timer(%s) error:%s', func, e)
            self._yields = []

            #准备下一次唤醒
            self._timers.sort()
            self._waiter.clear()
            len_timer = len(self._timers)
            if len_timer:
            ##                if len_timer > 50:
            ##                    log.error('TimerSet error:len(self._timers) > 50, it is may be an error?')
            ##                    for nt, func in self._timers:
            ##                        log.info('  next_time=%s, func=%s', nt, func)
            ##                    raise Exception('TimerSet error:len(self._timers) > 50, it is may be an error?')
                s_time = (self._timers[0][0] - cur_time) / 1000.0
                #log.debug('****wait(%s) _timers(%s)', s_time, self._timers)
                self._waiter.wait(timeout=min(s_time, self.default_wait))
            else:
                if self.stoped:
                    return
                self._waiter.wait(timeout=self.default_wait)

        self.stop()
        if 0:
            log.debug('TimerSet._loop stoped')


class TimeCounter(object):
    """
    一段時間內計數器，如果超出（默認一天的時間）範圍，重新計數
    """
    def __init__(self, days=1):
        self.last_time_stamp = datetime.datetime.now().date()#時間戳
        self._count = 0
        if days and isinstance(days,int):
            self._delay = datetime.timedelta(days)
        else:
            self._delay = datetime.timedelta(1) #計數器重新計數間隔，默認一天

    @property
    def count(self):
        """返回計數值"""
        if self.is_over:
            self._reset()
        return self._count

    def increase(self):
        if  self.is_over:#如果超时，重置
            self._reset()
        self._count += 1

    def _reset(self):
        """計數值重設為0"""
        self._count = 0

    @property
    def is_over(self):
        """判斷當前時間與最後時間戳這段時間是否超出設定的範圍，如果超過返回 True
            否則False
        """
        today = datetime.datetime.now().date()
        if today - self.last_time_stamp >= self._delay:
            self.last_time_stamp = today
            return True
        else:
            return False
