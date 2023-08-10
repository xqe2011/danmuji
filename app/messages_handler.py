from .live import liveEvent
from .logger import timeLog
from .filter import filterDanmu, filterGift, filterGuardBuy, filterLike, filterSubscribe, filterWelcome, filterSuperChat
from .stats import setOutputMessagesLength, appendDanmuFilteredStats, appendGiftFilteredStats, appendWelcomeFilteredStats, appendLikeFilteredStats, appendGuardBuyFilteredStats, appendSubscribeFilteredStats, appendSuperChatFilteredStats
import time

messagesQueue = []

def messagesQueueSystemAppend(text):
    global messagesQueue
    messagesQueue = [message for message in messagesQueue if message['type'] != 'system']
    messagesQueue.insert(0, {
        'type': 'system',
        'time': time.time(),
        'msg': text
    })
    setOutputMessagesLength(len(messagesQueue))

def popMessagesQueue():
    global messagesQueue
    if len(messagesQueue) == 0:
        return None
    data = messagesQueue.pop(0)
    setOutputMessagesLength(len(messagesQueue))
    return data

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
            'time': time.time(),
            'uid': uid,
            'uname': uname,
            'msg': msg
        })
    else:
        appendDanmuFilteredStats(uid=uid, uname=uname, msg=msg, isEmoji=isEmoji, filterd=True)

@liveEvent.on('gift')
async def onGift(uid, uname, price, giftName, num):
    def deduplicateCallback(userInfo, giftName):
        giftInfo = userInfo['gifts'][giftName]
        messagesQueueAppend({
            'type': 'gift',
            'time': time.time(),
            'uid': userInfo['uid'],
            'uname': userInfo['uname'],
            'giftName': giftName,
            'num': giftInfo['count']
        })
    result = filterGift(uid, uname, price, giftName, num, deduplicateCallback)
    if result == True:
        appendGiftFilteredStats(uid=uid, uname=uname, giftName=giftName, num=num, filterd=False)
        messagesQueueAppend({
            'type': 'gift',
            'time': time.time(),
            'uid': uid,
            'uname': uname,
            'giftName': giftName,
            'num': num
        })
    else:
        appendGiftFilteredStats(uid=uid, uname=uname, giftName=giftName, num=num, filterd=(result != None))

@liveEvent.on('guardBuy')
async def onGuardBuy(uid, uname, newGuard, giftName, num):
    if filterGuardBuy(uid, uname, newGuard, giftName, num):
        appendGuardBuyFilteredStats(uid=uid, uname=uname, newGuard=newGuard, giftName=giftName, num=num, filterd=False)
        messagesQueueAppend({
            'type': 'guardBuy',
            'time': time.time(),
            'uid': uid,
            'uname': uname,
            'newGuard': newGuard,
            'giftName': giftName,
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
            'time': time.time(),
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
            'time': time.time(),
            'uid': uid,
            'uname': uname,
            'price': price,
            'msg': msg
        })
    else:
        appendSuperChatFilteredStats(uid=uid, uname=uname, price=price, msg=msg, filterd=True)

@liveEvent.on('subscribe')
async def onSubscribe(uid, uname, isFansMedalBelongToLive, fansMedalLevel, fansMedalGuardLevel):
    if filterSubscribe(uid, uname, isFansMedalBelongToLive, fansMedalLevel, fansMedalGuardLevel):
        appendSubscribeFilteredStats(uid=uid, uname=uname, filterd=False)
        messagesQueueAppend({
            'type': 'subscribe',
            'time': time.time(),
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
            'time': time.time(),
            'uid': uid,
            'uname': uname
        })
    else:
        appendWelcomeFilteredStats(uid=uid, uname=uname, filterd=True)

async def markAllMessagesInvalid():
    global messagesQueue
    messagesQueue = [{
        'type': 'system',
        'time': time.time(),
        'msg': "已清空弹幕列表"
    }]
    setOutputMessagesLength(len(messagesQueue))