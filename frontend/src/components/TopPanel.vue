<template>
<v-sheet class='ma-1 pa-1'>
    <!--<v-sheet class='text-h4 mb-2'>ImageNomer</v-sheet>-->
    <v-img class='ma-2' src='./../assets/LogoImageNomer.png' alt='ImageNomer' height='54'></v-img>
    <v-divider thickness='1'></v-divider>
    <v-sheet class='d-inline-flex mt-2 mb-2'>
        <v-select 
            label='Cohort'
            :items='store.cohorts'
            v-model='cohort'
            class='d-inline-flex mr-n6'
        ></v-select>
        <div class='text-body-1'>
            <a href='https://imagenomer.readthedocs.io/en/latest/' class='mr-2' target='_blank'>Documentation</a>
            <a href='https://github.com/TulaneMBB/ImageNomer' class='mr-2' target='_blank'>GitHub</a>
            <a href='mailto:aorlichenko@tulane.edu' target='_blank'>Report Bugs</a>
        </div>
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
