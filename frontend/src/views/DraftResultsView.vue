<template>
    <div>
        <h2>Draft #{{ draft_id }}</h2>
        <RouterLink :to="`/drafts/${draft_id}`" class="btn btn-primary me-4">
            Try this draft
        </RouterLink>
        <RouterLink :to="`/drafts/${draft_id}/statistics`" class="btn btn-accent">
            Draft Statistics
        </RouterLink>

        <template v-if="!loading_count">
            <div v-for="play in playthroughs" class="mt-4">
                <span>By {{ play.player_name }}, at {{ humanize_date(play.created_at) }}</span>
                <span class="italic text-neutral-700 block" v-if="play.player_id === our_player_id">
                    Your playthrough
                </span>
                <span class="italic text-neutral-700 block" v-if="play.is_og">
                    Original playthrough
                </span>
                <button v-else class="btn btn-sm block mb-1 btn-neutral" @click="compare(play)">
                    Compare with the original run
                </button>
                <div class="flex gap-2 mt-1">
                    <div v-for="card in play.cards">
                        <img
                            :src="card.image"
                            :alt="card.name"
                            :title="card.name"
                            class="rounded"
                        />
                    </div>
                </div>
            </div>
        </template>
        <span v-else class="loading loading-spinner loading-lg"></span>
    </div>
</template>
<script>
import { useDraftStore } from "@/stores/draft.js"
import { computed, watch } from "vue"
import { storeToRefs } from "pinia"
import { humanize_date } from "../util.js"
import { useAuthStore } from "@/stores/auth.js"
import { useRouter } from "vue-router"

export default {
    methods: { humanize_date },
    props: ["draft_id"],
    setup(props) {
        const draftStore = useDraftStore()
        const authStore = useAuthStore()
        const router = useRouter()
        watch(() => props.draft_id, draftStore.load, { immediate: true })

        const { current_draft_plays: playthroughs, loading_count } = storeToRefs(draftStore)
        const { user_data } = storeToRefs(authStore)
        const our_player_id = computed(() => (user_data.value ? user_data.value.id : -1))
        const compare = (play) => router.push(`/drafts/${props.draft_id}/compare/${play.id}`)
        return { playthroughs, our_player_id, compare, loading_count }
    },
}
</script>
