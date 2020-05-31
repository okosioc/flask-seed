# -*- coding: utf-8 -*-
"""
    dashboard
    ~~~~~~~~~~~~~~

    # Enter description here

    :copyright: (c) 2019 by weiminfeng.
    :date: 2020/5/31
"""
from flask import Blueprint, render_template

dashboard = Blueprint('dashboard', __name__)
PAGE_COUNT = 15
MAX_PAGE = 20


@dashboard.route('/')
def index():
    """ Index page. """
    return render_template('dashboard/index.html')


@dashboard.route('/blank')
def blank():
    """ Blank page. """
    return render_template('dashboard/blank.html')
