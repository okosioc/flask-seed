# -*- coding: utf-8 -*-
"""
    qiniusupport
    ~~~~~~~~~~~~~~

    Qiniu client wrapper.

    https://developer.qiniu.com/kodo/sdk/1242/python

    :copyright: (c) 2018 by fengweimin.
    :date: 2018/3/21
"""

import qiniu


class QiniuSupport(object):
    """ This class is a wrapper of Qiniu client. """

    def __init__(self, app=None):
        self.app = app
        self.auth = None
        self.bucket = None
        self.base = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        self.auth = qiniu.Auth(app.config['UPLOAD_AK'], app.config['UPLOAD_SK'])
        self.bucket = app.config['UPLOAD_BUCKET']
        self.base = app.config['UPLOAD_BASE']

    def token(self, policy=None):
        """ Create upload token using policy.

        https://developer.qiniu.com/kodo/manual/1208/upload-token
        """
        return self.auth.upload_token(self.bucket, policy=policy)

    def gen_token(self):
        """ Create upload token.

        https://developer.qiniu.com/kodo/manual/1206/put-policy
        https://developer.qiniu.com/kodo/manual/1235/vars#magicvar
        """
        policy = {
            # Config unit is megabyte
            'fsizeLimit': self.app.config['UPLOAD_MAX'] * 1024 * 1024,
            'mimeLimit': ';'.join(self.app.config['UPLOAD_MIMES']),
            # Please keep ext in the last position because some callback/render logic depend on it
            'saveKey': '${year}${mon}${day}/${etag}${ext}',
            'returnBody': '{'
                          '"etag":"${etag}",'
                          '"name":"${fname}",'
                          '"key":"${key}",'
                          '"url":"%s/${key}",'
                          '"width":${imageInfo.width},'
                          '"height":${imageInfo.height}'
                          '}' % self.base
        }
        return self.token(policy)

    def upload_data(self, key, data, **kwargs):
        """ Upload data.

        NOTE: Qiniu is a key-value store
        """
        ret, info = qiniu.put_data(self.token(), key, data, **kwargs)
        if ret:
            return self.url(ret['key'])
        else:
            self.app.logger.error('Failed when uploading data, error info %s' % info)
            return None

    def upload_stream(self, key, input_stream, file_name, data_size, **kwargs):
        """ Upload stream. """
        ret, info = qiniu.put_stream(self.token(), key, input_stream, file_name, data_size, **kwargs)
        if ret:
            return self.url(ret['key'])
        else:
            self.app.logger.error('Failed when uploading stream, error info %s' % info)
            return None

    def upload_file(self, key, file, **kwargs):
        """ Upload file. """
        ret, info = qiniu.put_file(self.token(), key, file, **kwargs)
        if ret:
            return self.url(ret['key'])
        else:
            self.app.logger.error('Failed when uploading file, error info %s' % info)
            return None

    def url(self, key):
        """ Get full path of a qiniu key. """
        return '%s/%s' % (self.base, key)
