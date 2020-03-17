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
    """ Async execution. """

    @wraps(f)
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        # https://docs.python.org/3/library/threading.html#threading.Thread.daemon
        thr.setDaemon(True)
        thr.start()

    return wrapper


def auth_permission(f):
    """ Check auth permission and other business checking.

    :return:
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        if current_user.is_anonymous:
            abort(401)
        if current_user.is_rejected:
            abort(403)
        return f(*args, **kwargs)

    return wrapper


def admin_permission(f):
    """ Check admin permission and other business checking.

    :return:
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        if current_user.is_anonymous:
            abort(401)
        if not current_user.is_admin:
            abort(403)

        return f(*args, **kwargs)

    return wrapper
