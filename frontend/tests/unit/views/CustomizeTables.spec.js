import { shallowMount, createLocalVue } from '@vue/test-utils';
import CustomizeTables from '@/views/CustomizeTables';
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

describe('CustomizeTables.vue', () => {
    const localVue = createLocalVue();
    const vuetify = new Vuetify();

    it('gets selections once created', async () => {
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
    });

    describe('methods', () => {
        test("'onContinueClick' changes include status of current table to true", async () => {
            store.commit('setUploadDetails', {
                id: 'test id',
                type: UPLOAD_TYPES.UPLOAD,
            });
            const wrapper = shallowMount(CustomizeTables, {
                localVue,
                vuetify,
                store,
                router,
            });

            await store.dispatch('fetchSelections', 'test id');
            await wrapper.vm.onContinueClick();
            expect(ApiService.changeIncludeStatus).toBeCalledTimes(1);
            expect(wrapper.vm.currentTableIndex).toBe(1);
        });

        test("'onRemoveClick' changes include status of current table to false", async () => {
            store.commit('setUploadDetails', {
                id: 'test id',
                type: UPLOAD_TYPES.UPLOAD,
            });
            const wrapper = shallowMount(CustomizeTables, {
                localVue,
                vuetify,
                store,
                router,
            });

            jest.clearAllMocks();
            wrapper.vm.$root.openConfirmDialog = jest.fn(() => Promise.resolve(false));
            await store.dispatch('fetchSelections', 'test id');
            await wrapper.vm.onRemoveClick();
            expect(ApiService.changeIncludeStatus).toBeCalledTimes(0);
            expect(wrapper.vm.currentTableIndex).toBe(0);

            wrapper.vm.$root.openConfirmDialog = jest.fn(() => Promise.resolve(true));
            await wrapper.vm.onRemoveClick();
            expect(ApiService.changeIncludeStatus).toBeCalledTimes(1);
            expect(wrapper.vm.currentTableIndex).toBe(1);
        });
    });
});
