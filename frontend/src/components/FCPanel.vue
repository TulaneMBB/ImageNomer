<template>
<div class='mb-4'>
    <div v-if='displayedFC.length > 0'>
        <v-card subtitle='Display Options'>
            <v-row align='center' class='pa-4'>
                <v-radio-group 
                    row 
                    class='d-inline-flex' 
                    v-model='store.fctype' 
                    label='Type'>
                    <v-radio 
                        label='FC' 
                        value='fc'></v-radio>
                    <v-radio 
                        label='Partial Correlation' 
                        value='partial'></v-radio>
                </v-radio-group>
                <v-select
                    label='Task'
                    v-model='task'
                    :items='["All"].concat(store.tasks("fc"))'
                    dense
                    class='d-inline-flex ma-0 pa-0 ml-4'>
                </v-select>
                <v-checkbox
                    v-for='field in ["ID","Task"].concat(Object.keys(store.demo))'
                    :key="field" 
                    v-model="store.labels[field]" 
                    :label="field"
                    dense
                    class="d-inline-flex ma-0 pa-0">
                </v-checkbox>
            </v-row>
        </v-card>
        <v-pagination
            v-model='page'
            :length="Math.ceil(filteredFC.length/NUM_FC_PAGE)"
            total-visible='10'>
        </v-pagination>
        <FC 
            v-for="fc in displayedFC"
            :key="fc.id" cohort='test' :sub='fc.sub' :task='fc.task' remap>
        </FC>
        <div class='text-body-2 ml-4'>
            Create summary image:
            <v-btn @click='stats("mean")' 
                class='ml-4'>Mean</v-btn>
            <v-btn @click='stats("std")' 
                class='ml-4'>Standard Deviation</v-btn>
        </div>
    </div>
    <div v-else class='text-h6 ma-0 ml-2'>
        No groups or subjects selected
    </div>
</div>
</template>

<script>
import { useCohortStore } from "@/stores/CohortStore";
import FC from './FC.vue';

export default {
    name: 'FCPanel',
    components: {
        FC
    },
    computed: {
        displayedFC() {
            const fcs = this.filteredFC;
            const n = this.NUM_FC_PAGE;
            return fcs.slice((this.page-1)*n, this.page*n);
        },
        filteredFC() {
            let bygroup = this.store.groups
                .reduce((acc, g) => acc || g.selected, false);
            const fcs = bygroup
                ? this.store.groupSelected(this.store.fctype, this.task)
                : this.store.selected(this.store.fctype, this.task);
            return fcs;
        },
    },
    data() {
        return {
            page: 1,
            NUM_FC_PAGE: 18,
            task: 'All',
            loading: true,
            error: null,
        }
    },
    methods: {
        stats(type) {
            let groups = 
                this.store.groups
                .filter(g => g.selected)
                .map(g => g.query).join(",");
            const task = this.task;
            const fnames = this.filteredFC.map(fc => fc.fname);
            if (!groups) {
                groups = `custom ${fnames.length}`;
            }
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
                    type: `stats-${type}-${this.store.fctype}`, 
                    label: `(${json.id}) stats-${type}-${this.store.fctype} | groups: ${groups}, task: ${task}`, 
                    data: json.data, 
                    id: json.id,
                });
                this.store.display = 'math';
            });
        }
    },
    setup() {
        const store = useCohortStore();
        return {
            store
        }
    },
    watch: {
        task() {
            this.page = 1;
        },
    }
}
</script>

<style scoped>
</style>
