""" shop module. """
from datetime import datetime

from bson import ObjectId
from flask import Blueprint, render_template, current_app, redirect, request, abort, jsonify, url_for
from flask_login import current_user

from py3seed import populate_model, populate_search
from .common import get_id
from www.tools import auth_permission
from www.models import Block


shop = Blueprint('shop', __name__)


@shop.route('/index')
@auth_permission
def index():
    """ 商城. """
    id_ = get_id(int)
    block = Block.find_one(id_)
    if not block:
        abort(404)
    #
    return render_template('shop/index.html', block=block)


@shop.route('/index-asymmetric')
@auth_permission
def index_asymmetric():
    """ 商城. """
    id_ = get_id(int)
    block = Block.find_one(id_)
    if not block:
        abort(404)
    #
    return render_template('shop/index-asymmetric.html', block=block)


@shop.route('/index-horizontal')
@auth_permission
def index_horizontal():
    """ 商城. """
    id_ = get_id(int)
    block = Block.find_one(id_)
    if not block:
        abort(404)
    #
    return render_template('shop/index-horizontal.html', block=block)


