# -*- coding: utf-8 -*-
"""
    test_schema
    ~~~~~~~~~~~~~~

    Test cases for schema.

    :copyright: (c) 2019 by weiminfeng.
    :date: 2019/11/4
"""
import json
from datetime import datetime
from typing import List, Dict

import pytest
from pymongo.errors import DuplicateKeyError

from app.seed import SimpleEnum, BaseModel, DATETIME_FORMAT, DataError, MongoModel


class UserRole(SimpleEnum):
    """ User roles. """
    MEMBER = 1
    EDITOR = 2
    ADMIN = 9


class UserStatus(SimpleEnum):
    """ User Status. """
    NORMAL = 'normal'
    REJECTED = 'rejected'


class LastLogin(BaseModel):
    """ last login modal. """
    ip: str
    time: datetime


class Comment(BaseModel):
    """ Comment model. """
    author: str
    content: str
    date: datetime = datetime.now


class Post(BaseModel):
    """ Post model"""
    title: str
    content: str
    date: datetime = datetime.now
    likes: int = 0
    comments: List[Comment] = None


class User(MongoModel):
    """ User definition. """
    name: str
    email: str
    password: str
    intro: str = None
    avatar: str = None
    point: int = 0
    status: UserStatus = UserStatus.NORMAL
    roles: List[UserRole] = [UserRole.MEMBER]

    update_time: datetime = None
    create_time: datetime = datetime.now

    last_login: LastLogin = None

    posts: List[Post] = None

    l: List[str] = None
    d: Dict[str, str] = None


def test_modal(app):
    """ Test cases for modal definition. """
    now = datetime.now()
    usr = User()

    # Test default values
    assert usr.point == 0
    assert usr.status == UserStatus.NORMAL
    assert usr.roles[0] == UserRole.MEMBER
    assert len(usr.l) == 0

    # Test referral modal
    usr.last_login.ip = '127.0.0.1'
    usr.last_login.time = now
    assert usr.last_login.ip == '127.0.0.1'

    # Test copy
    another_usr = usr.copy()
    assert usr.point == another_usr.point
    assert usr != another_usr
    assert usr.last_login.ip == another_usr.last_login.ip
    assert usr.last_login != another_usr.last_login

    # Test json
    json_ = json.loads(usr.json())
    assert json_['create_time'] == usr.create_time.strftime(DATETIME_FORMAT)

    # Test dict
    admin = User(
        name='admin',
        email='admin',
        password='admin',
        roles=[UserRole.ADMIN],
        last_login=LastLogin(ip='127.0.0.1', time=now),
        posts=[Post(title='admin', content='content')]
    )
    editor = User(**{
        'name': 'editor',
        'email': 'editor',
        'password': 'editor',
        'last_login': {'ip': '127.0.0.1', 'time': now},
        'posts': [{'title': 'editor', 'content': 'editor'}]
    })
    assert len(admin.posts) == len(editor.posts)

    # Test validate
    def _validate_and_check_message(message):
        errors = usr.validate()
        assert next((e for e in errors if message in e.message), None) is not None

    _validate_and_check_message('User.name')
    usr.name = 'test'
    usr.email = 'test'
    usr.password = 'test'

    usr.posts.append(Post())
    _validate_and_check_message('Post.title')
    pst = usr.posts[0]
    pst.title = 'test'
    pst.content = 'test'

    usr.status = 'DELETED'
    _validate_and_check_message('User.status')
    usr.status = UserStatus.NORMAL

    pst.comments.append(Comment(author='test', content='test'))

    # Should be valid
    assert len(usr.validate()) == 0


def test_crud(app):
    """ Test cases for crud. """
    # Init
    assert User.delete_many({})
    assert User.count({}) == 0
    # C
    usr = User()
    usr.name = 'test'
    usr.email = 'test'
    usr.password = 'test'
    usr.save()
    assert User.count({}) == 1
    # R
    assert User.find_one({'name': 'test'}).name == 'test'

    # U
    del usr.name
    # Validation
    with pytest.raises(DataError, match='name') as excinfo:
        usr.save()
    # print(excinfo.value)

    usr.name = 'test1'
    # DulplicateKey from pymongo
    with pytest.raises(DuplicateKeyError) as excinfo:
        usr.save(insert_with_id=True)
    # print(excinfo.value)

    usr.save()
    assert User.find_one({'name': 'test1'}).name == 'test1'

    # D
    assert usr.delete().deleted_count == 1

    # Verify
    assert User.count({}) == 0
