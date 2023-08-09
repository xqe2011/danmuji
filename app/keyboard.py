import keyboard, asyncio
from .logger import timeLog
from .messages_handler import markAllMessagesInvalid

async def handleFlush():
    timeLog('[Keyboard] Trigging flush')
    await markAllMessagesInvalid()

async def initalizeKeyboard():
    runningLoop = asyncio.get_running_loop()
    keyboard.add_hotkey('ctrl+alt+shift+q', lambda: asyncio.run_coroutine_threadsafe(handleFlush(), runningLoop))