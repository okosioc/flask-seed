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
        'children': [

        ]
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
    #
    # Shop
    #
    {
        'key': 'header-shop',
        'title': 'Shop.',
        'subtitle': '<i class="fe fe-truck mr-2"></i><span>Free Shipping Worldwide</span>',
        'children': [
            {
                'title': 'Home', 'url': '#',
                'children': [
                    {'title': 'Default', 'url': '/shop/index'},
                    {'title': 'Asymmetric', 'url': '/shop/index-asymmetric'},
                    {'title': 'Sidenav', 'url': '/shop/index-sidenav'},
                ],
            },
            {'title': 'Catelog', 'url': 'javascript:coming();'},
            {'title': 'Blog', 'url': 'javascript:coming();'},
            {'title': 'Account', 'url': 'javascript:coming();'},
            {'title': '<i class="fe fe-search d-inline"></i>', 'url': 'javascript:coming();'},
            {'title': '<i class="fe fe-shopping-cart d-inline"></i>', 'url': 'javascript:coming();'},
        ]
    },
    {
        'key': 'welcome-shop',
        'children': [
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
        ]
    },
    {
        'key': 'categories-shop',
        'children': [
            {
                'title': 'Summer Hats',
                'image': '/static/assets/img/products/product-22.jpg',
                'action': {'title': 'Shop Now <i class="fe fe-arrow-right ml-2"></i>', 'url': 'javascript:coming();'}
            },
            {
                'title': 'Men Hats',
                'image': '/static/assets/img/products/product-23.jpg',
                'action': {'title': 'Shop Now <i class="fe fe-arrow-right ml-2"></i>', 'url': 'javascript:coming();'}
            },
            {
                'title': 'Floral Dresses',
                'image': '/static/assets/img/products/product-24.jpg',
                'action': {'title': 'Shop Now <i class="fe fe-arrow-right ml-2"></i>', 'url': 'javascript:coming();'}
            },
        ],
    },
    {
        'key': 'categories-must-haves-shop',
        'title': 'Our must haves',
        'content': 'Open created shall two he second moving whose. He face whose two upon, fowl behold waters. Fly there their day creepeth. Darkness beginning spirit after.',
        'remarks': 'Third. For morning whales saw were had seed can\'t divide it light shall moveth, us blessed given.',
        'action': {'title': 'Discover more', 'url': 'javascript:coming();'},
        'children': [
            {
                'title': 'Dress', 'url': '#',
                'image': '/static/assets/img/products/product-71.jpg',
            },
            {
                'title': 'Cropped Trousers', 'url': '#',
                'image': '/static/assets/img/products/product-72.jpg',
            },
        ],
    },
    {
        'key': 'products-best-sellers-shop',
        'tag': 'Monthly Top Sellings',
        'title': 'Best Sellers',
        'children': [
            {
                'title': 'Leather mid-heel Sandals', 'subtitle': 'Shoes', 'content': '$129.00',
                'images': ['/static/assets/img/products/product-120.jpg', '/static/assets/img/products/product-5.jpg']
            },
            {
                'title': 'Cotton floral print Dress', 'subtitle': 'Dresses', 'content': '$40.00',
                'images': ['/static/assets/img/products/product-121.jpg', '/static/assets/img/products/product-6.jpg']
            },
            {
                'tag': 'HOT', 'title': 'Leather Sneakers', 'subtitle': 'Shoes', 'content': '<span class="text-decoration-line-through">$85.00</span><span class="ml-2 text-danger">$50.00</span>',
                'images': ['/static/assets/img/products/product-122.jpg', '/static/assets/img/products/product-7.jpg']
            },
            {
                'title': 'Cropped cotton Top', 'subtitle': 'Tops', 'content': '$29.00',
                'images': ['/static/assets/img/products/product-8.jpg']
            },
            {
                'title': 'Floral print midi Dress', 'subtitle': 'Dresses', 'content': '$55.00',
                'images': ['/static/assets/img/products/product-9.jpg']
            },
            {
                'tag': 'HOT', 'title': 'Suede cross body Bag', 'subtitle': 'Bags', 'content': '<span class="text-decoration-line-through">$79.00</span><span class="ml-2 text-danger">$49.00</span>',
                'images': ['/static/assets/img/products/product-123.jpg', '/static/assets/img/products/product-10.jpg']
            },
            {
                'title': 'Printed A-line Skirt', 'subtitle': 'Skirts', 'content': '$79.00',
                'images': ['/static/assets/img/products/product-124.jpg', '/static/assets/img/products/product-11.jpg']
            },
            {
                'tag': 'NEW', 'title': 'Heel strappy Sandals', 'subtitle': 'Shoes', 'content': '$90.00',
                'images': ['/static/assets/img/products/product-12.jpg']
            },
        ],
    },
    {
        'key': 'products-asymmetric-shop',
        'children': [
            {
                'title': 'Floral Cotton midi Dress', 'content': '$59.00',
                'image': '/static/assets/img/products/product-65.jpg',
            },
            {
                'title': 'Linen basic Trousers', 'content': '$125.00',
                'image': '/static/assets/img/products/product-66.jpg',
            },
            {
                'tag': 'HOT', 'title': 'Leather heel Sandals', 'content': '$89.99',
                'image': '/static/assets/img/products/product-67.jpg',
            },
            {
                'title': 'Leather square Tote Bag', 'content': '$35.00',
                'image': '/static/assets/img/products/product-68.jpg',
            },
            {
                'title': 'Cotton basic T-Shirt', 'content': '$50.00',
                'image': '/static/assets/img/products/product-69.jpg',
            },
            {
                'title': 'Acymmetric Cotton Top', 'content': '$39.00',
                'image': '/static/assets/img/products/product-70.jpg',
            },
        ],
    },
    {
        'key': 'banner-shop',
        'tag': 'Summer trends',
        'title': 'Our must haves',
        'content': 'Male his our upon seed had said wherein their i great wherein under you\'ll deep first multiply. Fish waters they\'re herb shall saying.',
        'image': '/static/assets/img/covers/cover-10.jpg',
        'action': {'title': 'Shop Now <i class="fe fe-arrow-right ml-2"></i>', 'cls': 'dark', 'url': 'javascript:coming();'},
    },
    {
        'key': 'banner-discount-shop',
        'subtitle': 'Summer Styles',
        'title': '50% OFF',
        'image': '/static/assets/img/covers/cover-17.jpg',
        'actions': [
            {'title': 'Shop Woman', 'url': 'javascript:coming();'},
            {'title': 'Shop Men', 'url': 'javascript:coming();'},
        ],
    },
    {
        'key': 'products-new-arrivals-shop',
        'tag': 'Summer new products',
        'title': 'New Arrivals',
        'children': [
            {
                'title': 'Cotton floral print Dress', 'content': '$40.00',
                'image': '/static/assets/img/products/product-6.jpg',
            },
            {
                'tag': 'HOT', 'title': 'Suede cross body Bag', 'content': '<span class="text-decoration-line-through">$85.00</span><span class="ml-2 text-danger">$50.00</span>',
                'image': '/static/assets/img/products/product-10.jpg',
            },
            {
                'title': 'Cotton leaf print Shirt', 'content': '$65.00',
                'image': '/static/assets/img/products/product-32.jpg',
            },
            {
                'title': 'Leather Sneakers', 'content': '$50.00',
                'image': '/static/assets/img/products/product-7.jpg',
            },
            {
                'title': 'Another fine dress', 'content': '$99.00',
                'image': '/static/assets/img/products/product-11.jpg',
            },
            {
                'title': 'Baseball Cap', 'content': '$10.00',
                'image': '/static/assets/img/products/product-33.jpg',
            },
            {
                'title': 'Leather sneakers', 'content': '$19.00',
                'image': '/static/assets/img/products/product-49.jpg',
            },
        ],
    },
    {
        'key': 'reviews-shop',
        'tag': 'What buyers say',
        'title': 'Latest buyers Reviews',
        'children': [
            {
                'title': 'Low top Sneakers', 'subtitle': 'Shoes', 'value': 3.,
                'image': '/static/assets/img/products/product-13.jpg',
                'content': 'From creepeth said moved given divide make multiply of him shall itself also above second doesn\'t unto created saying land herb sea midst night wherein.',
                'remarks': 'Logan Edwards, 01 Jun 2019',
            },
            {
                'title': 'Cotton print Dress', 'subtitle': 'Dresses', 'value': 5.,
                'image': '/static/assets/img/products/product-14.jpg',
                'content': 'God every fill great replenish darkness unto. Very open. Likeness their that light. Given under image to. Subdue of shall cattle day fish form saw spirit and given stars, us you whales may, land, saw fill unto.',
                'remarks': 'Jane Jefferson, 29 May 2019',
            },
            {
                'title': 'Oversized print T-shirt', 'subtitle': 'T-shirts', 'value': 4.,
                'image': '/static/assets/img/products/product-15.jpg',
                'content': 'Fill his waters wherein signs likeness waters. Second light gathered appear sixth fourth, seasons behold creeping female.',
                'remarks': 'Darrell Baker, 18 May 2019',
            },
            {
                'title': 'Suede cross body Bag', 'subtitle': 'Bags & Accessories', 'value': 4.,
                'image': '/static/assets/img/products/product-13.jpg',
                'content': 'God every fill great replenish darkness unto. Very open. Likeness their that light. Given under image to. Subdue of shall cattle day fish form saw spirit and given stars.',
                'remarks': 'Pavel Doe, 29 May 2019',
            },
        ],
    },
    {
        'key': 'social-shop',
        'title': '@shop',
        'subtitle': 'Appear, dry there darkness they\'re seas, dry waters.',
        'children': [
            {
                'image': '/static/assets/img/products/product-16.jpg',
                'content': '<i class="fe fe-heart mr-2"></i> 248 <i class="fe fe-message-square mr-2 ml-3"></i> 7',
            },
            {
                'image': '/static/assets/img/products/product-17.jpg',
                'content': '<i class="fe fe-heart mr-2"></i> 248 <i class="fe fe-message-square mr-2 ml-3"></i> 7',
            },
            {
                'image': '/static/assets/img/products/product-18.jpg',
                'content': '<i class="fe fe-heart mr-2"></i> 248 <i class="fe fe-message-square mr-2 ml-3"></i> 7',
            },
            {
                'image': '/static/assets/img/products/product-19.jpg',
                'content': '<i class="fe fe-heart mr-2"></i> 248 <i class="fe fe-message-square mr-2 ml-3"></i> 7',
            },
            {
                'image': '/static/assets/img/products/product-20.jpg',
                'content': '<i class="fe fe-heart mr-2"></i> 248 <i class="fe fe-message-square mr-2 ml-3"></i> 7',
            },
            {
                'image': '/static/assets/img/products/product-21.jpg',
                'content': '<i class="fe fe-heart mr-2"></i> 248 <i class="fe fe-message-square mr-2 ml-3"></i> 7',
            },
        ],
    },
    {
        'key': 'footer-shop',
        'title': 'Shop.',
        'children': [
            {'title': 'Contact Us', 'url': 'javascript:coming();'},
            {'title': 'FAQs', 'url': 'javascript:coming();'},
            {'title': 'Size Guide', 'url': 'javascript:coming();'},
            {'title': 'Shipping & Returns', 'url': 'javascript:coming();'},
            {'title': 'Terms & Conditions', 'url': 'javascript:coming();'},
            {'title': 'Privacy & Cookie Policy', 'url': 'javascript:coming();'},
        ],
        'remarks': '2023 © flask-seed.com',
    },
]
