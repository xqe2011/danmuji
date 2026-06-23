import asyncio
import aifc
import audioop
import io
import json
import math
import os
import platform
import re
import tempfile
import time
import traceback

import pygame
import pygame._sdl2.audio as sdl2_audio
from pydub import AudioSegment

from .config import getJsonConfig
from .logger import timeLog
from .messages_handler import getHaveReadMessages, popMessagesQueue
from .stats import appendDelay

IS_WINDOWS = os.name == 'nt'
IS_MACOS = platform.system() == 'Darwin'

if IS_WINDOWS:
    import winsdk.windows.media.speechsynthesis as speechsynthesis
    import winsdk.windows.storage.streams as streams
elif IS_MACOS:
    import AppKit
    from Foundation import NSURL


symbolToText = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../symbol-to-text.json'), encoding='utf-8', mode='r'))
prepareDisableTTSTask = False
disableTTSTask = False
readHistoryIndex = None
initalized = False
ttsSystemCallerID = 0


def _clamp(value, min_value, max_value):
    return max(min_value, min(max_value, value))


def _config_rate_to_windows_rate(rate):
    return 0.5 + (_clamp(rate, 1, 100) / 100.0) * 5.5


def _config_rate_to_ssml_rate(rate):
    return 0.5 + (_clamp(rate, 1, 100) / 100.0) * 2.5


def _config_rate_to_macos_wpm(rate):
    # Keep the old 1..100 UI while mapping to a useful macOS speech range.
    return int(round(150 + ((_clamp(rate, 1, 100) - 1) / 99.0) * 250))


def _volume_to_gain(volume):
    volume = _clamp(volume, 1, 100) / 100.0
    return 20.0 * math.log10(volume)


def _normalize_locale(locale):
    if locale == None:
        return ''
    locale = str(locale).replace('_', '-')
    parts = locale.split('-')
    language = parts[0].lower()
    region = ''
    for part in reversed(parts[1:]):
        if len(part) == 2 or part.isdigit():
            region = part.upper()
            break
    if language == 'zh' and region == '' and any(part.lower() == 'hans' for part in parts[1:]):
        region = 'CN'
    if region != '':
        return language + '-' + region
    return language


def _prepare_audio_segment(segment):
    segment += 12
    segment = segment.compress_dynamic_range(threshold=-3.0, ratio=20.0)
    byte_stream = io.BytesIO()
    segment.export(byte_stream, format='wav')
    byte_stream.seek(0)
    return byte_stream


def _audio_segment_from_aiff(path):
    with aifc.open(path, 'rb') as aiffFile:
        channels = aiffFile.getnchannels()
        sampleWidth = aiffFile.getsampwidth()
        frameRate = aiffFile.getframerate()
        data = aiffFile.readframes(aiffFile.getnframes())
    if sampleWidth > 1:
        data = audioop.byteswap(data, sampleWidth)
    return AudioSegment(data=data, sample_width=sampleWidth, frame_rate=frameRate, channels=channels)


def _audio_segment_from_file(path, format=None):
    try:
        return AudioSegment.from_file(path, format=format)
    except Exception:
        if path.lower().endswith(('.aif', '.aiff')):
            return _audio_segment_from_aiff(path)
        raise


async def _play_audio_segment(segment, channel):
    byte_stream = _prepare_audio_segment(segment)
    pygame.mixer.Channel(channel).stop()
    while pygame.mixer.Channel(channel).get_busy():
        await asyncio.sleep(0.01)

    pygame.mixer.Channel(channel).play(pygame.mixer.Sound(byte_stream))

    while pygame.mixer.Channel(channel).get_busy():
        await asyncio.sleep(0.01)


