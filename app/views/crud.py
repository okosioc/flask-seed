# -*- coding: utf-8 -*-
"""
    crud
    ~~~~~~~~~~~~~~

    CRUD.

    :copyright: (c) 2016 by fengweimin.
    :date: 16/7/24
"""

import json

from bson.objectid import ObjectId
from flask import Blueprint, render_template, abort, current_app, request, jsonify, make_response
from pymongo.errors import DuplicateKeyError

from app.core import populate_model, SeedConnectionError, SeedDataError, populate_search
from app.extensions import mdb
from app.tools import editor_permission

crud = Blueprint('crud', __name__)

PAGE_COUNT = 30
MAX_PAGE = 20


@crud.route('/')
@editor_permission
def index():
    """ Index page. """
    registered_models = mdb.registered_models
    models = []
    for m in registered_models:
        models.append({
            'name': m.__name__.lower(),
            'jschema': m.to_json_schema()
        })
    return render_template('crud/index.html', models=models)


@crud.route('/query/<string:model_name>')
@editor_permission
def query(model_name):
    """ Query. """
    registered_models = mdb.registered_models
    model = next((m for m in registered_models if m.__name__.lower() == model_name.lower()), None)
    if not model:
        abort(404)
    #
    page = request.args.get('p', 1, lambda x: int(x) if x.isdigit() else 1)
    search, condition = populate_search(request.args, model)
    sort = None
    records, pagination = model.search(condition, page, sort=sort)
    return render_template('crud/query.html',
                           model={
                               'name': model_name.lower(),
                               'jschema': model.to_json_schema()
                           },
                           search=search, records=records, pagination=pagination)


@crud.route('/form/<string:model_name>/')
@crud.route('/form/<string:model_name>/<ObjectId:record_id>')
@editor_permission
def form(model_name, record_id=None):
    """ Form page which is used to new/change a record. """
    registered_models = mdb.registered_models
    model = next((m for m in registered_models if m.__name__.lower() == model_name.lower()), None)
    if record_id:
        record = model.find_one(record_id)
        if not record:
            abort(404)
    else:
        record = model()
    #
    return render_template('crud/form.html',
                           model={
                               'name': model_name.lower(),
                               'jschema': model.to_json_schema()
                           },
                           record=record)


@crud.route('/raw/<string:model_name>/')
@crud.route('/raw/<string:model_name>/<ObjectId:record_id>')
@editor_permission
def raw(model_name, record_id=None):
    """ Form page which is used to new/change a record. """
    registered_models = mdb.registered_models
    model = next((m for m in registered_models if m.__name__.lower() == model_name.lower()), None)
    if record_id:
        record = model.find_one(record_id)
        if not record:
            abort(404)
    else:
        record = model()
    #
    return render_template('crud/raw.html',
                           model={
                               'name': model_name.lower(),
                               'jschema': model.to_json_schema()
                           },
                           record=record)


@crud.route('/save/<string:model_name>/', methods=('POST',))
@crud.route('/save/<string:model_name>/<ObjectId:record_id>', methods=('POST',))
@editor_permission
def save(model_name, record_id=None):
    """ Create a new record or save an existing record. """
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
    #
    return jsonify(success=True, message='Save successfully. (%s)' % record._id, rid=record._id)


@crud.route('/delete/<string:model_name>/<ObjectId:record_id>', methods=('GET', 'POST'))
@editor_permission
def delete(model_name, record_id):
    """ Delete record. """
    registered_models = mdb.registered_models
    model = next((m for m in registered_models if m.__name__.lower() == model_name.lower()), None)
    record = model.find_one({'_id': record_id})
    if not record:
        abort(404)
    #
    record.delete()
    return jsonify(success=True, message='Delete successfully. (%s)' % record_id)


@crud.route('/json/<string:model_name>/<ObjectId:record_id>')
@editor_permission
def to_json(model_name, record_id):
    """ Output a json string for specified record. """
    registered_models = mdb.registered_models
    model = next((m for m in registered_models if m.__name__.lower() == model_name.lower()), None)
    record = model.find_one({'_id': record_id})
    if not record:
        abort(404)
    #
    r = make_response(record.to_json(indent=2))
    r.mimetype = 'application/json'
    return r


@crud.route('/schemas')
@editor_permission
def schemas():
    """ Output json schemas for all models. """
    registered_models = mdb.registered_models
    ret = [{'name': m.__name__.lower(), 'jschema': m.to_json_schema()} for m in registered_models]
    r = make_response(json.dumps(ret, indent=2))
    r.mimetype = 'application/json'
    return r


@crud.route('/schema/<string:model_name>')
@editor_permission
def schema(model_name):
    """ Output a json schema string for specified model. """
    registered_models = mdb.registered_models
    model = next((m for m in registered_models if m.__name__.lower() == model_name.lower()), None)
    r = make_response(json.dumps(model.to_json_schema(), indent=2))
    r.mimetype = 'application/json'
    return r
