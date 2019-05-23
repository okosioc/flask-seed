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
from flask_login import current_user, login_required

from app.extensions import cache
from app.permissions import admin_permission

# 角色定义
role_admin = 'admin'  # 管理员


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
        if current_user.is_anonymous or current_user.is_rejected:
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


def check_roles(needed=[]):
    """
    检查所需权限，默认调用该装饰器的函数需要登录并且是非拒绝用户.

    :param needed:权限列表，参照本文件开头处常量定义
    :return:
    """

    def decorator(f):
        @wraps(f)
        @login_required
        @user_not_rejected
        def wrapper(*args, **kwargs):
            if role_admin in needed:
                with admin_permission.require(403):
                    pass

            return f(*args, **kwargs)

        return wrapper

    return decorator
