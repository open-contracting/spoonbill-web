import { shallowMount, createLocalVue } from '@vue/test-utils';
import CustomizeTables from '@/views/CustomizeTables';
import store from '@/store';
import Vuetify from 'vuetify';
import router from '@/router';
import ApiService from '@/services/ApiService';
import { UPLOAD_TYPES } from '@/constants';
import VueRouter from 'vue-router';

jest.mock('@/utils/getQueryParam', () => {
    return (name) => {
        return name + '-id';
    };
});

describe('CustomizeTables.vue', () => {
    const localVue = createLocalVue();
    const vuetify = new Vuetify();

    describe('methods', () => {
        /** @type { Wrapper<Vue> }*/
        let wrapper;
        beforeEach(() => {
            router.push = new VueRouter().push;
            store.commit('setUploadDetails', {
                id: 'test id',
                type: UPLOAD_TYPES.UPLOAD,
            });
            wrapper = shallowMount(CustomizeTables, {
                localVue,
                vuetify,
                store,
                router,
            });
            jest.clearAllMocks();
        });

        test("'onBackClick' goes to previous table if exists", async () => {
            await store.dispatch('fetchSelections', 'test id');
            expect(wrapper.vm.currentTableIndex).toBe(0);
            await wrapper.vm.onContinueClick();
            expect(ApiService.changeIncludeStatus).toBeCalledTimes(1);
            expect(wrapper.vm.currentTableIndex).toBe(1);
            wrapper.vm.onBackClick();
            expect(wrapper.vm.currentTableIndex).toBe(0);
            router.push = jest.fn();
            wrapper.vm.onBackClick();
            expect(router.push).toBeCalledWith({
                path: '/select-data',
                query: {},
            });
        });

        test("'onContinueClick' changes include status of current table to true", async () => {
            await store.dispatch('fetchSelections', 'test id');
            await wrapper.vm.onContinueClick();
            expect(ApiService.changeIncludeStatus).toBeCalledTimes(1);
            expect(wrapper.vm.currentTableIndex).toBe(1);
        });

        test("'onRemoveClick' changes include status of current table to false", async () => {
            wrapper.vm.$root.openConfirmDialog = jest.fn(() => Promise.resolve(false));
            await store.dispatch('fetchSelections', 'test id');
            const oldIndex = wrapper.vm.currentTableIndex;
            await wrapper.vm.onRemoveClick();
            expect(ApiService.changeIncludeStatus).toBeCalledTimes(0);
            expect(wrapper.vm.currentTableIndex).toBe(oldIndex);

            wrapper.vm.$root.openConfirmDialog = jest.fn(() => Promise.resolve(true));
            await wrapper.vm.onRemoveClick();
            expect(ApiService.changeIncludeStatus).toBeCalledTimes(1);
            expect(wrapper.vm.currentTableIndex).toBe(oldIndex + 1);
        });

        test("'goTo' opens specified table", async () => {
            await store.dispatch('fetchSelections', 'test id');
            router.push = jest.fn();
            wrapper.vm.goTo('test-id');
            expect(router.push).toBeCalledTimes(1);
        });

        test("'goToNext' goes to the next table if it exists", async () => {
            await store.dispatch('fetchSelections', 'test id');
            router.push = jest.fn();
            wrapper.vm.goToNext();
            expect(router.push).toBeCalledWith({
                path: '/customize-tables/' + store.state.selections.tables[wrapper.vm.currentTableIndex + 1].id,
                query: {},
            });
        });

        test("'goToNext' goes to the next step if it is last table", async () => {
            await store.dispatch('fetchSelections', 'test id');
            router.push = new VueRouter().push;
            await wrapper.vm.goTo(store.state.selections.tables[store.state.selections.tables.length - 1].id);
            router.push = jest.fn();
            wrapper.vm.goToNext();
            expect(router.push).toBeCalledWith({
                path: '/edit-headings',
                query: {},
            });
        });
    });

    it('gets selections once created', async () => {
        jest.clearAllMocks();
        store.commit('setSelections', null);
        store.commit('setUploadDetails', {
            id: 'test id',
            type: UPLOAD_TYPES.UPLOAD,
        });

        shallowMount(CustomizeTables, {
            localVue,
            vuetify,
            store,
            router,
        });
        expect(ApiService.getSelections).toBeCalledTimes(1);

        store.dispatch = jest.fn();
        router.push = jest.fn();
        const wrapper = shallowMount(CustomizeTables, {
            localVue,
            vuetify,
            store,
            router,
        });
        await wrapper.vm.$nextTick();
        expect(router.push).toBeCalledTimes(1);
    });
});
