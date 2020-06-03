# -*- coding: utf-8 -*-
"""
    blog.py
    ~~~~~~~~~~~~~~

    blog related models.

    :copyright: (c) 2016 by fengweimin.
    :date: 16/8/16
"""
from datetime import datetime

from bson.objectid import ObjectId
from werkzeug.utils import cached_property

from app.core import Model, Comparator, Format
from app.extensions import mdb
from app.models import User


@mdb.register
class Tag(Model):
    __collection__ = 'tags'
    schema = {
        'name': str,
        'weight': int,
        'createTime': datetime,
    }

    required_fields = ['name', 'weight', 'createTime']
    default_values = {'weight': 0, 'createTime': datetime.now}
    searchables = [('name', Comparator.LIKE)]
    indexes = [
        {'fields': ['name'], 'unique': True}
    ]


@mdb.register
class Post(Model):
    __collection__ = 'posts'
    schema = {
        'uid': ObjectId,
        'cover': str,
        'title': str,
        'abstract': str,
        'body': str,
        'tids': [ObjectId],  # 相关标签
        'createTime': datetime,
        'updateTime': datetime,  # 更新时间
        'viewTimes': int,
        'comments': [{
            'id': int,
            'uid': ObjectId,  # 发表评论人
            'uname': str,  # 评论人名字, 冗余数据
            'uavatar': str,  # 评论人头像, 冗余数据
            'content': str,
            'time': datetime
        }]
    }

    required_fields = ['uid', 'cover', 'title', 'abstract', 'body', 'tids', 'createTime', 'viewTimes',
                       'comments[].id', 'comments[].uid', 'comments[].content', 'comments[].time']
    default_values = {'createTime': datetime.now, 'viewTimes': 0}
    formats = {'cover': Format.IMAGE, 'abstract': Format.TEXTAREA, 'body': Format.RTE, 'tids': Format.SELECT}
    searchables = [('title', Comparator.LIKE), 'tids']
    columns = ['cover', 'uid', 'title', 'tids', 'viewTimes', 'createTime']
    indexes = [
        {'fields': 'tids'},
        {'fields': 'createTime'}
    ]

    @cached_property
    def author(self):
        author = User.find_one({'_id': self.uid})
        return author

    @cached_property
    def tags(self):
        ids = list(self.tids)
        tag_dict = {t._id: t for t in Tag.find({'_id': {'$in': ids}})}
        return [tag_dict[id] for id in ids if id in tag_dict]
