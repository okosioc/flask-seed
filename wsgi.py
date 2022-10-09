# -*- coding: utf-8 -*-
"""
    wsgi
    ~~~~~~~~~~~~~~

    Gunicorn wsgi.

    :copyright: (c) 2016 by fengweimin.
    :date: 16/6/30
"""

from www import create_www

www = create_www()

if __name__ == "__main__":
    www.run()
