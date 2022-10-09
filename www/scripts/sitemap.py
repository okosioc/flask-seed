# -*- coding: utf-8 -*-
"""
    sitemap
    ~~~~~~~~~~~~~~

    Sitemap generation.

    关于sitemap的生成请参考, http://zhanzhang.baidu.com/college/courseinfo?id=267&page=2

    执行脚本:
    export PYTHONIOENCODING=utf-8
    python2.7 sitemap.py

    :copyright: (c) 2016 by fengweimin.
    :date: 16/10/14
"""

import os
import sys

import pymongo
from flask import current_app
from lxml import etree

sys.path.append(os.path.join(os.getcwd(), '../../'))

from app import create_app
from app.models import Post

LIMIT = 30000


def generate_site_map():
    """
    生成站点地图, 将站点地图保存在static文件夹中.
    """
    print('Try to generate site map ...')

    domain = current_app.config['DOMAIN']
    index = 0
    pending = ['http://%s/' % domain]

    cursor_post = Post.find({}, sort=[('_id', pymongo.DESCENDING)])
    for p in cursor_post:
        print('Generating post %s/%s' % (p._id, p.title))
        pending.append('http://%s/blog/post/%s' % (domain, p._id))
        if len(pending) >= LIMIT:
            write_site_map(index, pending)
            index += 1
            del pending[:]

    if len(pending) > 0:
        write_site_map(index, pending)


def write_site_map(index, urls):
    _write_site_map_txt(index, urls)


def _write_site_map_txt(index, urls):
    """
    生成txt格式的sitemap.
    """
    site_map_file = os.path.join(current_app.root_path, 'static', 'sitemap.%s.txt' % index)
    with open(site_map_file, 'w') as f:
        for u in urls:
            f.write(u + '\n')
    print('Successfully write sitemap file %s' % site_map_file)


def _write_site_map_xml(index, urls):
    """
    生成xml格式的sitemap.
    """
    site_map_file = os.path.join(current_app.root_path, 'static', 'sitemap.%s.xml' % index)
    urlset = etree.Element('urlset')
    for u in urls:
        url = etree.Element('url')
        loc = etree.Element('loc')
        loc.text = u
        lastmod = etree.Element('lastmod')
        lastmod.text = '2016-10-18'
        url.append(loc)
        url.append(lastmod)
        urlset.append(url)

    et = etree.ElementTree(urlset)
    et.write(site_map_file, pretty_print=True)

    print('Successfully write sitemap file %s' % site_map_file)


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        generate_site_map()
