import asyncio, time, re
import pygame._sdl2.audio as sdl2_audio
from .messages_handler import popMessagesQueue, getHaveReadMessages, messagesQueueSystemAppend
from .stats import appendDelay
from .config import getJsonConfig, updateJsonConfig
from .logger import timeLog
import winsdk.windows.media.speechsynthesis as speechsynthesis
import winsdk.windows.storage.streams as streams
import pygame
import io

lastRate = None
lastVolume = None
lastVoice = None
lastSpeaker = None
nowSpeaker = None
synthesizer = None
allVoices = []
allSpeakers = []
prepareReadLastMessagesMode = False
readLastMessagesMode = False
readLastMessagesIndex = 0

def getAllVoices():
    global allVoices
    return [ { 'name': voice.display_name, 'language': voice.language } for voice in list(allVoices)]

def getAllSpeakers():
    global allSpeakers
    return allSpeakers

async def init():
    global synthesizer, allVoices, allSpeakers
    pygame.mixer.init()
    allSpeakers = sdl2_audio.get_audio_device_names(False)
    for name in list(allSpeakers):
        timeLog(f'[TTS] Found speaker: {name}')

    synthesizer = speechsynthesis.SpeechSynthesizer()
    allVoices = speechsynthesis.SpeechSynthesizer.all_voices
    for voice in list(allVoices):
        timeLog(f'[TTS] Found voice: {voice.display_name} ({voice.language})"')

    await tts("TTS模块初始化成功")

def syncWithConfig():
    global lastRate, lastVolume, lastVoice, lastSpeaker
    ttsConfig = getJsonConfig()['dynamic']['tts']
    if lastVolume != ttsConfig['volume']:
        lastVolume = ttsConfig['volume']
        synthesizer.options.audio_volume = lastVolume / 100.0
    if lastRate != ttsConfig['rate']:
        lastRate = ttsConfig['rate']
        # This value can range from 0.5 (half the default rate) to 6.0 (6x the default rate), inclusive.
        # The default value is 1.0 (the "normal" speaking rate for the current voice).
        synthesizer.options.speaking_rate = 0.5 + (lastRate / 100.0) * 5.5
    if lastVoice != ttsConfig['voice']:
        lastVoice = ttsConfig['voice']
        targetVoice = None
        for voice in list(allVoices):
            if ttsConfig['voice'] in voice.display_name:
                targetVoice = voice
                break
        if targetVoice != None:
            timeLog(f'[TTS] Use voice: {targetVoice.display_name} ({targetVoice.language})"')
            synthesizer.voice = targetVoice
        else:
            voice = synthesizer.voice
            timeLog(f'[TTS] Use default voice: {voice.display_name} ({voice.language})"')
    if lastSpeaker != ttsConfig['speaker']:
        lastSpeaker = ttsConfig['speaker']
        global nowSpeaker
        for speaker in list(allSpeakers):
            if ttsConfig['speaker'] in speaker:
                nowSpeaker = speaker
                break
        if nowSpeaker != None:
            timeLog(f'[TTS] Use speaker: {nowSpeaker}"')
        else:
            nowSpeaker = allSpeakers[0]
            timeLog(f'[TTS] Use default speaker: {nowSpeaker}"')
        pygame.mixer.quit()
        pygame.mixer.init(devicename=nowSpeaker)

def getNowSpeaker():
    global nowSpeaker
    return nowSpeaker

def calculateTags(lang, config, text):
    tagsXml = '<voice name="{}" xml:lang="{}"><prosody rate="{}" volume="{}">{}</prosody></voice>'
    return tagsXml.format(config["voice"], lang, 0.5 + (config["rate"] / 100.0) * 2.5, config["volume"], text)

async def tts(text):
    global synthesizer, media_player
    syncWithConfig()

    ttsConfig = getJsonConfig()['dynamic']['tts']
    # 支持日语
    if ttsConfig['japanese']['enable']:
        text = re.sub(r'[\u3040-\u309F\u30A0-\u30FF]+', calculateTags("ja-JP", ttsConfig['japanese'], '\g<0>'), text)
    
    ssml = f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="zh-CN"><voice xml:lang="zh-CN">{text}</voice></speak>'
    # Synthesize text to a stream
    stream = await synthesizer.synthesize_ssml_to_stream_async(ssml)

    temp_buffer = bytes(0)
    data_reader = streams.DataReader(stream)
    await data_reader.load_async(stream.size)
    while data_reader.unconsumed_buffer_length > 0:
        temp_buffer += bytes(data_reader.read_buffer(data_reader.unconsumed_buffer_length)) + b'\x00\x00\x00\x00\x00\x00\x00\x00'

    byte_stream = io.BytesIO(temp_buffer)

    pygame.mixer.music.load(byte_stream)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        await asyncio.sleep(0.05)



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
    elif msg['type'] == 'system':
        return f"系统提示{msg['msg']}"

async def ttsTask():
    global prepareReadLastMessagesMode, readLastMessagesMode
    await init()
    while True:
        if prepareReadLastMessagesMode:
            readLastMessagesMode = True
            await asyncio.sleep(0.1)
            continue
        else:
            readLastMessagesMode = False
        msg = popMessagesQueue()
        if msg == None:
            await asyncio.sleep(0.1)
            continue
        appendDelay(time.time() - msg['time'])
        text = messagesToText(msg)
        await tts(text)

async def setReadLastMessagesMode(mode):
    global prepareReadLastMessagesMode, readLastMessagesIndex, readLastMessagesMode
    if prepareReadLastMessagesMode == False and mode == True:
        prepareReadLastMessagesMode = mode
        while not readLastMessagesMode:
            await asyncio.sleep(0.1)
        readLastMessagesIndex = -1
        await tts(messagesToText({'type': 'system', 'msg': '已进入历史消息阅读模式'}))
    elif prepareReadLastMessagesMode == True and mode == False:
        messagesQueueSystemAppend('已退出历史消息阅读模式')
        prepareReadLastMessagesMode = mode
        while readLastMessagesMode:
            await asyncio.sleep(0.1)

async def readLastMessagesAndIncreaseIndex():
    global readLastMessagesIndex
    readLastMessagesIndex += 1
    if readLastMessagesIndex == len(getHaveReadMessages()):
        readLastMessagesIndex = -1
        await tts(messagesToText({'type': 'system', 'msg': '已到达最后一条,继续翻页将从第一条开始'}))
        return
    await tts(messagesToText(getHaveReadMessages()[readLastMessagesIndex]))