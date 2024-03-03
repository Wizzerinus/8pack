import { createRouter, createWebHistory } from "vue-router"
import HomeView from "../views/HomeView.vue"
import {useAuthStore} from "@/stores/auth.js";
import PlayDraftView from "@/views/PlayDraftView.vue";
import DraftResultsView from "@/views/DraftResultsView.vue";
import DraftCompareView from "@/views/DraftCompareView.vue";

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        { path: "/", name: "home", component: HomeView },
        { path: "/drafts/:draft_id", name: "draft", component: PlayDraftView, props: true },
        { path: "/drafts/:draft_id/results", name: "draft-results", component: DraftResultsView, props: true },
        { path: "/drafts/:draft_id/compare/:run_id", name: "draft-compare", component: DraftCompareView, props: true },
    ],
})

router.beforeEach(async () => {
    const auth = useAuthStore()
    await auth.load()
})


export default router
