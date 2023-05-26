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
import random
import re
import socket
import string
from datetime import datetime
from importlib import import_module
from logging.handlers import SMTPHandler, TimedRotatingFileHandler
from urllib.parse import urlparse

from flask import Flask, request, redirect, jsonify, url_for, render_template, session, has_request_context, abort, current_app
from flask_babel import Babel
from flask_login import LoginManager
from py3seed import ModelJSONEncoder, connect, SimpleEnumMeta
from werkzeug.datastructures import MultiDict
from werkzeug.urls import url_quote, url_encode

from www import views
from www.blocks import BLOCKS
from www.extensions import mail, cache, qiniu
from www.jobs import init_schedule
from www.models import DemoUser, Block
from www.tools import SSLSMTPHandler, helpers, ListConverter, BSONObjectIdConverter

DEFAULT_APP_NAME = 'www'

DEFAULT_BLUEPRINTS = (
    (views.public, ''),
    (views.demo, '/demo'),
)

MODELS_MODULE = import_module('www.models')


def create_www(blueprints=None, pytest=False, runscripts=False):
    """ Create www instance. """
    if blueprints is None:
        blueprints = DEFAULT_BLUEPRINTS
    #
    app = Flask(DEFAULT_APP_NAME, instance_relative_config=True)
    # Json encoder
    app.json_encoder = ModelJSONEncoder
    # Url converter
    app.url_map.converters['list'] = ListConverter
    app.url_map.converters['ObjectId'] = BSONObjectIdConverter
    # Jinja whitespace control
    app.jinja_options['trim_blocks'] = True
    app.jinja_options['lstrip_blocks'] = True
    # Config
    app.config.from_object('www.config')
    app.config.from_pyfile('config.py')
    if pytest:
        # Use test db
        app.config['MONGODB_URI'] = app.config['MONGODB_URI_PYTEST']
    # Chain
    configure_logging(app)
    configure_errorhandlers(app)
    configure_blocks(app)
    configure_py3seed(app)
    configure_extensions(app)
    configure_login(app)
    configure_before_handlers(app)
    configure_template_filters(app)
    configure_template_functions(app)
    configure_context_processors(app)
    configure_i18n(app)
    configure_uploads(app)
    if not pytest and not runscripts:  # Do not start schedules during testing
        configure_schedulers(app)
    # Register blueprints
    configure_blueprints(app, blueprints)
    #
    return app


def configure_extensions(app):
    """ Prepare extensions. """
    mail.init_app(app)
    cache.init_app(app)


def configure_blocks(app):
    """ Prepare blocks. """
    keys = []
    for b in BLOCKS:
        blk = Block(b)
        blk.save()
        #
        keys.append(blk.key)
    #
    app.logger.debug(f'loaded {len(keys)} blocks: {keys}')


def configure_py3seed(app):
    """ Prepare db connection. """
    connect(app.config.get('MONGODB_URI'))


def configure_login(app):
    """ Prepare login. """
    login_manager = LoginManager(app)

    @login_manager.user_loader
    def load_user(user_id):
        """ Reload the user object from the user ID stored in the session. """
        return DemoUser.find_one(int(user_id))


def configure_uploads(app):
    """ Configure upload settings. """
    endpoint = app.config['UPLOAD_ENDPOINT']
    is_local = re.match(r'^\/[a-z]+', endpoint)
    is_qiniu = 'qiniu' in endpoint
    upload_max = app.config['UPLOAD_MAX']

    if is_local:
        # https://flask.palletsprojects.com/en/1.1.x/patterns/fileuploads/#improving-uploads
        app.config['MAX_CONTENT_LENGTH'] = upload_max * 1024 * 1024  # Config unit is megabyte
    elif is_qiniu:
        qiniu.init_app(app)

    @app.context_processor
    def inject_upload_config():
        """ Can use upload_config directly in template. """
        token = qiniu.gen_token() if is_qiniu else ''
        mimes = app.config['UPLOAD_MIMES']
        uc = {
            'endpoint': endpoint,
            'mimes': mimes,
            'mimes_image': [m for m in mimes if m.startswith('image')],
            'max': f'{upload_max}mb',  # Config unit is megabyte
            'image_preview_sm': app.config['UPLOAD_IMAGE_PREVIEW_SM'],
            'image_preview_md': app.config['UPLOAD_IMAGE_PREVIEW_MD'],
            'video_poster_sm': app.config['UPLOAD_VIDEO_POSTER_SM'],
            'token': token
        }
        return dict(upload_config=uc)


def configure_i18n(app):
    """ 国际化支持. """

    def get_locale():
        """ Guess locale. """
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

    #
    Babel(app, locale_selector=get_locale)


def configure_schedulers(app):
    """ Init jobs. """
    init_schedule(app)


def configure_context_processors(app):
    """ Context processors run before the template is rendered and inject new values into the template context. """

    @app.context_processor
    def inject_config():
        """ Can use config directly in template. """
        return dict(config=app.config)

    @app.context_processor
    def inject_debug():
        """ Can use debug directly in template. """
        return dict(debug=app.debug)


