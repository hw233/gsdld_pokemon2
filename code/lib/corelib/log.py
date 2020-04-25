#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os, sys
import traceback
import types
import locale
locale_encode = locale.getdefaultlocale()[1]
if locale_encode is None:
    locale_encode = 'UTF-8'

import time
import ujson
import logging
from logging import (DEBUG, INFO, WARNING, ERROR, FATAL, NOTSET,
        debug, info, warning, error, exception,
      getLogger, StreamHandler, handlers, config)

for n in logging.__all__:
    globals()[n] = getattr(logging, n)

simpleformat = '[%(asctime)s]p%(process)d{%(module)s:%(funcName)s:%(lineno)d}%(levelname)s-%(message)s'
shortformat = '[%(asctime)s]p%(process)d{%(module)s:%(lineno)d}%(levelname)s-%(message)s'
shortdatefmt = '%m-%d %H:%M:%S'

def _StreamHandler_emit(self, record):
    if getattr(self, 'stoped', False): return
    try:
        msg = self.format(record)
        fs = "%s\n"

        self.stream.write(fs % msg)

        self.flush()
    except (KeyboardInterrupt, SystemExit):
        raise
    except IOError:
        self.stoped = 1
        #self.close()
    except:
        log_except('args=(%s)', record.args)
        #self.handleError(record)

def _StreamHandler_wrap_init(init_func):
    def _wrap_init(self, *args, **kw):
        init_func(self, *args, **kw)
        self.stoped = 0
    return _wrap_init
logging.StreamHandler.__init__ = _StreamHandler_wrap_init(logging.StreamHandler.__init__)
logging.StreamHandler.emit = _StreamHandler_emit

# class LogRecordEx(logging.LogRecord):
#     def __init__(self, name, level, pathname, lineno,
#                        msg, args, exc_info, func=None):
#         if sys.platform != 'win32':
#             pathname = pathname.replace('\\', '/')
#         logging.LogRecord.__init__(self, name, level, pathname, lineno,
#                                                msg, args, exc_info, func)


class MyLogger(logging.Logger):
    def log(self, *args, **kw):
        self.debug("\n" + str(args) + str(kw) + "\n")

    def log_except(self, *args):
        log_except(*args, logger=self)

    def log_stack(self, msg='', level=WARNING):
        log_stack(msg=msg, level=level, logger=self)

    write = logging.Logger.debug
    write_info = logging.Logger.info
    write_error= logging.Logger.exception

    def close(self):
        for hd in self.handlers:
            hd.close()
        self.disabled = 1

    # def makeRecord(self, name, level, fn, lno, msg, args, exc_info, func=None, extra=None):
    #     rv = LogRecordEx(name, level, fn, lno, msg, args, exc_info, func)
    #     if extra is not None:
    #         for key in extra:
    #             if (key in ["message", "asctime"]) or (key in rv.__dict__):
    #                 raise KeyError("Attempt to overwrite %r in LogRecord" % key)
    #             rv.__dict__[key] = extra[key]
    #     return rv

    def makeRecord(self, name, level, fn, lno, msg, args, exc_info,
                   func=None, extra=None, sinfo=None):
        """
        A factory method which can be overridden in subclasses to create
        specialized LogRecords.
        """
        rv = logging.LogRecord(name, level, fn, lno, msg, args, exc_info, func,
                             sinfo)
        if extra is not None:
            for key in extra:
                if (key in ["message", "asctime"]) or (key in rv.__dict__):
                    raise KeyError("Attempt to overwrite %r in LogRecord" % key)
                rv.__dict__[key] = extra[key]
        return rv

logging.setLoggerClass(MyLogger)

