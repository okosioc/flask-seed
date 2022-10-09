# -*- coding: utf-8 -*-
"""
    helpers
    ~~~~~~~~~~~~~~

    Helper functions.

    :copyright: (c) 2016 by fengweimin.
    :date: 16/6/11
"""

import json
from datetime import datetime, timedelta

from flask_babel import gettext, ngettext


def timesince(dt, default=None):
    """  Returns string representing "time since".

    :param dt:
    :param default:
    :return: e.g. 3 days ago, 5 hours ago etc.
    """
    if default is None:
        default = gettext("just now")

    now = datetime.now()
    diff = now - dt

    years = diff.days // 365
    months = diff.days // 30
    weeks = diff.days // 7
    days = diff.days
    hours = diff.seconds // 3600
    minutes = diff.seconds // 60
    seconds = diff.seconds

    periods = (
        (years, ngettext("%(num)s year", "%(num)s years", num=years)),
        (months, ngettext("%(num)s month", "%(num)s months", num=months)),
        (weeks, ngettext("%(num)s week", "%(num)s weeks", num=weeks)),
        (days, ngettext("%(num)s day", "%(num)s days", num=days)),
        (hours, ngettext("%(num)s hour", "%(num)s hours", num=hours)),
        (minutes, ngettext("%(num)s minute", "%(num)s minutes", num=minutes)),
        (seconds, ngettext("%(num)s second", "%(num)s seconds", num=seconds)),
    )

    for period, trans in periods:
        if period:
            return gettext("%(period)s ago", period=trans)

    return default


def date_str(dt):
    """ Show date string in jinja2. """
    return dt.strftime('%Y-%m-%d')


def time_str(dt):
    """ Show date time string in jinja2. """
    return dt.strftime('%H:%M:%S')


def datetime_str(dt):
    """ Show date time string in jinja2. """
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def str_datetime(dts):
    """ Convert datetime string to datetine. """
    return datetime.strptime(dts, '%Y-%m-%d %H:%M:%S')


def timedelta_str(seconds):
    """ Show timedelta of seconds, e.g, 100 -> 0:01:40. """
    return str(timedelta(seconds=seconds))


def json_dumps(data, pretty=False):
    """ 序列化json对象.

    pretty=False, 返回无空格以及utf8编码的json字符串, 用于调用api时进行签名.
    pretty=True, 漂亮的打印, 用于日志.
    """
    if pretty:
        return json.dumps(data, indent=2, ensure_ascii=False)
    else:
        return json.dumps(data, separators=(',', ':'), ensure_ascii=False)
