from typing import Optional
from pyee.asyncio import AsyncIOEventEmitter

from blivedm.blivedm.clients import ws_base
from .config import configEvent, getJsonConfig, updateJsonConfig, disableWebProtocol
from .logger import timeLog
from .tool import isAllCharactersEmoji
from blivedm.blivedm import OpenLiveClient, BLiveClient, BaseHandler
import aiohttp, concurrent.futures, asyncio, sys, time
from bilibili_api import Credential, user, sync, login_v2, sync
from bilibili_api.utils.network import get_client
import tkinter as tk
import json

liveEvent = AsyncIOEventEmitter()
roomWeb = None
roomOpen = None
firstHeartBeat = True

# 0为普通用户，1为总督，2位提督，3为舰长
guardLevelMap = {
    0: 0,
    1: 3,
    2: 2,
    3: 1
}

async def setDisableWebProtocol():
    global roomWeb
    roomWeb.stop()

class LiveMsgHandler(BaseHandler):
    def on_client_stopped(self, client: ws_base.WebSocketClientBase, exception: Optional[Exception]):
        liveEvent.emit('disconnected')
        if roomOpen != None:
            global firstHeartBeat
            firstHeartBeat = True
            timeLog(f"[Live] Connecting OpenLive")
            liveEvent.emit('connectingOpenLive')
            asyncio.get_running_loop().call_later(3, lambda: roomOpen.start())

    def _on_heartbeat(self, client: BLiveClient, command: dict):
        global firstHeartBeat
        if firstHeartBeat:
            timeLog(f"[Live] Connected")
            liveEvent.emit('connected')
            firstHeartBeat = False

    def onDanmuCallback(self, client: BLiveClient, command: dict):
        uid = command["info"][2][0]
        msg = command['info'][1]
        uname = command["info"][2][1]
        if len(command["info"][3]) != 0:
            isFansMedalBelongToLive = command["info"][3][3] == getJsonConfig()['engine']['bili']['liveID']
            fansMedalLevel = command["info"][3][0]
            fansMedalGuardLevel = guardLevelMap[command["info"][3][10]]
        else:
            isFansMedalBelongToLive = False
            fansMedalLevel = 0
            fansMedalGuardLevel = 0
        isEmoji = command['info'][0][12] == 1 or isAllCharactersEmoji(msg)
        replyUname = json.loads(command['info'][0][15]['extra'])['reply_uname']
        timeLog(f"[Danmu] {uname}: {'@' + replyUname + ' ' if replyUname != '' else ''}{msg}")
        liveEvent.emit('danmu', uid, uname, isFansMedalBelongToLive, fansMedalLevel, fansMedalGuardLevel, msg, isEmoji, replyUname)

    def onGuardBuyCallback(self, client: BLiveClient, command: dict):
        if 'role_name' not in command['data'] or command['data']['role_name'] not in ['总督', '提督', '舰长']:
            return
        uid = command["data"]["uid"]
        num = command["data"]["num"]
        uname = command["data"]["username"]
        giftName = command['data']['role_name']
        newGuard = '第1天' == command["data"]["toast_msg"][-3:]
        timeLog(f"[GuardBuy] {uname} bought {'New ' if newGuard else ''}{giftName} x {num}.")
        liveEvent.emit('guardBuy', uid, uname, newGuard, giftName, num)

    def onSCCallback(self, client: BLiveClient, command: dict):
        uid = command["data"]["uid"]
        uname = command["data"]["user_info"]["uname"]
        price = command["data"]["price"]
        msg = command["data"]["message"]
        timeLog(f"[SuperChat] {uname} bought {price}元的SC: {msg}")
        liveEvent.emit('superChat', uid, uname, price, msg)

    def onGiftCallback(self, client: BLiveClient, command: dict):
        uid = command["data"]["uid"]
        uname = command["data"]["uname"]
        giftName = command["data"]["giftName"]
        num = command["data"]["num"]
        price = command["data"]["price"] / 1000
        price = price if command["data"]["coin_type"] == 'gold' else 0
        timeLog(f"[Gift] {uname} bought {price:.1f}元的{giftName} x {num}.")
        liveEvent.emit('gift', uid, uname, price, giftName, num)

    def onInteractWordCallback(self, client: BLiveClient, command: dict):
        if command["data"]["roomid"] != getJsonConfig()['engine']['bili']['liveID']:
            return
        uid = command["data"]["uid"]
        uname = command["data"]["uname"]
        if command["data"]["fans_medal"] != None:
            isFansMedalBelongToLive = command["data"]["fans_medal"]["anchor_roomid"] == getJsonConfig()['engine']['bili']['liveID']
            fansMedalLevel = command["data"]["fans_medal"]["medal_level"]
            fansMedalGuardLevel = guardLevelMap[command["data"]["fans_medal"]["guard_level"]]
        else:
            isFansMedalBelongToLive = False
            fansMedalLevel = 0
            fansMedalGuardLevel = 0
        isSubscribe = command["data"]["msg_type"] == 2
        timeLog(f"[Interact] {uname} {'subscribe' if isSubscribe else 'enter'} the stream.")
        if isSubscribe:
            liveEvent.emit('subscribe', uid, uname, isFansMedalBelongToLive, fansMedalLevel, fansMedalGuardLevel)
        else:
            liveEvent.emit('welcome', uid, uname, isFansMedalBelongToLive, fansMedalLevel, fansMedalGuardLevel)

    def onLikeCallback(self, client: BLiveClient, command: dict):
        uid = command["data"]["uid"]
        uname = command["data"]["uname"]
        timeLog(f"[Like] {uname} liked the stream.")
        liveEvent.emit('like', uid, uname)
    
    def onWarning(self, client: BLiveClient, command: dict):
        msg = command['msg']
        timeLog(f"[Warning] {msg}")
        liveEvent.emit('warning', msg, False)

    def onCutOff(self, client: BLiveClient, command: dict):
        msg = command['msg']
        timeLog(f"[Warning] Cut Off, {msg}")
        liveEvent.emit('warning', msg, True)

    def onOpenLiveDanmuCallback(self, client: OpenLiveClient, command: dict):
        uid = command["data"]["uid"]
        msg = command["data"]["msg"]
        uname = command["data"]["uname"]
        if command["data"]["fans_medal_wearing_status"]:
            isFansMedalBelongToLive = True
            fansMedalLevel = command["data"]["fans_medal_level"]
            fansMedalGuardLevel = guardLevelMap[command["data"]["guard_level"]]
        else:
            isFansMedalBelongToLive = False
            fansMedalLevel = 0
            fansMedalGuardLevel = 0
        isEmoji = command['data']["dm_type"] == 1 or isAllCharactersEmoji(msg)
        replyUname = command["data"]["reply_uname"]
        timeLog(f"[Danmu] {uname}: {'@' + replyUname + ' ' if replyUname != '' else ''}{msg}")
        liveEvent.emit('danmu', uid, uname, isFansMedalBelongToLive, fansMedalLevel, fansMedalGuardLevel, msg, isEmoji, replyUname)
    
    def onOpenLiveGiftCallback(self, client: OpenLiveClient, command: dict):
        uid = command["data"]["uid"]
        uname = command["data"]["uname"]
        giftName = command["data"]["gift_name"]
        num = command["data"]["gift_num"]
        price = command["data"]["price"] / 1000
        price = price if command["data"]["paid"] else 0
        timeLog(f"[Gift] {uname} bought {price:.1f}元的{giftName} x {num}.")
        liveEvent.emit('gift', uid, uname, price, giftName, num)

    def onOpenLiveGuardBuyCallback(self, client: OpenLiveClient, command: dict):
        uid = command["data"]["user_info"]["uid"]
        uname = command["data"]["user_info"]["uname"]
        num = command["data"]["guard_num"]
        giftName = guardLevelMap[command["data"]["guard_level"]]
        timeLog(f"[GuardBuy] {uname} bought {giftName} x {num}.")
        liveEvent.emit('guardBuy', uid, uname, False, giftName, num)
    
    def onOpenLiveSuperChatCallback(self, client: OpenLiveClient, command: dict):
        uid = command["data"]["uid"]
        uname = command["data"]["uname"]
        price = command["data"]["rmb"]
        msg = command["data"]["message"]
        timeLog(f"[SuperChat] {uname} bought {price}元的SC: {msg}")
        liveEvent.emit('superChat', uid, uname, price, msg)
    
    def onOpenLiveLikeCallback(self, client: OpenLiveClient, command: dict):
        uid = command["data"]["uid"]
        uname = command["data"]["uname"]
        timeLog(f"[Like] {uname} liked the stream.")
        liveEvent.emit('like', uid, uname)
    
    def onOpenLiveEnterRoomCallback(self, client: OpenLiveClient, command: dict):
        uid = command["data"]["uid"]
        uname = command["data"]["uname"]
        timeLog(f"[Interact] {uname} enter the stream.")
        liveEvent.emit('welcome', uid, uname, False, 0, 0)
    
    _CMD_CALLBACK_DICT = {
        **BaseHandler._CMD_CALLBACK_DICT,
        'DANMU_MSG': onDanmuCallback,
        'SEND_GIFT': onGiftCallback,
        'USER_TOAST_MSG': onGuardBuyCallback,
        'SUPER_CHAT_MESSAGE': onSCCallback,
        'INTERACT_WORD': onInteractWordCallback,
        'LIKE_INFO_V3_CLICK': onLikeCallback,
        'WARNING': onWarning,
        'CUT_OFF': onCutOff,
        'LIVE_OPEN_PLATFORM_DM': onOpenLiveDanmuCallback,
        'LIVE_OPEN_PLATFORM_SEND_GIFT': onOpenLiveGiftCallback,
        'LIVE_OPEN_PLATFORM_GUARD': onOpenLiveGuardBuyCallback,
        'LIVE_OPEN_PLATFORM_SUPER_CHAT': onOpenLiveSuperChatCallback,
        'LIVE_OPEN_PLATFORM_LIKE': onOpenLiveLikeCallback,
        'LIVE_OPEN_PLATFORM_LIVE_ROOM_ENTER': onOpenLiveEnterRoomCallback,
    }