def log_except(*args, **kw):
    logger = kw.get('logger', None)
    better = kw.pop('_better', 0)
    if not logger:
        logger = logging.root

    if not len(args):
        msg = None
    elif len(args) == 1:
        msg = args[0]
        args = []
    else:
        msg = args[0]
        args = args[1:]
    lines = ['Traceback (most recent call last):\n']
    try: #问题:在centos中,出现过在traceback.extract_tb行出现编码错误,由代码行有中文引起
        if better:
            import better_exchook
            better_exchook.better_exchook(*sys.exc_info(),
                    output=lambda s:lines.append('%s\n' % s))
        else:
            ei = sys.exc_info()
            st = traceback.extract_stack(f=ei[2].tb_frame.f_back)
            et = traceback.extract_tb(ei[2])
            lines.extend(traceback.format_list(st))
            lines.append('  ****** Traceback ******  \n')
            lines.extend(traceback.format_list(et))
            lines.extend(traceback.format_exception_only(ei[0], ei[1]))
        exc = ''.join(lines)
        if msg:
            args = list(args)
            args.append(exc)
            logger.error(msg + ':\n%s', *args)
        else:
            logger.error(exc)
    except:
        exception('log_except error:')


def log_stack(msg='', level=WARNING, logger=None):
    if not logger:
        logger = logging.root
    msg = 'log_stack:%s\n%s' % (msg, ''.join(traceback.format_stack()))
    if level == WARNING:
        logger.warning(msg)
    elif level == DEBUG:
        logger.debug(msg)
    elif level == INFO:
        logger.info(msg)
    elif level == ERROR:
        logger.error(msg)


def logmsg(obj):
    func = logmsg
    result = ''
    if isinstance(obj, str):
        return obj

    elif isinstance(obj, dict):
        for k,v in obj.items():
            k8 = func(k)
            v8 = func(v)
            result += '%s:%s, ' %(k8, v8)
        return '{%s}' % result
    elif isinstance(obj, list):
        for v in obj:
            result += '%s, ' % func(v)
        return '[%s]' % result
    elif isinstance(obj, tuple):
        for v in obj:
            result += '%s, ' % func(v)
        return '(%s)' % result
    else:
        return str(obj)

######################salog##################################
salogger = None
def init_salog(tag, level=logging.INFO):
    global salogger
    logger = logging.getLogger('SALogger')
    logger.setLevel(level)

    SysLogHandler = logging.handlers.SysLogHandler
    if sys.platform.startswith('linux'):
        # Linux下写到syslog
        # TODO: sys log 不去标注输出
        ch = SysLogHandler('/dev/log', facility=SysLogHandler.LOG_LOCAL0)
        ch.setLevel(level)
        formatter = logging.Formatter(tag + ": %(message)s")
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        #不传递给父的logger,SAlog指纪录在syslog
        logger.propagate = False
    else:
        # Windows/MAC 下写到文件
        filename = tag+"_"+time.strftime("%Y%m%d_%H%M%S")+'.txt'
        filename = tag+'.txt' #TODO: 先多个进程写到一个文件，方便测试
        filehandler = logging.FileHandler(filename)
        formatter = logging.Formatter("%(message)s")
        filehandler.setFormatter(formatter)
        logger.addHandler(filehandler)
    salogger = logger


def salog(operation, info):
    salogger.info('[%s][%s],%s' % (
        time.strftime("%Y-%m-%d %H:%M:%S"),
        operation,
        ujson.dumps(info, ensure_ascii=False),
        )
    )
######################syslog##################################


def console_config(debug=True, log_file=None, format=shortformat, datefmt=shortdatefmt):
        level = DEBUG if debug else INFO
        while logging.root.handlers:
            logging.root.handlers.pop()
        logging.basicConfig(level=level,
                format=format,
                datefmt=datefmt,
                stream=sys.stdout,
                #filename= logFullName('app.log'), filemode='w'
                )
        if log_file:
            fmt = logging.Formatter(format, datefmt)
            hdlr = logging.FileHandler(log_file, 'a')
            hdlr.setFormatter(fmt)
            logging.root.addHandler(hdlr)

