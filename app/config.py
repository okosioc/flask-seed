DOMAIN = 'flask-seed.com'

ENV = 'production'
DEBUG = False
SECRET_KEY = 'this is a secret'

CACHE_TYPE = "simple"
CACHE_DEFAULT_TIMEOUT = 300
CACHE_THRESHOLD = 10240

ACCEPT_LANGUAGES = ['en', 'zh']

BABEL_DEFAULT_LOCALE = 'zh'
BABEL_DEFAULT_TIMEZONE = 'Asia/Shanghai'

DEBUG_LOG = 'logs/debug.log'
ERROR_LOG = 'logs/error.log'

ADMINS = ['okosioc@gmail.com']

MAIL_SERVER = 'smtp.mxhichina.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = ''
MAIL_PASSWORD = ''
MAIL_DEFAULT_SENDER = ''

MONGODB_DATABASE = 'flask-seed'
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
MONGODB_USERNAME = None
MONGODB_PASSWORD = None
