# -*- coding: utf-8 -*-
"""
    mongosupport.py
    ~~~~~~~~~~~~~~

    定义的对象只要继承MongoSupport即可获取读写MongoDB的能力

    :copyright: (c) 2016 by fengweimin.
    :date: 16/5/25
"""

import json
import re
from collections import MutableSequence, MutableMapping
from copy import deepcopy
from datetime import datetime

import pymongo
from bson.objectid import ObjectId
from pymongo import MongoClient, ReadPreference, uri_parser, WriteConcern
from pymongo.cursor import Cursor as PyMongoCursor


# ----------------------------------------------------------------------------------------------------------------------
# 自定义类型
#

class SchemaOperator(object):
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
    """
    Defined available values of a field.
    """
    repr = 'in'

    def __init__(self, *args):
        super(IN, self).__init__(*args)

    def __str__(self):
        return "<%s " % self.repr + ', '.join([repr(i) for i in self.operands]) + '>'

    def validate(self, value):
        if value in self.operands:
            for op in self.operands:
                if value == op and isinstance(value, type(op)):
                    return True
        return False


''' 暂时不支持, CRUD页面编辑该类型的字段时需要指定类型, 否则不知道应该将表单提交的值转化为哪种类型
class OR(SchemaOperator):
    """
    Defined available types of a field.
    """
    repr = 'or'

    def __init__(self, *args):
        super(OR, self).__init__(*args)

    def __str__(self):
        repr = ' %s ' % self.repr
        return '<' + repr.join([i.__name__ for i in self.operands]) + '>'

    def validate(self, value):
        return isinstance(value, tuple(self.operands))
'''

# ----------------------------------------------------------------------------------------------------------------------
# Constants
#

# 日期格式
DATETIME_FORMATS = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S.%fZ', '%Y:%m:%d %H:%M:%S',
                    '%Y-%m-%d']

# 字段允许使用的类型
# https://api.mongodb.com/python/current/api/bson/son.html
AUTHORIZED_TYPES = [
    bool,
    int,
    int,
    float,
    str,
    datetime,
    ObjectId,
]


# ----------------------------------------------------------------------------------------------------------------------
# Conversions
#

class MongoSupportJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        elif isinstance(o, datetime):
            return str(o.strftime(DATETIME_FORMATS[0]))

        return json.JSONEncoder.default(self, o)


# ----------------------------------------------------------------------------------------------------------------------
# Exceptions
#

class MongoSupportError(Exception):
    pass


class StructureError(MongoSupportError):
    """
    数据模型的定义上的错误.
    """
    pass


class DataError(MongoSupportError):
    """
    数据内容与数据定义不符.
    """
    pass


class ConnectionError(MongoSupportError):
    """
    数据库连接错误.
    """
    pass


# ----------------------------------------------------------------------------------------------------------------------
# Metaclass
#

