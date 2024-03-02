<template>
    <nav class="navbar bg-neutral text-neutral-content">
        <div class="container mx-auto flex">
            <div class="flex-grow">
                <RouterLink to="/" class="btn btn-ghost text-xl">8pack</RouterLink>
            </div>
            <div class="flex-grow-0">
                <NavbarLogin />
            </div>
        </div>
    </nav>

    <main class="container mx-auto mt-3">
        <AlertThing />
        <RouterView />
    </main>
</template>
<script>
import NavbarLogin from "@/components/NavbarLogin.vue";
import AlertThing from "@/components/AlertThing.vue";

export default {
    components: {AlertThing, NavbarLogin}
}
</script>