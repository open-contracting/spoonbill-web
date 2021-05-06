import { mount, createLocalVue } from '@vue/test-utils';
import SelectData from '@/views/SelectData';
import store from '@/store';
import Vuetify from 'vuetify';
import router from '@/router';
import ApiService from '@/services/ApiService';
import { UPLOAD_TYPES } from '@/constants';

const uploadDetails = {
    id: 'test',
    unavailable_tables: ['test'],
    available_tables: [
        {
            name: 'parties',
            rows: 5,
            arrays: { one: 'one', two: 'two' },
            available_data: { columns: { total: 22, available: 18, additional: ['parties/0/identifier/Name'] } },
        },
        {
            name: 'tenders',
            rows: 11,
            arrays: {},
            available_data: { columns: { total: 35, available: 34 } },
        },
        {
            name: 'awards',
            rows: 4,
            arrays: { one: 'one' },
            available_data: { total: 16, available: 9 },
        },
        {
            name: 'documents',
            arrays: {},
            rows: 5,
        },
    ],
};

describe('SelectData.vue', () => {
    const localVue = createLocalVue();
    const vuetify = new Vuetify();

    store.commit('setUploadDetails', uploadDetails);
    /** @type { Wrapper<Vue> } */
    let wrapper;
    beforeEach(() => {
        wrapper = mount(SelectData, {
            localVue,
            vuetify,
            store,
            router,
        });
    });

    it('goes to the first step if uploadDetails are empty', () => {
        store.commit('setUploadDetails', null);
        router.push = jest.fn();

        mount(SelectData, {
            localVue,
            vuetify,
            store,
            router,
        });
        expect(router.push).toBeCalledTimes(1);
        store.commit('setUploadDetails', uploadDetails);
    });

    it('filter all tables once created', () => {
        expect(wrapper.vm.availableTables.length).toBe(4);
        expect(wrapper.vm.unavailableTables.length).toBe(1);
    });

    describe('methods', () => {
        test("'isInTheSameSection' checks of tables are in the same table", () => {
            expect(wrapper.vm.isInTheSameSection('tenders', 'awards')).toBe(true);
            expect(wrapper.vm.isInTheSameSection('tenders', 'some table')).toBe(false);
        });

        test("'removeTables' moves checked tables to available", () => {
            wrapper.vm.checkedTables = ['tenders', 'awards'];
            wrapper.vm.addTables();
            expect(wrapper.vm.availableTables.length).toBe(2);
            wrapper.vm.checkedTables = ['tenders'];
            wrapper.vm.removeTables();
            expect(wrapper.vm.availableTables.length).toBe(3);
            expect(wrapper.vm.selectedTables.length).toBe(1);
        });

        test("'addTables' moves checked tables to selected", () => {
            wrapper.vm.checkedTables = ['tenders', 'awards'];
            wrapper.vm.addTables();
            expect(wrapper.vm.selectedTables.length).toBe(2);
            wrapper.vm.selectedTables.forEach((table) => {
                expect(['tenders', 'awards'].includes(table.name)).toBeTruthy();
            });
            expect(wrapper.vm.checkedTables.length).toBe(0);
        });

        test("'onTableClick' selects correct table", () => {
            wrapper.vm.onTableClick({}, 'awards');
            expect(wrapper.vm.checkedTables).toStrictEqual(['awards']);

            wrapper.vm.onTableClick({ ctrlKey: true }, 'awards');
            expect(wrapper.vm.checkedTables).toStrictEqual([]);

            wrapper.vm.onTableClick({}, 'awards');
            wrapper.vm.onTableClick({ ctrlKey: true }, 'tenders');
            expect(wrapper.vm.checkedTables).toStrictEqual(['awards', 'tenders']);
        });

        test("'createSelections' sends request with selected tables", async () => {
            store.commit('setUploadDetails', {
                type: UPLOAD_TYPES.UPLOAD,
                id: 'test id',
            });
            wrapper.vm.checkedTables = ['awards'];
            wrapper.vm.addTables();
            await wrapper.vm.createSelections();
            expect(ApiService.createSelections).toBeCalledWith(UPLOAD_TYPES.UPLOAD + 's', 'test id', ['awards']);
        });
    });
});