def configure_template_filters(app):
    """ 自定义Filter. """

    @app.template_filter()
    def timesince(value):
        """ 显示友好日期. """
        return helpers.timesince(value)

    @app.template_filter()
    def date(value):
        """ 显示日期. """
        if isinstance(value, str):
            return value
        #
        return helpers.date_str(value)

    @app.template_filter()
    def datetime(value):
        """ 显示日期时间. """
        if isinstance(value, str):
            return value
        #
        return helpers.datetime_str(value)

    @app.template_filter()
    def time(value):
        """ 显示时间. """
        if isinstance(value, str):
            return value
        #
        return helpers.time_str(value)

    @app.template_filter()
    def timedelta(value):
        """ 将秒转化为时钟格式. """
        if isinstance(value, str):
            return value
        #
        return helpers.timedelta_str(value)

    @app.template_filter()
    def commas(value):
        """ Add commas to an number. """
        if value is None:
            return ''
        # 打印小数点
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
    def index(value, element):
        """ Return index of the element, value should be a list. """
        try:
            return value.index(element)
        except ValueError:
            return -1

    @app.template_filter()
    def todict(value):
        """ Convert a list to dict. """
        if isinstance(value, list):
            return {i: v for i, v in enumerate(value)}
        else:
            return {}

    @app.template_filter()
    def urlquote(value, charset='utf-8'):
        """ Url Quote. """
        return url_quote(value, charset)

    @app.template_filter()
    def quote(value):
        """ Add single quote to value if it is str, else return its __str__. """
        if isinstance(value, str):
            return '\'' + value + '\''
        else:
            return str(value)

    @app.template_filter()
    def dirname(value):
        """ Return dir name from a path.
        e.g,
        /foo/bar/ -> /foo/bar
        /foo/bar -> /foo
        """
        return os.path.dirname(value)

    @app.template_filter()
    def basename(value):
        """ Return file name from a path.
        e.g,
        /foo/bar/ -> ''
        /foo/bar -> bar
        """
        return os.path.basename(value)

    @app.template_filter()
    def filename(value):
        """ Return file name from a path, without ext. """
        return os.path.splitext(value)[0]

    @app.template_filter()
    def split(value, separator):
        """ Split a string. """
        return value.split(separator)

    @app.template_filter()
    def path(value):
        """ Return the path part from a url. """
        return value.split('?')[0]

    @app.template_filter()
    def complete(url: str):
        """ 尝试补全一个url, i.e, 分享到微信时候需要完整的地址

        i.e:
        - 图片上传到七牛后地址不带scheme, e.g, //cdn.koiplan.com/20211224/Fovvi2-1jwL2j8pyBJcomk4iz5TJ.jpeg
        """
        # 以//开头的网址会解析域名, 否则会被认为是相对路径
        if url.startswith('//'):
            url += request.scheme + ':'
        #
        o = urlparse(url)
        ret = ''
        if not o.scheme:
            ret += request.scheme + '://'
        if not o.netloc:
            ret += request.host
        if url.startswith('/'):
            ret += url
        else:
            ret += '/' + url
        #
        return ret

    @app.template_filter()
    def tocolor(value: str):
        """ 将字符串转化为颜色代码, e.g, primary, secondary, success, info, danger, warning
        """
        if not value:
            return 'secondary'
        #
        if re.match(r'(normal|primary|pending|\w+able)', value, re.IGNORECASE):  # have something to do
            return 'primary'
        elif re.match(r'(active|running|online|success)', value, re.IGNORECASE):  # have something ran succsessfully
            return 'success'
        elif re.match(r'(error|fail\w+|reject\w+|offline|danger)', value, re.IGNORECASE):  # have something ran failed
            return 'danger'
        elif re.match(r'(overdue\w+|warning)', value, re.IGNORECASE):  # have something ran but has warning
            return 'warning'
        else:
            return 'secondary'  # something is done


