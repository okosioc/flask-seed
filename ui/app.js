const express = require('express');
const nunjucks = require('nunjucks');
const app = express();
const port = 3000;
// Use nunjucks as express template
var env = nunjucks.configure('templates', {
    autoescape: true,
    express: app
});

//
// Compatible with flask
//

// Jinja2's babel function
env.addGlobal('_', function (str) {
    return str
});
// flask-login
var current_user = {
    is_authenticated: false,
    is_admin: true,
    head: '/static/assets/img/blog/avt-1.jpg',
    name: 'Admin',
};
env.addGlobal('current_user', current_user);

// Static
app.use('/static', express.static('static'));

//
// Routers
//

// Index
app.get('/', function (req, res) {
    res.render('public/index.html');
});

// Dashboard
app.get('/dashboard/', function (req, res) {
    res.render('dashboard/index.html');
});
app.get('/dashboard/blank', function (req, res) {
    res.render('dashboard/blank.html');
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

// Blank
app.get('/blank', function (req, res) {
    res.render('public/blank.html');
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