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

        test("'navigateTo' navigates to specified path", async () => {
            await wrapper.vm.navigateTo(-1, '/test-route');
            expect(router.push).toBeCalledTimes(1);
            await wrapper.vm.navigateTo(2, '/select-data');
            expect(router.push).toBeCalledTimes(1);
        });
    });
});
