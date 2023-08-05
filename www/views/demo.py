""" demo module. """
from datetime import datetime

from bson import ObjectId
from flask import Blueprint, render_template, current_app, redirect, request, abort, jsonify, url_for
from flask_login import current_user

from py3seed import populate_model, populate_search
from .common import get_id
from www.tools import auth_permission, admin_permission, prepare_demo_data
from core.models import DemoProjectDashboard, DemoTeam, DemoUser, DemoProject

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


@demo.route('/team-profile')
@auth_permission
def team_profile():
    """ 团队设置. """
    preloads = {}
    id_ = get_id(int)
    demo_team = DemoTeam.find_one(id_)
    if not demo_team:
        abort(404)
    #
    return render_template('demo/team-profile.html', demo_team=demo_team, **preloads)


@demo.route('/team-profile-update', methods=('POST',))
@auth_permission
def team_profile_update():
    """ Update demo team. """
    req_demo_team = populate_model(request.form, DemoTeam)
    id_ = get_id(int)
    current_app.logger.info(f'Try to save demo team with id {id_}: {req_demo_team}')
    #
    existing = DemoTeam.find_one(id_)
    if not existing:
        abort(404)
    #
    existing.name = req_demo_team.name
    existing.code = req_demo_team.code
    existing.remarks = req_demo_team.remarks
    existing.logo = req_demo_team.logo
    #
    existing.update_time = datetime.now()
    existing.save()
    current_app.logger.info(f'Successfully update demo team {id_}')
    #
    return jsonify(error=0, message='Save demo team successfully.', id=id_)


@demo.route('/team-members')
@auth_permission
def team_members():
    """ 团队成员. """
    id_ = get_id(int)
    demo_team = DemoTeam.find_one(id_)
    if not demo_team:
        abort(404)
    #
    return render_template('demo/team-members.html', demo_team=demo_team)


@demo.route('/user-profile')
@auth_permission
def user_profile():
    """ 用户设置. """
    preloads = {}
    id_ = get_id(int)
    demo_user = DemoUser.find_one(id_)
    if not demo_user:
        abort(404)
    #
    return render_template('demo/user-profile.html', demo_user=demo_user, **preloads)


@demo.route('/user-profile-update', methods=('POST',))
@auth_permission
def user_profile_update():
    """ Update demo user. """
    req_demo_user = populate_model(request.form, DemoUser)
    id_ = get_id(int)
    current_app.logger.info(f'Try to save demo user with id {id_}: {req_demo_user}')
    #
    existing = DemoUser.find_one(id_)
    if not existing:
        abort(404)
    #
    existing.name = req_demo_user.name
    existing.phone = req_demo_user.phone
    existing.intro = req_demo_user.intro
    existing.avatar = req_demo_user.avatar
    #
    existing.update_time = datetime.now()
    existing.save()
    current_app.logger.info(f'Successfully update demo user {id_}')
    #
    return jsonify(error=0, message='Save demo user successfully.', id=id_)
