# -*- coding: utf-8 -*-
"""
    model
    ~~~~~~~~~~~~~~

    Model related.

    :copyright: (c) 2020 by weiminfeng.
    :date: 2021/6/5
"""

import json
from abc import ABCMeta
from copy import deepcopy
from datetime import datetime
from typing import no_type_check, Dict, Type, Callable, get_origin, get_args, get_type_hints, Set, Any

from bson import ObjectId

from . import SchemaError, DataError


# ----------------------------------------------------------------------------------------------------------------------
# Custom Types
#

class SimpleEnumMeta(type):
    """ Metaclass for SimpleEnum. """

    def __new__(mcs, name, bases, attrs):
        enum_class = type.__new__(mcs, name, bases, attrs)
        # Remove the attributes such as __module__, __qualname__
        enum_class._member_dict_ = {k: attrs[k] for k in attrs if not k.startswith('_')}
        # TODO: Check repeated names or values
        return enum_class

    def __getattr__(cls, name):
        if name.startswith('_'):
            raise AttributeError(name)
        try:
            return cls._member_dict_[name]
        except KeyError:
            raise AttributeError(name) from None

    def __getitem__(cls, name):
        return cls._member_dict_[name]

    def __iter__(cls):
        """ Returns all values. """
        return (cls._member_dict_[name] for name in cls._member_dict_)

    @property
    def __members__(cls):
        """ Returns all members name->value. """
        return cls._member_dict_

    def __len__(cls):
        return len(cls._member_dict_)

    def __repr__(cls):
        """ Return representation str. """
        return "<SimpleEnumMeta %r %s>" % (cls.__name__, list(cls))

    @property
    def type(cls):
        """ Get type of members, All members should be the same type. """
        return type(next(cls.__iter__(), None))

    def validate(cls, value):
        """ Validate if a value is defined in a simple enum class. """
        return value in cls._member_dict_.values()


class SimpleEnum(object, metaclass=SimpleEnumMeta):
    """ Parent class for simple enum fields. """
    pass


class Format(SimpleEnum):
    """ Predefined available formats, which should be used to control ui or api generation.

    Below values are the same with OAS 3.0
    https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.3.md#data-types
    https://swagger.io/docs/specification/data-models/data-types/
    """
    DATETIME = 'date-time'
    DATE = 'date'
    PASSWORD = 'password'
    BYTE = 'byte'
    # Below values are self-defined
    SELECT = 'select'
    TEXTAREA = 'textarea'
    RTE = 'rte'
    MARKDOWN = 'markdown'
    IMAGE = 'image'  # Image upload support
    FILE = 'file'  # File upload support
    SWITCH = 'switch'  # Bool
    IPV4 = 'ipv4'
    IPV6 = 'ipv6'
    CHART = 'chart'
    LATLNG = 'latlng'
    TABLE = 'table'
    OBJECTID = 'objectid'


class Comparator(SimpleEnum):
    """ Predefined compartors, which should be used to control search conditions.

    These comparators are referred to https://docs.mongodb.com/manual/reference/operator/query-comparison/
    Just append $ to build a search.
    """
    EQ = 'eq'  # =
    NE = 'ne'  # !=
    GT = 'gt'  # >
    GTE = 'gte'  # >=
    LT = 'lt'  # <
    LTE = 'lte'  # <=
    IN = 'in'
    NIN = 'nin'
    LIKE = 'like'  # Need to convert this to regex


# ----------------------------------------------------------------------------------------------------------------------
# Constants
#

# Date format
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'

# Supported types for modal fields
# NOTE: These types are also used in form generation.
AUTHORIZED_TYPES = [
    bool,
    int,
    float,
    str,
    datetime,
    ObjectId,  # https://api.mongodb.com/python/current/api/bson/son.html
]


class UndefinedType:
    """ Undefined type. """

    def __repr__(self) -> str:
        return 'Undefined'

    def __reduce__(self) -> str:
        return 'Undefined'


