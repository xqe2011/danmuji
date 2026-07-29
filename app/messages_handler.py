from .live import liveEvent
from .filter import filterDanmu, filterGift, filterGuardBuy, filterLike, filterSubscribe, filterWelcome, filterSuperChat, filterWarning
from .stats import setOutputMessagesLength, appendDanmuFilteredStats, appendGiftFilteredStats, appendWelcomeFilteredStats, appendLikeFilteredStats, appendGuardBuyFilteredStats, appendSubscribeFilteredStats, appendSuperChatFilteredStats, appendWarningFilteredStats
import time

messagesQueue = []
haveReadMessages = []
onlyReportOnceConnectingOpenLive = False
onlyReportOnceDisconnected = False
onlyReportOnceUidIs0 = False

def popMessagesQueue():
    global messagesQueue, haveReadMessages
    if len(messagesQueue) == 0:
        return None
    data = messagesQueue.pop(0)
    setOutputMessagesLength(len(messagesQueue))
    haveReadMessages.append(data)
    return data

def getHaveReadMessages():
    global haveReadMessages
    return haveReadMessages

def messagesQueueAppend(data):
    global messagesQueue
    messagesQueue.append(data)
    setOutputMessagesLength(len(messagesQueue))

def messagesQueueAppendAtStart(data):
    global messagesQueue
    messagesQueue.insert(0, data)
    setOutputMessagesLength(len(messagesQueue))

@liveEvent.on('uidIs0')
async def onUidIs0():
    global onlyReportOnceUidIs0
    if onlyReportOnceUidIs0:
        return
    onlyReportOnceUidIs0 = True
    messagesQueueAppend({
        'type': 'system',
        'time': time.time(),
        'msg': '检测到直播间接口UID为0 弹幕机可以正常运转 但是黑名单用户和白名单用户功能将失效'
    })

@liveEvent.on('liveCodeNotConfig')
async def onLiveCodeNotConfig():
    messagesQueueAppend({
        'type': 'system',
        'time': time.time(),
        'msg': '检测到未配置身份码 建议尽快配置以增加稳定性 配置方法可查看帮助文档'
    })

@liveEvent.on('connectingOpenLive')
async def onConnectingOpenLive():
    global onlyReportOnceConnectingOpenLive
    if onlyReportOnceConnectingOpenLive:
        return
    onlyReportOnceConnectingOpenLive = True
    messagesQueueAppend({
        'type': 'system',
        'time': time.time(),
        'msg': '检测到已经配置身份码 正在通过开放平台重新连接直播间'
    })

@liveEvent.on('disconnected')
async def liveConnectedHandler():
    global onlyReportOnceDisconnected
    if onlyReportOnceDisconnected:
        return
    onlyReportOnceDisconnected = True
    messagesQueueAppend({
        'type': 'system',
        'time': time.time(),
        'msg': 'B站直播间已断开连接'
    })

@liveEvent.on('connected')
async def liveConnectedHandler():
    messagesQueueAppend({
        'type': 'system',
        'time': time.time(),
        'msg': 'B站直播间已连接'
    })

@liveEvent.on('login')
async def needLoginHandler():
    messagesQueueAppend({
        'type': 'system',
        'time': time.time(),
        'msg': 'B站登陆已失效 请在弹出的企鹅弹幕机扫码登陆B站窗口中使用小号重新登录B站'
    })

@liveEvent.on('danmu')
async def onDanmu(ukey, uname, isFansMedalBelongToLive, fansMedalLevel, guardLevel, msg, isEmoji, replyUname):
    if filterDanmu(ukey, uname, isFansMedalBelongToLive, fansMedalLevel, guardLevel, msg, isEmoji):
        appendDanmuFilteredStats(ukey=ukey, uname=uname, msg=msg, isEmoji=isEmoji, filterd=False)
        messagesQueueAppend({
            'type': 'danmu',
            'time': time.time(),
            'ukey': ukey,
            'uname': uname,
            'replyUname': replyUname,
            'msg': msg
        })
    else:
        appendDanmuFilteredStats(ukey=ukey, uname=uname, msg=msg, isEmoji=isEmoji, filterd=True)

