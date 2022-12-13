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
                    <v-row>
                        <MainPanel/>
                    </v-row>
                    <v-row>
                        <BottomPanel/>
                    </v-row>
                </v-container>
            </v-col>
        </v-row>
    </v-main>
</v-app>
</template>

<script>
import SidePanel from './components/SidePanel.vue'
import MainPanel from './components/MainPanel.vue'
import BottomPanel from './components/BottomPanel.vue'
import TopPanel from './components/TopPanel.vue'

export default {
    name: 'App',
    components: {
    SidePanel,
    MainPanel,
    BottomPanel,
    TopPanel
}
}
</script>

<style>
.v-main {
    font-size: 14px;
    padding: 20px;
}
.checkbox-dense {
    height: 24px;
}
.checkbox-list-wrapper {
    padding-bottom: 20px;
}
.padded {
    margin: 8px;
}
.padded-alt {
    padding: 8px;
}
.v-card {
    margin-bottom: 8px;
}
</style>
