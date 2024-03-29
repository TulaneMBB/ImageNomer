<template>
    <div v-if="cohort == null">Loading...</div>
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
                e.g., "age &gt; 180"
                or "sex == 'F' and age &lt; 200"
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
import { mapState } from 'pinia';
import { useCohortStore } from "@/stores/CohortStore";
import { enc } from './../functions.js';

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
        this.store.getCohorts();
    },
    computed: {
        ...mapState(useCohortStore, ['cohort']),
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
            .catch(err => {
                console.log(err);
                alert('An error occurred; are you sure you spelled everything correctly? Field names are case-sensitive.');
            });
        },
        resetPage() {
            this.page = 1;
        },
    },
    setup() {
        const store = useCohortStore();
        return {
            store
        }
    },
    watch: {
        cohort() {
            this.store.fetchCohort(this.cohort);
        }
    }
}
</script>

<style scoped>
</style>
