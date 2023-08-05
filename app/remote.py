import websockets, json, asyncio
from .config import REMOTE_SERVER, REMOTE_ENABLE, REMOTE_PASSWORD, HTTP_TOKEN
from .http import fakeRequest
from .logger import timeLog

websocketClient = None

async def remoteWSBroadcast(msg):
    if websocketClient != None:
        await websocketClient.send(json.dumps({
            "type": "websocket",
            "data": msg
        }, ensure_ascii=False))

async def initRemote():
    if REMOTE_ENABLE != 1:
        return
    while True:
        try:
            async with websockets.connect(f"{REMOTE_SERVER}/ws/server?password={REMOTE_PASSWORD}&token={HTTP_TOKEN}") as websocket:
                timeLog('[Remote] Connected')
                global websocketClient
                websocketClient = websocket
                while True:
                    data = json.loads(await websocket.recv())
                    if data['type'] == 'request':
                        await websocket.send(json.dumps({
                            "type": "response",
                            "id": data['id'],
                            "data": await fakeRequest(data['url'], data['query'], data['method'], data['data'])
                        }, ensure_ascii=False))
        except (websockets.exceptions.ConnectionClosedError, ConnectionRefusedError):
            websocketClient = None
            timeLog('[Remote] Error: ConnectionClosedError')
        except websockets.exceptions.InvalidStatusCode:
            websocketClient = None
            timeLog(f'[Remote] Error: Server rejected')
        except asyncio.CancelledError:
            websocketClient = None
            break
        await asyncio.sleep(1)
    timeLog('[Remote] Disconnected')
            