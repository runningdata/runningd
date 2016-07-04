'use strict';

var _ = require('lodash');
var trimLeft = _.trimLeft;
var debug = require('debug')('dolphin:lib:backend');
var parse = require('url').parse;

// 测试机的IP
// 如果IP会变, 就使用域名
var TEST_IPS = exports.TEST_IPS = {
  '1': '10.32.62.183', // test01
  '2': '10.32.99.72', // test02
  '3': '10.32.93.88', // test03
  '4': '10.32.92.34' // test04
};

// 默认线上后端
var DEFAULT_BACKEND = exports.DEFAULT_BACKEND = 'http://host:port/metamap';

/**
 * 获取后端地址
 */
var getBackend = exports._get = function getBackend(backend) {
  if (!backend) {
    return; // return EMPTY
  }

  // 8410 or :8410
  if (/^:?\d+$/.test(backend)) {
    return 'http://127.0.0.1:' + trimLeft(backend, ':') + '/metamap';
  }

  // @1:8410
  if (/^@\d:\d+$/.test(backend)) {
    backend = backend.replace(/^@(\d)(?=:)/g, function(_, n) {
      return TEST_IPS[n];
    });
    backend = 'http://' + backend + '/metamap';
  }

  // 其他, 完整URL
  // TODO: check
  // var p = parse(backend);
  return backend;
};

// backend
exports.BACKEND = DEFAULT_BACKEND;

// process.env.BACKEND 优先于 arg
if (process.env.BACKEND) {
  exports.BACKEND = getBackend(process.env.BACKEND);
} else {

  // node index server=xxx
  var arg = _.find(process.argv, function(arg) {
    return _.startsWith(arg, 'server=');
  });

  if (arg) {
    arg = arg.split(/=/)[1];
    exports.BACKEND = getBackend(arg);
  }
}