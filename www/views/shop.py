""" shop module. """

from flask import Blueprint, render_template

from www.tools import auth_permission

shop = Blueprint('shop', __name__)


@shop.route('/index')
@auth_permission
def index():
    """ 商城. """
    return render_template('shop/index.html')


@shop.route('/index-asymmetric')
@auth_permission
def index_asymmetric():
    """ 商城. """
    return render_template('shop/index-asymmetric.html')


@shop.route('/index-horizontal')
@auth_permission
def index_sidenav():
    """ 商城. """
    return render_template('shop/index-horizontal.html')
