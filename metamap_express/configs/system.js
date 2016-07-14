/**
 *
 * 登录相关配置信息
 *
 * @date 2015-04-15 星期三
 /**
 *
 * README:
 *
 * npm start 默认IP及端口取production
 *
 * 增加server参数指定IP及端口号，如：
 * npm start server=testServer
 *
 * name,hostIp及port在serverMap里面添加，如：
 *
 *  {
 *     name: 'testServer',
 *     hostIp: 'http://10.32.62.183',
 *     port: '8417'
 *   }
 *
 * 暂不支持以pm2方式运行，pm2运行时默认取production
 *
 */
'use strict';
var express = require('express');
var url = require('url');
var debug = require('debug')('metamap:configs:system');
var program = require('commander');
/**
 * node端 -> BACKEND JAVA端
 *
 * 通过 process.env.BACKEND 设置
 * 1. :8410 -> localhost:8410
 * 2. @1:8410 -> 测试机1:8410
 * 3. http://foo.com/bar 完整url
 *
 * 不传, 返回默认的线上 BACKEND
 */

var dev = {
  hostIp: 'http://192.168.80.130',
  port: 9090 || 80,
  basePath: '/metamap'
};

var prod = {
  hostIp: 'http://10.0.1.62',
  port: 8080 || 80,
  basePath: '/metamap'
};

program
  .version('0.0.1')
  .option('-e, --environment <string>', 'target environment')
  .parse(process.argv);

var env = program.environment;

var config = prod;
if (env == 'dev') {
  console.log('dev emvironment');
  config = dev;
} else {
  console.log('prod emvironment');
}



module.exports = {

  // server地址
  site: {
    URL: config.siteUrl
  },

  // 后台地址
  service: {
    method: 'GET',
    host: url.parse(config.hostIp).hostname,
    basePath: config.basePath,
    port: config.port,
    headers: {
      'Content-Type': 'application/json'
    }
  },
  config: config
};