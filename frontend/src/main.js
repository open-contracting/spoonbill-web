import Vue from 'vue';
import App from './App.vue';
import router from './router';
import store from './store';
import vuetify from './plugins/vuetify';
import axios from 'axios';
import GetTextPlugin from 'vue-gettext';
import translations from '@/translations/translations.json';
import * as Sentry from '@sentry/vue';

const selectedLanguage = localStorage.getItem('lang');
const availableLanguages = {
    en_US: 'English',
    es: 'Español',
};
const languagesArray = Object.keys(availableLanguages);
Vue.use(GetTextPlugin, {
    availableLanguages,
    defaultLanguage: languagesArray.includes(selectedLanguage) ? selectedLanguage : languagesArray[0],
    translations,
    silent: true,
});

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
    console.error(e);
    if (e?.response?.data?.detail) {
        store.commit('openSnackbar', {
            text: e.response.data.detail,
            color: 'error',
        });
    }
};

new Vue({
    router,
    store,
    vuetify,
    render: (h) => h(App),
}).$mount('#app');
