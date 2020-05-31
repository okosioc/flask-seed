const express = require('express');
const nunjucks = require('nunjucks');
const _ = require('lodash');
const Mock = require('mockjs');
const querystring = require('querystring');
const qiniu = require('qiniu');
const config = require('./instance/ui.json');

const app = express();
const port = 3000;
// Use Nunjucks as express template
var env = nunjucks.configure('templates', {
    watch: true,
    autoescape: true,
    express: app
});
app.use(express.json());
app.use(express.urlencoded({extended: false})); // NOTE: extended:true can NOT parse complicated form names, e.g. user.accounts[0].id

//
// Compatible with flask folder structure
//

// Static
app.use('/static', express.static('static'));

//
// Compatible with Jinja2's filters
//

// Jinja2's tojson filter
// Dumps a structure to JSON so that it’s safe to use in <script> tags
env.addFilter('tojson', function (value, spaces) {
    if (value instanceof nunjucks.runtime.SafeString) {
        value = value.toString()
    }
    return nunjucks.runtime.markSafe(JSON.stringify(value, null, spaces));
});

// We need to invoke dict method keys(), it is not supported in Nunjucks.
// These filters should also be implemented in Jinja2.
env.addFilter('keys', function (object) {
    return _.keys(object);
});

// NOTE: Add filters here if you are using jinja2 filters like filesizeformat, etc.

//
// Compatible with Jinja2's global variables
//

// i18n function of flask-babel
env.addGlobal('_', function (str) {
    return str;
});
// User session of flask-login
var current_user = {
    is_authenticated: false,
    is_admin: true,
    head: '/static/assets/img/blog/avt-1.jpg',
    name: 'Admin',
};
env.addGlobal('current_user', current_user);
// Request level variables to all templates
app.use(function (req, res, next) {
    // Inject Request object of express, http://expressjs.com/en/api.html#req
    // Please note the difference to flask.request, https://flask.palletsprojects.com/en/1.1.x/templating/#standard-context
    env.addGlobal('request', req);

    // Update params of current url, e.g, href="{{ update_query(p=1) }}".
    // Nunjucks also support keyword arguments, https://mozilla.github.io/nunjucks/templating#keyword-arguments
    env.addGlobal('update_query', function (kwargs) {
        // Remove the __keywords params added by Nunjucks
        _.unset(kwargs, '__keywords');
        // Update current query, http://expressjs.com/en/api.html#req.query
        return req.path + '?' + querystring.stringify(_.assign(req.query, kwargs));
    });

    next();
});

//
// Compatible with Jinja2's tests
//

// Jinja2's Builtin Tests, https://jinja.palletsprojects.com/en/2.11.x/templates/#list-of-builtin-tests
env.addTest('none', function (v) {
    return _.isNull(v);
});
env.addTest('undefined', function (v) {
    return _.isUndefined(v);
});
env.addTest('defined', function (v) {
    return !_.isUndefined(v);
});
env.addTest('string', function (v) {
    if (v instanceof nunjucks.runtime.SafeString) {
        return true;
    }
    return _.isString(v);
});

//
// Compatible with flask-seed's model definition and related crud logic
//

