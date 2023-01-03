<template>
    <div v-if="loading">Loading...</div>
    <div v-else-if="error">{{ error }}</div>
    <div v-else>
        <v-card title='Subjects' class='mb-2'>
            <v-card-subtitle>
                {{ store.subs.length }} subjects
                <span v-if="store.selected">
                    ({{ store.selected().length }} selected)
                </span>
            </v-card-subtitle>
            <div id='sub-list-div'>
                <v-checkbox 
                    v-for="sub in displayed" 
                    :key="sub.id"
                    v-model="sub.selected" 
                    :label="sub.id" 
                    dense
                    hide-details 
                    class="mb-n7">
                </v-checkbox>
            </div>
            <v-pagination
                v-model='page'
                :length="Math.ceil(filtered.length/NUM_PAGE)"
                total-visible='1'
                class='pt-4 mb-n2'>
            </v-pagination>
            <v-text-field
                label="Filter Subjects"
                v-model="search"
                @input="resetPage()"
                dense
                hide-details
                class='pa-4 pb-2'>
            </v-text-field>
        </v-card>
        <v-card title='Groups' class='mb-2'>
            <v-card-subtitle>
                Create groups based on phenotypes<br>
                e.g., "age &gt; 180 and age &lt; 240"<br>
                or "sex == 'F'"
            </v-card-subtitle>
            <v-row align='center'>
                <v-text-field
                    label="Group Query"
                    v-model="query"
                    dense
                    hide-details
                    class='ma-4 mr-2'
                ></v-text-field>
                <v-btn @click='makeGroup' class='mr-6'>Create</v-btn>
            </v-row>
            <div class='pb-6'>
                <v-checkbox 
                    v-for="group in store.groups" 
                    :key="group.query" 
                    v-model="group.selected" 
                    :label="`${group.query} (${group.subs.length})`" 
                    dense
                    hide-details 
                    class="mb-n7">
                </v-checkbox>
            </div>
        </v-card>
        <v-card title='Phenotypes' class='mb-2'>
            <v-card-text>
                <div 
                    v-for="field in Object.keys(store.demo)" 
                    :key="field">
                    <strong>{{ field }}</strong> {{ store.summary(field) }}
                </div>
            </v-card-text>
        </v-card>
    </div>
</template>

<script>
import { useCohortStore } from "@/stores/CohortStore";
import { enc, getFnameField } from './../functions.js';

export default {
    name: 'CohortInfo',
    data() {
        return {
            error: false,
            loading: true,
            search: '',
            query: '',
            page: 1,
            NUM_PAGE: 6
        }
    },
    created() {
        this.fetchCohort();
    },
    computed: {
        displayed() {
            const subs = this.filtered;
            return subs.slice((this.page-1)*this.NUM_PAGE, 
                this.page*this.NUM_PAGE);
        },
        filtered() {
            const inc = this.store.subs.filter(
                sub => sub.id.includes(this.search));
            return inc;
        }
    },
    methods: {
        fetchCohort() {
            fetch(`/data/info?cohort=${enc(this.cohort)}`)
            .then(resp => resp.json())
            .then(json => {
                this.loading = false;
                if (json.err) {
                    this.error = json.err;
                    return;
                }
                this.store.fc = this.parseFC(json.fc);
                this.store.demo = json.demo;
                this.store.subs = this.getSubs(json.demo);
                this.store.weights = json.weights;
                this.store.groups = [{query: 'All', 
                    subs: this.store.subs.map(sub => sub.id)}];
            })
            .catch(err => this.error = err);
        },
        getSubs(demo) {
            let subs = new Set();
            for (let key in demo) {
                Object.keys(demo[key]).forEach(
                    sub => subs.add(sub));
            }
            subs = [...subs].map(sub => ({id: sub, selected: false}));
            return subs;
        },
        makeGroup() {
            fetch(`/data/group?cohort=${enc(this.cohort)}&query=${enc(this.query)}`)
            .then(resp => resp.json())
            .then(json => {
                if (json.err) {
                    alert(json.err);
                    return;
                }
                this.store.groups.push({query: this.query, subs: json});
            })
            .catch(err => alert(err));
        },
        resetPage() {
            this.page = 1;
        },
        parseFC(jsonfc) {
            // id is just an index (from the map call)
            jsonfc.sort();
            return jsonfc.map((fname, idx) => {
                return {
                    id: idx, 
                    fname: fname, 
                    ...this.parseFname(fname) 
                }
            });
        },
        parseFname(fname) {
            const sub = fname.split('_')[0];
            const task = getFnameField(fname, 'task');
            /*const parts = fname.split('_');
            const sub = parts[0];
            let task = '';
            parts.slice(1).forEach(part => {
                if (part.startsWith('task-')) {
                    task = part.substr(5);
                }
            });*/
            return {
                sub, task
            }
        }
    },
    props: {
        cohort: String
    },
    setup() {
        const store = useCohortStore();
        return {
            store
        }
    },
}
</script>

<style scoped>
</style>
