import { defineStore } from "pinia"
import { computed, ref, watch } from "vue"
import { post } from "@/util.js"
import { useAlertStore } from "@/stores/alert.js"

export const useAuthStore = defineStore("auth", () => {
    const token = ref(localStorage.getItem("access_key"))
    watch(token, (newValue) => localStorage.setItem("access_key", newValue))

    const user_data = ref(null)
    const load = () => {
        if (token.value === "" || user_data.value !== null) return
        post("users/token", {}, token.value)
            .then((e) => e.json())
            .then(_process_error)
            .then((e) => (user_data.value = e))
            .catch(() => {})
    }

    const user_login = computed(() => user_data.value.login)
    const logged_in = computed(() => user_data.value !== null)

    const _process_error = (e) => {
        const store = useAlertStore()
        if (!e.detail) {
            store.clear_alert()
            return e
        }
        token.value = ""
        store.set_alert(e.detail)
        return Promise.reject("already failed")
    }
    const _login_to_url = (url) => (login, password) => {
        if (!login || !password) return
        post(url, { login, password })
            .then((e) => e.json())
            .then(_process_error)
            .then((e) => (token.value = e.token || ""))
            .then(load)
            .catch(() => {})
    }

    const try_login = _login_to_url("users/login")
    const register = _login_to_url("users/register")

    const logout = () => {
        user_data.value = null
        token.value = ""
        console.log("logged out")
    }

    return {
        token,
        user_data,
        load,
        logged_in,
        try_login,
        logout,
        register,
        _login_to_url,
        _process_error,
        user_login,
    }
})
