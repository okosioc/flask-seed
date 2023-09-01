# -*- coding: utf-8 -*-
"""
    public
    ~~~~~~~~~~~~~~

    Public view.

    :copyright: (c) 2021 by weiminfeng.
    :date: 2023/8/31
"""
import os
from datetime import datetime

from flask import Blueprint, render_template, current_app, redirect, request, abort, jsonify, url_for
from flask_babel import gettext as _
from flask_login import login_user, logout_user, login_required
from flask_wtf import FlaskForm
from werkzeug.datastructures import FileStorage
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from wtforms import StringField, PasswordField, BooleanField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Regexp

from core.models import DemoUser, DemoUserRole
from www.commons import send_support_email, editor_permission

public = Blueprint('public', __name__, url_prefix='')


@public.route('/')
def index():
    """ 首页. """
    return render_template('public/index.html')


@public.route('/400')
@public.route('/403')
@public.route('/404')
@public.route('/500')
def error():
    """ 错误页面. """
    abort(int(request.path.strip('/')))


@public.route('/dashboard')
def dashboard():
    """ 仪表盘. """
    return redirect(url_for('demo.project_dashboard'))


# ----------------------------------------------------------------------------------------------------------------------
# Login/Signup
#

class LoginForm(FlaskForm):
    """ 登录表单. """
    email = StringField('email', validators=[
        DataRequired(_('Email is required!')),
        Email(_('Invalid email address!'))
    ])
    password = PasswordField('password', validators=[DataRequired(_('Password is required!'))])
    remember = BooleanField('remember')
    next_url = HiddenField('next')


@public.route('/login', methods=('GET', 'POST'))
def login():
    """ 登录. """
    form = LoginForm()
    #
    if form.validate_on_submit():
        em = form.email.data.strip().lower()
        u = DemoUser.find_one({'email': em})
        if not u or not check_password_hash(u.password, form.password.data):
            form.email.errors.append('登录邮箱或者登录密码不匹配')
            return render_template('public/login.html', form=form)
        # Keep the user info in the session using Flask-Login
        login_user(u, remember=form.remember.data)
        # TODO: Validate next url
        next_url = form.next_url.data
        if not next_url:
            next_url = '/'
        return redirect(next_url)
    #
    next_url = request.args.get('next', '')
    form.next_url.data = next_url
    return render_template('public/login.html', form=form)


@public.route('/logout')
@login_required
def logout():
    """ Logout. """
    logout_user()
    return redirect("/")


class SignupForm(FlaskForm):
    """ 注册表单. """
    email = StringField('email', validators=[
        DataRequired(_('Email is required!')),
        Email(_('Invalid email address!'))
    ])
    password = PasswordField('password', validators=[
        DataRequired(_('Password is required!')),
        Regexp(r'^(?=.{8,16}$)(?=.*[a-zA-Z])(?=.*[0-9]).*', 0,
               _('Password length should between 8 and 16, and should contains at least one letter and one number!'))
    ])
    repassword = PasswordField('repassword', validators=[
        DataRequired(_('Password is required!')),
        EqualTo('password', _('Password mismatched!'))
    ])
    agree = BooleanField('agree', validators=[DataRequired(_('Please agree our terms and conditions!'))])


@public.route('/signup', methods=('GET', 'POST'))
def signup():
    """ 注册. """
    form = SignupForm()
    #
    if form.validate_on_submit():
        em = form.email.data.strip().lower()
        pwd = form.password.data.strip()
        u = DemoUser.find_one({'email': em})
        if u:
            form.email.errors.append('该登录邮箱已经注册!')
            return render_template('public/signup.html', form=form)
        # Create user
        u = DemoUser()
        u.email = em
        u.password = generate_password_hash(pwd)
        u.name = u.email.split('@')[0]
        u.avatar = url_for('static', filename='img/avatar.jpg')
        count = DemoUser.count({})
        # Set first signup user to admin
        if count == 0:
            u.roles = [DemoUserRole.MEMBER, DemoUserRole.ADMIN]
            current_app.logger.info('First user, set it to admin')
        else:
            current_app.logger.info('Current number of users is %s' % count)
        #
        u.save()
        current_app.logger.info(f'A new user created: {u}')
        send_support_email('signup()', f'New user {u}')
        # Keep the user info in the session using Flask-Login
        login_user(u)
        return redirect('/')
    #
    return render_template('public/signup.html', form=form)


# TODO: Forget password?


@public.route('/upload', methods=('POST',))
@editor_permission
def upload_file():
    """ Create a simple upload service.

    In production env we should not use python web server to serve static files directly,
    and we alwasys use nginx to serve the static folder, so simply use its sub folder to store upload files.

    It is also suggested to use a storage service to store your files, such us aws s3.
    """
    if 'file' not in request.files:
        abort(400)
    file = request.files['file']
    if not isinstance(file, FileStorage) or '.' not in file.filename:
        abort(400)
    ext = file.filename.rsplit('.', 1)[1].lower()
    mine_exts = [m.split('/')[1] for m in current_app.config['UPLOAD_MIMES']]
    if ext not in mine_exts:
        abort(400)
    #
    filename = secure_filename(file.filename)
    key = '%s/%s/%s' % (current_app.config['UPLOAD_FOLDER'], datetime.now().strftime('%Y%m%d'), filename)
    path = os.path.join(current_app.root_path, 'static', key)
    parent = os.path.dirname(path)
    if not os.path.exists(parent):
        os.makedirs(parent)
    #
    file.save(path)
    return jsonify(key=key, url=url_for('static', filename=key), name=filename)
