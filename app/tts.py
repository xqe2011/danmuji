import asyncio, time
from .messages_handler import popMessagesQueue
from .stats import appendDelay
import pyttsx3
import concurrent.futures
import functools

ttsEngine = None

def tts_init():
    global ttsEngine
    ttsEngine = pyttsx3.init()  # object creation
    ttsEngine.setProperty('volume', 1.0)    # setting up volume level  between 0 and 1
    voices = ttsEngine.getProperty('voices')       #getting details of current voice
    for voice in voices:
        print(voice.id)
        print(voice.name)
    ttsEngine.setProperty('voice', voices[0].id)   #changing index, changes voices. 1 for female
    ttsEngine.setProperty('rate', 1000)     # setting up new voice rate
    ttsEngine.say("tts 初始化成功")
    ttsEngine.runAndWait()


def tts(text):
    global ttsEngine
    if ttsEngine == None:
        tts_init()
    ttsEngine.say(text)
    ttsEngine.runAndWait()

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
    loop = asyncio.get_running_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        await loop.run_in_executor(pool, tts_init)

        while True:
            msg = popMessagesQueue()
            if msg == None:
                await asyncio.sleep(0.1)
                continue
            appendDelay(time.time() - msg['time'])
            text = messagesToText(msg)
            await loop.run_in_executor(pool, functools.partial(tts, text))

if __name__ == '__main__':
    pass
