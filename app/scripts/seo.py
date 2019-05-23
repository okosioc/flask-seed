# -*- coding: utf-8 -*-
"""
    seo
    ~~~~~~~~~~~~~~

    SEO related task.

    SEO相关脚本, 比如:
    1) 抓取关键词列表
    2) 根据关键词列表查询百度指数以及相关长尾关键字并排序

    执行脚本:
    export PYTHONIOENCODING=utf-8
    nohup python2.7 seo.py > ~/seo.txt &

    :copyright: (c) 2016 by fengweimin.
    :date: 2016/10/18
"""

import os
import random
import sys
import time

import requests
from lxml import html
from werkzeug.urls import url_quote

sys.path.append(os.path.join(os.getcwd(), '../../'))

from app import create_app
from app.models import KeywordLevel, Keyword

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

ym = 'http://www.yameituku.net'


def fetch_keywords():
    """
    获取站点级别的关键字并插入数据库中.
    """
    ss.headers['Referer'] = ym
    r = ss.get(ym + '/girls/all/')
    r.encoding = 'gbk'
    tree = html.fromstring(r.text)
    links = tree.xpath('//div[@class="listap"]/a')
    print('Found %s keywords' % len(links))
    ret = []
    for link in links:
        msg = 'Processing keyword %s' % link.get('title')
        text = link.get('title').strip()
        keyword = Keyword.find_one({'name': text})
        name = text
        if keyword:
            msg += ', skipped as existing'
        else:
            keyword = Keyword()
            keyword.name = name
            keyword.level = KeywordLevel.SITE
            keyword.refer = '%s%s' % (ym, link.get('href'))
            keyword.save()
        print(msg)
        ret.append(name)

    return ret


def analyze_keyword(k):
    """
    分析站点级别的关键字, 获取其百度指数以及其相关的长尾关键字.
    """
    keyword = Keyword.find_one({'name': k})
    if not keyword:
        print('Keyword %s does not exist' % k)
        return
    if keyword.baiduIndex > 0 or keyword.baiduResult > 0:
        print('Keyword %s is imported before' % k)
        return
    print('Try to analyze keyword %s/%s' % (keyword._id, k))

    ss.headers['Referer'] = 'http://www.5118.com/'
    t = ss.get('http://www.5118.com/seo/words/%s' % url_quote(k)).text
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
        print('Found keyword: %s/%s/%s' % (name, baidu_index, baidu_result))

        if name == k:
            keyword.baiduIndex = int(baidu_index)
            keyword.baiduResult = int(baidu_result)
            if total > 2:
                keyword.total = total - 2
            keyword.save()
        else:
            if Keyword.count({'name': name}) > 0:
                print('This keyword already exists')
                continue
            long_tail = Keyword()
            long_tail.name = name
            long_tail.level = KeywordLevel.LONG_TAIL
            long_tail.parentId = keyword._id
            long_tail.baiduIndex = int(baidu_index)
            long_tail.baiduResult = int(baidu_result)
            long_tail.save()

    time.sleep(random.randint(5, 15))


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        keywords = fetch_keywords()
        for k in keywords:
            analyze_keyword(k)
