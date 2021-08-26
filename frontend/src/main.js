import Vue from 'vue';
import App from './App.vue';
import router from './router';
import store from './store';
import vuetify from './plugins/vuetify';
import getQueryParam from '@/utils/getQueryParam';
import axios from 'axios';
import GetTextPlugin from 'vue-gettext';
import translations from '@/translations/translations.json';
import * as Sentry from '@sentry/vue';

const langFromQueryParam = getQueryParam('lang');
const langFromLocalStorage = localStorage.getItem('lang');
const availableLanguages = {
    en_US: 'English',
    es: 'Español',
    ru: 'Russian',
};
const languagesArray = Object.keys(availableLanguages);
let defaultLanguage;
if (langFromQueryParam && languagesArray.includes(langFromQueryParam)) {
    defaultLanguage = langFromQueryParam;
} else if (langFromLocalStorage && languagesArray.includes(langFromLocalStorage)) {
    defaultLanguage = langFromLocalStorage;
} else {
    defaultLanguage = languagesArray[0];
}
Vue.use(GetTextPlugin, {
    availableLanguages,
    defaultLanguage,
    translations,
    silent: true,
});

axios.defaults.headers.common['Accept-Language'] = defaultLanguage;
axios.defaults.baseURL = process.env.VUE_APP_API_URL;
axios.interceptors.response.use(
    function (response) {
        return response;
    },
    function (error) {
        if (error.message === 'Network Error') {
            store.commit('openSnackbar', {
                text: Vue.prototype.$gettext('Network Error'),
                color: 'error',
            });
        }
        return Promise.reject(error);
    }
);
Vue.config.productionTip = false;

Sentry.init({
    Vue: Vue,
    dsn: process.env.VUE_APP_SENTRY_DSN,
    logErrors: true,
});

Vue.prototype.$error = (e) => {
    if (Array.isArray(e)) {
        store.commit('openSnackbar', {
            text: e[0],
            color: 'error',
        });
    } else {
        console.error(e);
        if (e?.response?.data?.detail) {
            store.commit('openSnackbar', {
                text: e.response.data.detail,
                color: 'error',
            });
        }
    }
};

new Vue({
    router,
    store,
    vuetify,
    render: (h) => h(App),
}).$mount('#app');
