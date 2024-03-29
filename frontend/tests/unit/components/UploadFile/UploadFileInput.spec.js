import { mount, createLocalVue } from '@vue/test-utils';
import UploadFileInput from '@/components/UploadFile/UploadFileInput';
import Vuetify from 'vuetify';
import ApiService from '@/services/ApiService';
import store from '@/store';
import router from '@/router';
import { UPLOAD_STATUSES, UPLOAD_TYPES } from '@/constants';

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
            const url = 'http://mocked-url.com';
            let recivedUrl = url.split('/n');
            let initialStoreValue = store.state.numberOfUploads;
            expect(wrapper.vm.loading.value).toBe(false);
            await wrapper.vm.sendUrl(url);
            expect(wrapper.vm.loading.value).toBe(false);

            expect(store.state.downloadProgress).toBe(0);
            expect(store.state.numberOfUploads).toBe(initialStoreValue + 1);
            expect(store.state.downloadProgress).toBe(0);
            //Api service send url test
            expect(ApiService.sendUrl).toBeCalledWith(recivedUrl);
            expect(ApiService.sendUrl).toBeCalledTimes(1);
            //router test
            wrapper.vm.$router.push = jest.fn();
            expect(wrapper.vm.$router.push).toBeCalledTimes(0);
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
            expect(wrapper.vm.loading.value).toBe(false);
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
        test("'showLoading' changes showLoading", () => {
            const wrapper = mount(UploadFileInput, {
                localVue,
                store,
                vuetify,
            });

            wrapper.vm.showLoading('test', true);
            expect(wrapper.vm.fileName).toBe('test');
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

        test("'processValidationStatus' changes loading status depends on validation status", async () => {
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
            expect(wrapper.vm.loader).toBe(true);
            await new Promise((resolve) => {
                setTimeout(() => {
                    resolve();
                }, 1500);
            });
            expect(wrapper.vm.loader).toBe(false);
            expect(wrapper.vm.isValid).toBe(true);

            store.commit('setUploadDetails', {
                id: 'test id',
                type: UPLOAD_TYPES.UPLOAD,
                validation: {
                    is_valid: null,
                },
            });

            wrapper.vm.processValidationStatus();
            expect(store.state.uploadDetails).toBeTruthy();

            store.commit('setUploadDetails', {
                id: 'test id',
                type: UPLOAD_TYPES.UPLOAD,
                status: UPLOAD_STATUSES.FAILED,
            });

            await wrapper.vm.$nextTick();
            expect(wrapper.vm.loading.value).toBe(false);

            store.commit('setUploadDetails', {
                id: 'test id',
                type: UPLOAD_TYPES.UPLOAD,
                status: UPLOAD_STATUSES.DOWNLOADING,
            });

            await wrapper.vm.$nextTick();
            expect(wrapper.vm.loading.value).toBe(true);
            expect(wrapper.vm.loading.status).toBe('Upload in progress');

            store.commit('setUploadDetails', {
                id: 'test id',
                type: UPLOAD_TYPES.UPLOAD,
                status: UPLOAD_STATUSES.QUEUED_VALIDATION,
            });

            await wrapper.vm.$nextTick();
            expect(wrapper.vm.loading.value).toBe(true);
            expect(wrapper.vm.loading.status).toBe('File is queued for validation...');

            store.commit('setUploadDetails', {
                id: 'test id',
                type: UPLOAD_TYPES.UPLOAD,
                status: UPLOAD_STATUSES.QUEUED_DOWNLOAD,
            });

            await wrapper.vm.$nextTick();
            expect(wrapper.vm.loading.value).toBe(true);
            expect(wrapper.vm.loading.status).toBe('File is queued for downloading...');
        });
    });
});
