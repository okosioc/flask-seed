# -*- coding: utf-8 -*-
"""
    fabfile
    ~~~~~~~~~~~~~~

    Fab.

    :copyright: (c) 2016 by fengweimin.
    :date: 16/7/21
"""

from fabric.api import *

# The user to use for the remote commands
env.user = ''
env.password = ''
# The servers where the commands are executed
env.hosts = ['']
# www folder
project_folder = '/appl/projects/fb/www'


def deploy():
    """
    检测服务器上的版本, 用户确认后安装git上的最新版.
    """
    with cd(project_folder):
        run('git fetch')
        print('- 最新版本')
        run('git log origin/master -1')
        print('- 当前版本')
        run('git log -1')
        run('git status')

        p = prompt('- 你确定要发布么？[y/n]', validate=r'^[yn]$')
        if p == 'y':
            run('git pull')
            # Restart unicorn
            # run('killall -9 gunicorn')
            # run('gunicorn wsgi:app -p wsgi.pid -b 0.0.0.0:6060 -D --log-file app/logs/gunicorn.log')
            run('kill -HUP `cat wsgi.pid`')


def ustart():
    with cd(project_folder):
        run('gunicorn wsgi:app -p wsgi.pid -b 0.0.0.0:6060 --log-file app/logs/gunicorn.log')
