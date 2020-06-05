DOMAIN = 'flask-seed.com'

ENV = 'production'
DEBUG = False
SECRET_KEY = '<FIXME>'

CACHE_TYPE = "simple"
CACHE_DEFAULT_TIMEOUT = 300
CACHE_THRESHOLD = 10240

ACCEPT_LANGUAGES = ['en', 'zh']

BABEL_DEFAULT_LOCALE = 'en'
BABEL_DEFAULT_TIMEZONE = 'UTC'

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

UPLOAD_ENDPOINT = '//upload.qiniup.com/'
UPLOAD_BASE = '//cdn.flask-seed.com'
UPLOAD_BUCKET = 'flask-seed'
UPLOAD_AK = '<FIXME>'
UPLOAD_SK = '<FIXME>'
UPLOAD_IMAGE_EXTS = ['jpg', 'jpeg', 'png']
UPLOAD_IMAGE_MAX = '10mb'
UPLOAD_IMAGE_PREVIEW = '?imageView2/1/w/300/h/300/q/75'
UPLOAD_IMAGE_NORMAL = '?imageView2/1/w/600/q/75'
