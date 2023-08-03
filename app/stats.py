import asyncio
from pyee import AsyncIOEventEmitter
from .logger import timeLog

statsEvent = AsyncIOEventEmitter()
registeredStatsCount = []
lastDurationStats = None
messagesQueue = []

def resetDuration():
    global lastDurationStats, registeredStatsCount, messagesQueue
    messagesQueue = []
    lastDurationStats = {
        'cpu_usage': 50,
        'messagesQueueLength': lastDurationStats['messagesQueueLength'] if lastDurationStats else 0
    }
    for type in registeredStatsCount:
        lastDurationStats["raw" + type[0].upper() + type[1:]] = 0
        lastDurationStats["filtered" + type[0].upper() + type[1:]] = 0

def statsFunctionGenerator(type):
    global registeredStatsCount
    registeredStatsCount.append(type)
    def statsFunction(filterd, **args):
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

def setOutputMessagesLength(messagesQueueLength):
    global lastDurationStats
    lastDurationStats['messagesQueueLength'] = messagesQueueLength

resetDuration()

async def statsTask():
    resetDuration()
    while True:
        await asyncio.sleep(1)
        statsEvent.emit('stats', {
            'events': messagesQueue,
            'stats': lastDurationStats
        })
        timeLog(f'[Stats] {lastDurationStats}')
        resetDuration()