class ModelMetaclass(type):
    """
    元类, 校验数据模型是否正确定义.
    """

    def __new__(mcs, name, bases, attrs):
        if name == 'Model':
            return type.__new__(mcs, name, bases, attrs)

        # 保护字段, 使用dot notation的方式访问数据的时候, 跳过这些保护字段
        attrs['_protected_field_names'] = {'_protected_field_names', '_valid_paths', 'validation_errors'}
        # 父类及其父类的所有类属性
        for mro in bases[0].__mro__:
            attrs['_protected_field_names'] = attrs['_protected_field_names'].union(set(mro.__dict__))
        attrs['_protected_field_names'] = list(attrs['_protected_field_names'])

        # 添加保留字段
        if '_id' not in attrs['structure']:
            attrs['structure']['_id'] = ObjectId

        # 验证数据结构
        attrs['_valid_paths'] = {}
        mcs._validate_structure(name, attrs)
        attrs['_valid_paths'] = {k.replace(name + '.', ''): v for k, v in attrs['_valid_paths'].items() if
                                 not k == name}

        '''
        print "Init model class %s with valid paths {" % name
        for k, v in sorted(attrs['_valid_paths'].iteritems()):
            print "    '%s': %s" % (k, v)
        print "} and protected field names {"
        for v in sorted(attrs['_protected_field_names']):
            print "    '%s'" % v
        print "}"
        '''

        # 验证其他描述符, 如必填/验证器/默认值/索引等
        mcs._validate_descriptors(name, attrs)

        return type.__new__(mcs, name, bases, attrs)

    @classmethod
    def _validate_structure(mcs, name, attrs):
        """
        验证数据结构的合法性.
        """
        struct = attrs['structure']
        protected = attrs['_protected_field_names']

        def __validate_structure(_struct, _name):
            # type
            if type(_struct) is type:
                attrs['_valid_paths'][_name] = _struct
                if _struct not in AUTHORIZED_TYPES:
                    raise StructureError("%s: %s is not an authorized type" % (_name, _struct))
            # {}
            elif isinstance(_struct, dict):
                attrs['_valid_paths'][_name] = {}
                if not len(_struct):
                    raise StructureError(
                        "%s: %s can not be a empty dict" % (_name, _struct))
                for key in _struct:
                    # Check key type
                    if isinstance(key, str):
                        if not re.match('^[a-zA-Z0-9_]+$', key):
                            raise StructureError("%s: %s can only contain letters, numbers or _" % (_name, key))
                        if key[0].isdigit():
                            raise StructureError("%s: %s must not start with digit" % (_name, key))
                        if attrs.get('use_dot_notation', True) and key in protected:
                            raise StructureError(
                                "%s: %s is a protected field name, please set use_dot_notation = False if you insist "
                                "to use this field name; protected fields are %s." % (_name, key, sorted(protected)))
                    else:
                        raise StructureError("%s: %s must be a str" % (_name, key))

                    __validate_structure(_struct[key], "%s.%s" % (_name, key))
            # []
            elif isinstance(_struct, list):
                attrs['_valid_paths'][_name] = []
                if not len(_struct):
                    raise StructureError(
                        "%s: %s can not be a empty list" % (_name, _struct))
                if len(_struct) > 1:
                    raise StructureError(
                        "%s: %s must not have more then one type" % (_name, _struct))
                __validate_structure(_struct[0], "%s.$" % _name)
            # SchemaOperator
            elif isinstance(_struct, SchemaOperator):
                if len(_struct) == 0:
                    raise StructureError("%s: %s can not be empty" % (_name, _struct))
                if isinstance(_struct, IN):
                    types = set()
                    for operand in _struct:
                        types.add(type(operand))
                        if type(operand) not in AUTHORIZED_TYPES:
                            raise StructureError("%s: %s in %s is not an authorized type (%s found)" % (
                                _name, operand, _struct, type(operand).__name__))
                    if len(types) > 1:
                        raise StructureError("%s: %s can not have more than one type" % (_name, _struct))
                    attrs['_valid_paths'][_name] = list(types)[0]
                else:
                    for operand in _struct:
                        if operand not in AUTHORIZED_TYPES:
                            raise StructureError("%s: %s in %s is not an authorized type (%s found)" % (
                                _name, operand, _struct, type(operand).__name__))
                    # Use tuple to represent many available types
                    attrs['_valid_paths'][_name] = tuple(_struct)
            else:
                raise StructureError(
                    "%s: %s is not a supported thing" % (_name, _struct))

        if struct is None:
            raise StructureError("%s.structure must not be None" % name)
        if not isinstance(struct, dict):
            raise StructureError("%s.structure must be a dict instance" % name)
        __validate_structure(struct, name)

    @classmethod
    def _is_nested_structure_in_list(mcs, valid_paths, path):
        """
        判断指定的访问路径是否是一个列表内部的嵌套结构.
        """
        tokens = path.split('.')
        if len(tokens) > 1:
            del tokens[-1]
            if '$' in tokens:
                return True
        return False

    @classmethod
    def _validate_descriptors(mcs, name, attrs):
        """
        验证相关设置, 如必填/验证器/默认值/索引等.
        """
        valid_paths = attrs['_valid_paths']

        for dv in attrs.get('default_values', {}):
            if dv not in valid_paths:
                raise StructureError("%s: Error in default_values: can't find %s in structure" % (name, dv))
            if mcs._is_nested_structure_in_list(valid_paths, dv):
                raise StructureError(
                    "%s: Error in default_values: can't set default values to %s which is a nested structure in list" %
                    (name, dv))

        for rf in attrs.get('required_fields', []):
            if rf not in valid_paths:
                raise StructureError("%s: Error in required_fields: can't find %s in structure" % (name, rf))
            if mcs._is_nested_structure_in_list(valid_paths, rf):
                raise StructureError(
                    "%s: Error in required_fields: can't set required fields to %s which is a nested structure in list"
                    % (name, rf))

        for v in attrs.get('validators', {}):
            if v not in valid_paths:
                raise StructureError("%s: Error in validators: can't find %s in structure" % (name, v))
            if mcs._is_nested_structure_in_list(valid_paths, v):
                raise StructureError(
                    "%s: Error in validators: can't set validators to %s which is a nested structure in list" %
                    (name, v))

        # required_fields
        if attrs.get('required_fields'):
            if len(attrs['required_fields']) != len(set(attrs['required_fields'])):
                raise StructureError("%s: duplicate required_fields : %s" % (name, attrs['required_fields']))

        # indexes
        if attrs.get('indexes'):
            for index in attrs['indexes']:
                if index.get('check', True):
                    if 'fields' not in index:
                        raise StructureError("%s: 'fields' key must be specify in indexes" % name)
                    for key, value in index.items():
                        if key == "fields":
                            if isinstance(value, str):
                                if value not in valid_paths:
                                    raise StructureError(
                                        "%s: Error in indexes: can't find %s in structure" % (name, value))
                            elif isinstance(value, list):
                                for val in value:
                                    if isinstance(val, tuple):
                                        field, direction = val
                                        if field not in valid_paths:
                                            raise StructureError(
                                                "%s: Error in indexes: can't find %s in structure" % (name, field))
                                        if direction not in [pymongo.DESCENDING, pymongo.ASCENDING, pymongo.HASHED,
                                                             pymongo.GEO2D, pymongo.GEOHAYSTACK,
                                                             pymongo.GEOSPHERE, pymongo.TEXT]:
                                            raise StructureError(
                                                "%s: index direction must be INDEX_DESCENDING, INDEX_ASCENDING, "
                                                "INDEX_HASHED, INDEX_GEO2D, INDEX_GEOHAYSTACK, "
                                                "INDEX_GEOSPHERE, INDEX_TEXT. Got %s" % (name, direction))
                                    else:
                                        if val not in valid_paths:
                                            raise StructureError(
                                                "%s: Error in indexes: can't find %s in structure" % (name, val))
                            else:
                                raise StructureError("%s: fields must be a string, a list of string or tuple "
                                                     "(got %s instead)" % (name, type(value)))
                        elif key == "ttl":
                            assert isinstance(value, int)


