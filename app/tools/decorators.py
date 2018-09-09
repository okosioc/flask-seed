# -*- coding: utf-8 -*-
"""
    decorators
    ~~~~~~~~~~~~~~

    Decorators definition.

    :copyright: (c) 2016 by fengweimin.
    :date: 16/8/15
"""

from functools import wraps
from threading import Thread

from flask import abort
from flask_login import current_user

from app.extensions import cache


def async_exec(f):
    """
    异步执行函数.
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        # https://docs.python.org/2/library/threading.html#threading.Thread.daemon
        # 重启Flask服务器时中止正在执行的异步线程
        thr.setDaemon(True)
        thr.start()

    return wrapper


def user_not_rejected(f):
    """
    检测当前用户是否被封.
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        if current_user.is_rejected:
            abort(403)
        return f(*args, **kwargs)

    return wrapper


def user_not_evil(f):
    """
    检测当前用户是否是非法用户.
    1) 15秒内不能重复操作.
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        key = 'evil_' + str(current_user._id)
        rv = cache.get(key)
        if not rv:
            # 15秒
            cache.set(key, object(), timeout=15)
        else:
            abort(403)
        return f(*args, **kwargs)

    return wrapper
