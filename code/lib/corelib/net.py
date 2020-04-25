#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import sys
import socket
import urllib

from gevent import with_timeout
from functools import partial, wraps

from corelib import log

sys_setting = sys.modules['SysSetting']

def get_local_ip():
    """ 获取本机ip,如果网络不通，反应会慢 """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("baidu.com",80))
        return s.getsockname()[0]
    except :
        return socket.gethostbyname(socket.gethostname())

def new_stream_server(addr, handle):
    from gevent.server import StreamServer
    if isinstance(addr, list):
        addr = tuple(addr)
    svr = StreamServer(addr, handle=handle)
    svr.reuse_addr = 1 #重用端口,防止重启异常
    svr.start()
    return svr

def new_stream_server_by_ports(host, ports, handle, is_random=False):
    import random, socket
    def _listen(port):
        try:
            svr = new_stream_server((host, port), handle)
            return svr
        except socket.error:#端口不可监听，换一个
            pass

    if is_random:
        choiced = []
        while 1:
            port = random.choice(ports)
            if port in choiced:
                if len(choiced) == len(ports):
                    raise ValueError('not free port for client')
                continue
            choiced.append(port)
            svr = _listen(port)
            if svr is not None:
                return svr
    else:
        for p in ports:
            svr = _listen(p)
            if svr is not None:
                return svr
        raise ValueError('not free port for client')

def get_rel_urls(url, params):
    if params is not None:
        if isinstance(params, dict):
            s = urllib.urlencode(params)
        else:
            s = str(params)
        return '%s?%s' %(url, s)
    else:
        return url

def get_urls(host, port, url, params, ssl=False):
    if port is None:
        port = ''
    else:
        port = ':%s' % port
    http = 'http'
    if ssl:
        http = 'https'
    return '%s://%s%s%s' % (http, host, port, get_rel_urls(url, params))


def _wrap_time_out(func):
    @wraps(func)
    def _func(*args, **kw):
        timeout = kw.pop('timeout', 5)
        return with_timeout(timeout, func, *args, **kw)
    return _func


@_wrap_time_out
def http_httplib(host, port, url, params=None, data=None, raise_err=False, con=None, headers=None, ssl=False):
    """ 用http方式发送数据 """
    import httplib
    if headers is None:
        headers = {}
    err_msg = '发送数据到HTTP服务器(%s:%d%s)时出错' % (host, port, url)
    want_close = (con is None)
    if want_close:
        HC = httplib.HTTPConnection if not ssl else httplib.HTTPSConnection
        con = HC(host, port)
    try:
        urls = get_rel_urls(url, params)
        data = urllib.urlencode(data)
        con.request('POST' if data is not None else 'GET', urls, body=data, headers=headers)
        rs = con.getresponse()
        if rs.status != 200:
            if raise_err:
                raise ValueError(rs.status, rs.read())
            log.error('%s:%s - %s', err_msg, rs.status, rs.read())
        else:
            return rs.read()
    except socket.error as e:
        if raise_err:
            raise ValueError(e)
        log.error('%s:%s', err_msg, str(e))
    except Exception:
        if raise_err:
            raise
        log.log_except()
    finally:
        if want_close:
            con.close()

try:
    import urllib3
    from urllib3 import connectionpool
    _http_pool = urllib3.PoolManager(maxsize=10)
    connectionpool.log.setLevel(connectionpool.logging.WARN)
except ImportError:
    urllib3 = None

@_wrap_time_out
def http_urllib3(host, port, url, params=None, data=None, raise_err=False, headers=None, ssl=False):
    """ 用http方式发送数据 """
    err_msg = '发送数据到HTTP服务器(%s:%s%s)时出错' % (host, port, url)
    try:
        urls = get_urls(host, port, url, params, ssl=ssl)
        data = urllib.urlencode(data)
        rs = _http_pool.urlopen('POST' if data is not None else 'GET',
            urls, body=data, headers=headers)
        if rs.status != 200:
            if raise_err:
                raise ValueError(rs.status, rs.data[:50])
            log.error('%s:%s - %s', err_msg, rs.status, rs.data[:50])
        else:
            return rs.data
    except socket.error as e:
        if raise_err:
            raise ValueError(e)
        log.error('%s:%s', err_msg, str(e))
    except Exception:
        if raise_err:
            raise
        log.log_except()

http_post = http_httplib
if urllib3:
    http_post_ex = http_urllib3
else:
    http_post_ex = http_httplib
