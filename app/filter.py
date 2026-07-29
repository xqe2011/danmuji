from .config import getJsonConfig
import regex
import asyncio

lastDanmuMessages = []
def filterDanmu(ukey, uname, isFansMedalBelongToLive, fansMedalLevel, guardLevel, msg, isEmoji):
    global lastDanmuMessages
    dynamicConfig = getJsonConfig()['dynamic']
    if not dynamicConfig["filter"]["danmu"]["enable"]:
        return False
    if ukey in [f"uid:{uid}" for uid in dynamicConfig["filter"]["danmu"]["whitelistUsers"]]:
        return True
    if dynamicConfig["filter"]["danmu"]["whitelistKeywords"] != []:
        for keyword in dynamicConfig["filter"]["danmu"]["whitelistKeywords"]:
            if keyword in msg:
                return True
    if dynamicConfig["filter"]["danmu"]["isFansMedalBelongToLive"] and not isFansMedalBelongToLive:
        return False
    if dynamicConfig["filter"]["danmu"]["fansMedalLevelBigger"] != 0 and fansMedalLevel < dynamicConfig["filter"]["danmu"]["fansMedalLevelBigger"]:
        return False
    if dynamicConfig["filter"]["danmu"]["fansMedalGuardLevelBigger"] != 0 and guardLevel < dynamicConfig["filter"]["danmu"]["fansMedalGuardLevelBigger"]:
        return False
    if dynamicConfig["filter"]["danmu"]["lengthShorter"] != 0 and len(msg) > dynamicConfig["filter"]["danmu"]["lengthShorter"]:
        return False
    if not dynamicConfig["filter"]["danmu"]["symbolEnable"] and regex.search(r'^[^\p{L}\p{N}]+$', msg) is not None:
        return False
    if not dynamicConfig["filter"]["danmu"]["emojiEnable"] and isEmoji:
        return False
    if ukey in [f"uid:{uid}" for uid in dynamicConfig["filter"]["danmu"]["blacklistUsers"]]:
        return False
    for keyword in dynamicConfig["filter"]["danmu"]["blacklistKeywords"]:
        if keyword in msg:
            return False
    if dynamicConfig["filter"]["danmu"]["deduplicate"]:
        if msg in lastDanmuMessages:
            lastDanmuMessages.append(None)
            return False
        lastDanmuMessages.append(msg)
        if len(lastDanmuMessages) > 10:
            lastDanmuMessages.pop(0)
    return True

giftUkeys = {}
def filterGift(ukey, uname, price, giftName, num, deduplicateCallback):
    global giftUkeys
    dynamicConfig = getJsonConfig()['dynamic']
    if not dynamicConfig["filter"]["gift"]["enable"]:
        return False
    if price == 0:
        if not dynamicConfig["filter"]["gift"]["freeGiftEnable"]:
            return False
        if dynamicConfig["filter"]["gift"]["freeGiftCountBigger"] != 0 and num < dynamicConfig["filter"]["gift"]["freeGiftCountBigger"]:
            return False
    else:
        if dynamicConfig["filter"]["gift"]["moneyGiftPriceBigger"] != 0 and price < dynamicConfig["filter"]["gift"]["moneyGiftPriceBigger"]:
            return False
    # 开启了礼物聚合后，所有的礼物都不读除非超时和变化了礼物名称
    if dynamicConfig["filter"]["gift"]["deduplicateTime"] != 0:
        if ukey not in giftUkeys:
            giftUkeys[ukey] = {
                'ukey': ukey,
                'uname': uname,
                'gifts': {}
            }
        if giftName in giftUkeys[ukey]['gifts']:
            giftUkeys[ukey]['gifts'][giftName]['task'].cancel()
        def callback():
            deduplicateCallback(giftUkeys[ukey], giftName)
            del giftUkeys[ukey]['gifts'][giftName]
        giftUkeys[ukey]['gifts'][giftName] = {
            'count': giftUkeys[ukey]['gifts'][giftName]['count'] + num if giftName in giftUkeys[ukey]['gifts']  else num,
            'task': asyncio.get_running_loop().call_later(dynamicConfig["filter"]["gift"]["deduplicateTime"], callback)
        }
        return None
    return True

def filterWelcome(ukey, uname):
    dynamicConfig = getJsonConfig()['dynamic']
    if not dynamicConfig["filter"]["welcome"]["enable"]:
        return False
    return True

def filterGuardBuy(ukey, uname, newGuard, giftName, num):
    dynamicConfig = getJsonConfig()['dynamic']
    if not dynamicConfig["filter"]["guardBuy"]["enable"]:
        return False
    return True

likedUkeys = {}
def filterLike(ukey, uname):
    dynamicConfig = getJsonConfig()['dynamic']
    if not dynamicConfig["filter"]["like"]["enable"]:
        return False
    if dynamicConfig["filter"]["like"]["deduplicate"]:
        if ukey in likedUkeys:
            return False
        likedUkeys[ukey] = True
    return True

def filterSubscribe(ukey, uname):
    dynamicConfig = getJsonConfig()['dynamic']
    if not dynamicConfig["filter"]["subscribe"]["enable"]:
        return False
    return True

def filterSuperChat(ukey, uname, price, msg):
    dynamicConfig = getJsonConfig()['dynamic']
    if not dynamicConfig["filter"]["superChat"]["enable"]:
        return False
    return True

def filterWarning(msg, isCutOff):
    dynamicConfig = getJsonConfig()['dynamic']
    if not dynamicConfig["filter"]["warning"]["enable"]:
        return False
    return True