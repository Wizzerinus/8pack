<template>
    <span class="loading loading-spinner loading-lg" v-if="!current_draft_choices"></span>
    <div v-else class="grid grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
        <div class="col-span-2 lg:col-span-3 xl:col-span-4 mr-4">
            <div v-if="cards" class="flex flex-wrap items-center justify-center gap-2">
                <div class="max-w-48" v-for="card in cards">
                    <img :src="card.image" :alt="card.name" :title="card.name"
                         class="rounded cursor-pointer" @click="pick(card)" />
                </div>
            </div>
            <div v-else>
                <button class="btn btn-primary block" v-if="logged_in" @click="save">Save results</button>
                <span v-else class="block">Log in or register to save this draft!</span>
                <button class="btn block mt-4" @click="view">View results without saving</button>
            </div>
        </div>
        <div>
            <h4>Already picked</h4>
            <div class="relative">
                <div v-for="(card, idx) in current_picks" class="absolute left-0 max-w-48" :style="{'top': `${idx * 40}px`}">
                    <img :src="card.image" :alt="card.name" :title="card.name" class="rounded" />
                </div>
            </div>
        </div>
    </div>
</template>
<script>
import {useDraftStore} from "@/stores/draft.js";
import {computed, watch} from "vue";
import {storeToRefs} from "pinia";
import {useAuthStore} from "@/stores/auth.js";
import {auth_post} from "@/util.js";
import {useRouter} from "vue-router";

export default {
    props: ["draft_id"],
    setup(props) {
        const draftStore = useDraftStore()
        const authStore = useAuthStore()
        watch(() => props.draft_id, draftStore.load, { immediate: true })

        const { logged_in } = storeToRefs(authStore)
        const { current_draft_choices, current_picks } = storeToRefs(draftStore)
        const cards = computed(() => current_draft_choices.value[current_picks.value.length])
        const pick = card => current_picks.value.push(card)

        const save = () => {
            auth_post(`drafts/${props.draft_id}/save`, {picks: current_picks.value.map(card => card.id)})
                .then(() => draftStore.reload())
                .then(view)
        }
        const view = () => {
            const router = useRouter()
            router.push(`/drafts/${props.draft_id}/results`)
        }

        return { current_draft_choices, current_picks, cards, pick, logged_in, save, view }
    }
}
</script>