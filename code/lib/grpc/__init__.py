# -*- coding:utf-8 -*-

try:
    from grpc.rpc import *
    from grpc.rpc_shell import *
except ImportError as e:
    print("Import grpc:%s" % e)



