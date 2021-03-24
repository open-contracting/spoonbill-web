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
        path: '*',
        redirect: '/select-data',
    },
];

const router = new VueRouter({
    routes,
});

export default router;
