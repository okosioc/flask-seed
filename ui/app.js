const express = require('express');
const nunjucks = require('nunjucks');
const _ = require('lodash');
const querystring = require('querystring');
const app = express();
const port = 3000;
// Use Nunjucks as express template
var env = nunjucks.configure('templates', {
    autoescape: true,
    express: app
});

//
// Compatible with Jinja2's filter
//

// Jinja2's tojson filter
env.addFilter('tojson', env.dump);

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
// Compatible with flask folder structure
//
// Static
app.use('/static', express.static('static'));

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

// Dashboard
app.get('/dashboard/', function (req, res) {
    res.render('dashboard/index.html');
});
app.get('/dashboard/blank', function (req, res) {
    res.render('dashboard/blank.html');
});

// CRUD
app.get('/crud/', function (req, res) {
    res.render('crud/index.html');
});
app.get('/crud/list/:modelName', function (req, res) {
    res.render('crud/list.html');
});
app.get('/crud/form/:modelName/(.*)', function (req, res) {
    res.render('crud/form.html');
});
app.get('/crud/delete/:modelName/:modelId', function (req, res) {
    res.render('crud/delete.html');
});
app.get('/crud/raw/:modelName', function (req, res) {
    res.render('crud/raw.html');
});
app.get('/crud/raw/:modelName/:modelId', function (req, res) {
    res.render('crud/raw.html');
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

// Errors
app.get('/400', function (req, res) {
    res.status(400).render('errors/400.html');
});
app.get('/403', function (req, res) {
    res.status(403).render('errors/403.html');
});
app.get('/500', function (req, res) {
    throw new Error()
});
app.use(function (req, res, next) {
    res.status(404).render('errors/404.html');
});
app.use(function (err, req, res, next) {
    console.error(err.stack);
    res.status(500).render('errors/500.html');
});


//
// Run
//
app.listen(port, () => console.log(`ui is listening on port ${port}!`));