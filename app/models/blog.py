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

from app.extensions import mdb
from app.models import User
from app.core import Model


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
    indexes = [{'fields': ['name'], 'unique': True}]


@mdb.register
class Post(Model):
    __collection__ = 'posts'
    schema = {
        'uid': ObjectId,
        'pics': [str],
        'title': str,
        'body': str,
        'tids': [ObjectId],  # 相关标签
        'createTime': datetime,
        'viewTimes': int,
        'comments': [{
            'id': int,
            'uid': ObjectId,  # 发表评论人
            'content': str,
            'time': datetime,
            'replys': [{
                'uid': ObjectId,  # 发表回复的人
                'rid': ObjectId,  # 接收回复的人
                'content': str,
                'time': datetime
            }]
        }]
    }

    required_fields = ['uid', 'title', 'body', 'tids', 'createTime']
    default_values = {'createTime': datetime.now, 'viewTimes': 0}
    indexes = [{'fields': 'tids'}, {'fields': 'createTime'}]

    @cached_property
    def author(self):
        author = User.find_one({'_id': self.uid})
        return author

    @cached_property
    def tags(self):
        ids = list(self.tids)
        tag_dict = {t._id: t for t in Tag.find({'_id': {'$in': ids}})}
        return [tag_dict[id] for id in ids if id in tag_dict]
