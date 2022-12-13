<template>
    <div class='demo-div'>
        <span v-if='loading'>Loading...</span>
        <span v-else-if='error'>{{ error }}</span>
        <div v-else>
            <img v-bind:src="'data:image/png;base64,'+imageData">
        </div>
    </div>
</template>

<script>
import { useCohortStore } from "@/stores/CohortStore";

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
        this.fetchDemoImage();
    },
    props: {
        cohort: String,
    },
    setup() {
        const store = useCohortStore();
        return {
            store
        }
    },
    methods: {
        fetchDemoImage() {
            const groupsArr = this.store.groups.filter(g => g.selected);
            const groupsObj = {};
            groupsArr.forEach(g => {
                groupsObj[g.query] = g.subs;
            });
            const formData = new FormData();
            formData.append('cohort', this.cohort);
            formData.append('groups', JSON.stringify(groupsObj));
            formData.append('field', this.store.display);
            fetch(`/data/demo/hist`, {
                method: 'POST',
                body: formData
            })
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

</style>