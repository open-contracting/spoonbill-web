import getQueryParam from '@/utils/getQueryParam';

describe('utils', () => {
    test('getQueryParam', () => {
        window.location.hash = '#/customize-tables?upload=upload-id&selections=selections-id';
        expect(getQueryParam('upload')).toBe('upload-id');
        expect(getQueryParam('selections')).toBe('selections-id');
        expect(getQueryParam('p')).toBe('');
    });
});
