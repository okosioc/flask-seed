""" demo module. """
from datetime import datetime

from bson import ObjectId
from flask import Blueprint, render_template, current_app, redirect, request, abort, jsonify, url_for
from flask_login import current_user

from py3seed import populate_model, populate_search
from .common import get_id
from www.tools import auth_permission, admin_permission, prepare_demo_data
from core.models import DemoProjectDashboard, DemoProject, DemoUser

demo = Blueprint('demo', __name__)

prepare_demo_data()


@demo.route('/project-dashboard')
@auth_permission
def project_dashboard():
    """ 项目仪表盘. """
    # NOTE: 目前是实时扫描数据并整合为一个仪表盘数据, 实际应用中应该是是使用定时任务来生成
    dpd = DemoProjectDashboard()
    # Metric x4
    demo_projects = DemoProject.find()
    demo_users = DemoUser.find()
    #
    dpd.active_projects_count = len(demo_projects)
    dpd.active_projects_value = sum(map(lambda x: x.value, demo_projects))
    dpd.members_count = len(demo_users)
    dpd.tasks_count = sum(map(lambda x: len(x.tasks), demo_projects))
    # Table
    dpd.active_projects = demo_projects
    # Timeline
    recent_activities = []
    for p in demo_projects:
        recent_activities.extend(p.activities)
    #
    recent_activities.sort(key=lambda x: x.time, reverse=True)
    dpd.recent_activities = recent_activities[:10]
    #
    return render_template('demo/project-dashboard.html', demo_project_dashboard=dpd)
