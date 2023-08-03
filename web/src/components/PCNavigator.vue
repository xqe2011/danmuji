<template>
    <!-- <v-navigation-drawer permanent elevation="10">
        <v-list nav class="text-white" aria-label="导航栏" role="menu">
            <template v-for="(route, index) in router.options.routes" :key="index">
                <v-list-item :prepend-icon="route.meta?.icon" :title="route.meta?.name" :value="route.meta?.name" :to="route.path" link tabindex="1" role="menuitem"></v-list-item>
            </template>
        </v-list>
    </v-navigation-drawer> -->
</template>

<style scoped lang="scss">
@import "../styles/settings.scss";

.v-navigation-drawer {
  background-color: $nuozi-deep-blue;
  border: none;
}
.v-list-item__prepend>.v-avatar {
  margin-inline-end: 0 !important;
}
.footer {
    white-space: pre-line;
}
</style>

<script lang="ts" setup>
import { useRouter } from 'vue-router';

const router = useRouter();
</script>