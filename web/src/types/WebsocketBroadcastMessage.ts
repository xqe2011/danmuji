export type DanmuEvent = {
    'type': 'danmu',
    'filterd': boolean,
    'uid': number,
    'uname': string,
    'msg': string
};

export type GiftEvent = {
    'type': 'gift',
    'filterd': boolean,
    'uid': number,
    'uname': string,
    'giftName': string,
    'num': number
};

export type GuardBuyEvent = {
    'type': 'guardBuy',
    'filterd': boolean,
    'uid': number,
    'uname': string,
    'newGuard': number,
    'giftName': string,
    'num': number
};

export type LikeEvent = {
    'type': 'like',
    'filterd': boolean,
    'uid': number,
    'uname': string
};

export type SubscribeEvent = {
    'type': 'subscribe',
    'filterd': boolean,
    'uid': number,
    'uname': string
};

export type WelcomeEvent = {
    'type': 'welcome',
    'filterd': boolean,
    'uid': number,
    'uname': string
};

export type WebsocketBroadcastMessage = {
    "events": (DanmuEvent | GiftEvent | GuardBuyEvent | LikeEvent | SubscribeEvent | WelcomeEvent)[],
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
        'cpuUsage': number,
        'messagesQueueLength': number,
        'delay': number
    }
};