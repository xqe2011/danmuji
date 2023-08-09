export type DynamicConfig = {
    "tts": {
        "speaker": string,
        "volume": number,
        "voice": string,
        "rate": number,
        "japanese": {
            "enable": boolean,
            "voice": string,
            "rate": number,
            "volume": number
        }
    },
    "filter": {
        "danmu": {
            "enable": boolean,
            "emojiEnable": boolean,
            "isFansMedalBelongToLive": boolean,
            "fansMedalLevelBigger": number,
            "fansMedalGuardLevelBigger": number,
            "lengthShorter": number,
            "blacklistKeywords": string[],
            "blacklistUsers": string[],
            "whitelistUsers": string[],
        },
        "gift": {
            "enable": boolean,
            "freeGiftEnable": boolean,
            "freeGiftCountBigger": number,
            "moneyGiftPriceBigger": number,
        },
        "welcome": {
            "enable": boolean,
            "isFansMedalBelongToLive": boolean,
            "fansMedalLevelBigger": number,
            "fansMedalGuardLevelBigger": number,
        },
        "guardBuy": {
            "enable": boolean,
        },
        "like": {
            "enable": boolean,
            "deduplicate": boolean,
        },
        "subscribe": {
            "enable": boolean,
        },
        "superChat": {
            "enable": boolean,
        }
    }
};