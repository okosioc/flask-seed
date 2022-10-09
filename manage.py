# -*- coding: utf-8 -*-
"""
    manage.py
    ~~~~~~~~~~~~~~

    Manage scripts.

    :copyright: (c) 2016 by fengweimin.
    :date: 16/6/11
"""

from flask_script import Server, Shell, Manager

from www import create_www

www = create_www()
manager = Manager(www)

manager.add_command('runserver', Server('0.0.0.0', port=6060))


def _make_context():
    return dict(www=www)


manager.add_command('shell', Shell(make_context=_make_context))

if __name__ == '__main__':
    manager.run()
