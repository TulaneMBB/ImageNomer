<template>
    <v-card
        title='Features'
        subtitle='Compare features from analysis runs'
        class='mb-2'
    >
        <v-select
            label='Feature File'
            v-model='fname'
            :items='this.store.feats'
            :change='loadFeat()'
            dense
            class='ma-0 ml-4 mr-4 pa-0'>
        </v-select>
        <v-row align='center' class='ma-0 ml-4 mr-4 pa-0'>
            <v-radio-group row v-model='labtype' @change='getTop()' label='Label Type'>
                <v-radio label='Raw' value='raw'></v-radio>
                <v-radio label='ROIs' value='rois'></v-radio>
                <v-radio label='Functional Networks' value='fns'></v-radio>
            </v-radio-group>
            <v-radio-group row v-model='rank' @change='getTop()' label='Ranking'>
                <v-radio label='Absolute' value='abs'></v-radio>
                <v-radio label='Positive' value='pos'></v-radio>
                <v-radio label='Negative' value='neg'></v-radio>
            </v-radio-group>
            <v-slider label='Number' min='3' max='50' step='1' @change='getTop()' v-model='ntop'>
            </v-slider>
            <v-col align='center' justify='center'>
                <v-select
                    label='Group'
                    v-model='group'
                    :items='["All"].concat(this.store.groups)'
                    :change='getTop()'
                    dense
                    class='ma-0 ml-4 mr-4 pa-0'>
                </v-select>
                <v-select
                    label='Input Task'
                    v-model='task'
                    :items='["All"].concat(this.store.tasks("fc"))'
                    :change='getTop()'
                    dense
                    class='ma-0 ml-4 mr-4 pa-0'>
                </v-select>
                <v-checkbox 
                    v-model='mult' 
                    @change='getTop()'>
                    Multiply
                </v-checkbox>
            </v-col>
        </v-row>
        <div v-if='fname' class='text-h6 text-center ml-4'>
            <div>{{ desc }}</div>
            <v-row align='center' justify='center' class='my-4'>
                <img v-bind:src="'data:image/png;base64,'+w">
                <img v-if='topdata' v-bind:src="'data:image/png;base64,'+topdata">
            </v-row>
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
            id: null,
            topdata: null,
            labtype: 'raw',
            rank: 'abs',
            ntop: 10,
            group: "All",
            task: "All",
            mult: false,
        }
    },
    methods: {
        alert(stuff) {
            console.log(stuff);
        },
        getTop() {
            this.loading = true;
            fetch(`/image/top?id=${this.id}&ntop=${this.ntop}&rank=${this.rank}&labtype=${this.labtype}&task=${this.task}&mult=${this.mult}&group=${encodeURIComponent(this.group)}`)
            .then(resp => resp.json())
            .then(json => {
                this.loading = false;
                if (json.err) {
                    this.error = json.err;
                    return;
                }
                this.topdata = json.data;
            })
            .catch(err => console.log(err));
        },
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
                this.id = json.id;
                this.getTop();
            })
            .catch(err => console.log(err));
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
