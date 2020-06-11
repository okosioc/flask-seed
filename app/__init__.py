# -*- coding: utf-8 -*-
"""
    __init__.py
    ~~~~~~~~~~~~~~

    Project Init.

    :copyright: (c) 2016 by fengweimin.
    :date: 16/6/11
"""

import logging
import os
import re
import socket
from datetime import datetime
from logging.handlers import SMTPHandler, TimedRotatingFileHandler

from bson.objectid import ObjectId
from flask import Flask, request, redirect, jsonify, url_for, render_template, session, has_request_context
from flask_babel import Babel
from flask_login import LoginManager
from werkzeug.urls import url_quote, url_encode

from app import views
from app.core import SchemaJSONEncoder
from app.extensions import mail, cache, mdb, qiniu
from app.jobs import init_schedule
from app.models import User
from app.tools import SSLSMTPHandler, helpers
from app.tools.converters import ListConverter, BSONObjectIdConverter

DEFAULT_APP_NAME = 'app'

DEFAULT_BLUEPRINTS = (
    (views.public, ''),
    (views.dashboard, '/dashboard'),
    (views.crud, '/crud'),
    (views.blog, '/blog'),
)


def create_app(blueprints=None, pytest=False, runscripts=False):
    if blueprints is None:
        blueprints = DEFAULT_BLUEPRINTS

    app = Flask(DEFAULT_APP_NAME, instance_relative_config=True)

    # Json Encoder
    app.json_encoder = SchemaJSONEncoder

    # Url converter
    app.url_map.converters['list'] = ListConverter
    app.url_map.converters['ObjectId'] = BSONObjectIdConverter

    # Config
    app.config.from_object('app.config')
    app.config.from_pyfile('config.py')
    if pytest:
        # Use test db
        app.config['MONGODB_URI'] = app.config['MONGODB_URI_PYTEST']

    # Chain
    configure_extensions(app)
    configure_login(app)
    configure_logging(app)
    configure_errorhandlers(app)
    configure_before_handlers(app)
    configure_template_filters(app)
    configure_template_functions(app)
    configure_context_processors(app)
    configure_i18n(app)
    if not pytest and not runscripts:  # Do not start schedules during testing
        configure_schedulers(app)
    configure_uploads(app)

    # Register blueprints
    configure_blueprints(app, blueprints)

    return app


def configure_extensions(app):
    mail.init_app(app)
    cache.init_app(app)
    mdb.init_app(app)


def configure_login(app):
    login_manager = LoginManager(app)

    @login_manager.user_loader
    def load_user(user_id):
        # Reload the user object from the user ID stored in the session
        return User.find_one({'_id': ObjectId(user_id)})


def configure_uploads(app):
    """ Configure upload settings. """
    endpoint = app.config['UPLOAD_ENDPOINT']
    is_local = re.match(r'^\/[a-z]+', endpoint)
    is_qiniu = 'qiniu' in endpoint

    if is_local:
        # https://flask.palletsprojects.com/en/1.1.x/patterns/fileuploads/#improving-uploads
        app.config['MAX_CONTENT_LENGTH'] = app.config['UPLOAD_IMAGE_MAX'] * 1024 * 1024  # Config unit is megabyte
    elif is_qiniu:
        qiniu.init_app(app)

    @app.context_processor
    def inject_upload_config():
        token = qiniu.image_token() if is_qiniu else ''
        uc = {
            'endpoint': endpoint,
            'image_exts': app.config['UPLOAD_IMAGE_EXTS'],
            'image_max': '%smb' % app.config['UPLOAD_IMAGE_MAX'],  # Config unit is megabyte
            'image_preview': app.config['UPLOAD_IMAGE_PREVIEW'],
            'image_normal': app.config['UPLOAD_IMAGE_NORMAL'],
            'image_token': token
        }
        return dict(upload_config=uc)


def configure_i18n(app):
    babel = Babel(app)

    @babel.localeselector
    def get_locale():
        if has_request_context() and request:
            # Request a locale and save to session
            rl = request.args.get('_locale', None)
            if rl:
                accept_languages = app.config.get('ACCEPT_LANGUAGES')
                if rl not in accept_languages:
                    rl = request.accept_languages.best_match(accept_languages)
                session['_locale'] = rl

            # Get locale from session, or return default locale
            return session.get('_locale', app.config.get('BABEL_DEFAULT_LOCALE'))
        else:
            return None


def configure_schedulers(app):
    init_schedule(app)


def configure_context_processors(app):
    """ Context processors run before the template is rendered and inject new values into the template context. """

    @app.context_processor
    def inject_config():
        return dict(config=app.config)

    @app.context_processor
    def inject_debug():
        return dict(debug=app.debug)


