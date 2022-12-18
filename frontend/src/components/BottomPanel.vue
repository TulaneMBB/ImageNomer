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
                    :items='store.groups' 
                    item-title='query' 
                    label='Group' 
                    hide-details dense class='padded'>
                </v-select>
                <v-select 
                    v-model='feat'
                    :items='Object.keys(store.demo)' 
                    label='Demographic Feature' 
                    hide-details dense class='padded'>
                </v-select>
                <v-select 
                    v-model='respVar'
                    :items="Object.keys(store.demo).concat(['fc'])" 
                    label='Response Var' 
                    hide-details dense class='padded'>
                </v-select>
                <v-select
                    v-model='task'
                    :items='["All"].concat(store.tasks("fc"))'
                    label='Task'
                    hide-details dense class='padded'>
                </v-select>
                <v-btn @click='getCorr()' key='go' value='Go' class='padded-alt'>Go</v-btn>
            </v-row>
        </v-card>
        <v-card 
            title='Image Math' 
            subtitle='Perform operations on images, e.g., correlation images'
            v-if='store.saved.filter(item => item.type == "corr").length > 0'
        >
            <v-row
                align='center' 
                class='padded'>
                <v-text-field
                    label='Expression (e.g. "A-B", "std(A,BA,C)")'
                    v-model='expr'
                    hide-details dense class='padded'>
                </v-text-field>
                <v-btn @click='doImageMath()' key='go' value='Go' class='padded-alt'>Go</v-btn>
            </v-row>
            <h3>Images</h3>
            <div class='checkbox-list-wrapper'>
                <v-checkbox 
                    v-for="item in store.saved.filter(item => item.type == 'corr')" 
                    :key="item.num" 
                    v-model="item.selected" 
                    :label="item.label"
                    dense
                    hide-details 
                    class="checkbox-dense">
                </v-checkbox>
            </div>
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
            task: null,
            expr: ''
        }
    },
    setup() {
        const store = useCohortStore();
        return {
            store
        }
    },
    methods: {
        doImageMath() {
            fetch(`/math/image?expr=${encodeURIComponent(this.expr)}`)
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
        },
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
                if (this.respVar == 'fc') {
                    this.store.saved.push(
                        {
                            type: 'corr', 
                            label: `(${json.id}) group: ${this.group}, feat: ${this.feat}, task: ${this.task}`, 
                            data: json.data, 
                            id: json.id,
                        });
                }
                this.store.display = "corr";
            })
            .catch(err => this.error = err);
        }
    }
}
</script>

<style scoped>
/*#correlation {
    max-width: 800px;
}*/
</style>