/**
 * 用假数据模拟对后台的请求
 * @author GUOQING07
 * @date 20150602
 */
var urls = require('./urls');
var request = require('request');
var fs = require('fs');


module.exports = function(options, callback){
  var data = {
    code: 1,
    data: null,
    msg: "test ERROR"
  };
  var path;

  if(options.urlsName){
  //  //读取json文件 urls.urlsName.mock_data
   var urlsObj = urls[options.urlsName];

    data = fs.readFile(urlsObj.mock_data,'utf-8', function(err, data){
      //var json = require('../' + urlsObj.mock_data);
      callback && callback(JSON.parse(data));
    });

  }

}