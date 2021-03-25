import Vue from 'vue';
import Vuetify from 'vuetify';

Vue.use(Vuetify);
Vue.config.productionTip = false;

jest.mock('@/services/ApiService', () => {
    return {
        sendFile: jest.fn(() => {
            return {
                data: {
                    id: 'mocked_id',
                },
            };
        }),
    };
});
