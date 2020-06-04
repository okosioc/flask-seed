# -*- coding: utf-8 -*-
"""
    blog
    ~~~~~~~~~~~~~~

    Blog pages/actions.

    :copyright: (c) 2016 by fengweimin.
    :date: 16/8/16
"""

from datetime import datetime

import pymongo
from flask import Blueprint, request, render_template, abort, jsonify, current_app
from flask_babel import gettext as _
from flask_login import current_user

from app.core import populate_model, populate_search
from app.extensions import qiniu, cache
from app.jobs import post_view_times_counter
from app.models import Post, Tag
from app.tools import editor_permission, auth_permission

blog = Blueprint('blog', __name__)


@blog.route('/')
def index():
    """ Index. """
    page = request.args.get('p', 1, lambda x: int(x) if x.isdigit() else 1)
    search, condition = populate_search(request.args, Post)
    sort = [('createTime', pymongo.DESCENDING)]
    records, pagination = Post.search(condition, page, per_page=10, sort=sort)
    tag = Tag.find_one(condition['tids']) if condition and 'tids' in condition else None  # The searched tag
    return render_template('blog/index.html',
                           search=search, tag=tag,
                           tags=all_tags(),
                           posts=records, pagination=pagination)


@cache.memoize(900)
def all_tags():
    """ Fetch all tags. """
    cursor = Tag.find({}, sort=[('weight', pymongo.DESCENDING)])
    return [t for t in cursor]


@blog.route('/form/')
@blog.route('/form/<ObjectId:pid>')
@editor_permission
def form(pid=None):
    if pid:
        post = Post.find_one(pid)
        if not post:
            abort(404)
    else:
        post = Post()
    #
    return render_template('blog/form.html', post=post, token=qiniu.image_token(), tags=all_tags())


@blog.route('/save/', methods=('POST',))
@blog.route('/save/<ObjectId:pid>', methods=('POST',))
@editor_permission
def save(pid=None):
    """ Create or Update a post. """
    try:
        post = populate_model(request.form, Post)
        # Create
        if not pid:
            post.uid = current_user._id
            post.save()
            pid = post._id
            current_app.logger.info('Successfully create post %s' % pid)
        # Update
        else:
            existing = Post.find_one(pid)
            if not existing:
                abort(404)
            existing.title = post.title
            existing.tids = post.tids
            existing.abstract = post.abstract
            existing.cover = post.cover
            existing.body = post.body
            existing.updateTime = datetime.now()
            existing.save()
            current_app.logger.info('Successfully update post %s' % pid)
    except:
        current_app.logger.exception('Failed when saving post')
        return jsonify(success=False, message=_('Failed when saving post, please try again later!'))
    #
    return jsonify(success=True, message=_('Save post successfully.'), pid=pid)


@blog.route('/post/<ObjectId:pid>')
def post(pid):
    """ Post. """
    existing = Post.find_one(pid)
    if not existing:
        abort(404)
    # Update view times counter, app::jobs will save it once in a while
    post_view_times_counter[pid] += 1
    return render_template('blog/post.html', post=existing, tags=all_tags())


@blog.route('/comment/<ObjectId:pid>', methods=('POST',))
@auth_permission
def comment(pid):
    """ Comment on a post. """
    existing = Post.find_one(pid)
    if not existing:
        return jsonify(success=False, message=_('The post does not exist!'))

    content = request.form.get('content', '').strip()
    if not content:
        return jsonify(success=False, message=_('Comment can not be blank!'))

    idx = max([c.id for c in existing.comments] + [0])
    cmt = {
        'id': idx + 1,
        'uid': current_user._id,
        'uname': current_user.name,
        'uavatar': current_user.avatar,
        'content': content,
        'time': datetime.now()
    }
    existing.comments.insert(0, cmt)
    existing.save()
    return jsonify(success=True, message=_('Save comment successfully.'))
