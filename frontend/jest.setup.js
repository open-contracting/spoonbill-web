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

        getSelections: jest.fn(() => {
            return new Promise((resolve) => {
                setTimeout(() => {
                    resolve({
                        data: {
                            id: 'test id',
                            tables: [
                                {
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
                                    name: 'tenders',
                                    rows: 11,
                                    arrays: { count: 7, threshold: 5, above_threshold: ['tender/items'] },
                                    available_data: { columns: { total: 35, available: 34 } },
                                },
                                {
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
                                    name: 'documents',
                                    rows: 5,
                                },
                            ],
                        },
                    });
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

        createSelections: jest.fn((id) => {
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
    };
});
