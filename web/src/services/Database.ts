import axios from 'axios';
import { DynamicConfig } from '@/types/DynamicConfig';
import { WebsocketBroadcastMessage } from '@/types/WebsocketBroadcastMessage';
import { Subscriber } from '@/services/Subscriber';
import { EngineConfig } from '@/types/EngineConfig';

let token = '';
const functionURL = window.location.hostname === 'localhost' ? 'localhost:8080' : window.location.host;
let websocketClient = undefined;
export const onWSMessages = new Subscriber<(data: WebsocketBroadcastMessage) => void>();
export const onWSState = new Subscriber<(state: 'connecting' | 'connected') => void>(true);

async function httpExecute(url: string, method: 'GET' | 'POST', data?: any) {
    let protocol = 'http://';
    if (window.location.protocol == 'https:') {
        protocol = 'https://';
    }
    const result = (await axios.request({
        url: `${protocol}${functionURL}/api/${url}?token=${token}`,
        method: method,
        data: data
    })).data;
    if (result['status'] != 0) {
        throw new Error(result['msg']);
    }
    return result['msg'];
}

export async function getDynamicConfig() {
    const data = await httpExecute('config/dynamic', 'GET');
    return data as DynamicConfig;
}

export async function setDynamicConfig(config: DynamicConfig) {
    await httpExecute('config/dynamic', 'POST', config);
}

export async function getEngineConfig() {
    const data = await httpExecute('config/engine', 'GET');
    return data as EngineConfig;
}

export async function setEngineConfig(config: EngineConfig) {
    await httpExecute('config/engine', 'POST', config);
}


export async function flushQueue() {
    await httpExecute('flush', 'POST');
}

export async function init(loginToken: string) {
    token = loginToken;
    if (token == null || token == '' || token == undefined) {
        alert('无法登陆到服务器，未携带有效token');
        return;
    }
    let protocol = 'ws://';
    if (window.location.protocol == 'https:') {
        protocol = 'wss://';
    }
    websocketClient = new WebSocket(`${protocol}${functionURL}/ws/client?token=${token}`);
    websocketClient.onmessage = (event) => {
        const data = JSON.parse(event.data);
        onWSMessages.emit(data);
    };
    websocketClient.onopen = () => {
        console.log('[Database] Connected');
        onWSState.emit('connected');
    };
    websocketClient.onclose = () => {
        console.log('[Database] Disconnected');
        onWSState.emit('connecting');
        setTimeout(() => init(token), 1000);
    };
}