import Vue from 'vue';
import Vuex from 'vuex';
import ApiService from '@/services/ApiService';
import { FLATTEN_STATUSES, TASK_TYPES, UPLOAD_TYPES } from '@/constants';
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
        tableOrder: [],
    },
    getters: {
        uploadStatus(state) {
            return state.uploadDetails ? state.uploadDetails.status : null;
        },
        isFileFromDataRegistry(state) {
            if (state.uploadDetails) {
                if (state.uploadDetails.author === 'Dataregistry') {
                    return true;
                } else {
                    return false;
                }
            } else {
                return false;
            }
        },
    },
    mutations: {
        openSnackbar(state, { text, color }) {
            state.snackbar.text = text;
            state.snackbar.color = color;
            state.snackbar.opened = true;
        },
        setTableOrder(state, payload) {
            state.tableOrder = payload.split(', ');
        },
        closeSnackbar(state) {
            state.snackbar.text = null;
            state.snackbar.color = null;
            state.snackbar.opened = false;
        },

        setSelections(state, selections) {
            if (selections?.tables && state.tableOrder && state.tableOrder.length > 0) {
                let sortedSelectionTables = [];
                state.tableOrder.forEach((t) => {
                    let selectionTable = selections.tables.find((selTable) => selTable.name === t);
                    selectionTable && sortedSelectionTables.push(selectionTable);
                });
                selections.tables = [...sortedSelectionTables];
            } else {
                if (selections?.tables) {
                    selections.tables.sort((a, b) => {
                        if (a.name < b.name) {
                            return -1;
                        }
                        if (a.name > b.name) {
                            return 1;
                        }
                        return 0;
                    });
                }
            }

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

        setSplitStatus(state, { tableId, value }) {
            const table = state.selections.tables.find((table) => table.id === tableId);
            table.split = value;
        },

        setIncludeStatus(state, { tableId, value }) {
            const table = state.selections.tables.find((table) => table.id === tableId);
            table.include = value;
        },

        setHeadingsType(state, value) {
            state.selections.headings_type = value;
        },

        setFlatten(state, flatten) {
            if (!flatten.status) return;
            const index = state.selections.flattens.findIndex((f) => f.id === flatten.id);
            if (index === -1) {
                state.selections.flattens.push(flatten);
            } else {
                state.selections.flattens[index] = flatten;
            }
            state.selections.flattens = [...state.selections.flattens];
        },
    },
    actions: {
        async fetchSelections({ state, commit }, id) {
            try {
                const res = await ApiService.getSelections(state.uploadDetails.type + 's', state.uploadDetails.id, id);
                commit('setSelections', res.data);
            } catch (e) {
                /* istanbul ignore next */
                console.error(e);
            }
        },

        async updateSplitStatus({ state, commit }, { tableId, value }) {
            try {
                const { data } = await ApiService.changeSplitStatus(
                    state.uploadDetails.type + 's',
                    state.uploadDetails.id,
                    state.selections.id,
                    tableId,
                    value
                );
                commit('setSplitStatus', {
                    tableId,
                    value: data.split,
                });
            } catch (e) {
                /* istanbul ignore next */

                commit('openSnackbar', {
                    text: e?.response?.data?.detail,
                    color: 'error',
                });
                console.error(e);
            }
        },

        async updateIncludeStatus({ state, commit }, { tableId, value }) {
            try {
                const { data } = await ApiService.changeIncludeStatus(
                    state.uploadDetails.type + 's',
                    state.uploadDetails.id,
                    state.selections.id,
                    tableId,
                    value
                );
                commit('setIncludeStatus', {
                    tableId,
                    value: data.include,
                });
            } catch (e) {
                /* istanbul ignore next */
                console.error(e);
            }
        },

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
                commit('setUploadDetails', data);
                if (data.order) {
                    commit('setTableOrder', data.order);
                } else {
                    // FIXME
                    commit(
                        'setTableOrder',
                        'ocid, id, date, tag, initiationType, parties, buyer, planning, ' +
                            'tenders, awards, contracts, language, relatedProcesses, documents, milestones, amendments'
                    );
                }
                data.type = type;
                commit('setUploadDetails', data);
            } catch (e) {
                console.log(e);
                /* istanbul ignore next */
                if (e.response.status === 404) {
                    commit('openSnackbar', {
                        text: 'This linked file is no longer available. Please supply a new URL',
                        color: 'error',
                    });
                    router.push('/').catch(() => {});
                }
            }
        },
        //@ts-ignore
        setupConnection({ commit }, { id, type, onOpen }) {
            let connection;
            if (process.env.VUE_APP_WEBSOCKET_URL.includes('ws:/') || process.env.VUE_APP_WEBSOCKET_URL.includes('wss:/')) {
                connection = new WebSocket(`${process.env.VUE_APP_WEBSOCKET_URL}/${id}/`);
            } else {
                let protocol = window.location.protocol;
                let socketProtocol = 'ws';
                if (protocol.includes('https')) {
                    socketProtocol = 'wss';
                }

                let socketPath = `${socketProtocol}://${window.location.host}/api/ws/${id}/`;
                connection = new WebSocket(socketPath);
            }

            connection.onmessage = (event) => {
                const data = JSON.parse(event.data);
                if (data.progress) {
                    const progress = data.progress.percentage;
                    commit('setDownloadProgress', progress <= 100 ? progress : 100);
                }
                if ([TASK_TYPES.VALIDATE, TASK_TYPES.DOWNLOAD_DATA_SOURCE].includes(data.type)) {
                    commit('setUploadDetails', {
                        ...data.datasource,
                        type,
                    });
                }
                if (data.type === TASK_TYPES.FLATTEN) {
                    if (data.flatten.status === FLATTEN_STATUSES.FAILED) {
                        commit('openSnackbar', {
                            text: data.flatten.error,
                            color: 'error',
                        });
                    }
                    commit('setFlatten', data.flatten);
                }
                if (data.error) {
                    commit('setUploadDetails', {
                        validation: {
                            is_valid: false,
                        },
                        status: 'validation',
                    });
                    // connection.close();
                }
            };

            connection.onerror = (e) => {
                /* istanbul ignore next */
                console.error(e);
            };

            connection.onopen = () => {
                commit('setConnection', connection);
                onOpen && onOpen();
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
