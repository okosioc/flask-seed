# -*- coding: utf-8 -*-
"""
    public.py
    ~~~~~~~~~~~~~~

    Public pages/actions.

    :copyright: (c) 2016 by fengweimin.
    :date: 16/5/12
"""

from flask import Blueprint, render_template, current_app, session, redirect, request
from flask_babel import gettext as _
from flask_login import login_user, logout_user, login_required
from flask_principal import identity_changed, Identity, AnonymousIdentity
from flask_wtf import Form
from werkzeug.security import check_password_hash, generate_password_hash
from wtforms import StringField, PasswordField, BooleanField, HiddenField
from wtforms.validators import DataRequired, Email

from app.models import User, UserRole
from app.tools import send_support_email

public = Blueprint('public', __name__)


@public.route('/')
def index():
    """
    Index page.
    """
    return render_template('public/index.html')


@public.route('/blank')
def blank():
    """
    Blank page.
    """
    return render_template('public/blank.html')


@public.route('/styleguide')
def styleguide():
    """
    Blank page.
    """
    return render_template('public/styleguide.html')


# ----------------------------------------------------------------------------------------------------------------------
# Login/Signup
#

class LoginForm(Form):
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired()])
    remember = BooleanField('remember')
    next_url = HiddenField('next')


@public.route('/login', methods=('GET', 'POST'))
def login():
    """
    Login.
    """
    form = LoginForm()

    if form.validate_on_submit():
        em = form.email.data.strip().lower()
        u = User.find_one({'email': em})
        if not u or not check_password_hash(u.password, form.password.data):
            return render_template('public/login.html', form=form, error=_('User name or password incorrect!'))

        # Keep the user info in the session using Flask-Login
        login_user(u)

        # Tell Flask-Principal the identity changed
        identity_changed.send(current_app._get_current_object(), identity=Identity(u.get_id()))

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
    """
    Logout.
    """
    logout_user()

    # Remove session keys set by Flask-Principal
    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)

    # Tell Flask-Principal the user is anonymous
    identity_changed.send(current_app._get_current_object(), identity=AnonymousIdentity())

    return redirect("/")


class SignupForm(Form):
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired()])
    repassword = PasswordField('repassword', validators=[DataRequired()])
    agree = BooleanField('agree', validators=[DataRequired(_('Please agree our service policy!'))])


@public.route('/signup', methods=('GET', 'POST'))
def signup():
    """
    Signup.
    """
    form = SignupForm()

    if form.validate_on_submit():
        if not form.password.data == form.repassword.data:
            return render_template('public/signup.html', form=form, error=_('Password dismatch!'))

        em = form.email.data.strip().lower()
        u = User.find_one({'email': em})
        if u:
            return render_template('public/signup.html', form=form, error=_('This email has been registered!'))

        u = User()
        u.email = em
        u.password = generate_password_hash(form.password.data.strip())
        u.name = u.email.split('@')[0]

        count = User.count({})
        # Set first signup user to admin
        if count == 0:
            u.roles = [UserRole.MEMBER, UserRole.ADMIN]
            current_app.logger.info('First user, set it to admin')
        else:
            current_app.logger.info('Current number of users is %s' % count)

        u.save()

        current_app.logger.info('A new user created, %s' % u)
        send_support_email('signup()', 'New user %s with id %s.' % (u.email, u._id))

        # Keep the user info in the session using Flask-Login
        login_user(u)

        # Tell Flask-Principal the identity changed
        identity_changed.send(current_app._get_current_object(), identity=Identity(u.get_id()))

        return redirect('/')

    return render_template('public/signup.html', form=form)
