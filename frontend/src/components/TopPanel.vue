<template>
    <v-card class='mb-2'>
        <v-card-title>ImageNomer</v-card-title>
        <v-card-subtitle>{{ cohort }} cohort</v-card-subtitle>
    </v-card>
</template>

<script>
import { useCohortStore } from "@/stores/CohortStore";

export default {
    name: 'CohortInfo',
    props: {
        cohort: String,
    },
    setup() {
        const store = useCohortStore();
        return {
            store
        }
    }
}
</script>

<style>
</style>
