import Vue from 'vue';
import Vuetify from 'vuetify/lib/framework';

Vue.use(Vuetify);

export default new Vuetify({
    theme: {
        themes: {
            light: {
                primary: '#444444',
                darkest: '#323232',
                accent: '#E0E83D',
                'gray-dark': '#DADADA',
                'gray-light': '#EEEEEE',
                error: '#FF9393',
                'error-light': '#FFE8E8',
                success: '#71B604',
                'success-light': '#F0F8E5',
                'success-notification': '#25B2A7',
                'error-notification': '#F44336',
                'moody-blue': '#6C75E1',
            },
        },
    },
});
