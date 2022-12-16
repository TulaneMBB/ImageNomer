<template>
    <v-container>
        <v-btn-toggle class='padded' v-model='store.display'>
            <v-btn v-for='field in Object.keys(store.demo)' :key='field' :value='field'> 
                {{ field }}
            </v-btn>
            <v-btn key='fc' value='fc'>FC</v-btn>
        </v-btn-toggle>
        <v-card title='Correlation' id='correlation'>
            <v-card-subtitle>Find correlation between demographic features and FC for group</v-card-subtitle>
            <v-row align='center' class='padded'>
                <v-select 
                    v-model='group'
                    cols='2'
                    :items='store.groups' 
                    item-title='query' 
                    label='Group' 
                    hide-details dense class='padded'>
                </v-select>
                <v-select 
                    v-model='feat'
                    cols='2'
                    :items='Object.keys(store.demo)' 
                    label='Demographic Feature' 
                    hide-details dense class='padded'>
                </v-select>
                <v-select 
                    v-model='respVar'
                    cols='2'
                    :items="Object.keys(store.demo).concat(['fc'])" 
                    label='Response Var' 
                    hide-details dense class='padded'>
                </v-select>
                <v-select
                    v-model='task'
                    cols='2'
                    :items='["All"].concat(store.tasks)'
                    label='Task'
                    hide-details dense class='padded'>
                </v-select>
                <v-btn cols='2' @click='getCorr()' key='go' value='Go' class='padded-alt'>Go</v-btn>
            </v-row>
        </v-card>
    </v-container>
</template>

<script>
import { useCohortStore } from "@/stores/CohortStore";

export default {
    name: 'BottomPanel',
    data() {
        return {
            group: null,
            feat: null,
            respVar: null,
            task: null
        }
    },
    setup() {
        const store = useCohortStore();
        return {
            store
        }
    },
    methods: {
        getCorr() {
            const taskPart = (this.task == 'All')
                ? ''
                : `&task=${this.task}`;
            const url = (this.respVar == 'fc') 
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
                this.store.display = "corr";
            })
            .catch(err => this.error = err);
        }
    }
}
</script>

<style scoped>
#correlation {
    max-width: 800px;
}
</style>