""" demo module. """
from datetime import datetime

from flask import Blueprint, render_template, current_app, request, abort, jsonify
from py3seed import populate_model, populate_search
from werkzeug.security import generate_password_hash

from core.models import DemoProjectDashboard, DemoTeam, DemoUser, DemoProject, DemoTask, DemoUserRole, DemoActivity, DemoCategory, DemoAttribute, DemoAttributeOption
from www.tools import auth_permission, str_datetime
from .common import get_id

demo = Blueprint('demo', __name__)

# 演示团队
demo_team_koi = DemoTeam(
    name='锦鲤团队',
)
demo_team_koi.save()
# 演示用户
demo_user_admin = DemoUser(
    name='管理员',
    roles=[DemoUserRole.MEMBER, DemoUserRole.ADMIN],
    email='admin@flask-seed.com',
    password=generate_password_hash('1q2w3e4r'),
    team=demo_team_koi,
    team_join_time=datetime.now(),
)
demo_user_admin.save()
demo_user_yun = DemoUser(
    name='云榕',
    roles=[DemoUserRole.MEMBER],
    email='yun@flask-seed.com',
    password=generate_password_hash('1q2w3e4r'),
    team=demo_team_koi,
    team_join_time=datetime.now(),
)
demo_user_yun.save()
demo_user_yue = DemoUser(
    name='月瑶',
    roles=[DemoUserRole.MEMBER],
    email='yue@flask-seed.com',
    password=generate_password_hash('1q2w3er4'),
    team=demo_team_koi,
    team_join_time=datetime.now(),
)
demo_user_yue.save()
demo_user_tian = DemoUser(
    name='天清',
    roles=[DemoUserRole.MEMBER],
    email='tian@flask-seed.com',
    password=generate_password_hash('1q2w3e4r'),
    team=demo_team_koi,
    team_join_time=datetime.now(),
)
demo_user_tian.save()
demo_user_hai = DemoUser(
    name='海阔',
    roles=[DemoUserRole.MEMBER],
    email='hai@flask-seed.com',
    password=generate_password_hash('1q2w3e4r'),
    team=demo_team_koi,
    team_join_time=datetime.now(),
)
demo_user_hai.save()
# 字符串模板
template_create_project = '<a class="mx-1" href="#">{}</a>创建项目<a class="mx-1" href="#">{}</a>'
template_create_project_task = '<a class="mx-1" href="#">{}</a>在项目<a class="mx-1" href="#">{}</a>中创建任务<a class="mx-1" href="#">{}</a>'


# 演示项目
def _demo_task(project, user, title, start, end):
    task = DemoTask(title=title, start=start, end=end, project=project, user=user)
    task.save()
    return task


