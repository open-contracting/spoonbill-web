import Vue from 'vue';
import VueRouter from 'vue-router';

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
        path: '/customize-tables',
        name: 'customize tables',
        component: () => import('@/views/CustomizeTables'),
    },
    {
        path: '*',
        redirect: '/upload-file',
    },
];

const router = new VueRouter({
    routes,
});

export default router;
