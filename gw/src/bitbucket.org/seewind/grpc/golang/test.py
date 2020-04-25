#!/usr/bin/env python
# -*- coding:utf-8 -*-
import sys
from os.path import join, dirname, abspath
from gevent import sleep
grpc_path = join(abspath(dirname(__file__)), '..')
sys.path.insert(0, grpc_path)
import grpc
tcp_endpoint = ('127.0.0.1', 18081)
unix_endpoint = '/tmp/grpc_svr.sock'

class Client(object):
    _rpc_name_ = 'client'
    def __init__(self):
        pass

    def get_name(self):
        return 'client_name'

    def test_raise(self, v):
        print "test_raise:%s" % repr(v)
        raise ValueError("Value is:%s" % repr(v))


def test():
    cobj = Client()
    cobj1 = Client()
    client = grpc.RpcClient()
    client.connect(tcp_endpoint)
    client.start()
    svr = client.svc.get_proxy('server')
    print svr.echo('abc'*10)
    print svr.test_proxy(cobj, _proxy=True)
    cobj1._rpc_name_ = 'aaaa'
    try:
        print svr.test_exception(cobj1, _proxy=True)
    except Exception as e:
        print e

    svr.test_proxys([cobj, cobj1], _proxy=True)
    #sleep(2)
    client.stop()
    print 'finish'

def main():
    for i in xrange(1):
        test()

if __name__ == '__main__':
    main()

