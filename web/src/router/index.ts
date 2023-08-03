// Composables
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
    {
        path: '/',
        component: () => import('@/views/Home.vue'),
        meta: {
            name: "配置",
            seo: {
                description: "配置页面"
            }
        }
    },
]

const router = createRouter({
    history: createWebHistory(process.env.BASE_URL),
    routes,
})

export default router