# ----------------------------------------------------------------------------------------------------------------------
# Core
#

class Model(dict, metaclass=ModelMetaclass):
    """
    Model = Dict schema definition + Dict content validation + Crud for Mongodb collection.
    """

    # 数据结构
    structure = None

    '''
    使用dot notations的方式在数据结构的外部设置必填/默认值/验证器,
    相比于内联的方式, 出现了行为上的歧义, 如下, 当某个列表内部包含嵌套的数据结构时,
    structure = {
        'name': unicode,
        'accounts': [{
            'no': unicode,
            'balance: float
        }]
    }
    设置字段accounts.balance的默认值时, 无法知道列表的初始长度;
    设置其为必填字段时, 又无法明确定义当accounts为空列表的时候是否需要执行必填判断;
    因此对当前版本的mongosupport, 我们不支持对一个列表内嵌套结构的字段设置必填/默认值/验证器.
    嵌套数组, 哈哈, 无解

    TODO: 可以考虑实现如下的内联模式, 无需采用dot notation的方式来设置必填/默认值/验证器, 因此也没有上述的歧义,
    structure = {
        Field('name', r=True, v=validator): unicode,
        Field('accounts', r=True): [{
            Field('no', r=True): unicode,
            Field('balance', r=True, default=0, v=validator): float
        }]
    }
    与mongoengine不同, mongoengine把嵌套的数据结构解释为另一个数据对象, 我们只是将其视为整个数据模型的一部分,
    必填和验证器的逻辑可以勉强实现一致, 但是设置默认值的逻辑则不完全相同,
    mongoengine总是可以在生成这个子数据对象的时候初始化默认值, 而mongosupport作为一个整体, 初始化的机会只有一次,
    后续想要添加子数据结构的时候, 则没有生成默认值的机制了, 除非使用自己定义的dict（牺牲代码的简洁度）或者是重载__setattr__方法.

    '''

    # 必填字段
    required_fields = []

    # 字段默认值
    default_values = {}

    # 验证器
    validators = {}
    # 是否触发异常, 如果不触发, 验证错误会被保存在self.validation_errors中
    raise_validation_errors = True

    # 索引定义
    indexes = []

    # Enable schemaless support
    # 允许保存没有定义的字段, 字段值的读写暂时只能通过__getitem__或者__setitem__访问, 或者在初始化整个文档对象时传入
    use_schemaless = False

    # 是否使用dot notations的方式访问
    # https://docs.mongodb.com/manual/core/document/#document-dot-notation
    # <embedded document>.<field>
    # <array>.<index> or <array>.$
    use_dot_notation = True

    # 该数据模型对应的collection名字
    __collection__ = None

    # pymongo.Collection - 可以使用此字段直接调用pymongo的方法, 返回的是普通的dict对象
    # https://api.mongodb.com/python/current/tutorial.html
    collection = None

    # 当前正在访问的数据库别名, 如果为空, 相当于DEFAULT_CONNECTION_NAME
    db_alias = None

    def __init__(self, doc=None, set_default=True):
        """
        :param doc: a dict
        """
        super(Model, self).__init__()

        # raise_validation_errors=False时, 验证器返回的所有错误
        self.validation_errors = {}

        if doc is not None:
            for k, v in doc.items():
                self[k] = v

        if set_default and self.default_values:
            self._set_default_values(self, self.structure)

    def __str__(self):
        """
        定义输出格式.
        :return:
        """
        return "%s(%s)" % (self.__class__.__name__, dict(self))

    def validate(self):
        """
        validate the document.
        This method will verify if:
          * the doc follow the structure,
          * all required fields are filled
        Additionally, this method will process all validators.
        """
        self._validate_doc(self, self.structure)

        if self.required_fields:
            self._validate_required(self)

        if self.validators:
            self._process_validators(self)

        return False if self.validation_errors else True

    def _validate_doc(self, doc, struct, path=""):
        """
        check if doc field types match the doc field structure.
        """
        if doc is None:
            return
        # type
        if type(struct) is type:
            if not isinstance(doc, struct):
                self._raise_exception(DataError, path,
                                      "%s must be an instance of %s not %s" % (
                                          path, struct.__name__, type(doc).__name__))
        # {}
        elif isinstance(struct, dict):
            if not isinstance(doc, dict):
                self._raise_exception(DataError, path,
                                      "%s must be an instance of dict not %s" % (
                                          path, type(doc).__name__))

            # For fields in doc but not in structure
            doc_struct_diff = list(set(doc).difference(set(struct)))
            bad_fields = [d for d in doc_struct_diff]
            # TODO: Simple validation for the fields in doc but not in structure
            if bad_fields and not self.use_schemaless:
                self._raise_exception(DataError, None,
                                      "unknown fields %s in %s" % (bad_fields, type(doc).__name__))
            for key in struct:
                if key in doc:
                    self._validate_doc(doc[key], struct[key], ("%s.%s" % (path, key)).strip('.'))
        # []
        elif isinstance(struct, list):
            if not isinstance(doc, list):
                self._raise_exception(DataError, path,
                                      "%s must be an instance of list not %s" % (path, type(doc).__name__))
            for obj in doc:
                self._validate_doc(obj, struct[0], path)
        # SchemaOperator
        elif isinstance(struct, SchemaOperator):
            if not struct.validate(doc):
                if isinstance(struct, IN):
                    self._raise_exception(DataError, path,
                                          "%s must be in %s not %s" % (path, struct.operands, doc))
                else:
                    self._raise_exception(DataError, path,
                                          "%s must be an instance of %s not %s" % (path, struct, type(doc).__name__))
        #
        else:
            self._raise_exception(DataError, path,
                                  "%s must be an instance of %s not %s" % (
                                      path, struct.__name__, type(doc).__name__))

    def _validate_required(self, doc):
        """
        验证必填字段.
        """
        for rf in self.required_fields:
            vals = self._get_values_by_path(doc, rf)
            if not vals:
                self._raise_exception(DataError, rf, "%s is required" % rf)

    def _process_validators(self, doc):
        """
        调用预定义的validator进行校验.
        """
        for key, validators in self.validators.items():
            vals = self._get_values_by_path(doc, key)
            if vals:
                if not hasattr(validators, "__iter__"):
                    validators = [validators]
                for val in vals:
                    for validator in validators:
                        try:
                            if not validator(val):
                                raise DataError("%s does not pass the validator " + validator.__name__)
                        except Exception as e:
                            self._raise_exception(DataError, key, str(e) % key)

    def _raise_exception(self, exception, field, message):
        """
        处理异常.
        """
        if self.raise_validation_errors:
            raise exception(message)
        else:
            if field not in self.validation_errors:
                self.validation_errors[field] = []
            self.validation_errors[field].append(exception(message))

    def _get_values_by_path(self, doc, path):
        """
        获取指定路径的所有值, 会递归进去列表内部.
        """
        vals = [doc]
        for key in path.split('.'):
            # print 'getting values by path %s from %s' % (key, vals)
            new_vals = []
            for val in vals:
                if val is None or key not in val:
                    continue
                val = val[key]
                if isinstance(val, list):
                    for v in val:
                        new_vals.append(v)
                else:
                    new_vals.append(val)
            vals = new_vals

        return vals

    def _set_default_values(self, doc, struct, path=""):
        """
        设置字段的默认值.
        """
        for key in struct:
            new_path = ("%s.%s" % (path, key)).strip('.')
            # print "setting default value for %s with type %s" % (new_path, struct[key])
            # type
            if type(struct[key]) is type:
                if new_path in self.default_values and key not in doc:
                    new_value = self.default_values[new_path]
                    if callable(new_value):
                        new_value = new_value()
                    doc[key] = new_value
            # {}
            if isinstance(struct[key], dict):
                # 设置整个字典字段的默认值
                if new_path in self.default_values and key not in doc:
                    new_value = self.default_values[new_path]
                    if callable(new_value):
                        new_value = new_value()
                    elif isinstance(new_value, dict):
                        new_value = deepcopy(new_value)
                    doc[key] = new_value
                # 递归处理字典字段
                if [i for i in self.default_values if i.startswith("%s." % new_path)]:
                    if key not in doc or doc[key] is None:
                        doc[key] = {}
                    self._set_default_values(doc[key], struct[key], new_path)
            # []
            if isinstance(struct[key], list):
                # 设置整个列表字段的默认值
                # 无需再递归进列表内部设置默认值, 因为无法初始化列表的元素个数
                if new_path in self.default_values and key not in doc:
                    new_value = self.default_values[new_path]
                    if callable(new_value):
                        new_value = new_value()
                    elif isinstance(new_value, list):
                        new_value = new_value[:]
                    doc[key] = new_value
            # SchemaOperator
            if isinstance(struct[key], SchemaOperator):
                if new_path in self.default_values and key not in doc:
                    new_value = self.default_values[new_path]
                    doc[key] = new_value

    def __setattr__(self, key, value):
        """
        Support dot notation.
        """
        if self.use_dot_notation and key not in self._protected_field_names and key in self.structure:
            # print "setting attr %s with %s" % (key, value)
            if isinstance(value, (DotDictProxy, DotListProxy)):
                self[key] = value._obj_
            else:
                self[key] = value
        else:
            dict.__setattr__(self, key, value)

    def __getattr__(self, key):
        """
        Support dot notation.
        """
        if self.use_dot_notation and key not in self._protected_field_names and key in self.structure:
            s = self.structure[key]
            found = self.get(key, None)
            # print "getting attr %s for structure %s with value %s" % (key, s, type(found))
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

    #
    #
    # Class level pymongo api
    #
    #

    @classmethod
    def get_collection(cls, **kwargs):
        """
        Returns the collection for the document.
        可以在此处为collection重置read_preference/write_concern等参数.
        """
        if kwargs.get('refresh', False) or not hasattr(cls, 'collection') or cls.collection is None:
            db = get_db(cls.db_alias if cls.db_alias else DEFAULT_CONNECTION_NAME)

            read_preference = kwargs.get("read_preference") or ReadPreference.PRIMARY
            write_concern = kwargs.get("write_concern") or WriteConcern(w=1)

            collection_name = cls.__collection__
            cls.collection = db[collection_name].with_options(read_preference=read_preference,
                                                              write_concern=write_concern)
            # 每次获取collection时尝试创建索引
            # https://docs.mongodb.com/getting-started/python/indexes/
            cls._create_indexes(cls.collection)

        return cls.collection

    @classmethod
    def _create_indexes(cls, collection):
        """
        创建索引.
        对于复杂路径, 比如一个数组下的结构, 我们预定义好的路径是使用$标识数组.
        比如{images:[{'url':unicode}]}, images.$.url是正确的路径, 需要将其转化为images.url来创建mongodb的索引.
        """
        # print "Try to create index for %s" % cls.__name__
        for index in deepcopy(cls.indexes):
            unique = False
            if 'unique' in index:
                unique = index.pop('unique')

            given_fields = index.pop("fields", list())
            if isinstance(given_fields, str):
                fields = [(given_fields, pymongo.ASCENDING)]
            else:
                fields = []
                for field in given_fields:
                    if isinstance(field, str):
                        field = (field, pymongo.ASCENDING)
                    fields.append(field)

            # print 'Creating index for {}'.format(str(given_fields))
            fields = [(f[0].replace('.$', ''), f[1]) for f in fields]
            collection.create_index(fields, unique=unique, **index)

    @classmethod
    def insert_one(cls, doc, *args, **kwargs):
        """
        Please note we do not apply validation here.
        """
        collection = cls.get_collection(**kwargs)
        # InsertOneResult
        return collection.insert_one(doc, *args, **kwargs)

    @classmethod
    def insert_many(cls, docs, *args, **kwargs):
        """
        Please note we do not apply validation here.
        """
        collection = cls.get_collection(**kwargs)
        # InsertManyResult
        return collection.insert_many(docs, *args, **kwargs)

    @classmethod
    def find_one(cls, filter_or_id=None, *args, **kwargs):
        collection = cls.get_collection(**kwargs)
        doc = collection.find_one(filter_or_id, *args, **kwargs)
        if doc:
            return cls(doc)
        else:
            return None

    @classmethod
    def find(cls, *args, **kwargs):
        """
        查找多个数据记录, 参数可以参考:
        https://api.mongodb.com/python/current/api/pymongo/collection.html#pymongo.collection.Collection.find
        """
        collection = cls.get_collection(**kwargs)
        return ModelCursor(cls, collection, *args, **kwargs)

    @classmethod
    def find_by_ids(cls, ids, *args, **kwargs):
        """
        指定多个id查询, 返回结果保留ids的顺序.
        """
        filter = {}
        if 'filter' in kwargs:
            filter.update(kwargs.pop('filter'))
        elif len(args) > 0:
            filter.update(args.pop(0))
        filter.update({'_id': {'$in': ids}})

        records = list(cls.find(filter, *args, **kwargs))
        records.sort(key=lambda i: ids.index(i._id))
        return records

    @classmethod
    def count(cls, filter=None, **kwargs):
        collection = cls.get_collection(**kwargs)
        return collection.count(filter, **kwargs)

    @classmethod
    def replace_one(cls, filter, replacement, *args, **kwargs):
        """
        Please note we do not apply validation here.
        """
        collection = cls.get_collection(**kwargs)
        # UpdateResult
        return collection.replace_one(filter, replacement, *args, **kwargs)

    @classmethod
    def update_one(cls, filter, update, *args, **kwargs):
        """
        Please note we do not apply validation here.
        """
        collection = cls.get_collection(**kwargs)
        # UpdateResult
        return collection.update_one(filter, update, *args, **kwargs)

    @classmethod
    def update_many(cls, filter, update, *args, **kwargs):
        """
        Please note we do not apply validation here.
        """
        collection = cls.get_collection(**kwargs)
        # UpdateResult
        return collection.update_many(filter, update, *args, **kwargs)

    @classmethod
    def delete_one(cls, filter, **kwargs):
        collection = cls.get_collection(**kwargs)
        # DeleteResult
        return collection.delete_one(filter)

    @classmethod
    def delete_many(cls, filter, **kwargs):
        collection = cls.get_collection(**kwargs)
        # DeleteResult
        return collection.delete_many(filter)

    @classmethod
    def aggregate(cls, pipeline, **kwargs):
        """
        聚合逻辑, 参考:
        https://api.mongodb.com/python/current/api/pymongo/collection.html#pymongo.collection.Collection.aggregate
        """
        collection = cls.get_collection(**kwargs)
        return collection.aggregate(pipeline, **kwargs)

    @classmethod
    def distinct(cls, key, filter=None, **kwargs):
        collection = cls.get_collection(**kwargs)
        return collection.distinct(key, filter, **kwargs)

    @classmethod
    def group(cls, key, condition, initial, reduce, finalize=None, **kwargs):
        collection = cls.get_collection(**kwargs)
        return collection.group(key, condition, initial, reduce, finalize, **kwargs)

    #
    #
    # Instance level pymongo api
    #
    #

    def save(self, insert_with_id=False, **kwargs):
        if not self.validate():
            raise DataError(
                "It is an illegal %s object with errors, %s" % (self.__class__.__name__, self.validation_errors))

        collection = self.get_collection(**kwargs)
        _id = self.get('_id', None)
        if insert_with_id or not _id:
            # InsertOneResult
            return collection.insert_one(self)
        else:
            # UpdateResult
            return collection.replace_one({'_id': _id}, self)

    def reload(self, **kwargs):
        existing = self.find_one({'_id': self['_id']}, **kwargs)
        if not existing:
            raise DataError("Can not load existing document by %s" % self['_id'])

        self.clear()
        for k, v in existing.items():
            self[k] = v

        self.validation_errors = {}

    def delete(self, **kwargs):
        collection = self.get_collection(**kwargs)
        # DeleteResult
        return collection.delete_one({'_id': self['_id']})

    #
    #
    # JSON serialization
    #
    #

    def to_json(self, **kwargs):
        """
        Convert the model instance to a json string.
        """
        return json.dumps(self, cls=MongoSupportJSONEncoder, **kwargs)

    @classmethod
    def from_json(cls, doc, **kwargs):
        """
        Convert a json string to a model instance.
        Make use of the structure for decoding.
        """

        def json_decode(value, type):
            if value is None:
                return value

            if type is datetime:
                return datetime.strptime(value, DATETIME_FORMATS[0])
            elif type is ObjectId:
                return ObjectId(value)
            else:
                return type(value)

        def _convert_dict(doc, struct):
            """
            Recursively convert specified type.
            """
            for key in struct:
                s = struct[key]
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

        def _convert_list(doc, struct):
            s = struct[0]
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
        _convert_dict(d, cls.structure)
        return cls(d, False)

    def foobar(self):
        pass


