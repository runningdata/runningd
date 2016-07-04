'use strict';
var request = require('request');
var ROOT_PATH = require('x-root-path');

var system = require( ROOT_PATH + '/configs/system' ),
    common = require( ROOT_PATH + '/utils/common');


module.exports = function (router) {
    router.get('/list', function (req, res) {
      var etls;
      request.get('http://192.168.80.128:9090/metamap/etl/getAll', function (error, response, body) {
        if (!error && response.statusCode == 200) {
          etls =  JSON.parse(body);

          console.log('inner ' + JSON.stringify(etls));
          res.render('etls/list', { etls : etls});
        }
      })
      console.log('outter: ' + JSON.stringify(etls));
    });

    router.get('/add', function (req, res) {
          res.render('etls/add');
    });

    router.post('/add', function (req, res) {
      console.log('bbody---->' + JSON.stringify(req.body.name));
      // var etls;
      // request.get('http://mobile.weather.com.cn/data/forecast/101010100.html?_=1381891660081', function (error, response, body) {
      //   if (!error && response.statusCode == 200) {
      //     etls =  JSON.parse(body);

      //     console.log('inner ' + JSON.stringify(etls));
      //     res.render('etls/add', { etls : etls.f.f1[0]});
      //   }
      // })
      // console.log('outter: ' + JSON.stringify(etls));
      res.redirect("list");
    });

    router.get('/edit', function (req, res) {
      common.getRequest({
        urlsName:'editETL',
        req: req,
        params: req.query
      }, function (body) {
        res.render('etls/edit', { etl : body});
      })
    });

};