class BaseTTSBackend:
    def __init__(self):
        self.allSpeakers = []
        self.allVoices = []
        self.nowSpeaker = None
        self.lastSpeaker = None
        self.channels = [
            {'lastRate': None, 'lastVolume': None, 'lastVoice': None},
            {'lastRate': None, 'lastVolume': None, 'lastVoice': None},
        ]

    def is_supported(self):
        return False

    def load_speakers(self):
        try:
            if pygame.mixer.get_init() == None:
                pygame.mixer.init()
            self.allSpeakers = list(sdl2_audio.get_audio_device_names(False))
        except Exception as e:
            timeLog(f'[TTS] Failed to list speakers: {e}')
            self.allSpeakers = []
        return self.allSpeakers

    def get_all_speakers(self):
        if len(self.allSpeakers) == 0:
            self.load_speakers()
        return self.allSpeakers

    def get_all_voices(self):
        return []

    def get_now_speaker(self):
        return self.nowSpeaker

    async def init(self):
        pygame.mixer.init()
        self.load_speakers()
        for name in list(self.allSpeakers):
            timeLog(f'[TTS] Found speaker: {name}')
        self.load_voices()
        self.sync_speaker_with_config()

    def load_voices(self):
        return []

    def sync_speaker_with_config(self):
        ttsConfig = getJsonConfig()['dynamic']['tts']
        if self.lastSpeaker == ttsConfig['speaker'] and pygame.mixer.get_init() != None:
            return

        self.lastSpeaker = ttsConfig['speaker']
        self.nowSpeaker = None
        for speaker in list(self.get_all_speakers()):
            if ttsConfig['speaker'] != '' and ttsConfig['speaker'] in speaker:
                self.nowSpeaker = speaker
                break

        for channel in range(len(self.channels)):
            pygame.mixer.Channel(channel).stop()
        pygame.mixer.quit()

        if self.nowSpeaker != None:
            timeLog(f'[TTS] Use speaker: {self.nowSpeaker}"')
            pygame.mixer.init(devicename=self.nowSpeaker)
        else:
            if len(self.allSpeakers) > 0:
                self.nowSpeaker = self.allSpeakers[0]
                timeLog(f'[TTS] Use default speaker: {self.nowSpeaker}"')
                pygame.mixer.init(devicename=self.nowSpeaker)
            else:
                timeLog('[TTS] Use system default speaker"')
                pygame.mixer.init()

    def sync_with_config(self, ttsConfig=None, channel=0):
        if ttsConfig == None:
            ttsConfig = getJsonConfig()['dynamic']['tts']
        channelInfo = self.channels[channel]
        if channelInfo['lastVolume'] != ttsConfig['volume']:
            channelInfo['lastVolume'] = ttsConfig['volume']
        if channelInfo['lastRate'] != ttsConfig['rate']:
            channelInfo['lastRate'] = ttsConfig['rate']
        if channelInfo['lastVoice'] != ttsConfig['voice']:
            channelInfo['lastVoice'] = ttsConfig['voice']

    async def synthesize(self, text, channel=0, config=None):
        raise RuntimeError('TTS is not supported on this platform')


class UnsupportedTTSBackend(BaseTTSBackend):
    pass


