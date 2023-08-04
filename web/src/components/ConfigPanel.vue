<template>
    <v-card class="mx-auto" elevation="4">
        <v-card-title tabindex="2">
            <div><p>综合配置</p></div>
            <v-btn :loading="reading" color="green" @click="onRead">读取</v-btn>
            <v-btn :loading="saving" color="blue" @click="onSave">保存</v-btn>
        </v-card-title>

        <v-form class="overflow-auto">
            <v-switch v-model="config.filter.danmu.enable" inset color="blue" label="启用弹幕朗读"></v-switch>
            <v-switch v-model="config.filter.danmu.emojiEnable" inset color="blue" label="启用弹幕表情朗读"></v-switch>
            <v-text-field v-model="config.filter.danmu.fansMedalGuardLevelBigger" label="大航海大于"></v-text-field>
            <v-text-field v-model="config.filter.danmu.fansMedalLevelBigger" label="粉丝牌等级大于"></v-text-field>
            <v-text-field v-model="config.filter.danmu.lengthShorter" label="文本长度小于"></v-text-field>
            <v-combobox v-model="config.filter.danmu.blacklistKeywords" label="黑名单关键词" chips multiple></v-combobox>
            <v-combobox v-model="config.filter.danmu.blacklistUsers" label="黑名单用户" chips multiple></v-combobox>
            <v-combobox v-model="config.filter.danmu.whitelistUsers" label="白名单用户" chips multiple></v-combobox>
            <v-divider></v-divider>

            <v-switch v-model="config.filter.gift.enable" inset color="blue" label="启用礼物朗读"></v-switch>
            <v-switch v-model="config.filter.gift.freeGiftEnable" inset color="blue" label="启用免费礼物朗读"></v-switch>
            <v-text-field v-model="config.filter.gift.freeGiftCountBigger" label="免费礼物数量大于"></v-text-field>
            <v-text-field v-model="config.filter.gift.moneyGiftPriceBigger" label="付费礼物金额大于"></v-text-field>
            <v-divider></v-divider>

            <v-switch v-model="config.filter.guardBuy.enable" inset color="blue" label="启用舰长朗读"></v-switch>
            <v-divider></v-divider>

            <v-switch v-model="config.filter.like.enable" inset color="blue" label="启用点赞朗读"></v-switch>
            <v-switch v-model="config.filter.like.deduplicate" inset color="blue" label="去除重复点赞"></v-switch>
            <v-divider></v-divider>

            <v-switch v-model="config.filter.welcome.enable" inset color="blue" label="启用进入直播间朗读"></v-switch>
            <v-text-field v-model="config.filter.welcome.fansMedalGuardLevelBigger" label="大航海大于"></v-text-field>
            <v-text-field v-model="config.filter.welcome.fansMedalLevelBigger" label="粉丝牌等级大于"></v-text-field>
            <v-divider></v-divider>

            <v-switch v-model="config.filter.subscribe.enable" inset color="blue" label="启用关注朗读"></v-switch>
            <v-divider></v-divider>

            <v-switch v-model="config.filter.superChat.enable" inset color="blue" label="启用醒目留言朗读"></v-switch>
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

<script lang="ts" setup>
import { ref, onMounted } from 'vue';
import { DynamicConfig } from "../types/DynamicConfig";
import { getDynamicConfig, setDynamicConfig } from '@/services/Database';

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
        },
        superChat: {
            enable: true
        }
    }
};
const reading = ref(true);
const saving = ref(false);

function onRead() {
    reading.value = true;
    getDynamicConfig().then(msg => {
        console.log(msg);
        config.value = msg;
        reading.value = false;
    }).catch(err => {
        console.error(err);
        reading.value = false;
        alert('读取失败');
    })
}

function onSave() {
    saving.value = true;
    /* 强制转换number类型 */
    config.value.filter.danmu.fansMedalGuardLevelBigger = Number(config.value.filter.danmu.fansMedalGuardLevelBigger);
    config.value.filter.danmu.fansMedalLevelBigger = Number(config.value.filter.danmu.fansMedalLevelBigger);
    config.value.filter.danmu.lengthShorter = Number(config.value.filter.danmu.lengthShorter);
    config.value.filter.gift.freeGiftCountBigger = Number(config.value.filter.gift.freeGiftCountBigger);
    config.value.filter.gift.moneyGiftPriceBigger = Number(config.value.filter.gift.moneyGiftPriceBigger);
    config.value.filter.welcome.fansMedalGuardLevelBigger = Number(config.value.filter.welcome.fansMedalGuardLevelBigger);
    config.value.filter.welcome.fansMedalLevelBigger = Number(config.value.filter.welcome.fansMedalLevelBigger);

    setDynamicConfig(config.value).then(val => {
        saving.value = false;
        alert('保存成功');
    }).catch(err => {
        console.error(err);
        saving.value = false;
        alert('保存失败');
    });
}

onMounted(() => {
    onRead();
});
</script>