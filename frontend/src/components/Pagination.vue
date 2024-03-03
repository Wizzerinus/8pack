<template>
    <div class="flex items-center mt-4 ms-7">
        <h3 class="me-8">{{ name }}</h3>
        <div class="join">
            <button
                v-for="index in total_pages"
                class="join-item btn"
                :class="{ 'btn-active': index - 1 === current_page }"
                @click="current_page = index - 1"
            >
                {{ index }}
            </button>
        </div>
    </div>

    <div class="grid grid-cols-2 lg:grid-cols-3 2xl:grid-cols-4 m-4">
        <component :is="subcomponent" v-for="item in items" :item="item"></component>
    </div>
</template>

<script>
import { ref, watch } from "vue"
import { get } from "@/util.js"

export default {
    props: ["subcomponent", "url", "name"],
    setup(props) {
        const items = ref([])
        const total_objects = ref(0)
        const total_pages = ref(0)
        const current_page = ref(0)

        const loadPage = (set_total_pages = false) => {
            get(`${props.url}?page_num=${current_page.value}`)
                .then((e) => e.json())
                .then((e) => {
                    items.value = e.data
                    total_objects.value = e.total_objects
                    if (set_total_pages)
                        total_pages.value =
                            e.data.length > 0 ? Math.ceil(e.total_objects / e.data.length) : 1
                })
        }
        loadPage(true)
        watch(current_page, () => loadPage())

        return { items, total_objects, total_pages, current_page }
    },
}
</script>
