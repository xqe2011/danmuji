import asyncio
from .live import connectLive
from .logger import timeLog
from .messages_handler import *
from .http import startHttpServer, broadcastWSMessage
from .stats import statsTask, statsEvent
from .tts import ttsTask
from .remote import initRemote, remoteWSBroadcast

@statsEvent.on('stats')
async def statsHandler(stats):
    await broadcastWSMessage(stats)
    await remoteWSBroadcast(stats)

async def main():
    timeLog('[Main] Started')
    await connectLive()

try:
    startHttpServer([
        statsTask,
        ttsTask,
        initRemote,
        main
    ])
except KeyboardInterrupt:
    pass
except asyncio.CancelledError:
    pass
except SystemExit:
    pass