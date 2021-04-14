import { mount, createLocalVue } from '@vue/test-utils';
import EditHeadingOptions from '@/components/EditHeadings/EditHeadingOptions';
import store from '@/store';
import Vuetify from 'vuetify';
import { UPLOAD_TYPES } from '@/constants';

describe('EditHeadingOptions.vue', () => {
    const localVue = createLocalVue();
    const vuetify = new Vuetify();

    describe('computed', () => {
        test('canApply', async () => {
            store.commit('setUploadDetails', {
                id: 'test id',
                type: UPLOAD_TYPES.UPLOAD,
            });
            await store.dispatch('fetchSelections', 'test id');
            const wrapper = mount(EditHeadingOptions, {
                localVue,
                vuetify,
                store,
            });
            expect(wrapper.vm.headingsType).toBe(store.state.selections.headings_type);
            expect(wrapper.vm.canApply).toBe(false);
            store.commit('setHeadingsType', 'en_user_friendly');
            expect(wrapper.vm.canApply).toBe(true);
        });
    });
});
