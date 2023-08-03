import asyncio
from pyee import EventEmitter
from .logger import timeLog

statsEvent = EventEmitter()
registeredStatsCount = []
lastDurationStats = None
messagesQueue = []

async def resetDuration():
    global lastDurationStats, registeredStatsCount
    lastDurationStats = {}
    for type in registeredStatsCount:
        lastDurationStats["raw" + type[0].upper() + type[1:]] = 0
        lastDurationStats["filtered" + type[0].upper() + type[1:]] = 0

def statsFunctionGenerator(type):
    global registeredStatsCount
    registeredStatsCount.append(type)
    async def statsFunction(filterd, **args):
        global lastDurationStats, messagesQueue
        lastDurationStats["raw" + type[0].upper() + type[1:]] += 1
        if filterd:
            lastDurationStats["filtered" + type[0].upper() + type[1:]] += 1
            messagesQueue.append({
                'type': type,
                'filterd': filterd,
                **args
            })
    return statsFunction

appendDanmuFilteredStats = statsFunctionGenerator('danmu')
appendGiftFilteredStats = statsFunctionGenerator('gift')
appendWelcomeFilteredStats = statsFunctionGenerator('welcome')
appendLikeFilteredStats = statsFunctionGenerator('like')
appendGuardBuyFilteredStats = statsFunctionGenerator('guardBuy')
appendSubscribeFilteredStats = statsFunctionGenerator('subscribe')

async def statsTask():
    await resetDuration()
    while True:
        await asyncio.sleep(10)
        statsEvent.emit('stats', lastDurationStats)
        timeLog(f'[Stats] {lastDurationStats}')
        await resetDuration()