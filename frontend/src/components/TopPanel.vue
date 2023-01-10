<template>
<div id='imagenomer-h'>
    <div class='text-h4'>ImageNomer</div>
    <div class='text-body-2'>
        <span>
            {{ cohort }} cohort
        </span>
        <span style='margin-left: 10px;'>
            <a href='#'>Upload Data</a>
            <a href='#'>All Cohorts</a>
        </span>
        <div style='float: right'>
            <a href='#'>GitHub</a>
            <a href='#'>Report Bugs</a>
            <a href='#'>Settings</a>
            <span style='margin-left: 10px;'>
                Logged in: <a href='#'>Anton</a>
                <a href='#'>Sign out</a>
            </span>
        </div>
    </div>
</div>
</template>

<script>
import { useCohortStore } from "@/stores/CohortStore";

export default {
    name: 'CohortInfo',
    props: {
        cohort: String,
    },
    setup() {
        const store = useCohortStore();
        return {
            store
        }
    }
}
</script>

<style scope>
#imagenomer-h {
    background-color: #fee;
    border: 1px solid #ddd;
    padding: 5px;
    padding-left: 10px;
    padding-right: 10px;
    margin-bottom: 10px;
    border-radius: 2px;
}
#imagenomer-h a {
    margin-left: 5px;
}
</style>
