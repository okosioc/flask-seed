# -*- coding: utf-8 -*-
"""
    sslsmtphandler
    ~~~~~~~~~~~~~~

    A handler for ssl smtp email provider.

    :copyright: (c) 2016 by fengweimin.
    :date: 16/6/24
"""

import smtplib
import traceback
from email.utils import formatdate
from logging.handlers import SMTPHandler
from smtplib import SMTPServerDisconnected

from pydash import retry

from app.tools.decorators import async_exec


class SSLSMTPHandler(SMTPHandler):
    def emit(self, record):
        """
        Emit a record.

        :param record:
        :return:
        """
        self.async_emit(record)

    @async_exec
    def async_emit(self, record):
        """
        Async emit a record.

        :param record:
        :return:
        """
        try:
            self.retry_emit(record)
        except:
            traceback.print_exc()

    # 遇到连接问题则触发重试, 默认重复3次
    # https://pydash.readthedocs.io/en/latest/api.html#pydash.utilities.retry
    @retry(delay=1, exceptions=(SMTPServerDisconnected,))
    def retry_emit(self, record):
        """
        Retry emit a record.

        :param record:
        :return:
        """
        # print('Emitting ...')
        port = self.mailport
        if not port:
            port = smtplib.SMTP_PORT
        smtp = smtplib.SMTP_SSL(self.mailhost, port)
        msg = self.format(record)
        msg = "From: %s\r\nTo: %s\r\nSubject: %s\r\nDate: %s\r\n\r\n%s" % (
            self.fromaddr,
            ",".join(self.toaddrs),
            self.getSubject(record),
            formatdate(), msg)
        if self.username:
            smtp.login(self.username, self.password)
        smtp.sendmail(self.fromaddr, self.toaddrs, msg)
        smtp.quit()
