var ROOT_PATH = require('x-root-path');

var system = require( ROOT_PATH + '/configs/system' ),
    common = require( ROOT_PATH + '/utils/common');

module.exports = function (router) {

        router.get('/', function (req, res) {
          common.getRequest({
            urlsName:'bloodDAG',
            req: req,
            params: req.query
          }, function (bloods) {
            var tempArr = [];
            if (bloods) {
              bloods.forEach(function(blood) {
                if (blood.relatedEtlId == req.query.id) {
                  tempArr.push('style ' + blood.tblName.replace('@','___')  + ' fill:#f9f,stroke:#333,stroke-width:4px;');
                  console.log("got id : " + blood.tblName);
                }
                if (blood.parentTbl.length > 0 && blood.tblName.length > 0) {
                  tempArr.push(blood.parentTbl.replace('@','___')  + '-->'+ blood.tblName.replace('@','___') + ';');
                }
              });
            } else {
              res.render('blood/dag', { bloods : false});
            }
           res.render('blood/dag', { bloods : tempArr.join(' ')});
      });
    });


    router.get('/blood', function (req, res) {
          common.getRequest({
            urlsName:'bloodDAGByName',
            req: req,
            params: req.query
          }, function (bloods) {
            var tempArr = [];
            if (bloods) {
              bloods.forEach(function(blood) {
                if (blood.tblName == req.query.tblName) {
                  tempArr.push('style ' + blood.tblName.replace('@','___')  + ' fill:#f9f,stroke:#333,stroke-width:4px;');
                  console.log("got tblName : " + blood.tblName);
                }
                if (blood.parentTbl.length > 0 && blood.tblName.length > 0) {
                  tempArr.push(blood.parentTbl.replace('@','___')  + '-->'+ blood.tblName.replace('@','___') + ';');
                }
              });
            } else {
              res.render('blood/dag', { bloods : false});
            }
           res.render('blood/dag', { bloods : tempArr.join(' ')});
      });
    });
        
};