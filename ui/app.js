const express = require('express');
const nunjucks = require('nunjucks');
const app = express();
const port = 3000;

// Use nunjucks as express template
var env = nunjucks.configure('templates', {
    autoescape: true,
    express: app
});
// Compatible with jinja2's babel function
env.addGlobal('_', function (str) {
    return str
});
env.addGlobal('current_user', {
    is_authenticated: false,
});

// Static
app.use('/static', express.static('static'));

// Routers
app.get('/', function (req, res) {
    res.render('public/index.html');
});

// Errors
app.use(function (req, res, next) {
    res.status(404).send('404!');
});
app.use(function (err, req, res, next) {
    console.error(err.stack);
    res.status(500).send('500!');
});

app.listen(port, () => console.log(`ui is listening on port ${port}!`));