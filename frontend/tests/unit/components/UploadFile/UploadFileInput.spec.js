import { mount, createLocalVue } from '@vue/test-utils';
import UploadFileInput from '@/components/UploadFile/UploadFileInput';
import Vuetify from 'vuetify';
import ApiService from '@/services/ApiService';
import store from '@/store';
import router from '@/router';
import { UPLOAD_TYPES } from '@/constants';

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

        test("'selectUploadType' changes selected upload type", () => {
            const wrapper = mount(UploadFileInput, {
                localVue,
                store,
                vuetify,
            });

            wrapper.vm.selectUploadType('url');
            expect(wrapper.vm.uploadType).toBe('url');
            wrapper.vm.selectUploadType('upload');
            expect(wrapper.vm.uploadType).toBe('upload');
        });

        test("'onOptionSelect' navigates to another step depends on selected option", () => {
            const wrapper = mount(UploadFileInput, {
                localVue,
                store,
                vuetify,
                router,
            });
            store.commit('setUploadDetails', {
                id: 'test id',
                type: UPLOAD_TYPES.UPLOAD,
            });

            wrapper.vm.$router.push = jest.fn();
            wrapper.vm.onOptionSelect('MANUAL');
            expect(wrapper.vm.$router.push).toBeCalledTimes(1);
        });

        test("'onUploadFail' show error message", () => {
            const wrapper = mount(UploadFileInput, {
                localVue,
                store,
                vuetify,
                router,
            });
            store.commit('setUploadDetails', {
                id: 'test id',
                type: UPLOAD_TYPES.UPLOAD,
            });

            wrapper.vm.onUploadFail();
            expect(wrapper.vm.loading.value).toBe(false);
            expect(store.state.snackbar.opened).toBe(true);
            expect(store.state.uploadDetails).toBe(null);
        });

        test("'processValidationStatus' changes loading status depends on validation status", () => {
            const wrapper = mount(UploadFileInput, {
                localVue,
                store,
                vuetify,
                router,
            });
            store.commit('setUploadDetails', {
                id: 'test id',
                type: UPLOAD_TYPES.UPLOAD,
                validation: {
                    is_valid: false,
                },
            });

            wrapper.vm.processValidationStatus();
            expect(wrapper.vm.loading.value).toBe(false);
            expect(store.state.uploadDetails).toBe(null);

            store.commit('setUploadDetails', {
                id: 'test id',
                type: UPLOAD_TYPES.UPLOAD,
                validation: {
                    is_valid: true,
                },
            });

            wrapper.vm.processValidationStatus();
            expect(wrapper.vm.loading.value).toBe(true);
            expect(store.state.uploadDetails).toBeTruthy();
            expect(store.state.downloadProgress).toBe(100);

            store.commit('setUploadDetails', {
                id: 'test id',
                type: UPLOAD_TYPES.UPLOAD,
                validation: {
                    is_valid: null,
                },
            });

            wrapper.vm.processValidationStatus();
            expect(store.state.uploadDetails).toBeTruthy();
        });
    });
});
