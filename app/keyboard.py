import keyboard, asyncio
from .logger import timeLog
from .messages_handler import markAllMessagesInvalid
import os, time
from .config import getJsonConfig, updateJsonConfig
from .tts import getAllSpeakers, getNowSpeaker, setReadLastMessagesMode, readLastMessagesAndIncreaseIndex, ttsSystem
from .stats import getDelay

async def handleFlush():
    timeLog('[Keyboard] Trigging flush')
    await setReadLastMessagesMode(False)
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

async def handleEnableReadLastMessages():
    timeLog('[Keyboard] Trigging enabe read last messages')
    await setReadLastMessagesMode(True)
    await readLastMessagesAndIncreaseIndex()

async def handleDisableReadLastMessages():
    timeLog('[Keyboard] Trigging disable read last messages')
    await setReadLastMessagesMode(False)

async def initalizeKeyboard():
    runningLoop = asyncio.get_running_loop()
    if os.name == "nt":
        keyboard.add_hotkey('ctrl+alt+f1', lambda: asyncio.run_coroutine_threadsafe(handleFlush(), runningLoop))
        keyboard.add_hotkey('alt+f1', lambda: asyncio.run_coroutine_threadsafe(handleGetDelay(), runningLoop))

        keyboard.add_hotkey('ctrl+alt+l', lambda: asyncio.run_coroutine_threadsafe(handleTTSRatePlus(), runningLoop))
        keyboard.add_hotkey('ctrl+alt+k', lambda: asyncio.run_coroutine_threadsafe(handleTTSRateMinus(), runningLoop))

        keyboard.add_hotkey('ctrl+alt+p', lambda: asyncio.run_coroutine_threadsafe(handleTTSVolumePlus(), runningLoop))
        keyboard.add_hotkey('ctrl+alt+o', lambda: asyncio.run_coroutine_threadsafe(handleTTSVolumeMinus(), runningLoop))

        keyboard.add_hotkey('ctrl+alt+m', lambda: asyncio.run_coroutine_threadsafe(handleTTSVoicePlus(), runningLoop))

        keyboard.add_hotkey('ctrl+alt+f11', lambda: asyncio.run_coroutine_threadsafe(handleDisableReadLastMessages(), runningLoop))
        keyboard.add_hotkey('ctrl+alt+f12', lambda: asyncio.run_coroutine_threadsafe(handleEnableReadLastMessages(), runningLoop))
        