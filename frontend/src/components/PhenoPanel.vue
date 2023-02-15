<template>
    <div v-if='imageData'>
        <img v-bind:src="'data:image/png;base64,'+imageData">
    </div>
    <v-card>
        <v-card-title>Phenotypes</v-card-title>
        <v-card-subtitle>
            Display phenotypes associated with the cohort
        </v-card-subtitle>
        <div class='ma-4'>
            <v-select
                label='Field'
                :items='fields'
                v-model='field'
                dense>
            </v-select>
            <div v-if='field != null && subs.length > 0' class='text-body-2'>
                Selected groups: {{ groupsStr }} - 
                {{ subs.length}} subjects
            </div>
            <div v-else class='text-body-2'>
                No subject info - select a field and group(s)
            </div>
         </div>
    </v-card>
</template>


<script>
import { useCohortStore } from "@/stores/CohortStore";

export default {
    name: 'FC',
    computed: {
        fields() {
            return Object.keys(this.store.demo);
        },
        groups() {
            return this.store.groups.filter(g => g.selected);
        },
        groupsStr() {
            const groups = this.groups;
            if (groups.length == 0) 
                return "no groups selected";
            else
                return groups.map(g => g.query).join(', ');
        },
        subs() {
            if (!this.field || !this.groups) return [];
            const subs = new Set();
            this.groups.forEach(g => 
                g.subs.forEach(s => subs.add(s)));
            return [...subs].filter(s => 
                s in this.store.demo[this.field]);
        }
    },
    data() {
        return {
            field: '',
            error: false,
            imageData: '',
            loading: true,
        };
    },
    props: {
    },
    setup() {
        const store = useCohortStore();
        return {
            store
        }
    },
    methods: {
        fetchImage() {
            const groupsArr = this.groups;
            const groupsObj = {};
            groupsArr.forEach(g => {
                groupsObj[g.query] = g.subs;
            });
            const formData = new FormData();
            formData.append('cohort', this.store.cohort);
            formData.append('groups', JSON.stringify(groupsObj));
            formData.append('field', this.field);
            fetch(`/data/demo/hist`, {
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
                this.imageData = json.data;
            })
            .catch(err => this.error = err);
        }
    },
    watch: {
        field() {
            this.fetchImage();
        },
        groups() {
            this.fetchImage();
        }
    }
}
</script>

<style scoped>
</style>
