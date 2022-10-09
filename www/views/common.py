# -*- coding: utf-8 -*-
"""
    common
    ~~~~~~~~~~~~~~

    公共视图逻辑.

    :copyright: (c) 2020 by weiminfeng.
    :date: 2020/12/12
"""

import os
import shutil
from typing import Type
from urllib.parse import urlparse

import requests
from flask import abort, request, current_app

from www.extensions import qiniu


def get_id(type_: Type):
    """ Try to get model id from request.args and request.form.  """
    id_ = request.values.get('id')
    if id_:
        try:
            id_ = type_(id_)
        except ValueError:
            abort(400)
    #
    return id_


def download_to_static(url, folder, save_as=None, overwrite=False, backup=False, request_session=None):
    """ 将url的资源现在到app/static/{folder}中.

    :param backup - 如果设置为True
    """
    static_folder = 'static'
    full_folder = os.path.join(current_app.root_path, static_folder, folder)
    os.makedirs(full_folder, exist_ok=True)
    fn = os.path.basename(urlparse(url).path)
    if save_as is None:
        save_as = fn
    else:
        if '.' not in save_as:
            save_as += os.path.splitext(fn)[1]
    #
    fk = f'{folder}/{save_as}'
    local_url = f'/{static_folder}/{fk}'
    # 下载到本地
    fp = os.path.join(full_folder, save_as)
    if overwrite or not os.path.exists(fp):
        if url.startswith('//'):
            url = f'http:{url}'
        #
        current_app.logger.info(f'Download {url} -> {fp}')
        if request_session is None:
            r = requests.get(url, stream=True, timeout=30)
        else:
            r = request_session.get(url, stream=True, timeout=30)
        #
        with open(fp, 'wb') as f:
            shutil.copyfileobj(r.raw, f)
    else:
        current_app.logger.info(f'File exists at {fp}')
    # 上传到七牛
    # 如果上传成功, 删除本地文件
    # 如果上传失败, 返回本地路径; 可以使用批处理的方式扫描数据结构中依然是有本地路径的地方, 进行重试
    if backup:
        current_app.logger.info(f'Upload output file as {fk}')
        backup_url = qiniu.upload_file(fk, fp)
        if backup_url:
            # 直接删除本地文件
            current_app.logger.info(f'Upload succesfully, try to delete local file at {fp}')
            os.remove(fp)
            #
            return backup_url
    #
    return local_url
