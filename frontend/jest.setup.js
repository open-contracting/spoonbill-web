import Vue from 'vue';
import Vuetify from 'vuetify';

Vue.use(Vuetify);
Vue.config.productionTip = false;

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
