<template>
    <v-card class="mx-auto" elevation="4" @keydown="onKeydown">
        <v-card-title>
            <div><p tabindex="0">实时配置</p></div>
        </v-card-title>

        <v-form class="overflow-auto">
            <v-btn class="clean-button" block :loading="flushing" color="red" @click="onFlush">清空待读语音队列</v-btn>
            <v-divider></v-divider>

            <v-switch v-model="config.filter.danmu.enable" inset color="blue" label="启用弹幕朗读" aria-label="启用弹幕朗读"></v-switch>
            <v-switch v-model="config.filter.danmu.emojiEnable" inset color="blue" label="启用弹幕表情朗读" aria-label="启用弹幕表情朗读"></v-switch>
            <v-switch v-model="config.filter.danmu.deduplicate" inset color="blue" label="去除短时间内重复弹幕" aria-label="去除短时间内重复弹幕"></v-switch>
            <v-switch v-model="config.filter.danmu.isFansMedalBelongToLive" inset color="blue" label="粉丝牌必须为本直播间" aria-label="粉丝牌必须为本直播间"></v-switch>
            <v-select v-model="config.filter.danmu.fansMedalGuardLevelBigger" :items="[{title: '无', value: 0}, {title: '舰长', value: 1}, {title: '提督', value: 2}, {title: '总督', value: 3}]" label="大航海大于等于" aria-label="弹幕大航海大于等于"></v-select>
            <v-text-field type="number" v-model="config.filter.danmu.fansMedalLevelBigger" label="粉丝牌等级大于等于" aria-label="弹幕粉丝牌等级大于等于"></v-text-field>
            <v-text-field type="number" v-model="config.filter.danmu.lengthShorter" label="文本长度小于等于" aria-label="弹幕文本长度小于等于"></v-text-field>
            <v-text-field v-model="blacklistKeywords" label="黑名单关键词(逗号分隔)" aria-label="弹幕黑名单关键词(逗号分隔)"></v-text-field>
            <v-text-field v-model="blacklistUsers" label="黑名单用户UID(逗号分隔)" aria-label="弹幕黑名单用户UID(逗号分隔)"></v-text-field>
            <v-text-field v-model="whitelistUsers" label="白名单用户UID(逗号分隔)" aria-label="弹幕白名单用户UID(逗号分隔)"></v-text-field>
            <v-text-field v-model="whitelistKeywords" label="白名单关键词(逗号分隔)" aria-label="弹幕白名单关键词(逗号分隔)"></v-text-field>
            <v-divider></v-divider>

            <v-switch v-model="config.filter.gift.enable" inset color="blue" label="启用礼物朗读" aria-label="启用礼物朗读"></v-switch>
            <v-switch v-model="config.filter.gift.freeGiftEnable" inset color="blue" label="启用免费礼物朗读" aria-label="启用免费礼物朗读"></v-switch>
            <v-text-field type="number" v-model="config.filter.gift.deduplicateTime" label="几秒内礼物不重复朗读" aria-label="几秒内礼物不重复朗读"></v-text-field>
            <v-text-field type="number" v-model="config.filter.gift.freeGiftCountBigger" label="免费礼物数量大于等于" aria-label="免费礼物数量大于等于"></v-text-field>
            <v-text-field type="number" v-model="config.filter.gift.moneyGiftPriceBigger" label="付费礼物金额大于等于" aria-label="付费礼物金额大于等于"></v-text-field>
            <v-divider></v-divider>

            <v-switch v-model="config.filter.guardBuy.enable" inset color="blue" label="启用舰长朗读" aria-label="启用舰长朗读"></v-switch>
            <v-divider></v-divider>

            <v-switch v-model="config.filter.like.enable" inset color="blue" label="启用点赞朗读" aria-label="启用点赞朗读"></v-switch>
            <v-switch v-model="config.filter.like.deduplicate" inset color="blue" label="去除重复点赞" aria-label="去除重复点赞"></v-switch>
            <v-divider></v-divider>

            <v-switch v-model="config.filter.welcome.enable" inset color="blue" label="启用进入直播间朗读" aria-label="启用进入直播间朗读"></v-switch>
            <v-switch v-model="config.filter.welcome.isFansMedalBelongToLive" inset color="blue" label="粉丝牌必须为本直播间" aria-label="粉丝牌必须为本直播间"></v-switch>
            <v-select v-model="config.filter.welcome.fansMedalGuardLevelBigger" :items="[{title: '无', value: 0}, {title: '舰长', value: 1}, {title: '提督', value: 2}, {title: '总督', value: 3}]" label="大航海大于等于" aria-label="直播间朗读大航海大于等于"></v-select>
            <v-text-field type="number" v-model="config.filter.welcome.fansMedalLevelBigger" label="粉丝牌等级大于等于" aria-label="直播间朗读粉丝牌等级大于等于"></v-text-field>
            <v-divider></v-divider>

            <v-switch v-model="config.filter.subscribe.enable" inset color="blue" label="启用关注朗读" aria-label="启用关注朗读"></v-switch>
            <v-divider></v-divider>

            <v-switch v-model="config.filter.superChat.enable" inset color="blue" label="启用醒目留言朗读" aria-label="启用醒目留言朗读"></v-switch>
            <v-divider></v-divider>

            <v-switch v-model="config.filter.warning.enable" inset color="blue" label="启用超管警告朗读" aria-label="启用超管警告朗读"></v-switch>
            <v-divider></v-divider>

            <v-select class="block-select" v-model="config.tts.speaker" :items="ttsSpeakers" label="TTS音频通道" aria-label="TTS音频通道"></v-select>
            <v-select v-model="config.tts.voice" :items="ttsCNVoices" label="主TTS发音引擎" aria-label="主TTS发音引擎"></v-select>
            <v-slider v-model="config.tts.rate" label="总语速" hint="TTS语速(包括其他语言)" min="1" max="100" step="1"></v-slider>
            <v-slider v-model="config.tts.volume" label="总音量" hint="TTS音量(包括其他语言)" min="1" max="100" step="1"></v-slider>

            <v-select v-model="config.tts.history.voice" :items="ttsCNVoices" label="历史模块TTS发音引擎" aria-label="历史模块TTS发音引擎"></v-select>
            <v-slider v-model="config.tts.history.rate" label="总语速" hint="历史模块TTS语速" min="1" max="100" step="1"></v-slider>
            <v-slider v-model="config.tts.history.volume" label="总音量" hint="历史模块TTS音量" min="1" max="100" step="1"></v-slider>

            <v-switch v-model="config.tts.japanese.enable" inset color="blue" label="启用日语朗读" aria-label="启用日语朗读"></v-switch>
            <v-select v-model="config.tts.japanese.voice" :items="ttsJPVoices" label="日语TTS发音引擎" aria-label="日语TTS发音引擎"></v-select>
            <v-slider v-model="config.tts.japanese.rate" label="日语相对语速" hint="TTS日语相对语速" min="1" max="100" step="1"></v-slider>
            <v-slider v-model="config.tts.japanese.volume" label="日语相对音量" hint="TTS日语相对音量" min="1" max="100" step="1"></v-slider>

            <v-divider></v-divider>
            <v-btn class="save-button" :loading="saving" color="blue" @click="onSave" aria-label="实时配置保存(可以使用键盘Ctrl+S保存)" block>保存</v-btn>
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
.clean-button {
    margin-bottom: 16px;
}
.save-button {
    margin-top: 16px;
}
.block-select {
    margin-top: 16px;
}
</style>