async def getSelfInfo():
    # 检查B站凭证是否有效
    try:
        config = getJsonConfig()
        return await user.get_self_info(Credential(config["kvdb"]["bili"]["sessdata"], config["kvdb"]["bili"]["jct"], config["kvdb"]["bili"]["buvid3"]))
    except:
        return None

async def getSelfLiveID():
    # 获取自己直播间ID
    try:
        config = getJsonConfig()
        return (await user.User(config["kvdb"]["bili"]["uid"], Credential(config["kvdb"]["bili"]["sessdata"], config["kvdb"]["bili"]["jct"], config["kvdb"]["bili"]["buvid3"])).get_live_info())["live_room"]["roomid"]
    except:
        return None

async def getSelfLiveCode():
    # 获取自己直播间身份码
    try:
        config = getJsonConfig()
        response = await get_client().request(
            method='POST',
            url='https://api.live.bilibili.com/xlive/open-platform/v1/common/operationOnBroadcastCode',
            data={
                'csrf': config["kvdb"]["bili"]["jct"],
                'action': 1
            },
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
                'Referer': 'https://play-live.bilibili.com/',
                'Origin': 'https://play-live.bilibili.com',
            },
            cookies={'SESSDATA': config["kvdb"]["bili"]["sessdata"]}
        )
        data = response.json()
        if data["code"] != 0:
            return None
        return data["data"]["code"]
    except:
        return None

