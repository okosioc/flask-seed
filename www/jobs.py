# -*- coding: utf-8 -*-
"""
    jobs
    ~~~~~~~~~~~~~~

    Jobs defined here.

    :copyright: (c) 2016 by fengweimin.
    :date: 16/8/12
"""

import os
import threading
import time

import schedule
from flask import current_app


def do_something(app, hm):
    """ 使用示例, 可增加@async_exec异步执行, 否则会阻塞运行. """
    with app.app_context():
        try:
            current_app.logger.info(f'Scheduler do_something running: {hm}')
            #
            pass
        except:
            current_app.logger.exception('Failed in do_something')
        #
        current_app.logger.info('Scheduler do_something finished')


def run_schedule(app):
    """ Invoke schedule. """
    # For schedule rules please refer to https://github.com/dbader/schedule
    # Invoke do_something every 30 mins
    for hour in range(24):
        for minutes in [0, 30]:
            hm = '{:02d}:{:02d}'.format(hour, minutes)
            schedule.every().day.at(hm).do(do_something, app, hm)
    # 初始化的日志
    runnable_jobs = [job for job in schedule.default_scheduler.jobs]
    app.logger.info(f'Job initialized: {len(runnable_jobs)}')
    #
    while True:
        schedule.run_pending()
        time.sleep(1)


def init_schedule(app):
    """ Init.

    TODO: 在多进程下避免每个进程都启动一次
    """
    # http://stackoverflow.com/questions/9449101/how-to-stop-flask-from-initialising-twice-in-debug-mode/
    is_main_run = os.environ.get('WERKZEUG_RUN_MAIN')
    app.logger.info(f'Try to init schedule with debug {app.debug} and is_main_run {is_main_run}')
    if not app.debug or is_main_run == 'true':
        t = threading.Thread(target=run_schedule, args=(app,))
        # Python threads don't die when the main thread exits, unless they are daemon threads.
        t.setDaemon(True)
        t.start()
