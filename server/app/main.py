from quart import Quart, websocket, request, send_from_directory
import asyncio, random, os
from .logger import timeLog
from .config import HTTP_SERVER_PASSWORD

staticFilesPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), './static')
app = Quart(__name__, static_folder=staticFilesPath, static_url_path='/')
danmuji = {}

@app.route('/', methods=['GET'])
async def index():
    global staticFilesPath
    return await send_from_directory(staticFilesPath, 'index.html')

@app.route('/api/<path:path>', methods=['GET', 'POST'])
async def proxyRequest(path):
    global danmuji
    if request.args.get('token') not in danmuji:
        return { 'status': -1, 'msg': 'token error' }, 401
    target = danmuji[request.args.get('token')]
    requestID = random.randrange(100000000, 999999999)
    timeLog(f"[Client] Forwarding http request {'/api/' +path} to server which token: {request.args.get('token')}, ip: {request.remote_addr}")
    await target['server'].send_json({
        'type': 'request',
        'id': requestID,
        'url': '/api/' + path,
        'query': request.args,
        'method': request.method,
        'data': await request.json,
    })
    while target['response'] == None or target['response']['id'] != requestID:
        await target['event'].wait()
    timeLog(f"[Client] Got http response from server which token: {request.args.get('token')}, ip: {request.remote_addr}")
    return target['response']['data']

@app.websocket('/ws/client')
async def wsClient():
    global danmuji
    if 'token' not in websocket.args or websocket.args['token'] not in danmuji:
        await websocket.close(code=-1, reason='token error')
        return
    token = websocket.args['token']
    timeLog(f'[Client] New connection from token: {token}, ip: {websocket.remote_addr}')
    try:
        danmuji[token]['client'].append(websocket._get_current_object())
        while True:
            await websocket.receive()
    except asyncio.CancelledError:
        timeLog(f'[Client] Disconnected from token: {token}, ip: {websocket.remote_addr}')
        danmuji[token]['client'].remove(websocket._get_current_object())
        raise

@app.websocket('/ws/server')
async def wsServer():
    if 'password' not in websocket.args or 'token' not in websocket.args:
        timeLog(f'[Server] Password or token not found from ip: {websocket.remote_addr}')
        await websocket.close(code=-1003, reason='password or token not found!')
        return
    if websocket.args['password'] != HTTP_SERVER_PASSWORD:
        timeLog(f'[Server] Password incorrect from ip: {websocket.remote_addr}')
        await websocket.close(code=-1002, reason='server password is incorrect!')
        return
    global danmuji
    token = websocket.args['token']
    if token in danmuji:
        await websocket.close(code=-1001, reason='this token has been used!')
        return
    danmuji[token] = {
        'client': [],
        'server': websocket._get_current_object(),
        'event': asyncio.Event(),
        'response': None,
    }
    timeLog(f'[Server] New connection from token: {token}')
    try:
        while True:
            message = await websocket.receive_json()
            if message['type'] == 'response':
                danmuji[token]['response'] = message
                danmuji[token]['event'].set()
                danmuji[token]['event'].clear()
            elif message['type'] == 'websocket':
                for client in danmuji[token]['client']:
                    await client.send_json(message['data'])
    except asyncio.CancelledError:
        timeLog(f'[Server] Disconnected from token: {token}')
        del danmuji[token]
        raise

def main():
    app.run(host='0.0.0.0', port=7070)

if __name__ == '__main__':
    main()