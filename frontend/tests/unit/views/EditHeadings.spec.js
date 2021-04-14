import { shallowMount, createLocalVue } from '@vue/test-utils';
import EditHeadings from '@/views/EditHeadings';
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

describe('EditHeadings.vue', () => {
    const localVue = createLocalVue();
    const vuetify = new Vuetify();

    it('gets selections once created', async () => {
        store.commit('setSelections', null);
        store.commit('setUploadDetails', {
            id: 'test id',
            type: UPLOAD_TYPES.UPLOAD,
        });
        shallowMount(EditHeadings, {
            localVue,
            vuetify,
            store,
            router,
        });
        expect(ApiService.getSelections).toBeCalledTimes(1);
    });

    describe('methods', () => {
        /** @type { Wrapper<Vue> } */
        let wrapper;
        beforeEach(() => {
            router.push = jest.fn();
            store.commit('setUploadDetails', {
                id: 'test id',
                type: UPLOAD_TYPES.UPLOAD,
            });
            wrapper = shallowMount(EditHeadings, {
                localVue,
                vuetify,
                store,
                router,
            });
            jest.clearAllMocks();
        });

        test("'onBackClick' goes to previous table or previous step", async () => {
            await store.dispatch('fetchSelections', 'test id');
            wrapper.vm.onContinueClick();
            expect(wrapper.vm.currentTableIndex).toBe(1);
            wrapper.vm.onBackClick();
            expect(wrapper.vm.currentTableIndex).toBe(0);
            wrapper.vm.onBackClick();
            expect(router.push).toBeCalledTimes(1);
        });

        test("'onContinueClick' goes to next table or next step", async () => {
            await store.dispatch('fetchSelections', 'test id');
            wrapper.vm.onContinueClick();
            expect(wrapper.vm.currentTableIndex).toBe(1);
            wrapper.vm.onContinueClick();
            wrapper.vm.onContinueClick();
            wrapper.vm.onContinueClick();
            expect(router.push).toBeCalledTimes(1);
        });

        test("'changeHeadingsType' updates headings type of selection", async () => {
            await store.dispatch('fetchSelections', 'test id');
            await wrapper.vm.changeHeadingsType('r_friendly');
            expect(ApiService.changeHeadingsType).toBeCalledTimes(1);
            expect(store.state.selections.headings_type).toBe('r_friendly');
        });
    });
});