project_0 = DemoProject(
    title='项目仪表盘', value=1000.,
    start='2022-07-25', end='2022-07-29',
    activities=[
        DemoActivity(user=demo_user_admin, title=template_create_project_task.format('管理员', '项目仪表盘', '生成页面'),
                     time=str_datetime('2022-07-25 09:10:00')),
        DemoActivity(user=demo_user_admin, title=template_create_project_task.format('管理员', '项目仪表盘', '数据结构'),
                     time=str_datetime('2022-07-25 09:05:00')),
        DemoActivity(user=demo_user_admin, title=template_create_project.format('管理员', '项目仪表盘'),
                     time=str_datetime('2022-07-25 09:00:00'))
    ],
    members=[demo_user_yun],
)
project_0.save()
_demo_task(project_0, demo_user_yun, '数据结构', '2022-07-25', '2022-07-26')
_demo_task(project_0, demo_user_yun, '生成页面', '2022-07-27', '2022-07-29')
#
project_1 = DemoProject(
    title='用户和团队管理', value=2000.,
    start='2022-08-01', end='2022-08-05',
    activities=[
        DemoActivity(user=demo_user_admin, title=template_create_project_task.format('管理员', '用户和团队管理', '团队成员'),
                     time=str_datetime('2022-08-01 09:20:00')),
        DemoActivity(user=demo_user_admin, title=template_create_project_task.format('管理员', '用户和团队管理', '团队设置'),
                     time=str_datetime('2022-08-01 09:15:00')),
        DemoActivity(user=demo_user_admin, title=template_create_project_task.format('管理员', '用户和团队管理', '用户设置'),
                     time=str_datetime('2022-08-01 09:10:00')),
        DemoActivity(user=demo_user_admin, title=template_create_project_task.format('管理员', '用户和团队管理', '数据结构'),
                     time=str_datetime('2022-08-01 09:05:00')),
        DemoActivity(user=demo_user_admin, title=template_create_project.format('管理员', '用户和团队管理'),
                     time=str_datetime('2022-08-01 09:00:00'))
    ],
    members=[demo_user_yun, demo_user_yue],
)
project_1.save()
_demo_task(project_1, demo_user_yun, '数据结构', '2022-08-01', '2022-08-01')
_demo_task(project_1, demo_user_yue, '用户设置', '2022-08-02', '2022-08-02')
_demo_task(project_1, demo_user_yue, '团队设置', '2022-08-03', '2022-08-03')
_demo_task(project_1, demo_user_yue, '团队成员', '2022-08-04', '2022-08-04')
#
project_2 = DemoProject(
    title='项目管理', value=2000.,
    start='2022-08-08', end='2022-08-10',
    activities=[
        DemoActivity(user=demo_user_admin, title=template_create_project_task.format('管理员', '项目管理', '项目编辑'),
                     time=str_datetime('2022-08-08 09:20:00')),
        DemoActivity(user=demo_user_admin, title=template_create_project_task.format('管理员', '项目管理', '项目详情'),
                     time=str_datetime('2022-08-08 09:15:00')),
        DemoActivity(user=demo_user_admin, title=template_create_project_task.format('管理员', '项目管理', '项目列表'),
                     time=str_datetime('2022-08-08 09:10:00')),
        DemoActivity(user=demo_user_admin, title=template_create_project_task.format('管理员', '项目管理', '数据结构'),
                     time=str_datetime('2022-08-08 09:05:00')),
        DemoActivity(user=demo_user_admin, title=template_create_project.format('管理员', '项目管理'),
                     time=str_datetime('2022-08-08 09:00:00'))
    ],
    members=[demo_user_yun, demo_user_yue],
)
project_2.save()
_demo_task(project_2, demo_user_yun, '数据结构', '2022-08-08', '2022-08-08')
_demo_task(project_2, demo_user_yue, '项目列表', '2022-08-09', '2022-08-09')
_demo_task(project_2, demo_user_yue, '项目详情', '2022-08-09', '2022-08-09')
_demo_task(project_2, demo_user_yue, '项目编辑', '2022-08-10', '2022-08-10')


@demo.route('/project-dashboard')
@auth_permission
def project_dashboard():
    """ 项目仪表盘. """
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


@demo.route('/user-profile')
@auth_permission
def user_profile():
    """ 用户设置. """
    id_ = get_id(int)
    args = []
    if id_:
        demo_user = DemoUser.find_one(id_)
        if not demo_user:
            abort(404)
    else:
        demo_user = DemoUser()
        #
        if 'team_id' in request.args:
            team_id = int(request.args.get('team_id'))
            demo_user.team = DemoTeam.find_one(team_id)
            args.append(('team_id', team_id))
    #
    preloads = {}
    #
    return render_template('demo/user-profile.html', demo_user=demo_user, args=args, **preloads)


@demo.route('/user-profile/demo-user-form', methods=('POST',))
@auth_permission
def user_profile_demo_user_form():
    """ 保存用户设置. """
    req_demo_user = populate_model(request.form, DemoUser)
    id_ = get_id(int)
    current_app.logger.info(f'Try to save demo user: {req_demo_user}')
    #
    if not id_:  # Create
        req_demo_user.save()
        id_ = req_demo_user.id
        current_app.logger.info(f'Successfully create demo user: {id_}')
    else:  # Update
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


@demo.route('/team-profile')
@auth_permission
def team_profile():
    """ 团队设置. """
    id_ = get_id(int)
    demo_team = DemoTeam.find_one(id_)
    if not demo_team:
        abort(404)
    #
    return render_template('demo/team-profile.html', demo_team=demo_team)


