import { mount, createLocalVue } from '@vue/test-utils';
import AppDropzone from '@/components/App/AppDropzone';
import Vuetify from 'vuetify';

describe('AppDropzone.vue', () => {
    const localVue = createLocalVue();
    const vuetify = new Vuetify();

    it("emits 'input' event once user selects file", async () => {
        const wrapper = mount(AppDropzone, {
            localVue,
            vuetify,
        });
        wrapper.find('input').trigger('change');

        expect(wrapper.emitted().input).toBeTruthy();
    });

    it("emits 'input' event once user drops file on the dropzone", async () => {
        const wrapper = mount(AppDropzone, {
            localVue,
            vuetify,
        });
        const dropzone = wrapper.find('.app-dropzone');
        dropzone.trigger('drop', {
            dataTransfer: {
                files: [],
            },
        });

        expect(wrapper.emitted().input).toBeFalsy();

        dropzone.trigger('drop', {
            dataTransfer: {
                files: ['mocked'],
            },
        });

        expect(wrapper.emitted().input).toBeTruthy();
    });
});
