// Plugins
var gulp = require('gulp'),
    sass = require('gulp-sass'),
    autoprefixer = require('gulp-autoprefixer'), // Add vendor prefixes
    concat = require('gulp-concat'),
    rename = require('gulp-rename'),
    cleancss = require('gulp-clean-css'),// Minify css
    uglify = require('gulp-uglify'), // Minify js
    npmdist = require('gulp-npm-dist');

// Paths
const paths = {
    node: './node_modules',
    vendor: './app/static/assets/vendor',
    scss: {
        dir: './app/static/assets/scss',
        main: './app/static/assets/scss/*.scss'
    },
    css: {
        dir: './app/static/assets/css'
    },
    js: {
        dir: './app/static/assets/js'
    },
    appjs: {
        dir: './app/static/js'
    }
};

// Styles
gulp.task('styles', function () {
    // Scss -> autoprefixer -> cleancss -> min
    return gulp
        .src(paths.scss.main)
        .pipe(sass().on('error', sass.logError))
        .pipe(autoprefixer())
        .pipe(gulp.dest(paths.css.dir))
        .pipe(cleancss())
        .pipe(rename({suffix: '.min'}))
        .pipe(gulp.dest(paths.css.dir));
});

// Scripts
gulp.task('scripts:copy', function () {
    // Copy libs from node_modules to vendor folder
    gulp
        .src(npmdist(), {base: paths.node})
        .pipe(gulp.dest(paths.vendor));
    // Copy special libs that gulp-npm-dist can not handle
    return gulp
        .src([
            paths.node + "/moment/min/*",
        ], {base: paths.node})
        .pipe(gulp.dest(paths.vendor));
});
gulp.task('scripts:merge', function () {
    // Merge core libs into vendor.min.js, which will be shared in all pages
    gulp
        .src([
            paths.vendor + "/jquery/dist/jquery.min.js",
            paths.vendor + "/bootstrap/dist/js/bootstrap.bundle.min.js",
            paths.vendor + "/bootstrap4-notify/bootstrap-notify.min.js"
        ])
        .pipe(concat("vendor.min.js"))
        .pipe(gulp.dest(paths.js.dir));
    // Minify app.js & form.js
    return gulp
        .src([
            paths.appjs.dir + "/app.js",
            paths.appjs.dir + "/form.js"
        ])
        .pipe(uglify())
        .pipe(rename({suffix: '.min'}))
        .pipe(gulp.dest(paths.appjs.dir));
});
gulp.task('scripts', gulp.series('scripts:copy', 'scripts:merge'));

// Build command
gulp.task('build', gulp.parallel(
    'styles',
    'scripts'
));
