# -*- coding: utf-8 -*-
"""
    test_schema
    ~~~~~~~~~~~~~~

    Test cases for schema.

    :copyright: (c) 2019 by weiminfeng.
    :date: 2019/11/4
"""
from datetime import datetime

import pytest

from app.core import IN, SchemaDict, SeedDataError


class TestStatus:
    NORMAL = 'normal'
    REJECTED = 'rejected'


class UserDict(SchemaDict):
    schema = {
        'name': str,
        'point': int,
        'status': IN(TestStatus.NORMAL, TestStatus.REJECTED),
        'roles': [int],
        'accounts': [{
            'id': str,
            'name': str,
            'balance': float,
        }],
        'createTime': datetime,
    }
    required_fields = ['name', 'point', 'status', 'roles', 'createTime', 'accounts.id']
    default_values = {
        'point': 0,
        'status': TestStatus.NORMAL,
        'roles': [1],
        'accounts.balance': 0.0,
        'createTime': datetime.now,
    }


def test_schema_dict(app):
    ud = UserDict()

    # Test default values
    assert ud.point == 0
    assert ud['point'] == 0
    assert ud.status == TestStatus.NORMAL
    assert ud.roles[0] == 1
    assert ud.accounts[0].balance == 0.0

    # Test validate
    with pytest.raises(SeedDataError, match='name') as excinfo:
        ud.validate()
    # print(excinfo.value)
    ud.name = 'test'

    with pytest.raises(SeedDataError, match='accounts\.id') as excinfo:
        ud.validate()
    # print(excinfo.value)
    ud.accounts[0].id = 'test'

    ud.status = 'DELETED'
    with pytest.raises(SeedDataError, match='status') as excinfo:
        ud.validate()
    # print(excinfo.value)
    ud.status = TestStatus.NORMAL

    # Test json
    td_json = ud.to_json()
    td2 = UserDict.from_json(td_json)
    assert ud.createTime == td2.createTime
