from pyee import AsyncIOEventEmitter
from .config import getJsonConfig, updateJsonConfig
from .logger import timeLog
from .tool import isAllCharactersEmoji
from blivedm.blivedm import BLiveClient, BaseHandler, HeartbeatMessage
import aiohttp, concurrent.futures, asyncio, sys
from bilibili_api import Credential, user, sync, login_func
import tkinter as tk

liveEvent = AsyncIOEventEmitter()
room = None
firstHeartBeat = True

# 0为普通用户，1为总督，2位提督，3为舰长
guardLevelMap = {
    0: 0,
    1: 3,
    2: 2,
    3: 1
}

class LiveMsgHandler(BaseHandler):
    async def _on_heartbeat(self, client: BLiveClient, message: HeartbeatMessage):
        global firstHeartBeat
        if firstHeartBeat:
            liveEvent.emit('connected')
            firstHeartBeat = False

    async def onDanmuCallback(self, client: BLiveClient, command: dict):
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
        timeLog(f"[Danmu] {uname}: {msg}")
        liveEvent.emit('danmu', uid, uname, isFansMedalBelongToLive, fansMedalLevel, fansMedalGuardLevel, msg, isEmoji)

    async def onGuardBuyCallback(self, client: BLiveClient, command: dict):
        if 'role_name' not in command['data'] or command['data']['role_name'] not in ['总督', '提督', '舰长']:
            return
        uid = command["data"]["uid"]
        num = command["data"]["num"]
        uname = command["data"]["username"]
        giftName = command['data']['role_name']
        newGuard = '第1天' == command["data"]["toast_msg"][-3:]
        timeLog(f"[GuardBuy] {uname} bought {'New ' if newGuard else ''}{giftName} x {num}.")
        liveEvent.emit('guardBuy', uid, uname, newGuard, giftName, num)

    async def onSCCallback(self, client: BLiveClient, command: dict):
        uid = command["data"]["uid"]
        uname = command["data"]["user_info"]["uname"]
        price = command["data"]["price"]
        msg = command["data"]["message"]
        timeLog(f"[SuperChat] {uname} bought {price}元的SC: {msg}")
        liveEvent.emit('superChat', uid, uname, price, msg)

    async def onGiftCallback(self, client: BLiveClient, command: dict):
        uid = command["data"]["uid"]
        uname = command["data"]["uname"]
        giftName = command["data"]["giftName"]
        num = command["data"]["num"]
        price = command["data"]["price"] / 1000
        price = price if command["data"]["coin_type"] == 'gold' else 0
        timeLog(f"[Gift] {uname} bought {price:.1f}元的{giftName} x {num}.")
        liveEvent.emit('gift', uid, uname, price, giftName, num)

    async def onInteractWordCallback(self, client: BLiveClient, command: dict):
        if command["data"]["roomid"] != getJsonConfig()['engine']['bili']['liveID']:
            return
        uid = command["data"]["uid"]
        uname = command["data"]["uname"]
        isFansMedalBelongToLive = command["data"]["fans_medal"]["anchor_roomid"] == getJsonConfig()['engine']['bili']['liveID']
        fansMedalLevel = command["data"]["fans_medal"]["medal_level"]
        fansMedalGuardLevel = guardLevelMap[command["data"]["fans_medal"]["guard_level"]]
        isSubscribe = command["data"]["msg_type"] == 2
        timeLog(f"[Interact] {uname} {'subscribe' if isSubscribe else 'enter'} the stream.")
        if isSubscribe:
            liveEvent.emit('subscribe', uid, uname, isFansMedalBelongToLive, fansMedalLevel, fansMedalGuardLevel)
        else:
            liveEvent.emit('welcome', uid, uname, isFansMedalBelongToLive, fansMedalLevel, fansMedalGuardLevel)

    async def onLikeCallback(self, client: BLiveClient, command: dict):
        uid = command["data"]["uid"]
        uname = command["data"]["uname"]
        timeLog(f"[Like] {uname} liked the stream.")
        liveEvent.emit('like', uid, uname)
    
    async def onWarning(self, client: BLiveClient, command: dict):
        print(msg)
        msg = command['msg']
        timeLog(f"[Warning] {msg}")
        liveEvent.emit('warning', msg, False)

    async def onCutOff(self, client: BLiveClient, command: dict):
        print(msg)
        msg = command['msg']
        timeLog(f"[Warning] Cut Off, {msg}")
        liveEvent.emit('warning', msg, True)
    
    _CMD_CALLBACK_DICT = {
        **BaseHandler._CMD_CALLBACK_DICT,
        'DANMU_MSG': onDanmuCallback,
        'SEND_GIFT': onGiftCallback,
        'USER_TOAST_MSG': onGuardBuyCallback,
        'SUPER_CHAT_MESSAGE': onSCCallback,
        'INTERACT_WORD': onInteractWordCallback,
        'LIKE_INFO_V3_CLICK': onLikeCallback,
        'WARNING': onWarning,
        'CUT_OFF': onCutOff
    }

async def getSelfInfo():
    # 检查B站凭证是否有效
    try:
        config = getJsonConfig()
        return await user.get_self_info(Credential(config["kvdb"]["bili"]["sessdata"], config["kvdb"]["bili"]["jct"], config["kvdb"]["bili"]["buvid3"]))
    except:
        return None

def loginBili():
    timeLog(f'[Live] B站凭证无效，使用扫码重新登录B站...')
    img, token = login_func.get_qrcode()
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
        nonlocal img, token, count
        if count == 60:
            img, token = login_func.get_qrcode()
            image.configure(file=img.url.replace("file://", ""))
            count = 0
            timeLog(f"[Live] 刷新二维码")
        count += 1
        event, cred = login_func.check_qrcode_events(token)
        nonlocal outputCred
        outputCred = cred
        if event != login_func.QrCodeLoginEvents.DONE:
            timeLog(f"[Live] 等待二维码登录中...")
            window.after(1000, update)
        else:
            window.destroy()
    window.after(1000, update)
    window.protocol("WM_DELETE_WINDOW", lambda : sys.exit(0))
    window.mainloop()
    config = getJsonConfig()
    config["kvdb"]["bili"]["uid"] = int(outputCred.dedeuserid)
    config["kvdb"]["bili"]["sessdata"] = outputCred.sessdata
    config["kvdb"]["bili"]["buvid3"] = outputCred.buvid3
    config["kvdb"]["bili"]["jct"] = outputCred.bili_jct
    sync(updateJsonConfig(config))
    timeLog(f'[Live] 二维码登录完成，uid: {config["kvdb"]["bili"]["uid"]}，sessdata: {config["kvdb"]["bili"]["sessdata"]}，buvid3: {config["kvdb"]["bili"]["buvid3"]}, jct: {config["kvdb"]["bili"]["jct"]}')

async def connectLive():
    room.start()

async def disconnectLive():
    await room.close()

async def initalizeLive():
    global room
    # 检查B站凭证是否有效
    data = await getSelfInfo()
    if data == None:
        loop = asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            await loop.run_in_executor(pool, loginBili)
    config = getJsonConfig()
    session = aiohttp.ClientSession(headers={
        'Cookie': f'buvid3={config["kvdb"]["bili"]["buvid3"]}; SESSDATA={config["kvdb"]["bili"]["sessdata"]}; bili_jct={config["kvdb"]["bili"]["jct"]};'
    })
    room = BLiveClient(config['engine']['bili']['liveID'], ssl=True, uid=config["kvdb"]["bili"]["uid"], session=session)
    room.add_handler(LiveMsgHandler())
    await connectLive()