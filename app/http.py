from quart import Quart, request, websocket
from .config import updateDynamicConfig, getDynamicConfig
import random, string, asyncio, json
from .logger import timeLog
from .messages_handler import markAllMessagesInvalid

app = Quart(__name__, static_folder='static', static_url_path='/')
token = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(32))
tasks = []
allWSClients = []

def checkToken(func):
    async def wrappedFunc(*args, **kwargs):
        if request.args.get('token') != token:
            return { 'status': -1, 'msg': 'token error' }, 401
        return await func(*args, **kwargs)
    wrappedFunc.__name__ = func.__name__
    return wrappedFunc

@app.route('/flush')
@checkToken
async def flush():
    await markAllMessagesInvalid()
    return { 'status': 0, 'msg': 'ok' }

@app.route('/get_config')
@checkToken
async def getConfig():
    return { 'status': 0, 'msg': await getDynamicConfig() }

@app.route('/update_config')
@checkToken
async def updateConfig():
    await updateDynamicConfig(await request.json)
    return { 'status': 0, 'msg': 'ok' }

@app.websocket('/ws')
async def ws():
    try:
        allWSClients.append(websocket._get_current_object())
        while True:
            await websocket.receive()
    except asyncio.CancelledError:
        allWSClients.remove(websocket)
        raise

@app.before_serving
async def startup():
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
    timeLog('[HTTP] Started, url: http://127.0.0.1:8080/?token=' + token)
    app.run(host='0.0.0.0', port=8080)