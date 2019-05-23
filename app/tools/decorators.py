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

from app.permissions import admin_permission

permission_admin = 'admin'


def async_exec(f):
    """
    Async execution.
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
    Check if user is rejected.
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        if current_user.is_anonymous or current_user.is_rejected:
            abort(403)
        return f(*args, **kwargs)

    return wrapper


def check_permission(needed=None):
    """
    Check permission needed.

    :param needed:
    :return:
    """

    def decorator(f):
        @wraps(f)
        @login_required
        @user_not_rejected
        def wrapper(*args, **kwargs):
            if needed == 'permission_admin':
                with admin_permission.require(403):
                    pass

            return f(*args, **kwargs)

        return wrapper

    return decorator
