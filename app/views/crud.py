# -*- coding: utf-8 -*-
"""
    crud
    ~~~~~~~~~~~~~~

    CRUD.

    :copyright: (c) 2016 by fengweimin.
    :date: 16/7/24
"""

from bson.objectid import ObjectId
from flask import Blueprint, render_template, abort, current_app, request, jsonify, make_response
from pymongo.errors import DuplicateKeyError

from app.core import populate_model, SeedConnectionError, SeedDataError
from app.extensions import mdb
from app.tools import admin_permission

crud = Blueprint('crud', __name__)

PAGE_COUNT = 30


@crud.route('/')
@admin_permission
def index():
    """ Index page. """
    registered_models = mdb.registered_models
    return render_template('crud/index.html', models={m.__name__.lower(): m for m in registered_models})


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
