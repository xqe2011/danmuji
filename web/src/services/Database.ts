import axios from 'axios';
import { DynamicConfig } from '@/types/DynamicConfig';
import { WebsocketBroadcastMessage } from '@/types/WebsocketBroadcastMessage';

const token = '';
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

export async function getDynamicConfig() {
    return (await axios.get(`http://${functionURL}/get_config?token=${token}`)).data as DynamicConfig;
}

export async function init(loginToken: string) {
    loginToken = token;
    websocketClient = new WebSocket(`ws://${functionURL}/ws`);
    websocketClient.onmessage = (event) => {
        const data = JSON.parse(event.data);
        websocketsMessagesCallbacks.forEach(callback => callback(data));
    };
}