if IS_WINDOWS:
    class WindowsTTSBackend(BaseTTSBackend):
        def __init__(self):
            super().__init__()
            self.channels = [
                {'lastRate': None, 'lastVolume': None, 'lastVoice': None, 'synthesizer': speechsynthesis.SpeechSynthesizer()},
                {'lastRate': None, 'lastVolume': None, 'lastVoice': None, 'synthesizer': speechsynthesis.SpeechSynthesizer()},
            ]

        def is_supported(self):
            return True

        def load_voices(self):
            self.allVoices = speechsynthesis.SpeechSynthesizer.all_voices
            for voice in list(self.allVoices):
                timeLog(f'[TTS] Found voice: {voice.display_name} ({voice.language})"')
            return self.allVoices

        def get_all_voices(self):
            if len(self.allVoices) == 0:
                self.load_voices()
            return [{'name': voice.display_name, 'language': voice.language} for voice in list(self.allVoices)]

        def sync_with_config(self, ttsConfig=None, channel=0):
            if ttsConfig == None:
                ttsConfig = getJsonConfig()['dynamic']['tts']
            channelInfo = self.channels[channel]
            if channelInfo['lastVolume'] != ttsConfig['volume']:
                channelInfo['lastVolume'] = ttsConfig['volume']
                channelInfo['synthesizer'].options.audio_volume = channelInfo['lastVolume'] / 100.0
            if channelInfo['lastRate'] != ttsConfig['rate']:
                channelInfo['lastRate'] = ttsConfig['rate']
                channelInfo['synthesizer'].options.speaking_rate = _config_rate_to_windows_rate(channelInfo['lastRate'])
            if channelInfo['lastVoice'] != ttsConfig['voice']:
                channelInfo['lastVoice'] = ttsConfig['voice']
                targetVoice = None
                for voice in list(self.allVoices):
                    if ttsConfig['voice'] in voice.display_name:
                        targetVoice = voice
                        break
                if targetVoice != None:
                    timeLog(f'[TTS] Use voice: {targetVoice.display_name} ({targetVoice.language})"')
                    channelInfo['synthesizer'].voice = targetVoice
                else:
                    voice = channelInfo['synthesizer'].voice
                    timeLog(f'[TTS] Use default voice: {voice.display_name} ({voice.language})"')

        async def synthesize(self, text, channel=0, config=None):
            self.sync_with_config(config, channel)
            ttsConfig = getJsonConfig()['dynamic']['tts']
            text = xmlEscape(text)
            if ttsConfig['japanese']['enable']:
                text = re.sub(
                    r'[\u3040-\u309F\u30A0-\u30FF]+',
                    lambda match: calculateTags('ja-JP', ttsConfig['japanese'], xmlEscape(match.group(0))),
                    text,
                )
            ssml = f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="zh-CN"><voice xml:lang="zh-CN">{text}</voice></speak>'
            stream = await self.channels[channel]['synthesizer'].synthesize_ssml_to_stream_async(ssml)

            temp_buffer = bytes(0)
            data_reader = streams.DataReader(stream)
            await data_reader.load_async(stream.size)
            while data_reader.unconsumed_buffer_length > 0:
                temp_buffer += bytes(data_reader.read_buffer(data_reader.unconsumed_buffer_length)) + b'\x00\x00\x00\x00\x00\x00\x00\x00'

            segment = AudioSegment.from_file(io.BytesIO(temp_buffer), format='wav')
            stream.close()
            return segment


