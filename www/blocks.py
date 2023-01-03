# -*- coding: utf-8 -*-
"""
    blocks
    ~~~~~~~~~~~~~~

    预加载页面版块.

    :copyright: (c) 2021 by weiminfeng.
    :date: 2022/12/14
"""

BLOCKS = [
    # Headers
    {
        'key': 'header',
        'icon': '/static/img/logo.png',
        'children': []
    },
    {
        'key': 'header-dash',
        'children': [
            {'icon': 'fe fe-user', 'title': '账号设置', 'url': '/dashboard/profile'},
            {'title': ''},
            {'icon': 'fe fe-log-out', 'title': '退出', 'url': '/logout'}
        ]
    },
    # Promos
    {
        'key': 'promo',
        'title': 'Welcome to <span class="text-primary">flask-seed</span>.<br>Develop anything.',
        'subtitle': '数据结构+项目模板，生成易于二次开发的种子项目',
        'image': '/static/assets/img/illustrations/cowork.png',
        'children': [
            {'title': 'Github<i class="fe fe-github d-none d-md-inline ml-2"></i>', 'url': 'https://github.com/okosioc/flask-seed/', 'cls': 'btn btn-primary'},
            {'title': 'View all pages<i class="fe fe-arrow-right d-none d-md-inline ml-2"></i>', 'url': '/dashboard', 'cls': 'btn btn-outline-primary'},
        ]
    },
    # Features
    {
        'key': 'features',
        'title': '',
        'subtitle': '',
        'children': [
            {
                'icon': '<svg width="48" height="48" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><g fill="none" fill-rule="evenodd"><path d="M0 0h24v24H0z"></path><path d="M4 9.675l6.88 3.972a.89.89 0 00.231.093v7.704l-6.62-3.918a1 1 0 01-.491-.86V9.675zm16-.106v7.097a1 1 0 01-.49.86l-6.621 3.918v-7.771a.903.903 0 00.048-.026L20 9.569z" fill="#335EEA"></path><path d="M4.216 7.747a.999.999 0 01.314-.262l7-3.728a1 1 0 01.94 0l7 3.728c.095.05.18.116.253.191l-7.675 4.431a.893.893 0 00-.14.1.893.893 0 00-.139-.1l-7.553-4.36z" fill="#335EEA" opacity=".3"></path></g></svg>',
                'title': '数据结构', 'content': '通过简单的方式定义业务所需的数据结构，无需考虑存储细节，支持主流数据库。'},
            {
                'icon': '<svg width="48" height="48" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><g fill="none" fill-rule="evenodd"><path d="M0 0h24v24H0z"></path><path d="M13.207 4A5.5 5.5 0 0020 10.793V17a3 3 0 01-3 3H7a3 3 0 01-3-3V7a3 3 0 013-3h6.207z" fill="#335EEA"></path><circle fill="#335EEA" opacity=".3" cx="18.5" cy="5.5" r="2.5"></circle></g></svg>',
                'title': '项目模板', 'content': '定义项目蓝图，即可配合项目模板生成各个平台的种子项目，如网站、小程序、iOS和Android应用等等，内置了多个专业的项目模板。'},
            {
                'icon': '<svg width="48" height="48" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><g fill="none" fill-rule="evenodd"><path d="M0 0h24v24H0z"></path><path d="M7 3h10a4 4 0 110 8H7a4 4 0 110-8zm0 6a2 2 0 100-4 2 2 0 000 4z" fill="#335EEA"></path><path d="M7 13h10a4 4 0 110 8H7a4 4 0 110-8zm10 6a2 2 0 100-4 2 2 0 000 4z" fill="#335EEA" opacity=".3"></path></g></svg>',
                'title': '二次开发', 'content': '可以方便的对种子项目进行二次开发，如果数据结构或者模板组件的有更新，可重新生成项目，代码会自动合并。'}
        ]
    },
    {
        'key': 'feature-1',
        'icon': 'DATA',
        'title': '数据优先',
        'subtitle': '数据结构决定了整个项目的业务逻辑，可配合项目模板生成种子项目',
        'image': '/static/assets/img/illustrations/think.png',
        'children': [
            {'title': '支持数据结构的嵌套，并可通过优雅的方式支持数据结构之间的关系', 'subtitle': ''},
            {'title': '支持内存以及主流数据库，包含MySQL以及MongoDB等', 'subtitle': ''},
            {'title': '通过数据字段的格式指定前端组件的使用', 'subtitle': ''}
        ]
    },
    {
        'key': 'feature-2',
        'icon': 'TEMPLATE',
        'title': '项目模板',
        'subtitle': '通过定义<span class="text-primary">蓝图</span>可以生成多个平台的项目',
        'image': '/static/assets/img/illustrations/design.png',
        'children': [
            {'title': '多平台', 'subtitle': '可以生成多个平台的项目，如网站、小程序、iOS和Android应用等'},
            {'title': '专业模板', 'subtitle': '生成符合最佳实践的项目组织结构以及规范代码'},
            {'title': '组件化', 'subtitle': '定义数据结构时可以指定字段使用的格式，生成项目时可以生成对应的组件'}
        ]
    },
    # Pricings
    {
        'key': 'pricing',
        'icon': 'PRICING',
        'title': '产品价格',
        'subtitle': '免费使用',
        'children': [
            {
                'title': 'FREE',
                'subtitle': '免费',
                'action': {'title': '免费使用', 'url': '/dashboard', 'cls': 'primary'},
                'children': [
                    {'title': '开源', 'content': '<i class="fe fe-check-circle text-success"></i>'},
                    {'title': '默认模板', 'content': '<i class="fe fe-check-circle text-success"></i>'},
                    {'title': '客户支持', 'content': '<i class="fe fe-x-circle text-danger"></i>'},
                ]
            },
            {
                'title': 'ENTERPRISE',
                'subtitle': '定制',
                'action': {'title': '联系我们', 'url': 'javascript:coming()', 'cls': 'light'},
                'children': [
                    {'title': '开源', 'content': '<i class="fe fe-check-circle text-success"></i>'},
                    {'title': '定制模板', 'content': '<i class="fe fe-check-circle text-success"></i>'},
                    {'title': '客户支持', 'content': '<i class="fe fe-check-circle text-success"></i>'},
                ]
            },
        ]
    },
    # Footers
    {
        'key': 'footer',
        'title': 'flask-seed',
        'subtitle': '数据结构+项目模板=种子项目',
        'action': {'title': '免费试用<i class="fe fe-arrow-right d-none d-md-inline ml-2"></i>', 'url': '/dashboard'},
        'remarks': '2023 © flask-seed.com',
    },
    {
        'key': 'footer-simple',
        'remarks': '2023 © flask-seed.com',
    },
    {
        'key': 'footer-dash',
        'remarks': '2023 © flask-seed.com',
        'children': [
            {'title': 'About Us', 'url': 'javascript:coming();'},
            {'title': 'Help', 'url': 'javascript:coming();'}
        ]
    },
]
