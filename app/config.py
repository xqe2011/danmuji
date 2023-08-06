from .logger import timeLog
import json, sys, os

configPath = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.getcwd()

if not os.path.isfile(os.path.join(configPath, './config.json')):
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../config.template.json'), encoding='utf-8', mode='r') as f,  open(os.path.join(configPath, './config.json'), encoding='utf-8', mode='w') as f2:
        f2.write(f.read())

jsonConfig = json.load(open(os.path.join(configPath, './config.json'), encoding='utf-8'))         
timeLog(f'[Config] Loaded json config: {json.dumps(jsonConfig, ensure_ascii=False)}')

async def updateJsonConfig(config):
    global jsonConfig
    jsonConfig = config
    with open(os.path.join(configPath, './config.json'), encoding='utf-8', mode='w') as f:
        json.dump(jsonConfig, f, ensure_ascii=False, indent=4)
    timeLog(f'[Config] Updated json config: {json.dumps(jsonConfig, ensure_ascii=False)}')

def getJsonConfig():
    global jsonConfig
    return jsonConfig
