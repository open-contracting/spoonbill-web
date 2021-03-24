import Vue from 'vue';
import Vuetify from 'vuetify/lib/framework';

Vue.use(Vuetify);

export default new Vuetify({
    theme: {
        themes: {
            light: {
                primary: '#323232',
                accent: '#E0E83D',
                'gray-dark': '#444444',
                'gray-light': '#EEEEEE',
            },
        },
    },
});
