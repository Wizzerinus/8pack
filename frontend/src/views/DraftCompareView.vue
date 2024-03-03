<template>
    <h2 class="mb-3">Compare runs of draft {{ draft_id }}</h2>
    <div class="mb-3">
        <RouterLink :to="`/drafts/${draft_id}`" class="btn btn-primary me-4">
            Play this draft
        </RouterLink>
        <RouterLink :to="`/drafts/${draft_id}/results`" class="btn btn-accent">
            See all results
        </RouterLink>
    </div>
    <div class="mb-3 flex flex-col gap-1">
        <div class="flex items-center gap-2">
            <div class="badge badge-lg" style="background-color: green; border-color: green"></div>
            Picked by both players
        </div>
        <div class="flex items-center gap-2">
            <div
                class="badge badge-lg"
                style="background-color: orange; border-color: orange"
            ></div>
            Picked by the original player
        </div>
        <div class="flex items-center gap-2">
            <div class="badge badge-lg" style="background-color: blue; border-color: blue"></div>
            Picked by the compared player
        </div>
    </div>
    <div v-if="!loading_count">
        <div class="flex flex-col" v-for="(cards, idx) in picks">
            <h3 class="mb-1">Pack 1, pick {{ idx + 1 }}</h3>
            <div class="flex flex-wrap items-center gap-2 mb-3">
                <div class="max-w-48" v-for="card in cards">
                    <img
                        :src="card.image"
                        :alt="card.name"
                        :title="card.name"
                        class="rounded"
                        :class="get_border(card, idx)"
                    />
                </div>
            </div>
        </div>
    </div>
    <span v-else class="loading loading-spinner loading-lg"></span>
</template>
<style scoped>
.picked-by-both {
    border: 4px solid green;
    box-sizing: border-box;
}
.picked-by-us {
    border: 4px solid blue;
    box-sizing: border-box;
}
.picked-by-og {
    border: 4px solid orange;
    box-sizing: border-box;
}
</style>
<script>
import { useDraftStore } from "@/stores/draft.js"
import { computed, watch } from "vue"
import { storeToRefs } from "pinia"

export default {
    props: ["run_id", "draft_id"],
    setup(props) {
        const draftStore = useDraftStore()
        watch(() => props.draft_id, draftStore.load, { immediate: true })
        const {
            current_draft_plays: plays,
            current_draft_choices: picks,
            loading_count,
        } = storeToRefs(draftStore)

        const og_run = computed(() => {
            for (const i of plays.value) if (i.is_og) return i
        })
        const compared_run = computed(() => {
            for (const i of plays.value) if (String(i.id) === props.run_id) return i
        })

        const get_border = (card, idx) => {
            const we_picked = compared_run.value.cards[idx].name === card.name
            const they_picked = og_run.value.cards[idx].name === card.name
            if (we_picked && they_picked) return "picked-by-both"
            else if (we_picked) return "picked-by-us"
            else if (they_picked) return "picked-by-og"
        }

        return { og_run, compared_run, picks, get_border, loading_count }
    },
}
</script>