Undefined = UndefinedType()


# ----------------------------------------------------------------------------------------------------------------------
# Conversions
#

class ModelJSONEncoder(json.JSONEncoder):
    """ Json encoder for model. """

    def default(self, o):
        """ Returns a serializable object for o. """
        if isinstance(o, ObjectId):
            return str(o)
        elif isinstance(o, datetime):
            return o.strftime(DATETIME_FORMAT)

        return json.JSONEncoder.default(self, o)


# ----------------------------------------------------------------------------------------------------------------------
# Validator
#

class Validator:
    """ Callable validator definition. """
    __slots__ = 'func', 'skip_on_failure'

    def __init__(
            self,
            func: Callable,
            skip_on_failure: bool = False,
    ):
        self.func = func
        self.skip_on_failure = skip_on_failure


# ----------------------------------------------------------------------------------------------------------------------
# Model
#

class ModelField:
    """ Field definition for model. """
    __slots__ = (
        'name',
        'type_',
        'required',
        'format_',
        'default',
        'label',
        'description',
    )

    def __init__(self, name: str, type_: Type, required: bool = True, format_: Format = None, **kwargs) -> None:
        """ Init method.

        :param type_: annotaion for field, e.g, str or Dict[str, str] or List[Object]
        """
        self.name = name
        self.type_ = type_
        self.required = required
        self.format_ = format_
        self.default = kwargs.pop('default', None)
        self.label = kwargs.pop('label', None)
        self.description = kwargs.pop('description', None)

    def __str__(self):
        return f'{self.name}/{self.type_}/{self.required}/{self.format_}/{self.default}'


class ModelMeta(ABCMeta):
    """ Metaclass for model. """

    @no_type_check
    def __new__(mcs, name, bases, namespace, **kwargs):
        """ Create and return a new object. """
        fields: Dict[str, ModelField] = {}

        # TODO: Support callable validators

        slots: Set[str] = namespace.get('__slots__', ())
        slots = {slots} if isinstance(slots, str) else set(slots)

        for base in reversed(bases):
            if issubclass(base, BaseModel) and base is not BaseModel:
                fields.update(deepcopy(base.__fields__))

        def _validate_annotation(field_name, field_type):
            """ Validate field definition."""
            # Validate if shadows a parent attribute
            for base in bases:
                if getattr(base, field_name, None):
                    raise SchemaError(f'{field_name}: {field_type} shadows a parent attribute')
            #
            origin = get_origin(field_type)
            # Simple, including built-in type, SimpleEnum or sub model
            if origin is None:
                _validate_simple_annotation(field_name, field_type)
            # Dict
            elif origin is dict:
                k_type, v_type = get_args(field_type)
                if k_type is not str:
                    raise SchemaError(f'{field_name}: {field_type} only support str keys')
                #
                _validate_simple_annotation(field_name, v_type)
            # List
            elif origin is list:
                l_type = get_args(field_type)[0]
                _validate_simple_annotation(field_name, l_type)
            else:
                raise SchemaError(f'{field_name}: {field_type} is not supported')

        def _validate_simple_annotation(field_name, field_type):
            """ Inner method to validate built-in types, SimpleEnums or sub models. """
            if isinstance(field_type, SimpleEnumMeta):
                enum_types = set()
                for member in field_type:
                    enum_types.add(type(member))
                    if type(member) not in AUTHORIZED_TYPES:
                        raise SchemaError(f'{field_name}: {field_type} is not an authorized type')
                if len(enum_types) > 1:
                    raise SchemaError(f'{field_name}: {field_type} can not have more than one type')
            elif issubclass(field_type, BaseModel):
                for a_n, a_t in get_type_hints(field_type).items():
                    _validate_annotation(a_n, a_t)
            elif field_type not in AUTHORIZED_TYPES:
                raise SchemaError(f'{field_name}: {field_type} is not an authorized type')

        # Validation
        skips = set()
        if namespace.get('__qualname__') != 'BaseModel':
            # Create user defined fields
            annotations = namespace.get('__annotations__', {})
            for ann_name, ann_type in annotations.items():
                # Skip
                if ann_name.startswith('__'):
                    skips.add(ann_name)
                    continue
                # Validate
                _validate_annotation(ann_name, ann_type)
                # Create model field
                field = ModelField(ann_name, ann_type)
                value = namespace.get(ann_name, Undefined)
                # Field is required if undefined
                if value is Undefined:
                    field.required = True
                # Field is NOT required
                elif value is None:
                    field.required = False
                # Define a ModelField directly
                elif isinstance(value, ModelField):
                    field.required = value.required
                    field.format_ = value.format_
                    field.default = value.default
                    field.label = value.label
                    field.description = value.description
                # Set default value
                else:
                    field.default = value
                #
                fields[ann_name] = field

        # Create class
        exclude_from_namespace = fields.keys() | skips | {'__slots__'}
        new_namespace = {
            '__fields__': fields,
            '__slots__': slots,
            **{n: v for n, v in namespace.items() if n not in exclude_from_namespace},
        }
        cls = super().__new__(mcs, name, bases, new_namespace, **kwargs)
        return cls


