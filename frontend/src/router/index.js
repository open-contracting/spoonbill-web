import Vue from 'vue';
import VueRouter from 'vue-router';
import store from '@/store';

Vue.use(VueRouter);

const routes = [
    {
        path: '/upload-file',
        name: 'upload file',
        component: () => import('@/views/UploadFile'),
    },
    {
        path: '/upload-file/registry',
        name: 'upload file from registry',
        component: () => import('@/views/UploadFile/UploadFileRegistry'),
    },
    {
        path: '/select-data',
        name: 'select data',
        component: () => import('@/views/SelectData'),
    },
    {
        path: '/customize-tables/:id?',
        name: 'customize tables',
        component: () => import('@/views/CustomizeTables'),
    },
    {
        path: '/edit-headings',
        name: 'edit headings',
        component: () => import('@/views/EditHeadings'),
    },
    {
        path: '/download',
        name: 'download',
        component: () => import('@/views/Download'),
    },
    {
        path: '*',
        redirect: '/upload-file',
    },
];

const router = new VueRouter({
    routes,
});

router.beforeEach(async (to, from, next) => {
    const fromIndex = routes.findIndex((route) => route.name === from.name);
    const toIndex = routes.findIndex((route) => route.name === to.name);
    if (fromIndex > -1 && fromIndex > toIndex) {
        const confirmed = await router.app.$root.openConfirmDialog();
        if (confirmed && to.name === 'upload file') {
            store.commit('setSelections', null);
            store.commit('setUploadDetails', null);
        }
        next(confirmed);
    } else {
        next();
    }
});

export default router;
