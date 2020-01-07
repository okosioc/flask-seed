# -*- coding: utf-8 -*-
"""
    test_mongosupport
    ~~~~~~~~~~~~~~

    Test cases for mongosupport.

    :copyright: (c) 2018 by fengweimin.
    :date: 2019/12/15
"""
from datetime import datetime

import pytest
from pymongo.errors import DuplicateKeyError
from werkzeug.datastructures import MultiDict

from app.core import SeedDataError, populate_model
from app.models import User, UserRole, UserStatus


def test_populate_model(app):
    md = MultiDict([
        ('user.name', 'test'),
        ('user.email', 'test@test.com'),
        ('user.password', 'test'),
        ('user.roles[0]', UserRole.MEMBER),
        ('user.roles[1]', UserRole.ADMIN),
        ('user.createTime', '2019-12-15 10:00:00')
    ])
    user = populate_model(md, User)

    assert user.point == 0
    assert user.status == UserStatus.NORMAL
    assert user.is_admin
    assert user.createTime < datetime.now()


def test_crud(app):
    # Init
    assert User.delete_many({})
    assert User.count({}) == 0
    # C
    user = User()
    user.name = 'test'
    user.email = 'test@test.com'
    user.password = 'test'
    user.save()
    assert User.count({}) == 1
    # R
    assert User.find_one({'name': 'test'}).name == 'test'

    # U
    del user.name
    # Validation
    with pytest.raises(SeedDataError, match='name') as excinfo:
        user.save()
    # print(excinfo.value)

    user.name = 'test1'
    # DulplicateKey from pymongo
    with pytest.raises(DuplicateKeyError) as excinfo:
        user.save(insert_with_id=True)
    # print(excinfo.value)

    user.save()
    assert User.find_one({'name': 'test1'}).name == 'test1'

    # D
    assert user.delete().deleted_count == 1

    # Verify
    assert User.count({}) == 0
