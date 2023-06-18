<template>
    <div class='fc-div'>
        <span v-if='loading'>Loading...</span>
        <span v-else-if='error'>{{ error }}</span>
        <div v-else>
            <p>
                <span class='text-body-2' v-for='field in display' :key='field.num'>
                    {{field.label}}<br>
                </span>
            </p>
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
            return Object.keys(this.store.labels)
            .filter(field => this.store.labels[field])
            .map(field => {
                let label;
                if (field == 'ID') {
                    label = this.sub;
                } else if (field == 'Task') {
                    label = this.task;
                } else if (field == 'Set') {
                    label = this.set;
                } else {
                    label = `${field}: ${this.store.demo[field][this.sub]}`;
                }
                return {num: num++, label};
            });
        },
    },
    created() {
        this.fetchImage();
    },
    methods: {
        fetchImage() {
            if (this.type == 'snps')
                this.fetchSNPsImage();
            else
                this.fetchFcImage();
        },
        fetchFcImage() {
            const remap = this.remap ? '&remap' : '';
            const colorbar = this.colorbar ? '&colorbar' : '';
            fetch(`/data/fc?cohort=${enc(this.store.cohort)}&sub=${enc(this.sub)}&task=${enc(this.task)}&type=${enc(this.type)}${remap}${colorbar}`)
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
        },
        fetchSNPsImage() {
            fetch(`/data/snps?cohort=${enc(this.store.cohort)}&sub=${enc(this.sub)}&set=${enc(this.set)}`)
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
        sub: String,
        type: String,
        task: {
            type: String,
            default: '',
        },
        set: {
            type: String,
            default: '',
        },
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
        set() {
            this.fetchImage();
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
