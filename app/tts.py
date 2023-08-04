import asyncio, time
from .messages_handler import popMessagesQueue
from .stats import appendDelay

async def tts(text):
    # 模拟tts发音延迟
    await asyncio.sleep(len(text) * 0.1)

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
    while True:
        msg = popMessagesQueue()
        if msg == None:
            await asyncio.sleep(0.1)
            continue
        appendDelay(time.time() - msg['time'])
        text = messagesToText(msg)
        await tts(text)
