<template>
    <div v-if="loading">Loading...</div>
    <div v-else-if="error">{{ error }}</div>
    <div v-else>
        <v-card title='FC' class='mb-2'>
            <v-card-subtitle>
                {{ store.fc.length }} FCs 
                <span v-if="store.selected('fc')">({{ store.selected('fc').length }} selected)</span>
            </v-card-subtitle>
            <div id='fc-list-div'>
                <v-checkbox 
                    v-for="fc in displayedFC" 
                    :key="fc.id"
                    v-model="fc.selected" 
                    :label="fc.fname" 
                    dense
                    hide-details 
                    class="mb-n7">
                </v-checkbox>
            </div>
            <v-pagination
                    v-model='fcPage'
                    :length="Math.ceil(filteredFC.length/NUM_FC_PAGE)"
                    total-visible='1'
                    class='pt-4 mb-n2'>
            </v-pagination>
            <v-text-field
                label="Filter FCs"
                v-model="search.fc"
                @input="resetFcPagination()"
                dense
                hide-details
                class='pa-4 pb-2'
            ></v-text-field>
        </v-card>
        <v-card title='Demographics' class='mb-2'>
            <v-card-text>
                <div v-for="field in Object.keys(store.demo)" :key="field">
                    <strong>{{ field }}</strong> {{ store.summary(field) }}
                </div>
            </v-card-text>
        </v-card>
        <v-card title='Groups' class='mb-2'>
            <v-card-subtitle>
                Create groups based on demographics<br>
                e.g., "age &gt; 180 and age &lt; 240"
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
    </div>
</template>

<script>
import { useCohortStore } from "@/stores/CohortStore";

export default {
    name: 'CohortInfo',
    data() {
        return {
            error: false,
            loading: true,
            search: {fc: ''},
            query: '',
            active: null,
            fcPage: 0,
            NUM_FC_PAGE: 6
        }
    },
    props: {
        cohort: String
    },
    created() {
        this.fetchCohort();
    },
    setup() {
        const store = useCohortStore();
        return {
            store
        }
    },
    computed: {
        displayedFC() {
            const fc = this.filteredFC;
            return fc.slice(this.fcPage*this.NUM_FC_PAGE,(this.fcPage+1)*this.NUM_FC_PAGE);
        },
        filteredFC() {
            const fc = this.store.fc.filter(fc => {
                const keep = fc.fname.includes(this.search['fc']);
                if (!keep && fc.selected) fc.selected = false;
                return keep;
            });
            return fc;
        }
    },
    methods: {
        activate(group) {
            this.active = group;
        },
        fetchCohort() {
            fetch(`/data/info?cohort=${this.cohort}`)
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
                this.store.feats = json.feats;
                this.store.groups = [{query: 'All', subs: this.store.subs}];
            })
            .catch(err => this.error = err);
        },
        getSubs(demo) {
            const subs = new Set();
            for (let key in demo) {
                Object.keys(demo[key]).forEach(sub => subs.add(sub));
            }
            return [...subs];
        },
        makeGroup() {
            fetch(`/data/group?cohort=${this.cohort}&query=${this.query}`)
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
        resetFcPagination() {
            this.fcPage = 0;
        },
        parseFC(fc) {
            fc.sort();
            return fc.map((fname, idx) => ({ id: idx, fname: fname, ...this.parseFname(fname) }));
        },
        parseFname(fname) {
            const parts = fname.split('_');
            const sub = parts[0];
            let task = '';
            parts.slice(1).forEach(part => {
                if (part.startsWith('task-')) {
                    task = part.substr(5);
                }
            });
            return {
                sub, task
            }
        }
    }
}
</script>

<style scoped>
/* #fc-list-div {
    max-height: 160px;
    overflow-y: scroll;
} */
</style>