def configure_template_filters(app):
    @app.template_filter()
    def timesince(value):
        return helpers.timesince(value)

    @app.template_filter()
    def date(value):
        return helpers.date(value)

    @app.template_filter()
    def commas(value):
        """ Add commas to an number. """
        if type(value) is int:
            return '{:,d}'.format(value)
        else:
            return "{:,.2f}".format(value)

    @app.template_filter()
    def urlquote(value, charset='utf-8'):
        """ Url Quote. """
        return url_quote(value, charset)

    @app.template_filter()
    def keys(value):
        """ Return keys of dict. """
        return value.keys()

    @app.template_filter()
    def values(value):
        """ Return values of dict. """
        return value.values()

    @app.template_filter()
    def items(value):
        """ Return key-value pairs of dict. """
        return value.items()

    @app.template_filter()
    def split(value, separator):
        """ Split a string. """
        return value.split(separator)


def configure_template_functions(app):
    @app.template_global()
    def update_query(**new_values):
        """ Update query. """
        args = request.args.copy()
        for key, value in new_values.items():
            args[key] = value
        return '{}?{}'.format(request.path, url_encode(args))


def configure_before_handlers(app):
    @app.before_request
    def set_device():
        """ Set mobile device. """
        mobile_agents = re.compile('android|fennec|iemobile|iphone|opera (?:mini|mobi)|mobile')
        ua = request.user_agent.string.lower()
        platform = request.user_agent.platform
        request.MOBILE = True if mobile_agents.search(ua) else False
        request.IPHONE = True if platform == 'iphone' else False
        request.ANDROID = True if platform == 'android' else False

    @app.before_request
    def set_is_xhr():
        """ Set is_xhr. """
        request.is_xhr = request.accept_mimetypes.best == 'application/json'


def configure_errorhandlers(app):
    @app.errorhandler(400)
    def server_error(error):
        err = {
            'status': error.code,
            'title': 'Invalid Request',
            'content': 'Unexpected request received!'
        }
        if request.is_xhr:
            return jsonify(success=False, code=error.code, message='{content}({status})'.format(**err))
        return render_template('public/error.html', error=err), error.code

    @app.errorhandler(401)
    def unauthorized(error):
        err = {
            'status': error.code,
            'title': 'Please Login',
            'content': 'Login required!'
        }
        if request.is_xhr:
            return jsonify(success=False, code=error.code, message='{content}({status})'.format(**err))
        return redirect(url_for('public.login', next=request.path))

    @app.errorhandler(403)
    def forbidden(error):
        err = {
            'status': error.code,
            'title': 'Permission Denied',
            'content': 'Not allowed or forbidden!'
        }
        if request.is_xhr:
            return jsonify(success=False, code=error.code, message='{content}({status})'.format(**err))
        return render_template('public/error.html', error=err), error.code

    @app.errorhandler(404)
    def page_not_found(error):
        err = {
            'status': error.code,
            'title': 'Page Not Found',
            'content': 'The requested URL was not found on this server!'
        }
        if request.is_xhr:
            return jsonify(success=False, code=error.code, message='{content}({status})'.format(**err))
        return render_template('public/error.html', error=err), error.code

    @app.errorhandler(500)
    def server_error(error):
        err = {
            'status': error.code,
            'title': 'Internal Server Error',
            'content': 'Unexpected error occurred! Please try again later.'
        }
        if request.is_xhr:
            return jsonify(success=False, code=error.code, message='{content}({status})'.format(**err))
        return render_template('public/error.html', error=err), error.code


def configure_blueprints(app, blueprints):
    for blueprint, url_prefix in blueprints:
        app.register_blueprint(blueprint, url_prefix=url_prefix)


def configure_logging(app):
    subject = '[Error] %s encountered errors on %s' % (app.config['DOMAIN'], datetime.now().strftime('%Y/%m/%d'))
    hostname = socket.gethostname()
    subject += (' [%s]' % hostname if hostname else '')

    mail_config = [(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                   app.config['MAIL_DEFAULT_SENDER'], app.config['ADMINS'],
                   subject,
                   (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])]
    if app.config['MAIL_USE_SSL']:
        mail_handler = SSLSMTPHandler(*mail_config)
    else:
        mail_handler = SMTPHandler(*mail_config)

    # Only send email in productio mode
    if not app.debug:
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

    formatter = logging.Formatter(
        '%(asctime)s %(process)d-%(thread)d %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')

    debug_log = os.path.join(app.root_path, app.config['DEBUG_LOG'])
    debug_file_handler = TimedRotatingFileHandler(debug_log, when='midnight', interval=1, backupCount=90)
    debug_file_handler.setLevel(logging.DEBUG)
    debug_file_handler.setFormatter(formatter)
    app.logger.addHandler(debug_file_handler)

    error_log = os.path.join(app.root_path, app.config['ERROR_LOG'])
    error_file_handler = TimedRotatingFileHandler(error_log, when='midnight', interval=1, backupCount=90)
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(formatter)
    app.logger.addHandler(error_file_handler)

    # Set logging level to info in production mode
    if not app.debug:
        app.logger.setLevel(logging.INFO)
