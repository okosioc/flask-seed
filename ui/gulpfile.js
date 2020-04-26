// Plugins
var gulp = require('gulp'),
    sass = require('gulp-sass'),
    autoprefixer = require('gulp-autoprefixer'), // Add vendor prefixes
    concat = require('gulp-concat'),
    rename = require('gulp-rename'),
    cleancss = require('gulp-clean-css'),// Minify css
    uglify = require('gulp-uglify'), // Minify js
    imagemin = require('gulp-imagemin'), // Compresses PNG, JPEG, GIF and SVG images
    npmdist = require('gulp-npm-dist');

// Paths
const paths = {
    node: './node_modules',
    vendor: './static/assets/vendor',
    scss: {
        dir: './static/assets/scss',
        files: './static/assets/scss/**/*',
        main: './static/assets/scss/*.scss'
    },
    css: {
        dir: './static/assets/css'
    },
    js: {
        dir: './static/assets/js'
    },
    img: {
        dir: './static/assets/img',
        files: './static/assets/img/**/*',
    }
};

// Styles autoprefixing and minification
gulp.task('scss', function () {
    return gulp
        .src(paths.scss.main)
        .pipe(sass().on('error', sass.logError))
        .pipe(autoprefixer())
        .pipe(gulp.dest(paths.css.dir))
        .pipe(cleancss())
        .pipe(rename({suffix: '.min'}))
        .pipe(gulp.dest(paths.css.dir));
});

// Image compression
gulp.task('img', function () {
    return gulp.src(paths.img.files)
        .pipe(imagemin())
        .pipe(gulp.dest(paths.img.dir))
});

// Scripts
gulp.task('scripts', function () {
    // Copy libs from node_modules to vendor folder
    gulp
        .src(npmdist(), {base: paths.node})
        .pipe(gulp.dest(paths.vendor));
    // Merge core libs into vendor.min.js, which will be shared in all pages
    gulp
        .src([
            paths.vendor + "/jquery/dist/jquery.min.js",
            paths.vendor + "/bootstrap/dist/js/bootstrap.bundle.min.js",
            paths.vendor + "/jquery-slimscroll/jquery.slimscroll.min.js",
            paths.vendor + "/node-waves/dist/waves.min.js",
            paths.vendor + "/waypoints/lib/jquery.waypoints.min.js",
            paths.vendor + "/bootstrap4-notify/bootstrap-notify.min.js"

        ])
        .pipe(concat("vendor.min.js"))
        .pipe(gulp.dest(paths.js.dir));
    // Minify app.js
    return gulp
        .src([
            paths.js.dir + "/app.js"
        ])
        .pipe(uglify())
        .pipe(rename({suffix: '.min'}))
        .pipe(gulp.dest(paths.js.dir));
});