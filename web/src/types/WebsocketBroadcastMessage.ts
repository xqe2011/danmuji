import { DynamicConfig } from "./DynamicConfig";

export type DanmuEvent = {
    'type': 'danmu',
    'filterd': boolean,
    'ukey': number,
    'uname': string,
    'msg': string
};

export type GiftEvent = {
    'type': 'gift',
    'filterd': boolean,
    'ukey': number,
    'uname': string,
    'giftName': string,
    'num': number
};

export type GuardBuyEvent = {
    'type': 'guardBuy',
    'filterd': boolean,
    'ukey': number,
    'uname': string,
    'newGuard': number,
    'giftName': string,
    'num': number
};

export type LikeEvent = {
    'type': 'like',
    'filterd': boolean,
    'ukey': number,
    'uname': string
};

export type SubscribeEvent = {
    'type': 'subscribe',
    'filterd': boolean,
    'ukey': number,
    'uname': string
};

export type WelcomeEvent = {
    'type': 'welcome',
    'filterd': boolean,
    'ukey': number,
    'uname': string
};

export type SuperChatEvent = {
    "type": "superChat",
    "filterd": boolean,
    "ukey": number,
    "uname": string,
    "price": number,
    "msg": string
};

export type ConfigEvent = DynamicConfig;

export type StatsEvent = {
    "events": (DanmuEvent | GiftEvent | GuardBuyEvent | LikeEvent | SubscribeEvent | WelcomeEvent | SuperChatEvent)[],
    "stats": {
        'filteredDanmu': number,
        'rawDanmu': number,
        'filteredGift': number,
        'rawGift': number,
        'filteredWelcome': number,
        'rawWelcome': number,
        'filteredLike': number,
        'rawLike': number,
        'filteredGuardBuy': number,
        'rawGuardBuy': number,
        'filteredSubscribe': number,
        'rawSubscribe': number,
        'filteredSuperChat': number,
        'rawSuperChat': number,
        'cpuUsage': number,
        'messagesQueueLength': number,
        'delay': number
    }
};

export type WebsocketBroadcastMessage = {
    "type": "stats",
    "data": StatsEvent
} | {
    "type": "config",
    "data": ConfigEvent
};