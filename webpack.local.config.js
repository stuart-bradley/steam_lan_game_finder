var path = require("path");
var webpack = require('webpack');
var BundleTracker = require('webpack-bundle-tracker');

var config = require('./webpack.base.config.js');


// override django's STATIC_URL for webpack bundles
config.output.publicPath = 'http://127.0.0.1:8000/assets/bundles/';

module.exports = config;