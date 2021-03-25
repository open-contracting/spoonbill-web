import Vue from 'vue';
import VueRouter from 'vue-router';

Vue.use(VueRouter);

const routes = [
    {
        path: '/select-data',
        name: 'select data',
        component: () => import('@/views/SelectData'),
    },
    {
        path: '/select-data/select-file',
        name: 'select file',
        component: () => import('@/views/SelectData/SelectFile'),
    },
    {
        path: '/select-data/select-tables',
        name: 'select tables',
        component: () => import('@/views/SelectData/SelectTables'),
    },
    {
        path: '*',
        redirect: '/select-data',
    },
];

const router = new VueRouter({
    routes,
});

export default router;