@liveEvent.on('gift')
async def onGift(ukey, uname, price, giftName, num):
    def deduplicateCallback(userInfo, giftName):
        giftInfo = userInfo['gifts'][giftName]
        messagesQueueAppend({
            'type': 'gift',
            'time': time.time(),
            'ukey': userInfo['ukey'],
            'uname': userInfo['uname'],
            'giftName': giftName,
            'num': giftInfo['count']
        })
    result = filterGift(ukey, uname, price, giftName, num, deduplicateCallback)
    if result == True:
        appendGiftFilteredStats(ukey=ukey, uname=uname, giftName=giftName, num=num, filterd=False)
        messagesQueueAppend({
            'type': 'gift',
            'time': time.time(),
            'ukey': ukey,
            'uname': uname,
            'giftName': giftName,
            'num': num
        })
    else:
        appendGiftFilteredStats(ukey=ukey, uname=uname, giftName=giftName, num=num, filterd=(result != None))

@liveEvent.on('guardBuy')
async def onGuardBuy(ukey, uname, newGuard, giftName, num):
    if filterGuardBuy(ukey, uname, newGuard, giftName, num):
        appendGuardBuyFilteredStats(ukey=ukey, uname=uname, newGuard=newGuard, giftName=giftName, num=num, filterd=False)
        messagesQueueAppend({
            'type': 'guardBuy',
            'time': time.time(),
            'ukey': ukey,
            'uname': uname,
            'newGuard': newGuard,
            'giftName': giftName,
            'num': num
        })
    else:
        appendGuardBuyFilteredStats(ukey=ukey, uname=uname, newGuard=newGuard, giftName=giftName, num=num, filterd=True)

@liveEvent.on('like')
async def onLike(ukey, uname):
    if filterLike(ukey, uname):
        appendLikeFilteredStats(ukey=ukey, uname=uname, filterd=False)
        messagesQueueAppend({
            'type': 'like',
            'time': time.time(),
            'ukey': ukey,
            'uname': uname
        })
    else:
        appendLikeFilteredStats(ukey=ukey, uname=uname, filterd=True)

@liveEvent.on('superChat')
async def onSuperChat(ukey, uname, price, msg):
    if filterSuperChat(ukey, uname, price, msg):
        appendSuperChatFilteredStats(ukey=ukey, uname=uname, price=price, msg=msg, filterd=False)
        messagesQueueAppend({
            'type': 'superChat',
            'time': time.time(),
            'ukey': ukey,
            'uname': uname,
            'price': price,
            'msg': msg
        })
    else:
        appendSuperChatFilteredStats(ukey=ukey, uname=uname, price=price, msg=msg, filterd=True)

@liveEvent.on('subscribe')
async def onSubscribe(ukey, uname):
    if filterSubscribe(ukey, uname):
        appendSubscribeFilteredStats(ukey=ukey, uname=uname, filterd=False)
        messagesQueueAppend({
            'type': 'subscribe',
            'time': time.time(),
            'ukey': ukey,
            'uname': uname
        })
    else:
        appendSubscribeFilteredStats(ukey=ukey, uname=uname, filterd=True)

@liveEvent.on('welcome')
async def onWelcome(ukey, uname):
    if filterWelcome(ukey, uname):
        appendWelcomeFilteredStats(ukey=ukey, uname=uname, filterd=False)
        messagesQueueAppend({
            'type': 'welcome',
            'time': time.time(),
            'ukey': ukey,
            'uname': uname
        })
    else:
        appendWelcomeFilteredStats(ukey=ukey, uname=uname, filterd=True)

@liveEvent.on('warning')
async def onWarning(msg, isCutOff):
    if filterWarning(msg, isCutOff):
        appendWarningFilteredStats(msg=msg, isCutOff=isCutOff, filterd=False)
        messagesQueueAppend({
            'type': 'warning',
            'time': time.time(),
            'msg': msg,
            'isCutOff': isCutOff
        })
    else:
        appendWarningFilteredStats(msg=msg, isCutOff=isCutOff, filterd=True)

async def markAllMessagesInvalid():
    global messagesQueue
    messagesQueue = [{
        'type': 'system',
        'time': time.time(),
        'msg': "已清空弹幕列表"
    }]
    setOutputMessagesLength(len(messagesQueue))