# -*- coding: utf-8 -*-
"""
    crud
    ~~~~~~~~~~~~~~

    CRUD.

    :copyright: (c) 2016 by fengweimin.
    :date: 16/7/24
"""
import re

from bson.objectid import ObjectId
from flask import Blueprint, render_template, abort, current_app, request, jsonify, make_response
from pymongo.errors import DuplicateKeyError

from app.core import populate_model, SeedConnectionError, SeedDataError, Pagination, convert_from_string, Comparator
from app.extensions import mdb, qiniu
from app.tools import auth_permission

crud = Blueprint('crud', __name__)

PAGE_COUNT = 30
MAX_PAGE = 20


@crud.route('/')
@auth_permission
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
@auth_permission
def query(model_name):
    """ Query. """
    registered_models = mdb.registered_models
    model = next((m for m in registered_models if m.__name__.lower() == model_name.lower()), None)
    if not model:
        abort(404)

    page = _parse_page()
    search, condition = _parse_search(model)
    sort = None
    records, pagination = _get_records_and_pagination(model, page, condition, sort)
    return render_template('crud/query.html',
                           model={
                               'name': model_name.lower(),
                               'jschema': model.to_json_schema()
                           },
                           search=search, records=records, pagination=pagination)


def _parse_page():
    """ Make sure page param is valid. """
    p = request.args.get('p', '1')
    if p.isdigit():
        return int(p)
    else:
        return 1


def _parse_search(model):
    """ Parse search param. """
    search, condition = {}, {}
    # Used to get type from a path
    valid_paths = model._valid_paths
    for k, v in request.args.items():
        if not k.startswith('search.') or not v:
            continue
        # Remove search. from k
        k = k.replace('search.', '')
        search[k] = v
        # Parse Comparator
        if '__' in k:
            k, c = k.split('__')
            t = valid_paths[k]
            if Comparator.LIKE == c:
                # In order to use index, we only support starting string search here
                # https://docs.mongodb.com/manual/reference/operator/query/regex/#index-use
                regx = re.compile('^%s' % re.escape(v))
                condition[k] = {'$regex': regx}
            else:
                condition[k] = {'$%s' % c: convert_from_string(v, t)}
        else:
            t = valid_paths[k]
            condition[k] = convert_from_string(v, t)
    #
    return search, condition if condition else None


def _get_records_and_pagination(model, page, search, sort):
    """ Query records and generate pagination. """
    count = model.count(search)
    limit = PAGE_COUNT * MAX_PAGE
    if count > limit:
        count = limit
    start = (page - 1) * PAGE_COUNT
    records = list(model.find(search, skip=start, limit=PAGE_COUNT, sort=sort))
    pagination = Pagination(page, PAGE_COUNT, count)
    return records, pagination


@crud.route('/form/<string:model_name>/')
@crud.route('/form/<string:model_name>/<ObjectId:record_id>')
@auth_permission
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
    return render_template('crud/form.html',
                           model={
                               'name': model_name.lower(),
                               'jschema': model.to_json_schema()
                           },
                           record=record,
                           token=qiniu.image_token())


@crud.route('/raw/<string:model_name>/')
@crud.route('/raw/<string:model_name>/<ObjectId:record_id>')
@auth_permission
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
    return render_template('crud/raw.html',
                           model={
                               'name': model_name.lower(),
                               'jschema': model.to_json_schema()
                           },
                           record=record)


@crud.route('/json/<string:model_name>/<ObjectId:record_id>')
@auth_permission
def json(model_name, record_id):
    """ Output a json string for specified record. """
    registered_models = mdb.registered_models
    model = next((m for m in registered_models if m.__name__.lower() == model_name.lower()), None)

    record = model.find_one({'_id': record_id})
    if not record:
        abort(404)

    r = make_response(record.to_json(indent=2))
    r.mimetype = 'application/json'
    return r


@crud.route('/save/<string:model_name>/', methods=('POST',))
@crud.route('/save/<string:model_name>/<ObjectId:record_id>', methods=('POST',))
@auth_permission
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

    return jsonify(success=True, message='Save successfully. (%s)' % record._id, rid=record._id)


@crud.route('/delete/<string:model_name>/<ObjectId:record_id>', methods=('GET', 'POST'))
@auth_permission
def delete(model_name, record_id):
    """ Delete record. """
    registered_models = mdb.registered_models
    model = next((m for m in registered_models if m.__name__.lower() == model_name.lower()), None)

    record = model.find_one({'_id': record_id})
    if not record:
        abort(404)
    record.delete()

    return jsonify(success=True, message='Delete successfully. (%s)' % record_id)
