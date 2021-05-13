import { mount, createLocalVue } from '@vue/test-utils';
import LayoutHeader from '@/components/Layout/LayoutHeader';
import Vuetify from 'vuetify';
const vuetify = new Vuetify();

describe('LayoutHeader.vue', () => {
    const localVue = createLocalVue();
    /** @type { Wrapper<Vue> } */
    let wrapper;
    beforeEach(() => {
        wrapper = mount(LayoutHeader, {
            localVue,
            vuetify,
        });
    });

    describe('methods', () => {
        test("'changeLanguage' changes current language", () => {
            wrapper.vm.$language.current = 'en_US';
            wrapper.vm.changeLanguage();
            expect(wrapper.vm.$language.current).toBe('es');
            wrapper.vm.changeLanguage();
            expect(wrapper.vm.$language.current).toBe('en_US');
        });
    });
});
