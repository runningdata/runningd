'use strict';
var ROOT_PATH = require('x-root-path');

var system = require( ROOT_PATH + '/configs/system' ),
    common = require( ROOT_PATH + '/utils/common');


module.exports = function (router) {
    router.get('/list', function (req, res) {
      common.getRequest({
            urlsName:'allETL',
            req: req,
            params: req.query
          }, function (etls) {
            res.render('etls/list', { etls : etls});
          })
    });

    router.get('/add', function (req, res) {
          res.render('etls/edit');
    });

    router.post('/add', function (req, res) {
      common.postFormRequest({
        urlsName: 'addETL',
        req: req,
        form: req.body
      }, function (results) {
        if (results.message == 'success') {
          console.log(req.body.tblName + ' has been added');
          res.redirect("list");
        } else {
          res.send(results);
        }
      });
    });

    router.get('/edit', function (req, res) {
      common.getRequest({
        urlsName:'editETL',
        req: req,
        params: req.query
      }, function (body) {
        body.ctimeFormat = common.formatDateTS(body.ctime, 'yymmdd hh:mm:ss');
        res.render('etls/edit', { etl : body});
      })
    });

};