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
from bson.objectid import ObjectId
from flask import Blueprint, request, render_template, abort, jsonify, current_app
from flask_babel import gettext as _
from flask_login import current_user

from app.jobs import post_view_times_counter
from app.models import Post, Tag, User
from app.core import Pagination, populate_model
from app.tools import auth_permission, send_support_email

blog = Blueprint('blog', __name__)

PAGE_COUNT = 10


@blog.route('/')
@blog.route('/index')
def index():
    """
    Index.
    """
    tid = request.args.get('t', None)
    page = int(request.args.get('p', 1))
    start = (page - 1) * PAGE_COUNT
    condition = {}
    if tid:
        condition = {'tids': ObjectId(tid)}
    count = Post.count(condition)
    cursor = Post.find(condition, skip=start, limit=PAGE_COUNT, sort=[('createTime', pymongo.DESCENDING)])
    pagination = Pagination(page, PAGE_COUNT, count)
    return render_template('blog/index.html', posts=list(cursor), pagination=pagination, tags=all_tags())


def all_tags():
    """
    Fetch all tags.
    """
    cursor = Tag.find({}, sort=[('weight', pymongo.DESCENDING)])
    return [t for t in cursor]


@blog.route('/post/<ObjectId:post_id>')
def post(post_id):
    """
    Post.
    """
    p = Post.find_one({'_id': post_id})
    if not p:
        abort(404)

    post_view_times_counter[post_id] += 1

    uids = set()
    for c in p.comments:
        uids.add(c.uid)
        for r in c.replys:
            uids.add(r.uid)
    user_dict = {u._id: u for u in User.find({'_id': {'$in': list(uids)}})}
    return render_template('blog/post.html', id=post_id, post=p, tags=all_tags(), user_dict=user_dict)


@blog.route('/post/new', methods=('GET', 'POST'))
@blog.route('/post/change/<ObjectId:post_id>', methods=('GET', 'POST'))
@auth_permission
def new(post_id=None):
    # Open page
    if request.method == 'GET':
        p = None
        # Change
        if post_id:
            p = Post.find_one({'_id': post_id})
            if not p:
                abort(404)

        return render_template('blog/new.html', post=p, tags=all_tags())
    # Handle post request
    else:
        try:
            post = populate_model(request.form, Post)
            if not post.title:
                return jsonify(success=False, message=_('Post title can not be blank!'))
            if not post.body:
                return jsonify(success=False, message=_('Post body can not be blank!'))
            if not post.tids:
                return jsonify(success=False, message=_('Post must at least have a tag!'))

            # New
            if not post_id:
                post.uid = current_user._id
                post.save()
                post_id = post._id
                current_app.logger.info('Successfully new a post %s' % post._id)
            # Change
            else:
                existing = Post.find_one({'_id': post_id})
                existing.title = post.title
                existing.tids = post.tids
                existing.body = post.body
                existing.save()
                current_app.logger.info('Successfully change a post %s' % post._id)
        except:
            current_app.logger.exception('Failed when saving post')
            return jsonify(success=False, message=_('Failed when saving the post, please try again later!'))

        return jsonify(success=True, message=_('Save the post successfully.'), pid=str(post_id))


@blog.route('/comment/<ObjectId:post_id>', methods=('POST',))
@auth_permission
def comment(post_id):
    """
    评论博文.
    """
    post = Post.find_one({'_id': post_id})
    if not post:
        return jsonify(success=False, message=_('The post does not exist!'))

    content = request.form.get('content', None)
    if not content or not content.strip():
        return jsonify(success=False, message=_('Comment content can not be blank!'))

    max = -1
    for c in post.comments:
        if max < c.id:
            max = c.id

    now = datetime.now()

    cmt = {
        'id': max + 1,
        'uid': current_user._id,
        'content': content,
        'time': now
    }

    post.comments.insert(0, cmt)
    post.save()

    send_support_email('comment()',
                       'New comment %s on post %s.' % (content, post._id))

    return jsonify(success=True, message=_('Save comment successfully.'))


@blog.route('/reply/<ObjectId:post_id>/<int:comment_id>', methods=('POST',))
@auth_permission
def reply(post_id, comment_id):
    """
    回复.
    """
    post = Post.find_one({'_id': post_id})
    if not post:
        return jsonify(success=False, message=_('The post does not exist!'))

    content = request.form.get('content', None)
    if not content or not content.strip():
        return jsonify(success=False, message=_('Reply content can not be blank!'))

    cmt = next((c for c in post.comments if c.id == comment_id), -1)
    if cmt == -1:
        return jsonify(success=False, message=_('The comment you would like to reply does not exist!'))

    now = datetime.now()

    reply = {
        'uid': current_user._id,
        'rid': ObjectId(request.form.get('rid', None)),
        'content': content,
        'time': now
    }

    cmt.replys.append(reply)
    post.save()

    send_support_email('reply()', 'New reply %s on post %s.' % (content, post._id))

    return jsonify(success=True, message=_('Save reply successfully.'))
