import asyncio, time, re

from .messages_handler import popMessagesQueue
from .stats import appendDelay
from .config import getJsonConfig
from .logger import timeLog
import winsdk.windows.media.speechsynthesis as speechsynthesis
import winsdk.windows.media.playback as playback

lastRate = None
lastVolume = None
synthesizer = None
media_player = None


def syncWithConfig():
    global ttsEngine, lastRate, lastVolume
    ttsConfig = getJsonConfig()['dynamic']['tts']
    if lastVolume != ttsConfig['volume']:
        lastVolume = ttsConfig['volume']
        synthesizer.options.audio_volume = lastVolume / 100.0
    if lastRate != ttsConfig['rate']:
        lastRate = ttsConfig['rate']
        # This value can range from 0.5 (half the default rate) to 6.0 (6x the default rate), inclusive.
        # The default value is 1.0 (the "normal" speaking rate for the current voice).
        synthesizer.options.speaking_rate = 0.5 + (lastRate / 100.0) * 5.5

async def init():
    global synthesizer, media_player
    synthesizer = speechsynthesis.SpeechSynthesizer()
    media_player = playback.MediaPlayer()

    voices = speechsynthesis.SpeechSynthesizer.all_voices
    dynamicConfig = getJsonConfig()['dynamic']['tts']
    targetVoice = None
    for index, voice in enumerate(voices):
        if dynamicConfig['voice'] in voice.display_name:
            targetVoice = voice
            break

    if targetVoice != None:
        timeLog(f'[TTS] Use voice: {targetVoice.display_name} ({targetVoice.language})"')
        synthesizer.voice = targetVoice
    else:
        voice = synthesizer.voice
        timeLog(f'[TTS] Use default voice: {voice.display_name} ({voice.language})"')

    syncWithConfig()
    await tts("TTS模块初始化成功")


async def tts(text):
    syncWithConfig()
    global synthesizer, media_player
    ttsConfig = getJsonConfig()['dynamic']['tts']

    # 支持日语
    if ttsConfig['japanese']['enable']:
        text = re.sub(r'[\u3040-\u309F\u30A0-\u30FF]+', r'<lang langid="411">\g<0></lang>', text)
    ssml = '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="zh-CN"><voice xml:lang="zh-CN">'\
           + text + '</voice></speak>'
    # Synthesize text to a stream
    stream = await synthesizer.synthesize_ssml_to_stream_async(ssml)
    # stream = await synthesizer.synthesize_text_to_stream_async(text)

    media_player.set_stream_source(stream)
    media_player.play()
    sound_seconds = stream.size / (32.0 * 1024)  # 32 KB/s
    await asyncio.sleep(sound_seconds)


def messagesToText(msg):
    if msg['type'] == 'danmu':
        return f"{msg['uname']}说{msg['msg']}"
    elif msg['type'] == 'gift':
        return f"感谢{msg['uname']}送出的{msg['num']}个{msg['giftName']}"
    elif msg['type'] == 'guardBuy':
        return f"感谢{msg['uname']}购买{msg['num']}个月的{msg['giftName']}"
    elif msg['type'] == 'like':
        return f"感谢{msg['uname']}点赞"
    elif msg['type'] == 'superChat':
        return f"感谢{msg['uname']}的{msg['price']}元的醒目留言{msg['msg']}"
    elif msg['type'] == 'subscribe':
        return f"感谢{msg['uname']}关注"
    elif msg['type'] == 'welcome':
        return f"欢迎{msg['uname']}进入直播间"

async def ttsTask():
    await init()
    while True:
        msg = popMessagesQueue()
        if msg == None:
            await asyncio.sleep(0.1)
            continue
        appendDelay(time.time() - msg['time'])
        text = messagesToText(msg)
        await tts(text)