<script lang="ts" setup>
import { ref } from 'vue';
import { DynamicConfig } from "../types/DynamicConfig";
import { getDynamicConfig, setDynamicConfig, onWSState, flushQueue, getAllVoices, getAllSpeakers, onWSMessages } from '@/services/Database';

const ttsCNVoices = ref([] as { title: string, value: string }[]);
const ttsJPVoices = ref([] as { title: string, value: string }[]);
const ttsSpeakers = ref([] as { title: string, value: string }[]);
const blacklistKeywords = ref("");
const blacklistUsers = ref("");
const whitelistUsers = ref("");
const whitelistKeywords = ref("");
const config = ref(undefined as unknown as DynamicConfig);
config.value = {
    tts: {
        speaker: "",
        volume: 100,
        voice: "",
        rate: 100,
        history: {
            voice: "",
            rate: 100,
            volume: 100
        },
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
            deduplicate: true,
            isFansMedalBelongToLive: true,
            fansMedalGuardLevelBigger: 0,
            fansMedalLevelBigger: 0,
            lengthShorter: 0,
            blacklistKeywords: [],
            blacklistUsers: [],
            whitelistUsers: [],
            whitelistKeywords: []
        },
        gift: {
            enable: true,
            freeGiftEnable: true,
            deduplicateTime: 0,
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
            isFansMedalBelongToLive: true,
            fansMedalGuardLevelBigger: 0,
            fansMedalLevelBigger: 0
        },
        subscribe: {
            enable: true
        },
        superChat: {
            enable: true
        },
        warning: {
            enable: true
        }
    }
};
const reading = ref(true);
const saving = ref(false);
const flushing = ref(false);

