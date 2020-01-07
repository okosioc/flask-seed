# -*- coding: utf-8 -*-
"""
    schema.py
    ~~~~~~~~~~~~~~

    Meta class with very simple schema.

    :copyright: (c) 2019 by fengweimin.
    :date: 2019/8/8
"""

import json
import re
from collections import MutableSequence, MutableMapping
from copy import deepcopy
from datetime import datetime

from bson import ObjectId


# ----------------------------------------------------------------------------------------------------------------------
# Schema Operator
#

class SchemaOperator(object):
    """ Customized operators which can be used to define a schema. """

    repr = None

    def __init__(self, *args):
        assert self.repr is not None
        self.operands = []
        for arg in args:
            if isinstance(arg, (list, tuple)):
                self.operands = self.operands + arg
            else:
                self.operands.append(arg)

    def __repr__(self):
        return str(self)

    def __iter__(self):
        for operand in self.operands:
            yield operand

    def __len__(self):
        return len(self.operands)

    def __eq__(self, other):
        return type(self) == type(other) and self.operands == other.operands

    def validate(self, value):
        raise NotImplementedError


class IN(SchemaOperator):
    """ Defined available values of a field. """
    repr = 'in'

    def __init__(self, *args):
        super(IN, self).__init__(*args)

    def __str__(self):
        return '<%s ' % self.repr + ', '.join([repr(i) for i in self.operands]) + '>'

    def validate(self, value):
        if value in self.operands:
            for op in self.operands:
                if value == op and isinstance(value, type(op)):
                    return True
        return False


# ----------------------------------------------------------------------------------------------------------------------
# Constants
#

# Date format
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'

# Supported types for modal fields
AUTHORIZED_TYPES = [
    bool,
    int,
    float,
    str,
    datetime,
    ObjectId,  # https://api.mongodb.com/python/current/api/bson/son.html
]


# ----------------------------------------------------------------------------------------------------------------------
# Conversions
#

class SchemaJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        elif isinstance(o, datetime):
            return o.strftime(DATETIME_FORMAT)
        elif isinstance(o, (DotDictProxy, DotListProxy)):
            return o.raw

        return json.JSONEncoder.default(self, o)


# ----------------------------------------------------------------------------------------------------------------------
# Exceptions
#

class SeedSchemaError(Exception):
    """ Schema error. """
    pass


class SeedDataError(Exception):
    """ Data error. """
    pass


# ----------------------------------------------------------------------------------------------------------------------
# Metaclass
#