# ----------------------------------------------------------------------------------------------------------------------
# Cursor - Wrap pymongo.cursor to return mongosupport objects
#

class ModelCursor(PyMongoCursor):
    def __init__(self, document_class, collection, *args, **kwargs):
        self._document_class = document_class
        super(ModelCursor, self).__init__(collection, *args, **kwargs)

    def __next__(self):
        return self._document_class(next(super(ModelCursor, self)))

    def __next__(self):
        return self._document_class(super(ModelCursor, self).__next__())

    def __getitem__(self, index):
        if isinstance(index, slice):
            return super(ModelCursor, self).__getitem__(index)
        else:
            return self._document_class(super(ModelCursor, self).__getitem__(index))


# ----------------------------------------------------------------------------------------------------------------------
# Connection - Support multiple database
#

DEFAULT_CONNECTION_NAME = 'default'

# {alias:setting parameters dict}
_connection_settings = {}
# {alias:instance of pymongo.MongoClient}
_connections = {}
# {alias:database of pymongo.Database}
_dbs = {}


def _register_connection(alias, name=None, host=None, port=None,
                         read_preference=ReadPreference.PRIMARY,
                         username=None, password=None, authentication_source=None,
                         **kwargs):
    """
    注册数据库的连接字符串
    Add a connection.
    :param alias: the name that will be used to refer to this connection throughout MongoSupport
    :param name: the name of the specific database to use
    :param host: the host name of the :program:`mongod` instance to connect to
    :param port: the port that the :program:`mongod` instance is running on
    :param read_preference: The read preference for the collection
    :param username: username to authenticate with
    :param password: password to authenticate with
    :param authentication_source: database to authenticate against
    :param kwargs: allow ad-hoc parameters to be passed into the pymongo driver
    """
    global _connection_settings

    conn_settings = {
        'name': name or 'test',
        'host': host or 'localhost',
        'port': port or 27017,
        'read_preference': read_preference,
        'username': username,
        'password': password,
        'authentication_source': authentication_source
    }

    conn_host = conn_settings['host']
    if '://' in conn_host:
        uri_dict = uri_parser.parse_uri(conn_host)
        # Connection parameters in host url will replace the ones in conn_settings
        conn_settings.update({
            'name': uri_dict.get('database') or name,
            'username': uri_dict.get('username'),
            'password': uri_dict.get('password'),
            'read_preference': read_preference,
        })
        uri_options = uri_dict['options']
        if 'replicaset' in uri_options:
            conn_settings['replicaSet'] = True
        if 'authsource' in uri_options:
            conn_settings['authentication_source'] = uri_options['authsource']

    conn_settings.update(kwargs)
    _connection_settings[alias] = conn_settings


