# -*- coding: utf-8 -*-
"""
    dashboard
    ~~~~~~~~~~~~~~

    # Enter description here

    :copyright: (c) 2019 by weiminfeng.
    :date: 2020/5/31
"""
from datetime import datetime

from flask import Blueprint, render_template, current_app, abort, jsonify, request
from flask_login import current_user

from app.core import populate_model
from app.extensions import qiniu
from app.models import User
from app.tools import auth_permission

dashboard = Blueprint('dashboard', __name__)
PAGE_COUNT = 15
MAX_PAGE = 20


@dashboard.route('/')
@auth_permission
def index():
    """ Index page. """
    return render_template('dashboard/index.html')


@dashboard.route('/blank')
@auth_permission
def blank():
    """ Blank page. """
    return render_template('dashboard/blank.html')


@dashboard.route('/profile')
@auth_permission
def profile():
    """ Profile page. """
    return render_template('dashboard/profile.html', user=current_user, token=qiniu.image_token())


@dashboard.route('/save_basic/<ObjectId:uid>', methods=('POST',))
@auth_permission
def save_basic(uid):
    """ Save basic info for user. """
    try:
        user = populate_model(request.form, User)
        existing = User.find_one(uid)
        if not existing:
            abort(404)
        existing.name = user.name
        existing.intro = user.intro
        existing.avatar = user.avatar
        existing.updateTime = datetime.now()
        existing.save()
        current_app.logger.info('Successfully update basic info %s' % uid)
    except:
        current_app.logger.exception('Failed when saving basic info')
        return jsonify(success=False, message='Failed when saving basic info, please try again later!')

    return jsonify(success=True, message='Save basic info successfully.', uid=uid)
