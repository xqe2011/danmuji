import asyncio, time, re, traceback
import pygame._sdl2.audio as sdl2_audio
from .messages_handler import popMessagesQueue, getHaveReadMessages
from .stats import appendDelay
from .config import getJsonConfig
from .logger import timeLog
import winsdk.windows.media.speechsynthesis as speechsynthesis
import winsdk.windows.storage.streams as streams
import pygame
import io

channels = [{"lastRate": None, "lastVolume": None, "lastVoice": None, "synthesizer": speechsynthesis.SpeechSynthesizer()}] * 2
lastSpeaker = None
nowSpeaker = None
allVoices = []
allSpeakers = []
prepareDisableTTSTask = False
disableTTSTask = False
readHistoryIndex = None
initalized = False

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

    allVoices = speechsynthesis.SpeechSynthesizer.all_voices
    for voice in list(allVoices):
        timeLog(f'[TTS] Found voice: {voice.display_name} ({voice.language})"')

    await tts("TTS模块初始化成功")
    global initalized
    initalized = True

def syncSpeakerWithConfig():
    # 更新TTS音频通道
    global nowSpeaker, lastSpeaker
    ttsConfig = getJsonConfig()['dynamic']['tts']
    if lastSpeaker != ttsConfig['speaker']:
        lastSpeaker = ttsConfig['speaker']
        for speaker in list(allSpeakers):
            if ttsConfig['speaker'] in speaker:
                nowSpeaker = speaker
                break
        if nowSpeaker != None:
            timeLog(f'[TTS] Use speaker: {nowSpeaker}"')
        else:
            nowSpeaker = allSpeakers[0]
            timeLog(f'[TTS] Use default speaker: {nowSpeaker}"')
        for channel in range(len(channels)):
            pygame.mixer.Channel(channel).stop()
        pygame.mixer.quit()
        pygame.mixer.init(devicename=nowSpeaker)

def syncWithConfig(ttsConfig=None, channel=0):
    global channels, lastSpeaker
    if ttsConfig == None:
        ttsConfig = getJsonConfig()['dynamic']['tts']
    channelInfo = channels[channel]
    if channelInfo['lastVolume'] != ttsConfig['volume']:
        channelInfo['lastVolume'] = ttsConfig['volume']
        channelInfo['synthesizer'].options.audio_volume = channelInfo['lastVolume'] / 100.0
    if channelInfo['lastRate'] != ttsConfig['rate']:
        channelInfo['lastRate'] = ttsConfig['rate']
        # This value can range from 0.5 (half the default rate) to 6.0 (6x the default rate), inclusive.
        # The default value is 1.0 (the "normal" speaking rate for the current voice).
        channelInfo['synthesizer'].options.speaking_rate = 0.5 + (channelInfo['lastRate'] / 100.0) * 5.5
    if channelInfo['lastVoice'] != ttsConfig['voice']:
        channelInfo['lastVoice'] = ttsConfig['voice']
        targetVoice = None
        for voice in list(allVoices):
            if ttsConfig['voice'] in voice.display_name:
                targetVoice = voice
                break
        if targetVoice != None:
            timeLog(f'[TTS] Use voice: {targetVoice.display_name} ({targetVoice.language})"')
            channelInfo['synthesizer'].voice = targetVoice
        else:
            voice = channelInfo['synthesizer'].voice
            timeLog(f'[TTS] Use default voice: {voice.display_name} ({voice.language})"')

def getNowSpeaker():
    global nowSpeaker
    return nowSpeaker

def xmlEscape(text):
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

def calculateTags(lang, config, text):
    tagsXml = '<voice name="{}" xml:lang="{}"><prosody rate="{}" volume="{}">{}</prosody></voice>'
    return tagsXml.format(config["voice"], lang, 0.5 + (config["rate"] / 100.0) * 2.5, config["volume"], text)

