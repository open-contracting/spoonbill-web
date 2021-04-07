import store from '@/store';
import { TASK_TYPES, UPLOAD_TYPES } from '@/constants';
import ApiService from '@/services/ApiService';
import WS from 'jest-websocket-mock';

const testSelections = {
    id: 'test id',
    tables: [
        {
            id: 'table-1',
            name: 'b table',
            split: false,
            include: false,
        },
        {
            id: 'table-2',
            name: 'a table',
            split: false,
            include: false,
        },
    ],
};

describe('store', () => {
    describe('mutations', () => {
        test("'openSnackbar' opens snackbar", () => {
            store.commit('openSnackbar', {
                text: 'test',
                color: 'success',
            });
            expect(store.state.snackbar.text).toBe('test');
            expect(store.state.snackbar.color).toBe('success');
            expect(store.state.snackbar.opened).toBe(true);
        });

        test("'openSnackbar' closes snackbar", () => {
            store.commit('closeSnackbar');
            expect(store.state.snackbar.opened).toBe(false);
        });

        test("'setSelections' sets selections with sorted tables", () => {
            store.commit('setSelections', testSelections);
            expect(store.state.selections.id).toBe('test id');
            expect(store.state.selections.tables.length).toBe(2);
            expect(store.state.selections.tables[0].name).toBe('a table');
            expect(store.state.selections.tables[1].name).toBe('b table');

            store.commit('setSelections', null);
            expect(store.state.selections).toBe(null);
        });

        test("'setConnection' sets connections", () => {
            store.commit('setConnection', 'test');
            expect(store.state.connection).toBe('test');
        });

        test("'setUploadDetails' sets info about upload/url", () => {
            store.commit('setUploadDetails', {
                id: 'test id',
            });
            expect(store.state.uploadDetails.id).toBe('test id');
        });

        test("'setDownloadProgress' sets download progress", () => {
            store.commit('setDownloadProgress', 33);
            expect(store.state.downloadProgress).toBe(33);
        });

        test("'increaseNumberOfUploads' increases number of uploads", () => {
            expect(store.state.numberOfUploads).toBe(0);
            store.commit('increaseNumberOfUploads');
            expect(store.state.numberOfUploads).toBe(1);
        });

        test("'setSplitStatus' changes split status of specified table", () => {
            store.commit('setSelections', testSelections);
            store.commit('setSplitStatus', {
                tableId: 'table-2',
                value: true,
            });
            expect(store.state.selections.tables.find((table) => table.id === 'table-2').split).toBe(true);
        });

        test("'setIncludeStatus' changes include status of specified table", () => {
            store.commit('setSelections', testSelections);
            store.commit('setIncludeStatus', {
                tableId: 'table-1',
                value: true,
            });
            expect(store.state.selections.tables.find((table) => table.id === 'table-1').include).toBe(true);
        });
    });

    describe('getters', () => {
        test("'uploadStatus' returns status of job", () => {
            store.commit('setUploadDetails', null);
            expect(store.getters.uploadStatus).toBe(null);
            store.commit('setUploadDetails', {
                status: 'test status',
            });
            expect(store.getters.uploadStatus).toBe('test status');
        });
    });

    describe('actions', () => {
        test("'fetchSelections' fetches selections", async () => {
            store.commit('setUploadDetails', {
                id: 'uploads id',
                type: UPLOAD_TYPES.UPLOAD,
            });
            await store.dispatch('fetchSelections', 'selection id');
            expect(ApiService.getSelections).toBeCalledWith(UPLOAD_TYPES.UPLOAD + 's', 'uploads id', 'selection id');
        });

        test("'updateSplitStatus' sends request to change split status of table", async () => {
            store.commit('setUploadDetails', {
                id: 'uploads id',
                type: UPLOAD_TYPES.UPLOAD,
            });
            store.commit('setSelections', testSelections);
            await store.dispatch('updateSplitStatus', {
                tableId: testSelections.tables[0].id,
                value: true,
            });
            expect(ApiService.changeSplitStatus).toBeCalledWith(
                UPLOAD_TYPES.UPLOAD + 's',
                'uploads id',
                testSelections.id,
                testSelections.tables[0].id,
                true
            );
        });

        test("'updateIncludeStatus' sends request to change include status of table", async () => {
            store.commit('setUploadDetails', {
                id: 'uploads id',
                type: UPLOAD_TYPES.UPLOAD,
            });
            store.commit('setSelections', testSelections);
            await store.dispatch('updateIncludeStatus', {
                tableId: testSelections.tables[0].id,
                value: true,
            });
            expect(ApiService.changeSplitStatus).toBeCalledWith(
                UPLOAD_TYPES.UPLOAD + 's',
                'uploads id',
                testSelections.id,
                testSelections.tables[0].id,
                true
            );
        });

        test("'fetchUploadDetails' fetches detail of upload/url", async () => {
            await store.dispatch('fetchUploadDetails', {
                id: 'upload id',
                type: UPLOAD_TYPES.UPLOAD,
            });
            expect(ApiService.getUploadInfo).toBeCalledWith('upload id');
            expect(store.state.uploadDetails.id).toBe('upload id');
            expect(store.state.uploadDetails.type).toBe(UPLOAD_TYPES.UPLOAD);

            await store.dispatch('fetchUploadDetails', {
                id: 'url id',
                type: UPLOAD_TYPES.URL,
            });
            expect(ApiService.getUploadInfoByUrl).toBeCalledWith('url id');
            expect(store.state.uploadDetails.id).toBe('url id');
            expect(store.state.uploadDetails.type).toBe(UPLOAD_TYPES.URL);
        });

        test("'closeConnection' closes socket connection if exists", () => {
            const connection = {
                close: jest.fn(),
            };
            store.commit('setConnection', connection);
            store.dispatch('closeConnection');
            expect(connection.close).toBeCalledTimes(1);
            expect(store.state.connection).toBe(null);
        });

        test("'setupConnection' opens socket connection and sets up message handlers", async () => {
            const id = 'test id';
            const server = new WS(`${process.env.VUE_APP_WEBSOCKET_URL}/${id}/`);

            await store.dispatch('setupConnection', {
                id,
                type: UPLOAD_TYPES.UPLOAD,
            });

            await server.connected;
            expect(store.state.connection).toBeTruthy();

            await server.send(
                JSON.stringify({
                    progress: 90,
                })
            );
            expect(store.state.downloadProgress).toBe(90);

            await server.send(
                JSON.stringify({
                    type: TASK_TYPES.VALIDATE,
                    datasource: {
                        id: 'received from socket',
                    },
                })
            );
            expect(store.state.uploadDetails.id).toBe('received from socket');
            await server.close();
        });
    });
});
