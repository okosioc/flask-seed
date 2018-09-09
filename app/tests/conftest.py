# -*- coding: utf-8 -*-
"""
    conftest
    ~~~~~~~~~~~~~~

    Sharing fixture functions.

    :copyright: (c) 2018 by fengweimin.
    :date: 2018/5/8
"""

import pytest

from app import create_app


@pytest.fixture
def app():
    """
    为每个测试配置一个app, 使用测试用的数据库.
    """
    app = create_app(pytest=True)
    return app


@pytest.fixture
def client(app):
    """
    用于测试app的客户端模拟.
    """
    return app.test_client()
