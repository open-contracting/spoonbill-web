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
                            tables: [],
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
