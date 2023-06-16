<template>
<v-sheet class='ma-1 pa-1'>
    <v-sheet class='text-h4 mb-2'>ImageNomer</v-sheet>
    <v-sheet class='d-inline-flex'>
        <v-select 
            label='Cohort'
            :items='store.cohorts'
            v-model='cohort'
            class='d-inline-flex mr-n6'
        ></v-select>
        <v-btn class='d-inline-flex ma-1 mt-2'>View Documentation</v-btn>
        <v-btn class='d-inline-flex ma-1 mt-2'>Visit GitHub</v-btn>
    </v-sheet>
</v-sheet>
</template>

<script>
import { mapWritableState } from 'pinia';
import { useCohortStore } from "@/stores/CohortStore";

export default {
    name: 'TopPanel',
    computed: {
        ...mapWritableState(useCohortStore, ['cohort'])
    },
    setup() {
        const store = useCohortStore();
        return {
            store
        }
    },
    watch: {
        cohort() {
            this.store.fetchCohort(this.store.cohort);
            console.log('got here');
        }
    },
}
</script>

<style scope>
#imagenomer-h {
    /*background-color: #fee;*/
    border: 1px solid #ddd;
    padding: 5px;
    padding-left: 10px;
    padding-right: 10px;
    margin-bottom: 10px;
    border-radius: 3px;
}
/*#imagenomer-h a {
    margin-left: 5px;
}*/
</style>
