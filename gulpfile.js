// Plugins
var gulp = require('gulp'),
    sass = require('gulp-sass'),
    autoprefixer = require('gulp-autoprefixer'),
    cssnano = require('gulp-cssnano'),
    concat = require('gulp-concat'),
    rename = require('gulp-rename'),
    plumber = require('gulp-plumber'),
    uglify = require('gulp-uglify'),
    imagemin = require('gulp-imagemin'),
    lodash = require("lodash");

// Relative paths
var pathsConfig = function () {
    var appRoot = "./app", vendorsRoot = "./node_modules";

    return {
        app: appRoot,
        templates: appRoot + '/templates',
        css: appRoot + '/static/css',
        sass: appRoot + '/static/scss',
        fonts: appRoot + '/static/fonts',
        images: appRoot + '/static/img',
        js: appRoot + '/static/js',
        srcJs: appRoot + '/static/js/src',
        bootstrapSass: vendorsRoot + "/bootstrap/scss",
        vendorsJs: [ // This vendors will be shared in the whole project
            vendorsRoot + "/jquery/dist/jquery.js",
            vendorsRoot + "/bootstrap/dist/js/bootstrap.bundle.js",
            vendorsRoot + "/jquery-slimscroll/jquery.slimscroll.js",
            vendorsRoot + "/node-waves/dist/waves.js",
            vendorsRoot + "/waypoints/lib/jquery.waypoints.js",
            vendorsRoot + "/parsleyjs/dist/parsley.js",
            vendorsRoot + "/bootstrap4-notify/bootstrap-notify.js"
        ],
    }
};

var paths = pathsConfig();

// Styles autoprefixing and minification
function styles() {
    gulp.src(paths.sass + '/bootstrap.scss')
        .pipe(sass({
            includePaths: [
                paths.bootstrapSass,
                paths.sass
            ]
        }).on('error', sass.logError))
        .pipe(plumber()) // Checks for errors
        .pipe(autoprefixer()) // Adds vendor prefixes
        .pipe(gulp.dest(paths.css))
        .pipe(rename({suffix: '.min'}))
        .pipe(cssnano()) // Minifies the result
        .pipe(gulp.dest(paths.css));

    gulp.src(paths.sass + '/icons.scss')
        .pipe(sass({
            includePaths: [
                paths.bootstrapSass,
                paths.sass
            ]
        }).on('error', sass.logError))
        .pipe(plumber())
        .pipe(autoprefixer())
        .pipe(gulp.dest(paths.css))
        .pipe(rename({suffix: '.min'}))
        .pipe(cssnano())
        .pipe(gulp.dest(paths.css));

    return gulp.src(paths.sass + '/app.scss')
        .pipe(sass({
            includePaths: [
                paths.bootstrapSass,
                paths.sass
            ]
        }).on('error', sass.logError))
        .pipe(plumber())
        .pipe(autoprefixer())
        .pipe(gulp.dest(paths.css))
        .pipe(rename({suffix: '.min'}))
        .pipe(cssnano())
        .pipe(gulp.dest(paths.css));
}


// Javascript minification
function scripts() {
    var allJs = lodash.union(paths.vendorsJs, [paths.srcJs + '/app.js']);

    return gulp.src(allJs)
        .pipe(concat('app.js'))
        .pipe(gulp.dest(paths.js))
        .pipe(plumber()) // Checks for errors
        .pipe(uglify()) // Minifies the js
        .pipe(rename({suffix: '.min'}))
        .pipe(gulp.dest(paths.js));
}

// Image compression
function imgCompression() {
    return gulp.src(paths.images + '/*')
        .pipe(imagemin()) // Compresses PNG, JPEG, GIF and SVG images
        .pipe(gulp.dest(paths.images))
}


var generateAssets = gulp.parallel(
    gulp.series(styles, scripts),
    imgCompression
);

// Commands
exports["styles"] = styles;
exports["scripts"] = scripts;
// Default generate assets
exports.default = generateAssets, exports["build"] = generateAssets;
