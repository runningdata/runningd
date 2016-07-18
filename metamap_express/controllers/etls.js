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

    router.get('/exec_list', function (req, res) {
      common.getRequest({
            urlsName:'executionList',
            req: req,
            params: req.query
          }, function (execs) {
            execs.forEach(function(exec) {
              console.log('end time - > ' + exec.endTime);
              exec.startTimeFormat = common.formatDate(new Date(exec.startTime), 'yymmdd hh:mm:ss');
              exec.endTimeFormat = common.formatDate(new Date(exec.endTime), 'yymmdd hh:mm:ss');
            });
            res.render('etls/exec_list', { execs : execs});
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

    router.get('/exec', function (req, res) {
      common.getRequest({
        urlsName:'execETLScript',
        req: req,
        params: req.query
      }, function (body) {
        res.redirect('/etls/get_exec?id=' + body.exec);
      })
    });

    router.get('/get_exec', function (req, res) {
        // res.render('etls/exec', {
        //     log: req.query.log,
        //     id: req.query.id
        // });
        common.getRequest({
          urlsName:'getExecution',
          req: req,
          params: req.query
        }, function (body) {
          res.render('etls/exec', {
              log: body.logLocation,
              id: body.id
          });
        })
    });

    router.get('/get_log', function (req, res) {
        fs.readFile(req.query.location, 'utf8',function(err, data){
          if (err) throw err;
          res.send({log: data.replace(/\n/g, '<br/>'), status: 1});
        });
    });


};