// Mock model's jschema is a subset of Object Schema from OAS 3.0, it is converted from app.core.schema::SchemaDict
// https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.3.md#schemaObject
// https://swagger.io/docs/specification/data-models/
// However, we still add two grammars
//   - Add format to array, so that we can gen a component for the whole array
//   - Add indexes to root object, so that it can be used to generate search form
var mock_models = [
    {
        'name': 'user',
        'jschema': {
            'type': 'object',
            'properties': {
                '_id': {
                    'type': 'string',
                    'format': 'ObjectId'
                },
                'name': {
                    'type': 'string'
                },
                'email': {
                    'type': 'string'
                },
                'intro': {
                    'type': 'string',
                    'format': 'textarea'
                },
                'detail': {
                    'type': 'string',
                    'format': 'rte'
                },
                'avatar': {
                    'type': 'string',
                    'format': 'image'
                },
                'photos': {
                    'type': 'array',
                    'items': {
                        'type': 'string'
                    },
                    'format': 'image'
                },
                'portfolios': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'url': {
                                'type': 'string'
                            },
                            'key': {
                                'type': 'string'
                            },
                            'name': {
                                'type': 'string'
                            },
                            'width': {
                                'type': 'integer'
                            },
                            'height': {
                                'type': 'integer'
                            }
                        }
                    },
                    'format': 'image'
                },
                'point': {
                    'type': 'integer'
                },
                'vip': {
                    'type': 'boolean'
                },
                'status': {
                    'type': 'string',
                    'enum': ['normal', 'rejected'],
                    'format': 'select'
                },
                'tags': {
                    'type': 'array',
                    'items': {
                        'type': 'string'
                    },
                    'format': 'select'
                },
                'roles': {
                    'type': 'array',
                    'items': {
                        'type': 'integer',
                        'enum': [1, 2, 9]
                    },
                    'format': 'select'
                },
                'accounts': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'id': {
                                'type': 'integer'
                            },
                            'name': {
                                'type': 'string'
                            },
                            'balance': {
                                'type': 'number'
                            },
                            'logo': {
                                'type': 'string',
                                'format': 'image'
                            }
                        },
                        'required': ['id']
                    }
                },
                'lastLogin': {
                    'type': 'object',
                    'properties': {
                        'ip': {
                            'type': 'string',
                            'format': 'ipv4'
                        },
                        'location': {
                            'type': 'string'
                        },
                        'device': {
                            'type': 'string'
                        },
                        'dateTime': {
                            'type': 'string',
                            'format': 'date-time'
                        }
                    }
                },
                'createTime': {
                    'type': 'string',
                    'format': 'date-time'
                },
                'updateTime': {
                    'type': 'string',
                    'format': 'date-time'
                }
            },
            'required': ['name', 'avatar', 'point', 'vip', 'status', 'roles', 'createTime'],
            'indexes': ['name', 'email', 'point', 'vip', 'status']
        }
    }
];
var mock_model = mock_models[0];
// Mock records generation with pagination support
// About mockjs's random, https://github.com/nuysoft/Mock/wiki/Mock.Random
var mock_records = Mock.mock({
    'data|20-50': [{
        '_id': '@string("number", 24)', // NOTE: _id field should be 12-byte bson.ObjectId.
        'name': '@first',
        'email': '@email("flask-seed.com")',
        'point': '@integer(0, 100)',
        'vip': '@boolean',
        'status': '@pick(["normal", "rejected"])',
        'roles': ['@pick([1, 2, 9])'],
        'accounts|2-5': [{
            'id|+1': 1,
            'name': /act_\d{11}/,
            'balance': '@float(0, 10000, 0, 2)',
        }],
        'createTime': '@date("yyyy-MM-dd HH:mm:ss.S")'
    }]
}).data, mock_page_count = 10;

function init_mock_record() {
    return Mock.mock({
        'name': '@first',
        'point': 0,
        'vip': false,
        'status': 'normal',
        'roles': [1],
        'createTime': '@now("yyyy-MM-dd HH:mm:ss.S")'
    });
}

// Create qiniu put policy
// https://developer.qiniu.com/kodo/manual/1206/put-policy
// https://developer.qiniu.com/kodo/manual/1235/vars#magicvar
function gen_qiniu_token() {
    var options = {
        scope: config.qiniu.bucket,
        mimeLimit: 'image/jpeg;image/png',
        saveKey: '${year}${mon}${day}/${hour}${min}${sec}_${fsize}${ext}',
        returnBody: '{"etag":"${etag}","name":"${fname}","key":"${key}","url":"' + config.qiniu.base + '/${key}","width":${imageInfo.width},"height":${imageInfo.height}}'
    };
    var pp = new qiniu.rs.PutPolicy(options), mac = new qiniu.auth.digest.Mac(config.qiniu.as, config.qiniu.sk);
    return pp.uploadToken(mac);
}

