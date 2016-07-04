import Ember from 'ember';

export default Ember.Controller.extend({
    tbbloods1: [],
    tbbloods2: '',


    init() {
      Ember.$.ajax('http://192.168.80.128:9090/metamap/etl/getMermaid?tblName=mymeta@my_table', {
            type: 'GET',
           context: this,
           success: function(data) {
                var tempArr = [];
                tempArr.push('<div class="mermaid">');
                tempArr.push('graph TD;');
                for (var i = data.length - 1; i >= 0; i--) {
                    if (data[i].parentTbl) {
                        tempArr.push(data[i].parentTbl.replace('@','___') + '-->' + data[i].tblName.replace('@','___')+';');
                    }
                }
                tempArr.push('</div>');
              this.set('tbbloods2', tempArr.join('\n'));

              this.set('tbbloods1', data);
           },
           error: this.errorFunction
         });
    }
});
