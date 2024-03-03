<template>
    <div class="mb-3">
        <RouterLink :to="`/drafts/${draft_id}`" class="btn btn-primary me-4">
            Play this draft
        </RouterLink>
        <RouterLink :to="`/drafts/${draft_id}/results`" class="btn btn-accent">
            See all results
        </RouterLink>
    </div>
    <div v-if="!loading_count">
        <div class="flex flex-col" v-for="(cards, idx) in picks">
            <h3 class="mb-1">Pack 1, pick {{ idx + 1 }}</h3>
            <div class="flex flex-wrap items-center gap-2 mb-3">
                <div class="max-w-48 relative p-2" v-for="card in cards">
                    <div
                        class="absolute -z-20 bottom-0 top-0 left-0 right-0 scale-background rounded pointer-events-none"
                    ></div>
                    <div
                        class="absolute -z-10 top-0 left-0 right-0 rounded-b bg-white pointer-events-none"
                        :style="{ height: `${100 - get_weight(idx, card)}%` }"
                    ></div>
                    <div class="flex flex-col items-center">
                        <img
                            :src="card.image"
                            :alt="card.name"
                            :title="`${card.name} - picked by ${get_weight(idx, card)}% players`"
                            class="rounded"
                        />
                        <span>{{ get_weight(idx, card) }}% players</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <span v-else class="loading loading-spinner loading-lg"></span>
</template>
<style scoped>
.wrapper {
    left: 0;
    right: 0;
    z-index: -1;
}
.scale-background {
    background: linear-gradient(
        0deg,
        rgba(227, 40, 40, 1) 0%,
        rgba(255, 255, 0, 1) 44%,
        rgba(255, 255, 0, 1) 56%,
        rgba(22, 172, 0, 1) 100%
    );
}
</style>
<script>
import { useDraftStore } from "@/stores/draft.js"
import { computed, watch } from "vue"
import { storeToRefs } from "pinia"

export default {
    props: ["draft_id"],
    setup(props) {
        const draftStore = useDraftStore()
        watch(() => props.draft_id, draftStore.load, { immediate: true })
        const {
            current_draft_plays: plays,
            current_draft_choices: picks,
            loading_count,
        } = storeToRefs(draftStore)
        const card_weights = computed(() => {
            const weights = [{}, {}, {}, {}, {}, {}, {}, {}]
            const multiplier = 100 / plays.value.length
            for (const play of plays.value) {
                for (let i = 0; i < play.cards.length; i++) {
                    weights[i][play.cards[i].id] = (weights[i][play.cards[i].id] || 0) + multiplier
                }
            }
            console.log(weights)
            return weights
        })
        const get_weight = (idx, card) => Math.round(card_weights.value[idx][card.id] || 0)

        return { plays, picks, loading_count, get_weight }
    },
}
</script>