async def tts(text, channel=0, config=None):
    global synthesizer, channels
    syncWithConfig(config, channel)
    text = xmlEscape(text)

    ttsConfig = getJsonConfig()['dynamic']['tts']
    # 支持日语
    if ttsConfig['japanese']['enable']:
        text = re.sub(r'[\u3040-\u309F\u30A0-\u30FF]+', calculateTags("ja-JP", ttsConfig['japanese'], '\g<0>'), text)
    
    ssml = f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="zh-CN"><voice xml:lang="zh-CN">{text}</voice></speak>'
    # Synthesize text to a stream
    stream = await channels[channel]['synthesizer'].synthesize_ssml_to_stream_async(ssml)

    temp_buffer = bytes(0)
    data_reader = streams.DataReader(stream)
    await data_reader.load_async(stream.size)
    while data_reader.unconsumed_buffer_length > 0:
        temp_buffer += bytes(data_reader.read_buffer(data_reader.unconsumed_buffer_length)) + b'\x00\x00\x00\x00\x00\x00\x00\x00'

    byte_stream = io.BytesIO(temp_buffer)

    pygame.mixer.Channel(channel).stop()
    while pygame.mixer.Channel(channel).get_busy():
        await asyncio.sleep(0.01)
    
    pygame.mixer.Channel(channel).play(pygame.mixer.Sound(byte_stream))

    while pygame.mixer.Channel(channel).get_busy():
        await asyncio.sleep(0.01)



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
    global prepareDisableTTSTask, disableTTSTask
    await init()
    while True:
        try:
            # 暂停TTS线程
            if prepareDisableTTSTask:
                disableTTSTask = True
                await asyncio.sleep(0.01)
                continue
            else:
                disableTTSTask = False
            syncSpeakerWithConfig()
            msg = popMessagesQueue()
            if msg == None:
                await asyncio.sleep(0.01)
                continue
            appendDelay(time.time() - msg['time'])
            text = messagesToText(msg)
            await tts(text)
        except Exception as e:
            if not isinstance(e, asyncio.CancelledError):
                traceback.print_exc()
                await asyncio.sleep(0.1)
            else:
                break

async def setDisableTTSTask(mode, waiting = True):
    global prepareDisableTTSTask, disableTTSTask
    if prepareDisableTTSTask == False and mode == True:
        prepareDisableTTSTask = mode
        while (not disableTTSTask) and waiting:
            await asyncio.sleep(0.01)
    elif prepareDisableTTSTask == True and mode == False:
        prepareDisableTTSTask = mode
        while (disableTTSTask) and waiting:
            await asyncio.sleep(0.01)

ttsSystemCallerID = 0
async def ttsSystem(msg):
    global initalized
    while not initalized:
        await asyncio.sleep(0.01)
    global ttsSystemCallerID
    ttsSystemCallerID += 1
    myCallerID = ttsSystemCallerID
    await setDisableTTSTask(True, False)
    syncSpeakerWithConfig()
    await tts(messagesToText({'type': 'system', 'msg': msg}))
    # 打断逻辑处理
    if ttsSystemCallerID != myCallerID:
        return
    await setDisableTTSTask(False, False)

async def readHistoryByType(types):
    global readHistoryIndex
    if readHistoryIndex == None:
        readHistoryIndex = len(getHaveReadMessages())
    readHistoryIndex -= 1
    messages = getHaveReadMessages()
    found = False
    for i in range(readHistoryIndex, -1, -1):
        for type in types:
            if messages[i]['type'] == type:
                readHistoryIndex = i
                found = True
                break
        if found:
            break
    if readHistoryIndex == -1 or not found:
        readHistoryIndex = len(getHaveReadMessages())
        await tts(messagesToText({'type': 'system', 'msg': '已到达最后一条,继续翻页将从第一条开始'}), 1, getJsonConfig()['dynamic']['tts']['history'])
        return
    await tts(messagesToText(messages[readHistoryIndex]), 1, getJsonConfig()['dynamic']['tts']['history'])

async def resetHistoryIndex():
    global readHistoryIndex
    readHistoryIndex = len(getHaveReadMessages())
    await tts(messagesToText({'type': 'system', 'msg': '焦点已回到最新'}), 1, getJsonConfig()['dynamic']['tts']['history'])