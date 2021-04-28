import { mount, createLocalVue } from '@vue/test-utils';
import Download from '@/views/Download';
import store from '@/store';
import Vuetify from 'vuetify';
import router from '@/router';
import ApiService from '@/services/ApiService';
import { UPLOAD_TYPES } from '@/constants';
jest.mock('@/utils/getQueryParam', () => {
    return (name) => {
        return name + '-id';
    };
});

describe('Download.vue', () => {
    const localVue = createLocalVue();
    const vuetify = new Vuetify();
    const actualDispatch = store.dispatch;

    describe('methods', () => {
        /** @type { Wrapper<Vue> } */
        let wrapper;
        beforeEach(() => {
            router.push = jest.fn();
            store.commit('setUploadDetails', {
                id: 'test id',
                type: UPLOAD_TYPES.UPLOAD,
            });
            wrapper = mount(Download, {
                localVue,
                vuetify,
                store,
                router,
            });
            jest.clearAllMocks();
        });

        test("'download' downloads file", async () => {
            await store.dispatch('fetchSelections', 'test-id');
            wrapper.vm.download('xlsx');
            expect(window.open).toBeCalledTimes(1);
        });

        test("'createFlatten' sends request to create flatten and opens websocket connection if needed", async () => {
            await store.dispatch('fetchSelections', 'test-id');
            store.dispatch = jest.fn();
            await wrapper.vm.createFlatten('xlsx');
            expect(ApiService.createFlatten).toBeCalledTimes(1);
            expect(store.dispatch).toBeCalledTimes(1);

            store.dispatch = jest.fn();
            store.commit('setConnection', {});
            await wrapper.vm.createFlatten('xlsx');
            expect(ApiService.createFlatten).toBeCalledTimes(2);
            expect(store.dispatch).toBeCalledWith('fetchSelections', store.state.selections.id);
            store.dispatch = actualDispatch;
        });
    });

    it('gets selections once created', async () => {
        jest.clearAllMocks();
        store.commit('setSelections', null);
        store.commit('setUploadDetails', {
            id: 'test id',
            type: UPLOAD_TYPES.UPLOAD,
        });

        mount(Download, {
            localVue,
            vuetify,
            store,
            router,
        });
        expect(ApiService.getSelections).toBeCalledTimes(1);

        store.dispatch = jest.fn();
        router.push = jest.fn();
        const wrapper = mount(Download, {
            localVue,
            vuetify,
            store,
            router,
        });
        await wrapper.vm.$nextTick();
        expect(router.push).toBeCalledTimes(1);
    });
});
