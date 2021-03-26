import Vue from 'vue';
import VueRouter from 'vue-router';

Vue.use(VueRouter);

const routes = [
    {
        path: '/select-data',
        name: 'select data',
        component: () => import(/* webpackChunkName: "SelectData" */ '@/views/SelectData'),
    },
    {
        path: '/select-data/registry',
        name: 'select file',
        component: () => import(/* webpackChunkName: "SelectDataRegistry" */ '@/views/SelectData/SelectDataRegistry'),
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
