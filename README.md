# 企鹅弹幕机
为语音读弹幕而生的B站直播弹幕机。
- 支持无障碍，对于视力障碍群体可以完全实现自己操作和控制
- 支持高速语音，比常规弹幕机的语速更快，可以在大量弹幕时降低语音延迟
- 支持多种过滤功能，如屏蔽词/表情包等
- 支持图表显示弹幕机实时数据，方便在线调节参数
- 支持中文/英文/日语
- 支持远程控制功能，你可以连接远程服务器后通过分享链接让其他人控制弹幕机

## 使用方法
- 点击[这里](https://github.com/xqe2011/danmuji/releases/download/latest/installer.exe)下载最新版
- 打开下载的文件并点击安装，安装完成后在桌面打开企鹅弹幕机图标
- 在弹出的企鹅弹幕机配置页面处设置好直播间号，重启弹幕机
- 如果需要使用日语功能，请在`系统-语言-添加语言`处选择日语，只勾选语音包其他无需勾选，安装完成重启弹幕机即可

# 常用键位
部分游戏会占用所有键位，此时全局键位功能将失效。 
| 场景 | 键位 | 功能 |
|---|---|---|
| 网页 | Ctrl+S | 保存配置 |
| 任何时候 | Ctrl+Alt+等于号 | 音量增加 |
| 任何时候 | Ctrl+Alt+减号 | 音量减少 |
| 任何时候 | Ctrl+Alt+左方括号 | 语速增加 |
| 任何时候 | Ctrl+Alt+右方括号 | 语速减少 |
| 任何时候 | Ctrl+Alt+M | 音频输出切换 |
| 任何时候 | Alt+F6 | 查看弹幕延迟 |
| 任何时候 | Ctrl+Alt+F5 | 清空弹幕 |
| 任何时候 | Alt+F7 | 历史模式查看上一条礼物 |
| 任何时候 | Alt+F8 | 历史模式查看上一条弹幕 |
| 任何时候 | Alt+T | 历史模式查看下一条礼物 |
| 任何时候 | Alt+Y | 历史模式查看下一条弹幕 |
| 任何时候 | Alt+F9 | 历史模式回到最新弹幕 |
| 任何时候 | Ctrl+Alt+F8 | 强制切换开放平台连接 |

## EdgeOne 开放平台代理（edge-functions）

`edge-functions/` 是 [open-server](./open-server) 的 [腾讯云 EdgeOne Makers Edge Functions](https://cloud.tencent.com/document/product/1552/127416) 实现，对外提供相同的 B 站直播开放平台 HTTP API，可直接作为弹幕机配置里的 `openAPIURL`。

### 路由对照

按 EdgeOne 约定，`/edge-functions` 目录会映射为站点路径：

| 文件 | 路由 | 方法 | 说明 |
|---|---|---|---|
| `edge-functions/v2/app/start.js` | `/v2/app/start` | POST | 开启场次，请求体 `{ "code": "<身份码>" }` |
| `edge-functions/v2/app/end.js` | `/v2/app/end` | POST | 结束场次，请求体 `{ "game_id": "..." }` |
| `edge-functions/v2/app/heartbeat.js` | `/v2/app/heartbeat` | POST | 心跳，请求体 `{ "game_id": "..." }` |

公共签名与请求逻辑在 `edge-functions/shared/common.js`。

### 与 open-server 的差异

- **不包含 WebSocket**：EdgeOne 目前不支持 WebSocket，因此未迁移 `WEBSOCKET_URL` / `WEBSOCKET_ENABLE`，也不提供 `/sub` 代理。
- `/v2/app/start` 返回的 `websocket_info.wss_link` **保持哔哩哔哩原始地址**，行为与 open-server 在 `WEBSOCKET_ENABLE=false` 时一致。
- 其余 HTTP 接口的鉴权头、请求体、响应结构与 open-server 保持一致。

### 环境变量

在 EdgeOne Makers 项目中配置（通过 `context.env` 读取）：

| 变量 | 说明 |
|---|---|
| `ACCESS_KEY_ID` | 哔哩哔哩开放平台 access key |
| `ACCESS_KEY_SECRET` | 哔哩哔哩开放平台 access secret |
| `APP_ID` | 开放平台应用 ID（数字） |

无需配置任何 `WEBSOCKET_*` 变量。

### 部署说明

将本仓库接入 EdgeOne Makers 后，平台会根据 `edge-functions/` 目录自动生成上述路由。部署完成后，把弹幕机 `engine.bili.openAPIURL` 设为该站点根地址即可（例如 `https://your-makers-domain.example`）。

## 贡献本项目
### 克隆并安装依赖
```
git clone --recurse-submodules https://github.com/xqe2011/danmuji
pip install -r requirements.txt
```
### 编译配置页面
```
cd web
npm run build
cd ../
mv ./web/dist ./static
```
### 启动主程序
```
python launcher.py
```
### 打包
```
pyinstaller launcher.spec
```
