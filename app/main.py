import asyncio, os
from .live import initalizeLive
from .logger import timeLog
from .messages_handler import *
from .http import startHttpServer, broadcastWSMessage
from .stats import statsTask, statsEvent
from .remote import initRemote, remoteWSBroadcast
# only load tts in windows
if os.name == 'nt':
    from .tts import ttsTask

@statsEvent.on('stats')
async def statsHandler(stats):
    await broadcastWSMessage(stats)
    await remoteWSBroadcast(stats)

def main():
    timeLog('[Main] Started')
    try:
        tasks = [statsTask, initRemote, initalizeLive]
        if os.name == 'nt':
            tasks.append(ttsTask)
        startHttpServer(tasks)
    except KeyboardInterrupt:
        pass
    except asyncio.CancelledError:
        pass
    except SystemExit:
        pass
