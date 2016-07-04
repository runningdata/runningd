'use strict';

module.exports = function (router) {
  router.get('/', function (req, resp) {
    resp.redirect('/etls/list');
  });
};