from .config import getJsonConfig
import asyncio

lastDanmuMessages = []
def filterDanmu(uid, uname, isFansMedalBelongToLive, fansMedalLevel, fansMedalGuardLevel, msg, isEmoji):
    global lastDanmuMessages
    dynamicConfig = getJsonConfig()['dynamic']
    if not dynamicConfig["filter"]["danmu"]["enable"]:
        return False
    if uid in dynamicConfig["filter"]["danmu"]["whitelistUsers"]:
        return True
    if dynamicConfig["filter"]["danmu"]["whitelistKeywords"] != []:
        for keyword in dynamicConfig["filter"]["danmu"]["whitelistKeywords"]:
            if keyword in msg:
                return True
    if dynamicConfig["filter"]["danmu"]["isFansMedalBelongToLive"] and not isFansMedalBelongToLive:
        return False
    if dynamicConfig["filter"]["danmu"]["fansMedalLevelBigger"] != 0 and fansMedalLevel < dynamicConfig["filter"]["danmu"]["fansMedalLevelBigger"]:
        return False
    if dynamicConfig["filter"]["danmu"]["fansMedalGuardLevelBigger"] != 0 and fansMedalGuardLevel < dynamicConfig["filter"]["danmu"]["fansMedalGuardLevelBigger"]:
        return False
    if dynamicConfig["filter"]["danmu"]["lengthShorter"] != 0 and len(msg) > dynamicConfig["filter"]["danmu"]["lengthShorter"]:
        return False
    if not dynamicConfig["filter"]["danmu"]["emojiEnable"] and isEmoji:
        return False
    if uid in dynamicConfig["filter"]["danmu"]["blacklistUsers"]:
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

giftUids = {}
def filterGift(uid, uname, price, giftName, num, deduplicateCallback):
    global giftUids
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
        if uid not in giftUids:
            giftUids[uid] = {
                'uid': uid,
                'uname': uname,
                'gifts': {}
            }
        if giftName in giftUids[uid]['gifts']:
            giftUids[uid]['gifts'][giftName]['task'].cancel()
        def callback():
            deduplicateCallback(giftUids[uid], giftName)
            del giftUids[uid]['gifts'][giftName]
        giftUids[uid]['gifts'][giftName] = {
            'count': giftUids[uid]['gifts'][giftName]['count'] + num if giftName in giftUids[uid]['gifts']  else num,
            'task': asyncio.get_running_loop().call_later(dynamicConfig["filter"]["gift"]["deduplicateTime"], callback)
        }
        return None
    return True

def filterWelcome(uid, uname, isFansMedalBelongToLive, fansMedalLevel, fansMedalGuardLevel):
    dynamicConfig = getJsonConfig()['dynamic']
    if not dynamicConfig["filter"]["welcome"]["enable"]:
        return False
    if dynamicConfig["filter"]["welcome"]["isFansMedalBelongToLive"] and not isFansMedalBelongToLive:
        return False
    if dynamicConfig["filter"]["welcome"]["fansMedalLevelBigger"] != 0 and fansMedalLevel < dynamicConfig["filter"]["welcome"]["fansMedalLevelBigger"]:
        return False
    if dynamicConfig["filter"]["welcome"]["fansMedalGuardLevelBigger"] != 0 and fansMedalGuardLevel < dynamicConfig["filter"]["welcome"]["fansMedalGuardLevelBigger"]:
        return False
    return True

def filterGuardBuy(uid, uname, newGuard, giftName, num):
    dynamicConfig = getJsonConfig()['dynamic']
    if not dynamicConfig["filter"]["guardBuy"]["enable"]:
        return False
    return True

likedUids = {}
def filterLike(uid, uname):
    dynamicConfig = getJsonConfig()['dynamic']
    if not dynamicConfig["filter"]["like"]["enable"]:
        return False
    if dynamicConfig["filter"]["like"]["deduplicate"]:
        if uid in likedUids:
            return False
        likedUids[uid] = True
    return True

def filterSubscribe(uid, uname, isFansMedalBelongToLive, fansMedalLevel, fansMedalGuardLevel):
    dynamicConfig = getJsonConfig()['dynamic']
    if not dynamicConfig["filter"]["subscribe"]["enable"]:
        return False
    return True

def filterSuperChat(uid, uname, price, msg):
    dynamicConfig = getJsonConfig()['dynamic']
    if not dynamicConfig["filter"]["superChat"]["enable"]:
        return False
    return True