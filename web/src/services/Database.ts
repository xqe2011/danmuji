import axios from 'axios';
import { DynamicConfig } from '@/types/DynamicConfig';
import { WebsocketBroadcastMessage } from '@/types/WebsocketBroadcastMessage';

let token = '';
const functionURL = window.location.hostname === 'localhost' ? 'localhost:8080' : '/';
let websocketClient = undefined;
const websocketsMessagesCallbacks: ((data: WebsocketBroadcastMessage) => void)[] = []

export function registerCallback(callback: (data: WebsocketBroadcastMessage) => void) {
    websocketsMessagesCallbacks.push(callback);
}

export function unregisterCallback(callback: (data: WebsocketBroadcastMessage) => void) {
    const index = websocketsMessagesCallbacks.indexOf(callback);
    if (index !== -1) {
        websocketsMessagesCallbacks.splice(index, 1);
    }
}

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

export async function init(loginToken: string) {
    token = loginToken;
    websocketClient = new WebSocket(`ws://${functionURL}/ws`);
    websocketClient.onmessage = (event) => {
        const data = JSON.parse(event.data);
        websocketsMessagesCallbacks.forEach(callback => callback(data));
    };
}