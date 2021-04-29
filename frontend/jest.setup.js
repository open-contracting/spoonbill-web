import Vue from 'vue';
import Vuetify from 'vuetify';
import GetTextPlugin from 'vue-gettext';
import translations from '@/translations/translations.json';

Vue.use(Vuetify);
Vue.config.productionTip = false;

Vue.use(GetTextPlugin, {
    availableLanguages: {
        en: 'British English',
        es: 'Español',
    },
    defaultLanguage: 'en',
    translations,
    silent: true,
});

jest.mock('@/services/ApiService', () => {
    return {
        sendFile: jest.fn(() => {
            return new Promise((resolve) => {
                setTimeout(() => {
                    resolve({
                        data: {
                            id: 'mocked_id',
                        },
                    });
                }, 10);
            });
        }),

        sendUrl: jest.fn(() => {
            return new Promise((resolve) => {
                setTimeout(() => {
                    resolve({
                        data: {
                            id: 'mocked_id',
                        },
                    });
                }, 10);
            });
        }),

        getSelections: jest.fn((id) => {
            return new Promise((resolve, reject) => {
                setTimeout(() => {
                    if (id === 'error') {
                        reject();
                    } else {
                        resolve({
                            data: {
                                id: 'test id',
                                headings_type: 'ocds',
                                flattens: [
                                    {
                                        id: 'flatten-1',
                                        export_format: 'csv',
                                        file: null,
                                        status: 'processing',
                                        error: '',
                                    },
                                    {
                                        id: 'flatten-2',
                                        export_format: 'xlsx',
                                        file: 'https://link-to-somewhere.com',
                                        status: 'completed',
                                        error: '',
                                    },
                                ],
                                tables: [
                                    {
                                        id: 'parties-table',
                                        name: 'parties',
                                        include: true,
                                        split: false,
                                    },
                                    {
                                        id: 'tenders-table',
                                        name: 'tenders',
                                        include: true,
                                        split: false,
                                    },
                                    {
                                        id: 'awards-table',
                                        name: 'awards',
                                        include: true,
                                        split: false,
                                    },
                                    {
                                        id: 'documents-table',
                                        name: 'documents',
                                        include: false,
                                        split: true,
                                    },
                                ],
                            },
                        });
                    }
                }, 10);
            });
        }),

        changeSplitStatus: jest.fn((type, uploadId, selectionsId, tableId, value) => {
            return new Promise((resolve) => {
                setTimeout(() => {
                    resolve({
                        data: {
                            tableId,
                            split: value,
                        },
                    });
                }, 10);
            });
        }),

        changeIncludeStatus: jest.fn((type, uploadId, selectionsId, tableId, value) => {
            return new Promise((resolve) => {
                setTimeout(() => {
                    resolve({
                        data: {
                            tableId,
                            include: value,
                        },
                    });
                }, 10);
            });
        }),

        getUploadInfo: jest.fn((id) => {
            return new Promise((resolve) => {
                setTimeout(() => {
                    resolve({
                        data: {
                            id: id,
                        },
                    });
                }, 10);
            });
        }),

        getUploadInfoByUrl: jest.fn((id) => {
            return new Promise((resolve) => {
                setTimeout(() => {
                    resolve({
                        data: {
                            id: id,
                        },
                    });
                }, 10);
            });
        }),

        createSelections: jest.fn(() => {
            return new Promise((resolve) => {
                setTimeout(() => {
                    resolve({
                        data: {
                            id: 'test id',
                            headings_type: 'ocds',
                            tables: [
                                {
                                    id: 'parties-table',
                                    name: 'parties',
                                    rows: 5,
                                    arrays: {
                                        count: 2,
                                        threshold: 5,
                                        above_threshold: ['tenderer'],
                                        below_threshold: ['parties/0/roles'],
                                    },
                                    available_data: {
                                        columns: { total: 22, available: 18, additional: ['parties/0/identifier/Name'] },
                                    },
                                },
                                {
                                    id: 'tenders-table',
                                    name: 'tenders',
                                    rows: 11,
                                    arrays: { count: 7, threshold: 5, above_threshold: ['tender/items'] },
                                    available_data: { columns: { total: 35, available: 34 } },
                                },
                                {
                                    id: 'awards-table',
                                    name: 'awards',
                                    rows: 4,
                                    arrays: {
                                        count: 2,
                                        threshold: 5,
                                        above_threshold: ['awards/0/suppliers', 'awards/0/items'],
                                    },
                                    available_data: { total: 16, available: 9 },
                                },
                                {
                                    id: 'documents-table',
                                    name: 'documents',
                                    rows: 5,
                                },
                            ],
                        },
                    });
                }, 10);
            });
        }),

        changeHeadingsType: jest.fn((id) => {
            return new Promise((resolve) => {
                setTimeout(() => {
                    resolve({
                        data: {
                            id: id,
                        },
                    });
                }, 10);
            });
        }),

        updateTableHeading: jest.fn((id) => {
            return new Promise((resolve) => {
                setTimeout(() => {
                    resolve({
                        data: {
                            id: id,
                        },
                    });
                }, 10);
            });
        }),

        getTablePreview: jest.fn((type, uploadId, selectionsId, tableId) => {
            return new Promise((resolve) => {
                setTimeout(() => {
                    resolve({
                        data: [
                            {
                                id: tableId,
                                name: 'Awards_a.csv',
                                preview: 'col1,col2,col3↵cell11,cell12,cell13↵cell21,cell22,cell23',
                            },
                            {
                                id: 'table 2',
                                name: 'Awards_b.csv',
                                preview: 'col1,col2,col3↵cell11,cell12,cell13↵cell21,cell22,cell23',
                            },
                        ],
                    });
                }, 10);
            });
        }),

        createFlatten: jest.fn(() => {
            return new Promise((resolve) => {
                setTimeout(() => {
                    resolve();
                }, 10);
            });
        }),
    };
});

Object.defineProperty(window, 'scroll', {
    value: jest.fn(),
});
Object.defineProperty(window, 'open', {
    value: jest.fn(),
});
