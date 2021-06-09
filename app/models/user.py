# -*- coding: utf-8 -*-
"""
    user.py
    ~~~~~~~~~~~~~~

    Model user.

    :copyright: (c) 2016 by fengweimin.
    :date: 16/6/11
"""

from datetime import datetime
from typing import List

from flask_login import UserMixin
from werkzeug.utils import cached_property

from app.core import Model, SimpleEnum, Format, Comparator
from app.extensions import mdb


class UserRole(SimpleEnum):
    """ User roles. """
    MEMBER = 1
    EDITOR = 2
    ADMIN = 9


class UserStatus(SimpleEnum):
    """ User Status. """
    NORMAL = 'normal'
    REJECTED = 'rejected'


class Account():
    name: str
    email: str
    password: str
    intro: str = None
    avatar: str = None
    point: int = 0
    status: UserStatus = UserStatus.NORMAL
    roles: List[UserRole] = [UserRole.MEMBER]
    updateTime: datetime = None
    createTime: datetime = datetime.now

    __collection = 'accounts'
    __indexes = [{'fields': ['email'], 'unique': True}]


@mdb.register
class User(Model, UserMixin):
    __collection__ = 'users'
    schema = {
        'name': str,
        'email': str,
        'password': str,
        'intro': str,
        'avatar': str,
        'point': int,
        'status': UserStatus,
        'roles': [UserRole],
        'createTime': datetime,
        'updateTime': datetime
    }
    required_fields = ['name', 'email', 'avatar', 'point', 'status', 'roles', 'createTime']
    default_values = {'point': 0, 'status': UserStatus.NORMAL, 'roles': [UserRole.MEMBER], 'createTime': datetime.now}
    formats = {'intro': Format.TEXTAREA, 'avatar': Format.IMAGE, 'roles': Format.SELECT}
    searchables = [('name', Comparator.LIKE), 'email', 'point', 'status']
    columns = ['avatar', 'name', 'email', 'point', 'status', 'roles', 'createTime']
    indexes = [{'fields': ['email'], 'unique': True}]

    @cached_property
    def is_admin(self):
        return UserRole.ADMIN in self.roles

    @cached_property
    def is_editor(self):
        return UserRole.EDITOR in self.roles

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
