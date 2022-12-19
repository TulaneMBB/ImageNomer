<template>
    <v-card
        title='Features'
        subtitle='Compare features from analysis runs'
    >
        <v-select
            label='Feature File'
            v-model='fname'
            :items='this.store.feats'
            :change='loadFeat()'
            dense
            class='ma-0 ml-4 pa-0'>
        </v-select>
        <div v-if='fname' class='text-body-1'>
            <div>{{ fname }}</div>
            <div>{{ desc }}</div>
            <img v-bind:src="'data:image/png;base64,'+w">
        </div>
    </v-card>
</template>

<script>
import { useCohortStore } from "@/stores/CohortStore";

export default {
    name: 'FeaturesPanel',
    data() {
        return {
            fname: '',
            loading: null,
            error: null,
            desc: '',
            nsubs: 0,
            w: null,
            b: null
        }
    },
    methods: {
        loadFeat() {
            if (!this.fname)
                return;
            this.loading = true;
            fetch(`/data/feature?cohort=test&fname=${this.fname}&remap`)
            .then(resp => resp.json())
            .then(json => {
                this.loading = false;
                if (json.err) {
                    this.error = json.err;
                    return;
                }
                this.desc = json.desc;
                this.nsubs = json.nsubs;
                this.w = json.w;
                this.b = json.b;
            });
        }
    },
    setup() {
        const store = useCohortStore();
        return {
            store
        }
    }
}
</script>

<style scoped>
</style>