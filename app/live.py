from bilibili_api import live, Credential, user
from pyee import AsyncIOEventEmitter
from .config import getJsonConfig, updateJsonConfig
from .logger import timeLog
from .tool import isAllCharactersEmoji
from selenium import webdriver
import os, asyncio
import concurrent.futures

liveEvent = AsyncIOEventEmitter()
userCredential=Credential(getJsonConfig()['kvdb']['bili']['sessdata'], getJsonConfig()['kvdb']['bili']['jct'])
userID = None
room = live.LiveDanmaku(getJsonConfig()['engine']['bili']['liveID'], credential=userCredential)

# 0为普通用户，1为总督，2位提督，3为舰长
guardLevelMap = {
    0: 0,
    1: 3,
    2: 2,
    3: 1
}

@room.on('DANMU_MSG')
async def onDanmuCallback(event):
    uid = event["data"]["info"][2][0]
    msg = event['data']['info'][1]
    uname = event["data"]["info"][2][1]
    if len(event["data"]["info"][3]) != 0:
        isFansMedalBelongToLive = event["data"]["info"][3][3] == getJsonConfig()['engine']['bili']['liveID']
        fansMedalLevel = event["data"]["info"][3][0]
        fansMedalGuardLevel = guardLevelMap[event["data"]["info"][3][10]]
    else:
        isFansMedalBelongToLive = False
        fansMedalLevel = 0
        fansMedalGuardLevel = 0
    isEmoji = event['data']['info'][0][12] == 1 or isAllCharactersEmoji(msg)
    global userID
    if uid == userID:
        return
    timeLog(f"[Danmu] {uname}: {msg}")
    liveEvent.emit('danmu', uid, uname, isFansMedalBelongToLive, fansMedalLevel, fansMedalGuardLevel, msg, isEmoji)

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
    timeLog(f"[SuperChat] {uname} bought {price}元的SC: {msg}")
    liveEvent.emit('superChat', uid, uname, price, msg)

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
    if event["data"]["data"]["roomid"] != getJsonConfig()['engine']['bili']['liveID']:
        return
    uid = event["data"]["data"]["uid"]
    uname = event["data"]["data"]["uname"]
    isFansMedalBelongToLive = event["data"]["data"]["fans_medal"]["anchor_roomid"] == getJsonConfig()['engine']['bili']['liveID']
    fansMedalLevel = event["data"]["data"]["fans_medal"]["medal_level"]
    fansMedalGuardLevel = guardLevelMap[event["data"]["data"]["fans_medal"]["guard_level"]]
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

async def getSelfInfo():
    # 检查B站凭证是否有效
    try:
        return await user.get_self_info(userCredential)
    except:
        return None

def openBroswer():
    global userCredential
    if os.name == "nt":
        timeLog(f'[Live] B站凭证无效，使用Edge重新登录B站...')
        driver = webdriver.Edge()
    else:
        timeLog(f'[Live] B站凭证无效，使用Chrome重新登录B站...')
        driver = webdriver.Chrome()
    driver.get("https://passport.bilibili.com/pc/passport/login?gourl=https%3A%2F%2Fspace.bilibili.com")
    while not driver.current_url.startswith("https://space.bilibili.com"):
        pass
    sessdata = driver.get_cookie("SESSDATA")["value"]
    jct = driver.get_cookie("bili_jct")["value"]
    driver.quit()
    userCredential = Credential(sessdata, jct)

async def initalizeLive():
    global userCredential, userID
    # 检查B站凭证是否有效
    data = await getSelfInfo()
    if data == None:
        loop = asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            await loop.run_in_executor(pool, openBroswer)
        data = await getSelfInfo()
        # 写入配置
        nowJsonConfig = getJsonConfig()
        nowJsonConfig['kvdb']['bili']['sessdata'] = userCredential.sessdata
        nowJsonConfig['kvdb']['bili']['jct'] = userCredential.bili_jct
        await updateJsonConfig(nowJsonConfig)

    userID = data['mid']
    await connectLive()