class SchemaMetaclass(type):
    """ Meta class with a simple built-in schema. """

    def __new__(mcs, name, bases, attrs):
        # Abstract classes such as SchemaDict or Model do not define schema
        if 'schema' not in attrs or attrs['schema'] is None:
            return type.__new__(mcs, name, bases, attrs)

        # Protected field names, when dot-mode enabled, can NOT use these names as schema's field names
        attrs['_protected_field_names'] = {'_protected_field_names', '_valid_paths', 'validation_errors'}
        for mro in bases[0].__mro__:
            attrs['_protected_field_names'] = attrs['_protected_field_names'].union(set(mro.__dict__))
        attrs['_protected_field_names'] = list(attrs['_protected_field_names'])

        # ObjectId
        if '_id' not in attrs['schema']:
            attrs['schema']['_id'] = ObjectId

        # Valid paths
        attrs['_valid_paths'] = {}
        mcs._validate_schema(name, attrs)
        attrs['_valid_paths'] = {
            k.replace(name + '.', ''): v for k, v in attrs['_valid_paths'].items() if not k == name
        }

        # Validate schema descriptors, e.g, default_values/required_fields/validators
        mcs._validate_descriptors(name, attrs)

        return type.__new__(mcs, name, bases, attrs)

    @classmethod
    def _validate_schema(mcs, name, attrs):
        """ Validate schema. """
        schema = attrs['schema']
        protected = attrs['_protected_field_names']

        def __validate_schema(_schema, _name):
            # type
            if type(_schema) is type:
                attrs['_valid_paths'][_name] = _schema
                if _schema not in AUTHORIZED_TYPES:
                    raise SeedSchemaError('%s: %s is not an authorized type' % (_name, _schema))
            # {}
            elif isinstance(_schema, dict):
                attrs['_valid_paths'][_name] = {}
                if not len(_schema):
                    raise SeedSchemaError(
                        '%s: %s can not be a empty dict' % (_name, _schema))
                for key in _schema:
                    # Check key type
                    if isinstance(key, str):
                        if not re.match('^[a-zA-Z0-9_]+$', key):
                            raise SeedSchemaError('%s: %s can only contain letters, numbers or _' % (_name, key))
                        if key[0].isdigit():
                            raise SeedSchemaError('%s: %s must not start with digit' % (_name, key))
                        if attrs.get('use_dot_notation', True) and key in protected:
                            raise SeedSchemaError(
                                '%s: %s is a protected field name, please set use_dot_notation = False if you insist '
                                'to use this field name; protected fields are %s.' % (_name, key, sorted(protected)))
                    else:
                        raise SeedSchemaError('%s: %s must be a str' % (_name, key))

                    __validate_schema(_schema[key], '%s.%s' % (_name, key))
            # []
            elif isinstance(_schema, list):
                attrs['_valid_paths'][_name] = []
                if not len(_schema):
                    raise SeedSchemaError(
                        '%s: %s can not be a empty list' % (_name, _schema))
                if len(_schema) > 1:
                    raise SeedSchemaError(
                        '%s: %s must not have more then one type' % (_name, _schema))
                __validate_schema(_schema[0], _name)
            # SchemaOperator
            elif isinstance(_schema, SchemaOperator):
                if len(_schema) == 0:
                    raise SeedSchemaError('%s: %s can not be empty' % (_name, _schema))
                if isinstance(_schema, IN):
                    types = set()
                    for operand in _schema:
                        types.add(type(operand))
                        if type(operand) not in AUTHORIZED_TYPES:
                            raise SeedSchemaError('%s: %s in %s is not an authorized type (%s found)' % (
                                _name, operand, _schema, type(operand).__name__))
                    if len(types) > 1:
                        raise SeedSchemaError('%s: %s can not have more than one type' % (_name, _schema))
                    attrs['_valid_paths'][_name] = list(types)[0]
                else:
                    for operand in _schema:
                        if operand not in AUTHORIZED_TYPES:
                            raise SeedSchemaError('%s: %s in %s is not an authorized type (%s found)' % (
                                _name, operand, _schema, type(operand).__name__))
                    # Use tuple to represent many available types
                    attrs['_valid_paths'][_name] = tuple(_schema)
            else:
                raise SeedSchemaError(
                    '%s: %s is not a supported thing' % (_name, _schema))

        if schema is None:
            raise SeedSchemaError('%s.schema must not be None' % name)
        if not isinstance(schema, dict):
            raise SeedSchemaError('%s.schema must be a dict instance' % name)
        __validate_schema(schema, name)

    @classmethod
    def _validate_descriptors(mcs, name, attrs):
        """ Validate schema descriptors, e.g, default_values/required_fields/validators. """
        valid_paths = attrs['_valid_paths']

        # default_values
        for dv in attrs.get('default_values', {}):
            if dv not in valid_paths:
                raise SeedSchemaError('%s: Error in default_values: can\'t find %s in schema' % (name, dv))

        # required_fields
        for rf in attrs.get('required_fields', []):
            if rf not in valid_paths:
                raise SeedSchemaError('%s: Error in required_fields: can\'t find %s in schema' % (name, rf))
        if attrs.get('required_fields', []):
            if len(attrs['required_fields']) != len(set(attrs['required_fields'])):
                raise SeedSchemaError('%s: duplicate required_fields : %s' % (name, attrs['required_fields']))

        # validators
        for v in attrs.get('validators', {}):
            if v not in valid_paths:
                raise SeedSchemaError('%s: Error in validators: can\'t find %s in schema' % (name, v))


