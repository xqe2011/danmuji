<template>
    <v-toolbar>
        <template v-for="(route, index) in router.options.routes" :key="index">
            <a class="text-white link" :href="route.path" :class="{ selected: router.currentRoute.value.path == route.path }"><p>{{ route.meta?.name }}</p></a>
        </template>
        <v-spacer></v-spacer>
        <div class="text-white link"><p>{{ websocketStatus }}</p></div>
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
import { onWSState } from '@/services/Database';
import { ref } from 'vue';

const router = useRouter();
const websocketStatus = ref('未连接');

onWSState.subscribe(data => {
    if (data == 'connected') {
        websocketStatus.value = '已连接';
    } else {
        websocketStatus.value = '未连接';
    }
});
</script>