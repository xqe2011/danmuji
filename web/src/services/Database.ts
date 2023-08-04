import axios from 'axios';
import { DynamicConfig } from '@/types/DynamicConfig';
import { WebsocketBroadcastMessage } from '@/types/WebsocketBroadcastMessage';
import { Subscriber } from '@/services/Subscriber';

let token = '';
const functionURL = window.location.hostname === 'localhost' ? 'localhost:8080' : '/';
let websocketClient = undefined;
export const onWSMessages = new Subscriber<(data: WebsocketBroadcastMessage) => void>();
export const onWSState = new Subscriber<(state: 'connecting' | 'connected') => void>(true);

async function httpExecute(url: string, method: 'GET' | 'POST', data?: any) {
    const result = (await axios.request({
        url: `http://${functionURL}/${url}?token=${token}`,
        method: method,
        data: data
    })).data;
    if (result['status'] != 0) {
        throw new Error(result['msg']);
    }
    return result['msg'];
}

export async function getDynamicConfig() {
    const data = await httpExecute('config', 'GET');
    return data as DynamicConfig;
}

export async function setDynamicConfig(config: DynamicConfig) {
    await httpExecute('config', 'POST', config);
}

export async function flushQueue() {
    await httpExecute('flush', 'POST');
}

export async function init(loginToken: string) {
    token = loginToken;
    websocketClient = new WebSocket(`ws://${functionURL}/ws`);
    websocketClient.onmessage = (event) => {
        const data = JSON.parse(event.data);
        onWSMessages.emit(data);
    };
    websocketClient.onopen = () => {
        onWSState.emit('connected');
    };
    websocketClient.onclose = () => {
        onWSState.emit('connecting');
        setTimeout(() => init(token), 1000);
    };
}