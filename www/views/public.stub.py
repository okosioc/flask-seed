""" public module. """
from datetime import datetime

from bson import ObjectId
from flask import Blueprint, render_template, current_app, redirect, request, abort, jsonify, url_for
from flask_login import current_user

from py3seed import populate_model, populate_search
from .common import get_id
from www.tools import auth_permission
from www.models import Block


public = Blueprint('public', __name__)


@public.route('/index')
def index():
    """ 首页. """
    id_ = get_id(int)
    block = Block.find_one(id_)
    if not block:
        abort(404)
    #
    return render_template('public/index.html', block=block)


@public.route('/login')
def login():
    """ 登录. """
    return render_template('public/login.html')


@public.route('/signup')
def signup():
    """ 注册. """
    return render_template('public/signup.html')


@public.route('/error')
def error():
    """ 出错了. """
    return render_template('public/error.html')


