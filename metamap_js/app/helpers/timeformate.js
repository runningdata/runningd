import Ember from 'ember';
import moment from 'moment';

export function timeformate(params/*, hash*/) {
  return moment(params * 1000).format('YYYY-MM-DD HH:mm:ss');
}

export default Ember.Helper.helper(timeformate);
