""" demo module. """
from datetime import datetime

from bson import ObjectId
from flask import Blueprint, render_template, current_app, redirect, request, abort, jsonify, url_for
from flask_login import current_user

from py3seed import populate_model, populate_search
from core.models import DemoProject, DemoUser, DemoTask, DemoProjectDashboard, DemoTeam
from www.commons import get_id, auth_permission, admin_permission, prepare_demo_data

demo = Blueprint('demo', __name__, url_prefix='/demo')


@demo.route('/project-list')
@auth_permission
def project_list():
    """ 项目管理. """
    page, sort = request.args.get('p', 1, lambda x: int(x) if x.isdigit() else 1), [('create_time', -1)]
    search, condition = populate_search(request.args, DemoProject)
    current_app.logger.info(f'Try to search demo project by {condition}, sort by {sort}')
    demo_projects, pagination = DemoProject.search(condition, page, sort=sort)
    #
    return render_template('demo/project-list.html',
                           search=search, pagination=pagination, demo_projects=demo_projects)


@demo.route('/project-detail')
@auth_permission
def project_detail():
    """ 项目详情. """
    id_ = get_id(int)
    demo_project = DemoProject.find_one(id_)
    if not demo_project:
        abort(404)
    #
    return render_template('demo/project-detail.html', demo_project=demo_project)


@demo.route('/project-edit')
@auth_permission
def project_edit():
    """ 项目编辑. """
    args, preloads = [], {}
    id_ = get_id(int)
    if id_:
        demo_project = DemoProject.find_one(id_)
        if not demo_project:
            abort(404)
    else:
        demo_project = DemoProject()
    #
    demo_users, demo_users_pagination = DemoUser.search({}, projection=['avatar', 'name', 'status', 'roles', 'email', 'phone', 'create_time'], sort=[('create_time', -1)])
    current_app.logger.info(f'Preloaded {len(demo_users)} demo users')
    preloads.update({'demo_users': demo_users, 'demo_users_pagination': dict(demo_users_pagination), })
    #
    return render_template('demo/project-edit.html', demo_project=demo_project, args=args, **preloads)


@demo.route('/project-edit-upcreate', methods=('POST',))
@auth_permission
def project_edit_upcreate():
    """ 保存项目编辑. """
    req_demo_project = populate_model(request.form, DemoProject)
    id_ = get_id(int)
    current_app.logger.info(f'Try to save demo project with id {id_}: {req_demo_project}')
    #
    if not id_:
        req_demo_project.save()
        id_ = req_demo_project.id
        current_app.logger.info(f'Successfully create demo project {id_}')
    else:
        existing = DemoProject.find_one(id_)
        if not existing:
            abort(404)
        #
        existing.title = req_demo_project.title
        existing.description = req_demo_project.description
        existing.status = req_demo_project.status
        existing.value = req_demo_project.value
        existing.start = req_demo_project.start
        existing.end = req_demo_project.end
        existing.percent = req_demo_project.percent
        existing.members = req_demo_project.members
        #
        existing.update_time = datetime.now()
        existing.save()
        current_app.logger.info(f'Successfully update demo project {id_}')
    #
    return jsonify(error=0, message='Save demo project successfully.', id=id_)


@demo.route('/project-edit/search-demo-users', methods=('POST',))
@auth_permission
def project_edit_search_demo_users():
    """ 查找用户. """
    page, sort = request.form.get('p', 1, lambda x: int(x) if x.isdigit() else 1), [('create_time', -1)]
    search, condition = populate_search(request.form, DemoUser)
    current_app.logger.info(f'Try to search demo user at page {page} by {condition}, sort by {sort}')
    demo_users, pagination = DemoUser.search(condition, page, projection=['avatar', 'name', 'status', 'roles', 'email', 'phone', 'create_time'], sort=sort)
    return jsonify(error=0, message='Search demo user successfully.', pagination=dict(pagination), demo_users=demo_users)


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


@demo.route('/task-detail')
@auth_permission
def task_detail():
    """ 任务详情. """
    id_ = get_id(int)
    demo_task = DemoTask.find_one(id_)
    if not demo_task:
        abort(404)
    #
    return render_template('demo/task-detail.html', demo_task=demo_task)


@demo.route('/task-edit')
@auth_permission
def task_edit():
    """ 任务编辑. """
    args, preloads = [], {}
    id_ = get_id(int)
    if id_:
        demo_task = DemoTask.find_one(id_)
        if not demo_task:
            abort(404)
    else:
        demo_task = DemoTask()
        #
        if 'project_id' in request.args:
            project_id = int(request.args.get('project_id'))
            demo_task.project = DemoProject.find_one(project_id)
            args.append(('project_id', project_id))
    #
    demo_users, demo_users_pagination = DemoUser.search({}, projection=['avatar', 'name', 'status', 'roles', 'email', 'phone', 'create_time'], sort=[('create_time', -1)])
    current_app.logger.info(f'Preloaded {len(demo_users)} demo users')
    preloads.update({'demo_users': demo_users, 'demo_users_pagination': dict(demo_users_pagination), })
    #
    return render_template('demo/task-edit.html', demo_task=demo_task, args=args, **preloads)


@demo.route('/task-edit-upcreate', methods=('POST',))
@auth_permission
def task_edit_upcreate():
    """ 保存任务编辑. """
    req_demo_task = populate_model(request.form, DemoTask)
    id_ = get_id(int)
    current_app.logger.info(f'Try to save demo task with id {id_}: {req_demo_task}')
    #
    if not id_:
        req_demo_task.save()
        id_ = req_demo_task.id
        current_app.logger.info(f'Successfully create demo task {id_}')
    else:
        existing = DemoTask.find_one(id_)
        if not existing:
            abort(404)
        #
        existing.title = req_demo_task.title
        existing.status = req_demo_task.status
        existing.content = req_demo_task.content
        existing.start = req_demo_task.start
        existing.end = req_demo_task.end
        existing.user = req_demo_task.user
        #
        existing.update_time = datetime.now()
        existing.save()
        current_app.logger.info(f'Successfully update demo task {id_}')
    #
    return jsonify(error=0, message='Save demo task successfully.', id=id_)


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
    """ 保存团队设置. """
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
    if id_:
        demo_user = DemoUser.find_one(id_)
        if not demo_user:
            abort(404)
    else:
        demo_user = current_user
    #
    return render_template('demo/user-profile.html', demo_user=demo_user, **preloads)


@demo.route('/user-profile-update', methods=('POST',))
@auth_permission
def user_profile_update():
    """ 保存用户设置. """
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
