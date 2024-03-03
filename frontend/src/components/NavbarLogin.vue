<template>
    <div v-if="!logged_in" class="text-base-content">
        <input
            type="text"
            class="input input-bordered inline-block input-sm me-3"
            @keyup.enter="do_login"
            placeholder="Login"
            v-model="login"
        />
        <input
            type="password"
            class="input input-bordered inline-block input-sm me-3"
            @keyup.enter="do_login"
            placeholder="Password"
            v-model="password"
        />
        <button type="button" class="btn btn-sm me-3" @click="do_login">Login</button>
        <button type="button" class="btn btn-sm" @click="do_register">Register</button>
    </div>
    <div v-else>
        <span class="me-3"
            >Logged in as <code>{{ user_login }}</code></span
        >
        <button type="button" class="btn btn-sm" @click="do_logout">Logout</button>
    </div>
</template>
<script>
import { useAuthStore } from "@/stores/auth.js"
import { storeToRefs } from "pinia"
import { ref } from "vue"

export default {
    setup() {
        const authStore = useAuthStore()
        const { logged_in, user_login } = storeToRefs(authStore)
        const login = ref(""),
            password = ref("")
        const do_login = () => authStore.try_login(login.value, password.value)
        const do_register = () => authStore.register(login.value, password.value)
        const do_logout = () => authStore.logout()

        return { logged_in, user_login, login, password, do_login, do_logout, do_register }
    },
}
</script>
