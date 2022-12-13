<template>
    <div v-if="loading">Loading...</div>
    <div v-else-if="error">{{ error }}</div>
    <div v-else>
        <v-card title='FC'>
            <v-card-subtitle>
                {{ store.fc.length }} FCs 
                <span v-if="store.selected('fc')">({{ store.selected('fc').length }} selected)</span>
            </v-card-subtitle>
            <div id='fc-list-div'>
                <v-lazy
                    v-for="fc in filteredFC" 
                    :key="fc.id">
                    <v-checkbox 
                        v-model="fc.selected" 
                        :label="fc.fname" 
                        dense
                        hide-details 
                        class="checkbox-dense">
                    </v-checkbox>
                </v-lazy>
            </div>
            <v-text-field
                label="Filter FCs"
                v-model="search.fc"
                dense
                hide-details
                class='padded'
            ></v-text-field>
        </v-card>
        <v-card title='Demographics'>
            <v-card-text>
                <div v-for="field in Object.keys(store.demo)" :key="field">
                    <strong>{{ field }}</strong> {{ store.summary(field) }}
                </div>
            </v-card-text>
        </v-card>
        <v-card title='Groups'>
            <v-card-subtitle>
                Create groups based on demographics<br>
                e.g., "age &gt; 180 and age &lt; 240"
            </v-card-subtitle>
            <v-row align='center'>
                <v-col cols='8'>
                    <v-text-field
                        label="Group Query"
                        v-model="query"
                        dense
                        hide-details
                        class='padded'
                    ></v-text-field>
                </v-col>
                <v-col cols='4'>
                    <v-btn @click='makeGroup' class='padded-alt'>Create</v-btn>
                </v-col>
            </v-row>
            <div class='checkbox-list-wrapper'>
                <v-checkbox 
                    v-for="group in store.groups" 
                    :key="group.query" 
                    v-model="group.selected" 
                    :label="`${group.query} (${group.subs.length})`" 
                    dense
                    hide-details 
                    class="checkbox-dense">
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
            active: null
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
        filteredFC() {
            const fc = this.store.fc.filter(fc => fc.fname.includes(this.search['fc']));
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
                const subs = this.getSubs(json.demo);
                this.store.subs = subs;
                this.store.groups = [{query: 'All', subs: [...subs]}];
            })
            .catch(err => this.error = err);
        },
        getSubs(demo) {
            const subs = new Set();
            for (let key in demo) {
                Object.keys(demo[key]).forEach(sub => subs.add(sub));
            }
            return subs;
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
#fc-list-div {
    max-height: 160px;
    overflow-y: scroll;
}
</style>
