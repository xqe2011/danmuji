<template>
    <v-card class="mx-auto" elevation="4">
        <v-card-title>
            <div><p>弹幕日记</p></div>
            <v-btn :color="locked ? 'green': 'red'" @click="emits('toggle')">{{ props.locked ? '关闭自动滚动': '启动自动滚动' }}</v-btn>
        </v-card-title>
        <div ref="container" class="container">
            <v-data-table-virtual :height="tableHeight" style="width: 100%" fixed-header :items="props.data" ref="table">
                <template v-slot:headers>
                    <tr>
                        <th class="text-left username">用户名</th>
                        <th class="text-left action">操作</th>
                        <th class="text-left text">文本</th>
                    </tr>
                </template>
                <template v-slot:item="{ item: { raw } }">
                    <tr :class="{ filterd: raw.filterd }">
                        <td>{{ raw.uname }}</td>
                        <td v-if="raw.type == 'danmu'">弹幕</td>
                        <td v-if="raw.type == 'danmu'">{{ raw.msg }}</td>
                    
                        <td v-if="raw.type == 'gift'">礼物</td>
                        <td v-if="raw.type == 'gift'">赠送了{{ raw.num }}个{{ raw.giftName }}</td>
                    
                        <td v-if="raw.type == 'guardBuy'">上舰</td>
                        <td v-if="raw.type == 'guardBuy'">赠送了{{ raw.num }}个月{{ raw.giftName }}</td>
                    
                        <td v-if="raw.type == 'like' || raw.type == 'subscribe' || raw.type == 'welcome' || raw.type == 'superChat'">其他</td>
                        <td v-if="raw.type == 'like'">点赞</td>
                        <td v-if="raw.type == 'subscribe'">关注</td>
                        <td v-if="raw.type == 'welcome'">欢迎</td>
                        <td v-if="raw.type == 'superChat'">发送了{{ raw.price }}元的SC: {{ raw.msg }}</td>
                    </tr>
                </template>
            </v-data-table-virtual>
        </div>
    </v-card>
</template>

<style scoped>
.v-card {
    display: flex;
    flex-direction: column;
}
.container {
    display: flex;
    flex-direction: column;
    flex-grow: 1;
}
.username {
    width: 28%;

}
.action {
    width: 12%;
}
.text {
    width: 60%;
}
.filterd {
    background-color: rgba(255, 0, 0, 0.7) !important;
}
.filterd > td {
    background: none !important;
}
.v-card-title {
    display: flex;
}
.v-card-title > div {
    flex-grow: 1;
    display: flex;
    align-items: center;
}
.v-card-title > .v-btn {
    margin-left: 8px;
}

:deep(.v-data-table-rows-no-data) {
    display: none;
}
:deep(table) {
    table-layout: fixed;
}
</style>

<script setup lang="ts">
import { onMounted, onUnmounted, watch, ref, onUpdated } from "vue";
import { VDataTableVirtual } from "vuetify/lib/labs/components.mjs";

const container = ref<HTMLDivElement | null>(null);
const table = ref<VDataTableVirtual | null>(null);
const tableHeight = ref(1);
let resizeObserver: ResizeObserver;

const props = defineProps({
    data: {
        type: Array,
        required: true
    },
    locked: {
        type: Boolean,
        default: true
    }
});

const emits = defineEmits<{ (e: 'toggle'): void }>()

onMounted(() => {
    resizeObserver = new ResizeObserver((entries) => {
        tableHeight.value = entries[0].contentRect.height;
    });
    resizeObserver.observe(container.value!);
});

onUnmounted(() => {
    resizeObserver.disconnect();
});

onUpdated(() => {
    if (container.value && props.locked) {
        const divElement = table.value?.$el.querySelector('div.v-table__wrapper');
        divElement.scrollTop = divElement.scrollHeight;
    }
});
</script>