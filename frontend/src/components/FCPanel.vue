<template>
<div class='mb-4'>
    <div v-if='displayedFC.length > 0'>
        <v-card subtitle='Display Options'>
            <v-row align='center' class='pa-4'>
                <v-select
                    v-if='store.display == "snps"'
                    label='SNP Set'
                    v-model='set'
                    :items='store.snpsSets'
                    dense
                    class='d-inline-flex ma-0 pa-0 ml-4'>
                </v-select>
                <v-select
                    v-if='["fc", "partial"].includes(store.display)'
                    label='Task'
                    v-model='task'
                    :items='["All"].concat(store.tasks("fc"))'
                    dense
                    class='d-inline-flex ma-0 pa-0 ml-4'>
                </v-select>
                <v-checkbox
                    v-for='field in checkboxFields'
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
        <div v-if='store.display == "snps"'>
            <FC
                v-for='snps in displayedFC'
                :key="snps.id" :type='snps.type'
                :sub='snps.sub' :set='set' remap>
            </FC>
        </div>
        <div v-else-if='store.display == "partial"'>
            <FC 
                v-for="fc in displayedFC"
                :key="fc.id" :type='fc.type'
                :sub='fc.sub' :task='fc.task' remap>
            </FC>
        </div>
        <div v-else-if='store.display == "fc"'>
            <FC 
                v-for="fc in displayedFC"
                :key="fc.id" :type='fc.type'
                :sub='fc.sub' :task='fc.task' remap>
            </FC>
        </div>
        <div class='text-body-2 ml-4'>
            Create summary image:
            <div v-if='["fc", "partial"].includes(store.display)'>
                <v-btn @click='stats("mean")' 
                    class='ml-4'>Mean</v-btn>
                <v-btn @click='stats("std")' 
                    class='ml-4'>Standard Deviation</v-btn>
            </div>
            <div v-if='store.display == "snps"'>
                <v-btn @click='stats("snps")'
                    class='ml-4'>Distribution</v-btn>
            </div>
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
        checkboxFields() {
            const taskOrSet = this.store.display == 'snps' ? "Set" : "Task";
            return ["ID",taskOrSet].concat(Object.keys(this.store.demo))
        },
        display() {
            return this.store.display;
        },
        displayedFC() {
            const fcs = this.filteredFC;
            const n = this.NUM_FC_PAGE;
            return fcs.slice((this.page-1)*n, this.page*n);
        },
        filteredFC() {
            let bygroup = this.store.groups
                .reduce((acc, g) => acc || g.selected, false);
            const taskOrSet = this.store.display == 'snps'
                ? this.set : this.task;
            const fcs = bygroup
                ? this.store.groupSelected(this.store.display, taskOrSet)
                : this.store.selected(this.store.display, taskOrSet);
            return fcs.map(fc => {
                fc.type = this.store.display;
                return fc;
            });
        },
    },
    created() {
        if (this.store.snpsSets.length > 0) 
            this.set = this.store.snpsSets[0];
    },
    data() {
        return {
            page: 1,
            NUM_FC_PAGE: 18,
            task: 'All',
            loading: true,
            error: null,
            set: null,
        }
    },
    methods: {
        stats(type) {
            const fnames = this.filteredFC.map(fc => fc.fname);
            const formData = new FormData();
            formData.append('type', type)
            formData.append('cohort', this.store.cohort);
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
                if (['mean', 'std'].includes(type)) {
                    const task = this.task;
                    let groups = 
                        this.store.groups
                        .filter(g => g.selected)
                        .map(g => g.query).join(",");
                    if (!groups) {
                        groups = `custom ${fnames.length}`;
                    }
                    this.store.saved.push({
                        type: `stats-${type}-${this.store.display}`, 
                        label: `(${json.id}) stats-${type}-${this.store.display} | groups: ${groups}, task: ${task}`, 
                        data: json.data, 
                        id: json.id,
                    });
                    this.store.mathImage = null;
                } else if (type == 'snps') {
                    this.store.mathImage = json.data;
                }
                this.store.display = 'math';
            });
        }
    },
    setup() {
        const store = useCohortStore();
        return {
            store,
        }
    },
    watch: {
        display() {
            if (['fc', 'partial'].includes(this.store.display)) {
                this.store.labels['Set'] = false;
            } else if (this.store.display == 'snps') {
                this.store.labels['Task'] = false;
            }
        },
        task() {
            this.page = 1;
        },
    }
}
</script>

<style scoped>
</style>
