import { mount, createLocalVue } from '@vue/test-utils';
import CustomizeTablesTable from '@/components/CustomizeTables/CustomizeTablesTable';
import store from '@/store';
import Vuetify from 'vuetify';
import ApiService from '@/services/ApiService';
import { UPLOAD_TYPES } from '@/constants';
import router from '@/router';

const available_tables = [
    {
        arrays: {},
        name: 'parties',
        rows: 5,
        available_data: { columns: { total: 22, available: 18, additional: ['parties/0/identifier/Name'] } },
    },
    {
        arrays: { one: 'one', two: 'two' },
        name: 'tenders',
        rows: 11,
        available_data: { columns: { total: 35, available: 34 } },
    },
    {
        arrays: { one: 'one', two: 'two' },
        available_data: { total: 16, available: 9 },
        name: 'awards',
        rows: 4,
    },
    {
        arrays: {},
        available_data: {
            total: 10,
            available: 10,
            additional: ['documents/0/datePublished', 'documents/0/...'],
        },
        name: 'documents',
        rows: 5,
    },
];

describe('CustomizeTablesTable.vue', () => {
    const localVue = createLocalVue();
    const vuetify = new Vuetify();

    describe('methods', () => {
        test("'getTablePreview' gets tables preview", async () => {
            store.commit('setUploadDetails', {
                id: 'test id',
                type: UPLOAD_TYPES.UPLOAD,
                available_tables,
            });
            await store.dispatch('fetchSelections', 'test id');
            const wrapper = mount(CustomizeTablesTable, {
                localVue,
                vuetify,
                store,
                propsData: {
                    table: {
                        id: 'tenders-table',
                        name: 'tenders',
                    },
                },
            });

            await wrapper.vm.getTablePreview('tenders-table');
            expect(wrapper.vm.tables.length).toBe(2);
            expect(ApiService.getTablePreview).toBeCalledTimes(2);
            expect(wrapper.vm.availableData.length).toBe(1);
            expect(wrapper.vm.arrays.length).toBe(1);

            await wrapper.setProps({
                table: {
                    id: 'awards-table',
                    name: 'awards',
                },
            });
            expect(wrapper.vm.availableData.length).toBe(0);
            expect(wrapper.vm.arrays.length).toBe(1);

            await wrapper.setProps({
                table: {
                    id: 'documents-table',
                    name: 'documents',
                },
            });
            expect(wrapper.vm.availableData.length).toBe(0);
            expect(wrapper.vm.arrays.length).toBe(1);

            await wrapper.setProps({
                table: {
                    id: 'parties-table',
                    name: 'parties',
                },
            });
            expect(wrapper.vm.availableData.length).toBe(3);
            expect(wrapper.vm.arrays.length).toBe(1);
        });

        test("'onSplitSwitchChange' changes split status of table", async () => {
            jest.clearAllMocks();
            store.commit('setUploadDetails', {
                id: 'test id',
                type: UPLOAD_TYPES.UPLOAD,
                available_tables,
            });
            await store.dispatch('fetchSelections', 'test id');
            const wrapper = mount(CustomizeTablesTable, {
                localVue,
                vuetify,
                store,
                propsData: {
                    table: {
                        id: 'tenders-table',
                        name: 'tenders',
                    },
                },
            });

            await wrapper.vm.onSplitSwitchChange(true);
            expect(ApiService.changeSplitStatus).toHaveBeenCalledTimes(1);
            expect(ApiService.getTablePreview).toBeCalledTimes(2);
            expect(store.state.selections.tables.find((table) => table.id === 'tenders-table').split).toBe(true);
        });

        test("'changeIncludeStatus' changes include status of table", async () => {
            jest.clearAllMocks();
            store.commit('setUploadDetails', {
                id: 'test id',
                type: UPLOAD_TYPES.UPLOAD,
                available_tables,
            });
            await store.dispatch('fetchSelections', 'test id');
            const wrapper = mount(CustomizeTablesTable, {
                localVue,
                vuetify,
                store,
                propsData: {
                    table: {
                        id: 'tenders-table',
                        name: 'tenders',
                    },
                },
            });

            const table = { id: 'test id', include: true };
            await wrapper.vm.changeIncludeStatus(table, false);
            expect(ApiService.changeIncludeStatus).toHaveBeenCalledTimes(1);
            expect(table.include).toBe(false);
        });

        test("'removeTable' changes include status of table after confirmation", async () => {
            jest.clearAllMocks();
            store.commit('setUploadDetails', {
                id: 'test id',
                type: UPLOAD_TYPES.UPLOAD,
                available_tables,
            });
            await store.dispatch('fetchSelections', 'test id');
            const wrapper = mount(CustomizeTablesTable, {
                localVue,
                vuetify,
                store,
                propsData: {
                    table: {
                        id: 'tenders-table',
                        name: 'tenders',
                    },
                },
            });

            let table = { id: 'test id', include: true };
            wrapper.vm.$root.openConfirmDialog = jest.fn().mockImplementation(() => Promise.resolve(true));
            await wrapper.vm.removeTable(table);
            expect(ApiService.changeIncludeStatus).toHaveBeenCalledTimes(1);
            expect(table.include).toBe(false);

            table = { id: 'test id', include: true };
            wrapper.vm.$root.openConfirmDialog = jest.fn().mockImplementation(() => Promise.resolve(false));
            await wrapper.vm.removeTable(table);
            expect(ApiService.changeIncludeStatus).toHaveBeenCalledTimes(1);
            expect(table.include).toBe(true);
        });

        test("'removeMainTable' changes include status of main table after confirmation", async () => {
            jest.clearAllMocks();
            router.push = jest.fn();
            store.commit('setUploadDetails', {
                id: 'test id',
                type: UPLOAD_TYPES.UPLOAD,
                available_tables,
            });
            await store.dispatch('fetchSelections', 'test id');
            const wrapper = mount(CustomizeTablesTable, {
                localVue,
                vuetify,
                store,
                router,
                propsData: {
                    table: {
                        id: 'awards-table',
                        name: 'awards',
                    },
                },
            });
            store.state.selections.tables.slice(1).forEach((table) => {
                table.include = false;
            });
            wrapper.vm.$root.openConfirmDialog = jest.fn().mockImplementation(() => Promise.resolve(true));
            await wrapper.vm.removeMainTable();
            expect(ApiService.changeIncludeStatus).toHaveBeenCalledTimes(0);
            expect(router.push).toHaveBeenCalledTimes(1);

            wrapper.vm.$root.openConfirmDialog = jest.fn().mockImplementation(() => Promise.resolve(false));
            await wrapper.vm.removeMainTable();
            expect(ApiService.changeIncludeStatus).toHaveBeenCalledTimes(0);
            expect(router.push).toHaveBeenCalledTimes(1);

            wrapper.vm.$root.openConfirmDialog = jest.fn().mockImplementation(() => Promise.resolve(true));
            store.state.selections.tables[1].include = true;
            await wrapper.vm.removeMainTable();
            expect(ApiService.changeIncludeStatus).toHaveBeenCalledTimes(1);
            expect(router.push).toHaveBeenCalledTimes(1);
        });
    });
});