@demo.route('/team-profile/demo-team-form', methods=('POST',))
@auth_permission
def team_profile_demo_team_form():
    """ 保存团队设置. """
    req_demo_team = populate_model(request.form, DemoTeam)
    id_ = get_id(int)
    current_app.logger.info(f'Try to save demo team: {req_demo_team}')
    #
    if not id_:  # Create
        req_demo_team.save()
        id_ = req_demo_team.id
        current_app.logger.info(f'Successfully create demo team: {id_}')
    else:  # Update
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
    id_ = get_id(int)
    args = []
    if id_:
        demo_project = DemoProject.find_one(id_)
        if not demo_project:
            abort(404)
    else:
        demo_project = DemoProject()
        #
        if 'members_ids' in request.args:
            members_ids = list(map(int, request.args.getlist('members_ids')))
            demo_project.members = DemoUser.find_by_ids(members_ids)
            args.extend([('members_ids', i) for i in members_ids])
    #
    preloads = {}
    demo_users, demo_users_pagination = DemoUser.search({}, projection=['avatar', 'name', 'status', 'roles', 'email', 'phone', 'create_time'], sort=[('create_time', -1)])
    current_app.logger.info(f'Preloaded {len(demo_users)} demo users')
    preloads.update({'demo_users': demo_users, 'demo_users_pagination': dict(demo_users_pagination), })
    #
    return render_template('demo/project-edit.html', demo_project=demo_project, args=args, **preloads)


@demo.route('/project-edit/demo-project-form', methods=('POST',))
@auth_permission
def project_edit_demo_project_form():
    """ 保存项目编辑. """
    req_demo_project = populate_model(request.form, DemoProject)
    id_ = get_id(int)
    current_app.logger.info(f'Try to save demo project: {req_demo_project}')
    #
    if not id_:  # Create
        req_demo_project.save()
        id_ = req_demo_project.id
        current_app.logger.info(f'Successfully create demo project: {id_}')
    else:  # Update
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


@demo.route('/project-edit/demo-project-form/search-demo-users', methods=('POST',))
@auth_permission
def project_edit_demo_project_form_search_demo_users():
    """ 查找用户. """
    page, sort = request.form.get('p', 1, lambda x: int(x) if x.isdigit() else 1), [('create_time', -1)]
    search, condition = populate_search(request.form, DemoUser)
    current_app.logger.info(f'Try to search demo user at page {page} by {condition}, sort by {sort}')
    demo_users, pagination = DemoUser.search(condition, page, projection=['avatar', 'name', 'status', 'roles', 'email', 'phone', 'create_time'], sort=sort)
    return jsonify(error=0, message='Search demo user successfully.', pagination=dict(pagination), demo_users=demo_users)


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
    id_ = get_id(int)
    args = []
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
        if 'user_id' in request.args:
            user_id = int(request.args.get('user_id'))
            demo_task.user = DemoUser.find_one(user_id)
            args.append(('user_id', user_id))
    #
    preloads = {}
    demo_users, demo_users_pagination = DemoUser.search({}, projection=['avatar', 'name', 'status', 'roles', 'email', 'phone', 'create_time'], sort=[('create_time', -1)])
    current_app.logger.info(f'Preloaded {len(demo_users)} demo users')
    preloads.update({'demo_users': demo_users, 'demo_users_pagination': dict(demo_users_pagination), })
    #
    return render_template('demo/task-edit.html', demo_task=demo_task, args=args, **preloads)


@demo.route('/task-edit/demo-task-form', methods=('POST',))
@auth_permission
def task_edit_demo_task_form():
    """ 保存任务编辑. """
    req_demo_task = populate_model(request.form, DemoTask)
    id_ = get_id(int)
    current_app.logger.info(f'Try to save demo task: {req_demo_task}')
    #
    if not id_:  # Create
        req_demo_task.save()
        id_ = req_demo_task.id
        current_app.logger.info(f'Successfully create demo task: {id_}')
    else:  # Update
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


@demo.route('/task-edit/demo-task-form/search-demo-users', methods=('POST',))
@auth_permission
def task_edit_demo_task_form_search_demo_users():
    """ 查找用户. """
    page, sort = request.form.get('p', 1, lambda x: int(x) if x.isdigit() else 1), [('create_time', -1)]
    search, condition = populate_search(request.form, DemoUser)
    current_app.logger.info(f'Try to search demo user at page {page} by {condition}, sort by {sort}')
    demo_users, pagination = DemoUser.search(condition, page, projection=['avatar', 'name', 'status', 'roles', 'email', 'phone', 'create_time'], sort=sort)
    return jsonify(error=0, message='Search demo user successfully.', pagination=dict(pagination), demo_users=demo_users)


