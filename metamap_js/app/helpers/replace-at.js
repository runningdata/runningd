import Ember from 'ember';

export function replaceAt(params/*, hash*/) {
  return params[0].replace('@', '___');
}

export default Ember.Helper.helper(replaceAt);
