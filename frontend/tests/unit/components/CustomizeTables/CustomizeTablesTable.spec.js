import { mount, createLocalVue } from '@vue/test-utils';
import CustomizeTablesTable from '@/components/CustomizeTables/CustomizeTablesTable';
import store from '@/store';
import Vuetify from 'vuetify';
import ApiService from '@/services/ApiService';
import { UPLOAD_TYPES } from '@/constants';

const available_tables = [
    {
        arrays: {
            count: 2,
            threshold: 5,
            below_threshold: ['parties/0/roles'],
            above_threshold: ['tenderer'],
        },
        name: 'parties',
        rows: 5,
        available_data: { columns: { total: 22, available: 18, additional: ['parties/0/identifier/Name'] } },
    },
    {
        arrays: { count: 7, threshold: 5, above_threshold: ['tender/items'] },
        name: 'tenders',
        rows: 11,
        available_data: { columns: { total: 35, available: 34 } },
    },
    {
        arrays: { count: 2, threshold: 5, above_threshold: ['awards/0/suppliers', 'awards/0/items'] },
        available_data: { total: 16, available: 9 },
        name: 'awards',
        rows: 4,
    },
    {
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
            expect(wrapper.vm.arrays.length).toBe(0);
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

            await wrapper.vm.onSplitSwitchChange();
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
    });
});
