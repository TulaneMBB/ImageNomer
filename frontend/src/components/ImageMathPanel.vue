<template>
    <v-card 
        title='Image Math' 
        subtitle='Perform operations on images, e.g., correlation images'
    >
        <v-row align='center' dense class='mb-4'>
            <v-text-field
                label='Expression (e.g. "A-B", "std(A,BA,C)")'
                v-model='expr'
                hide-details dense class='ml-4'>
            </v-text-field>
            <v-btn @click='doImageMath()' key='go' value='Go' class='ml-4 mr-4'>Go</v-btn>
        </v-row>
        <div 
            v-if='store.saved.filter(item => savedImageType(item.type)).length > 0'
            class='text-h6 ml-4 mb-6'
        >
            Images
        </div>
        <v-checkbox 
            v-for="item in store.saved.filter(item => savedImageType(item.type))" 
            :key="item.num" 
            v-model="item.selected" 
            :label="item.label"
            dense
            hide-details 
            class="ma-0 pa-0 ml-2 mr-2 mt-n8 d-inline-flex">
        </v-checkbox>
    </v-card>
</template>

<script>
import { useCohortStore } from "@/stores/CohortStore";
import { savedImageType } from './../functions.js';

export default {
    name: 'ImageMathPanel',
    data() {
        return {
            expr: ""
        }
    },
    methods: {
        doImageMath() {
            fetch(`/math/image?expr=${encodeURIComponent(this.expr)}`)
            .then(resp => resp.json())
            .then(json => {
                this.loading = false;
                if (json.err) {
                    this.error = json.err;
                    return;
                }
                this.store.corr = json.data;
                this.store.display = "corr";
            })
            .catch(err => this.error = err);
        },
        savedImageType
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