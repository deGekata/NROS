import Vue from "vue";
import vuetify from "./plugins/vuetify";
import router from "./router";
import axios from 'axios';

import VueResource from 'vue-resource';
import VueHeadful from 'vue-headful';
import App from "./App";

import store from './store'
// vuex support for old browsers
import 'es6-promise/auto';

import {API_URL} from './constants';

Vue.component('vue-headful', VueHeadful);

Vue.use(VueResource);

Vue.config.productionTip = false;

axios.defaults.baseURL = API_URL;

const token = localStorage.getItem('token');

if (token)
    axios.defaults.headers.common['Authorization'] = token;

new Vue({
    vuetify,
    router,
    store,
    render: h => h(App),
}).$mount("#app");