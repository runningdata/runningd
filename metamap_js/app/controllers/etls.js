import Ember from 'ember';
// import ENV from '../config/environment';

export default Ember.Controller.extend({
    // isDatabaseRefreshInProgress: false,
    // etlService: Ember.inject.service('etl'),


    successFunction : function(data) {
            alert('success for ' + data.pang);
    },

    errorFunction : function(data) {
            alert('error for ' + data.pang);
    },

    // initiateETLSync: function() {
    //   // This was required so that the unit test would not stall
    //   if(ENV.environment !== "test") {
    //     Ember.run.later(this, function() {
    //       if (this.get('isDatabaseRefreshInProgress') === false) {
    //         this.syncETLs();
    //         this.initiateETLSync();
    //       }
    //     }, 15000);
    //   }
    // }.on('init'),

    // syncETLs: function() {
    //   this.set('isDatabaseRefreshInProgress', true);
    //   var oldDatabaseNames = this.store.all('etl').mapBy('query');
    //   var self = this;
    //   return this.get('etlService').getETLFromServer().then(function(data) {
    //     // Remove the databases from store which are not in server
    //     data.forEach(function(query) {
    //       if(!oldDatabaseNames.contains(query)) {
    //         self.store.createRecord('etl', {
    //           query: query
    //         });
    //       }
    //     });
    //     // Add the databases in store which are new in server
    //     oldDatabaseNames.forEach(function(query) {
    //       if(!data.contains(query)) {
    //         self.store.find('etl', query).then(function(db) {
    //           self.store.unloadRecord(db);
    //         });
    //       }
    //     });
    //   }).finally(function() {
    //     self.set('isETLRefreshInProgress', false);
    //   });
    // },
    actions : {
       addETL: function(){

          // var name = this.get('name');
          // var sc = this.get('onSchedule');
          Ember.$.ajax('http://192.168.80.128:9090/metamap/yinker', {
            type: 'GET',
           // dataType: 'json',
           data: { sql: "select * from batting" },
           context: this,
           success: this.successFunction,
           error: this.errorFunction
         });
	   console.log('sdfsd');
      }
    }
});


