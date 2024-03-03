import { defineStore } from "pinia"
import { ref } from "vue"

export const useAlertStore = defineStore("alert", () => {
    const alert = ref("")
    const alert_type = ref("alert-error")

    const set_alert = (text, type = "alert-error") => {
        alert.value = text
        alert_type.value = type
    }

    const clear_alert = () => (alert.value = "")
    return { alert, alert_type, set_alert, clear_alert }
})
