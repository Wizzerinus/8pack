import {defineStore} from "pinia";
import {ref, watch} from "vue";

export const useAuthStore = defineStore("auth", () => {
    const token = ref(localStorage.getItem("access_key"))
    watch(token, (newValue) => localStorage.setItem("access_key", newValue))

    return { token }
})
