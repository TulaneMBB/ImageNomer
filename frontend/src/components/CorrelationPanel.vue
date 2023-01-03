<template>
    <v-card title='Correlation' class='mb-2'>
        <v-card-subtitle>
            Find correlation between demographic features and FC for group
        </v-card-subtitle>
        <div>
            <div v-if='url' class='text-body-2 ma-4'>{{ url }}</div>
            <img v-if='imageData' 
                v-bind:src="'data:image/png;base64,'+imageData">
            <img v-if='pImageData' 
                v-bind:src="'data:image/png;base64,'+pImageData">
        </div>
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
            <v-btn @click='getCorr()' 
                key='go' value='Go' class='ml-4 mr-0'>Go</v-btn>
        </v-row>
    </v-card>
</template>

<script>
import { useCohortStore } from "@/stores/CohortStore";
import { enc } from './../functions.js';

export default {
    name: "CorrelationPanel",
    data() {
        return {
            imageData: null,
            pImageData: null,
            group: null,
            feat: null,
            respVar: null,
            task: null,
            url: null,
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
                : `&task=${enc(this.task)}`;
            this.url = (this.respVar == "fc")
                ? `/analysis/corr/fc?cohort=test&query=${enc(this.group)}&field=${enc(this.feat)}${taskPart}&remap`
                : `/analysis/corr/demo?cohort=test&query=${enc(this.group)}&field1=${enc(this.feat)}&field2=${enc(this.respVar)}`;
            fetch(this.url)
            .then(resp => resp.json())
            .then(json => {
                this.loading = false;
                if (json.err) {
                    this.error = json.err;
                    return;
                }
                if (this.respVar == "fc") {
                    this.store.corr = json.rdata;
                    this.store.p = json.pdata;
                    this.store.saved.push({
                        type: "fc-corr",
                        label: `(${json.rid}) fc-corr | group: ${this.group}, feat: ${this.feat}, task: ${this.task}`,
                        data: json.rdata,
                        id: json.rid,
                    });
                    this.store.saved.push({
                        type: "p-for-corr",
                        label: `(${json.pid}) p-for-corr | group: ${this.group}, feat: ${this.feat}, task: ${this.task}`,
                        data: json.pdata,
                        id: json.pid,
                        rid: json.rid,
                    });
                    this.imageData = json.rdata;
                    this.pImageData = json.pdata;
                    //this.store.display = "fc-corr";
                } else {
                    this.imageData = json.data;
                    this.pImageData = null;
                    //this.store.display = "corr";
                }
            })
            .catch(err => this.error = err);
        },
    }
}
</script>

<style scoped>
</style>
