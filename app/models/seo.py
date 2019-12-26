# -*- coding: utf-8 -*-
"""
    seo
    ~~~~~~~~~~~~~~

    SEO related models.

    :copyright: (c) 2016 by fengweimin.
    :date: 2016/10/18
"""

from datetime import datetime

import pymongo
from bson.objectid import ObjectId
from werkzeug.utils import cached_property

from app.extensions import mdb
from app.core import Model, IN


class KeywordLevel(object):
    """
    关键词级别.
    """
    # 站点关键词
    SITE = 1
    # 长尾关键词
    LONG_TAIL = 2


class KeywordStatus(object):
    """
    关键词状态.
    """
    BARE = 'bare'  # 初始状态
    PROCESSED = 'processed'  # 已经写了文章, 只用于长尾关键词
    REPEATED = 'repeated'  # 被标记为重复
    REJECTED = 'rejected'  # 忽略该关键词


@mdb.register
class Keyword(Model):
    __collection__ = 'keywords'
    schema = {
        'name': str,
        'level': IN(KeywordLevel.SITE, KeywordLevel.LONG_TAIL),
        'status': IN(KeywordStatus.BARE, KeywordStatus.PROCESSED, KeywordStatus.REPEATED, KeywordStatus.REJECTED),
        'parentId': ObjectId,  # 如果是长尾关键词, 应该指定一个站点的关键词作为其父关键词,
        'baiduIndex': int,  # 百度指数
        'baiduResult': int,  # 百度搜索结果
        'createTime': datetime,
        'updateTime': datetime,
        'hearsay': {  # 每个关键字暂时只能写一篇文章
            'title': str,
            'body': str
        },
        'processed': int,  # 如果是站点关键词, 表示其下已经处理的长尾词数量
        'total': int,  # 如果是站点关键词, 表示其下长尾词数量
        'refer': str,  # 相关链接
        'owner': str,  # 负责人
        'remarks': str,  # 备注
    }

    required_fields = ['name', 'level', 'status', 'baiduIndex', 'baiduResult', 'createTime']
    default_values = {'status': KeywordStatus.BARE, 'baiduIndex': 0, 'baiduResult': 0, 'createTime': datetime.now,
                      'processed': 0, 'total': 0}
    indexes = [
        {'fields': ['name'], 'unique': True},
        {'fields': ['level', 'owner', ('baiduIndex', pymongo.DESCENDING)]},
        {'fields': ['parentId', ('baiduIndex', pymongo.DESCENDING)]}
    ]

    @cached_property
    def sons(self):
        return [k for k in Keyword.find({'parentId': self._id})]
