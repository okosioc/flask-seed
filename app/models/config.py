# -*- coding: utf-8 -*-
"""
    config
    ~~~~~~~~~~~~~~

    Model config.

    :copyright: (c) 2017 by fengweimin.
    :date: 2017/2/28
"""

from datetime import datetime

from app.core import Model, Comparator
from app.extensions import mdb


@mdb.register
class Config(Model):
    __collection__ = 'configs'
    schema = {
        'name': str,
        'value': str,
        'createTime': datetime
    }

    required_fields = ['name', 'createTime']
    default_values = {'createTime': datetime.now}
    searchables = [('name', Comparator.LIKE)]
    indexes = [{'fields': ['name'], 'unique': True}]
