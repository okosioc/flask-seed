# -*- coding: utf-8 -*-
"""
    demo
    ~~~~~~~~~~~~~~

    用于演示的数据结构.

    :copyright: (c) 2021 by weiminfeng.
    :date: 2022/7/8
"""

from datetime import datetime
from typing import List, ForwardRef

from flask_login import UserMixin
from py3seed import SimpleEnum, CacheModel, ModelField as Field, RelationField as Relation, register, BaseModel, Format, Comparator, Ownership
from werkzeug.utils import cached_property

from .common import Block


@register
class DemoPage(CacheModel):
    """ 页面. """
    key: str = Field(searchable=Comparator.EQ, title='页面标识', description='通过该标识自动匹配模版')
    title: str = Field(searchable=Comparator.LIKE, icon='type', title='页面标题')
    blocks: List[Block] = Relation(title='区块')
    #
    update_time: datetime = Field(required=False, title='更新时间')
    create_time: datetime = Field(default=datetime.now, icon='clock', title='创建时间')
    #
    __icon__ = 'file'
    __title__ = '页面'
    #
    __actions__ = {
        'demo/page-list': {
            'domains': ['www'],
            'layout': '''#!query?title=页面管理
                key, title, blocks, create_time
            ''',
        },
        'demo/page-edit': {
            'domains': ['www'],
            'layout': '''#!form?title=页面编辑
                key, title
                blocks
            ''',
        },
        # 如果没有设置blueprint, 默认放在public下, 无需权限即可访问
        # 如果layout没有布局信息, 表示只根据action(即下述#!read_by_key)生成后端逻辑, 而无需生成页面模版; 页面模版需要开发人员自行实现
        'page-detail': {
            'domains': ['www'],
            'layout': '''#!read_by_key
            ''',
        },
    }


class DemoTeamStatus(SimpleEnum):
    """ 团队状态. """
    NORMAL = 'normal', '正常'
    REJECTED = 'rejected', '禁用'


@register
class DemoTeam(CacheModel):
    """ 团队. """
    name: str = Field(searchable=Comparator.LIKE, icon='type', title='团队名称')
    status: DemoTeamStatus = Field(searchable=Comparator.EQ, default=DemoTeamStatus.NORMAL, icon='circle', title='团队状态')
    logo: str = Field(required=False, format_=Format.AVATAR, title='团队图标')
    code: str = Field(required=False, title='邀请码')
    remarks: str = Field(required=False, format_=Format.TEXTAREA, title='备注')
    #
    update_time: datetime = Field(required=False, title='更新时间')
    create_time: datetime = Field(default=datetime.now, icon='clock', title='创建时间')
    #
    __icon__ = 'users'
    __title__ = '团队'
    #
    __actions__ = {
        'demo/team-profile': {
            'domains': ['www'],
            'layout': '''#!form?title=团队设置
                $#4,           0#8      
                  logo           name   
                  name           code   
                  status         remarks
                  members        logo   
                  create_time  
            ''',
        },
        'demo/team-members': {
            'domains': ['www'],
            'layout': '''#!read?title=团队成员
                $#4,           members#8                                                  
                  logo           avatar, name, status, roles, email, phone, team_join_time
                  name                                                                    
                  status                                                                  
                  members                                                                 
                  create_time
            ''',
        },
    }


class DemoUserStatus(SimpleEnum):
    """ 用户状态. """
    NORMAL = 'normal', '正常'
    OVERDUE = 'overdue', '过期'
    REJECTED = 'rejected', '禁用'


class DemoUserRole(SimpleEnum):
    """ 用户角色. """
    MEMBER = 'member', '普通用户'
    EDITOR = 'editor', '编辑'
    ADMIN = 'admin', '管理员'


class DemoUserType(SimpleEnum):
    """ 用户类型. """
    TRIAL = 'trial', '试用'
    STANDARD = 'standard', '标准'
    ENTERPRISE = 'enterprise', '企业'


