<template>
    <v-card title='Correlation' class='mb-2'>
        <v-card-subtitle>
            Find correlation between demographic features and FC for group
        </v-card-subtitle>
        <div>
            <div v-if='url' class='text-body-2 ma-4'>{{ decodeURIComponent(url) }}</div>
            <img v-if='imageData' 
                v-bind:src="'data:image/png;base64,'+imageData">
            <img v-if='pImageData' 
                v-bind:src="'data:image/png;base64,'+pImageData">
            <div v-if='isCorr'>
                <div v-if='saveResp'>{{ saveResp }}</div>
                <v-btn @click='saveImage("corr")' class='ml-4'>
                    Save Image
                </v-btn>
                <v-btn @click='saveImage("p")' class='ml-4'>
                    Save P-Value Image
                </v-btn>
            </div>
            <div v-else-if='corrVal' class='text-body-2 ml-4'>
                Correlation: {{ corrVal }}, n: {{ n }} p-value: {{ pVal }}, log10(p-value): {{ log10pVal }}
            </div>
        </div>
        <v-row align='center' class='pa-4 pt-3 pb-3 ma-0'>
           <v-select 
                v-model='group'
                :items='store.groups' 
                item-title='query' 
                label='Group' 
                hide-details dense class='pa-0 ma-0'>
            </v-select>
            <v-select 
                v-model='feat'
                :items='Object.keys(store.demo)' 
                label='Demographic Feature' 
                hide-details dense class='pa-0 ma-0 ml-4'>
            </v-select>
           <v-select 
                v-if='featIsCat'
                v-model='cat'
                :items='catItems' 
                label='Category' 
                hide-details 
                class='ml-4'
                dense>
            </v-select>
            <v-select 
                v-model='respVar'
                :items="Object.keys(store.demo).concat(
                    ['fc','partial','snps'])" 
                label='Response Var' 
                hide-details dense class='pa-0 ma-0 ml-4'>
            </v-select>
            <v-select
                v-if='["fc", "partial"].includes(respVar)'
                v-model='task'
                :items='["All"].concat(store.tasks(respVar))'
                label='Task'
                hide-details dense class='pa-0 ma-0 ml-4'>
            </v-select>
            <v-select 
                v-if='respVar == "snps"'
                v-model='set'
                :items='store.snpsSets'
                label='SNPs Sets'
                hide-details dense class='pa-0 ma-0 ml-4'>
            </v-select>
            <v-select
                v-if='respVar == "snps"'
                v-model='hap'
                :items='["0:Minor","1:Het","2:Major"]'
                label='Haplotype'
                hide-details dense class='pa-0 ma-0 ml-4'>
            </v-select>
            <v-select
                v-if='respVar == "snps"'
                v-model='labtype'
                :items='["rs", "index"]'
                label='Label Type'
                hide-details dense class='pa-0 ma-0 ml-4'>
            </v-select>
            <v-btn @click='getCorr()' 
                key='go' value='Go' class='ml-4 mr-0'>Go</v-btn>
        </v-row>
    </v-card>
</template>

<script>
import { useCohortStore } from "@/stores/CohortStore";
import { enc } from './../functions.js';

export default {
    name: "CorrelationPanel",
    computed: {
        catItems() {
            const cats = new Set();
            const pheno = this.store.demo[this.feat];
            for (let key in pheno) {
                cats.add(pheno[key]);
            }
            return [...cats];
        },
        featIsCat() {
            const pheno = this.store.demo[this.feat];
            for (let key in pheno) {
                return isNaN(pheno[key]);
            }
            return false;
        },
    },
    data() {
        return {
            imageData: null,
            pImageData: null,
            group: null,
            feat: null,
            respVar: null,
            task: null,
            url: null,
            isCorr: false,
            rid: null,
            pid: null,
            saveResp: null,
            set: null,
            hap: "0:Minor",
            labtype: "index",
            cat: null,
            corrVal: null,
            n: null,
            pVal: null,
            log10pVal: null
        };
    },
    setup() {
        const store = useCohortStore();
        return {
            store
        };
    },
    methods: {
        getCorr() {
            if (this.respVar == 'snps') {
                this.getCorrSNPs();
                return;
            }
            const cat = this.featIsCat ? `&cat=${enc(this.cat)}` : '';
            const taskPart = (this.task == "All")
                ? ""
                : `&task=${enc(this.task)}`;
            this.url = (this.respVar == "fc" || this.respVar == 'partial')
                ? `/analysis/corr/fc?cohort=${enc(this.store.cohort)}&query=${enc(this.group)}&field=${enc(this.feat)}${taskPart}&fctype=${enc(this.respVar)}&remap${cat}`
                : `/analysis/corr/demo?cohort=${enc(this.store.cohort)}&query=${enc(this.group)}&field1=${enc(this.feat)}&field2=${enc(this.respVar)}${cat}`;
            fetch(this.url)
            .then(resp => resp.json())
            .then(json => {
                this.loading = false;
                if (json.err) {
                    this.error = json.err;
                    return;
                }
                if (this.respVar == "fc" || this.respVar == 'partial') {
                    this.store.corr = json.rdata;
                    this.store.p = json.pdata;
                    this.store.saved.push({
                        type: "fc-corr",
                        label: `(${json.rid}) fc-corr | group: ${this.group}, feat: ${this.feat}, task: ${this.task}`,
                        data: json.rdata,
                        id: json.rid,
                    });
                    this.store.saved.push({
                        type: "p-for-corr",
                        label: `(${json.pid}) p-for-corr | group: ${this.group}, feat: ${this.feat}, task: ${this.task}`,
                        data: json.pdata,
                        id: json.pid,
                        rid: json.rid,
                    });
                    this.imageData = json.rdata;
                    this.pImageData = json.pdata;
                    this.isCorr = true;
                    this.rid = json.rid;
                    this.pid = json.pid;
                } else {
                    this.imageData = json.data;
                    this.pImageData = null;
                    this.isCorr = false;
                    this.corrVal = json.corr;
                    this.n = json.n;
                    this.pVal = json.p;
                    this.log10pVal = json.log10p;
                }
            })
            .catch(err => this.error = err);
        },
        getCorrSNPs() {
            const hap = this.hap[0];
            const cat = this.featIsCat ? `&cat=${enc(this.cat)}` : '';
            this.url = `/analysis/corr/snps?cohort=${this.store.cohort}&query=${enc(this.group)}&field=${enc(this.feat)}&set=${enc(this.set)}&n=10&hap=${enc(hap)}&labtype=${enc(this.labtype)}${cat}`;
            fetch(this.url)
            .then(resp => resp.json())
            .then(json => {
                if (json.err) {
                    console.log(json.err);
                    return;
                }
                this.imageData = json.rho;
                this.pImageData = json.top;
                this.isCorr = false;
            })
            .catch(err => console.log(err));
        },
        saveImage(type) {
            const id = type == 'corr' ? this.rid : this.pid;
            fetch(`/analysis/corr/save?cohort=${this.store.cohort}&id=${id}`)
            .then(resp => resp.json())
            .then(json => {
                if (json.error) {
                    this.saveResp = json.error;
                    return;
                }
                this.saveResp = json.resp;
            })
            .catch(err => console.log(err));
        }
    }
}
</script>

<style scoped>
</style>
