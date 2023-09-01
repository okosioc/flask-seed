# -*- coding: utf-8 -*-
"""
    __init__.py
    ~~~~~~~~~~~~~~

    Models pagekcage definition.

    :copyright: (c) 2016 by fengweimin.
    :date: 16/6/11
"""
from .common import Series, Action, Block
from .demo import DemoUserStatus, DemoUserRole, DemoUserType, DemoUser, DemoTeam, DemoTeamStatus, \
    DemoProjectStatus, DemoTaskStatus, DemoTask, DemoActivity, DemoProject, DemoProjectDashboard, \
    DemoAttributeOption, DemoAttribute, DemoCategory, DemoProductAttribute, DemoProduct, DemoSku
# You need to implement your user models, because above DemoXXX models are CacheModel, which is not suitable for real project
# Please use your own user models below
from .demo import DemoUserStatus as UserStatus, DemoUserRole as UserRole, DemoUserType as UserType, DemoUser as User