@register
class DemoUser(CacheModel, UserMixin):
    """ 用户. """
    name: str = Field(searchable=Comparator.LIKE, icon='type', title='用户名')
    status: DemoUserStatus = Field(default=DemoUserStatus.NORMAL, icon='circle', title='用户状态')
    roles: List[DemoUserRole] = Field(default=[DemoUserRole.MEMBER], format_=Format.SELECT, icon='box', title='用户角色')
    type: DemoUserType = Field(default=DemoUserType.STANDARD, title='用户类型')  # 默认为标准类型
    due_date: str = Field(required=False, format_=Format.DATE, title='过期日')  # 通过定时任务检测到过期日
    email: str = Field(icon='mail', title='登录邮箱')
    password: str = Field(format_=Format.PASSWORD, title='登录密码')
    phone: str = Field(required=False, searchable=Comparator.LIKE, icon='phone', title='手机号')
    avatar: str = Field(required=False, format_=Format.AVATAR, title='头像')
    intro: str = Field(required=False, format_=Format.TEXTAREA, title='个人简介')
    #
    team: DemoTeam = Relation(
        required=False, title='所属团队',
        back_field_name='members', back_field_is_list=True, back_field_order=[('team_join_time', 1)],
        back_field_format=Format.TABLE, back_field_icon='users', back_field_title='团队成员',
    )
    team_join_time: datetime = Field(required=False, title='加入团队的时间')
    #
    update_time: datetime = Field(required=False, title='更新时间')
    create_time: datetime = Field(default=datetime.now, icon='clock', title='创建时间')
    #
    __icon__ = 'user'
    __title__ = '用户'
    #
    __actions__ = {
        'demo/user-profile': {
            'domains': ['www'],
            'layout': '''#!form?title=用户设置
                $#4,           0#8                                           
                  avatar         name  
                  name           phone                                                  
                  status         intro                                                 
                  roles          avatar                                                
                  email
                  phone
                  create_time
            ''',
        },
    }

    @cached_property
    def is_admin(self):
        """ 是否为系统管理员. """
        return DemoUserRole.ADMIN in self.roles

    @cached_property
    def is_editor(self):
        """ 是否为系统编辑. """
        return DemoUserRole.EDITOR in self.roles

    def has_role(self, role):
        """ 检测是否有指定角色. """
        if 'admin' == role:
            return self.is_admin
        elif 'editor' == role:
            return self.is_editor
        else:
            # 默认返回真, 简化页面脚本
            return True

    @cached_property
    def is_rejected(self):
        """ 该账户是否被拒. """
        return self.status == DemoUserStatus.REJECTED

    def get_id(self):
        """ UserMixin of flask-login. """
        return str(self.id)

    def __eq__(self, other):
        return self.id == other.id

    def __str__(self):
        return f'{self.id}/{self.name}'


class DemoTaskStatus(SimpleEnum):
    """ 任务状态. """
    NORMAL = 'normal', '正常'
    OVERDUE = 'overdue', '过期'
    CANCELLED = 'cancelled', '取消'


class DemoActivity(BaseModel):
    """ 项目相关操作. """
    user: DemoUser = Relation(format_=Format.SELECT, title='操作人')
    title: str = Field(title='操作标题')  # 比较简单的说明, 如A新建了项目, A安排任务给B和C等
    content: str = Field(required=False, format_=Format.TEXTAREA, title='操作详情')  # 操作更为详细的说明, 如新建项目的开始结束时间, 安排任务的细节等
    time: datetime = Field(default=datetime.now, title='操作时间')
    #
    __icon__ = 'activity'
    __title__ = '操作'


class DemoProjectStatus(SimpleEnum):
    """ 项目状态. """
    ACTIVE = 'active', '活跃'
    COMPLETED = 'completed', '结束'
    CANCELLED = 'cancelled', '取消'


