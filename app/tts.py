import asyncio, time, re
from .messages_handler import popMessagesQueue
from .stats import appendDelay
from .config import getJsonConfig
from .logger import timeLog
import concurrent.futures
import win32com.client as wincl

ttsEngine = None
lastRate = None
lastVolume = None

def init():
    global ttsEngine
    dynamicConfig = getJsonConfig()['tts']
    ttsEngine = wincl.Dispatch("SAPI.SpVoice")
    vcs = ttsEngine.GetVoices()
    targetVoice = None
    for i in range(0, vcs.Count):
        item = vcs.Item(i)
        name = item.GetAttribute("Name")
        timeLog(f'[TTS] Found tts voices: {name}')
        if dynamicConfig['voice'] in name:
            targetVoice = item
    timeLog(f'[TTS] Use voice: {targetVoice.GetAttribute("Name")} as target voice')
    ttsEngine.Voice = targetVoice
    tts("TTS模块初始化成功")


def tts(text):
    global ttsEngine, lastRate, lastVolume
    ttsConfig = getJsonConfig()['tts']
    if lastVolume != ttsConfig['volume']:
        ttsEngine.Volume = ttsConfig['volume']
        lastVolume = ttsConfig['volume']
    if lastRate != ttsConfig['rate']:
        ttsEngine.Rate = ttsConfig['rate']
        lastRate = ttsConfig['rate']
    # 支持日语
    if ttsConfig['japanese']['enable']:
        text = re.sub(r'[\u3040-\u309F\u30A0-\u30FF]+', r'<lang langid="411">\g<0></lang>', text)
    ttsEngine.Speak('<lang langid="804">' + text + '</lang>')

def messagesToText(msg):
    if msg['type'] == 'danmu':
        return f"{msg['uname']}说{msg['msg']}"
    elif msg['type'] == 'gift':
        return f"感谢{msg['uname']}送出的{msg['num']}个{msg['giftName']}"
    elif msg['type'] == 'guardBuy':
        return f"感谢{msg['uname']}购买{msg['num']}个月的{msg['giftName']}"
    elif msg['type'] == 'like':
        return f"感谢{msg['uname']}点赞"
    elif msg['type'] == 'superChat':
        return f"感谢{msg['uname']}的{msg['price']}元的醒目留言{msg['msg']}"
    elif msg['type'] == 'subscribe':
        return f"感谢{msg['uname']}关注"
    elif msg['type'] == 'welcome':
        return f"欢迎{msg['uname']}进入直播间"

async def ttsTask():
    init()
    loop = asyncio.get_running_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        while True:
            msg = popMessagesQueue()
            if msg == None:
                await asyncio.sleep(0.1)
                continue
            appendDelay(time.time() - msg['time'])
            text = messagesToText(msg)
            await loop.run_in_executor(pool, tts, text)
