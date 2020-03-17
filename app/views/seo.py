# -*- coding: utf-8 -*-
"""
    seo
    ~~~~~~~~~~~~~~

    关键词管理相关.

    :copyright: (c) 2016 by fengweimin.
    :date: 16/8/16
"""
from datetime import datetime

import pymongo
import requests
from flask import Blueprint, render_template, request, abort, jsonify, current_app
from lxml import html
from werkzeug.urls import url_quote

from app.core import Pagination
from app.models import KeywordLevel, KeywordStatus, Keyword
from app.tools import async_exec, admin_permission

seo = Blueprint('seo', __name__)

PAGE_COUNT = 100

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
headers = {
    'User-Agent': user_agent,
    'Accept': 'application/json, text/javascript, text/html, */*; q=0.01',
    'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4,ja;q=0.2',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
    'Connection': 'keep-alive',
}
adapter = requests.adapters.HTTPAdapter(max_retries=5)
ss = requests.session()
ss.mount('http://', adapter)
ss.mount('https://', adapter)
ss.headers.update(headers)


@seo.route('/')
@seo.route('/index')
@admin_permission
def index():
    """
    关键词管理首页, 列举站点级别的关键词, 并支持简单查询和翻页.
    """
    s = request.args.get('status', 'bare,processed,repeated')
    k = request.args.get('keyword', '')
    o = request.args.get('owner', '')
    p = int(request.args.get('page', '1'))
    start = (p - 1) * PAGE_COUNT

    condition = {'level': KeywordLevel.SITE}
    if k:
        condition['name'] = k.strip()
    if o:
        condition['owner'] = o.strip()
    status = s.split(',')
    if status:
        condition['status'] = {'$in': status}

    count = Keyword.count(condition)
    cursor = Keyword.find(condition, skip=start, limit=PAGE_COUNT, sort=[('baiduIndex', pymongo.DESCENDING)])
    keywords = []
    for c in cursor:
        set_index(c)
        keywords.append(c)
    pagination = Pagination(p, PAGE_COUNT, count)
    return render_template('seo/index.html', keywords=keywords, pagination=pagination)


def set_index(k):
    """
    设置关键字的优化难易度, 仅供参考.
    """
    if k.baiduResult != 0:
        index = float(k.baiduIndex) / k.baiduResult
    else:
        index = 0
    k.index = round(index * 10000, 1)


@seo.route('/longtail/<ObjectId:keyword_id>')
@admin_permission
def longtail(keyword_id):
    """
    获取指定站点关键字下的长尾关键字.
    """
    keyword = Keyword.find_one({'_id': keyword_id})
    if not keyword:
        abort(404)

    s = request.args.get('status', 'bare,processed,repeated')
    p = int(request.args.get('page', '1'))
    start = (p - 1) * PAGE_COUNT
    condition = {'level': KeywordLevel.LONG_TAIL, 'parentId': keyword_id}
    status = s.split(',')
    if status:
        condition['status'] = {'$in': status}

    count = Keyword.count(condition)
    cursor = Keyword.find(condition, skip=start, limit=PAGE_COUNT, sort=[('baiduIndex', pymongo.DESCENDING)])
    keywords = []
    for c in cursor:
        keywords.append(c)
    pagination = Pagination(p, PAGE_COUNT, count)

    return render_template('seo/longtail.html', keyword=keyword, keywords=keywords, pagination=pagination)


@seo.route('/hearsay/<ObjectId:keyword_id>', methods=('GET', 'POST'))
@admin_permission
def hearsay(keyword_id):
    """
    编辑关键字对应的文章.
    """
    keyword = Keyword.find_one({'_id': keyword_id})
    if not keyword:
        abort(404)

    # Open page
    if request.method == 'GET':
        return render_template('seo/hearsay.html', keyword=keyword)
    # Handle post request
    else:
        current_app.logger.info('Try to save hearsay for keyword %s/%s' % (keyword._id, keyword.name))
        title = request.form.get('title', '')
        body = request.form.get('body', '')
        if not title:
            return jsonify(success=False, message='文章标题不能为空！')
        if not body:
            return jsonify(success=False, message='文章内容不能为空！')

        is_new = True if not keyword.hearsay else False
        keyword.hearsay.title = title
        keyword.hearsay.body = body
        keyword.updateTime = datetime.now()
        if is_new:
            keyword.status = KeywordStatus.PROCESSED

        keyword.save()

        if not current_app.debug and is_new:
            notify_baidu(current_app._get_current_object(), keyword._id)

        return jsonify(success=True, message='成功保存了你的文章。')


@async_exec
def notify_baidu(app, id):
    """
    主动将新建文章的url主动推送到百度.
    参考自 http://zhanzhang.baidu.com/linksubmit/index?site=http://www.girl-atlas.com/
    """
    url = 'http://www.girl-atlas.com/hearsay/%s' % id
    app.logger.info('Try to nofity baidu this new url %s' % url)
    with app.app_context():
        j = requests.post('http://data.zz.baidu.com/urls?site=www.girl-atlas.com&token=umKKIO97UfMdq9P6',
                          data=url, headers={'Content-Type': 'text/plain'}).json()
        app.logger.info('Notify baidu result is %s' % j)


@seo.route('/refresh/<ObjectId:keyword_id>', methods=('POST',))
@admin_permission
def refresh(keyword_id):
    """
    刷新一个指定关键字的长尾关键字.
    """
    keyword = Keyword.find_one({'_id': keyword_id})
    if not keyword:
        abort(404)

    analyze_keyword(current_app._get_current_object(), keyword)
    return jsonify(success=True, message='成功触发了刷新请求，请稍候查看最新数据。')


@async_exec
def analyze_keyword(app, keyword):
    """
    分析站点级别的关键字, 获取其百度指数以及其相关的长尾关键字.
    目前是从5118抓取.
    """
    app.logger.info('Try to analyze keyword %s/%s' % (keyword._id, keyword.name))

    ss.headers['Referer'] = 'http://www.5118.com/'
    t = ss.get('http://www.5118.com/seo/words/%s' % url_quote(keyword.name)).text
    tree = html.fromstring(t)
    dls = tree.xpath('//div[@class="Fn-ui-list dig-list"]/dl')
    total = len(dls)
    for dl in dls:
        if dl.get('class', '') == 'dl-word':
            continue
        name = dl.xpath('./dd[1]//a[1]/@title')[0].strip()
        baidu_index = dl.xpath('./dd[2]/text()')[0].strip()
        baidu_result = dl.xpath('./dd[3]/text()')[0].strip()
        if not baidu_index.isdigit():
            baidu_index = 0
        if not baidu_result.isdigit():
            baidu_result = 0
        app.logger.info('Found keyword: %s/%s/%s' % (name, baidu_index, baidu_result))

        if name == keyword.name:
            keyword.baiduIndex = int(baidu_index)
            keyword.baiduResult = int(baidu_result)
            if total > 2:
                keyword.total = total - 2
            keyword.save()
        else:
            long_tail = Keyword.find_one({'name': name})
            if not long_tail:
                long_tail = Keyword()
                long_tail.name = name
                long_tail.level = KeywordLevel.LONG_TAIL
                long_tail.parentId = keyword._id

            long_tail.baiduIndex = int(baidu_index)
            long_tail.baiduResult = int(baidu_result)
            long_tail.save()
