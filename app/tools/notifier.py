# -*- coding: utf-8 -*-
"""
    notifier
    ~~~~~~~~~~~~~~

    Notifier, which is used to send email/sms notifications.

    :copyright: (c) 2016 by fengweimin.
    :date: 16/8/14
"""
import socket
from datetime import datetime
from smtplib import SMTPServerDisconnected

from flask import current_app
from flask_mail import Message
from pydash import retry

from app.extensions import mail
from app.tools.decorators import async_exec


def send_support_email(type, body, **kwargs):
    """ Send emails to system admin for easy supporting. """
    # flask.current_app is a proxy.
    # http://flask.pocoo.org/docs/0.11/reqcontext/#notes-on-proxies
    app = kwargs.get('app', None)
    if not app:
        app = current_app._get_current_object()

    subject = '[Info] %s: %s on %s' % (app.config['DOMAIN'], type, datetime.now().strftime('%Y/%m/%d'))
    hostname = socket.gethostname()
    subject += (' [%s]' % hostname if hostname else '')
    recipients = app.config['ADMINS']
    app.logger.info('Try to send support email %s to %s' % (subject, recipients))
    send_async_email(app, subject, recipients, body)


def send_service_mail(subject, recipients, html, bcc=None, **kwargs):
    """ Send emails to business user for notification. """
    app = kwargs.get('app', None)
    if not app:
        app = current_app._get_current_object()

    hostname = socket.gethostname()
    subject += (' [%s]' % hostname if hostname else '')
    send_async_service_email(app, subject, recipients, html, bcc)


def _get_host_name():
    """ Get current host name.

    :return:
    """
    return socket.gethostname()


@async_exec
def send_async_email(app, subject, recipients, body):
    with app.app_context():
        msg = Message(subject, recipients, body)
        try:
            retry_send(msg)
        except Exception as e:
            app.logger.warn('Can not send support email %s to %s, %s' % (subject, recipients, e))


@async_exec
def send_async_service_email(app, subject, recipients, html, bcc):
    with app.app_context():
        msg = Message(subject, recipients, html=html, bcc=bcc)
        try:
            retry_send(msg)
        except Exception as e:
            app.logger.warn('Can not send service email %s to %s, %s' % (subject, recipients, e))


# https://pydash.readthedocs.io/en/latest/api.html#pydash.utilities.retry
@retry(delay=1, exceptions=(SMTPServerDisconnected,))
def retry_send(msg):
    # print('Sending ...')
    mail.send(msg)
