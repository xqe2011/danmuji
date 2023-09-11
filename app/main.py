import asyncio, os
from .live import initalizeLive, liveEvent
from .logger import timeLog
from .messages_handler import *
from .http import startHttpServer, broadcastWSMessage
from .stats import statsTask, statsEvent
from .remote import initRemote, remoteWSBroadcast
from .keyboard import initalizeKeyboard
from .config import configEvent
# only load tts in windows
if os.name == 'nt':
    from .tts import ttsTask, ttsSystem

@statsEvent.on('stats')
async def statsHandler(stats):
    await broadcastWSMessage({ 'type': 'stats', 'data': stats })
    await remoteWSBroadcast({ 'type': 'stats', 'data': stats })

@configEvent.on('update')
async def configHandler(oldConfig, newConfig):
    await broadcastWSMessage({ 'type': 'config', 'data': newConfig['dynamic'] })
    await remoteWSBroadcast({ 'type': 'config', 'data': newConfig['dynamic'] })

@liveEvent.on('connected')
async def liveConnectedHandler():
    await ttsSystem("B站直播间已连接")

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
