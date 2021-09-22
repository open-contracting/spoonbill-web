import { mount, createLocalVue } from '@vue/test-utils';
import CustomizeDialog from '@/components/CustomizeTables/CustomizeDialog';
import store from '@/store';
import Vuetify from 'vuetify';
import ApiService from '@/services/ApiService';
import { UPLOAD_TYPES } from '@/constants';
import router from '@/router';

describe('CustomizeDialog.vue', () => {
    const localVue = createLocalVue();
    const vuetify = new Vuetify();

    describe('methods', () => {
        test('test open dialog', async () => {
            const wrapper = mount(CustomizeDialog, {
                localVue,
                vuetify,
                store,
                propsData: {
                    isOpen: false,
                },
            });
            await wrapper.setProps({
                isOpen: false,
            });
            expect(wrapper.vm.isOpen).toBe(false);
            await wrapper.setProps({
                isOpen: true,
            });
            expect(wrapper.vm.isOpen).toBe(true);
        });
        test('test computed dialog', async () => {
            const wrapper = mount(CustomizeDialog, {
                localVue,
                vuetify,
                store,
                propsData: {
                    isOpen: false,
                },
            });
            await wrapper.setProps({
                isOpen: false,
            });
            expect(wrapper.vm.dialog).toBe(false);
            await wrapper.setProps({
                isOpen: true,
            });
            expect(wrapper.vm.dialog).toBe(true);
        });
        test('test method ', async () => {
            const wrapper = mount(CustomizeDialog, {
                localVue,
                vuetify,
                store,
                propsData: {
                    isOpen: false,
                },
            });
            await wrapper.setProps({
                isOpen: false,
            });
            wrapper.vm.onContinueClick();
            expect(wrapper.vm.dialog).toBe(false);
        });
        test('test radio group ', async () => {
            const wrapper = mount(CustomizeDialog, {
                localVue,
                vuetify,
                store,
                propsData: {
                    isOpen: false,
                },
            });
            await wrapper.setProps({
                isOpen: false,
            });
            wrapper.vm.radioGroup = null;
            expect(wrapper.vm.radioGroup).toBe(null);

            wrapper.vm.radioGroup = 'keep';
            expect(wrapper.vm.radioGroup).toBe('keep');
        });
    });
});
