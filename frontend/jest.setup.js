import Vue from 'vue';
import Vuetify from 'vuetify';
import GetTextPlugin from 'vue-gettext';
import translations from '@/translations/translations.json';

Vue.use(Vuetify);
Vue.config.productionTip = false;

Vue.use(GetTextPlugin, {
    availableLanguages: {
        en: 'British English',
        es: 'Español',
    },
    defaultLanguage: 'en',
    translations,
    silent: true,
});

jest.mock('@/services/ApiService', () => {
    return {
        sendFile: jest.fn(() => {
            return new Promise((resolve) => {
                setTimeout(() => {
                    resolve({
                        data: {
                            id: 'mocked_id',
                        },
                    });
                }, 100);
            });
        }),
        sendUrl: jest.fn(() => {
            return new Promise((resolve) => {
                setTimeout(() => {
                    resolve({
                        data: {
                            id: 'mocked_id',
                        },
                    });
                }, 100);
            });
        }),
    };
});
