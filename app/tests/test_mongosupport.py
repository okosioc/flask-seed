# -*- coding: utf-8 -*-
"""
    test_crud
    ~~~~~~~~~~~~~~

    Test cases for mongosupport.

    :copyright: (c) 2018 by fengweimin.
    :date: 2018/5/15
"""
import pytest
from pymongo.errors import DuplicateKeyError

from app.core import SeedDataError
from app.models import User


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
