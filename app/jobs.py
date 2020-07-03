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
from collections import Counter

import schedule

from app.models import Post

post_view_times_counter = Counter()


def update_view_times(app, hm):
    """ Update view times for posts. """
    app.logger.info('Scheduler update_view_times running: %s' % hm)
    d = dict(post_view_times_counter)
    post_view_times_counter.clear()
    for k, v in d.items():
        p = Post.find_one({'_id': k})
        if p:
            try:
                p.viewTimes += v
                p.save()
            except:
                app.logger.exception('Failed when updating the viewTime for album %s' % p._id)
    #
    app.logger.info('Scheduler update_view_times finished')


def run_schedule(app):
    """ Invoke schedule. """
    # For schedule rules please refer to https://github.com/dbader/schedule
    # Invoke update_view_times every 30 mins
    for hour in range(24):
        for minutes in [0, 30]:
            hm = '{:02d}:{:02d}'.format(hour, minutes)
            schedule.every().day.at(hm).do(update_view_times, app, hm)

    while True:
        schedule.run_pending()
        time.sleep(1)


def init_schedule(app):
    """ Init. """
    # http://stackoverflow.com/questions/9449101/how-to-stop-flask-from-initialising-twice-in-debug-mode/
    app.logger.info('Try to init schedule, current app status is %s/%s/%s' % (
        app.debug, app.env, os.environ.get('WERKZEUG_RUN_MAIN')))
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        t = threading.Thread(target=run_schedule, args=(app,))
        # Python threads don't die when the main thread exits, unless they are daemon threads.
        t.setDaemon(True)
        t.start()
