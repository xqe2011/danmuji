import asyncio
import os
import platform
import traceback

from .logger import timeLog
from .messages_handler import markAllMessagesInvalid
from .config import getJsonConfig, updateJsonConfig
from .tts import getAllSpeakers, getNowSpeaker, readHistoryByType, resetHistoryIndex, ttsSystem
from .stats import getDelay
from .live import setDisableWebProtocol

macHotkeyListener = None

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
    if len(allSpeakers) == 0:
        await ttsSystem('未找到可切换的TTS音频通道')
        return
    nowSpeaker = getNowSpeaker()
    nowIndex = allSpeakers.index(nowSpeaker) if nowSpeaker in allSpeakers else -1
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

async def handleDisableWebProtocol():
    timeLog('[Keyboard] Trigging disable web protocol')
    await setDisableWebProtocol()
    await ttsSystem('已强制使用开放平台建立连接')


def _log_hotkey_error(future):
    try:
        future.result()
    except Exception:
        traceback.print_exc()


def _schedule_hotkey(runningLoop, handler):
    future = asyncio.run_coroutine_threadsafe(handler(), runningLoop)
    future.add_done_callback(_log_hotkey_error)


def _initialize_windows_keyboard(runningLoop):
    import keyboard

    keyboard.add_hotkey('ctrl+alt+f5', lambda: _schedule_hotkey(runningLoop, handleFlush))
    keyboard.add_hotkey('alt+f6', lambda: _schedule_hotkey(runningLoop, handleGetDelay))

    keyboard.add_hotkey('ctrl+alt+[', lambda: _schedule_hotkey(runningLoop, handleTTSRatePlus))
    keyboard.add_hotkey('ctrl+alt+]', lambda: _schedule_hotkey(runningLoop, handleTTSRateMinus))

    keyboard.add_hotkey('ctrl+alt+=', lambda: _schedule_hotkey(runningLoop, handleTTSVolumePlus))
    keyboard.add_hotkey('ctrl+alt+-', lambda: _schedule_hotkey(runningLoop, handleTTSVolumeMinus))

    keyboard.add_hotkey('ctrl+alt+m', lambda: _schedule_hotkey(runningLoop, handleTTSVoicePlus))

    keyboard.add_hotkey('alt+f7', lambda: _schedule_hotkey(runningLoop, handleReadNextGiftMessages))
    keyboard.add_hotkey('alt+f8', lambda: _schedule_hotkey(runningLoop, handleReadNextHistoryDanmu))
    keyboard.add_hotkey('alt+t', lambda: _schedule_hotkey(runningLoop, handleReadLastGiftMessages))
    keyboard.add_hotkey('alt+y', lambda: _schedule_hotkey(runningLoop, handleReadLastHistoryDanmu))
    keyboard.add_hotkey('alt+f9', lambda: _schedule_hotkey(runningLoop, handleReadNewestMessages))

    keyboard.add_hotkey('ctrl+alt+f8', lambda: _schedule_hotkey(runningLoop, handleDisableWebProtocol))
    timeLog('[Keyboard] Windows hotkeys initialized')


def _initialize_macos_keyboard(runningLoop):
    global macHotkeyListener

    try:
        from pynput import keyboard as pynput_keyboard
    except ImportError as e:
        timeLog(f'[Keyboard] Failed to initialize macOS hotkeys: {e}')
        return

    if hasattr(pynput_keyboard.Listener, 'IS_TRUSTED') and not pynput_keyboard.Listener.IS_TRUSTED:
        timeLog('[Keyboard] macOS hotkeys need Accessibility/Input Monitoring permission for this app or terminal')

    hotkeys = {
        '<ctrl>+<alt>+<f5>': lambda: _schedule_hotkey(runningLoop, handleFlush),
        '<alt>+<f6>': lambda: _schedule_hotkey(runningLoop, handleGetDelay),

        '<ctrl>+<alt>+[': lambda: _schedule_hotkey(runningLoop, handleTTSRatePlus),
        '<ctrl>+<alt>+]': lambda: _schedule_hotkey(runningLoop, handleTTSRateMinus),

        '<ctrl>+<alt>+=': lambda: _schedule_hotkey(runningLoop, handleTTSVolumePlus),
        '<ctrl>+<alt>+-': lambda: _schedule_hotkey(runningLoop, handleTTSVolumeMinus),

        '<ctrl>+<alt>+m': lambda: _schedule_hotkey(runningLoop, handleTTSVoicePlus),

        '<alt>+<f7>': lambda: _schedule_hotkey(runningLoop, handleReadNextGiftMessages),
        '<alt>+<f8>': lambda: _schedule_hotkey(runningLoop, handleReadNextHistoryDanmu),
        '<alt>+t': lambda: _schedule_hotkey(runningLoop, handleReadLastGiftMessages),
        '<alt>+y': lambda: _schedule_hotkey(runningLoop, handleReadLastHistoryDanmu),
        '<alt>+<f9>': lambda: _schedule_hotkey(runningLoop, handleReadNewestMessages),

        '<ctrl>+<alt>+<f8>': lambda: _schedule_hotkey(runningLoop, handleDisableWebProtocol),
    }

    try:
        macHotkeyListener = pynput_keyboard.GlobalHotKeys(hotkeys)
        macHotkeyListener.start()
        timeLog('[Keyboard] macOS Ctrl/Alt hotkeys initialized')
    except Exception:
        traceback.print_exc()
        timeLog('[Keyboard] Failed to initialize macOS hotkeys')


async def initalizeKeyboard():
    runningLoop = asyncio.get_running_loop()
    if os.name == "nt":
        _initialize_windows_keyboard(runningLoop)
    elif platform.system() == 'Darwin':
        _initialize_macos_keyboard(runningLoop)
