<template>
    Draft results
</template>
<script>
import {useDraftStore} from "@/stores/draft.js";
import {watch} from "vue";

export default {
    props: ["draft_id"],
    setup(props) {
        const draftStore = useDraftStore()
        watch(() => props.draft_id, draftStore.load, { immediate: true })
    }
}
</script>