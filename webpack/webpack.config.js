var webpack = require('webpack');
var path = require('path');
// var ExtractTextPlugin = require('extract-text-webpack-plugin');
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const UglifyJSPlugin = require('uglifyjs-webpack-plugin');
const OptimizeCssAssetsPlugin = require('optimize-css-assets-webpack-plugin');

module.exports = {
    entry: {
	'app': './js/main.js',
	'styles': './scss/main.scss'
    },
    output: {
	path: path.dirname(__dirname) + '/assets/static/gen',
	filename: '[name].js'
    },
    devtool: '#cheap-module-source-map',
    resolve: {
	modules: ['node_modules'],
	extensions: ['.js']
    },
    optimization: {
	minimizer: [
	    new UglifyJSPlugin({
		cache: true,
		parallel: true,
		sourceMap: true,
	    }),
	    new OptimizeCssAssetsPlugin(),
	]
    },
    module: {
	rules: [
	    { test: /\.js$/, exclude: /node_modules/,
              loader: 'babel-loader' },
	    { test: /\.scss$/,
	      use: [
		  {
		      loader: MiniCssExtractPlugin.loader,
		      options: {
			  publicPath: '../'
		      }
		  },
		  'css-loader',
		  'sass-loader',
	      ]
	    },
	    { test: /\.css$/,
	      loader: 'css-loader' },
	    { test: /\.(woff2?|ttf|eot|svg|png|jpe?g|gif)$/,
              loader: 'file' }
	]
    },
    plugins: [
	new MiniCssExtractPlugin({
	    filename: 'styles.css',
	    chunkFilename: '[id].css',
	}),
    ]
};
