# -*- coding: utf-8 -*-
"""
    conftest
    ~~~~~~~~~~~~~~

    Sharing fixture functions.

    :copyright: (c) 2018 by fengweimin.
    :date: 2018/5/8
"""

import pytest

from www import create_www


@pytest.fixture
def app():
    """ Prepare a app for each testing, using testing db pytest. """
    app = create_www(pytest=True)
    return app


@pytest.fixture
def client(app):
    """ Creates a test client for this application. """
    return app.test_client()
