import axios from 'axios';
import { DynamicConfig } from '@/types/DynamicConfig';

const token = '';
const functionURL = window.location.hostname === 'localhost' ? 'http://localhost:8080' : '/';

export async function getDynamicConfig() {
    return (await axios.get(`${functionURL}/get_config?token=${token}`)).data as DynamicConfig;
}