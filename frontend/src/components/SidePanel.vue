<template>
    <div id='side'>
        <CohortInfo cohort='test'/>
    </div>
</template>

<script>
import CohortInfo from './CohortInfo.vue'

export default {
    name: 'SidePanel',
    components: {
        CohortInfo
    }
}
</script>

<style scoped>
#side {
    grid-area: 1 / 1 / span 2 / span 1;
    width: 300px;
}
</style>