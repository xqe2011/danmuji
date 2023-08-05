import configparser
from .logger import timeLog
import json

iniConfig = configparser.RawConfigParser()
iniConfig.read('config.ini', encoding='utf-8')

BILI_LIVE_ID = iniConfig.getint('common', 'bili.liveID')
BILI_UID = iniConfig.getint('common', 'bili.uid')
BILI_SESSDATA = iniConfig.get('common', 'bili.sessdata')
BILI_JCT = iniConfig.get('common', 'bili.jct')
HTTP_TOKEN = iniConfig.get('common', 'http.token')
REMOTE_ENABLE = iniConfig.getboolean('common', 'remote.enable')
REMOTE_SERVER = iniConfig.get('common', 'remote.server')
REMOTE_PASSWORD = iniConfig.get('common', 'remote.password')

dynamicConfig = {
    "filter": {
        "danmu": {
            "enable": iniConfig.getboolean('dynamic', 'filter.danmu.enable'),
            "emojiEnable": iniConfig.getboolean('dynamic', 'filter.danmu.emojiEnable'),
            "fansMedalLevelBigger": iniConfig.getint('dynamic', 'filter.danmu.fansMedalLevelBigger'),
            "fansMedalGuardLevelBigger": iniConfig.getint('dynamic', 'filter.danmu.fansMedalGuardLevelBigger'),
            "lengthShorter": iniConfig.getint('dynamic', 'filter.danmu.lengthShorter'),
            "blacklistKeywords": iniConfig.get('dynamic', 'filter.danmu.blacklistKeywords').split(',') if iniConfig.get('dynamic', 'filter.danmu.blacklistKeywords') else [],
            "blacklistUsers": iniConfig.get('dynamic', 'filter.danmu.blacklistUsers').split(',') if iniConfig.get('dynamic', 'filter.danmu.blacklistUsers') else [],
            "whitelistUsers": iniConfig.get('dynamic', 'filter.danmu.whitelistUsers').split(',') if iniConfig.get('dynamic', 'filter.danmu.whitelistUsers') else [],
        },
        "gift": {
            "enable": iniConfig.getboolean('dynamic', 'filter.gift.enable'),
            "freeGiftEnable": iniConfig.getboolean('dynamic', 'filter.gift.enable'),
            "freeGiftCountBigger": iniConfig.getint('dynamic', 'filter.gift.freeGiftCountBigger'),
            "moneyGiftPriceBigger": iniConfig.getint('dynamic', 'filter.gift.moneyGiftPriceBigger'),
        },
        "welcome": {
            "enable": iniConfig.getboolean('dynamic', 'filter.welcome.enable'),
            "fansMedalLevelBigger": iniConfig.getint('dynamic', 'filter.welcome.fansMedalLevelBigger'),
            "fansMedalGuardLevelBigger": iniConfig.getint('dynamic', 'filter.welcome.fansMedalGuardLevelBigger'),
        },
        "guardBuy": {
            "enable": iniConfig.getboolean('dynamic', 'filter.guardBuy.enable'),
        },
        "like": {
            "enable": iniConfig.getboolean('dynamic', 'filter.like.enable'),
            "deduplicate": iniConfig.getboolean('dynamic', 'filter.like.deduplicate'),
        },
        "subscribe": {
            "enable": iniConfig.getboolean('dynamic', 'filter.subscribe.enable'),
        },
        "superChat": {
            "enable": iniConfig.getboolean('dynamic', 'filter.superChat.enable'),
        }
    }
}
timeLog(f'[Config] Loaded dynamic config: {json.dumps(dynamicConfig, ensure_ascii=False)}')


async def updateDynamicConfig(config):
    global dynamicConfig
    dynamicConfig = config
    timeLog(f'[Config] Updated dynamic config: {json.dumps(dynamicConfig, ensure_ascii=False)}')

def getDynamicConfig():
    return dynamicConfig