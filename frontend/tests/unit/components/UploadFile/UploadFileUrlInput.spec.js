import { mount, createLocalVue } from '@vue/test-utils';
import UploadFileUrlInput from '@/components/UploadFile/UploadFileUrlInput';
import Vuetify from 'vuetify';

describe('UploadFileUrlInput.vue', () => {
    const localVue = createLocalVue();
    const vuetify = new Vuetify();

    it("emits 'submit' event once user clicks 'submit' button if url is valid", async () => {
        const wrapper = mount(UploadFileUrlInput, {
            localVue,
            vuetify,
        });
        const submitButton = wrapper.find('button');
        submitButton.trigger('click');

        expect(wrapper.emitted().submit).toBeFalsy();

        await wrapper.setData({
            url: 'mocked-url.com',
        });
        submitButton.trigger('click');

        expect(wrapper.emitted().submit).toStrictEqual([['mocked-url.com']]);
    });
});
