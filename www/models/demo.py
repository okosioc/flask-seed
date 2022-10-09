# -*- coding: utf-8 -*-
"""
    demo
    ~~~~~~~~~~~~~~

    用于演示的数据结构.

    :copyright: (c) 2021 by weiminfeng.
    :date: 2022/7/8
"""

from datetime import datetime
from typing import List

from bson import ObjectId
from flask_login import UserMixin
from py3seed import SimpleEnum, CacheModel, ModelField as Field, RelationField as Relation, register, BaseModel, Format, Comparator
from werkzeug.utils import cached_property


class DemoSeries(BaseModel):
    """ 序列, 适用于各种线图/柱状图/饼图的绘制. """
    title: str = Field(title='标题')
    total: float = Field(default=.0, title='数值的和')
    names: List[str] = Field(required=False, title='各元素的名字')
    values: List[float] = Field(required=False, title='各元素对应的数值')
    unit: str = Field(required=False, title='单位')


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
    update_time: datetime = Field(required=False, title='最近更新时间')
    create_time: datetime = Field(default=datetime.now, icon='clock', title='创建时间')
    #
    __icon__ = 'users'
    __title__ = '团队'
    __columns__ = ['logo', 'name', 'status', 'members', 'create_time']  # members is a back relation field auto-created from user
    __form__ = '''
    name
    code
    remarks
    logo
    '''


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
        title='所属团队',
        back_field_name='members', back_field_is_list=True, back_field_order=[('team_join_time', 1)],
        back_field_format=Format.TABLE, back_field_icon='users', back_field_title='团队成员',
    )
    team_join_time: datetime = Field(title='加入团队的时间')
    #
    update_time: datetime = Field(required=False, title='最近更新时间')
    create_time: datetime = Field(default=datetime.now, icon='clock', title='创建时间')
    #
    __icon__ = 'user'
    __title__ = '用户'
    __columns__ = ['avatar', 'name', 'status', 'roles', 'email', 'phone', 'create_time']
    __form__ = '''
    name
    phone
    intro
    avatar  
    '''

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
    user: DemoUser = Relation(format_=Format.SELECT, icon='user', title='操作人')
    title: str = Field(title='操作标题')  # 比较简单的说明, 如A新建了项目, A安排任务给B和C等
    content: str = Field(required=False, format_=Format.TEXTAREA, title='操作详情')  # 操作更为详细的说明, 如新建项目的开始结束时间, 安排任务的细节等
    time: datetime = Field(default=datetime.now, title='操作时间')
    #
    __icon__ = 'activity'
    __title__ = '操作'
    __columns__ = ['user', 'title', 'content', 'time']


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
        back_field_format=Format.GRID, back_field_icon='briefcase', back_field_title='参与项目',
    )
    activities: List[DemoActivity] = Field(required=False, format_=Format.TIMELINE, icon='activity', title='操作')  # 按照时间倒序
    # 其他
    update_time: datetime = Field(required=False, title='最近更新时间')
    create_time: datetime = Field(default=datetime.now, icon='clock', title='创建时间')
    #
    __icon__ = 'briefcase'
    __title__ = '项目'
    __columns__ = ['title', 'status', 'value', 'start', 'members', 'percent', 'create_time']
    __groups__ = [
        '''
        title
        description
        status, value
        start, end
        percent,
        ''',
    ]
    __read__ = '''
    ($,members)#4, (tasks,activities)#8
    '''
    __form__ = '''
    0
    members#4,
    '''


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
        icon='briefcase', title='所属项目',
        back_field_name='tasks', back_field_is_list=True, back_field_order=[('create_time', -1)],
        back_field_format=Format.TABLE, back_field_icon='check-square', back_field_title='任务列表',
    )
    user: DemoUser = Relation(
        format_=Format.SELECT, icon='user', title='负责人',
        back_field_name='tasks', back_field_is_list=True, back_field_order=[('create_time', -1)],
        back_field_format=Format.TABLE, back_field_icon='check-square', back_field_title='任务列表',
    )
    #
    update_time: datetime = Field(required=False, title='最近更新时间')
    create_time: datetime = Field(default=datetime.now, title='创建时间')
    #
    __icon__ = 'check-square'
    __title__ = '任务'
    __columns__ = ['title', 'status', 'user', 'start', 'create_time']
    __read__ = '''
    title
    status
    content
    start, end
    user
    create_time
    '''
    __form__ = '''
    title
    status
    content
    start, end
    user
    '''


@register
class DemoProjectDashboard(CacheModel):
    """ 仪表盘数据. """
    # Metricx4
    active_projects_count: int = Field(default=0, format_=Format.METRIC, icon='briefcase', title='活跃项目数量')
    active_projects_value: float = Field(default=0., format_=Format.METRIC, icon='dollar-sign', title='活跃项目价值', unit='元')
    members_count: int = Field(default=0, format_=Format.METRIC, icon='users', title='团队成员数量')
    tasks_count: int = Field(default=0, format_=Format.METRIC, icon='check-square', title='任务数量')
    # Table&Media
    active_projects: List[DemoProject] = Relation(format_=Format.TABLE, icon='briefcase', title='活跃项目')
    recent_activities: List[DemoActivity] = Field(format_=Format.TIMELINE, icon='activity', title='最近操作')  # 按照时间倒序

    __read__ = '''
    active_projects_count, active_projects_value, members_count, tasks_count
    active_projects#8, recent_activities#4
    '''


class DemoEnum(SimpleEnum):
    """ 状态. """
    FOO = 'foo', 'Foo'
    BAR = 'bar', 'Bar'


class DemoType(BaseModel):
    """ 类型演示. """
    str_field: str
    bool_field: bool
    int_field: int
    float_field: float
    datetime_field: datetime
    object_id_field: ObjectId
    enum_field: DemoEnum


class DemoList(BaseModel):
    """ 列表演示. """
    str_fields: List[str]
    bool_fields: List[bool]
    int_fields: List[int]
    float_fields: List[float]
    datetime_fields: List[datetime]
    object_id_fields: List[ObjectId]
    enum_fields: List[DemoEnum]


class DemoPersonGender(SimpleEnum):
    """ 性别. """
    MALE = 'male', '男'
    FEMALE = 'female', '女'


@register
class DemoPerson(CacheModel):
    """ 通过对个人数据的演示, 测试标题/注释/单位等常用有意义字段. """
    name: str = Field(searchable=Comparator.LIKE, title='名字', description='姓甚名谁?')
    gender: DemoPersonGender = Field(searchable=Comparator.EQ, title='性别')
    birthday: datetime = Field(required=False, format_=Format.DATE, title='生日')
    age: int = Field(required=False, searchable=Comparator.GTE, title='年龄', description='贵庚?', unit='岁')
    height: float = Field(required=False, title='身高', unit='cm')
    weight: float = Field(required=False, title='体重', unit='kg')
    avatar: str = Field(title='头像', format_=Format.AVATAR)
    remarks: str = Field(required=False, format_=Format.TEXTAREA, title='备注', description='个人简介')
    has_insurance: bool = Field(required=False, format_=Format.SWITCH, title='是否缴纳社保')
    #
    update_time: datetime = Field(required=False, title='最近更新时间')
    create_time: datetime = Field(default=datetime.now, title='创建时间')

    __columns__ = ['avatar', 'gender', 'birthday', 'age', 'height', 'weight', 'create_time']
    __layout__ = '''
    name, gender
    birthday, age
    height, weight
    avatar
    remarks
    '''
