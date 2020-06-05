# -*- coding: utf-8 -*-
"""
    public.py
    ~~~~~~~~~~~~~~

    Public pages/actions.

    :copyright: (c) 2016 by fengweimin.
    :date: 16/5/12
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

from app.extensions import qiniu
from app.models import User, UserRole
from app.tools import send_support_email, editor_permission

public = Blueprint('public', __name__)


@public.route('/')
def index():
    """ Index page. """
    return render_template('public/index.html')


@public.route('/blank')
def blank():
    """ Blank page. """
    return render_template('public/blank.html')


@public.route('/400')
@public.route('/403')
@public.route('/404')
@public.route('/500')
def error():
    """ Demo error pages. """
    abort(int(request.path.strip('/')))


# ----------------------------------------------------------------------------------------------------------------------
# Login/Signup
#

class LoginForm(FlaskForm):
    email = StringField('email', validators=[
        DataRequired(_('Email is required!')),
        Email(_('Invalid email address!'))
    ])
    password = PasswordField('password', validators=[DataRequired(_('Password is required!'))])
    remember = BooleanField('remember')
    next_url = HiddenField('next')


@public.route('/login', methods=('GET', 'POST'))
def login():
    """ Login. """
    form = LoginForm()

    if form.validate_on_submit():
        em = form.email.data.strip().lower()
        u = User.find_one({'email': em})
        if not u or not check_password_hash(u.password, form.password.data):
            form.email.erros.append(_('User name or password incorrect!'))
            return render_template('public/login.html', form=form)

        # Keep the user info in the session using Flask-Login
        login_user(u, remember=form.remember.data)

        # TODO: Validate next url
        next_url = form.next_url.data
        if not next_url:
            next_url = '/'
        return redirect(next_url)

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
    """ Signup. """
    form = SignupForm()

    if form.validate_on_submit():
        em = form.email.data.strip().lower()
        pwd = form.password.data.strip()
        u = User.find_one({'email': em})
        if u:
            form.email.erros.append(_('This email has been registered!'))
            return render_template('public/signup.html', form=form)
        # Create user
        u = User()
        u.email = em
        u.password = generate_password_hash(pwd)
        u.name = u.email.split('@')[0]
        u.avatar = qiniu.url('avatar.jpg')
        count = User.count({})
        # Set first signup user to admin
        if count == 0:
            u.roles = [UserRole.MEMBER, UserRole.ADMIN]
            current_app.logger.info('First user, set it to admin')
        else:
            current_app.logger.info('Current number of users is %s' % count)
        #
        u.save()

        current_app.logger.info('A new user created, %s' % u)
        send_support_email('signup()', 'New user %s with id %s.' % (u.email, u._id))

        # Keep the user info in the session using Flask-Login
        login_user(u)

        return redirect('/')

    return render_template('public/signup.html', form=form)


# TODO: Forget password?


@public.route('/upload', methods=('POST',))
@editor_permission
def upload_file():
    """ Create a simple upload service.

    NOTE: In production settings we always use nginx to serve the static folder,
    you should not use python web server to serve static files directly,
    so simply use its sub folder to store upload files.

    It is also suggested to use a storage service to store your files, such us aws s3 or qiniu.com.
    """
    if 'file' not in request.files:
        abort(400)
    file = request.files['file']
    if not isinstance(file, FileStorage) or '.' not in file.filename:
        abort(400)
    ext = file.filename.rsplit('.', 1)[1].lower()
    if ext not in current_app.config['UPLOAD_IMAGE_EXTS']:
        abort(400)
    filename = secure_filename(file.filename)
    key = '%s/%s/%s' % (current_app.config['UPLOAD_FOLDER'], datetime.now().strftime('%Y%m%d'), filename)
    path = os.path.join(current_app.root_path, 'static', key)
    parent = os.path.dirname(path)
    if not os.path.exists(parent):
        os.makedirs(parent)
    file.save(path)
    return jsonify(key=key, url=url_for('static', filename=key), name=filename)
