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
            },
        },
    },
});
