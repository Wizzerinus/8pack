import { defineStore } from "pinia"
import { ref } from "vue"
import { get } from "@/util.js"

export const useDraftStore = defineStore("draft", () => {
    const current_draft_choices = ref(null)
    const current_draft_id = ref(-1)
    const current_picks = ref([])
    const current_draft_plays = ref([])
    const loading_count = ref(0)
    const reload = () => {
        const id = current_draft_id.value
        current_draft_choices.value = null
        current_picks.value = []
        current_draft_plays.value = []
        loading_count.value = 2
        get(`drafts/${id}/choices`)
            .then((e) => e.json())
            .then((e) => {
                current_draft_choices.value = e.cards
                loading_count.value -= 1
            })
        get(`drafts/${id}/playthroughs`)
            .then((e) => e.json())
            .then((e) => {
                current_draft_plays.value = e.playthroughs
                loading_count.value -= 1
            })
    }
    const load = (id) => {
        if (id === current_draft_id.value) return
        current_draft_id.value = id
        reload()
    }

    return {
        load,
        reload,
        current_draft_choices,
        current_draft_id,
        current_picks,
        current_draft_plays,
        loading_count,
    }
})
