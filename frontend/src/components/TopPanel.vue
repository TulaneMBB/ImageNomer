<template>
    <v-card style='padding-bottom: 8px;'>
        <v-card-title>{{ cohort }} cohort</v-card-title>
        <v-card-subtitle>{{ store.subs.size }} subjects</v-card-subtitle>
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