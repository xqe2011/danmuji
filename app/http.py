from quart import Quart, request, websocket, send_from_directory
from quart_cors import cors
from .config import updateJsonConfig, getJsonConfig
import asyncio, json, os, webbrowser
from .logger import timeLog
from .messages_handler import markAllMessagesInvalid
if os.name == 'nt':
    from .tts import getAllVoices, getAllSpeakers

staticFilesPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../static')
app = Quart(__name__, static_folder=staticFilesPath, static_url_path='/')
app = cors(app, allow_origin='*')
tasks = []
allWSClients = []
token = getJsonConfig()['engine']['http']['token']

async def fakeRequest(url, query, method, data):
    return await (await app.test_client().open(path=url, query_string=query, method=method, json=data)).json

def checkToken(func):
    async def wrappedFunc(*args, **kwargs):
        global token
        if request.args.get('token') != token:
            return { 'status': -1, 'msg': 'token error' }, 401
        return await func(*args, **kwargs)
    wrappedFunc.__name__ = func.__name__
    return wrappedFunc

def onlyLocal(func):
    async def wrappedFunc(*args, **kwargs):
        if request.args.get('remote') == '1':
            return { 'status': -1, 'msg': 'not support this method in remote mode' }, 403
        return await func(*args, **kwargs)
    wrappedFunc.__name__ = func.__name__
    return wrappedFunc

@app.route('/', methods=['GET'])
async def index():
    global staticFilesPath
    return await send_from_directory(staticFilesPath, 'index.html')

@app.after_request
def addHeader(response):
    response.cache_control.no_cache = True
    return response

@app.route('/api/running_mode', methods=['GET'])
async def getRunningMode():
    return { 'status': 0, 'msg': { 'remote': False } }

@app.route('/api/logout', methods=['POST'])
@checkToken
@onlyLocal
async def logout():
    nowJsonConfig = getJsonConfig()
    nowJsonConfig['kvdb']['bili']['sessdata'] = ""
    nowJsonConfig['kvdb']['bili']['jct'] = ""
    await updateJsonConfig(nowJsonConfig)
    return { 'status': 0, 'msg': 'ok' }

@app.route('/api/tts/speakers', methods=['GET'])
@checkToken
async def getSpeakers():
    if os.name != 'nt':
        return { 'status': -1, 'msg': 'not support' }, 400
    return { 'status': 0, 'msg': getAllSpeakers() }

@app.route('/api/tts/voices', methods=['GET'])
@checkToken
async def getVoices():
    if os.name != 'nt':
        return { 'status': -1, 'msg': 'not support' }, 400
    return { 'status': 0, 'msg': getAllVoices() }

@app.route('/api/flush', methods=['POST'])
@checkToken
async def flush():
    await markAllMessagesInvalid()
    return { 'status': 0, 'msg': 'ok' }

@app.route('/api/config/dynamic', methods=['GET'])
@checkToken
async def getConfig():
    return { 'status': 0, 'msg': getJsonConfig()['dynamic'] }

@app.route('/api/config/dynamic', methods=['POST'])
@checkToken
async def updateConfig():
    nowJsonConfig = getJsonConfig()
    nowJsonConfig['dynamic'] = await request.json
    await updateJsonConfig(nowJsonConfig)
    return { 'status': 0, 'msg': 'ok' }

@app.route('/api/config/engine', methods=['GET'])
@checkToken
@onlyLocal
async def getEngineConfig():
    data = getJsonConfig()['engine']
    return { 'status': 0, 'msg': data }

@app.route('/api/config/engine', methods=['POST'])
@checkToken
@onlyLocal
async def updateEngineConfig():
    nowJsonConfig = getJsonConfig()
    nowJsonConfig['engine'] = await request.json
    await updateJsonConfig(nowJsonConfig)
    return { 'status': 0, 'msg': 'ok' }

@app.websocket('/ws/client')
async def ws():
    global token
    if 'token' not in websocket.args or websocket.args['token'] != token:
        await websocket.close(code=-1, reason='token error')
        return
    try:
        allWSClients.append(websocket._get_current_object())
        while True:
            await websocket.receive()
    except asyncio.CancelledError:
        allWSClients.remove(websocket)
        raise

@app.before_serving
async def startup():
    global token
    webbrowser.register('edge', None, webbrowser.GenericBrowser(os.environ['ProgramFiles(x86)'] + r'\Microsoft\Edge\Application\msedge_proxy.exe'), preferred=True)
    webbrowser.open('http://127.0.0.1:8080/?token=' + token, new=1, autoraise=True)
    for task in tasks:
        app.add_background_task(task)

@app.after_serving
async def cleanup():
    for task in app.background_tasks:
        task.cancel()

async def broadcastWSMessage(message):
    for ws in allWSClients:
        await ws.send(json.dumps(message, ensure_ascii=False))

def startHttpServer(backgroundTasks):
    global tasks, token
    tasks = backgroundTasks
    timeLog('[HTTP] Started, url: http://127.0.0.1:8080/?token=' + token)
    app.run(host='0.0.0.0', port=8080)