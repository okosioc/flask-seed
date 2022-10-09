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


def async_exec(f):
    """ Async execution.

    Below is sample usage:

    def execute():
        _execute(current_app._get_current_object())

    @async_exec
    def _execute(app, **kwargs):
        with app.context():
            pass
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        # https://docs.python.org/3/library/threading.html#threading.Thread.daemon
        thr.setDaemon(True)
        thr.start()

    return wrapper


def auth_permission(f):
    """ 检测是否已经登录且处于正常状态. """

    @wraps(f)
    def wrapper(*args, **kwargs):
        if current_user.is_anonymous:
            abort(401)
        if current_user.is_rejected:
            abort(403)
        return f(*args, **kwargs)

    return wrapper


def editor_permission(f):
    """ 检测是否为系统编辑. """

    @wraps(f)
    def wrapper(*args, **kwargs):
        if current_user.is_anonymous:
            abort(401)
        if current_user.is_rejected or (not current_user.is_admin and not current_user.is_editor):
            abort(403)
        return f(*args, **kwargs)

    return wrapper


def admin_permission(f):
    """ 检测是否为系统管理员. """

    @wraps(f)
    def wrapper(*args, **kwargs):
        if current_user.is_anonymous:
            abort(401)
        if not current_user.is_admin:
            abort(403)

        return f(*args, **kwargs)

    return wrapper
