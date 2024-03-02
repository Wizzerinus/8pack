import { createRouter, createWebHistory } from "vue-router"
import HomeView from "../views/HomeView.vue"
import {useAuthStore} from "@/stores/auth.js";
import DraftView from "@/views/DraftView.vue";

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        { path: "/", name: "home", component: HomeView },
        { path: "/drafts/:id", name: "draft", component: DraftView },
    ],
})

router.beforeEach(async () => {
    const auth = useAuthStore()
    await auth.load()
})


export default router
