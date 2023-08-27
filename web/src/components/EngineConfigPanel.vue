<template>
    <v-card class="mx-auto" elevation="4" @keydown="onKeydown">
        <v-card-title>
            <div><p tabindex="0">引擎配置 - 重启生效</p></div>
            <v-btn :loading="saving" color="blue" @click="onSave" aria-label="引擎配置保存(可以使用键盘Ctrl+S保存)">保存</v-btn>
        </v-card-title>

        <v-form class="overflow-auto">
            <v-text-field v-model="config.bili.liveID" label="直播间号" aria-label="直播间号"></v-text-field>
            <v-text-field v-model="config.http.token" label="HTTP令牌" aria-label="HTTP令牌"></v-text-field>
            <v-divider></v-divider>

            <v-switch v-model="config.remote.enable" inset color="blue" label="启用远程控制" aria-label="启用远程控制"></v-switch>
            <v-text-field v-model="config.remote.server" label="服务器地址" aria-label="远程控制的服务器地址"></v-text-field>
            <v-text-field v-model="config.remote.password" label="服务器密码" aria-label="远程控制的服务器密码"></v-text-field>
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
.block-divider {
    margin-bottom: 22px;
}
</style>

<script lang="ts" setup>
import { ref } from 'vue';
import { EngineConfig } from "../types/EngineConfig";
import { getEngineConfig, setEngineConfig, onWSState, logout } from '@/services/Database';

const config = ref(undefined as unknown as EngineConfig);
config.value = {
    bili: {
        liveID: 0,
    },
    http: {
        token: ""
    },
    remote: {
        enable: false,
        server: "",
        password: ""
    },
};
const reading = ref(true);
const saving = ref(false);
const logouting = ref(false);

function onRead() {
    reading.value = true;
    getEngineConfig().then(msg => {
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
    config.value.bili.liveID = Number(config.value.bili.liveID);

    setEngineConfig(config.value).then(val => {
        saving.value = false;
        alert('保存成功');
    }).catch(err => {
        console.error(err);
        saving.value = false;
        alert('保存失败');
    });
}

function onLogout() {
    logouting.value = true;

    logout().then(() => {
        logouting.value = false;
        alert('退出成功');
    }).catch(err => {
        console.error(err);
        logouting.value = false;
        alert('退出成功');
    });
}

onWSState.subscribe(data => {
    if (data == 'connected') {
        onRead();
    }
});

function onKeydown(event: KeyboardEvent) {
    if (event.ctrlKey && event.key === 's' || event.metaKey && event.key === 's') {
        event.preventDefault();
        onSave();
    }
}
</script>