def loginBili():
    qr = login_v2.QrCodeLogin(platform=login_v2.QrCodeLoginChannel.WEB) 
    sync(qr.generate_qrcode())
    img = qr.get_qrcode_picture()
    window = tk.Tk()
    window.resizable(0,0)
    window.title("企鹅弹幕机 - 扫码登陆B站")
    image = tk.PhotoImage(file=img.url.replace("file://", ""))
    widget = tk.Label(window, compound='top', image=image)
    widget.pack()
    window.eval('tk::PlaceWindow . center')
    outputCred = None
    count = 0
    def update():
        nonlocal img, qr, count
        if count == 60:
            img = qr.get_qrcode_picture()
            image.configure(file=img.url.replace("file://", ""))
            count = 0
            timeLog(f"[Live] 刷新二维码")
        count += 1
        event = sync(qr.check_state())
        if event != login_v2.QrCodeLoginEvents.DONE:
            timeLog(f"[Live] 等待二维码登录中...")
            window.after(1000, update)
        else:
            nonlocal outputCred
            outputCred = qr.get_credential()
            window.destroy()
    window.after(1000, update)
    window.protocol("WM_DELETE_WINDOW", lambda : sys.exit(0))
    window.mainloop()
    del image, widget
    config = getJsonConfig()
    config["kvdb"]["bili"]["uid"] = int(outputCred.dedeuserid)
    config["kvdb"]["bili"]["sessdata"] = outputCred.sessdata
    config["kvdb"]["bili"]["buvid3"] = outputCred.buvid3
    config["kvdb"]["bili"]["jct"] = outputCred.bili_jct
    sync(updateJsonConfig(config))
    timeLog(f'[Live] 二维码登录完成，uid: {config["kvdb"]["bili"]["uid"]}，sessdata: {config["kvdb"]["bili"]["sessdata"]}，buvid3: {config["kvdb"]["bili"]["buvid3"]}, jct: {config["kvdb"]["bili"]["jct"]}')