// Request values are all string, this helper function try to convert a string to a type, according the path in schema
function convert_string_to_type(schema, segments, v) {
    // Get sub schema of a path segment, e.g, [accounts, 0, id] or [name]
    // NOTE: We only support very little keywords of json schema here as it is generated from app.core.schema::SchemaDict.
    // There should be no keywords such as oneOf, $ref, patternProperties, additionalProperties, etc.
    var sub = _.reduce(segments, function (result, segment) {
        if (result.type == 'object') {
            return _.get(result, 'properties.' + segment);
        } else if (result.type == 'array') {
            return _.get(result, 'items');
        } else {
            return result;
        }
    }, schema);
    var type = sub.type, value = v;
    if (type == 'integer') {
        value = parseInt(v)
    } else if (type == 'number') {
        value = parseFloat(v);
    } else if (type == 'boolean') {
        value = ('true' == v.toLowerCase()) ? true : false;
    }
    return value;
}

//
// Routers
//

// Index
app.get('/', function (req, res) {
    res.render('public/index.html');
});
app.get('/blank', function (req, res) {
    res.render('public/blank.html');
});

// Login
app.get('/login', function (req, res) {
    res.render('public/login.html');
});
app.post('/login', function (req, res) {
    current_user['is_authenticated'] = true;
    res.redirect('/dashboard/');
});

// Logout
app.get('/logout', function (req, res) {
    current_user['is_authenticated'] = false;
    res.redirect('/');
});

// Signup
app.get('/signup', function (req, res) {
    res.render('public/signup.html');
});
app.post('/signup', function (req, res) {
    current_user['is_authenticated'] = true;
    res.redirect('/dashboard/');
});

// Dashboard
app.get('/dashboard/', function (req, res) {
    res.render('dashboard/index.html');
});
app.get('/dashboard/blank', function (req, res) {
    res.render('dashboard/blank.html');
});

