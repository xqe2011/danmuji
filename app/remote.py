import websockets, json, asyncio, traceback
from .config import getJsonConfig
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
    config = getJsonConfig()['engine']
    if config['remote']['enable'] != 1:
        return
    while True:
        try:
            async with websockets.connect(f"{config['remote']['server']}/ws/server?password={config['remote']['password']}&token={config['http']['token']}") as websocket:
                timeLog('[Remote] Connected')
                global websocketClient
                websocketClient = websocket
                while True:
                    data = json.loads(await websocket.recv())
                    if data['type'] == 'request':
                        data['query']['remote'] = '1'
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
        except:
            websocketClient = None
            timeLog(f'[Remote] Error: Unknown')
            traceback.print_exc()
        await asyncio.sleep(1)
    timeLog('[Remote] Disconnected')
            