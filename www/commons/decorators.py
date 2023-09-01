# -*- coding: utf-8 -*-
"""
    decorators
    ~~~~~~~~~~~~~~

    Decorators definition.

    :copyright: (c) 2016 by fengweimin.
    :date: 16/8/15
"""

import time

from functools import wraps, partial
from threading import Thread

from flask import abort, current_app
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
        """ Execute the function in a new thread. """
        thr = Thread(target=f, args=args, kwargs=kwargs)
        # https://docs.python.org/3/library/threading.html#threading.Thread.daemon
        thr.setDaemon(True)
        thr.start()

    return wrapper


def retry(f=None, attempts=3, exceptions=(Exception,), delay=0.5):
    """ Retry function.

    Below are sample usages, Note: this decorator should be used with or without parameters:

    @retry
    def func():
        pass

    @retry(3)
    def func():
        pass

    @retry(3, (ValueError, TypeError,))
    def func():
        pass
    """

    if f is None:
        return partial(retry, attempts=attempts, exceptions=exceptions, delay=delay)

    @wraps(f)
    def wrapper(*args, **kwargs):
        """ Wrapper. """
        nonlocal attempts, exceptions, delay
        for attempt in range(1, attempts + 1):
            try:
                return f(*args, **kwargs)
            except exceptions as exc:
                print(f'Attempt {attempt} failed', type(exc).__name__, '–', str(exc))
                #
                if attempt == attempts:
                    raise
                #
                if delay > 0:
                    time.sleep(delay)

    return wrapper


def auth_permission(f):
    """ 检测是否已经登录且处于正常状态. """

    @wraps(f)
    def wrapper(*args, **kwargs):
        """ Wrapper. """
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
        """ Wrapper. """
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
        """ Wrapper. """
        if current_user.is_anonymous:
            abort(401)
        if not current_user.is_admin:
            abort(403)

        return f(*args, **kwargs)

    return wrapper
