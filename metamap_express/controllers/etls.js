'use strict';
var ROOT_PATH = require('x-root-path');

var system = require( ROOT_PATH + '/configs/system' ),
    worker = require('child_process'),
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
        worker.exec("hive -e " + body.location + " > " + body.location +".log 2>&1", { 
          encoding: 'utf8',
          timeout: 0, /*子进程最长执行时间 */
          // maxBuffer: 200*1024,  /*stdout和stderr的最大长度*/
          killSignal: 'SIGTERM',
          cwd: null,
          env: null
        }); 
        res.render('etls/exec', {
          log: body.location + ".log",
          id: req.query.id
            });
      })
    });

    router.get('/get_log', function (req, res) {
      worker.exec("cat " + req.query.location, function (error, stdout, stderr) {
        console.log('stderr : ' + stderr);
        console.log('stdout : ' + stdout);
        console.log('error : ' + error);
        // res.render('etls/log', {stdout : stdout, log : req.query.location});
        res.send({log: stdout.replace(/\n/g, '<br/>'), status: 1});
      }); 
    });


};