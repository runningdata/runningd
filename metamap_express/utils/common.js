/**
 * 常规请求的一些处理方法封装
 * @date 2015-05-05
 */

'use strict';
var mock    = require('./mock'),
    urls    = require('./urls'),
    request = require('request'),
    config = require('../configs/system'),
    querystring = require('querystring');

var Common = function () {};
var proto = Common.prototype;


/**
 *
 * @params req
 * @params res
 * @params data 获取到的数据
 * @params template  渲染的模版
 */
proto.renderTemplate = function (req, res, data, template) {
  var templtData = data["data"],
    code = data["code"];
  if (code == 1) {
    //todo data.code 为1 时后台错误处理
  }
  res.render(template, templtData);

};

/**
 *
 * @params destination
 * @params source
 */
proto.extend = function (destination, source) {
  for (var property in source) {
    if (source[property] != undefined)
      destination[property] = source[property];
  }
  return destination;
}

/**
 * @params
 * @type {Common}
 */
proto.isEmptyObj = function (obj) {
  var name;
  for (name in obj) {
    return false;
  }
  return true;
}

/**
 * 参数包装（准备删除）
 * @param query
 * @returns {string}
 */
proto.formatQuery = function (query) {
  var path = "?";
  for (i in query) {
    if (i != "uid")
      path += i + "=" + query[i] + "&";
  }
  return path;
}

/**
 * [formatDate description]
 * @param  {[type]} date   [日期类型数据]
 * @param  {[type]} params [格式化字符串]
 * @return {[type]}        [String]
 */
proto.formatDate = function (date, params) {
  var date = date || new Date(),
    dateStr = "";
  switch (params) {
    case "yymmdd":
      dateStr += date.getFullYear() + (date.getMonth() > 9 ? "" : "0") + (date.getMonth() + 1) + (date.getDate());
      break;
  }
  return dateStr;
}

/**
 *后台get请求包装
 * @param options
 * @param callback
 */
proto.getRequest = function (options, callback) {

  var default0 = {
    method: 'GET',
    url: ''
  }, params, urlsObj;
  var opts = this.extend(default0, options);

  if (options.urlsName) {
    urlsObj = urls[options.urlsName];
    if (urlsObj.ifMock) {
      mock(options, callback);
      return;
    }

    params = opts.params;
    if(opts.req ){
      // console.log(opts.req.session.user.id);
      // params = this.extend({uid: opts.req.session.user.id}, opts.params);
      params = opts.params;
    }

    opts.url = "http://" + config.service.host + ':' +
                config.service.port  +
                (config.service.basePath ? config.service.basePath : '')+  urlsObj.path + '?' +
                querystring.stringify(params);
  }
  console.log("get服务器:" +  opts.url);
  request(opts, function (error, response, body) {
    if (!error && response.statusCode === 200){
      if(typeof body === 'string'){
        try{
          // may not be json
          body = JSON.parse(body);
        } catch(e) { 
          // it's not json
          // so we can think it's server error
          return callback && callback({code:1, data:null, msg:'server error'});
        }
      }
      callback && callback(body);
    }
    else{
      callback && callback({code:1, data:null, msg:'server error'});
    }
  });
}

/**
 * 后台post请求包装
 * @param options
 * @param callback
 */
proto.postRequest = function(options, callback){
  var default0 = {
    headers: {'content-type' : 'application/json'},
    method: 'POST',
    uri: '',
    json:true,
    body: {}
  };
  var opts = this.extend(default0, options);

  if(options.urlsName){
    var urlsObj = urls[options.urlsName];
    opts.url = "http://" + config.service.host + ':' +
                config.service.port  +
                (config.service.basePath ? config.service.basePath : '')+  urlsObj.path ;
    if(urlsObj.ifMock){
      mock(options, callback);
      return;
    }
  }
  if(opts.req ){
    opts.body = this.extend({uid: opts.req.session.user.id}, opts.body);
  }

  console.log("post服务器:" +  opts.url + "  上传数据：");
  console.log(opts.body);
  request.post(opts, function (error, response, body) {
    if (!error && response.statusCode === 200){
      body = typeof body == 'string' ? JSON.parse(body) : body;
      console.log(body);
      callback && callback(body);
    }
    else{
      callback && callback({code:1, data:null, msg:'server error'});
    }
  });
}

/**
 * 后台post form请求包装
 * @param options
 * @param callback
 */
proto.postFormRequest = function(options, callback){
  var default0 = {
    headers: {'Content-Type' : 'application/x-www-form-urlencoded'},
    form: {}
  };
  var opts = this.extend(default0, options);

  if(options.urlsName){
    var urlsObj = urls[options.urlsName];
    opts.url = "http://" + config.service.host + ':' +
    config.service.port  +
    (config.service.basePath ? config.service.basePath : '') +  urlsObj.path ;
    if(urlsObj.ifMock){
      mock(options, callback);
      return;
    }
  }
  if(opts.req ){
    opts.form = this.extend({uid: opts.req.session.user.id}, opts.form);
  }

  console.log("post form服务器:" +  opts.url + "  上传数据：");
  console.log(opts.form);
  request.post(opts, function (error, response, body) {
    if (!error && response.statusCode === 200){
      body = typeof body == 'string' ? JSON.parse(body) : body;
      console.log(body);
      callback && callback(body);
    }
    else{
      callback && callback({code:1, data:null, msg:'server error'});
    }
  });
}

module.exports =  new Common();