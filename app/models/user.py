# -*- coding: utf-8 -*-
"""
    user.py
    ~~~~~~~~~~~~~~

    Model user.

    :copyright: (c) 2016 by fengweimin.
    :date: 16/6/11
"""

from datetime import datetime

from flask_login import UserMixin
from werkzeug.utils import cached_property

from app.core import Model, IN
from app.extensions import mdb


class UserRole(object):
    """ User roles. """
    MEMBER = 1
    ADMIN = 9


class UserStatus(object):
    """ User Status. """
    NORMAL = 'normal'
    REJECTED = 'rejected'


@mdb.register
class User(Model, UserMixin):
    __collection__ = 'users'
    schema = {
        'name': str,
        'email': str,
        'password': str,
        'head': str,
        'point': int,
        'status': IN(UserStatus.NORMAL, UserStatus.REJECTED),
        'roles': [int],
        'createTime': datetime,
        'updateTime': datetime
    }
    required_fields = ['name', 'email', 'password', 'point', 'status', 'roles', 'createTime']
    default_values = {'point': 0, 'status': UserStatus.NORMAL, 'roles': [UserRole.MEMBER], 'createTime': datetime.now}
    indexes = [{'fields': ['email'], 'unique': True}]

    @cached_property
    def is_admin(self):
        return UserRole.ADMIN in self.roles

    @cached_property
    def is_rejected(self):
        return self.status == UserStatus.REJECTED

    def get_id(self):
        """
        UserMixin of flask-login.
        """
        return str(self._id)

    def __eq__(self, other):
        return self._id == other._id
