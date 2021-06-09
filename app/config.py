DOMAIN = 'flask-seed.com'

ENV = 'production'
DEBUG = False
SECRET_KEY = '<FIXME>'

CACHE_TYPE = "SimpleCache"
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

# Upload to Storage Service
UPLOAD_ENDPOINT = '//upload.qiniup.com/'
UPLOAD_BASE = '//cdn.flask-seed.com'
UPLOAD_BUCKET = 'flask-seed'
UPLOAD_AK = '<FIXME>'
UPLOAD_SK = '<FIXME>'
UPLOAD_MIMES = ['image/jpeg', 'image/png', 'image/gif',
                'video/quicktime', 'video/mp4', 'video/mpeg', 'video/webm',
                'audio/mpeg', 'audio/x-wav', 'audio/webm']
UPLOAD_MAX = 50
UPLOAD_IMAGE_PREVIEW_SM = '?imageMogr2/thumbnail/x200'
UPLOAD_IMAGE_PREVIEW_MD = '?imageMogr2/thumbnail/600x'
UPLOAD_VIDEO_POSTER_SM = '?vframe/jpg/offset/1/h/200'
# Upload to Local
# UPLOAD_ENDPOINT = '/upload'
# UPLOAD_FOLDER = 'uploads'
# UPLOAD_MIMES = ['image/jpeg', 'image/png']
# UPLOAD_MAX = 10
# UPLOAD_IMAGE_PREVIEW_SM = ''
# UPLOAD_IMAGE_PREVIEW_MD = ''
# UPLOAD_VIDEO_COVER_SM = ''
