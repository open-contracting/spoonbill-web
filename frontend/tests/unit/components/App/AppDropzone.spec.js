import { mount, createLocalVue } from '@vue/test-utils';
import AppDropzone from '@/components/App/AppDropzone';
import Vuetify from 'vuetify';
import ApiService from '@/services/ApiService';

describe('AppDropzone.vue', () => {
    const localVue = createLocalVue();
    const vuetify = new Vuetify();

    describe('methods', () => {
        test('sendFile makes post request with selected file', async () => {
            const wrapper = mount(AppDropzone, {
                localVue,
                vuetify,
                mocks: {
                    $store: {
                        commit: jest.fn(),
                    },
                },
            });
            let file = {
                size: 100000001,
            };

            await wrapper.vm.sendFile(file);
            expect(ApiService.sendFile).toBeCalledTimes(0);
            expect(wrapper.emitted().send).toBeFalsy();

            file = {
                size: 100000000,
            };

            await wrapper.vm.sendFile(file);
            expect(ApiService.sendFile).toBeCalledTimes(1);
            expect(wrapper.emitted().send).toBeTruthy();
        });
    });
});