if IS_MACOS:
    class MacOSTTSBackend(BaseTTSBackend):
        def is_supported(self):
            return True

        def load_voices(self):
            self.allVoices = []
            for voiceID in list(AppKit.NSSpeechSynthesizer.availableVoices()):
                attributes = AppKit.NSSpeechSynthesizer.attributesForVoice_(voiceID) or {}
                name = self._voice_attribute(attributes, 'NSVoiceName', 'VoiceName') or str(voiceID).split('.')[-1]
                locale = self._voice_attribute(attributes, 'NSVoiceLocaleIdentifier', 'VoiceLocaleIdentifier')
                if locale == None:
                    locale = self._voice_attribute(attributes, 'NSVoiceLanguage', 'VoiceLanguage')
                voice = {
                    'id': str(voiceID),
                    'name': str(name),
                    'language': _normalize_locale(locale),
                }
                self.allVoices.append(voice)
                timeLog(f'[TTS] Found voice: {voice["name"]} ({voice["language"]})"')
            return self.allVoices

        def _voice_attribute(self, attributes, constant_name, fallback_key):
            keys = []
            if hasattr(AppKit, constant_name):
                keys.append(getattr(AppKit, constant_name))
            keys.append(fallback_key)
            keys.append(constant_name)
            for key in keys:
                if key in attributes:
                    return attributes[key]
            for key, value in attributes.items():
                keyName = str(key)
                if keyName.endswith(fallback_key) or keyName.endswith(constant_name):
                    return value
            return None

        def get_all_voices(self):
            if len(self.allVoices) == 0:
                self.load_voices()
            return [{'name': voice['name'], 'language': voice['language']} for voice in list(self.allVoices)]

        def sync_with_config(self, ttsConfig=None, channel=0):
            super().sync_with_config(ttsConfig, channel)
            if ttsConfig == None:
                ttsConfig = getJsonConfig()['dynamic']['tts']
            voice = self._find_voice(ttsConfig.get('voice', ''), 'zh-CN')
            if voice != None:
                timeLog(f'[TTS] Use voice: {voice["name"]} ({voice["language"]})"')

        async def synthesize(self, text, channel=0, config=None):
            if config == None:
                config = getJsonConfig()['dynamic']['tts']
            self.sync_with_config(config, channel)
            ttsConfig = getJsonConfig()['dynamic']['tts']
            return await asyncio.to_thread(self._synthesize_text, text, config, ttsConfig)

        def _synthesize_text(self, text, config, ttsConfig):
            segments = self._split_text(text, config, ttsConfig)
            combined = AudioSegment.empty()
            for segmentText, segmentConfig, preferredLanguage in segments:
                if segmentText == '':
                    continue
                combined += self._synthesize_segment(segmentText, segmentConfig, preferredLanguage)
            if len(combined) == 0:
                return AudioSegment.silent(duration=100)
            return combined

        def _split_text(self, text, config, ttsConfig):
            if not ttsConfig['japanese']['enable']:
                return [(text, config, 'zh-CN')]

            segments = []
            lastEnd = 0
            for match in re.finditer(r'[\u3040-\u309F\u30A0-\u30FF]+', text):
                if match.start() > lastEnd:
                    segments.append((text[lastEnd:match.start()], config, 'zh-CN'))
                segments.append((match.group(0), ttsConfig['japanese'], 'ja-JP'))
                lastEnd = match.end()
            if lastEnd < len(text):
                segments.append((text[lastEnd:], config, 'zh-CN'))
            return segments if len(segments) > 0 else [(text, config, 'zh-CN')]

        def _synthesize_segment(self, text, config, preferredLanguage):
            voice = self._find_voice(config.get('voice', ''), preferredLanguage)
            voiceID = voice['id'] if voice != None else AppKit.NSSpeechSynthesizer.defaultVoice()
            synthesizer = AppKit.NSSpeechSynthesizer.alloc().initWithVoice_(voiceID)
            if synthesizer == None:
                synthesizer = AppKit.NSSpeechSynthesizer.alloc().init()
                if voiceID != None:
                    synthesizer.setVoice_(voiceID)
            synthesizer.setRate_(_config_rate_to_macos_wpm(config['rate']))
            if hasattr(synthesizer, 'setVolume_'):
                synthesizer.setVolume_(1.0)

            fd, path = tempfile.mkstemp(suffix='.aiff')
            os.close(fd)
            os.remove(path)
            try:
                url = NSURL.fileURLWithPath_(path)
                if not synthesizer.startSpeakingString_toURL_(text, url):
                    raise RuntimeError('failed to start macOS speech synthesis')
                while synthesizer.isSpeaking():
                    time.sleep(0.02)
                for _ in range(50):
                    if os.path.exists(path) and os.path.getsize(path) > 0:
                        break
                    time.sleep(0.02)
                segment = _audio_segment_from_file(path, format='aiff')
            finally:
                try:
                    os.remove(path)
                except OSError:
                    pass

            return segment + _volume_to_gain(config['volume'])

        def _find_voice(self, name, preferredLanguage):
            if len(self.allVoices) == 0:
                self.load_voices()
            if name != '':
                for voice in self.allVoices:
                    if name == voice['name'] or name in voice['name']:
                        return voice
            for voice in self.allVoices:
                if voice['language'] == preferredLanguage:
                    return voice
            preferredPrefix = preferredLanguage.split('-')[0]
            for voice in self.allVoices:
                if voice['language'].startswith(preferredPrefix):
                    return voice
            return None


def _create_tts_backend():
    if IS_WINDOWS:
        return WindowsTTSBackend()
    if IS_MACOS:
        return MacOSTTSBackend()
    return UnsupportedTTSBackend()


ttsBackend = _create_tts_backend()


def isTTSSupported():
    return ttsBackend.is_supported()


