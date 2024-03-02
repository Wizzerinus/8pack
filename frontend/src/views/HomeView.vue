<template>
    <Pagination :subcomponent="Draft" url="drafts" name="Recent drafts" />
</template>

<script>
import Pagination from "@/components/Pagination.vue";
import Draft from "@/components/Draft.vue";

export default {
    computed: {
        Draft() {
            return Draft
        }
    },
    components: {Pagination}
}
</script>
