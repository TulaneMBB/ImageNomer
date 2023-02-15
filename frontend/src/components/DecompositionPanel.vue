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
    <v-select
        v-model='corr'
        :items='["None", "pheno", "snps"]'
        label='Correlate Components'
        hide-details
        dense
        class='d-inline-block ma-4 mt-n2'
        style='width: 200px'>
    </v-select>
    <v-row v-if='name && corr == "pheno"' align='center' class='pa-4 pt-0 pb-3 ma-0'>
       <v-select 
            v-model='pheno'
            :items='phenoItems' 
            label='Phenotype' 
            hide-details 
            dense>
        </v-select>
       <v-select 
            v-if='phenoIsCat'
            v-model='cat'
            :items='catItems' 
            label='Category' 
            hide-details 
            class='ml-4'
            dense>
        </v-select>
        <v-slider
            v-model='m'
            :max='maxComp'
            label='To Component'
            step=1
            class='align-center'>
        </v-slider>
        <v-text-field
            v-model='m'
            type='number'
            style='width: 60px;'>
        </v-text-field>
        <v-btn 
            class='ml-4'
            @click='corrPheno'>Correlate Pheno</v-btn>
    </v-row>
    <v-row v-if='name && corr == "snps"' align='center' class='pa-4 pt-0 pb-3 ma-0'>
        <v-select
            label='SNPs Set' 
            v-model='set'
            :items='store.snpsSets'
            dense
            class='ma-0 pa-0'>
        </v-select>
        <v-select
            label='Haplotype'
            v-model='hap'
            :items='["0:Minor", "1:Het", "2:Major"]'
            dense
            class='ma-0 pa-0 ml-4'>
        </v-select>
        <v-select
            label='Label Type'
            v-model='labtype'
            :items='["rs", "index"]'
            dense
            class='ma-0 pa-0 ml-4'>
        </v-select>
        <v-slider
            v-model='m'
            :max='maxComp'
            label='To Component'
            step=1
            class='align-center'>
        </v-slider>
        <v-text-field
            v-model='m'
            type='number'
            style='width: 60px;'>
        </v-text-field>
        <v-slider
            v-model='ntop'
            :max='30'
            label='Display Top'
            step=1
            class='align-center'>
        </v-slider>
        <v-text-field
            v-model='ntop'
            type='number'
            style='width: 60px;'>
        </v-text-field>
        <v-btn 
            class='ml-4'
            @click='corrSNPs'>Correlate SNPs</v-btn>
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
        <div v-if='corr == "pheno"'>
            <div v-if='corrImageData' class='text-center d-inline-block'>
                <img v-bind:src="'data:image/png;base64,'+corrImageData">
            </div>
        </div>
        <div v-if='corr == "snps"'>
            <div v-if='snpsCorrDistImageData' class='text-center d-inline-block'>
                <img v-bind:src="'data:image/png;base64,'+snpsCorrDistImageData">
            </div>
            <div v-if='snpsCorrTopImageData' class='text-center d-inline-block'>
                <img v-bind:src="'data:image/png;base64,'+snpsCorrTopImageData">
            </div>
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
        catItems() {
            const cats = new Set();
            const pheno = this.store.demo[this.pheno];
            for (let key in pheno) {
                cats.add(pheno[key]);
            }
            return [...cats];
        },
        maxComp() {
            if (this.name) {
                return this.store.decomp[this.name]['comps'].length;
            }
            return 0;
        },
        maxCompSlider() {
            const max = this.maxComp;
            return (max > 30) ? 30 : max;
        },
        phenoIsCat() {
            const pheno = this.store.demo[this.pheno];
            for (let key in pheno) {
                return isNaN(pheno[key]);
            }
            return false;
        },
        phenoItems() {
            return Object.keys(this.store.demo);
        }
    },
    data() {
        return {
            imageData: null,
            varExpImageData: null,
            corrImageData: null,
            snpsCorrDistImageData: null,
            snpsCorrTopImageData: null,
            n: null,
            name: null,
            pheno: null,
            cat: null,
            m: 1,
            set: null,
            hap: null,
            labtype: null,
            ntop: 10,
            corr: 'None',
        };
    },
    methods: {
        corrPheno() {
            const cat = this.phenoIsCat ? `&cat=${enc(this.cat)}` : '';
            const url = `/analysis/corr/decomp?cohort=${enc(this.store.cohort)}&name=${enc(this.name)}&n=${this.m}&query=All&field=${enc(this.pheno)}${cat}`;
            fetch(url)
            .then(resp => resp.json())
            .then(json => {
                if (json.err) {
                    console.log(json.err);
                    return;
                }
                this.corrImageData = json.data;
            })
            .catch(err => console.log(err));
        },
        corrSNPs() {
            const hap = parseInt(this.hap);
            const url = `/analysis/corr/decomp-snps?cohort=${enc(this.store.cohort)}&name=${enc(this.name)}&n=${this.m}&query=All&set=${enc(this.set)}&hap=${hap}&labtype=${enc(this.labtype)}&ntop=${this.ntop}`;
            fetch(url)
            .then(resp => resp.json())
            .then(json => {
                if (json.err) {
                    console.log(json.err);
                    return;
                }
                this.snpsCorrTopImageData = json.data;
                this.snpsCorrDistImageData = json.dist;
            })
            .catch(err => console.log(err));
        },
        getComponent() {
            if (!this.name || this.n === null) {
                return;
            }
            const url = `/data/component?cohort=${enc(this.store.cohort)}&name=${enc(this.name)}&n=${enc(this.n)}&remap`;
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
            fetch(`/data/decomp/varexp?cohort=${enc(this.store.cohort)}&name=${enc(this.name)}`)
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
            this.m = 0;
            this.getVarExplained();
            this.getComponent();
        }
    }
}
</script>

<style>
</style>
