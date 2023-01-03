<template>
    <div class='mb-2'>
        <v-btn-toggle class='padded' v-model='store.display'>
            <!--<v-btn 
                v-for='field in Object.keys(store.demo)' 
                :key='field' :value='field'> 
                {{ field }}
            </v-btn>-->
            <v-btn key='pheno' value='pheno'>Phenotypes</v-btn>
            <v-btn key='fc' value='fc'>FC</v-btn>
            <v-btn key='fmri' value='fmri'>fMRI</v-btn>
            <v-btn key='smri' value='smri'>sMRI</v-btn>
            <v-btn key='weights' value='weights'>Weights</v-btn>
        </v-btn-toggle>
    </div>
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
