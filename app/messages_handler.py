from .live import liveEvent
from .logger import timeLog
from .filter import filterDanmu, filterGift, filterGuardBuy, filterLike, filterSubscribe, filterWelcome, filterSuperChat
from .stats import setOutputMessagesLength, appendDanmuFilteredStats, appendGiftFilteredStats, appendWelcomeFilteredStats, appendLikeFilteredStats, appendGuardBuyFilteredStats, appendSubscribeFilteredStats, appendSuperChatFilteredStats

messagesQueue = []

def messagesQueueAppend(data):
    global messagesQueue
    messagesQueue.append(data)
    setOutputMessagesLength(len(messagesQueue))

@liveEvent.on('danmu')
async def onDanmu(uid, uname, isFansMedalBelongToLive, fansMedalLevel, fansMedalGuardLevel, msg, isEmoji):
    if filterDanmu(uid, uname, isFansMedalBelongToLive, fansMedalLevel, fansMedalGuardLevel, msg, isEmoji):
        appendDanmuFilteredStats(uid=uid, uname=uname, msg=msg, isEmoji=isEmoji, filterd=False)
        messagesQueueAppend({
            'type': 'danmu',
            'uid': uid,
            'uname': uname,
            'msg': msg
        })
    else:
        appendDanmuFilteredStats(uid=uid, uname=uname, msg=msg, isEmoji=isEmoji, filterd=True)

@liveEvent.on('gift')
async def onGift(uid, uname, price, giftName, num):
    if filterGift(uid, uname, price, giftName, num):
        appendGiftFilteredStats(uid=uid, uname=uname, giftName=giftName, num=num, filterd=False)
        messagesQueueAppend({
            'type': 'gift',
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
        messagesQueueAppend({
            'type': 'guard_buy',
            'uid': uid,
            'uname': uname,
            'new_guard': newGuard,
            'gift_name': giftName,
            'num': num
        })
    else:
        appendGuardBuyFilteredStats(uid=uid, uname=uname, newGuard=newGuard, giftName=giftName, num=num, filterd=True)

@liveEvent.on('like')
async def onLike(uid, uname):
    if filterLike(uid, uname):
        appendLikeFilteredStats(uid=uid, uname=uname, filterd=False)
        messagesQueueAppend({
            'type': 'like',
            'uid': uid,
            'uname': uname
        })
    else:
        appendLikeFilteredStats(uid=uid, uname=uname, filterd=True)

@liveEvent.on('superChat')
async def onSuperChat(uid, uname, price, msg):
    if filterSuperChat(uid, uname, price, msg):
        appendSuperChatFilteredStats(uid=uid, uname=uname, price=price, msg=msg, filterd=False)
        messagesQueueAppend({
            'type': 'superChat',
            'uid': uid,
            'uname': uname
        })
    else:
        appendSuperChatFilteredStats(uid=uid, uname=uname, price=price, msg=msg, filterd=True)

@liveEvent.on('subscribe')
async def onSubscribe(uid, uname, isFansMedalBelongToLive, fansMedalLevel, fansMedalGuardLevel):
    if filterSubscribe(uid, uname, isFansMedalBelongToLive, fansMedalLevel, fansMedalGuardLevel):
        appendSubscribeFilteredStats(uid=uid, uname=uname, filterd=False)
        messagesQueueAppend({
            'type': 'subscribe',
            'uid': uid,
            'uname': uname
        })
    else:
        appendSubscribeFilteredStats(uid=uid, uname=uname, filterd=True)

@liveEvent.on('welcome')
async def onWelcome(uid, uname, isFansMedalBelongToLive, fansMedalLevel, fansMedalGuardLevel):
    if filterWelcome(uid, uname, isFansMedalBelongToLive, fansMedalLevel, fansMedalGuardLevel):
        appendWelcomeFilteredStats(uid=uid, uname=uname, filterd=False)
        messagesQueueAppend({
            'type': 'welcome',
            'uid': uid,
            'uname': uname
        })
    else:
        appendWelcomeFilteredStats(uid=uid, uname=uname, filterd=True)

async def markAllMessagesInvalid():
    global messagesQueue
    messagesQueue = []
    setOutputMessagesLength(len(messagesQueue))