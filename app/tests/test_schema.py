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

from app.core import IN, SchemaDict, DataError


class TestStatus:
    NORMAL = 'normal'
    REJECTED = 'rejected'


class TestDict(SchemaDict):
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
    td = TestDict()

    # Test default values
    assert td.point == 0
    assert td['point'] == 0
    assert td.status == TestStatus.NORMAL
    assert td.roles[0] == 1
    assert td.accounts[0].balance == 0.0

    # Test validate
    with pytest.raises(DataError, match='name') as excinfo:
        td.validate()
    # print(excinfo.value)
    td.name = 'test'

    with pytest.raises(DataError, match='accounts\.id') as excinfo:
        td.validate()
    # print(excinfo.value)
    td.accounts[0].id = 'test'

    td.status = 'DELETED'
    with pytest.raises(DataError, match='status') as excinfo:
        td.validate()
    # print(excinfo.value)
    td.status = TestStatus.NORMAL

    # Test json
    td_json = td.to_json()
    td2 = TestDict.from_json(td_json)
    assert td.createTime == td2.createTime

