//
// Start a express+nunjucks server for ui development.
//

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
var env = nunjucks.configure('./app/templates', {
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
app.use('/static', express.static('./app/static'));

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

// We need to invoke dict method keys()/values()/items(), it is not supported in Nunjucks
// So we add below filters in both Nunjucks and Jinja2
env.addFilter('keys', function (object) {
    return _.keys(object);
});
env.addFilter('values', function (object) {
    return _.values(object);
});
env.addFilter('items', function (object) {
    return _.toPairs(object);
});
// Add split filter in both Nunjucks and Jinja2
env.addFilter('split', function (string, separator) {
    return _.split(string, separator);
});
// Filter timesince is used to display friendly time
env.addFilter('timesince', function (string) {
    return 'x time ago';
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
    is_editor: true,
    is_admin: true,
    _id: '9394',
    avatar: '/static/img/avatar.jpg',
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
// However, we still some grammars
//   - Add format to array, so that we can gen a component for the whole array
//   - Add searchables to root object, so that it can be used to generate search form
//   - Add sortables to root object, so that it can be used to generate order drowpdown
//   - Add columns to root object, so that it can be used to generate columns for table
var mock_models = [{
    "name": "user",
    "jschema": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "email": {"type": "string"},
            "password": {"type": "string"},
            "intro": {"type": "string", "format": "textarea"},
            "avatar": {"type": "string", "format": "image"},
            "point": {"type": "integer"},
            "status": {"type": "string", "enum": ["normal", "rejected"]},
            "roles": {"type": "array", "items": {"type": "integer", "enum": [1, 2, 9]}, "format": "select"},
            "createTime": {"type": "string", "format": "date-time"},
            "updateTime": {"type": "string", "format": "date-time"},
            "_id": {"type": "string", "format": "objectid"}
        },
        "required": ["name", "email", "avatar", "point", "status", "roles", "createTime"],
        "searchables": ["name", "email", "point", "status"],
        "columns": ["avatar", "name", "email", "point", "status", "roles", "createTime"]
    }
}, {
    "name": "tag",
    "jschema": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "weight": {"type": "integer"},
            "createTime": {"type": "string", "format": "date-time"},
            "_id": {"type": "string", "format": "objectid"}
        },
        "required": ["name", "weight", "createTime"],
        "searchables": ["name__like"],
        "columns": ["name", "weight", "createTime"]
    }
}, {
    "name": "post",
    "jschema": {
        "type": "object",
        "properties": {
            "uid": {"type": "string", "format": "objectid"},
            "cover": {"type": "string", "format": "image"},
            "title": {"type": "string"},
            "abstract": {"type": "string", "format": "textarea"},
            "body": {"type": "string", "format": "rte"},
            "tids": {"type": "array", "items": {"type": "string", "format": "objectid"}, "format": "select"},
            "createTime": {"type": "string", "format": "date-time"},
            "updateTime": {"type": "string", "format": "date-time"},
            "viewTimes": {"type": "integer"},
            "comments": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "uid": {"type": "string", "format": "objectid"},
                        "uname": {"type": "string"},
                        "uavatar": {"type": "string"},
                        "content": {"type": "string"},
                        "time": {"type": "string", "format": "date-time"}
                    },
                    "required": ["id", "uid", "content", "time"]
                }
            },
            "_id": {"type": "string", "format": "objectid"}
        },
        "required": ["uid", "cover", "title", "abstract", "body", "tids", "createTime", "viewTimes"],
        "searchables": ["title__like", "tids"],
        "columns": ["cover", "uid", "title", "tids", "viewTimes", "createTime"]
    }
}, {
    "name": "config",
    "jschema": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "value": {"type": "string"},
            "createTime": {"type": "string", "format": "date-time"},
            "_id": {"type": "string", "format": "objectid"}
        },
        "required": ["name", "createTime"],
        "searchables": ["name__like"],
        "columns": ["name", "createTime"]
    }
}];