@register
class DemoProject(CacheModel):
    """ 项目. """
    # 基础信息
    title: str = Field(searchable=Comparator.LIKE, icon='type', title='项目名称')
    description: str = Field(required=False, format_=Format.TEXTAREA, title='项目介绍')
    status: DemoProjectStatus = Field(default=DemoProjectStatus.ACTIVE, searchable=Comparator.EQ, icon='circle', title='项目状态')
    value: float = Field(default=0., icon='dollar-sign', title='项目价值', unit='元')
    start: str = Field(searchable=Comparator.GTE, format_=Format.DATE, icon='calendar', title='开始日期')
    end: str = Field(format_=Format.DATE, icon='calendar', title='结束日期')
    percent: float = Field(default=0., icon='percent', title='项目进度', unit='%')
    # 内部数据结构
    members: List[DemoUser] = Relation(
        required=False, format_=Format.MEDIA, icon='users', title='项目成员',
        back_field_name='projects', back_field_is_list=True, back_field_order=[('create_time', -1)],
        back_field_format=Format.GRID, back_field_title='参与项目',
    )
    activities: List[DemoActivity] = Field(required=False, format_=Format.TIMELINE, title='操作')  # 按照时间倒序
    # 其他
    update_time: datetime = Field(required=False, title='更新时间')
    create_time: datetime = Field(default=datetime.now, icon='clock', title='创建时间')
    #
    __icon__ = 'briefcase'
    __title__ = '项目'
    #
    __actions__ = {
        'demo/project-list': {
            'domains': ['www'],
            'layout': '''#!query?title=项目列表result_view=grid
                title, status, value, start, members, percent, create_time
            ''',
        },
        'demo/project-detail': {
            'domains': ['www'],
            'layout': '''#!read?title=项目详情
                0#4,              1#8
                  $                 tasks                                   
                    title             title, status, user, start, create_time 
                    status          activities                  
                    value             user, title, content, time
                    start         
                    members       
                    percent       
                    create_time   
                  members                         
                    avatar, name            
            ''',
        },
        'demo/project-edit': {
            'domains': ['www'],
            'layout': '''#!form?title=项目编辑
                0?title=项目基本信息
                  title
                  description
                  status, value
                  start, end
                  percent,
                members#4
                  avatar, name            
            ''',
        },
    }


@register
class DemoTask(CacheModel):
    """ 项目所属任务. """
    title: str = Field(title='任务标题')
    status: DemoTaskStatus = Field(default=DemoTaskStatus.NORMAL, title='任务状态')
    content: str = Field(required=False, format_=Format.TEXTAREA, title='任务详情')
    start: str = Field(required=False, format_=Format.DATE, title='开始日期')
    end: str = Field(required=False, format_=Format.DATE, title='结束日期')
    #
    project: DemoProject = Relation(
        title='所属项目',
        back_field_name='tasks', back_field_is_list=True, back_field_order=[('create_time', -1)],
        back_field_format=Format.TABLE, back_field_title='任务列表',
        ownership=Ownership.OWN,
    )
    user: DemoUser = Relation(
        format_=Format.SELECT, title='负责人',
        back_field_name='tasks', back_field_is_list=True, back_field_order=[('create_time', -1)],
        back_field_format=Format.TABLE, back_field_title='任务列表',
    )
    #
    update_time: datetime = Field(required=False, title='更新时间')
    create_time: datetime = Field(default=datetime.now, title='创建时间')
    #
    __icon__ = 'check-square'
    __title__ = '任务'
    #
    __actions__ = {
        'demo/task-detail': {
            'domains': ['www'],
            'layout': '''#!read?title=任务详情
                project#4,       0#8     
                  $                title 
                    title          status     
                    status         content    
                    value          start, end 
                    start          user       
                    members        create_time
                    percent    
                    create_time
            ''',
        },
        'demo/task-edit': {
            'domains': ['www'],
            'layout': '''#!form?title=任务编辑
                project#4,       0#8           
                  $                title       
                    title          status      
                    status         content     
                    value          start, end  
                    start          user         
                    members         
                    percent                    
                    create_time        
            ''',
        },
    }


@register
class DemoProjectDashboard(CacheModel):
    """ 仪表盘数据. """
    # Metricx4
    active_projects_count: int = Field(default=0, format_=Format.METRIC, icon='briefcase', title='活跃项目数量')
    active_projects_value: float = Field(default=0., format_=Format.METRIC, icon='dollar-sign', title='活跃项目价值', unit='元')
    members_count: int = Field(default=0, format_=Format.METRIC, icon='users', title='团队成员数量')
    tasks_count: int = Field(default=0, format_=Format.METRIC, icon='check-square', title='任务数量')
    # Table&Media
    active_projects: List[DemoProject] = Relation(format_=Format.TABLE, title='活跃项目')
    recent_activities: List[DemoActivity] = Field(format_=Format.TIMELINE, title='最近操作')  # 按照时间倒序
    #
    __actions__ = {
        'demo/project-dashboard': {
            'domains': ['www'],
            'layout': '''#!read?title=仪表盘
                active_projects_count, active_projects_value, members_count, tasks_count
                active_projects#8, recent_activities#4
            ''',
        }
    }


