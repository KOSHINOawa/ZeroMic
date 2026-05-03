
# ZeroMic

<div align="center">
  <img src="https://x19.fp.ps.netease.com/file/69f5fc8dfcc7c18f65647c58EUpGTLbr07" width="128" height="128" alt="ZeroMic Logo">
  <h1>ZeroMic</h1>
  <p><strong>手机免安装 · 电脑绿色单文件 · MD3 现代 UI 设计</strong></p>
  <p>将你的智能手机瞬间变身为电脑的高保真无线麦克风</p>
  <img src="https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-blue?style=flat-square" alt="Platform">
  <img src="https://img.shields.io/badge/License-GPLv3-green?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/Built%20with-Python%20%7C%20WebRTC-yellow?style=flat-square" alt="Tech">
</div>

## 📖 简介

**ZeroMic** 是一款极简的跨平台无线麦克风传输工具。
当你台式机没有麦克风，或者需要高质量的语音输入来进行游戏开黑（如 Discord、KOOK）或网络会议时，只需运行 ZeroMic，用手机访问局域网地址，即可利用手机的高性能麦克风进行毫秒级延迟的音频传输。

核心采用 P2P **WebRTC 技术**，音频数据完全在局域网内直连，**不经过任何外部服务器**，保证极致的安全与极低的延迟。


# ✨ 特点
🚀 拿来就用：一个 .exe 文件，绿色免装，双击跑起来。

🔧 驱动全自动：虚拟声卡自动下载、静默安装、自动配好，不用你动手。

⚡ 延迟够低：WebRTC 局域网直连，通话跟插了线差不多。

🎨 看着舒服：深色界面，MD3 风格，交互跟手，状态反馈清楚。

🧹 走也干净：内置驱动清理，卸载不残留注册表垃圾。


## 🚀 快速开始

### 准备工作
- 一台 Windows 10 / 11 电脑（需要内置 WebView2 运行环境，现代 Win10/11 已自带）。
- 手机与电脑需要处于 **同一个局域网（Wi-Fi）** 下。

### 使用步骤
1. 前往 [Releases](https://github.com/hypixice/ZeroMic/releases) 页面下载最新的 `ZeroMic.exe`。
2. 右键点击 `ZeroMic.exe`，选择 **「以管理员身份运行」**（首次运行需要权限配置虚拟声卡）。
3. 如果是首次启动，软件会自动下载并部署运行环境，请耐心等待 10-20 秒。
4. 环境配置完毕后，电脑端会显示一个 URL 地址（如 `https://192.168.x.x:5000`）。
5. 在手机浏览器（推荐 Safari / Chrome / Edge）中输入该地址。
6. 在电脑游戏或语音软件的设置中，将 **麦克风输入设备** 更改为 `CABLE Output (VB-Audio Virtual Cable)`。
7. 开始说话吧！

## 🛠️ 开发者指南 (从源码构建)

如果你想自行修改代码并打包，请按照以下步骤操作：

```bash
# 1. 克隆仓库
git clone [https://github.com/hypixice/ZeroMic.git](https://github.com/hypixice/ZeroMic.git)
cd ZeroMic

# 2. 创建并激活虚拟环境 (推荐)
python -m venv .venv
.\.venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 一键打包 (确保你在管理员 PowerShell 中运行)
.\.venv\Scripts\pyinstaller -i icon.ico -w --onefile --uac-admin --add-data "webui;webui" --hidden-import="engineio.async_drivers.threading" main.py
```

*注意：打包后请在 `dist` 目录下找到生成的 EXE 文件。*

## ⚠️ 常见问题 (FAQ)

**Q: 手机浏览器提示“不安全”或拒绝访问？**
A: 因为我们使用了自签名证书来开启局域网 HTTPS（WebRTC 的强制要求）。请在浏览器拦截页面点击“高级” -> “继续访问”即可。

**Q: 为什么装完之后电脑突然没声音了？**
A: 这是 Windows 的底层机制，它可能会将新安装的虚拟声卡设为默认扬声器。请点击电脑右下角的喇叭 🔊 图标，手动切换回你原来的扬声器设备即可。

**Q: 点击卸载驱动报错？**
A: 请确保软件是以**管理员身份**运行的。卸载完成后建议重启电脑以彻底清理 Windows 音频路由表的残留。

## 📄 许可协议
本项目采用 [GPL-3.0 License](LICENSE) 许可协议。任何人都可以自由使用、修改和分发，但衍生作品必须同样开源并采用相同协议。

---
*Created with ❤️ by Hypixice Studio.*
