import { mount } from '@vue/test-utils';
import AppStepper from '@/components/App/AppStepper';
import store from '@/store';
import router from '@/router';

describe('AppStepper.vue', () => {
    describe('methods', () => {
        /** @type { Wrapper<Vue> } */
        let wrapper;
        beforeEach(() => {
            store.commit = jest.fn();
            router.push = jest.fn(
                () =>
                    new Promise((resolve) => {
                        resolve();
                    })
            );
            wrapper = mount(AppStepper, {
                store,
                router,
            });

            wrapper.vm.$root.openConfirmDialog = jest.fn(
                () =>
                    new Promise((resolve) => {
                        resolve(true);
                    })
            );
        });

        test("'openConfirmDialog' method opens 'confirm' dialog and returns Promise", () => {
            const res = wrapper.vm.openConfirmDialog();
            expect(res).toBeInstanceOf(Promise);
            expect(wrapper.vm.$root.openConfirmDialog).toBeCalledTimes(1);
        });

        test("'onUploadFileStepClick' clears state and navigates to '/upload-file'", async () => {
            await wrapper.vm.onUploadFileStepClick();
            expect(store.commit).toBeCalledTimes(2);
            expect(router.push).toBeCalledTimes(1);

            wrapper.vm.$root.openConfirmDialog = jest.fn(
                () =>
                    new Promise((resolve) => {
                        resolve(false);
                    })
            );

            expect(store.commit).toBeCalledTimes(2);
            expect(router.push).toBeCalledTimes(1);
        });

        test("'navigateTo' navigates to specified path", async () => {
            await wrapper.vm.navigateTo('/test-route');
            expect(router.push).toBeCalledTimes(1);

            wrapper.vm.$root.openConfirmDialog = jest.fn(
                () =>
                    new Promise((resolve) => {
                        resolve(false);
                    })
            );

            expect(router.push).toBeCalledTimes(1);
        });
    });
});
