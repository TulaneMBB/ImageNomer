<template>
    <div v-if='imageData'>
        <img v-bind:src="'data:image/png;base64,'+imageData">
    </div>
    <v-card 
        title='Image Math' 
        subtitle='Perform operations on images, e.g., correlation images'
        class='pa-4'
    >
        <v-row align='center' dense class='mb-4'>
            <v-text-field
                label='Expression (e.g. "A-B", "std(A,BA,C)")'
                v-model='expr'
                hide-details dense>
            </v-text-field>
            <v-btn 
                @click='doImageMath()' 
                key='go' value='Go' class='ml-4'>
                Go
            </v-btn>
        </v-row>
        <div v-if='saved.length > 0'
            class='text-h6 mb-6'>
            Images
        </div>
        <v-checkbox 
            v-for="item in saved" 
            :key="item.idx" 
            v-model="item.selected" 
            :label="item.label"
            dense
            hide-details 
            class="ma-0 pa-0 mr-4 mt-n8 d-inline-flex">
        </v-checkbox>
        <div>
            <v-btn @click='rm'>Remove</v-btn>
        </div>
    </v-card>
</template>

<script>
import { useCohortStore } from "@/stores/CohortStore";
import { enc, savedImageType } from './../functions.js';

export default {
    name: 'ImageMathPanel',
    created() {
        if (this.store.mathImage) {
            this.imageData = this.store.mathImage;
        } else if (this.saved.length > 0 
            && this.saved.at(-1).type.match(/stats/)) {
            this.expr = this.saved.at(-1).id;
            this.doImageMath();
        }
    },
    computed: {
        saved() {
            return this.store.saved
            .filter(item => savedImageType(item.type))
            .map((item,idx) => {
                item.idx = idx;
                return item;
            });
        },
        selected() {
            return this.saved
            .filter(item => item.selected);
        }
    },
    data() {
        return {
            expr: "",
            imageData: null,
        }
    },
    methods: {
        rm() {
            // TODO remove on server
            console.log(this.selected);
            this.selected.forEach(item => {
                this.store.saved = this.store.saved.filter(it => item.idx != it.idx);
            });
        },
        doImageMath() {
            fetch(`/math/image?expr=${enc(this.expr)}`)
            .then(resp => resp.json())
            .then(json => {
                this.loading = false;
                if (json.err) {
                    this.error = json.err;
                    return;
                }
                this.imageData = json.data;
                //this.store.corr = json.data;
                //this.store.display = "corr";
            })
            .catch(err => this.error = err);
        },
    },
    setup() {
        const store = useCohortStore();
        return {
            store
        }
    },
}
</script>

<style scoped>
</style>
