<template>
    <v-card class="mx-auto" elevation="4">
        <v-card-title tabindex="2">综合配置</v-card-title>

        <v-form class="overflow-auto">
            <v-text-field v-model="config.filter.danmu.enable" label="启用弹幕朗读"></v-text-field>
            <v-text-field v-model="config.filter.danmu.emojiEnable" label="启用弹幕表情朗读"></v-text-field>
            <v-text-field v-model="config.filter.danmu.fansMedalGuardLevelBigger" label="大航海大于"></v-text-field>
            <v-text-field v-model="config.filter.danmu.fansMedalLevelBigger" label="粉丝牌等级大于"></v-text-field>
            <v-text-field v-model="config.filter.danmu.lengthShorter" label="文本长度小于"></v-text-field>
            <v-text-field v-model="config.filter.danmu.blacklistKeywords" label="黑名单关键词"></v-text-field>
            <v-text-field v-model="config.filter.danmu.blacklistUsers" label="黑名单用户"></v-text-field>
            <v-text-field v-model="config.filter.danmu.whitelistUsers" label="白名单用户"></v-text-field>

            <v-text-field v-model="config.filter.gift.enable" label="启用礼物朗读"></v-text-field>
            <v-text-field v-model="config.filter.gift.freeGiftEnable" label="启用免费礼物朗读"></v-text-field>
            <v-text-field v-model="config.filter.gift.freeGiftCountBigger" label="免费礼物数量大于"></v-text-field>
            <v-text-field v-model="config.filter.gift.moneyGiftPriceBigger" label="付费礼物金额大于"></v-text-field>

            <v-text-field v-model="config.filter.guardBuy.enable" label="启用舰长朗读"></v-text-field>

            <v-text-field v-model="config.filter.like.enable" label="启用点赞朗读"></v-text-field>
            <v-text-field v-model="config.filter.like.deduplicate" label="去除重复点赞"></v-text-field>

            <v-text-field v-model="config.filter.welcome.enable" label="启用进入直播间朗读"></v-text-field>
            <v-text-field v-model="config.filter.welcome.fansMedalGuardLevelBigger" label="大航海大于"></v-text-field>
            <v-text-field v-model="config.filter.welcome.fansMedalLevelBigger" label="粉丝牌等级大于"></v-text-field>

            <v-text-field v-model="config.filter.subscribe.enable" label="启用订阅朗读"></v-text-field>
        </v-form>
    </v-card>
</template>

<style scoped>
.v-card {
    display: flex;
    flex-direction: column;
}
.v-form {
    padding: 0 16px 16px 16px;
}
</style>

<script lang="ts" setup>
import { ref } from 'vue';
import { DynamicConfig } from "../types/DynamicConfig";
import { getDynamicConfig } from '@/services/Database';

const config = ref(undefined as unknown as DynamicConfig);
config.value = {
    filter: {
        danmu: {
            enable: true,
            emojiEnable: true,
            fansMedalGuardLevelBigger: 0,
            fansMedalLevelBigger: 0,
            lengthShorter: 0,
            blacklistKeywords: [],
            blacklistUsers: [],
            whitelistUsers: []
        },
        gift: {
            enable: true,
            freeGiftEnable: true,
            freeGiftCountBigger: 0,
            moneyGiftPriceBigger: 0
        },
        guardBuy: {
            enable: true
        },
        like: {
            enable: true,
            deduplicate: true
        },
        welcome: {
            enable: true,
            fansMedalGuardLevelBigger: 0,
            fansMedalLevelBigger: 0
        },
        subscribe: {
            enable: true
        }
    }
};

getDynamicConfig().then(msg => {
    config.value = msg;
});
</script>