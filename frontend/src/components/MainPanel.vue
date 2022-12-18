<template>
    <div id='main'>
        <div v-if='store.display == "corr"'>
            <img v-bind:src="'data:image/png;base64,'+store.corr">
        </div>
        <div v-if='store.display == "fc"'>
            <div v-if='store.groups.filter(g => g.selected).length > 0'>
                <v-card subtitle='Display Options'>
                    <v-select
                        label='Task'
                        v-model='task'
                        :items='["All"].concat(store.tasks("fc"))'
                        dense
                        class='d-inline-flex ma-0 ml-4 pa-0'>
                    </v-select>
                    <v-checkbox
                        v-for='field in ["ID","Task"].concat(Object.keys(store.demo))'
                        :key="field" 
                        v-model="store.labels[field]" 
                        :label="field"
                        dense
                        class="d-inline-flex ma-0 pa-0">
                    </v-checkbox>
                </v-card>
                <v-pagination
                    v-model='page'
                    :length="Math.ceil(store.groupSelected('fc', task).length/NUM_FC_PAGE)"
                    total-visible='10'>
                </v-pagination>
                <FC 
                    v-for="fc in filteredGroupFC"
                    :key="fc.id" cohort='test' :sub='fc.sub' :task='fc.task' :display='display' remap>
                </FC>
            </div>
            <div v-else>
                <FC 
                    v-for="fc in store.selected('fc')" 
                    :key="fc.id" cohort='test' :sub='fc.sub' :task='fc.task' :display='display' remap>
                </FC>
            </div>
        </div>
        <div v-else v-for='field in Object.keys(store.demo)' :key='field'>
            <Demographics v-if='store.display == field' cohort='test' :field='store.display'/>
        </div>
    </div>
</template>

<script>
// FC should go into explore or fcs view
import FC from './FC.vue'
import { useCohortStore } from "@/stores/CohortStore";
import Demographics from './Demographics.vue';

export default {
    name: 'MainPanel',
    data() {
        return {
            page: 1,
            NUM_FC_PAGE: 18,
            task: 'All',
            display: {},
        }
    },
    components: {
        FC,
        Demographics
    },
    computed: {
        filteredGroupFC() {
            const fcs = this.store.groupSelected('fc', this.task);
            const n = this.NUM_FC_PAGE;
            return fcs.filter(fc => fc.num >= (this.page-1)*n && fc.num < this.page*n);
        },
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