// CRUD
app.get('/crud/', function (req, res) {
    res.render('crud/index.html', {models: mock_models});
});
app.get('/crud/list/:modelName', function (req, res) {
    var modelName = req.params.modelName,
        model = _.find(mock_models, function (n) {
            return n.name == modelName
        }),
        schema = model.jschema,
        search = {},
        p = parseInt(req.query.p) || 1,
        offset = (p - 1) * mock_page_count;
    // Perform search
    _.forEach(req.query, function (v, k) {
        if (_.isEmpty(v)) return true;
        // Only check the params starts with search.
        if (k.startsWith("search.")) {
            k = k.replace("search.", ""); // Remove the search.
            // Convert string path to segments, e.g, search.name -> [name]
            var segments = k.replace(/\[/, '.').replace(/\]/, '').split('.');
            search[k] = convert_string_to_type(schema, segments, v);
        }
    });
    var matched_records = mock_records;
    if (!_.isEmpty(search)) {
        console.log(search);
        // NOTE: Only support EQUALS match here, do not support LIKE or BETWEEN, etc
        // If need to implement complex search, a simple way is to add comparison operators to the end of param name
        // e.g,
        //   search.name__like
        //   search.status__in
        //   search.point__gte
        //   search.createDate__between
        matched_records = _.filter(mock_records, search);
    }
    var mock_pages = _.ceil(matched_records.length / mock_page_count),
        records = _.drop(matched_records, offset).slice(0, mock_page_count),
        pagination = {
            'page': p,
            'pages': mock_pages,
            'prev': p <= 1 ? null : p - 1,
            'next': p >= mock_pages ? null : p + 1,
            'iter_pages': _.range(1, mock_pages + 1)
        };
    res.render('crud/list.html', {model: mock_model, search: search, records: records, pagination: pagination});
});
app.get('/crud/form/:modelName/(*)', function (req, res) {
    var recordId = req.params[0],
        record = init_mock_record();
    if (recordId) {
        record = _.find(mock_records, function (n) {
            return n._id == recordId
        });
        if (!record) {
            res.redirect('/404');
            return;
        }
    }
    res.render('crud/form.html', {model: mock_model, record: record, token: gen_qiniu_token()});
});
app.get('/crud/raw/:modelName/(*)', function (req, res) {
    var recordId = req.params[0],
        record = init_mock_record();
    if (recordId) {
        record = _.find(mock_records, function (n) {
            return n._id == recordId
        });
        if (!record) {
            res.redirect('/404');
            return;
        }
    }
    res.render('crud/raw.html', {model: mock_model, record: record});
});
app.post('/crud/save/:modelName/(*)', function (req, res) {
    var modelName = req.params.modelName,
        model = _.find(mock_models, function (n) {
            return n.name == modelName
        }),
        schema = model.jschema,
        recordId = req.params[0],
        record = init_mock_record();
    // Populate record
    _.forEach(req.body, function (v, k) {
        if (_.isEmpty(v)) return true;
        // Only check the params starts with model name
        if (k.startsWith(modelName)) {
            // Convert string path to segments, e.g, user.accounts[0].id -> [accounts, 0, id]
            var segments = k.replace(/\[/, '.').replace(/\]/, '').split('.').slice(1); // Remove the model name
            _.set(record, segments, convert_string_to_type(schema, segments, v));
        }
    });
    console.log(record);
    if (recordId) { // Update
        var existing = _.find(mock_records, function (n) {
            return n._id == recordId
        });
        if (!existing) {
            res.redirect('/404');
            return;
        }
        _.assign(existing, record) // Overwrite the whole record
    } else { // Create
        recordId = Mock.mock('@string("number", 24)');
        record._id = recordId;
        mock_records.push(record);
    }
    res.json({success: true, message: 'Save successfully.', rid: recordId});
});
app.post('/crud/delete/:modelName/:recordId', function (req, res) {
    var record = _.find(mock_records, function (n) {
        return n._id == req.params.recordId
    });
    if (!record) {
        res.redirect('/404');
        return;
    }
    _.remove(mock_records, function (n) {
        return n._id == record._id;
    });
    res.json({success: true, message: 'Delete successfully.'});
});
app.get('/crud/json/:modelName/:recordId', function (req, res) {
    var record = _.find(mock_records, function (n) {
        return n._id == req.params.recordId
    });
    if (!record) {
        res.redirect('/404');
        return;
    }
    res.json(record);
});

// Errors
app.get('/400', function (req, res) {
    var error = {
        'status': 400,
        'title': 'Invalid Request',
        'content': 'Unexpected request received!'
    };
    if (req.xhr) {
        res.send({success: false, message: error.content + '(' + error.status + ')'});
        return;
    }
    res.status(400).render('public/error.html', {error: error});
});
app.get('/403', function (req, res) {
    var error = {
        'status': 403,
        'title': 'Permission Denied',
        'content': 'Not allowed or forbidden!'
    };
    if (req.xhr) {
        res.send({success: false, message: error.content + '(' + error.status + ')'});
        return;
    }
    res.status(403).render('public/error.html', {error: error});
});
app.get('/500', function (req, res) {
    throw new Error()
});
app.use(function (req, res, next) {
    var error = {
        'status': 404,
        'title': 'Not Found',
        'content': 'The requested URL was not found on this server!'
    };
    if (req.xhr) {
        res.send({success: false, message: error.content + '(' + error.status + ')'});
        return;
    }
    res.status(404).render('public/error.html', {error: error});
});
app.use(function (err, req, res, next) {
    console.error(err.stack);
    var error = {
        'status': 500,
        'title': 'Internal Server Error',
        'content': 'Unexpected error occurred! Please try again later.'
    };
    if (req.xhr) {
        res.send({success: false, message: error.content + '(' + error.status + ')'});
        return;
    }
    res.status(500).render('public/error.html', {error: error});
});

//
// Run
//

app.listen(port, () => console.log(`ui is listening on port ${port}!`));