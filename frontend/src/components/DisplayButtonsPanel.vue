<template>
</template>

<script>
import { useCohortStore } from "@/stores/CohortStore";

export default {
    name: "DisplayButtonsPanel",
    setup() {
        const store = useCohortStore();
        return {
            store
        }
    },
}
</script>

<style scoped>
</style>