// Generate Mock records by json schema
// About mockjs's random, https://github.com/nuysoft/Mock/wiki/Mock.Random
var mock_commands_dict = {};
_.forEach(mock_models, function (m) {
    var mock_commands = {
        '_id': '@string("number", 24)' // NOTE: _id field should be 12-byte bson.ObjectId.
    };
    _.forEach(m.jschema.required, function (f) { // Create for columns
        var schema = m.jschema.properties[f];
        // By name
        if (f == 'name') {
            mock_commands[f] = '@first'
        } else if (f == 'email') {
            mock_commands[f] = '@email("flask-seed.com")'
        } else if (f == 'title') {
            mock_commands[f] = '@title'
        }
        // By enum
        else if (schema.enum) {
            mock_commands[f] = '@pick(' + schema.enum + ')';
        } else if (schema.type == 'array' && schema.items.enum) {
            mock_commands[f] = ['@pick(' + schema.items.enum + ')'];
        }
        // By format
        else if (schema.format == 'objectid') {
            mock_commands[f] = '@string("number", 24)';
        } else if (schema.format == 'textarea') {
            mock_commands[f] = '@paragraph(1,2)';
        } else if (schema.format == 'rte') {
            mock_commands[f] = '@paragraph(3,7)';
        } else if (schema.format == 'date-time') {
            mock_commands[f] = '@now("yyyy-MM-dd HH:mm:ss.S")';
        }
        // By type
        else if (schema.type == 'boolean') {
            mock_commands[f] = '@@boolean'
        } else if (schema.type == 'integer') {
            mock_commands[f] = '@integer(0, 100)'
        } else if (schema.type == 'number') {
            mock_commands[f] = '@float(0, 10000, 0, 2)'
        }
    });
    mock_commands_dict[m.name] = mock_commands;
});

var mock_records_dict = function () {
    var ret = {};
    // Generate mock records
    _.forEach(mock_models, function (m) {
        var mock_commands = mock_commands_dict[m.name];
        // Manually control records size
        var size = '20-50';
        if (m.name == 'tag') {
            size = '3-8';
        }
        var mock = {};
        mock['data|' + size] = [mock_commands];
        ret[m.name] = Mock.mock(mock).data;
    });
    // Manually update records fields and relationship
    _.forEach(ret['user'], function (u) {
        u.avatar = '//cdn.flask-seed.com/avatar.jpg'
    });
    _.forEach(ret['post'], function (p) {
        p.uid = _.sample(ret['user'])._id;
        p.tids = [_.sample(ret['tag'])._id];
        p.cover = '//cdn.flask-seed.com/' + '800x533-' + _.sample(_.range(1, 6)) + '.jpg' // Pre-uploaded 3:2 images
    });
    return ret;
}(), mock_per_page = 10;

