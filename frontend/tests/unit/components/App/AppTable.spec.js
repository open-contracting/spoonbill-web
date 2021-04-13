import { mount } from '@vue/test-utils';
import AppTable from '@/components/App/AppTable';

describe('AppTable.vue', () => {
    test("'highlightedCols' returns indexes of additional columns", () => {
        const wrapper = mount(AppTable, {
            propsData: {
                name: 'Test',
                headers: ['h1', 'h2', 'h3', 'h4', 'h5'],
                data: [['d1', 'd2', 'd3', 'd4', 'd5']],
                additionalColumns: ['h2', 'h3'],
            },
        });

        expect(wrapper.vm.highlightedCols).toStrictEqual([1, 2]);
    });
});
