import Vue from 'vue';
import Vuex from 'vuex';
import ApiService from '@/services/ApiService';
import { UPLOAD_STATUSES } from '@/constants';
import router from '@/router';

Vue.use(Vuex);

export default new Vuex.Store({
    state: {
        snackbar: {
            opened: false,
            text: null,
            color: null,
        },
        uploadDetails: null,
        /** @type { WebSocket }*/
        connection: null,
    },
    getters: {
        uploadStatus(state) {
            return state.uploadDetails ? state.uploadDetails.status : null;
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

        setConnection(state, connection) {
            state.connection = connection;
        },

        setUploadDetails(state, payload) {
            if (payload && [UPLOAD_STATUSES.VALIDATION, UPLOAD_STATUSES.QUEUED_VALIDATION].includes(payload.status)) {
                router.push('/select-data?id=' + payload.id).catch(() => {});
            }
            state.uploadDetails = payload;
        },
    },
    actions: {
        async fetchUploadDetails({ commit }, id) {
            try {
                const { data } = await ApiService.getUploadInfo(id);
                commit('setUploadDetails', data);
            } catch (e) {
                if (e.response.status === 404) {
                    commit('openSnackbar', {});
                    router.push('/').catch(() => {});
                }
            }
        },

        setupConnection({ commit, dispatch }, id) {
            const connection = new WebSocket(`${process.env.VUE_APP_WEBSOCKET_URL}/${id}/`);

            connection.onmessage = (event) => {
                if (event.data?.type === 'task.validate') {
                    commit('setUploadDetails', event.data.datasource);
                }
            };

            connection.onerror = (e) => {
                console.error(e);
            };

            connection.onopen = () => {
                commit('setConnection', connection);
                dispatch('fetchUploadDetails', id);
            };
        },

        clearDetails({ commit, state }) {
            if (state.connection) {
                state.connection.close();
                commit('setConnection', null);
            }
            commit('setUploadDetails', null);
        },
    },
    modules: {},
});
