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
from flask import Flask, g, request, redirect, jsonify, url_for, render_template, session, has_request_context
from flask_babel import Babel, gettext as _
from flask_login import LoginManager, current_user
from flask_principal import Principal, identity_loaded
from flask_uploads import patch_request_class, UploadConfiguration
from werkzeug.urls import url_quote

from app import views
from app.extensions import mail, cache, mdb, uploads, qiniu
from app.jobs import init_schedule
from app.models import User
from app.mongosupport import MongoSupportJSONEncoder
from app.tools import SSLSMTPHandler, helpers
from app.tools.converters import ListConverter, BSONObjectIdConverter

DEFAULT_APP_NAME = 'app'

DEFAULT_BLUEPRINTS = (
    (views.public, ''),
    (views.admin, '/admin'),
    (views.crud, '/crud'),
    (views.blog, '/blog'),
    (views.seo, '/seo')
)


def create_app(blueprints=None, pytest=False, runscripts=False):
    if blueprints is None:
        blueprints = DEFAULT_BLUEPRINTS

    app = Flask(DEFAULT_APP_NAME, instance_relative_config=True)

    # Json Encoder
    app.json_encoder = MongoSupportJSONEncoder

    # Url converter
    app.url_map.converters['list'] = ListConverter
    app.url_map.converters['ObjectId'] = BSONObjectIdConverter

    # Config
    app.config.from_object('app.config')
    app.config.from_pyfile('config.py')
    if pytest:
        # Use test db
        app.config['MONGODB_DATABASE'] = 'pytest'

    # Chain
    configure_extensions(app)
    configure_login(app)
    configure_identity(app)
    configure_logging(app)
    configure_errorhandlers(app)
    configure_before_handlers(app)
    configure_template_filters(app)
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
    qiniu.init_app(app)
    mdb.init_app(app)


def configure_login(app):
    login_manager = LoginManager(app)

    @login_manager.user_loader
    def load_user(user_id):
        # Reload the user object from the user ID stored in the session
        return User.find_one({'_id': ObjectId(user_id)})


def configure_identity(app):
    Principal(app)

    @identity_loaded.connect_via(app)
    def on_identity_loaded(sender, identity):
        # Set the identity user object
        identity.user = current_user

        # Add the UserNeed to the identity
        if hasattr(current_user, 'provides'):
            identity.provides.update(current_user.provides)


def configure_uploads(app):
    """
    文件上传支持.
    将图片直接保存在static目录之下, 因此在生产环境中可以直接由nginx提供服务.
    注意没有调用flask_uploads的configure_uploads(), 这个方法负责为每个uploadset生成UploadConfiguration, 并且注册一个blueprint用来生成上传后的url.
    所以直接初始化UploadConfiguration, 注意在上传完文件后要使用url_for('static', filename=[])来生成url.
    """
    # 设置上传目标路径, 无需通过配置文件设置一个绝对路径
    uploads._config = UploadConfiguration(os.path.join(app.root_path, 'static', 'uploads'))
    # 限制上传文件大小
    patch_request_class(app, 10 * 1024 * 1024)


def configure_i18n(app):
    babel = Babel(app)

    @babel.localeselector
    def get_locale():
        if has_request_context() and request:
            # 某个请求加了此参数, 则保存到session中, 优先使用此locale
            l = request.args.get('_locale', None)
            if l:
                accept_languages = app.config.get('ACCEPT_LANGUAGES')
                if l not in accept_languages:
                    l = request.accept_languages.best_match(accept_languages)
                session['_locale'] = l

            # 从Session中读取locale, 没有则读取默认值
            sl = session.get('_locale', app.config.get('BABEL_DEFAULT_LOCALE'))
            return sl
        else:
            return None


def configure_schedulers(app):
    init_schedule(app)


def configure_context_processors(app):
    """
    Context processors run before the template is rendered and inject new values into the template context.
    """

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
        """Add commas to an number."""
        if type(value) is int:
            return '{:,d}'.format(value)
        else:
            return "{:,.2f}".format(value)

    @app.template_filter()
    def urlquote(value, charset='utf-8'):
        """Url Quote."""
        return url_quote(value, charset)


def configure_before_handlers(app):
    @app.before_request
    def authenticate():
        g.user = getattr(g.identity, 'user', None)

    @app.before_request
    def set_device():
        """
        设置浏览的设备.
        """
        mobile_agents = re.compile('android|fennec|iemobile|iphone|opera (?:mini|mobi)|mobile')
        ua = request.user_agent.string.lower()
        platform = request.user_agent.platform
        request.MOBILE = True if mobile_agents.search(ua) else False
        request.IPHONE = True if platform == 'iphone' else False
        request.ANDROID = True if platform == 'android' else False


def configure_errorhandlers(app):
    @app.errorhandler(400)
    def server_error(error):
        if request.is_xhr:
            return jsonify(success=False, message=_('Bad request!'))
        return render_template('errors/400.html', error=error), 400

    @app.errorhandler(401)
    def unauthorized(error):
        if request.is_xhr:
            return jsonify(success=False, message=_('Login required!'))
        return redirect(url_for('public.login', next=request.path))

    @app.errorhandler(403)
    def forbidden(error):
        if request.is_xhr:
            return jsonify(success=False, message=_('Sorry, Not allowed or forbidden!'))
        return render_template('errors/403.html', error=error), 403

    @app.errorhandler(404)
    def page_not_found(error):
        if request.is_xhr:
            return jsonify(success=False, message=_('Sorry, page not found!'))
        return render_template('errors/404.html', error=error), 404

    @app.errorhandler(500)
    def server_error(error):
        if request.is_xhr:
            return jsonify(success=False, message=_('Sorry, an error has occurred!'))
        return render_template('errors/500.html', error=error), 500


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

    # 产品模式时才发送错误邮件
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

    # Flask运行在产品模式时, 只会输出ERROR, 此处使之输入INFO
    if not app.debug:
        app.logger.setLevel(logging.INFO)
