<template>
        <div v-if='store.display == "corr" || store.display == "stats"'>
            <img v-bind:src="'data:image/png;base64,'+store.corr">
        </div>
        <div v-else-if='store.display == "fc-corr"'>
            <img v-bind:src="'data:image/png;base64,'+store.corr">
            <img v-bind:src="'data:image/png;base64,'+store.p">
        </div>
        <div v-else-if='store.display == "fc"'>
            <div v-if='store.groups.filter(g => g.selected).length > 0'>
                <v-card subtitle='Display Options'>
                    <v-select
                        label='Task'
                        v-model='task'
                        :items='["All"].concat(store.tasks("fc"))'
                        dense
                        class='d-inline-flex ma-0 pa-0'>
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
            <div>
                <span class='text-body-2'>Create summary image:</span>
                <v-btn @click='stats("mean")' class='ml-4'>Mean</v-btn>
                <v-btn @click='stats("std")' class='ml-4'>Standard Deviation</v-btn>
            </div>
        </div>
        <div v-else-if='store.display == "weights"'>
            <WeightsPanel></WeightsPanel>
        </div>
        <div v-else v-for='field in Object.keys(store.demo)' :key='field'>
            <Demographics v-if='store.display == field' cohort='test' :field='store.display'/>
        </div>
</template>

<script>
// FC should go into explore or fcs view
import FC from './FC.vue'
import { useCohortStore } from "@/stores/CohortStore";
import Demographics from './Demographics.vue';
import WeightsPanel from './WeightsPanel.vue';
import { savedImageType } from './../functions.js'

export default {
    name: 'MainPanel',
    data() {
        return {
            page: 1,
            NUM_FC_PAGE: 18,
            task: 'All',
            display: {},
            loading: true,
            error: null,
        }
    },
    components: {
        FC,
        Demographics,
        WeightsPanel
    },
    computed: {
        filteredGroupFC() {
            const fcs = this.store.groupSelected('fc', this.task);
            const n = this.NUM_FC_PAGE;
            return fcs.filter(fc => fc.num >= (this.page-1)*n && fc.num < this.page*n);
        },
    },
    methods: {
        savedImageType,
        stats(type) {
            const groups = this.store.groups.filter(g => g.selected).map(g => g.query).join(",");
            const task = this.task;
            const fnames = this.store.groupSelected('fc', this.task).map(fc => fc.fname);
            const formData = new FormData();
            formData.append('type', type)
            formData.append('cohort', 'test');
            formData.append('fnames', JSON.stringify(fnames));
            formData.append('remap', true);
            fetch(`/analysis/stats`, {
                method: 'POST',
                body: formData
            })
            .then(resp => resp.json())
            .then(json => {
                this.loading = false;
                if (json.err) {
                    this.error = json.err;
                    return;
                }
                this.store.saved.push({
                    type: 'stats', 
                    label: `(${json.id}) stats:${type} | groups: ${groups}, task: ${task}`, 
                    data: json.data, 
                    id: json.id,
                });
                this.store.corr = json.data;
                this.store.display = "stats";
            });
        }
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
