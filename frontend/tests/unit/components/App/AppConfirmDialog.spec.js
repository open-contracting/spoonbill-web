import { mount, createLocalVue } from '@vue/test-utils';
import AppConfirmDialog from '@/components/App/AppConfirmDialog';
import Vuetify from 'vuetify';

const testOptions = {
    title: 'Are you sure?',
    content: 'All current changes will be reversed',
    submitBtnText: 'Yes, go back',
    icon: require('@/assets/icons/back.svg'),
};

describe('AppConfirmDialog.vue', () => {
    const localVue = createLocalVue();
    const vuetify = new Vuetify();

    describe('methods', () => {
        test("'open' method opens dialog and returns Promise", () => {
            const wrapper = mount(AppConfirmDialog, {
                localVue,
                vuetify,
            });
            const res = wrapper.vm.open(testOptions);

            expect(wrapper.vm.dialog).toBeTruthy();
            expect(wrapper.vm.resolve).toBeInstanceOf(Function);
            expect(res).toBeInstanceOf(Promise);
        });

        test("'cancel' method closes dialog and resolves returned promise with 'false' value", () => {
            const wrapper = mount(AppConfirmDialog, {
                localVue,
                vuetify,
            });
            const res = wrapper.vm.open(testOptions);
            wrapper.vm.cancel();

            expect(wrapper.vm.dialog).toBeFalsy();
            expect(res).resolves.toBe(false);
        });

        test("'confirm' method closes dialog and resolves returned promise with 'true' value", () => {
            const wrapper = mount(AppConfirmDialog, {
                localVue,
                vuetify,
            });
            const res = wrapper.vm.open(testOptions);
            wrapper.vm.confirm();

            expect(wrapper.vm.dialog).toBeFalsy();
            expect(res).resolves.toBe(true);
        });
    });
});
