<template>
    <div class='fc-div'>
        <span v-if='loading'>Loading...</span>
        <span v-else-if='error'>{{ error }}</span>
        <div v-else>
            <p><span v-for='field in display' :key='field.num'>{{field.label}}<br></span></p>
            <img v-bind:src="'data:image/png;base64,'+imageData">
        </div>
    </div>
</template>

<script>
import { useCohortStore } from "@/stores/CohortStore";
import { enc } from './../functions.js';

export default {
    name: 'FC',
    data() {
        return {
            imageData: '',
            loading: true,
            error: false,
            label: ''
        }
    },
    computed: {
        display() {
            let num = 0;
            return Object.keys(this.store.labels).filter(field => this.store.labels[field]).map(field => {
                let label;
                if (field == 'ID') {
                    label = this.sub;
                } else if (field == 'Task') {
                    label = this.task;
                } else {
                    label = `${field}: ${this.store.demo[field][this.sub]}`;
                }
                return {num: num++, label};
            });
        },
        fctype() {
            return this.store.fctype;
        }
    },
    created() {
        this.fetchFcImage();
    },
    methods: {
        fetchFcImage() {
            const remap = this.remap ? '&remap' : '';
            const colorbar = this.colorbar ? '&colorbar' : '';
            fetch(`/data/fc?cohort=${enc(this.cohort)}&sub=${enc(this.sub)}&task=${enc(this.task)}&type=${enc(this.fctype)}${remap}${colorbar}`)
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
    props: {
        cohort: String,
        sub: String,
        task: String,
        remap: {
            type: Boolean,
            default: false
        },
        colorbar: {
            type: Boolean,
            default: true
        }
    },
    setup() {
        const store = useCohortStore();
        return {
            store
        }
    },
    watch: {
        fctype() {
            this.fetchFcImage();
        }
    }
}
</script>

<style scoped>
.fc-div {
    display: inline-block;
    text-align: center;
    font-size: smaller;
    color: #444;
}
.fc-div img {
    width: 150px;
}
.fc-div span {
    vertical-align: center;
}
</style>
