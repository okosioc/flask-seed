# -*- coding: utf-8 -*-
"""
    demodata
    ~~~~~~~~~~~~~~

    Demo data.

    :copyright: (c) 2021 by weiminfeng.
    :date: 2023/7/26
"""

from datetime import datetime
from werkzeug.security import generate_password_hash
from core.models import DemoTeam, DemoUser, DemoProject, DemoTask, DemoUserRole, DemoActivity, DemoCategory, DemoAttribute, DemoAttributeOption
from www.tools import str_datetime


def prepare_demo_data():
    """ 准备演示数据, 请注意所有演示数据都是使用内存模型. """
    #
    # 仪表盘演示数据
    #

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

    #
    # 商城演示数据
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
