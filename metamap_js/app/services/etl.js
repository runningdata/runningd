import Ember from 'ember';

export default Ember.Service.extend({
    // etls:[],

    // init: function () {
    //   this._super();
    //   var baseUrl = "http://192.168.80.128:9090/metamap/etl/getAll";
    //   this.set('baseUrl', baseUrl);
    // },

    // getETLFromServer: function() {
    //     var defer = Ember.RSVP.defer();
    //     var url = this.get('baseUrl');
    //     Ember.$.getJSON(url).then(function(data) {
    //       defer.resolve(data.databases);
    //     }, function(err) {
    //       defer.reject(err);
    //     });
    //     return defer.promise;
    // } 
});