async def connectLive():
    if disableWebProtocol:
        if roomOpen != None:
            roomOpen.start()
    else:
        roomWeb.start()

async def disconnectLive():
    await roomWeb.close()

async def initalizeLive():
    global roomWeb, roomOpen
    # 检查B站凭证是否有效
    if not disableWebProtocol:
        data = await getSelfInfo()
        if data == None:
            timeLog(f'[Live] B站凭证无效，使用扫码重新登录B站...')
            liveEvent.emit('login')
            loop = asyncio.get_running_loop()
            with concurrent.futures.ThreadPoolExecutor() as pool:
                await loop.run_in_executor(pool, loginBili)
            config = getJsonConfig()
            if config['kvdb']['isFirstTimeToLogin']:
                liveID = await getSelfLiveID()
                liveCode = await getSelfLiveCode()
                if liveID != None and liveCode != None:
                    timeLog(f'[Live] 第一次使用账号登陆，将默认直播间号修改为登陆的账号直播间号{liveID}并设置身份码{liveCode}')
                    config['engine']['bili']['liveID'] = liveID
                    config['engine']['bili']['liveCode'] = liveCode
                    await updateJsonConfig(config)
                else:
                    timeLog(f'[Live] 第一次使用账号登陆，但该账号未开通直播间，忽略直播间号自动设置')
    config = getJsonConfig()
    config['kvdb']['isFirstTimeToLogin'] = False
    await updateJsonConfig(config)
    if not disableWebProtocol:
        session = aiohttp.ClientSession(headers={
            'Cookie': f'SESSDATA={config["kvdb"]["bili"]["sessdata"]}; bili_jct={config["kvdb"]["bili"]["jct"]};'
        })
        roomWeb = BLiveClient(config['engine']['bili']['liveID'], uid=config["kvdb"]["bili"]["uid"], session=session)
        roomWeb.set_handler(LiveMsgHandler())
    if config['engine']['bili']['liveCode']:
        roomOpen = OpenLiveClient(config['engine']['bili']['openAPIURL'], config['engine']['bili']['liveCode'])
        roomOpen.set_handler(LiveMsgHandler())
    else:
        liveEvent.emit("liveCodeNotConfig")
    await connectLive()
