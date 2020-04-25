import socket
import time
import struct
import json
import gevent
import zlib

TAG_NO_RESULT = '\xff\xbc' #struct.pack('!H', 65468)


def send(sock, d, tag='\xff\xb0'):
    dd = json.dumps(d)
    dd = zlib.compress(dd)
    l = len(dd)
    data = '%s%s%s' % (tag, struct.pack('!I', l), dd)
    sock.sendall(data)
    r = sock.recv(1024)
    print repr(r)


def test1(name="test", c=10):
    s = socket.socket()
    s.connect(('localhost', 10100))
    time.sleep(0.1)
#    d = '\xff\xbc\x00\x00\x00\x1d{"f":"f","s":1,"d":"","m":""}'
    d = {"f":"f","s":1,"d":"","m":""}
    #
    send(s, {"f":"_ctl_connect","d":{"host":"172.16.40.250","port":8002}})
#    send(s, '\xff\xbc\x00\x00\x000{"f":"_ctl_connect","s":1,"d":"127.0.0.1:18081"}')

    for i in xrange(c):
        send(s, d)
        time.sleep(0.1)
    s.close()


def test2(n, c=20):
    from gevent.monkey import patch_all
    patch_all()
    tasks = []

    index = 0
    while 1:
        for i in xrange(c):
            t = gevent.spawn(test1, name="name-%s" % (index + i, ))
            tasks.append(t)
        gevent.joinall(tasks)
        index += c
        if index >= n:
            break
    # tasks.append(gevent.spawn(test1, name="name-%s" % (0, )))
    # gevent.joinall(tasks)


def main():
    test1(c=1)
#    test2(100000)

main()