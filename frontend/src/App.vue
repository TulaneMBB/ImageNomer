<template>
<v-app>
    <v-main>
        <TopPanel cohort='test'/>
        <v-row dense>
            <v-col cols='auto'>
                <SidePanel/>
            </v-col>
            <v-col>
                <v-container>
                    <DisplayButtonsPanel></DisplayButtonsPanel>
                    <MainPanel/>
                    <CorrelationPanel></CorrelationPanel>
                    <ImageMathPanel></ImageMathPanel>
                    <!-- <BottomPanel/> -->
                </v-container>
            </v-col>
        </v-row>
    </v-main>
</v-app>
</template>

<script>
import SidePanel from './components/SidePanel.vue';
import MainPanel from './components/MainPanel.vue';
// import BottomPanel from './components/BottomPanel.vue';
import TopPanel from './components/TopPanel.vue';
import DisplayButtonsPanel from './components/DisplayButtonsPanel.vue';
import ImageMathPanel from './components/ImageMathPanel.vue';
import CorrelationPanel from './components/CorrelationPanel.vue';

export default {
    name: 'App',
    components: {
        SidePanel,
        MainPanel,
        // BottomPanel,
        TopPanel,
        DisplayButtonsPanel,
        ImageMathPanel,
        CorrelationPanel
    }
}
</script>

<style>
.v-main {
    font-size: 14px;
    padding: 20px;
}
.no-display {
    display: none;
}
</style>
