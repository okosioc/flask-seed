# -*- coding: utf-8 -*-
"""
    test_crud
    ~~~~~~~~~~~~~~

    Test cases for crud.

    :copyright: (c) 2018 by fengweimin.
    :date: 2018/5/15
"""

from app.models import User


def test_user(app):
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
    user.name = 'test1'
    user.save()
    assert User.find_one({'name': 'test1'}).name == 'test1'
    # D
    assert user.delete()
    # Verify
    assert User.count({}) == 0
