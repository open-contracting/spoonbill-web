import { mount, createLocalVue } from '@vue/test-utils';
import UploadFileInput from '@/components/UploadFile/UploadFileInput';
import Vuetify from 'vuetify';
import ApiService from '@/services/ApiService';
import store from '@/store';
import router from '@/router';

const mockCancelTokenSource = {
    token: 'mocked',
    cancel: jest.fn(),
};
jest.mock('axios', () => {
    return {
        CancelToken: {
            source() {
                return mockCancelTokenSource;
            },
        },
    };
});

describe('UploadFileInput.vue', () => {
    const localVue = createLocalVue();
    const vuetify = new Vuetify();

    describe('methods', () => {
        test("'sendFile' method makes API call", async () => {
            const wrapper = mount(UploadFileInput, {
                localVue,
                store,
                vuetify,
                router,
            });
            await wrapper.vm.sendFile({ size: 101, name: 'test' });
            expect(ApiService.sendFile).toBeCalledTimes(1);
        });

        test("'sendUrl' method makes API call with entered URL", async () => {
            const wrapper = mount(UploadFileInput, {
                localVue,
                store,
                vuetify,
                router,
            });

            await wrapper.vm.sendUrl('http://mocked-url.com');
            expect(ApiService.sendUrl).toBeCalledWith('http://mocked-url.com');
        });

        test("'cancelRequest' cancels 'sendFile' request", () => {
            const wrapper = mount(UploadFileInput, {
                localVue,
                store,
                vuetify,
            });

            wrapper.vm.createCancelToken();
            wrapper.vm.cancelRequest();
            expect(mockCancelTokenSource.cancel).toBeCalledTimes(1);
        });
    });
});
