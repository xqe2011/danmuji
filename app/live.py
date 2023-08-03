from bilibili_api import live, Credential
from pyee import EventEmitter
from .config import BILI_LIVE_ID, BILI_SESSDATA, BILI_JCT, BILI_UID
from .logger import timeLog

liveEvent = EventEmitter()
room = live.LiveDanmaku(BILI_LIVE_ID, credential=Credential(BILI_SESSDATA, BILI_JCT))

@room.on('DANMU_MSG')
async def onDanmuCallback(event):
    uid = event["data"]["info"][2][0]
    msg = event['data']['info'][1]
    uname = event["data"]["info"][2][1]
    isFansMedalBelongToLive = event["data"]["data"]["fans_medal"]["anchor_roomid"] == BILI_UID
    fansMedalLevel = event["data"]["data"]["fans_medal"]["medal_level"]
    fansMedalGuardLevel = event["data"]["data"]["fans_medal"]["guard_level"]
    if uid == BILI_UID:
        return
    timeLog(f"[Danmu] {uname}: {msg}")
    liveEvent.emit('danmu', uid, uname, isFansMedalBelongToLive, fansMedalLevel, fansMedalGuardLevel, msg)

@room.on('USER_TOAST_MSG')
async def onGuardBuyCallback(event):
    if 'role_name' not in event['data']['data'] or event['data']['data']['role_name'] not in ['总督', '提督', '舰长']:
        return
    uid = event["data"]["data"]["uid"]
    num = event["data"]["data"]["num"]
    uname = event["data"]["data"]["username"]
    giftName = event['data']['data']['role_name']
    newGuard = '第1天' == event["data"]["data"]["toast_msg"][-3:]
    timeLog(f"[GuardBuy] {uname} bought {'New ' if newGuard else ''}{giftName} x {num}.")
    liveEvent.emit('guardBuy', uid, uname, newGuard, giftName, num)

@room.on('SUPER_CHAT_MESSAGE')
async def onSCCallback(event):
    uid = event["data"]["data"]["uid"]
    uname = event["data"]["data"]["user_info"]["uname"]
    price = event["data"]["data"]["price"]
    msg = event["data"]["data"]["message"]
    timeLog(f"[SC] {uname} bought {price}元的SC: {msg}")
    liveEvent.emit('sc', uid, uname, price, msg)

@room.on('SEND_GIFT')
async def onGiftCallback(event):
    uid = event["data"]["data"]["uid"]
    uname = event["data"]["data"]["uname"]
    giftName = event["data"]["data"]["giftName"]
    num = event["data"]["data"]["num"]
    price = event["data"]["data"]["price"] / 1000
    price = price if event["data"]["data"]["coin_type"] == 'gold' else 0
    timeLog(f"[Gift] {uname} bought {price:.1f}元的{giftName} x {num}.")
    liveEvent.emit('gift', uid, uname, price, giftName, num)

@room.on('INTERACT_WORD')
async def onInteractWordCallback(event):
    if event["data"]["data"]["roomid"] != BILI_LIVE_ID:
        return
    uid = event["data"]["data"]["uid"]
    uname = event["data"]["data"]["uname"]
    isFansMedalBelongToLive = event["data"]["data"]["fans_medal"]["anchor_roomid"] == BILI_UID
    fansMedalLevel = event["data"]["data"]["fans_medal"]["medal_level"]
    fansMedalGuardLevel = event["data"]["data"]["fans_medal"]["guard_level"]
    isSubscribe = event["data"]["data"]["msg_type"] == 2
    timeLog(f"[Interact] {uname} {'subscribe' if isSubscribe else 'enter'} the stream.")
    if isSubscribe:
        liveEvent.emit('subscribe', uid, uname, isFansMedalBelongToLive, fansMedalLevel, fansMedalGuardLevel)
    else:
        liveEvent.emit('welcome', uid, uname, isFansMedalBelongToLive, fansMedalLevel, fansMedalGuardLevel)

@room.on('LIKE_INFO_V3_CLICK')
async def onLikeCallback(event):
    uid = event["data"]["data"]["uid"]
    uname = event["data"]["data"]["uname"]
    timeLog(f"[Like] {uname} liked the stream.")
    liveEvent.emit('like', uid, uname)

async def connectLive():
    await room.connect()

async def disconnectLive():
    await room.disconnect()