class DemoAttributeOption(BaseModel):
    """ 属性选项. """
    title: str = Field(title='名称')
    value: str = Field(title='值')


@register
class DemoAttribute(CacheModel):
    """ 属性. """
    key: str = Field(title='唯一标识')  # 属性唯一标识, 一般为小写, 如, color
    name: str = Field(icon='type', title='名称')  # 如, 颜色
    unit: str = Field(required=False, title='单位')
    options: List[DemoAttributeOption] = Field(format_=Format.TABLE, title='选项')
    remarks: str = Field(required=False, format_=Format.TEXTAREA, title='备注')


@register
class DemoCategory(CacheModel):
    """ 类目. """
    name: str = Field(icon='type', title='名称')
    parent: ForwardRef('DemoCategory') = Field(required=False, title='父分类')
    #
    attrs: List[DemoAttribute] = Relation(required=False, format_=Format.TABLE, title='属性')
    promos: List[Block] = Field(required=False, title='推广')
    #
    update_time: datetime = Field(required=False, title='更新时间')
    create_time: datetime = Field(default=datetime.now, title='创建时间')
    #
    __icon__ = 'grid'
    __title__ = '类目'


class DemoProductAttribute(BaseModel):
    """ 产品属性值, e.g, 产品有面料属性, 面料为莫代尔, 这些属性不影响SKU. """
    attr: DemoAttribute = Relation(title='属性')
    value: str = Field(title='属性值', depends=lambda x: x.attr.options)
    is_required: bool = Field(default=False, title='是否必填')
    is_sku: bool = Field(default=False, title='是否SKU属性')  # 产品属性是否是SKU属性, 保存SKU时同步更新, 方便查询
    image: str = Field(required=False, format_=Format.IMAGE, title='属性图片')  # e.g, 颜色属性往往会有不同的小图


@register
class DemoProduct(CacheModel):
    """ 产品. """
    no: str = Field(title='')
    name: str = Field(icon='type', title='名称')
    category: DemoCategory = Relation(
        title='分类',
        back_field_name='products', back_field_is_list=True, back_field_order=[('create_time', -1)],
        back_field_format=Format.GRID, back_field_title='参与项目',
    )
    # 基本信息
    price: float = Field(default=0., icon='dollar-sign', title='价格')
    original_price: float = Field(required=False, title='原价')
    images: List[str] = Field(required=False, format_=Format.IMAGE, title='图片列表')
    description: str = Field(required=False, format_=Format.RTE, title='介绍')
    # 属性
    attrs: List[DemoProductAttribute] = Field(format_=Format.TABLE, title='属性')
    # 客户点评
    #
    update_time: datetime = Field(required=False, title='更新时间')
    create_time: datetime = Field(default=datetime.now, title='创建时间')
    #
    __icon__ = 'shopping-bag'
    __title__ = '产品'


@register
class DemoSku(CacheModel):
    """ 产品的库存信息. """
    no: str = Field(title='货号')
    product: DemoProduct = Relation(
        title='产品',
        back_field_name='skus', back_field_is_list=True, back_field_order=[('create_time', -1)],
        back_field_format=Format.TABLE, back_field_title='参与项目',
    )
    #
    attrs: List[DemoProductAttribute] = Field(format_=Format.TABLE, title='属性')  # 一个SKU对应多个属性, 如颜色和尺码
    quanity: int = Field(default=0, title='可销售数量')
    #
    update_time: datetime = Field(required=False, title='更新时间')
    create_time: datetime = Field(default=datetime.now, title='创建时间')
    #
    __icon__ = 'database'
    __title__ = 'SKU'
