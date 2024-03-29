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