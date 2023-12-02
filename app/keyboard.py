import keyboard, asyncio
from .logger import timeLog
from .messages_handler import markAllMessagesInvalid
import os, time
from .config import getJsonConfig, updateJsonConfig
from .tts import getAllSpeakers, getNowSpeaker, readHistoryByType, resetHistoryIndex, ttsSystem
from .stats import getDelay

async def handleFlush():
    timeLog('[Keyboard] Trigging flush')
    await markAllMessagesInvalid()

async def handleTTSRatePlus():
    timeLog('[Keyboard] Trigging TTS rate plus')
    nowJsonConfig = getJsonConfig()
    nowJsonConfig['dynamic']['tts']['rate'] += 1
    nowJsonConfig['dynamic']['tts']['rate'] = max(nowJsonConfig['dynamic']['tts']['rate'], 1)
    nowJsonConfig['dynamic']['tts']['rate'] = min(nowJsonConfig['dynamic']['tts']['rate'], 100)
    await updateJsonConfig(nowJsonConfig)
    await ttsSystem('TTS语速增加到' + str(nowJsonConfig['dynamic']['tts']['rate']))

async def handleTTSRateMinus():
    timeLog('[Keyboard] Trigging TTS rate minus')
    nowJsonConfig = getJsonConfig()
    nowJsonConfig['dynamic']['tts']['rate'] -= 1
    nowJsonConfig['dynamic']['tts']['rate'] = max(nowJsonConfig['dynamic']['tts']['rate'], 1)
    nowJsonConfig['dynamic']['tts']['rate'] = min(nowJsonConfig['dynamic']['tts']['rate'], 100)
    await updateJsonConfig(nowJsonConfig)
    await ttsSystem('TTS语速减少到' + str(nowJsonConfig['dynamic']['tts']['rate']))

async def handleTTSVolumePlus():
    timeLog('[Keyboard] Trigging TTS volume plus')
    nowJsonConfig = getJsonConfig()
    nowJsonConfig['dynamic']['tts']['volume'] += 1
    nowJsonConfig['dynamic']['tts']['volume'] = max(nowJsonConfig['dynamic']['tts']['volume'], 1)
    nowJsonConfig['dynamic']['tts']['volume'] = min(nowJsonConfig['dynamic']['tts']['volume'], 100)
    await updateJsonConfig(nowJsonConfig)
    await ttsSystem('TTS音量增加到' + str(nowJsonConfig['dynamic']['tts']['volume']))

async def handleTTSVolumeMinus():
    timeLog('[Keyboard] Trigging TTS volume minus')
    nowJsonConfig = getJsonConfig()
    nowJsonConfig['dynamic']['tts']['volume'] -= 1
    nowJsonConfig['dynamic']['tts']['volume'] = max(nowJsonConfig['dynamic']['tts']['volume'], 1)
    nowJsonConfig['dynamic']['tts']['volume'] = min(nowJsonConfig['dynamic']['tts']['volume'], 100)
    await updateJsonConfig(nowJsonConfig)
    await ttsSystem('TTS音量减少到' + str(nowJsonConfig['dynamic']['tts']['volume']))

async def handleTTSVoicePlus():
    timeLog('[Keyboard] Trigging TTS voice plus')
    nowJsonConfig = getJsonConfig()
    allSpeakers = getAllSpeakers()
    nowIndex = allSpeakers.index(getNowSpeaker())
    nowIndex += 1
    nowIndex %= len(allSpeakers)
    nowJsonConfig['dynamic']['tts']['speaker'] = allSpeakers[nowIndex]
    await updateJsonConfig(nowJsonConfig)
    await ttsSystem('TTS音频通道切换为' + allSpeakers[nowIndex])

async def handleGetDelay():
    timeLog('[Keyboard] Trigging get delay')
    await ttsSystem('当前延迟为%.1f秒' % getDelay())

async def handleReadNewestMessages():
    timeLog('[Keyboard] Trigging read newest messages')
    await resetHistoryIndex()

async def handleReadNextHistoryDanmu():
    timeLog('[Keyboard] Trigging read next history danmu')
    await readHistoryByType(['danmu'])

async def handleReadNextGiftMessages():
    timeLog('[Keyboard] Trigging read next history gift')
    await readHistoryByType(['gift', 'guardBuy', 'superChat'])

async def handleReadLastHistoryDanmu():
    timeLog('[Keyboard] Trigging read last history danmu')
    await readHistoryByType(['danmu'], True)

async def handleReadLastGiftMessages():
    timeLog('[Keyboard] Trigging read last history gift')
    await readHistoryByType(['gift', 'guardBuy', 'superChat'], True)

async def initalizeKeyboard():
    runningLoop = asyncio.get_running_loop()
    if os.name == "nt":
        keyboard.add_hotkey('ctrl+alt+f5', lambda: asyncio.run_coroutine_threadsafe(handleFlush(), runningLoop))
        keyboard.add_hotkey('alt+f6', lambda: asyncio.run_coroutine_threadsafe(handleGetDelay(), runningLoop))

        keyboard.add_hotkey('ctrl+alt+[', lambda: asyncio.run_coroutine_threadsafe(handleTTSRatePlus(), runningLoop))
        keyboard.add_hotkey('ctrl+alt+]', lambda: asyncio.run_coroutine_threadsafe(handleTTSRateMinus(), runningLoop))

        keyboard.add_hotkey('ctrl+alt+=', lambda: asyncio.run_coroutine_threadsafe(handleTTSVolumePlus(), runningLoop))
        keyboard.add_hotkey('ctrl+alt+-', lambda: asyncio.run_coroutine_threadsafe(handleTTSVolumeMinus(), runningLoop))

        keyboard.add_hotkey('ctrl+alt+m', lambda: asyncio.run_coroutine_threadsafe(handleTTSVoicePlus(), runningLoop))

        keyboard.add_hotkey('alt+f7', lambda: asyncio.run_coroutine_threadsafe(handleReadNextGiftMessages(), runningLoop))
        keyboard.add_hotkey('alt+f8', lambda: asyncio.run_coroutine_threadsafe(handleReadNextHistoryDanmu(), runningLoop))
        keyboard.add_hotkey('alt+t', lambda: asyncio.run_coroutine_threadsafe(handleReadLastGiftMessages(), runningLoop))
        keyboard.add_hotkey('alt+y', lambda: asyncio.run_coroutine_threadsafe(handleReadLastHistoryDanmu(), runningLoop))
        keyboard.add_hotkey('alt+f9', lambda: asyncio.run_coroutine_threadsafe(handleReadNewestMessages(), runningLoop))
        
        