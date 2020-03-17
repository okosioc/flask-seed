# -*- coding: utf-8 -*-
"""
    fabfile
    ~~~~~~~~~~~~~~

    Fab.

    :copyright: (c) 2016 by fengweimin.
    :date: 16/7/21
"""

from fabric import task

# Multi hosts
# host, e.g, root@129.168.0.1:9527
hosts = [
    {'host': '<FIXME>', 'connect_kwargs': {'password': '<FIXME>'}}
]
# www folder
project_folder = '/appl/projects/seed/www'


@task(hosts=hosts)
def deploy(ctx):
    """ Check newest version and confirm if needed to deploy. """
    with ctx.cd(project_folder):
        ctx.run('git fetch')
        print('\n- Newest Version:')
        ctx.run('git log origin/master -1')
        print('\n- Current Version:')
        ctx.run('git log -1')
        ctx.run('git status')

        if confirm('\n- Are you sure to deploy?'):
            ctx.run('git pull')
            # Restart unicorn
            # run('killall -9 gunicorn')
            # run('gunicorn wsgi:app -p wsgi.pid -b 0.0.0.0:6060 -D --timeout 300 --log-file app/logs/gunicorn.log')
            ctx.run('kill -HUP `cat wsgi.pid`')


def confirm(question, assume_yes=True):
    """ Ask user a yes/no question and return their response as a boolean. """
    # Set up suffix
    if assume_yes:
        suffix = "Y/n"
    else:
        suffix = "y/N"
    # Loop till we get something we like
    while True:
        # Ask
        response = input("{0} [{1}] ".format(question, suffix))
        response = response.lower().strip()  # Normalize
        # Default
        if not response:
            return assume_yes
        # Yes
        if response in ["y", "yes"]:
            return True
        # No
        if response in ["n", "no"]:
            return False
        # Didn't get empty, yes or no, so complain and loop
        err = "I didn't understand you. Please specify '(y)es' or '(n)o'."
        print(err)
