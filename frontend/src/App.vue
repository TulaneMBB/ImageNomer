<template>
<v-app>
    <v-main>
        <TopPanel/>
        <v-row dense>
            <v-col cols='auto'>
                <SidePanel/>
            </v-col>
            <v-col>
                <v-container>
                    <MainPanel/>
                </v-container>
            </v-col>
        </v-row>
    </v-main>
</v-app>
</template>

<script>
import TopPanel from './components/TopPanel.vue';
import SidePanel from './components/SidePanel.vue';
import MainPanel from './components/MainPanel.vue';

export default {
    name: 'App',
    components: {
        TopPanel,
        SidePanel,
        MainPanel,
    }
}
</script>

<style>
.v-main {
    font-size: 12px;
    padding: 10px;
}
.no-display {
    display: none;
}
</style>