def _get_connection(alias=DEFAULT_CONNECTION_NAME, reconnect=False):
    """
    获取数据路连接
    """
    global _connections

    if reconnect:
        disconnect(alias)

    if alias not in _connections:
        if alias not in _connection_settings:
            msg = 'Connection with alias "%s" has not been defined' % alias
            if alias == DEFAULT_CONNECTION_NAME:
                msg = 'You have not defined a default connection'
            raise ConnectionError(msg)
        # Check existing connections that can be shared for current alias
        conn_settings = _connection_settings[alias].copy()
        conn_settings.pop('name', None)
        conn_settings.pop('username', None)
        conn_settings.pop('password', None)
        conn_settings.pop('authentication_source', None)

        if 'replicaSet' in conn_settings:
            # Discard port since it can't be used on MongoReplicaSetClient
            conn_settings.pop('port', None)
            # Discard replicaSet if not base string
            if not isinstance(conn_settings['replicaSet'], str):
                conn_settings.pop('replicaSet', None)

        """
        Every MongoClient instance has a built-in connection pool.
        The client instance opens one additional socket per server for monitoring the server’s state.
        """
        connection_class = MongoClient

        try:
            connection = None
            # Check for shared connections
            connection_settings_iterator = (
                (db_alias, settings.copy()) for db_alias, settings in _connection_settings.items())
            for db_alias, connection_settings in connection_settings_iterator:
                connection_settings.pop('name', None)
                connection_settings.pop('username', None)
                connection_settings.pop('password', None)
                connection_settings.pop('authentication_source', None)
                if conn_settings == connection_settings and _connections.get(db_alias, None):
                    connection = _connections[db_alias]
                    break

            _connections[alias] = connection if connection else connection_class(**conn_settings)
        except Exception as e:
            raise ConnectionError("Cannot connect to database %s :\n%s" % (alias, e))
    return _connections[alias]


