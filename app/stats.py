import asyncio
from pyee import AsyncIOEventEmitter
from .logger import timeLog
from psutil import cpu_percent

statsEvent = AsyncIOEventEmitter()
registeredStatsCount = []
lastDurationStats = None
messagesQueue = []
delaysQueue = []

def resetDuration():
    global lastDurationStats, registeredStatsCount, messagesQueue, delaysQueue
    messagesQueue = []
    delaysQueue = []
    lastDurationStats = {
        'cpuUsage': 0,
        'messagesQueueLength': lastDurationStats['messagesQueueLength'] if lastDurationStats else 0,
        'delay': 0
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
appendSuperChatFilteredStats = statsFunctionGenerator('superChat')

def getDelay():
    global delaysQueue
    return sum(delaysQueue) / len(delaysQueue) if len(delaysQueue) > 0 else 0

def appendDelay(delay):
    global delaysQueue
    delaysQueue.append(delay)

def setOutputMessagesLength(messagesQueueLength):
    global lastDurationStats
    lastDurationStats['messagesQueueLength'] = messagesQueueLength

resetDuration()

async def statsTask():
    resetDuration()
    cpu_percent(interval=None)
    while True:
        await asyncio.sleep(5)
        lastDurationStats['cpuUsage'] = cpu_percent(interval=None)
        lastDurationStats['delay'] = getDelay()
        statsEvent.emit('stats', {
            'events': messagesQueue,
            'stats': lastDurationStats
        })
        timeLog(f'[Stats] {lastDurationStats}')
        resetDuration()