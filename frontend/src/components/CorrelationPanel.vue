<template>
    <v-card title='Correlation' class='mb-2'>
        <v-card-subtitle>Find correlation between demographic features and FC for group</v-card-subtitle>
        <v-row align='center' class='pa-4 pt-3 pb-3 ma-0'>
            <v-select 
                v-model='group'
                :items='store.groups' 
                item-title='query' 
                label='Group' 
                hide-details dense class='pa-0 ma-0'>
            </v-select>
            <v-select 
                v-model='feat'
                :items='Object.keys(store.demo)' 
                label='Demographic Feature' 
                hide-details dense class='pa-0 ma-0 ml-4'>
            </v-select>
            <v-select 
                v-model='respVar'
                :items="Object.keys(store.demo).concat(['fc'])" 
                label='Response Var' 
                hide-details dense class='pa-0 ma-0 ml-4'>
            </v-select>
            <v-select
                v-model='task'
                :items='["All"].concat(store.tasks("fc"))'
                label='Task'
                hide-details dense class='pa-0 ma-0 ml-4'>
            </v-select>
            <v-btn @click='getCorr()' key='go' value='Go' class='ml-4 mr-0'>Go</v-btn>
        </v-row>
    </v-card>
</template>

<script>
import { useCohortStore } from "@/stores/CohortStore";

export default {
    name: "CorrelationPanel",
    data() {
        return {
            group: null,
            feat: null,
            respVar: null,
            task: null,
        };
    },
    setup() {
        const store = useCohortStore();
        return {
            store
        };
    },
    methods: {
        getCorr() {
            const taskPart = (this.task == "All")
                ? ""
                : `&task=${this.task}`;
            const url = (this.respVar == "fc")
                ? `/analysis/corr/fc?cohort=test&query=${this.group}&field=${this.feat}${taskPart}&remap`
                : `/analysis/corr/demo?cohort=test&query=${this.group}&field1=${this.feat}&field2=${this.respVar}`;
            fetch(url)
            .then(resp => resp.json())
            .then(json => {
            this.loading = false;
            if (json.err) {
                this.error = json.err;
                return;
            }
            this.store.corr = json.data;
            if (this.respVar == "fc") {
                this.store.saved.push({
                    type: "corr",
                    label: `(${json.id}) corr | group: ${this.group}, feat: ${this.feat}, task: ${this.task}`,
                    data: json.data,
                    id: json.id,
                });
            }
            this.store.display = "corr";
            })
            .catch(err => this.error = err);
        },
    }
}
</script>

<style scoped>
</style>