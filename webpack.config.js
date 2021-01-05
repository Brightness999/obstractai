const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const VueLoaderPlugin = require('vue-loader/lib/plugin');

module.exports = {
  entry: {
    site: './assets/site.js',  // required for bulma sass/css styles
    app: './assets/javascript/app.js',
    teams: './assets/javascript/teams.js',
    pegasus: './assets/javascript/pegasus/pegasus.js',
    home: './assets/javascript/project/index.js',
    'react-object-lifecycle': './assets/javascript/pegasus/examples/react/react-object-lifecycle.js',
    'vue-object-lifecycle': './assets/javascript/pegasus/examples/vue/vue-object-lifecycle.js',
  },
  output: {
    path: path.resolve(__dirname, './static'),
    filename: 'js/[name]-bundle.js',
    library: ["SiteJS", "[name]"],
  },
  module: {
    rules: [
      {
        test: /\.vue$/,
        loader: 'vue-loader'
      },
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        loader: "babel-loader",
        options: { presets: ["@babel/env"] }
      },
      {
        test: /\.scss$/,
        use: [
          MiniCssExtractPlugin.loader,
          'css-loader',
          'sass-loader',
        ],
      },
    ]
  },
  plugins: [
    new MiniCssExtractPlugin({
      'filename': 'css/[name].css',
    }),
    new VueLoaderPlugin(),
  ]
};