function parseConfig(data: DynamicConfig) {
    reading.value = true;
    (async () => {
        config.value = data;
        blacklistKeywords.value = config.value.filter.danmu.blacklistKeywords.join('，');
        blacklistUsers.value = config.value.filter.danmu.blacklistUsers.join('，');
        whitelistUsers.value = config.value.filter.danmu.whitelistUsers.join('，');
        whitelistKeywords.value = config.value.filter.danmu.whitelistKeywords.join('，');
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
        ttsSpeakers.value = [];
        (await getAllSpeakers()).forEach(speaker => {
            ttsSpeakers.value.push({
                title: speaker,
                value: speaker
            });
        });
    })().then(msg => {
        reading.value = false;
    }).catch(err => {
        console.error(err);
        reading.value = false;
        alert('读取失败');
    });
}

onWSMessages.subscribe((event) => {
    if (event.type !== 'config') {
        return;
    }
    parseConfig(event.data);
});

function onSave() {
    saving.value = true;
    /* 强制转换number类型 */
    config.value.filter.danmu.fansMedalGuardLevelBigger = Number(config.value.filter.danmu.fansMedalGuardLevelBigger);
    config.value.filter.danmu.fansMedalLevelBigger = Number(config.value.filter.danmu.fansMedalLevelBigger);
    config.value.filter.danmu.lengthShorter = Number(config.value.filter.danmu.lengthShorter);
    config.value.filter.gift.deduplicateTime = Number(config.value.filter.gift.deduplicateTime);
    config.value.filter.gift.freeGiftCountBigger = Number(config.value.filter.gift.freeGiftCountBigger);
    config.value.filter.gift.moneyGiftPriceBigger = Number(config.value.filter.gift.moneyGiftPriceBigger);
    config.value.filter.welcome.fansMedalGuardLevelBigger = Number(config.value.filter.welcome.fansMedalGuardLevelBigger);
    config.value.filter.welcome.fansMedalLevelBigger = Number(config.value.filter.welcome.fansMedalLevelBigger);

    /* 切割字符串 */
    config.value.filter.danmu.blacklistKeywords = blacklistKeywords.value != "" ? blacklistKeywords.value.split(/[,，]+/) : [];   
    config.value.filter.danmu.blacklistUsers = blacklistUsers.value != "" ? blacklistUsers.value.split(/[,，]+/) : [];
    config.value.filter.danmu.whitelistUsers = whitelistUsers.value != "" ? whitelistUsers.value.split(/[,，]+/) : [];
    config.value.filter.danmu.whitelistKeywords = whitelistKeywords.value != "" ? whitelistKeywords.value.split(/[,，]+/) : [];

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
        getDynamicConfig().then(msg => {
            parseConfig(msg);
        }).catch(err => {
            console.error(err);
            reading.value = false;
            alert('读取失败');
        });
    }
});

function onKeydown(event: KeyboardEvent) {
    if (event.ctrlKey && event.key === 's' || event.metaKey && event.key === 's') {
        event.preventDefault();
        onSave();
    }
}
</script>