#
# 商城
#
attr_color = DemoAttribute(
    key='color',
    name='Color',
    options=[
        DemoAttributeOption(title='Black', value='#12263F'),
        DemoAttributeOption(title='White', value='#EDF2F9'),
        DemoAttributeOption(title='Blue', value='#2C7BE5'),
        DemoAttributeOption(title='Red', value='#E63757'),
        DemoAttributeOption(title='Gray', value='#283E59'),
        DemoAttributeOption(title='Pink', value='#FF679B'),
        DemoAttributeOption(title='Green', value='#00D97E'),
    ]
)
attr_color.save()
attr_size = DemoAttribute(
    key='size',
    name='Size',
    options=[
        DemoAttributeOption(title='XS', value='XS'),
        DemoAttributeOption(title='S', value='S'),
        DemoAttributeOption(title='M', value='M'),
        DemoAttributeOption(title='L', value='L'),
        DemoAttributeOption(title='XL', value='XL'),
        DemoAttributeOption(title='XXL', value='XXL'),
        DemoAttributeOption(title='One Size', value='ONE'),
    ],
)
attr_size.save()
#
category_clothing = DemoCategory(
    name='Clothing',
    attrs=[attr_color, attr_size],
    promos=[
        {
            'title': 'Summer Sale', 'subtitle': '-70%', 'content': 'with promo code CN67EW*',
            'cls': 'col-12 col-md-6 col-lg-5 col-xl-4 offset-md-2',
            'image': '/static/assets/img/covers/cover-5.jpg',
            'action': {'title': 'Shop Now <i class="fe fe-arrow-right ml-2"></i>', 'cls': 'dark', 'url': 'javascript:coming();'}
        },
        {
            'title': 'Summer Collection', 'content': 'So called give, one whales tree seas dry place own day, winged tree created spirit.',
            'cls': 'col-12 col-md-6 col-lg-5 col-xl-4 offset-md-7',
            'image': '/static/assets/img/covers/cover-23.jpg',
            'action': {'title': 'Shop Now <i class="fe fe-arrow-right ml-2"></i>', 'cls': 'dark', 'url': 'javascript:coming();'}
        },
        {
            'title': 'Summer Styles', 'subtitle': '<span class="text-white">50% OFF</span>',
            'cls': 'col-12 text-center text-white',
            'image': '/static/assets/img/covers/cover-16.jpg',
            'action': {'title': 'Shop Women <i class="fe fe-arrow-right ml-2"></i>', 'cls': 'outline-white', 'url': 'javascript:coming();'}
        },
    ],
)
category_clothing.save()


@demo.route('/shop-index')
@auth_permission
def shop_index():
    """ 商城首页. """
    return render_template('demo/shop-index.html')


@demo.route('/shop-index-asymmetric')
@auth_permission
def shop_index_asymmetric():
    """ 商城首页. """
    return render_template('demo/shop-index-asymmetric.html')


@demo.route('/shop-index-horizontal')
@auth_permission
def shop_index_sidenav():
    """ 商城首页. """
    return render_template('demo/shop-index-horizontal.html')


@demo.route('/shop-category')
@auth_permission
def shop_category():
    """ 商城类目. """
    id_ = get_id(int)
    if not id_:
        id_ = 1
    #
    demo_category = DemoCategory.find_one(id_)
    if not demo_category:
        abort(404)
    # filters is {DemoAttribute.key: [DemoAttributeOption]}, meaning selected attribute options
    # e.g, {size: [l, xl], color: [red, blue]}
    filters = {}
    for a in demo_category.attrs:
        params = request.values.getlist(a.key)
        selected_options = []
        # check if request param has valid value
        for p in params:
            found_option = next((o for o in a.options if o.value == p.strip()), None)
            if found_option:
                selected_options.append(found_option)
        #
        if selected_options:
            filters[a.key] = selected_options
    #
    return render_template('demo/shop-category.html', demo_category=demo_category, filters=filters)
