<template>
    <div class='mb-2'>
        <v-btn-toggle class='padded' v-model='store.display'>
            <v-btn key='pheno' value='pheno'>Phenotypes</v-btn>
            <v-btn key='fc' value='fc'>FC</v-btn>
            <v-btn key='partial' value='partial'>PC</v-btn>
            <v-btn key='snps' value='snps'>SNPs</v-btn>
            <v-btn key='comp' value='comp'>Decomposition</v-btn>
            <v-btn key='corr' value='corr'>Correlation</v-btn>
            <v-btn key='weights' value='weights'>Weights</v-btn>
            <v-btn key='math' value='math'>Image Math</v-btn>
        </v-btn-toggle>
    </div>
    <div v-if='store.display == "pheno"'>
        <PhenoPanel></PhenoPanel>
    </div>
    <div v-else-if='["fc", "partial", "snps"].includes(store.display)'>
        <FCPanel></FCPanel>
    </div>
    <div v-else-if='store.display == "comp"'>
        <DecompositionPanel></DecompositionPanel>
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
import DecompositionPanel from './DecompositionPanel.vue';
import CorrelationPanel from './CorrelationPanel.vue';
import WeightsPanel from './WeightsPanel.vue';
import ImageMathPanel from './ImageMathPanel.vue';

export default {
    name: 'MainPanel',
    components: {
        PhenoPanel,
        FCPanel,
        DecompositionPanel,
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
