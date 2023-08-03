<template>
    <v-container class="pa-0">
        <v-row no-gutters>
            <v-col cols="12" md="3">
                <v-sheet class="pa-2 ma-2 bg-transparent">
                    <ConfigPanel style="height: 90vh;"/>
                </v-sheet>
            </v-col>
            <v-col cols="12" md="4">
                <v-sheet class="pa-2 ma-2 bg-transparent">
                    <LogPanel style="height: 90vh;"/>
                </v-sheet>
            </v-col>
            <v-col cols="12" md="3">
                <v-sheet class="pa-2 ma-2 bg-transparent" style="height: 30vh;">
                    <GraphPanel style="height: 100%;"/>
                </v-sheet>
                <v-sheet class="pa-2 ma-2 bg-transparent" style="height: 30vh;">
                    <GraphPanel style="height: 100%;"/>
                </v-sheet>
                <v-sheet class="pa-2 ma-2 bg-transparent" style="height: 30vh;">
                    <GraphPanel style="height: 100%;"/>
                </v-sheet>
            </v-col>
            <v-col cols="12" md="2">
                <v-sheet class="pa-2 ma-2 bg-transparent" style="height: 30vh;">
                    <GraphPanel style="height: 100%;"/>
                </v-sheet>
                <v-sheet class="pa-2 ma-2 bg-transparent" style="height: 30vh;">
                    <GraphPanel style="height: 100%;"/>
                </v-sheet>
                <v-sheet class="pa-2 ma-2 bg-transparent" style="height: 30vh;">
                    <GraphPanel style="height: 100%;"/>
                </v-sheet>
            </v-col>
        </v-row>
    </v-container>
</template>

<style scoped>
.v-list-group__items .v-list-item {
    padding-inline-start: unset !important;
}

.v-list-item--one-line .v-list-item-subtitle {
    line-clamp: unset !important;
}
</style>

<script lang="ts" setup>
import { ref, onMounted } from 'vue';
import ConfigPanel from '@/components/ConfigPanel.vue'
import LogPanel from '@/components/LogPanel.vue';
import GraphPanel from '@/components/GraphPanel.vue';

</script>
