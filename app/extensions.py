# -*- coding: utf-8 -*-
"""
    extension.py
    ~~~~~~~~~~~~~~

    Extension reference.

    :copyright: (c) 2016 by fengweimin.
    :date: 16/5/9
"""

from flask_caching import Cache
from flask_mail import Mail

from app.vendors import QiniuSupport
from app.core import MongoSupport

__all__ = ['mail', 'cache', 'mdb', 'qiniu']

mail = Mail()
cache = Cache()
mdb = MongoSupport()
qiniu = QiniuSupport()
