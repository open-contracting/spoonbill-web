import Vue from 'vue';
import App from './App.vue';
import router from './router';
import store from './store';
import vuetify from './plugins/vuetify';
import axios from 'axios';
import GetTextPlugin from 'vue-gettext';
import translations from '@/translations/translations.json';
import * as Sentry from '@sentry/vue';

axios.defaults.baseURL = process.env.VUE_APP_API_URL;
Vue.config.productionTip = false;

Sentry.init({
    Vue: Vue,
    dsn: process.env.VUE_APP_SENTRY_DSN,
    logErrors: true,
});

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
