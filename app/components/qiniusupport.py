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
    def __init__(self, app=None):
        self.app = app
        self.auth = None
        self.bucket = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        self.auth = qiniu.Auth(app.config['QINIU_AK'], app.config['QINIU_SK'])
        self.bucket = app.config['QINIU_BUCKET']

    def token(self, policy=None):
        """
        生成token.
        """
        # 上传策略, 可以设置持久化逻辑, 比如进行视频的预处理
        # https://developer.qiniu.com/kodo/manual/1208/upload-token

        # 默认过期时间为3600秒
        return self.auth.upload_token(self.bucket, policy=policy)

    def upload_data(self, key, data, **kwargs):
        """
        上传数据.
        注: 七牛没有文件夹的概念, 其自身定位是对象存储, 所以只有key这个字段.
        """
        ret, info = qiniu.put_data(self.token(), key, data, **kwargs)
        if ret:
            return self.url(ret['key'])
        else:
            self.app.logger.error('Failed when uploading data, error info %s' % info)
            return None

    def upload_stream(self, key, input_stream, file_name, data_size, **kwargs):
        """
        上传本地的文件.
        """
        ret, info = qiniu.put_stream(self.token(), key, input_stream, file_name, data_size, **kwargs)
        if ret:
            return self.url(ret['key'])
        else:
            self.app.logger.error('Failed when uploading stream, error info %s' % info)
            return None

    def upload_file(self, key, file, **kwargs):
        """
        上传本地的文件.
        """
        ret, info = qiniu.put_file(self.token(), key, file, **kwargs)
        if ret:
            return self.url(ret['key'])
        else:
            self.app.logger.error('Failed when uploading file, error info %s' % info)
            return None

    def url(self, key):
        """
        生成完整路径.
        """
        return '%s/%s' % (self.app.config['QINIU_BASE_URL'], key)
