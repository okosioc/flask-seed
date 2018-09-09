# -*- coding: utf-8 -*-
"""
    flask_mongosupport.py
    ~~~~~~~~~~~~~~

    flask_mongosupport simplifies to use mongosupport

    :copyright: (c) 2016 by fengweimin.
    :date: 16/6/6
"""

import re
from datetime import datetime
from math import ceil

from .mongosupport import connect, get_db, DATETIME_FORMATS, IN, DotDictProxy, DotListProxy

# Find the stack on which we want to store the database connection.
# Starting with Flask 0.9, the _app_ctx_stack is the correct one,
# before that we need to use the _request_ctx_stack.
try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack


class MongoSupport(object):
    """
    This class is used to integrate `MongoSupport`_ into a Flask application.

    :param app: The Flask application will be bound to this MongoSupport instance.
                If an app is not provided at initialization time than it
                must be provided later by calling :meth:`init_app` manually.
    """

    def __init__(self, app=None):
        self.registered_models = []
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """
        This method connect your ``app`` with this extension. Flask-MongoSupport will now take care about to
        open and close the connection to your MongoDB.

        Currently, the connection is shared within the whole application, so no need to handle closing.
        """

        # Use the newstyle teardown_appcontext if it's available, otherwise fall back to the request context
        if hasattr(app, 'teardown_appcontext'):
            app.teardown_appcontext(self.teardown)
        else:
            app.teardown_request(self.teardown)

        # Connect
        conn_settings = {'db': app.config.get('MONGODB_DATABASE', 'flask'),
                         'host': app.config.get('MONGODB_HOST', '127.0.0.1'),
                         'port': app.config.get('MONGODB_PORT', 27017),
                         'username': app.config.get('MONGODB_USERNAME', None),
                         'password': app.config.get('MONGODB_PASSWORD', None)}

        connect(conn_settings.pop('db'), **conn_settings)

        # Register extension with app only to say "I'm here"
        app.extensions = getattr(app, 'extensions', {})
        app.extensions['mongosupport'] = self

        # Register filters
        @app.context_processor
        def utility_processor():
            def ms_is_simple(struct):
                return type(struct) is type

            def ms_is_list(struct):
                return isinstance(struct, list)

            def ms_is_dict(struct):
                return isinstance(struct, dict)

            def ms_is_operator_in(struct):
                return isinstance(struct, IN)

            def ms_get_type(struct):
                if type(struct) is type:
                    return struct.__name__
                else:
                    return struct.__class__.__name__

            def ms_create_empty_dict_or_list(struct):
                if isinstance(struct, dict):
                    return DotDictProxy({}, struct)
                if isinstance(struct, list):
                    return DotListProxy([], struct)
                return None

            return dict(ms_is_simple=ms_is_simple,
                        ms_is_list=ms_is_list,
                        ms_is_dict=ms_is_dict,
                        ms_is_operator_in=ms_is_operator_in,
                        ms_get_type=ms_get_type,
                        ms_create_empty_dict_or_list=ms_create_empty_dict_or_list)

        self.app = app

    def teardown(self, exception):
        pass

    def register(self, models):
        """
        Register model to flask admin, Can be also used as a decorator on documents:

        .. code-block:: python

            ms = MongoSupport(app)

            @ms.register
            class Task(Model):
                structure = {
                   'title': unicode,
                   'text': unicode,
                   'creation': datetime,
                }

        :param models: A :class:`list` of :class:`mongosupport.Model`.
        """

        # enable decorator usage
        decorator = None
        if not isinstance(models, (list, tuple, set, frozenset)):
            # we assume that the user used this as a decorator
            # using @register syntax or using db.register(SomeDoc)
            # we stock the class object in order to return it later
            decorator = models
            models = [models]

        for model in models:
            if model not in self.registered_models:
                self.registered_models.append(model)

        if decorator is None:
            return self.registered_models
        else:
            return decorator

    @property
    def db(self):
        """
        Return pymongo.database.Database
        """
        return get_db()

    def __getitem__(self, name):
        """
        Return pymongo.collection.Collection
        """
        return self.db[name]


# ----------------------------------------------------------------------------------------------------------------------
# Pagination
#

class Pagination(object):
    """
    Pagination support.
    """

    def __init__(self, page, per_page, total_count):
        self.page = page
        self.per_page = per_page
        self.total_count = total_count

    @property
    def pages(self):
        return int(ceil(self.total_count / float(self.per_page)))

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    def iter_pages(self, left_edge=2, left_current=2, right_current=3, right_edge=2):
        last = 0
        for num in range(1, self.pages + 1):
            if num <= left_edge or \
                    (num > self.page - left_current - 1 and \
                                 num < self.page + right_current) or \
                            num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num


# ----------------------------------------------------------------------------------------------------------------------
# Html request processing
#

