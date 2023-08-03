<template>
    <v-toolbar>
        <template v-for="(route, index) in router.options.routes" :key="index">
            <a class="text-white link" :href="route.path" :class="{ selected: router.currentRoute.value.path == route.path }"><p>{{ route.meta?.name }}</p></a>
        </template>
    </v-toolbar>
</template>

<style scoped lang="scss">
@import "../styles/settings.scss";

.v-toolbar {
    background-color: #2057bc;
}
.link {
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    text-decoration: none;
}
.link > p {
    padding-left: 32px;
    padding-right: 32px;
}
.link:hover {
    background-color: rgba($color: (#000000), $alpha: 0.1);
}
.selected {
    background-color: rgba($color: (#000000), $alpha: 0.2);
}
</style>

<script lang="ts" setup>
import { useRouter } from 'vue-router';

const router = useRouter();
</script>