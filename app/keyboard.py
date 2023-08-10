import keyboard, asyncio
from .logger import timeLog
from .messages_handler import markAllMessagesInvalid
import os

async def handleFlush():
    timeLog('[Keyboard] Trigging flush')
    await markAllMessagesInvalid()

async def initalizeKeyboard():
    runningLoop = asyncio.get_running_loop()
    if os.name == "nt":
        keyboard.add_hotkey('ctrl+alt+shift+q', lambda: asyncio.run_coroutine_threadsafe(handleFlush(), runningLoop))