class SchemaDict(dict, metaclass=SchemaMetaclass):
    """ Schema dict = dict schema definition + dict content validation. """

    schema = None
    required_fields = []
    default_values = {}
    validators = {}
    raise_validation_errors = True
    use_dot_notation = True

    def __init__(self, doc=None, set_default=True):
        """Init.

        :param doc:
        :param set_default:
        """
        super(SchemaDict, self).__init__()

        self.validation_errors = {}

        if doc is not None:
            for k, v in doc.items():
                self[k] = v

        if set_default and self.default_values:
            self._set_default_values(self, self.schema)

    def __str__(self):
        return "%s(%s)" % (self.__class__.__name__, dict(self))

    def validate(self):
        """
        Validate the document, this method will verify if:
          1. the doc follow the schema,
          2. all required fields are filled
          3. this method will process all validators.
        """
        self._validate_doc(self, self.schema)

        if self.required_fields:
            self._validate_required(self)

        if self.validators:
            self._process_validators(self)

        return False if self.validation_errors else True

    def _validate_doc(self, doc, schema, path=''):
        """ Check if doc field types match the doc field schema. """
        if doc is None:
            return
        # type
        if type(schema) is type:
            if not isinstance(doc, schema):
                self._raise_exception(SeedDataError, path,
                                      '%s must be an instance of %s not %s' % (
                                          path, schema.__name__, type(doc).__name__))
        # {}
        elif isinstance(schema, dict):
            if not isinstance(doc, dict):
                self._raise_exception(SeedDataError, path,
                                      '%s must be an instance of dict not %s' % (
                                          path, type(doc).__name__))

            # For fields in doc but not in schema
            doc_schema_diff = list(set(doc).difference(set(schema)))
            bad_fields = [d for d in doc_schema_diff]
            if bad_fields:
                self._raise_exception(SeedDataError, None,
                                      'unknown fields %s in %s' % (bad_fields, type(doc).__name__))
            for key in schema:
                if key in doc:
                    self._validate_doc(doc[key], schema[key], ("%s.%s" % (path, key)).strip('.'))
        # []
        elif isinstance(schema, list):
            if not isinstance(doc, list):
                self._raise_exception(SeedDataError, path,
                                      '%s must be an instance of list not %s' % (path, type(doc).__name__))
            for obj in doc:
                self._validate_doc(obj, schema[0], path)
        # SchemaOperator
        elif isinstance(schema, SchemaOperator):
            if not schema.validate(doc):
                if isinstance(schema, IN):
                    self._raise_exception(SeedDataError, path,
                                          '%s must be in %s not %s' % (path, schema.operands, doc))
                else:
                    self._raise_exception(SeedDataError, path,
                                          '%s must be an instance of %s not %s' % (path, schema, type(doc).__name__))
        #
        else:
            self._raise_exception(SeedDataError, path,
                                  '%s must be an instance of %s not %s' % (
                                      path, schema.__name__, type(doc).__name__))

    def _validate_required(self, doc):
        """ Validate required fields. """
        for rf in self.required_fields:
            vals = self._get_values_by_path(doc, rf)
            if not vals:
                self._raise_exception(SeedDataError, rf, '%s is required' % rf)

    def _process_validators(self, doc):
        """ Invoke validators. """
        for key, validators in self.validators.items():
            vals = self._get_values_by_path(doc, key)
            if vals:
                if not hasattr(validators, '__iter__'):
                    validators = [validators]
                for val in vals:
                    for validator in validators:
                        try:
                            if not validator(val):
                                raise SeedDataError('%s does not pass the validator %s' % (key, validator.__name__))
                        except Exception as e:
                            self._raise_exception(SeedDataError, key, e.message)

    def _raise_exception(self, exception, field, message):
        """ Handle exceptions. """
        if self.raise_validation_errors:
            raise exception(message)
        else:
            if field not in self.validation_errors:
                self.validation_errors[field] = []
            self.validation_errors[field].append(exception(message))

    def _get_values_by_path(self, doc, path):
        """ Get values from a path. """
        vals = [doc]
        for key in path.split('.'):
            # print('getting values by path %s from %s' % (key, vals))
            new_vals = []
            for val in vals:
                if val is None or key not in val:
                    continue
                val = val[key]
                if val is None:
                    continue
                elif isinstance(val, list):
                    for v in val:
                        new_vals.append(v)
                else:
                    new_vals.append(val)
            vals = new_vals

        return vals

    def _set_default_values(self, doc, schema, path=""):
        """ Set default values. """
        for key in schema:
            new_path = ('%s.%s' % (path, key)).strip('.')
            # print("setting default value for %s with type %s" % (new_path, schema[key]))
            # type
            if type(schema[key]) is type:
                if new_path in self.default_values and key not in doc:
                    new_value = self.default_values[new_path]
                    if callable(new_value):
                        new_value = new_value()
                    doc[key] = new_value
            # {}
            if isinstance(schema[key], dict):
                # Set default value of the whole dict
                if new_path in self.default_values and key not in doc:
                    new_value = self.default_values[new_path]
                    if callable(new_value):
                        new_value = new_value()
                    elif isinstance(new_value, dict):
                        new_value = deepcopy(new_value)
                    doc[key] = new_value
                # Recursively
                if [i for i in self.default_values if i.startswith("%s." % new_path)]:
                    if key not in doc or doc[key] is None:
                        doc[key] = {}
                    self._set_default_values(doc[key], schema[key], new_path)
            # []
            if isinstance(schema[key], list):
                # Set default value of the whole list
                if new_path in self.default_values and key not in doc:
                    new_value = self.default_values[new_path]
                    if callable(new_value):
                        new_value = new_value()
                    elif isinstance(new_value, list):
                        new_value = new_value[:]
                    doc[key] = new_value
                # Recursively, Please note that the set default logic only occurs during object initialization
                if [i for i in self.default_values if i.startswith("%s." % new_path)]:
                    if key not in doc or doc[key] is None:
                        doc[key] = [{}]
                    self._set_default_values(doc[key][0], schema[key][0], new_path)
            # SchemaOperator
            if isinstance(schema[key], SchemaOperator):
                if new_path in self.default_values and key not in doc:
                    new_value = self.default_values[new_path]
                    doc[key] = new_value

    def __setattr__(self, key, value):
        """ Support dot notation. """
        if self.use_dot_notation and key not in self._protected_field_names and key in self.schema:
            # print('setting attr %s with %s' % (key, value))
            if isinstance(value, (DotDictProxy, DotListProxy)):
                self[key] = value._obj_
            else:
                self[key] = value
        else:
            dict.__setattr__(self, key, value)

    def __getattr__(self, key):
        """ Support dot notation. """
        if self.use_dot_notation and key not in self._protected_field_names and key in self.schema:
            s = self.schema[key]
            found = self.get(key, None)
            # print('getting attr %s for schema %s with value %s' % (key, s, type(found)))
            if found is None:
                if isinstance(s, dict):
                    found = {}
                elif isinstance(s, list):
                    found = []
                else:
                    found = None
                self[key] = found

            return proxywrapper(found, s)
        else:
            return dict.__getattribute__(self, key)

    def __delattr__(self, key):
        """ Support dot notation. """
        if self.use_dot_notation and key not in self._protected_field_names and key in self.schema:
            del self[key]
        else:
            dict.__delattr__(self, key)

    #   
    #
    # JSON serialization
    #
    #

    def to_json(self, **kwargs):
        """ Convert the model instance to a json string. """
        return json.dumps(self, cls=SchemaJSONEncoder, **kwargs)

    @classmethod
    def from_json(cls, doc, **kwargs):
        """ Convert a json string to a model instance, making use of the schema for decoding. """

        def json_decode(value, type):
            if value is None:
                return value

            if type is datetime:
                return datetime.strptime(value, DATETIME_FORMAT)
            elif type is ObjectId:
                return ObjectId(value)
            else:
                return type(value)

        def _convert_dict(doc, schema):
            """Recursively convert specified type."""
            for key in schema:
                s = schema[key]
                if key not in doc:
                    continue
                old_value = doc[key]
                if old_value is None:
                    continue

                if type(s) is type:
                    doc[key] = json_decode(old_value, s)
                # {}
                elif isinstance(s, dict):
                    _convert_dict(old_value, s)
                # []
                elif isinstance(s, list):
                    _convert_list(old_value, s)
                # IN
                elif isinstance(s, SchemaOperator):
                    doc[key] = json_decode(old_value, type(s.operands[0]))

        def _convert_list(doc, schema):
            s = schema[0]
            if doc is None:
                return

            for i, v in enumerate(doc):
                old_value = doc[i]
                if type(s) is type:
                    doc[i] = json_decode(old_value, s)
                # {}
                elif isinstance(s, dict):
                    _convert_dict(old_value, s)
                # []
                elif isinstance(s, list):
                    _convert_list(old_value, s)
                # IN
                elif isinstance(s, SchemaOperator):
                    doc[i] = json_decode(old_value, type(s.operands[0]))

        d = json.loads(doc)
        _convert_dict(d, cls.schema)
        return cls(d, False)

    def foobar(self):
        pass


