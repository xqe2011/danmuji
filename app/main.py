import asyncio
from .live import connectLive
from .logger import timeLog
from .messages_handler import *
from .http import startHttpServer, broadcastWSMessage
from .stats import statsTask, statsEvent

@statsEvent.on('stats')
async def statsHandler(stats):
    await broadcastWSMessage(stats)

async def main():
    timeLog('[Main] Started')
    await connectLive()

try:
    startHttpServer([
        statsTask,
        main
    ])
except KeyboardInterrupt:
    pass
except asyncio.CancelledError:
    pass
except SystemExit:
    pass