def get_db(alias=DEFAULT_CONNECTION_NAME, reconnect=False):
    """
    获取数据库实例
    """
    global _dbs

    if reconnect:
        disconnect(alias)

    if alias not in _dbs:
        conn = _get_connection(alias)
        conn_settings = _connection_settings[alias]
        db = conn[conn_settings['name']]
        # Authenticate if necessary
        if conn_settings['username'] and conn_settings['password']:
            db.authenticate(conn_settings['username'],
                            conn_settings['password'],
                            source=conn_settings['authentication_source'])
        _dbs[alias] = db
    return _dbs[alias]


def connect(db=None, alias=DEFAULT_CONNECTION_NAME, **kwargs):
    """
    Connect to the database specified by the 'db' argument.
    Connection settings may be provided here as well if the database is not running on the default port on localhost.
    If authentication is needed, provide username and password arguments as well.

    Multiple databases are supported by using aliases. Provide a separate `alias` to connect to different MongoClient.
    """
    global _connections
    if alias not in _connections:
        _register_connection(alias, db, **kwargs)
    return _get_connection(alias)


def disconnect(alias=DEFAULT_CONNECTION_NAME):
    """
    断开数据库连接.
    """
    global _connections
    global _dbs

    if alias in _connections:
        _get_connection(alias=alias).close()
        del _connections[alias]
    if alias in _dbs:
        del _dbs[alias]


