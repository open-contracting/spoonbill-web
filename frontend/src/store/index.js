import Vue from 'vue';
import Vuex from 'vuex';

Vue.use(Vuex);

export default new Vuex.Store({
    state: {
        snackbar: {
            opened: false,
            text: null,
            color: null,
        },
    },
    mutations: {
        openSnackbar(state, { text, color }) {
            state.snackbar.text = text;
            state.snackbar.color = color;
            state.snackbar.opened = true;
        },

        closeSnackbar(state) {
            state.snackbar.text = null;
            state.snackbar.color = null;
            state.snackbar.opened = false;
        },
    },
    actions: {},
    modules: {},
});
