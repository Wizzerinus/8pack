<template>
    <div class="card m-3 bg-base-100 shadow-xl">
        <figure>
            <img
                :src="item.front_card.art_image"
                :title="item.front_card.name"
                :alt="item.front_card.name"
            />
        </figure>
        <div class="card-body">
            <h2 class="card-title">Draft #{{ item.id }} by {{ item.player_name }}</h2>
            <p>Created at {{ humanize_date(item.date) }}</p>
            <p>Played {{ item.run_count }} time{{ get_s(item.run_count) }}</p>
            <div class="card-actions justify-end">
                <RouterLink :to="`/drafts/${item.id}`" class="btn btn-primary">Play now</RouterLink>
                <RouterLink :to="`/drafts/${item.id}/results`" class="btn btn-accent">
                    See results
                </RouterLink>
            </div>
        </div>
    </div>
</template>
<script>
import { get_s, humanize_date } from "../util.js"

export default {
    methods: { get_s, humanize_date },
    props: ["item"],
}
</script>
