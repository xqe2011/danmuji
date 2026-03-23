import asyncio, os, time
from .live import initalizeLive, liveEvent
from .logger import timeLog
from .messages_handler import *
from .http import startHttpServer, broadcastWSMessage
from .stats import statsTask, statsEvent, getMessagesLength
from .remote import initRemote, remoteWSBroadcast
from .keyboard import initalizeKeyboard
from .config import configEvent, getJsonConfig
# only load tts in windows
if os.name == 'nt':
    from .tts import ttsTask

lastAlertTime = 0
@statsEvent.on('stats')
async def statsHandler(stats):
    await broadcastWSMessage({ 'type': 'stats', 'data': stats })
    await remoteWSBroadcast({ 'type': 'stats', 'data': stats })
    # 消息队列较长自动播报
    global lastAlertTime
    config = getJsonConfig()["dynamic"]["system"]["alertWhenMessagesQueueLonger"]
    if config["enable"]:
        if time.time() - lastAlertTime > config["interval"] and getMessagesLength() > config["threshold"]:
            # 为了保证统一出来的延迟一致，通过这个保证计算出来的延迟一样
            messagesQueueAppendAtStart({ 'type': 'system', 'time': time.time() - stats['stats']['delay'], 'msg': '当前延迟较高为%d秒 积压弹幕数为%d' % (stats['stats']['delay'], stats['stats']['messagesQueueLength']) })
            lastAlertTime = time.time()
    else:
        lastAlertTime = 0


@configEvent.on('update')
async def configHandler(oldConfig, newConfig):
    await broadcastWSMessage({ 'type': 'config', 'data': newConfig['dynamic'] })
    await remoteWSBroadcast({ 'type': 'config', 'data': newConfig['dynamic'] })

def main():
    timeLog('[Main] Started')
    try:
        tasks = [statsTask, initRemote, initalizeKeyboard, initalizeLive]
        if os.name == 'nt':
            tasks.append(ttsTask)
        startHttpServer(tasks)
    except KeyboardInterrupt:
        pass
    except asyncio.CancelledError:
        pass
    except SystemExit:
        pass
