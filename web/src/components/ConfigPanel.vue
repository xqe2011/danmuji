<template>
    <v-card class="mx-auto" elevation="4">
        <v-card-title>
            <div><p tabindex="0">实时配置</p></div>
            <v-btn :loading="reading" color="green" @click="onRead">读取</v-btn>
            <v-btn :loading="saving" color="blue" @click="onSave">保存</v-btn>
        </v-card-title>

        <v-form class="overflow-auto">
            <v-btn class="block-button" block :loading="flushing" color="red" @click="onFlush">清空待读语音队列</v-btn>
            <v-divider></v-divider>

            <v-switch v-model="config.filter.danmu.enable" inset color="blue" label="启用弹幕朗读" aria-label="启用弹幕朗读"></v-switch>
            <v-switch v-model="config.filter.danmu.emojiEnable" inset color="blue" label="启用弹幕表情朗读" aria-label="启用弹幕表情朗读"></v-switch>
            <v-select v-model="config.filter.danmu.fansMedalGuardLevelBigger" :items="[{title: '无', value: 0}, {title: '舰长', value: 1}, {title: '提督', value: 2}, {title: '总督', value: 3}]" label="大航海大于等于" aria-label="弹幕大航海大于等于"></v-select>
            <v-text-field v-model="config.filter.danmu.fansMedalLevelBigger" label="粉丝牌等级大于等于" aria-label="弹幕粉丝牌等级大于等于"></v-text-field>
            <v-text-field v-model="config.filter.danmu.lengthShorter" label="文本长度小于等于" aria-label="弹幕文本长度小于等于"></v-text-field>
            <v-combobox v-model="config.filter.danmu.blacklistKeywords" label="黑名单关键词" chips multiple aria-label="弹幕黑名单关键词"></v-combobox>
            <v-combobox v-model="config.filter.danmu.blacklistUsers" label="黑名单用户UID" chips multiple aria-label="弹幕黑名单用户UID"></v-combobox>
            <v-combobox v-model="config.filter.danmu.whitelistUsers" label="白名单用户UID" chips multiple aria-label="弹幕白名单用户UID"></v-combobox>
            <v-divider></v-divider>

            <v-switch v-model="config.filter.gift.enable" inset color="blue" label="启用礼物朗读" aria-label="启用礼物朗读"></v-switch>
            <v-switch v-model="config.filter.gift.freeGiftEnable" inset color="blue" label="启用免费礼物朗读" aria-label="启用免费礼物朗读"></v-switch>
            <v-text-field v-model="config.filter.gift.freeGiftCountBigger" label="免费礼物数量大于等于" aria-label="免费礼物数量大于等于"></v-text-field>
            <v-text-field v-model="config.filter.gift.moneyGiftPriceBigger" label="付费礼物金额大于等于" aria-label="付费礼物金额大于等于"></v-text-field>
            <v-divider></v-divider>

            <v-switch v-model="config.filter.guardBuy.enable" inset color="blue" label="启用舰长朗读" aria-label="启用舰长朗读"></v-switch>
            <v-divider></v-divider>

            <v-switch v-model="config.filter.like.enable" inset color="blue" label="启用点赞朗读" aria-label="启用点赞朗读"></v-switch>
            <v-switch v-model="config.filter.like.deduplicate" inset color="blue" label="去除重复点赞" aria-label="去除重复点赞"></v-switch>
            <v-divider></v-divider>

            <v-switch v-model="config.filter.welcome.enable" inset color="blue" label="启用进入直播间朗读" aria-label="启用进入直播间朗读"></v-switch>
            <v-select v-model="config.filter.welcome.fansMedalGuardLevelBigger" :items="[{title: '无', value: 0}, {title: '舰长', value: 1}, {title: '提督', value: 2}, {title: '总督', value: 3}]" label="大航海大于等于" aria-label="直播间朗读大航海大于等于"></v-select>
            <v-text-field v-model="config.filter.welcome.fansMedalLevelBigger" label="粉丝牌等级大于等于" aria-label="直播间朗读粉丝牌等级大于等于"></v-text-field>
            <v-divider></v-divider>

            <v-switch v-model="config.filter.subscribe.enable" inset color="blue" label="启用关注朗读" aria-label="启用关注朗读"></v-switch>
            <v-divider></v-divider>

            <v-switch v-model="config.filter.superChat.enable" inset color="blue" label="启用醒目留言朗读" aria-label="启用醒目留言朗读"></v-switch>
            <v-divider></v-divider>

            <v-select v-model="config.tts.voice" :items="ttsCNVoices" label="中英文TTS发音引擎" aria-label="中英文TTS发音引擎"></v-select>
            <v-slider v-model="config.tts.rate" label="语速" hint="TTS语速" min="0" max="100"></v-slider>
            <v-slider v-model="config.tts.volume" label="音量" hint="TTS音量" min="0" max="100"></v-slider>
            <v-switch v-model="config.tts.japanese.enable" inset color="blue" label="启用日语朗读" aria-label="启用日语朗读"></v-switch>
            <v-select v-model="config.tts.japanese.voice" :items="ttsJPVoices" label="日语TTS发音引擎" aria-label="日语TTS发音引擎"></v-select>
            <v-slider v-model="config.tts.japanese.rate" label="日语语速" hint="TTS日语语速" min="0" max="100"></v-slider>
            <v-slider v-model="config.tts.japanese.volume" label="日语音量" hint="TTS日语音量" min="0" max="100"></v-slider>
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
.block-button {
    margin-bottom: 16px;
}
</style>

<script lang="ts" setup>
import { ref } from 'vue';
import { DynamicConfig } from "../types/DynamicConfig";
import { getDynamicConfig, setDynamicConfig, onWSState, flushQueue, getAllVoices } from '@/services/Database';

const ttsCNVoices = ref([] as { title: string, value: string }[]);
const ttsJPVoices = ref([] as { title: string, value: string }[]);
const config = ref(undefined as unknown as DynamicConfig);
config.value = {
    tts: {
        volume: 100,
        voice: "",
        rate: 100,
        japanese: {
            enable: true,
            voice: "",
            rate: 100,
            volume: 100
        }
    },
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
const flushing = ref(false);

function onRead() {
    reading.value = true;
    (async () => {
        config.value = await getDynamicConfig();
        ttsCNVoices.value = [];
        ttsJPVoices.value = [];
        (await getAllVoices()).forEach(voice => {
            if (voice.language === 'zh-CN') {
                ttsCNVoices.value.push({
                    title: voice.name,
                    value: voice.name
                });
            } else if(voice.language === 'ja-JP') {
                ttsJPVoices.value.push({
                    title: voice.name,
                    value: voice.name
                });
            }
        });
    })().then(msg => {
        reading.value = false;
    }).catch(err => {
        console.error(err);
        reading.value = false;
        alert('读取失败');
    });
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

function onFlush() {
    flushing.value = true;
    flushQueue().then(val => {
        flushing.value = false;
        alert('清空成功');
    }).catch(err => {
        console.error(err);
        flushing.value = false;
        alert('清空失败');
    });
}

onWSState.subscribe(data => {
    if (data == 'connected') {
        onRead();
    }
});
</script>