class BaseModel(metaclass=ModelMeta):
    """ Base model definition. """

    __slots__ = ('__dict__', '__fields_set__', '__errors__')
    __doc__ = ''

    def __init__(self, *d: Dict[str, Any], **data: Any) -> None:
        """ Init.

        :param d: create model from dict
        :param **data: create model from kwargs
        """
        data_ = d[0] if d else data
        values, fields_set, errors = self.validate_data(data_)
        object.__setattr__(self, '__dict__', values)
        object.__setattr__(self, '__fields_set__', fields_set)
        object.__setattr__(self, '__errors__', errors)

    def validate(self):
        """ Validate self. """
        _, _, errors = self.validate_data(self.__dict__)
        object.__setattr__(self, '__errors__', errors)
        return errors

    @classmethod
    def validate_data(cls, data: Dict[str, Any]):
        """ Validate data against model.

        :param data: Inner sub models can be dict or model instance
        """
        values = {}
        fields_set = set()
        errors = []
        #
        # print(f'Validate {cls.__name__} with {data}')
        for field_name, field_type in cls.__fields__.items():
            field_value, field_errors = cls._validate_field(field_type, data.get(field_name, Undefined))
            if field_value is not Undefined:
                values[field_name] = field_value
                fields_set.add(field_name)
            if field_errors:
                errors.extend(field_errors)

        #
        return values, fields_set, errors

    @classmethod
    def _validate_field(cls, field: ModelField, value: Any):
        """ Validate value against field. """
        field_errors = []
        # Undefined logic, check required and set default value
        if value is Undefined:
            if field.required:
                field_errors.append(DataError(f'{cls.__name__}.{field.name}: {field.type_} is required'))
            #
            field_value = value
            if field.default is not None:
                if callable(field.default):
                    field_value = field.default()
                else:
                    field_value = field.default
        # Validate Logic, check value against field definition
        else:
            origin = get_origin(field.type_)
            # Dict
            if origin is dict:
                if field.required and not value:
                    field_errors.append(DataError(f'{cls.__name__}.{field.name}: {field.type_} is required'))
                #
                field_value = {}
                v_type = get_args(field.type_)[1]
                for k, v_ in value.items():
                    if not isinstance(k, str):
                        field_errors.append(
                            DataError(f'{cls.__name__}.{field.name}: {field.type_} only support str keys'))
                    #
                    type_value, type_errors = cls._validate_type(field, v_, v_type)
                    field_value[k] = type_value
                    if type_errors:
                        field_errors.extend(type_errors)
            # List
            elif origin is list:
                if field.required and not value:
                    field_errors.append(DataError(f'{cls.__name__}.{field.name}: {field.type_} is required'))
                #
                field_value = []
                l_type = get_args(field.type_)[0]
                for v_ in value:
                    type_value, type_errors = cls._validate_type(field, v_, l_type)
                    field_value.append(type_value)
                    if type_errors:
                        field_errors.extend(type_errors)
            # built-in type, SimpleEnum or sub model
            else:
                if value is None:
                    field_value = value
                    field_errors.append(DataError(f'{field.name}: {field.type_} is required'))
                else:
                    type_value, type_errors = cls._validate_type(field, value, field.type_)
                    field_value = type_value
                    if type_errors:
                        field_errors.extend(type_errors)
        #
        # print(f'Validate field {field} with {value} -> {field_value} {field_errors}')
        return field_value, field_errors

    @classmethod
    def _validate_type(cls, field: ModelField, value: Any, type_: Type):
        """ Validate simple type, i.e, built-in type, SimpleEnum or sub model. """
        type_errors = []
        type_value = value
        #
        if type_value is not None:
            if isinstance(type_, SimpleEnumMeta):
                if not type_.validate(type_value):
                    type_errors.append(
                        DataError(f'{cls.__name__}.{field.name}: {field.type_} has invalid value'))
            elif issubclass(type_, BaseModel):
                #  Value can be raw dict against sub model
                if isinstance(type_value, dict):
                    type_value = type_(**value)
                    if type_value.__errors__:
                        type_errors.extend(type_value.__errors__)
                # Value is instance of sub model
                else:
                    errors = type_value.validate()
                    if errors:
                        type_errors.extend(errors)
            elif not isinstance(type_value, type_):
                type_errors.append(DataError(f'{cls.__name__}.{field.name}: {field.type_} only support {type_} value'))
        #
        return type_value, type_errors

    def __setattr__(self, name, value):
        self.__dict__[name] = value
        self.__fields_set__.add(name)

    def __getattr__(self, name):
        """ if the field name is predefined and referral model, create a model object first. """
        if name in self.__class__.__fields__:
            type_ = self.__class__.__fields__[name].type_
            origin = get_origin(type_)
            v = None
            if origin is None:
                if issubclass(type_, BaseModel):
                    v = type_()
            elif origin is list:
                v = []
            elif origin is dict:
                v = {}
            #
            if v is not None:
                self.__setattr__(name, v)
            return v
        #
        raise AttributeError(f'\'{self.__class__.__name__}\' object has no attribute \'{name}\'')

    def __str__(self):
        return f'{self.__class__.__name__}{self.dict()}'

    def copy(self, update: Dict[str, Any] = None, deep: bool = False):
        """ Copy logic. """
        update = update or {}
        v = dict(
            self._iter(),
            **update,
        )
        if deep:
            # chances of having empty dict here are quite low for using smart_deepcopy
            v = deepcopy(v)
        #
        cls = self.__class__
        m = cls.__new__(cls)
        object.__setattr__(m, '__dict__', v)
        fields_set = self.__fields_set__ | update.keys()
        object.__setattr__(m, '__fields_set__', fields_set)
        #
        return m

    def dict(self):
        """ Convert to dict. """
        return dict(self._iter(to_dict=True))

    def _iter(self, to_dict: bool = False):
        """ Access model recrusively. """
        for field_name, field_value in self.__dict__.items():
            yield field_name, self._get_value(field_value, to_dict=to_dict)

    @classmethod
    def _get_value(cls, v, to_dict: bool):
        """ Access model field recrusively. """
        if isinstance(v, dict):
            return {k_: cls._get_value(v_, to_dict=to_dict) for k_, v_ in v.items()}
        elif isinstance(v, list):
            return [cls._get_value(v_, to_dict=to_dict) for v_ in v]
        elif isinstance(v, BaseModel):
            if to_dict:
                return v.dict()
            else:
                return v.copy()
        else:
            return v

    def json(self, **kwargs) -> str:
        """ Convert to json str. """
        return json.dumps(self.dict(), cls=ModelJSONEncoder, **kwargs)
