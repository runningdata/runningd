'use strict';
var ROOT_PATH = require('x-root-path'),
    common = require( ROOT_PATH + '/utils/common'),
    fs = require('fs');


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
        body.ctimeFormat = common.formatDate(new Date(body.ctime), 'yymmdd hh:mm:ss');
        res.render('etls/edit', { etl : body});
      })
    });

    router.get('/generate_script', function (req, res) {
      common.getRequest({
        urlsName:'generateEditScript',
        req: req,
        params: req.query
      }, function (body) {
        res.send('successed in location : ' + body.location);
      })
    });

    router.get('/exec', function (req, res) {
      common.getRequest({
        urlsName:'generateEditScript',
        req: req,
        params: req.query
      }, function (body) {
        res.redirect('/etls/get_exec?log=' + body.log + '&id=' + req.query.id);
      })
    });

    router.get('/get_exec', function (req, res) {
        res.render('etls/exec', {
            log: req.query.log,
            id: req.query.id
        });
    });

    router.get('/get_log', function (req, res) {
        fs.readFile(req.query.location, 'utf8',function(err, data){
          if (err) throw err;
          console.log(data);
          res.send({log: data.replace(/\n/g, '<br/>'), status: 1});
        });
    });


};