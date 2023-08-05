<template>
    <v-card class="mx-auto" elevation="4">
        <v-card-title>
            <div><p>弹幕日记</p></div>
            <v-btn :color="locked ? 'green': 'red'" @click="toggleLock">{{ locked ? '关闭自动滚动': '启动自动滚动' }}</v-btn>
        </v-card-title>
            <div class="overflow-auto pa-0" ref="container">
                <v-table style="width: 100%" fixed-header>
                    <thead>
                        <tr>
                            <th class="text-left username">用户名</th>
                            <th class="text-left action">操作</th>
                            <th class="text-left text">文本</th>
                        </tr>
                    </thead>
                    <tbody>
                        <template v-for="(item, index) in props.data as WebsocketBroadcastMessage['events']" :key="index">
                            <tr :class="{ filterd: item.filterd }">
                                <td>{{ item.uname }}</td>
                                <td v-if="item.type == 'danmu'">弹幕</td>
                                <td v-if="item.type == 'danmu'">{{ item.msg }}</td>

                                <td v-if="item.type == 'gift'">礼物</td>
                                <td v-if="item.type == 'gift'">赠送了{{ item.num }}个{{ item.giftName }}</td>

                                <td v-if="item.type == 'guardBuy'">上舰</td>
                                <td v-if="item.type == 'guardBuy'">赠送了{{ item.num }}个月{{ item.giftName }}</td>

                                <td v-if="item.type == 'like' || item.type == 'subscribe' || item.type == 'welcome' || item.type == 'superChat'">其他</td>
                                <td v-if="item.type == 'like'">点赞</td>
                                <td v-if="item.type == 'subscribe'">关注</td>
                                <td v-if="item.type == 'welcome'">欢迎</td>
                                <td v-if="item.type == 'superChat'">发送了{{ item.price }}元的SC: {{ item.msg }}</td>
                            </tr>
                        </template>
                    </tbody>
                </v-table>
            </div>
    </v-card>
</template>

<style scoped>
.v-card {
    display: flex;
    flex-direction: column;
}
.v-container {
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
    background-color: rgba(255, 0, 0, 0.7);
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
</style>

<script setup lang="ts">
import { WebsocketBroadcastMessage } from "@/types/WebsocketBroadcastMessage";
import { onUpdated } from "vue";
import { ref } from "vue";

const container = ref<HTMLDivElement | null>(null);
const locked = ref(true);

const props = defineProps({
    data: {
        type: Array,
        required: true
    }
});

onUpdated(() => {
    if (container.value && locked.value) {
        container.value.scrollTop = container.value.scrollHeight;
    }
});

function toggleLock() {
    locked.value = !locked.value;
    if (container.value && locked.value) {
        container.value.scrollTop = container.value.scrollHeight;
    }
}
</script>