function init_mock_record(modelName) {
    var record = _.clone(mock_records_dict[modelName][0]);
    // Remove _id field, or it will be regarded as a existing record in some logic
    _.unset(record, '_id');
    return record;
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
    var pp = new qiniu.rs.PutPolicy(options), mac = new qiniu.auth.digest.Mac(config.qiniu.ak, config.qiniu.sk);
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

// Create a record by http post
function polulate_record(modelName, body) {
    var model = _.find(mock_models, function (n) {
            return n.name == modelName;
        }),
        schema = model.jschema,
        record = init_mock_record(modelName);
    // Populate record
    _.forEach(body, function (v, k) {
        if (_.isEmpty(v)) return true;
        // Only check the params starts with model name
        if (k.startsWith(modelName)) {
            // Convert string path to segments, e.g, user.accounts[0].id -> [accounts, 0, id]
            var segments = k.replace(/\[/, '.').replace(/\]/, '').split('.').slice(1); // Remove the model name
            _.set(record, segments, convert_string_to_type(schema, segments, v));
        }
    });
    console.log('Got ' + modelName, record);
    return record;
}

// Perform search by http query
function search_mock_records(modelName, query) {
    var model = _.find(mock_models, function (n) {
            return n.name == modelName;
        }),
        schema = model.jschema,
        mock_records = mock_records_dict[modelName],
        search = {},
        p = parseInt(query.p) || 1,
        offset = (p - 1) * mock_per_page;
    // Perform search
    var chain = _.chain(mock_records);
    _.forEach(query, function (v, k) {
        // Only check the params starts with search and ignore empty value.
        if (!k.startsWith('search.') || _.isEmpty(v)) return true;
        // Remove the search.
        k = k.replace('search.', ''), f = k, c = 'eq';
        // Parse comparators, e.g, name__like, status__in, point__gte
        if (_.includes(f, '__')) {
            var tokens = f.split('__'), f = tokens[0], c = tokens[1];
        }
        // Change string path to segments and convert to typed value
        var segments = f.replace(/\[/, '.').replace(/\]/, '').split('.'), rv = null;
        if (_.isArray(v)) {
            rv = _.map(v, function (vv) {
                return convert_string_to_type(schema, segments, vv);
            })
        } else {
            rv = convert_string_to_type(schema, segments, v)
        }
        // Perform searching, please note it means all the conditions are AND
        if (c == 'eq') {
            chain = chain.filter(function (r) {
                return r[f] == rv;
            });
        } else if (c == 'ne') {
            chain = chain.filter(function (r) {
                return r[f] != rv;
            });
        } else if (c == 'lt') {
            chain = chain.filter(function (r) {
                return r[f] < rv;
            });
        } else if (c == 'lte') {
            chain = chain.filter(function (r) {
                return r[f] <= rv;
            });
        } else if (c == 'gt') {
            chain = chain.filter(function (r) {
                return r[f] > rv;
            });
        } else if (c == 'gte') {
            chain = chain.filter(function (r) {
                return r[f] >= rv;
            });
        } else if (c == 'in') {
            chain = chain.filter(function (r) {
                return _.includes(rv, r[f]);
            });
        } else if (c == 'nin') {
            chain = chain.filter(function (r) {
                return !_.includes(rv, r[f]);
            });
        } else if (c == 'like') {
            chain = chain.filter(function (r) {
                return new RegExp('^' + _.escapeRegExp(v)).test(r[f]); // Only supports startswith match :(
            });
        }
        // Set search for input value displaying
        search[k] = rv;
    });
    // Get under value of chain
    var matched_records = chain.value();
    console.log('Got ' + matched_records.length + ' ' + modelName + (matched_records.length > 1 ? 's' : ''), 'with condition', search);
    var mock_pages = _.ceil(matched_records.length / mock_per_page),
        records = _.drop(matched_records, offset).slice(0, mock_per_page),
        pagination = {
            'page': p,
            'pages': mock_pages,
            'prev': p <= 1 ? null : p - 1,
            'next': p >= mock_pages ? null : p + 1,
            'iter_pages': _.range(1, mock_pages + 1)
        };
    return [search, records, pagination]
}

// Find mock record by id
function find_mock_record_by_id(modelName, id) {
    return _.find(mock_records_dict[modelName], function (r) {
        return r._id == id;
    })
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

// Blog
app.get('/blog/', function (req, res) {
    var ret = search_mock_records('post', req.query), search = ret[0], posts = ret[1], tag = null;
    _.forEach(posts, function (p) {
        decorate_post(p);
    });
    if (_.has(search, 'tids')) {
        tag = find_mock_record_by_id('tag', search['tids'])
    }
    var sorted = _.orderBy(posts, ['createTime'], ['desc']);
    res.render('blog/index.html', {
        search: search, posts: sorted, pagination: ret[2],
        tag: tag, tags: mock_records_dict['tag']
    });
});
app.get('/blog/form/(*)', function (req, res) {
    var postId = req.params[0],
        post = init_mock_record('post');
    if (postId) {
        post = find_mock_record_by_id('post', postId);
        if (!post) {
            res.redirect('/404');
            return;
        }
    }
    res.render('blog/form.html', {post: decorate_post(post), tags: mock_records_dict['tag'], token: gen_qiniu_token()});
});
app.post('/blog/save/(*)', function (req, res) {
    var postId = req.params[0],
        post = polulate_record('post', req.body);
    if (postId) { // Update
        var existing = find_mock_record_by_id('post', postId);
        if (!existing) {
            res.redirect('/404');
            return;
        }
        _.assign(existing, post) // Overwrite the whole record
    } else { // Create
        postId = Mock.mock('@string("number", 24)');
        post._id = postId;
        mock_records_dict['post'].push(post);
    }
    res.json({success: true, message: 'Save successfully.', pid: postId});
});
app.get('/blog/post/:postId', function (req, res) {
    var postId = req.params.postId,
        post = find_mock_record_by_id('post', postId);
    if (!post) {
        res.redirect('/404');
        return;
    }
    res.render('blog/post.html', {post: decorate_post(post), tags: mock_records_dict['tag']});
});
app.post('/blog/comment/:postId', function (req, res) {
    var postId = req.params.postId,
        post = find_mock_record_by_id('post', postId);
    if (!post) {
        res.redirect('/404');
        return;
    }
    var content = req.body.content;
    if (content.trim().length == 0) {
        res.json({success: false, message: 'Content can not be blank!'});
        return;
    }
    var comments = post.comments || [];
    var max = _.max(_.concat([0], _.map(comments, function (c) {
        return c.id;
    })));
    var comment = {
        id: max + 1,
        uid: current_user._id,
        uname: current_user.name,
        uavatar: current_user.avatar,
        content: content,
        time: Mock.mock('@now("yyyy-MM-dd HH:mm:ss.S")')
    };
    comments.unshift(comment);
    post.comments = comments;
    res.json({success: true, message: 'Save comment successfully.'});
});

// Add some properties to post for ui drawing
function decorate_post(post) {
    var author = find_mock_record_by_id('user', post.uid);
    post.author = author;
    if (post.tids) {
        post.tags = _.filter(mock_records_dict['tag'], function (t) {
            return _.includes(post.tids, t._id);
        })
    } else {
        post.tids = [];
    }
    return post;
}

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
app.get('/crud/query/:modelName', function (req, res) {
    var modelName = req.params.modelName,
        model = _.find(mock_models, function (n) {
            return n.name == modelName;
        });
    var ret = search_mock_records(modelName, req.query);
    res.render('crud/query.html', {model: model, search: ret[0], records: ret[1], pagination: ret[2]});
});
app.get('/crud/form/:modelName/(*)', function (req, res) {
    var modelName = req.params.modelName,
        model = _.find(mock_models, function (n) {
            return n.name == modelName;
        }),
        recordId = req.params[0],
        record = init_mock_record(modelName);
    if (recordId) {
        record = find_mock_record_by_id(modelName, recordId);
        if (!record) {
            res.redirect('/404');
            return;
        }
    }
    res.render('crud/form.html', {model: model, record: record, token: gen_qiniu_token()});
});
app.get('/crud/raw/:modelName/(*)', function (req, res) {
    var modelName = req.params.modelName,
        model = _.find(mock_models, function (n) {
            return n.name == modelName;
        }),
        recordId = req.params[0],
        record = init_mock_record(modelName);
    if (recordId) {
        record = find_mock_record_by_id(modelName, recordId);
        if (!record) {
            res.redirect('/404');
            return;
        }
    }
    res.render('crud/raw.html', {model: model, record: record});
});
app.post('/crud/save/:modelName/(*)', function (req, res) {
    var modelName = req.params.modelName,
        mock_records = mock_records_dict[modelName],
        recordId = req.params[0],
        record = polulate_record(modelName, req.body);
    if (recordId) { // Update
        var existing = find_mock_record_by_id(modelName, recordId);
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
    var modelName = req.params.modelName,
        mock_records = mock_records_dict[modelName],
        recordId = req.params.recordId,
        record = find_mock_record_by_id(modelName, recordId);
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
    var modelName = req.params.modelName,
        recordId = req.params.recordId,
        record = find_mock_record_by_id(modelName, recordId);
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