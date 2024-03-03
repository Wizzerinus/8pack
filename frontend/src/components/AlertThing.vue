<template>
    <div role="alert" class="alert mt-4 mb-4 relative" :class="alert_type" v-if="alert">
        <span>{{ alert }}</span>
        <button class="btn btn-sm btn-circle btn-ghost absolute right-2 top-2" @click="clear_alert">
            <SvgClose />
        </button>
    </div>
</template>
<script>
import { useAlertStore } from "@/stores/alert.js"
import { storeToRefs } from "pinia"
import SvgClose from "@/components/svg/SvgClose.vue"

export default {
    components: { SvgClose },
    setup() {
        const alertStore = useAlertStore()

        const clear_alert = alertStore.clear_alert
        const { alert, alert_type } = storeToRefs(alertStore)

        return { alert, alert_type, clear_alert }
    },
}
</script>
