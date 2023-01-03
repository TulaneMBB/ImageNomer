<template>
        <div v-if='store.display == "corr" || store.display == "stats"'>
            <img v-bind:src="'data:image/png;base64,'+store.corr">
        </div>
        <div v-else-if='store.display == "fc-corr"'>
            <img v-bind:src="'data:image/png;base64,'+store.corr">
            <img v-bind:src="'data:image/png;base64,'+store.p">
        </div>
        <div v-else-if='store.display == "fc"'>
            <FCPanel></FCPanel>
        </div>
        <div v-else-if='store.display == "weights"'>
            <WeightsPanel></WeightsPanel>
        </div>
        <div v-else v-for='field in Object.keys(store.demo)' :key='field'>
            <Demographics v-if='store.display == field' cohort='test' :field='store.display'/>
        </div>
</template>

<script>
import { useCohortStore } from "@/stores/CohortStore";
import FCPanel from './FCPanel.vue';
import Demographics from './Demographics.vue';
import WeightsPanel from './WeightsPanel.vue';
//import { savedImageType } from './../functions.js'

export default {
    name: 'MainPanel',
    components: {
        FCPanel,
        Demographics,
        WeightsPanel
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
