<template>
    <v-card
        title='Weights'
        subtitle='Compare model weights from analysis runs'
        class='mb-2'
    >
        <!--<v-row align='center' class='ma-0 ml-4 mr-4 mb-4 pa-0'>
            <v-select
                label='
        </v-row>-->
        <v-btn-toggle v-model='wtype' class='mb-4'>
            <v-btn key='fc' value='fc'>FC/Partial</v-btn>
            <v-btn key='snps' value='snps'>SNPs</v-btn>
        </v-btn-toggle>
        <v-row align='center' class='ma-0 ml-4 mr-4 mb-4 pa-0'>
            <v-breadcrumbs divider='>'>
                <v-breadcrumbs-item 
                    :key='dir'
                    v-for='dir in dirPath'>
                <v-btn @click='backDir(dir)'>{{ dir }}</v-btn>
                </v-breadcrumbs-item>
            </v-breadcrumbs>
            <v-select 
                label='Directory' 
                v-model='dirSel'
                :items='dirItems'
                dense
                class='ma-0 pa-0 mr-4'>
            </v-select>
            <v-select
                label='Weights File'
                v-model='fname'
                :items='dirFnames'
                :change='loadWeights()'
                dense
                class='ma-0 pa-0'>
            </v-select>
        </v-row>
        <v-row 
            v-if='wtype == "fc"'
            align='center' class='ma-0 ml-4 mr-4 pa-0'>
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
        <v-row
            v-if='wtype == "fc"'
            align='center' class='ma-0 ml-4 mr-4 pa-0'>
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
            <v-slider label='Number' v-model='ntop' min='3' max='30' step='1'>
            </v-slider>
        </v-row>
        <v-row
            v-else-if='wtype == "snps"'
            align='center' class='ma-0 ml-4 mr-4 pa-0'>
            <v-select
                label='SNPs Set'
                v-model='set'
                :items='store.snpsSets'
                @change='loadWeights'
                dense
                class='ma-0 pa-0 ml-4'>
            </v-select>
            <v-select
                label='Haplotype'
                v-model='hap'
                :items='["0:Minor", "1:Het", "2:Major"]'
                @change='loadWeights'
                dense
                class='ma-0 pa-0 ml-4'>
            </v-select>
            <v-select
                label='Label Type'
                v-model='labtype'
                :items='["rs", "index"]'
                @change='loadWeights'
                dense
                class='ma-0 pa-0 ml-4'>
            </v-select>
            <v-slider label='Number' v-model='ntop' min='3' max='30' step='1'>
            </v-slider>
            <v-checkbox v-model='avg' label='Average' class='pa-0 ma-0'></v-checkbox>
            <v-checkbox v-model='limiqr' label='Limit IQR' class='pa-0 ma-0'></v-checkbox>
        </v-row>
        <div v-if='fname' class='text-h6 text-center ml-4'>
            <div>{{ desc }}</div>
            <div v-if='wtype == "fc" && !avg'>
                <div v-if='mult != "no"'>Product of weights and {{ mult }}</div>
                <div v-else>Raw weights</div>
            </div>
            <v-row align='center' justify='center' class='my-4'>
                <img v-bind:src="'data:image/png;base64,'+w">
                <img v-if='topdata' v-bind:src="'data:image/png;base64,'+topdata">
            </v-row>
        </div>
    </v-card>
</template>

<script>
import { useCohortStore } from "@/stores/CohortStore";
import { enc } from './../functions.js';

export default {
    name: 'WeightsPanel',
    /*created() {
        this.store.fetchCohort('test');
    },*/
    computed: {
        dirFnames() {
            const curDir = this.getCurDirContents();
            return curDir ? curDir['fnames'] : [];
        },
        dirItems() {
            const curDir = this.getCurDirContents();
            return curDir && curDir['dirs'] 
                ? Object.keys(curDir['dirs']) : [];
        }
    },
    data() {
        return {
            wtype: 'fc',
            fname: '',
            error: null,
            desc: '',
            ntrain: 0,
            ntest: 0,
            w: null,
            topdata: null,
            labtype: 'raw',
            rank: 'abs',
            ntop: 10,
            query: "All",
            task: "All",
            mult: "no",
            dirSel: null,
            dirPath: ["/"],
            dirFiles: [],
            hap: "0:Minor",
            set: null,
            avg: null,
            limiqr: false,
        }
    },
    methods: {
        backDir(dir) {
            for (let i=0; i<this.dirPath.length; i++) {
                if (this.dirPath[i] == dir) {
                    this.dirPath = this.dirPath.slice(0,i+1);
                    return;
                }
            }
        },
        changeDir() {
            this.dirPath.push(this.dirSel);
        },
        getCurDirContents() {
            let curDir = this.store.weights;
            this.dirPath.slice(1).forEach(d => {
                if (curDir['dirs']) {
                    curDir = curDir['dirs'][d];
                }
            });
            return curDir;
        },
        getTop() {
            if (!this.fname) return;
            fetch(`/image/top?ntop=${enc(this.ntop)}&rank=${enc(this.rank)}&labtype=${enc(this.labtype)}`)
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
            const fname = this.dirPath.slice(1).concat([this.fname]).join('/');
            console.log(fname);
            let url = null;
            const avg = this.avg ? "&average" : "";
            const limiqr = this.limiqr ? "&limiqr" : "";
            if (this.wtype == 'fc') {
                url = `/data/weights/fc?cohort=${enc(this.store.cohort)}&fname=${enc(fname)}&task=${enc(this.task)}&mult=${enc(this.mult)}&query=${enc(this.query)}&remap${avg}`;
            } else {
                if (!this.set) return;
                const hap = this.hap[0];
                url = `/data/weights/snps?cohort=${enc(this.store.cohort)}&fname=${enc(fname)}&n=${enc(this.ntop)}&set=${enc(this.set)}&hap=${enc(hap)}&labtype=${enc(this.labtype)}${avg}${limiqr}`;
            }
            fetch(url)
            .then(resp => resp.json())
            .then(json => {
                if (json.err) {
                    console.log(json);
                    this.error = json.err;
                    return;
                }
                this.desc = json.desc;
                this.ntrain = json.ntrain;
                this.ntest = json.ntest;
                this.w = json.w;
                if (this.wtype == 'fc')
                    this.getTop();
                else if (this.wtype == 'snps') {
                    this.topdata = json.top;
                }
            })
            .catch(err => console.log(err));
        },
    },
    setup() {
        const store = useCohortStore();
        return {
            store
        }
    },
    watch: {
        dirSel() {
            this.fname = '';
            this.changeDir();
        },
        ntop() {
            if (this.wtype == 'fc') 
                this.getTop();
            else if (this.wtype == 'snps')
                this.loadWeights();
        },
        wtype() {
            this.w = null;
            this.topdata = null;
            if (this.wtype == 'fc') 
                this.labtype = 'raw';
            else if (this.wtype == 'snps')
                this.labtype = 'index';
        }
    }
}
</script>

<style scoped>
</style>
