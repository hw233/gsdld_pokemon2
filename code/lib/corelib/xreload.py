#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# vim: fdm=marker

# NOTE !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#
# Python 各类特性使用说明
#   Property
#       针对同个名字的property 新旧代码都必须要有getter 要么都有setter要么都没有setter 要么都有deleter要么都没有deleter
#   装饰器
#       请谨慎使用 被装饰的函数能正常热更新，装饰器函数本身不能热更新，例如game.room.input.random_delay_robot_input
#   闭包
#       代码应该避免使用闭包，更新时不做闭包变量检查
#   全局变量|类属性
#       除了函数或类外一律用新的同名变量替换
#       请避免使用全局变量，类属性来存放动态数据
#   __slots__
#       请谨慎使用 使用尽量自己多热更新几次 看看是不是有未知未处理的风险
#   metaclass
#       请不要使用
#
# NOTE !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# TODO：
# reload失败的回滚处理
#

__all__ = ["reload_module"]

import gc
import sys
import types
import marshal
import inspect

from corelib import log

def logger(msg):
    log.info(msg)


# def do_replace_func(new_func, old_func, is_closure = False):
#     # 简单的closure的处理
#     re_attrs = ('func_doc', 'func_code', 'func_dict', 'func_defaults')
#     for attr_name in re_attrs:
#         setattr(old_func, attr_name, getattr(new_func, attr_name, None))
#     if not is_closure:
#         old_cell_nums = len(old_func.func_closure) if old_func.func_closure else 0
#         new_cell_nums = len(new_func.func_closure) if new_func.func_closure else 0
#         if new_cell_nums and new_cell_nums == old_cell_nums:
#             for idx, cell in enumerate(old_func.func_closure):
#                 if inspect.isfunction(cell.cell_contents):
#                     do_replace_func(new_func.func_closure[idx].cell_contents, cell.cell_contents, True)

def do_replace_func(new_func, old_func):
    # 暂时不支持closure的处理
    re_attrs = ('__doc__', '__code__', '__dict__', '__defaults__')
    for attr_name in re_attrs:
        setattr(old_func, attr_name, getattr(new_func, attr_name, None))

def update_class(cls_name, old_mod, new_mod, new_cls):
    old_cls = getattr(old_mod, cls_name, None)
    if old_cls:
        for name, new_attr in new_cls.__dict__.items():
            old_attr = old_cls.__dict__.get(name, None)
            if new_attr and not old_attr:
                setattr(old_cls, name, new_attr)
                continue
            if inspect.isfunction(new_attr) and inspect.isfunction(old_attr):
                do_replace_func(new_attr, old_attr)
    else:
        setattr(old_mod, cls_name, new_cls)

def update_function(func_name, old_mod, new_mod, new_func):
    old_func = getattr(old_mod, func_name, None)
    if old_func:
        if inspect.isfunction(old_func) and inspect.isfunction(new_func):
            do_replace_func(new_func, old_func)
    else:
        setattr(old_mod, func_name, new_func)


class Reloader(object):
    """ Reload a module in place, updating classes, methods and functions.

    Args:
      mod: a module object

    Returns:
      The (updated) input object itself.
    """

    def __init__(self, module):
        self.old_mod = module

    def reload(self):
        modname = self.old_mod.__name__

        old_mod = sys.modules.pop(modname)
        __import__(modname)
        new_mod = sys.modules.pop(modname)

        sys.modules[modname] = old_mod

        for name, newobj in inspect.getmembers(new_mod):
            if inspect.isclass(newobj):
                update_class(name, old_mod, new_mod, newobj)
            elif inspect.isfunction(newobj):
                update_function(name, old_mod, new_mod, newobj)


def reload_module(module_name):
    try:
        module = sys.modules.get(module_name)
        if not module:
            print("no module ---  %s"%(module_name))
            logger("real_reload_module no module %s" % module_name)
            return

        logger("reload_module %s %s begin" % (module_name, module))

        Reloader(module).reload()

        logger("reload_module %s %s end" % (module_name, module))

    except Exception as err:
        logger("!!! reload_module %s error %s" % (module_name, err))
        log.log_except()


