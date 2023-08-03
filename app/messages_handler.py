from .live import liveEvent
from .logger import timeLog
from .filter import filterDanmu, filterGift, filterGuardBuy, filterLike, filterSubscribe, filterWelcome
from .stats import appendDanmuFilteredStats, appendGiftFilteredStats, appendWelcomeFilteredStats, appendLikeFilteredStats, appendGuardBuyFilteredStats, appendSubscribeFilteredStats

messagesQueue = []

@liveEvent.on('danmu')
async def onDanmu(uid, uname, isFansMedalBelongToLive, fansMedalLevel, fansMedalGuardLevel, msg):
    if filterDanmu(uid, uname, isFansMedalBelongToLive, fansMedalLevel, fansMedalGuardLevel, msg):
        appendDanmuFilteredStats(uid=uid, uname=uname, msg=msg, filterd=False)
        messagesQueue.append({
            'type': 'danmu',
            'valid': True,
            'uid': uid,
            'uname': uname,
            'msg': msg
        })
    else:
        appendDanmuFilteredStats(uid=uid, uname=uname, msg=msg, filterd=True)

@liveEvent.on('gift')
async def onGift(uid, uname, price, giftName, num):
    if filterGift(uid, uname, price, giftName, num):
        appendGiftFilteredStats(uid=uid, uname=uname, giftName=giftName, num=num, filterd=False)
        messagesQueue.append({
            'type': 'gift',
            'valid': True,
            'uid': uid,
            'uname': uname,
            'gift_name': giftName,
            'num': num
        })
    else:
        appendGiftFilteredStats(uid=uid, uname=uname, giftName=giftName, num=num, filterd=True)

@liveEvent.on('guard_buy')
async def onGuardBuy(uid, uname, newGuard, giftName, num):
    if filterGuardBuy(uid, uname, newGuard, giftName, num):
        appendGuardBuyFilteredStats(uid=uid, uname=uname, newGuard=newGuard, giftName=giftName, num=num, filterd=False)
        messagesQueue.append({
            'type': 'guard_buy',
            'valid': True,
            'uid': uid,
            'uname': uname,
            'new_guard': newGuard,
            'gift_name': giftName,
            'num': num
        })
    else:
        appendGuardBuyFilteredStats(uid=uid, uname=uname, newGuard=newGuard, giftName=giftName, num=num, filterd=True)

@liveEvent.on('like')
async def onLike(uid, uname, isFansMedalBelongToLive, fansMedalLevel, fansMedalGuardLevel):
    if filterLike(uid, uname, isFansMedalBelongToLive, fansMedalLevel, fansMedalGuardLevel):
        appendLikeFilteredStats(uid=uid, uname=uname, filterd=False)
        messagesQueue.append({
            'type': 'like',
            'valid': True,
            'uid': uid,
            'uname': uname
        })
    else:
        appendLikeFilteredStats(uid=uid, uname=uname, filterd=True)

@liveEvent.on('subscribe')
async def onSubscribe(uid, uname, isFansMedalBelongToLive, fansMedalLevel, fansMedalGuardLevel):
    if filterSubscribe(uid, uname, isFansMedalBelongToLive, fansMedalLevel, fansMedalGuardLevel):
        appendSubscribeFilteredStats(uid=uid, uname=uname, filterd=False)
        messagesQueue.append({
            'type': 'subscribe',
            'valid': True,
            'uid': uid,
            'uname': uname
        })
    else:
        appendSubscribeFilteredStats(uid=uid, uname=uname, filterd=True)

@liveEvent.on('welcome')
async def onWelcome(uid, uname, isFansMedalBelongToLive, fansMedalLevel, fansMedalGuardLevel):
    if filterWelcome(uid, uname, isFansMedalBelongToLive, fansMedalLevel, fansMedalGuardLevel):
        appendWelcomeFilteredStats(uid=uid, uname=uname, filterd=False)
        messagesQueue.append({
            'type': 'welcome',
            'valid': True,
            'uid': uid,
            'uname': uname
        })
    else:
        appendWelcomeFilteredStats(uid=uid, uname=uname, filterd=True)

async def markAllMessagesInvalid():
    for message in messagesQueue:
        message['valid'] = False