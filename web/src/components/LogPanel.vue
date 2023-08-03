<template>
    <v-card class="mx-auto" elevation="4">
        <v-card-title tabindex="2">弹幕日记</v-card-title>
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
                            <tr v-if="index">
                                <td>{{ item.uname }}</td>
                                <td v-if="item.type == 'danmu'">弹幕</td>
                                <td v-if="item.type == 'danmu'">{{ item.msg }}</td>

                                <td v-if="item.type == 'gift'">礼物</td>
                                <td v-if="item.type == 'gift'">赠送了{{ item.num }}个{{ item.gift_name }}</td>

                                <td v-if="item.type == 'guard_buy'">上舰</td>
                                <td v-if="item.type == 'guard_buy'">赠送了{{ item.num }}个月{{ item.gift_name }}</td>

                                <td v-if="item.type == 'like' || item.type == 'subscribe' || item.type == 'welcome'">其他</td>
                                <td v-if="item.type == 'like'">点赞</td>
                                <td v-if="item.type == 'subscribe'">关注</td>
                                <td v-if="item.type == 'welcome'">欢迎</td>
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
</style>

<script setup lang="ts">
import { WebsocketBroadcastMessage } from "@/types/WebsocketBroadcastMessage";
import { ref, watch } from "vue";

const container = ref<HTMLDivElement | null>(null);

const props = defineProps({
    data: {
        type: Array,
        required: true
    }
});

watch(props, () => {
    if (container.value) {
        container.value.scrollTop = container.value.scrollHeight;
    }
});
</script>