def configure_template_functions(app):
    """ 自定义函数. """

    @app.template_global()
    def update_full_path(view):
        """ Update current full path, by supporting special commands.

        i.e, if current path is /dashboard/profile?uid=xxx&tab=password
        view=timeline -> timeline
        view=timeline? -> timeline?uid=xxx&index=0, keeping all queries
        view=timeline?uid -> timeline?uid=xxx, keeping the query with specified key
        """
        target_args = None
        if '?' in view:
            target_path = view[0:view.index('?')]
            needed_keys = view[view.index('?') + 1:].strip()
            if needed_keys:
                needed_keys = needed_keys.split('&')
            #
            current_args = request.args.deepcopy()
            if needed_keys:  # keeping the query with specified key
                target_args = MultiDict()
                for k, v in current_args.items(multi=True):
                    if k in needed_keys:  # case sensitive
                        target_args.add(k, v)
            else:  # keeping all queries
                target_args = current_args
        else:
            target_path = view
        #
        current_path = request.path
        if target_path == '<':
            # Back
            # i.e, pay-wechat -> pay
            if '-' in current_path:
                target_path = current_path[0:current_path.rindex('-')]
        #
        if target_args:
            target_path += '?' + url_encode(target_args)
        #
        return target_path

    @app.template_global()
    def current_query():
        """ Get current query string, as request.query_string returns bytes, which needs to encode manually. """
        args = request.args.copy()
        return url_encode(args)

    @app.template_global()
    def update_query(is_replace=True, **new_values):
        """ Update query string. """
        args = request.args.copy()
        for key, value in new_values.items():
            if value is None:
                pass
            else:
                if is_replace:
                    args[key] = value
                else:
                    args.update({key: value})
        #
        return url_encode(args)

    @app.template_global()
    def new_model(class_name):
        """ 初始化一个BaseModel. """
        klazz = getattr(MODELS_MODULE, class_name)
        return klazz()

    @app.template_global()
    def enum_titles(class_name):
        """ 返回枚举的可选项, {value:title}. """
        # 如果为数组则取内部的类型, i.e, List[DemoUserRole]
        inner = re.search(r'List\[([a-zA-Z]+)\]', class_name)
        if inner:
            class_name = inner.group(1)
        #
        klazz = getattr(MODELS_MODULE, class_name)
        if isinstance(klazz, SimpleEnumMeta):
            return klazz.titles
        else:
            return {}

    @app.template_global()
    def randstr(n=10):
        """ 生成长度为n的随机字符串. """
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=n))

    @app.template_global()
    def load_block(key):
        """ 读取页面板块内容. """
        b = Block.find_one({'key': key})
        if b is None:
            current_app.logger.error(f'Can not load block by {key}')
            abort(500)
        #
        return b


def configure_before_handlers(app):
    """ Injection before handling each request. """

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
        request.XHR = request.accept_mimetypes.best == 'application/json'


def configure_errorhandlers(app):
    """ Register error handlers. """

    @app.errorhandler(400)
    def server_error(error):
        """ 400. """
        err = {
            'status': error.code,
            'title': 'Invalid Request',
            'content': 'Unexpected request received!'
        }
        if request.XHR:
            return jsonify(error=error.code, message='{content}({status})'.format(**err))
        #
        return render_template('public/error.html', error=err), error.code

    @app.errorhandler(401)
    def unauthorized(error):
        """ 401. """
        err = {
            'status': error.code,
            'title': 'Please Login',
            'content': 'Login required!'
        }
        if request.XHR:
            return jsonify(error=error.code, message='{content}({status})'.format(**err))
        #
        return redirect(url_for('public.login', next=request.path))

    @app.errorhandler(403)
    def forbidden(error):
        """ 403. """
        err = {
            'status': error.code,
            'title': 'Permission Denied',
            'content': 'Not allowed or forbidden!'
        }
        if request.XHR:
            return jsonify(error=error.code, message='{content}({status})'.format(**err))
        #
        return render_template('public/error.html', error=err), error.code

    @app.errorhandler(404)
    def page_not_found(error):
        """ 404. """
        err = {
            'status': error.code,
            'title': 'Page Not Found',
            'content': 'The requested URL was not found on this server!'
        }
        if request.XHR:
            return jsonify(error=error.code, message='{content}({status})'.format(**err))
        #
        return render_template('public/error.html', error=err), error.code

    @app.errorhandler(500)
    def server_error(error):
        """ 500. """
        err = {
            'status': error.code,
            'title': 'Internal Server Error',
            'content': 'Unexpected error occurred! Please try again later.'
        }
        if request.XHR:
            return jsonify(error=error.code, message='{content}({status})'.format(**err))
        #
        return render_template('public/error.html', error=err), error.code


def configure_blueprints(app, blueprints):
    """ Register all the blueprints. """
    for blueprint, url_prefix in blueprints:
        app.register_blueprint(blueprint, url_prefix=url_prefix)


def configure_logging(app):
    """ Config logging. """
    subject = '[Error] %s encountered errors on %s' % (app.config['DOMAIN'], datetime.now().strftime('%Y/%m/%d'))
    hostname = socket.gethostname()
    subject += (' [%s]' % hostname if hostname else '')
    mail_config = [(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                   app.config['MAIL_DEFAULT_SENDER'], app.config['ADMINS'],
                   subject,
                   (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])]
    #
    if app.config['MAIL_USE_SSL']:
        mail_handler = SSLSMTPHandler(*mail_config)
    else:
        mail_handler = SMTPHandler(*mail_config)
    # Only send email in production mode
    if app.env == 'production':
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)
    #
    formatter = logging.Formatter(
        '%(asctime)s %(process)d-%(thread)d %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    #
    debug_log = os.path.join(app.root_path, app.config['DEBUG_LOG'])
    debug_file_handler = TimedRotatingFileHandler(debug_log, when='midnight', backupCount=90)
    debug_file_handler.setLevel(logging.DEBUG)
    debug_file_handler.setFormatter(formatter)
    app.logger.addHandler(debug_file_handler)
    #
    error_log = os.path.join(app.root_path, app.config['ERROR_LOG'])
    error_file_handler = TimedRotatingFileHandler(error_log, when='midnight', backupCount=90)
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(formatter)
    app.logger.addHandler(error_file_handler)

    # Set logging level to info in production mode
    if app.env == 'production':
        app.logger.setLevel(logging.INFO)
    else:
        app.logger.setLevel(logging.DEBUG)
