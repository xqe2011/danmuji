from quart import Quart, request, websocket, send_from_directory
from quart_cors import cors
from .config import updateDynamicConfig, getDynamicConfig, HTTP_TOKEN
import asyncio, json, os
from .logger import timeLog
from .messages_handler import markAllMessagesInvalid
import webbrowser

staticFilesPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), './static')
app = Quart(__name__, static_folder=staticFilesPath, static_url_path='/')
app = cors(app, allow_origin='*')
tasks = []
allWSClients = []

async def fakeRequest(url, query, method, data):
    return await (await app.test_client().open(path=url, query_string=query, method=method, json=data)).json

def checkToken(func):
    async def wrappedFunc(*args, **kwargs):
        if request.args.get('token') != HTTP_TOKEN:
            return { 'status': -1, 'msg': 'token error' }, 401
        return await func(*args, **kwargs)
    wrappedFunc.__name__ = func.__name__
    return wrappedFunc

@app.route('/', methods=['GET'])
async def index():
    global staticFilesPath
    return await send_from_directory(staticFilesPath, 'index.html')

@app.route('/api/flush', methods=['POST'])
@checkToken
async def flush():
    await markAllMessagesInvalid()
    return { 'status': 0, 'msg': 'ok' }

@app.route('/api/config', methods=['GET'])
@checkToken
async def getConfig():
    return { 'status': 0, 'msg': getDynamicConfig() }

@app.route('/api/config', methods=['POST'])
@checkToken
async def updateConfig():
    await updateDynamicConfig(await request.json)
    return { 'status': 0, 'msg': 'ok' }

@app.websocket('/ws/client')
async def ws():
    if 'token' not in websocket.args or websocket.args['token'] != HTTP_TOKEN:
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
    webbrowser.open('http://127.0.0.1:8080/?token=' + HTTP_TOKEN, new=1, autoraise=True)
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
    global tasks
    tasks = backgroundTasks
    timeLog('[HTTP] Started, url: http://127.0.0.1:8080/?token=' + HTTP_TOKEN)
    app.run(host='0.0.0.0', port=8080)