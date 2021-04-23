import { shallowMount, createLocalVue } from '@vue/test-utils';
import EditHeadingsTables from '@/components/EditHeadings/EditHeadingsTables';
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

describe('EditHeadingsTables.vue', () => {
    const localVue = createLocalVue();
    const vuetify = new Vuetify();

    describe('methods', () => {
        test("'getAllPreviews' gets previews for all tables", async () => {
            store.commit('setUploadDetails', {
                id: 'test id',
                type: UPLOAD_TYPES.UPLOAD,
                available_tables,
            });
            await store.dispatch('fetchSelections', 'test id');
            const wrapper = shallowMount(EditHeadingsTables, {
                localVue,
                vuetify,
                store,
                propsData: {
                    table: {
                        id: 'tenders table',
                        name: 'tenders',
                    },
                    headingsType: 'ocds',
                },
            });

            jest.clearAllMocks();
            await wrapper.vm.getAllPreviews();
            expect(ApiService.getTablePreview).toBeCalledTimes(4);
        });

        test("'getTablePreview' gets tables preview", async () => {
            store.commit('setUploadDetails', {
                id: 'test id',
                type: UPLOAD_TYPES.UPLOAD,
                available_tables,
            });
            await store.dispatch('fetchSelections', 'test id');
            const wrapper = shallowMount(EditHeadingsTables, {
                localVue,
                vuetify,
                store,
                propsData: {
                    table: {
                        id: 'tenders table',
                        name: 'tenders',
                    },
                    headingsType: 'ocds',
                },
            });

            jest.clearAllMocks();
            await wrapper.vm.getTablePreview('tenders table');
            expect(ApiService.getTablePreview).toBeCalledTimes(1);
        });

        test("'updateTableHeading' updates heading of table", async () => {
            jest.clearAllMocks();
            store.commit('setUploadDetails', {
                id: 'test id',
                type: UPLOAD_TYPES.UPLOAD,
                available_tables,
            });
            await store.dispatch('fetchSelections', 'test id');
            const wrapper = shallowMount(EditHeadingsTables, {
                localVue,
                vuetify,
                store,
                propsData: {
                    table: {
                        id: 'tenders-table',
                        name: 'tenders',
                    },
                    headingsType: 'ocds',
                },
            });

            await wrapper.vm.getTablePreview('tenders-table');
            await wrapper.vm.updateTableHeading('new name', 'tenders-table');
            expect(wrapper.vm.tables.find((table) => table.id === 'tenders-table').heading).toBe('new name');
        });
    });
});
