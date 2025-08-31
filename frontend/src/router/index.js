import { createRouter, createWebHistory } from 'vue-router';
import TotalRanking from '../components/TotalRanking.vue';
import SportDetail from '../views/SportDetail.vue';
import Admin from '../views/Admin.vue';

const routes = [
    {
        path: '/',
        name: 'Home',
        component: TotalRanking,
    },
    {
        path: '/sports/:sportName', // :sportName は動的な値
        name: 'SportDetail',
        component: SportDetail,
        props: true, // URLのパラメータをコンポーネントのpropsとして渡す
    },
    {
        path: '/admin',
        name: 'Admin',
        component: Admin,
    },
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

export default router;