# ----------------------------------------------------------------------------------------------------------------------
# Proxy - Support dot notation
#

class DotDictProxy(MutableMapping, object):
    """ A proxy for a dictionary that allows attribute access to underlying keys. """

    def __init__(self, obj, schema):
        self._obj_ = obj
        self._schema_ = schema

    def __getattr__(self, key):
        if key in ['_obj_', '_schema_'] or key not in self._schema_:
            return object.__getattribute__(self, key)

        s = self._schema_[key]
        found = self._obj_.get(key, None)
        # print "dict proxy getting attr %s for schema %s with value %s" % (key, type(s).__name__, found)
        if found is None:
            if isinstance(s, dict):
                found = {}
            elif isinstance(s, list):
                found = []
            else:
                found = None
            self._obj_[key] = found

        return proxywrapper(found, s)

    def __setattr__(self, key, value):
        if key in ['_obj_', '_schema_'] or key not in self._schema_:
            return object.__setattr__(self, key, value)
        # print "dict proxy setting attr %s with %s" % (key, value)
        if isinstance(value, (DotDictProxy, DotListProxy)):
            self._obj_[key] = value._obj_
        else:
            self._obj_[key] = value

    def __delitem__(self, key):
        del self._obj_[key]

    def __len__(self):
        return self._obj_.__len__()

    def __iter__(self):
        return self._obj_.__iter__()

    def __str__(self):
        return "DotDictProxy(%s)" % self._obj_.__str__()

    def __getitem__(self, key):
        return self._obj_[key]

    def __setitem__(self, key, value):
        self._obj_[key] = value

    def __eq__(self, other):
        if not isinstance(other, DotDictProxy):
            return NotImplemented
        return self._obj_ == other._obj_

    def __ne__(self, other):
        return not (self == other)

    @property
    def raw(self):
        return self._obj_


