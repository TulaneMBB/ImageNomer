<template>
    <v-card
        title='Weights'
        subtitle='Compare model weights from analysis runs'
        class='mb-2'
    >
        <v-select
            label='Weights File'
            v-model='fname'
            :items='this.store.weights'
            :change='loadWeights()'
            dense
            class='ma-0 ml-4 mr-4 pa-0'>
        </v-select>
        <v-row align='center' class='ma-0 ml-4 mr-4 pa-0'>
            <v-select
                label='Multiply by Features'
                v-model='mult'
                :items='["no", "mean", "std"]'
                @change='loadWeights()'
                dense
                class='ma-0 pa-0'>
            </v-select>
            <v-select
                label='Group'
                v-model='query'
                :items='this.store.groups.map(g => g.query)'
                @change='loadWeights()'
                dense
                class='ma-0 ml-4 mr-4 pa-0'>
            </v-select>
            <v-select
                label='Input Task'
                v-model='task'
                :items='["All"].concat(this.store.tasks("fc"))'
                @change='loadWeights()'
                dense
                class='ma-0 pa-0'>
            </v-select>
        </v-row>
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
            <v-col>
                <v-slider label='Number' v-model='ntop' min='3' max='30' step='1' @change='getTop()'>
                </v-slider>
                <v-btn @click='getTop()'>Refresh</v-btn>
            </v-col>
        </v-row>
        <div v-if='fname' class='text-h6 text-center ml-4'>
            <div>{{ desc }}</div>
            <div v-if='mult != "no"'>Product of weights and {{ mult }}</div>
            <div v-else>Raw weights</div>
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
    name: 'WeightsPanel',
    data() {
        return {
            fname: '',
            error: null,
            desc: '',
            nsubs: 0,
            w: null,
            topdata: null,
            labtype: 'raw',
            rank: 'abs',
            ntop: 10,
            query: "All",
            task: "All",
            mult: "no",
        }
    },
    methods: {
        alert(stuff) {
            console.log(stuff);
        },
        getTop() {
            if (!this.fname) return;
            fetch(`/image/top?ntop=${this.ntop}&rank=${this.rank}&labtype=${this.labtype}`)
            .then(resp => resp.json())
            .then(json => {
                if (json.err) {
                    console.log(json);
                    this.error = json.err;
                    return;
                }
                this.topdata = json.data;
            })
            .catch(err => console.log(err));
        },
        loadWeights() {
            if (!this.fname) return;
            fetch(`/data/weights?cohort=test&fname=${this.fname}&task=${this.task}&mult=${this.mult}&query=${encodeURIComponent(this.query)}&remap`)
            .then(resp => resp.json())
            .then(json => {
                if (json.err) {
                    console.log(json);
                    this.error = json.err;
                    return;
                }
                this.desc = json.desc;
                this.nsubs = json.nsubs;
                this.w = json.w;
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