def _multidict_decode(md, dict_char='.', list_char='-'):
    """
    Decode a werkzeug.datastructures.MultiDict into a nested dict.

    http://werkzeug.pocoo.org/docs/0.11/datastructures/#werkzeug.datastructures.MultiDict
    """
    result = {}
    dicts_to_sort = set()
    for key, value in md.items():
        # Split keys into tokens by dict_char and list_char
        keys = _normalized_path(key).split(dict_char)
        new_keys = []
        for k in keys:
            if list_char in k:
                list_tokens = k.split(list_char)
                # For list tokens, the 1st one should always be field name, the latter ones are indexes
                for i in range(len(list_tokens)):
                    if list_tokens[i].isdigit():
                        new_keys.append(int(list_tokens[i]))
                    else:
                        new_keys.append(list_tokens[i])
                    if i < len(list_tokens) - 1:
                        dicts_to_sort.add(tuple(new_keys))
            else:
                new_keys.append(k)

        # Create inner dicts, lists are also initialized as dicts
        place = result
        for i in range(len(new_keys) - 1):
            try:
                if not isinstance(place[new_keys[i]], dict):
                    place[new_keys[i]] = {None: place[new_keys[i]]}
                place = place[new_keys[i]]
            except KeyError:
                place[new_keys[i]] = {}
                place = place[new_keys[i]]

        # Fill the contents
        if new_keys[-1] in place:
            if isinstance(place[new_keys[-1]], dict):
                place[new_keys[-1]][None] = value
            elif isinstance(place[new_keys[-1]], list):
                if isinstance(value, list):
                    place[new_keys[-1]].extend(value)
                else:
                    place[new_keys[-1]].append(value)
            else:
                if isinstance(value, list):
                    place[new_keys[-1]] = [place[new_keys[-1]]]
                    place[new_keys[-1]].extend(value)
                else:
                    place[new_keys[-1]] = [place[new_keys[-1]], value]
        else:
            place[new_keys[-1]] = value

    # Convert sorted dict to list
    to_sort_list = sorted(dicts_to_sort, key=len, reverse=True)
    for key in to_sort_list:
        to_sort = result
        source = None
        last_key = None
        for sub_key in key:
            source = to_sort
            last_key = sub_key
            to_sort = to_sort[sub_key]
        if None in to_sort:
            none_values = [(0, x) for x in to_sort.pop(None)]
            none_values.extend(iter(to_sort.items()))
            to_sort = none_values
        else:
            to_sort = iter(to_sort.items())

        to_sort = [x[1] for x in sorted(to_sort, key=_sort_key)]
        source[last_key] = to_sort

    return result


def _sort_key(item):
    """
    Robust sort key that sorts items with invalid keys last.
    This is used to make sorting behave the same across Python 2 and 3.
    """
    key = item[0]
    return not isinstance(key, int), key


def populate_model(multidict, model_cls, set_default=True):
    """
    Create a model instance from a multidict of request.form or request.args

    http://flask.pocoo.org/docs/0.11/api/#incoming-request-data
    """
    d = {}
    valid_paths = model_cls._valid_paths
    model_prefix = model_cls.__name__.lower() + '.'
    for key, value in multidict.items():
        # NOTE: Blank string skipped
        if not value:
            continue
        # Only process the keys with leading model.
        if key.startswith(model_prefix):
            key = key[len(model_prefix):]
        else:
            continue
        # Normalized the path
        path = _normalized_path(key)
        # Convert the path to mongosupport's dot notation
        path = re.sub('\-[0-9]+', '.$', path)
        if path in valid_paths:
            t = valid_paths[path]
            # print "try to convert %s with value %s to type %s" % (path, value, t)
            try:
                if isinstance(value, list):  # Value should be instance of list
                    t = valid_paths[path + '.$']
                    converted_value = [convert_from_string(v, t) for v in value if v]
                else:
                    converted_value = convert_from_string(value, t)
            except ValueError as e:
                raise ValueError("%s: can not convert %s to %s" % (key, value, t))
        else:
            raise KeyError("%s is not a valid path" % key)
        d[key] = converted_value

    d = _multidict_decode(d)
    return model_cls(d, set_default)


def _normalized_path(path, list_char='-'):
    # Change [] -> - for easier processing
    return path.replace('[', list_char).replace(']', '')


class DefaultTypeConverter(object):
    """
    用于将表单的字符串转化为对应类型的值.
    """

    def _convert_from_string(self, string_value, type):
        try:
            return type(string_value)
        except ValueError:
            raise ValueError("can not convert %s to %s" % (string_value, type.__name__))


class BoolConverter(DefaultTypeConverter):
    """
    unicode -> bool
    """

    def _convert_from_string(self, string_value, type):
        return string_value.strip().lower() in ("yes", "true")


class DatetimeConverter(DefaultTypeConverter):
    """
    unicode -> datetime
    """

    def _convert_from_string(self, string_value, type):
        for fmt in DATETIME_FORMATS:
            try:
                return datetime.strptime(string_value, fmt)
            except ValueError:
                pass
        raise ValueError("can not convert %s to %s" % (string_value, type.__name__))


type_converters = {
    bool: BoolConverter(),
    datetime: DatetimeConverter(),
    None: DefaultTypeConverter(),  # Default converter
}


def convert_from_string(string_value, t):
    if isinstance(string_value, t):
        return string_value

    if t in type_converters:
        converter = type_converters[t]
    else:
        converter = type_converters[None]
    return converter._convert_from_string(string_value, t)
