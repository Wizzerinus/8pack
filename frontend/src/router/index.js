import { createRouter, createWebHistory } from "vue-router"
import HomeView from "../views/HomeView.vue"
import {useAuthStore} from "@/stores/auth.js";

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        { path: "/", name: "home", component: HomeView },
    ],
})

router.beforeEach(async () => {
    const auth = useAuthStore()
    await auth.load()
})


export default router
