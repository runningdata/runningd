import Ember from 'ember';
import config from './config/environment';

const Router = Ember.Router.extend({
  location: config.locationType
});

Router.map(function() {
  this.route('index');


  this.resource('etls', function() {
    this.route('list');
    this.route('edit', {path: '/edit/:id'});
  });
  
  this.route('tbblood');
  this.route('etls.list');
  this.route('etls.edit');
});

export default Router;