def getAllVoices():
    return ttsBackend.get_all_voices()


def getAllSpeakers():
    return ttsBackend.get_all_speakers()


async def init():
    await ttsBackend.init()
    await tts('TTS模块初始化成功')
    global initalized
    initalized = True


def syncSpeakerWithConfig():
    ttsBackend.sync_speaker_with_config()


def syncWithConfig(ttsConfig=None, channel=0):
    ttsBackend.sync_with_config(ttsConfig, channel)


def getNowSpeaker():
    return ttsBackend.get_now_speaker()


def xmlEscape(text):
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def calculateTags(lang, config, text):
    tagsXml = '<voice name="{}" xml:lang="{}"><prosody rate="{}" volume="{}">{}</prosody></voice>'
    return tagsXml.format(config['voice'], lang, _config_rate_to_ssml_rate(config['rate']), config['volume'], text)


async def tts(text, channel=0, config=None):
    ttsConfig = getJsonConfig()['dynamic']['tts']
    if ttsConfig['readSymbolEnable']:
        text = ''.join([symbolToText[char] if char in symbolToText else char for char in text])

    segment = await ttsBackend.synthesize(text, channel, config)
    await _play_audio_segment(segment, channel)


def messagesToText(msg):
    if msg['type'] == 'danmu':
        if msg['replyUname'] != '':
            return f"{msg['uname']}回复{msg['replyUname']}说{msg['msg']}"
        else:
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
    elif msg['type'] == 'warning':
        return f"超管警告直播间{msg['msg']}，{'，直播间已切断' if msg['isCutOff'] else ''}"
    elif msg['type'] == 'system':
        return f"系统提示{msg['msg']}"


async def ttsTask():
    global prepareDisableTTSTask, disableTTSTask
    if not isTTSSupported():
        timeLog('[TTS] This platform does not support TTS')
        return
    await init()
    while True:
        try:
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


async def setDisableTTSTask(mode, waiting=True):
    global prepareDisableTTSTask, disableTTSTask
    if prepareDisableTTSTask == False and mode == True:
        prepareDisableTTSTask = mode
        while (not disableTTSTask) and waiting:
            await asyncio.sleep(0.01)
    elif prepareDisableTTSTask == True and mode == False:
        prepareDisableTTSTask = mode
        while (disableTTSTask) and waiting:
            await asyncio.sleep(0.01)


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
    if ttsSystemCallerID != myCallerID:
        return
    await setDisableTTSTask(False, False)


async def readHistoryByType(types, revert=False):
    global readHistoryIndex
    if readHistoryIndex == None:
        readHistoryIndex = len(getHaveReadMessages())
    readHistoryIndex = (readHistoryIndex - 1) if not revert else (readHistoryIndex + 1)
    messages = getHaveReadMessages()
    found = False
    for i in range(readHistoryIndex, -1 if not revert else len(getHaveReadMessages()), -1 if not revert else 1):
        for type in types:
            if messages[i]['type'] == type:
                readHistoryIndex = i
                found = True
                break
        if found:
            break
    if (not revert and readHistoryIndex == -1) or (revert and readHistoryIndex > len(getHaveReadMessages())) or not found:
        if not revert:
            readHistoryIndex = len(getHaveReadMessages())
            await tts(messagesToText({'type': 'system', 'msg': '已到达最后一条,继续翻页将从第一条开始'}), 1, getJsonConfig()['dynamic']['tts']['history'])
        else:
            readHistoryIndex = 0
            await tts(messagesToText({'type': 'system', 'msg': '已到达第一条,继续翻页将从最后一条开始'}), 1, getJsonConfig()['dynamic']['tts']['history'])
        return
    await tts(messagesToText(messages[readHistoryIndex]), 1, getJsonConfig()['dynamic']['tts']['history'])


async def resetHistoryIndex():
    global readHistoryIndex
    readHistoryIndex = len(getHaveReadMessages())
    await tts(messagesToText({'type': 'system', 'msg': '焦点已回到最新'}), 1, getJsonConfig()['dynamic']['tts']['history'])
