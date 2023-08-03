export type DanmuEvent = {
    'type': 'danmu',
    'valid': boolean,
    'uid': number,
    'uname': string,
    'msg': string
};

export type GiftEvent = {
    'type': 'gift',
    'valid': boolean,
    'uid': number,
    'uname': string,
    'gift_name': string,
    'num': number
};

export type GuardBuyEvent = {
    'type': 'guard_buy',
    'valid': boolean,
    'uid': number,
    'uname': string,
    'new_guard': number,
    'gift_name': string,
    'num': number
};

export type LikeEvent = {
    'type': 'like',
    'valid': boolean,
    'uid': number,
    'uname': string
};

export type SubscribeEvent = {
    'type': 'subscribe',
    'valid': boolean,
    'uid': number,
    'uname': string
};

export type WelcomeEvent = {
    'type': 'welcome',
    'valid': boolean,
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
        'cpu_usage': number,
        'messagesQueueLength': number,
        'delay': number
    }
};