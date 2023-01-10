<template>
<v-card title='Decomposition' class='mb-2'>
    <v-card-subtitle>
        Decomposition of FC, PC, and SNPs into 
        lower-dimensional representations
    </v-card-subtitle>
    <v-row align='center' class='pa-4 pt-3 pb-3 ma-0'>
       <v-select 
            v-model='name'
            :items='Object.keys(store.decomp)' 
            label='Decomposition' 
            hide-details 
            dense 
            @change='getComponent'>
        </v-select>
        <v-slider
            v-model='n'
            :max='maxCompSlider'
            label='Component'
            step=1
            class='align-center'>
        </v-slider>
        <v-text-field
            v-model='n'
            type='number'
            style='width: 60px;'>
        </v-text-field>
    </v-row>
    <div v-if='name' class='pa-4 text-center'>
        {{ maxComp }} components
    </div>
    <v-row class='pa-4 pt-0'>
        <div v-if='varExpImageData' class='text-center d-inline-block'>
            Variance Explained<br>
            <img v-bind:src="'data:image/png;base64,'+varExpImageData">
        </div>
        <div v-if='imageData' class='text-center d-inline-block'>
            Component {{ n }}<br>
            <img v-bind:src="'data:image/png;base64,'+imageData">
        </div>
    </v-row>
</v-card>
</template>

<script>
import { useCohortStore } from "@/stores/CohortStore";
import { enc } from './../functions.js';

export default {
    name: "DecompositionPanel",
    computed: {
        maxComp() {
            if (this.name) {
                return this.store.decomp[this.name]['comps'].length;
            }
            return 0;
        },
        maxCompSlider() {
            const max = this.maxComp;
            return (max > 30) ? 30 : max;
        }
    },
    data() {
        return {
            imageData: null,
            varExpImageData: null,
            n: null,
            name: null,
        };
    },
    methods: {
        getComponent() {
            if (!this.name || this.n === null) {
                return;
            }
            const url = `/data/component?cohort=test&name=${enc(this.name)}&n=${enc(this.n)}&remap`;
            fetch(url)
            .then(resp => resp.json())
            .then(json => {
                if (json.err) {
                    console.log(json.err);
                    return;
                }
                this.imageData = json.data;
            })
            .catch(err => console.log(err));
        },
        getVarExplained() {
            fetch(`/data/decomp/varexp?cohort=test&name=${enc(this.name)}`)
            .then(resp => resp.json())
            .then(json => {
                if (json.err) {
                    console.log(json.err);
                    return;
                }
                this.varExpImageData = json.data;
            })
            .catch(err => console.log(err));
        }
    },
    setup() {
        const store = useCohortStore();
        return {
            store
        };
    },
    watch: {
        n() {
            if (this.n < this.maxComp 
                && this.n == Math.ceil(this.n) 
                && this.n >= 0) {
                this.getComponent();
            }
        },
        name() {
            this.n = 0;
            this.getVarExplained();
            this.getComponent();
        }
    }
}
</script>

<style>
</style>
