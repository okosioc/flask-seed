DOMAIN = 'flask-seed.com'
ENV = 'production'
SECRET_KEY = '<FIXME>'
# Cache
CACHE_TYPE = "simple"
CACHE_DEFAULT_TIMEOUT = 300
CACHE_THRESHOLD = 10240
# Locale
ACCEPT_LANGUAGES = ['en', 'zh']
BABEL_DEFAULT_LOCALE = 'zh'
BABEL_DEFAULT_TIMEZONE = 'UTC'
# Log
DEBUG_LOG = 'logs/debug.log'
ERROR_LOG = 'logs/error.log'
# Email
ADMINS = ['<FIXME>']
MAIL_SERVER = 'smtp.mxhichina.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = '<FIXME>'
MAIL_PASSWORD = '<FIXME>'
MAIL_DEFAULT_SENDER = '<FIXME>'
# DB
MONGODB_URI = 'mongodb://localhost:27017/flask-seed'
MONGODB_URI_PYTEST = 'mongodb://localhost:27017/pytest'
# Upload
# UPLOAD_ENDPOINT = '//upload.qiniup.com/'
# UPLOAD_BASE = '//cdn.flask-seed.com'
# UPLOAD_BUCKET = 'flask-seed'
# UPLOAD_AK = '<FIXME>'
# UPLOAD_SK = '<FIXME>'
# UPLOAD_MIMES = ['image/jpg', 'image/jpeg', 'image/png', 'image/gif',
#                 'video/quicktime', 'video/mp4', 'video/mpeg', 'video/webm',
#                 'audio/mpeg', 'audio/x-wav', 'audio/webm',
#                 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel']
# UPLOAD_MAX = 50
# UPLOAD_IMAGE_PREVIEW_SM = '?imageMogr2/thumbnail/x200'
# UPLOAD_IMAGE_PREVIEW_MD = '?imageMogr2/thumbnail/600x'
# UPLOAD_VIDEO_POSTER_SM = '?vframe/jpg/offset/1/h/200'
# Upload to Local
UPLOAD_ENDPOINT = '/upload'
UPLOAD_FOLDER = 'uploads'
UPLOAD_MIMES = ['image/jpg', 'image/jpeg', 'image/png', 'image/gif',
                'video/quicktime', 'video/mp4', 'video/mpeg', 'video/webm',
                'audio/mpeg', 'audio/x-wav', 'audio/webm']
UPLOAD_MAX = 50
UPLOAD_IMAGE_PREVIEW_SM = ''
UPLOAD_IMAGE_PREVIEW_MD = ''
UPLOAD_VIDEO_POSTER_SM = ''
