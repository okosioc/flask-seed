# -*- coding: utf-8 -*-
"""
    wsgi
    ~~~~~~~~~~~~~~

    Gunicorn wsgi.

    :copyright: (c) 2016 by fengweimin.
    :date: 16/6/30
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
