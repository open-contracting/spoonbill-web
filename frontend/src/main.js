import Vue from 'vue';
import App from './App.vue';
import router from './router';
import store from './store';
import vuetify from './plugins/vuetify';
import axios from 'axios';
import GetTextPlugin from 'vue-gettext';
import translations from '@/translations/translations.json';

axios.defaults.baseURL = process.env.VUE_APP_API_URL;
Vue.config.productionTip = false;

const selectedLanguage = localStorage.getItem('lang');
Vue.use(GetTextPlugin, {
    availableLanguages: {
        en: 'British English',
        es: 'Español',
    },
    defaultLanguage: ['en', 'es'].includes(selectedLanguage) ? selectedLanguage : 'en',
    translations,
    silent: true,
});

new Vue({
    router,
    store,
    vuetify,
    render: (h) => h(App),
}).$mount('#app');