# ----------------------------------------------------------------------------------------------------------------------
# Proxy - 使用代理机制来支持dot notation的方式来访问, 不会改变内部结构, 只是在访问的时候创建轻量级的proxy对象
#

class DotDictProxy(MutableMapping, object):
    """
    A proxy for a dictionary that allows attribute access to underlying keys.
    """

    def __init__(self, obj, struct):
        self._obj_ = obj
        self._struct_ = struct

    def __getattr__(self, key):
        if key in ['_obj_', '_struct_'] or key not in self._struct_:
            return object.__getattribute__(self, key)

        s = self._struct_[key]
        found = self._obj_.get(key, None)
        # print "dict proxy getting attr %s for structure %s with value %s" % (key, type(s).__name__, found)
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
        if key in ['_obj_', '_struct_'] or key not in self._struct_:
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

    def raw(self):
        return self._obj_


class DotListProxy(MutableSequence, object):
    """
    A proxy for a list that allows for wrapping items.
    """

    def __init__(self, obj, struct):
        self._obj_ = obj
        self._struct_ = struct

    def __getitem__(self, index):
        # print "list proxy getting index %s for structure %s with value %s" % (index, self._struct_, self._obj_[index])
        if isinstance(index, slice):
            return proxywrapper(self._obj_[index], self._struct_)
        else:
            return proxywrapper(self._obj_[index], self._struct_[0])

    def __setitem__(self, index, value):
        if isinstance(value, (DotDictProxy, DotListProxy)):
            self._obj_[index] = value._obj_
        else:
            self._obj_[index] = value

    def __delitem__(self, index):
        del self._obj_[index]

    def insert(self, index, value):
        if isinstance(value, (DotDictProxy, DotListProxy)):
            self._obj_.insert(index, value._obj_)
        else:
            self._obj_.insert(index, value)

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

    def raw(self):
        return self._obj_


def proxywrapper(value, struct):
    """
    The top-level API for wrapping an arbitrary object.
    """
    if isinstance(struct, dict):
        return DotDictProxy(value, struct)
    if isinstance(struct, list):
        return DotListProxy(value, struct)
    return value
