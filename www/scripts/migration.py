# -*- coding: utf-8 -*-
"""
    migration
    ~~~~~~~~~~~~~~

    Database migration scripts

    :copyright: (c) 2021 by weiminfeng.
    :date: 2023/9/1
"""

import os
import sys

sys.path.append(os.path.join(os.getcwd(), '../../'))

from www import create_www


def do_something():
    """ do something. """
    print('Begin to do something...')


if __name__ == '__main__':
    app = create_www()
    with app.app_context():
        do_something()
