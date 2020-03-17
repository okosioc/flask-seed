# -*- coding: utf-8 -*-
"""
    crud
    ~~~~~~~~~~~~~~

    CRUD.

    :copyright: (c) 2016 by fengweimin.
    :date: 16/7/24
"""

from collections import OrderedDict

from bson.objectid import ObjectId
from flask import Blueprint, render_template, abort, current_app, request, jsonify, make_response
from pymongo.errors import DuplicateKeyError

from app.core import Pagination, populate_model, SeedConnectionError, SeedDataError, convert_from_string
from app.extensions import mdb
from app.tools import admin_permission

crud = Blueprint('crud', __name__)

PAGE_COUNT = 30


@crud.route('/index')
@crud.route('/index/<string:model_name>')
@admin_permission
def index(model_name=None):
    """
    Index page.
    """
    registered_models = mdb.registered_models
    if model_name:
        model = next((m for m in registered_models if m.__name__.lower() == model_name.lower()), None)
    elif registered_models:
        model = registered_models[0]
    if not model:
        abort(404)

    model_name = model.__name__.lower()
    # 获取指定model的索引
    index_dict = OrderedDict({'_id': ObjectId})
    for i in model.indexes:
        value = i['fields']
        if isinstance(value, str):
            index_dict[value] = model._valid_paths[value]
        elif isinstance(value, list):
            for val in value:
                if isinstance(val, tuple):
                    field, direction = val
                    index_dict[field] = model._valid_paths[field]
                else:
                    index_dict[val] = model._valid_paths[val]

    # 查询条件
    ''' 20161123/Samuel/暂时不使用populate_model来生成查询条件
    # 调用populate_model将查询条件转化为数据对象, 会自动转换查询条件的数据类型
    search_record = populate_model(request.args, model, False)
    # 将数据对象中非空的值提取出来, 构造成一个mongoDB查询的条件
    condition = {f: v for f, v in search_record.iteritems() if v}
    '''
    condition = {}
    for k, t in index_dict.items():
        v = request.args.get(k, None)
        if v:
            cv = convert_from_string(v, t)
            condition[k.replace('.$', '')] = cv

    # 翻页支持
    page = int(request.args.get('_p', 1))
    count = model.count(condition)
    start = (page - 1) * PAGE_COUNT

    # 返回结果只显示索引中的字段
    projection = {k.replace('.$', ''): True for k in index_dict}

    current_app.logger.debug(
        'There are %s %ss for condition %s, with projection %s' % (count, model_name, condition, projection))

    # TODO: 排序
    records = model.find(condition, projection, start, PAGE_COUNT)
    pagination = Pagination(page, PAGE_COUNT, count)

    # current_app.logger.debug('Indexed fields for %s are %s' % (model_name, index_dict))
    return render_template('/crud/index.html',
                           models=registered_models,
                           model=model,
                           index_dict=index_dict,
                           records=records,
                           pagination=pagination)


@crud.route('/new/<string:model_name>')
@crud.route('/change/<string:model_name>/<ObjectId:record_id>', endpoint='change_model')
@admin_permission
def form(model_name, record_id=None):
    """
    Form page which is used to new/change a record.
    """
    registered_models = mdb.registered_models
    model = next((m for m in registered_models if m.__name__.lower() == model_name.lower()), None)

    if record_id:
        record = model.find_one({'_id': record_id})
        if not record:
            abort(404)
    else:
        record = model()

    return render_template('/crud/form.html',
                           model=model,
                           record=record)


@crud.route('/json/<string:model_name>/<ObjectId:record_id>')
@admin_permission
def json(model_name, record_id):
    """
    Output a json string for specified record.
    """
    registered_models = mdb.registered_models
    model = next((m for m in registered_models if m.__name__.lower() == model_name.lower()), None)

    record = model.find_one({'_id': record_id})
    if not record:
        abort(404)

    r = make_response(record.to_json(indent=2))
    r.mimetype = 'application/json'
    return r


@crud.route('/create/<string:model_name>', methods=('POST',))
@crud.route('/save/<string:model_name>/<ObjectId:record_id>', methods=('POST',))
@admin_permission
def save(model_name, record_id=None):
    """
    Create a new record or save an existing record.
    """
    registered_models = mdb.registered_models
    model = next((m for m in registered_models if m.__name__.lower() == model_name.lower()), None)

    try:
        record = populate_model(request.form, model, False)
        if record_id:
            record._id = record_id
            record.save()
        else:
            record._id = ObjectId()
            record.save(True)
    except (SeedConnectionError, SeedDataError, DuplicateKeyError) as err:
        return jsonify(success=False, message='Save failed! (%s)' % err.message)
    except:
        current_app.logger.exception('Failed when saving %s' % model_name)
        return jsonify(success=False, message='Save failed!')

    return jsonify(success=True, message='Save successfully. (%s)' % record._id, rid=record._id)


@crud.route('/delete/<string:model_name>/<ObjectId:record_id>', methods=('GET', 'POST'))
@admin_permission
def delete(model_name, record_id):
    """
    Delete record.
    """
    registered_models = mdb.registered_models
    model = next((m for m in registered_models if m.__name__.lower() == model_name.lower()), None)

    record = model.find_one({'_id': record_id})
    if not record:
        abort(404)
    record.delete()

    return jsonify(success=True, message='Delete successfully. (%s)' % record_id)
