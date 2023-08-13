import asyncio, os
from .live import initalizeLive
from .logger import timeLog
from .messages_handler import *
from .http import startHttpServer, broadcastWSMessage
from .stats import statsTask, statsEvent
from .remote import initRemote, remoteWSBroadcast
from .keyboard import initalizeKeyboard
from .config import configEvent
from .deep_learning import initalizeDeepLearning
# only load tts in windows
if os.name == 'nt':
    from .tts import ttsTask

@statsEvent.on('stats')
async def statsHandler(stats):
    await broadcastWSMessage({ 'type': 'stats', 'data': stats })
    await remoteWSBroadcast({ 'type': 'stats', 'data': stats })

@configEvent.on('update')
async def configHandler(oldConfig, newConfig):
    await broadcastWSMessage({ 'type': 'config', 'data': newConfig['dynamic'] })
    await remoteWSBroadcast({ 'type': 'config', 'data': newConfig['dynamic'] })

def main():
    timeLog('[Main] Started')
    try:
        tasks = [statsTask, initRemote, initalizeKeyboard, initalizeDeepLearning, initalizeLive]
        if os.name == 'nt':
            tasks.append(ttsTask)
        startHttpServer(tasks)
    except KeyboardInterrupt:
        pass
    except asyncio.CancelledError:
        pass
    except SystemExit:
        pass