class DotListProxy(MutableSequence, object):
    """ A proxy for a list that allows for wrapping items. """

    def __init__(self, obj, schema):
        self._obj_ = obj
        self._schema_ = schema

    def __getitem__(self, index):
        # print "list proxy getting index %s for schema %s with value %s" % (index, self._schema_, self._obj_[index])
        if isinstance(index, slice):
            return proxywrapper(self._obj_[index], self._schema_)
        else:
            return proxywrapper(self._obj_[index], self._schema_[0])

    def __setitem__(self, index, value):
        if isinstance(value, (DotDictProxy, DotListProxy)):
            self._obj_[index] = value._obj_
        else:
            self._obj_[index] = value

    def __delitem__(self, index):
        del self._obj_[index]

    def __reversed__(self):
        return self._obj_.__reversed__()

    def __len__(self):
        return self._obj_.__len__()

    def __str__(self):
        return "DotListProxy(%s)" % self._obj_.__str__()

    def __eq__(self, other):
        if not isinstance(other, DotListProxy):
            return NotImplemented
        return self._obj_ == other._obj_

    def __ne__(self, other):
        return not (self == other)

    def insert(self, index, value):
        if isinstance(value, (DotDictProxy, DotListProxy)):
            self._obj_.insert(index, value._obj_)
        else:
            self._obj_.insert(index, value)

    def append(self, value):
        if isinstance(value, (DotDictProxy, DotListProxy)):
            self._obj_.append(value._obj_)
        else:
            self._obj_.append(value)

    def remove(self, value):
        self._obj_.remove(value)

    def reverse(self):
        self._obj_.reverse()

    @property
    def raw(self):
        return self._obj_


def proxywrapper(value, schema):
    """ The top-level API for wrapping an arbitrary object. """
    if isinstance(schema, dict):
        return DotDictProxy(value, schema)
    if isinstance(schema, list):
        return DotListProxy(value, schema)
    return value
