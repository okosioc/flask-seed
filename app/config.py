DOMAIN = 'flask-seed.com'

ENV = 'production'
DEBUG = False
SECRET_KEY = '<FIXME>'

CACHE_TYPE = "simple"
CACHE_DEFAULT_TIMEOUT = 300
CACHE_THRESHOLD = 10240

ACCEPT_LANGUAGES = ['en', 'zh']

BABEL_DEFAULT_LOCALE = 'zh'
BABEL_DEFAULT_TIMEZONE = 'Asia/Shanghai'

DEBUG_LOG = 'logs/debug.log'
ERROR_LOG = 'logs/error.log'

ADMINS = ['<FIXME>']
MAIL_SERVER = 'smtp.mxhichina.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = '<FIXME>'
MAIL_PASSWORD = '<FIXME>'
MAIL_DEFAULT_SENDER = '<FIXME>'

MONGODB_URI = 'mongodb://localhost:27017/flask-seed'
MONGODB_URI_PYTEST = 'mongodb://localhost:27017/pytest'

QINIU_AK = '<FIXME>'
QINIU_SK = '<FIXME>'
QINIU_BUCKET = 'flask-seed'
QINIU_BASE_URL = 'http://cdn.flask-seed.com'
