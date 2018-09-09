# -*- coding: utf-8 -*-
"""
    notifier
    ~~~~~~~~~~~~~~

    Notifier, which is used to send email/sms notifications.

    :copyright: (c) 2016 by fengweimin.
    :date: 16/8/14
"""

from datetime import datetime

from flask import current_app
from flask_mail import Message

from app.extensions import mail
from app.tools import async_exec


def send_support_email(type, body, **kwargs):
    """
    For email setting, please refer to `Flask-Mail <https://pythonhosted.org/Flask-Mail/>`.
    """
    # flask.current_app is a proxy.
    # http://flask.pocoo.org/docs/0.11/reqcontext/#notes-on-proxies
    app = kwargs.get('app', None)
    if not app:
        app = current_app._get_current_object()

    subject = '[Info] %s: %s on %s' % (app.config['DOMAIN'], type, datetime.now().strftime('%Y/%m/%d'))
    subject += (' [DEV]' if app.debug else '')
    recipients = app.config['ADMINS']
    app.logger.info('Try to send support email %s to %s' % (subject, recipients))
    send_async_email(app, subject, recipients, body)


def send_service_mail(subject, recipients, html, **kwargs):
    """
    发送业务邮件, 业务代码生成邮件主体内容.
    """
    app = kwargs.get('app', None)
    if not app:
        app = current_app._get_current_object()

    subject += (' [DEV]' if app.debug else '')
    send_async_service_email(app, subject, recipients, html)


@async_exec
def send_async_email(app, subject, recipients, body):
    with app.app_context():
        msg = Message(subject, recipients, body)
        mail.send(msg)


@async_exec
def send_async_service_email(app, subject, recipients, html):
    with app.app_context():
        msg = Message(subject, recipients, html=html)
        mail.send(msg)
