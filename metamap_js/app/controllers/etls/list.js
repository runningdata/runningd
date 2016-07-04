import Ember from 'ember';

export default Ember.Controller.extend({
    etls: [],

    init() {
      Ember.$.ajax('http://192.168.80.128:9090/metamap/etl/getAll', {
            type: 'GET',
           context: this,
           success: function(data) {
              this.set('etls', data);
           },
           error: this.errorFunction
         });
      console.log(this.etls);
    }
});
