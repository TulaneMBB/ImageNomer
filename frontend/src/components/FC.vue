<template>
    <div class='fc-div'>
        <span v-if='loading'>Loading...</span>
        <span v-else-if='error'>{{ error }}</span>
        <div v-else>
            <div>{{ sub }}, {{ task }}</div>
            <img v-bind:src="'data:image/png;base64,'+imageData">
        </div>
    </div>
</template>

<script>
export default {
    name: 'FC',
    data() {
        return {
            imageData: '',
            loading: true,
            error: false
        }
    },
    created() {
        this.fetchFcImage();
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
    methods: {
        fetchFcImage() {
            const remap = this.remap ? '&remap' : '';
            const colorbar = this.colorbar ? '&colorbar' : '';
            fetch(`/data/fc?cohort=${this.cohort}&sub=${this.sub}&task=${this.task}${remap}${colorbar}`)
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
    }
}
</script>

<style scoped>
.fc-div {
    display: inline-block;
    text-align: center;
}
.fc-div img {
    width: 150px;
}
.fc-div span {
    vertical-align: center;
}
</style>