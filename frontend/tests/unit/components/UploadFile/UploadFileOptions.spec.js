import { mount, createLocalVue } from '@vue/test-utils';
import UploadFileOptions from '@/components/UploadFile/UploadFileOptions';
import AppButton from '@/components/App/AppButton';
import Vuetify from 'vuetify';

describe('UploadFileOptions.vue', () => {
    const localVue = createLocalVue();
    const vuetify = new Vuetify();

    it("emits 'select' event with selected option", () => {
        const wrapper = mount(UploadFileOptions, {
            localVue,
            vuetify,
        });
        const buttons = wrapper.findAllComponents(AppButton);

        buttons.at(0).vm.$emit('click');
        expect(wrapper.emitted().select).toStrictEqual([['AUTO']]);

        buttons.at(1).vm.$emit('click');
        expect(wrapper.emitted().select).toStrictEqual([['AUTO'], ['MANUAL']]);
    });
});
