# -*- coding: utf-8 -*-
"""
    permissions.py
    ~~~~~~~~~~~~~~

    Permissions definition.

    :copyright: (c) 2016 by fengweimin.
    :date: 16/5/9
"""

from flask_principal import RoleNeed, Permission

auth_permission = Permission(RoleNeed('authenticated'))
admin_permission = Permission(RoleNeed('admin'))

# this is assigned when you want to block a permission to all
# never assign this role to anyone !
null = Permission(RoleNeed('null'))
