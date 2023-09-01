# -*- coding: utf-8 -*-
"""
    test_commons
    ~~~~~~~~~~~~~~

    Test cases for commons package.

    :copyright: (c) 2021 by weiminfeng.
    :date: 2023/9/1
"""
import pytest

from www.commons import retry


def test_retry():
    """ Test retry decorator. """
    count = 0

    @retry
    def do_something():
        """ Do something. """
        nonlocal count
        count += 1
        raise RuntimeError

    # After 3 times retry, it will raise a RuntimeError, need to catch it
    with pytest.raises(RuntimeError):
        do_something()
    #
    assert count == 3
