
import Vue from 'vue';
import App from './App.vue';

Vue.config.productionTip = false;

// global mixin to make static files available on the inner objects
// https://stackoverflow.com/a/40897670/8207
Vue.mixin({
  data: function() {
    return {
      staticFiles: STATIC_FILES,  // STATIC_FILES must be defined in the template above vue bundle import.
    };
  }
});


new Vue({
  render: h => h(App),
}).$mount('#object-lifecycle-home')
