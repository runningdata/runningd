import Model from 'ember-data/model';
import attr from 'ember-data/attr';
// import { belongsTo, hasMany } from 'ember-data/relationships';

export default Model.extend({
    query: attr('string'),
    meta: attr(),
    id: attr(),
    tblName: attr(),
    author: attr(),
    preSql: attr(),
    onSchedule: attr(),
    ctime: attr(),
    utime: attr(),
    priority: attr()
});
