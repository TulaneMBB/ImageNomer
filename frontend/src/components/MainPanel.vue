<template>
    <div class='mb-2'>
        <v-btn-toggle class='padded' v-model='store.display'>
            <v-btn key='pheno' value='pheno'>Phenotypes</v-btn>
            <v-btn key='fc' value='fc'>FC</v-btn>
            <v-btn key='corr' value='corr'>Correlation</v-btn>
            <v-btn key='weights' value='weights'>Weights</v-btn>
            <v-btn key='math' value='math'>Image Math</v-btn>
            <v-btn key='fmri' value='fmri'>fMRI</v-btn>
            <v-btn key='smri' value='smri'>sMRI</v-btn>
        </v-btn-toggle>
    </div>
    <div v-if='store.display == "pheno"'>
        <PhenoPanel cohort='test'></PhenoPanel>
    </div>
    <div v-else-if='store.display == "fc"'>
        <FCPanel></FCPanel>
    </div>
    <div v-else-if='store.display == "corr"'>
        <CorrelationPanel></CorrelationPanel>
    </div>
    <div v-else-if='store.display == "weights"'>
        <WeightsPanel></WeightsPanel>
    </div>
    <div v-else-if='store.display == "math"'>
        <ImageMathPanel></ImageMathPanel>
    </div>
</template>

<script>
import { useCohortStore } from "@/stores/CohortStore";
import PhenoPanel from './PhenoPanel.vue';
import FCPanel from './FCPanel.vue';
import CorrelationPanel from './CorrelationPanel.vue';
import WeightsPanel from './WeightsPanel.vue';
import ImageMathPanel from './ImageMathPanel.vue';

export default {
    name: 'MainPanel',
    components: {
        PhenoPanel,
        FCPanel,
        CorrelationPanel,
        WeightsPanel,
        ImageMathPanel,
    },
    setup() {
        const store = useCohortStore();
        return {
            store
        }
    }
}
</script>

<style scoped>
</style>
