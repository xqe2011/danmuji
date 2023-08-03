from ctypes import *

zdsrDLL = windll.LoadLibrary("C:\\Program Files (x86)\\zdsr\\zdsr_yth\\ZDSRAPI_x64.dll")
zdsrDLL.InitTTS.argtypes = [c_int, c_wchar_p, c_bool]
zdsrDLL.InitTTS.restype = c_int
print(zdsrDLL.InitTTS(c_int(0), c_wchar_p(0), c_bool(False)))

zdsrDLL.Speak.argtypes = [c_wchar_p, c_bool]
zdsrDLL.Speak.restype = c_int
print(zdsrDLL.Speak(c_wchar_p("你好，我是小七"), c_bool(False)))