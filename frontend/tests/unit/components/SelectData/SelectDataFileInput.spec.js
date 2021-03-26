import { mount, createLocalVue } from '@vue/test-utils';
import SelectDataFileInput from '@/components/SelectData/SelectDataFileInput';
import Vuetify from 'vuetify';
import ApiService from '@/services/ApiService';
import store from '@/store';

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

describe('SelectDataFileInput.vue', () => {
    const localVue = createLocalVue();
    const vuetify = new Vuetify();

    describe('methods', () => {
        test("'sendFile' method makes API call", async () => {
            const wrapper = mount(SelectDataFileInput, {
                localVue,
                store,
                vuetify,
            });
            await wrapper.vm.sendFile({ size: 101 });
            expect(ApiService.sendFile).toBeCalledTimes(1);
        });

        test("'sendUrl' method makes API call with entered URL", async () => {
            const wrapper = mount(SelectDataFileInput, {
                localVue,
                store,
                vuetify,
            });

            await wrapper.vm.sendUrl('http://mocked-url.com');
            expect(ApiService.sendUrl).toBeCalledWith('http://mocked-url.com');
        });

        test("'cancelRequest' cancels 'sendFile' request", () => {
            const wrapper = mount(SelectDataFileInput, {
                localVue,
                store,
                vuetify,
            });

            wrapper.vm.sendFile({ size: 101 });
            wrapper.vm.cancelRequest();
            expect(mockCancelTokenSource.cancel).toBeCalledTimes(1);
        });
    });
});
