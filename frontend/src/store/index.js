import Vue from 'vue';
import Vuex from 'vuex';
import ApiService from '@/services/ApiService';
import { TASK_TYPES, UPLOAD_TYPES } from '@/constants';
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
        selections: null,

        /** @type { WebSocket }*/
        connection: null,

        downloadProgress: -1,
        numberOfUploads: 0,
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

        setSelections(state, selections) {
            state.selections = selections;
        },

        setConnection(state, connection) {
            state.connection = connection;
        },

        setUploadDetails(state, payload) {
            state.uploadDetails = payload;
        },

        setDownloadProgress(state, progress) {
            state.downloadProgress = progress;
        },

        increaseNumberOfUploads(state) {
            state.numberOfUploads++;
        },
    },
    actions: {
        async fetchUploadDetails({ commit }, { id, type }) {
            try {
                let data = null;
                if (type === UPLOAD_TYPES.UPLOAD) {
                    const res = await ApiService.getUploadInfo(id);
                    data = res.data;
                } else {
                    const res = await ApiService.getUploadInfoByUrl(id);
                    data = res.data;
                }
                data.type = type;
                commit('setUploadDetails', data);
            } catch (e) {
                if (e.response.status === 404) {
                    router.push('/').catch(() => {});
                }
            }
        },

        setupConnection({ commit, dispatch }, { id, type }) {
            const connection = new WebSocket(`${process.env.VUE_APP_WEBSOCKET_URL}/${id}/`);

            connection.onmessage = (event) => {
                const data = JSON.parse(event.data);
                if (data.progress) {
                    commit('setDownloadProgress', data.progress);
                }
                if ([TASK_TYPES.VALIDATE, TASK_TYPES.DOWNLOAD_DATA_SOURCE].includes(data.type)) {
                    commit('setUploadDetails', {
                        ...data.datasource,
                        type,
                    });
                }
            };

            connection.onerror = (e) => {
                console.error(e);
            };

            connection.onopen = () => {
                commit('setConnection', connection);
                dispatch('fetchUploadDetails', { id, type });
            };
        },

        closeConnection({ state, commit }) {
            if (state.connection) {
                state.connection.close();
                commit('setConnection', null);
            }
        },
    },
    modules: {},
});
