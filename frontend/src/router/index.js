import { createRouter, createWebHistory } from 'vue-router';
import TotalRanking from '../components/TotalRanking.vue';
import SportDetail from '../views/SportDetail.vue';
import Admin from '../views/Admin.vue';
import Login from '../views/Login.vue'; // 追加
import { auth } from '../services/auth'; // 追加

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
        beforeEnter: (to, from, next) => { // 追加
            if (auth.state.isLoggedIn) {
                next();
            } else {
                next('/login');
            }
        },
    },
    {
        path: '/login',
        name: 'Login',
        component: Login,
    },
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

export default router;