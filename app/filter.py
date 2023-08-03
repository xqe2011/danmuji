from .config import dynamicConfig

def filterDanmu(uid, uname, isFansMedalBelongToLive, fansMedalLevel, fansMedalGuardLevel, msg):
    if not dynamicConfig["filter"]["danmu"]["enable"]:
        return False
    if dynamicConfig["filter"]["danmu"]["fansMedalLevelBigger"] != 0 and fansMedalLevel < dynamicConfig["filter"]["danmu"]["fansMedalLevelBigger"]:
        return False
    if dynamicConfig["filter"]["danmu"]["fansMedalGuardLevelBigger"] != 0 and fansMedalGuardLevel < dynamicConfig["filter"]["danmu"]["fansMedalGuardLevelBigger"]:
        return False
    if dynamicConfig["filter"]["danmu"]["lengthDhorter"] != 0 and len(msg) < dynamicConfig["filter"]["danmu"]["lengthDhorter"]:
        return False
    if uid in dynamicConfig["filter"]["danmu"]["blacklistUsers"]:
        return False
    if uid in dynamicConfig["filter"]["danmu"]["whitelistUsers"]:
        return True
    for keyword in dynamicConfig["filter"]["danmu"]["blacklistKeywords"]:
        if keyword in msg:
            return False
    return True

def filterGift(uid, uname, price, giftName, num):
    if not dynamicConfig["filter"]["gift"]["enable"]:
        return False
    if price == 0:
        if not dynamicConfig["filter"]["gift"]["freeGiftEnable"]:
            return False
        if dynamicConfig["filter"]["gift"]["freeGiftCountBigger"] != 0 and num < dynamicConfig["filter"]["gift"]["freeGiftCountBigger"]:
            return False
        return True
    else:
        if dynamicConfig["filter"]["gift"]["moneyGiftPriceBigger"] != 0 and price < dynamicConfig["filter"]["gift"]["moneyGiftPriceBigger"]:
            return False
        return True

def filterWelcome(uid, uname, isFansMedalBelongToLive, fansMedalLevel, fansMedalGuardLevel):
    if not dynamicConfig["filter"]["welcome"]["enable"]:
        return False
    if dynamicConfig["filter"]["welcome"]["fansMedalLevelBigger"] != 0 and fansMedalLevel < dynamicConfig["filter"]["welcome"]["fansMedalLevelBigger"]:
        return False
    if dynamicConfig["filter"]["welcome"]["fansMedalGuardLevelBigger"] != 0 and fansMedalGuardLevel < dynamicConfig["filter"]["welcome"]["fansMedalGuardLevelBigger"]:
        return False
    return True

def filterGuardBuy(uid, uname, newGuard, giftName, num):
    if not dynamicConfig["filter"]["guardBuy"]["enable"]:
        return False
    return True

likedUids = {}
def filterLike(uid, uname, isFansMedalBelongToLive, fansMedalLevel, fansMedalGuardLevel):
    if not dynamicConfig["filter"]["like"]["enable"]:
        return False
    if dynamicConfig["filter"]["like"]["deduplicate"]:
        if uid in likedUids:
            return False
        likedUids[uid] = True
        return True
    return True

def filterSubscribe(uid, uname, isFansMedalBelongToLive, fansMedalLevel, fansMedalGuardLevel):
    if not dynamicConfig["filter"]["subscribe"]["enable"]:
        return False
    return True