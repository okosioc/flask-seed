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
    base: './',
    node: './node_modules',
    scss: {
        dir: './static/assets/scss',
        files: './static/assets/scss/**/*',
        main: './static/assets/scss/*.scss'
    },
    css: {
        dir: './static/assets/css',
        files: './static/assets/css/**/*'
    },
    js: {
        dir: './static/assets/js',
        files: './static/assets/js/**/*'
    },
    img: {
        dir: './static/assets/img',
        files: './static/assets/img/**/*',
    },
    vendor: './static/assets/vendor'
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
