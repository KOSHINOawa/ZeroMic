
import os
import socket
import threading
import webview
from flask import Flask, send_from_directory, jsonify
from flask_socketio import SocketIO, emit
import urllib.request
import zipfile
import tempfile
import ctypes
import subprocess
import sys
import time
import comtypes
from comtypes import GUID, IUnknown, COMMETHOD, HRESULT
from ctypes import c_wchar_p, c_int
import OpenSSL
import cryptography


# 兼容 PyInstaller 的资源路径定位机制
if getattr(sys, 'frozen', False):
    # 如果是打包后的 EXE 运行
    base_path = sys._MEIPASS
else:
    # 如果是 Python 源码运行
    base_path = os.path.dirname(os.path.abspath(__file__))



# 常量
VERSION = "v0.0.2"




def is_admin():
    """检查当前是否拥有管理员权限"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def check_virtual_cable_installed():
    """通过 PowerShell 检查是否已安装 VB-Cable"""
    try:
        # 查询音频端点中是否包含 'CABLE' 字样
        cmd = 'powershell -Command "Get-CimInstance Win32_SoundDevice | Select-Object -Property Name"'
        output = subprocess.check_output(cmd, shell=True, text=True)
        return "VB-Audio Virtual" in output or "CABLE" in output
    except Exception:
        return False
    

def uninstall_vb_cable():
    """静默卸载 VB-Cable 虚拟声卡"""
    setup_path = r"C:\Program Files\VB\CABLE\VBCABLE_Setup_x64.exe"
    
    if not os.path.exists(setup_path):
        return False, "未找到卸载程序，可能已被手动卸载。"
    
    try:
        # 【修改】去掉 check=True，手动判断状态码
        # 卸载程序返回 1 或 2 通常代表“成功，但需要重启电脑”
        process = subprocess.run([setup_path, "-u", "-h"], check=False)
        
        if process.returncode in [0, 1, 2]:
            return True, "卸载成功！"
        else:
            return False, f"卸载程序返回了异常状态码: {process.returncode}"
    except Exception as e:
        return False, f"卸载时发生异常: {str(e)}"

# ==========================================
# 1. Flask & SocketIO 初始化
# ==========================================
# 指定前端文件的目录
WEBUI_DIR = os.path.join(base_path, 'webui')
app = Flask(__name__, static_folder=WEBUI_DIR, static_url_path='')
app.config['SECRET_KEY'] = 'webmic-super-secret-key'

# 允许跨域，方便局域网设备连接
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

def get_lan_ip():
    """获取本机在局域网内的 IPv4 地址"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # 并不需要真正连通，只是为了获取路由网卡 IP
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

# ==========================================
# 2. 路由配置 (页面托管)
# ==========================================
@app.route('/')
def index():
    """手机端访问首页"""
    return send_from_directory(WEBUI_DIR, 'index.html')

@app.route('/api/uninstall_driver', methods=['POST'])
def api_uninstall_driver():
    """前端触发卸载的 API 接口"""
    success, msg = uninstall_vb_cable()
    return jsonify({"success": success, "msg": msg})

@app.route('/api/exit', methods=['POST'])
def api_exit():
    """接收到前端信号后，延迟 1 秒强行关闭整个程序"""
    def kill_me():
        time.sleep(1) # 给前端留 1 秒时间渲染"再见"的动画
        os._exit(0)   # 物理层面的无痛死亡
    threading.Thread(target=kill_me).start()
    return jsonify({"success": True})

@app.route('/desktop')
def desktop():
    """电脑 pywebview 访问接收页"""
    return send_from_directory(WEBUI_DIR, 'desktop.html')

@app.route('/api/info')
def api_info():
    """让前端获取系统信息、版本号以及局域网 IP"""
    return jsonify({
        "ip": get_lan_ip(), 
        "port": 5000,
        "version": VERSION
    })

@app.route('/api/check_driver', methods=['GET'])
def api_check_driver():
    """检查系统是否已安装虚拟声卡"""
    return jsonify({"installed": check_virtual_cable_installed()})

@app.route('/api/install_driver', methods=['POST'])
def api_install_driver():
    """前端触发的自动化安装 API"""
    if check_virtual_cable_installed():
        return jsonify({"success": True, "msg": "虚拟声卡已安装"})

    if not is_admin():
        return jsonify({"success": False, "msg": "权限不足，请关闭程序后，右键选择「以管理员身份运行」。"})

    try:
        download_url = "https://x19.fp.ps.netease.com/file/69f5f04aa4b381a43364a834LmYUuSiN07"
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, "vbcable.zip")
        
        # 1. 下载
        req = urllib.request.Request(download_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open(zip_path, 'wb') as out_file:
            out_file.write(response.read())

        # 2. 解压
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # 3. 静默安装
        setup_exe = os.path.join(temp_dir, "VBCABLE_Setup_x64.exe")
        subprocess.run([setup_exe, "-i", "-h"], check=True)
        
        return jsonify({"success": True, "msg": "安装成功！"})

    except Exception as e:
        return jsonify({"success": False, "msg": f"安装异常: {str(e)}"})

# ==========================================
# 3. WebRTC 信令服务器逻辑 (Socket.IO)
# ==========================================
# 这部分仅仅负责让手机和电脑“互相认识” (交换 SDP 和 ICE 候选)
# 一旦握手成功，音频数据就走 P2P 直连了，不经过服务器

@socketio.on('join')
def on_join(data):
    role = data.get('role', 'unknown')
    print(f"[{role}] 已连接到信令服务器")
    # 通知房间内的其他人（电脑/手机）准备连接
    emit('ready', {'role': role}, broadcast=True, include_self=False)

@socketio.on('offer')
def on_offer(data):
    # 手机发出 Offer，转发给电脑
    emit('offer', data, broadcast=True, include_self=False)

@socketio.on('answer')
def on_answer(data):
    # 电脑回复 Answer，转发给手机
    emit('answer', data, broadcast=True, include_self=False)

@socketio.on('ice_candidate')
def on_ice_candidate(data):
    # 转发网络穿透候选数据
    emit('ice_candidate', data, broadcast=True, include_self=False)



# 忽略证书错误的 Hack (针对 WebView2)
os.environ['WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS'] = (
    '--ignore-certificate-errors '               # 忽略 HTTPS 证书警告
    '--use-fake-ui-for-media-stream '            # 自动静默允许麦克风权限，绝不弹窗！
    '--autoplay-policy=no-user-gesture-required' # 允许音频自动播放，无需用户先点击页面
)


def start_flask():
    lan_ip = get_lan_ip()
    print(f"\n=========================================")
    print(f"ZeroMic 服务端已启动！")
    print(f"手机请访问: https://{lan_ip}:5000")
    print(f"=========================================\n")
    

    socketio.run(app, host='0.0.0.0', port=5000, ssl_context='adhoc', debug=False, use_reloader=False)

if __name__ == '__main__':
    # 启动 Flask 线程
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()
    
    # 创建无边框窗口
    window_obj = webview.create_window(
        title='ZeroMic Desktop',
        url='https://127.0.0.1:5000/desktop', 
        width=380,
        height=740,
        resizable=False,
        frameless=False,       
        easy_drag=False,      
        background_color='#121212'
    )


    # 强制使用 EdgeChromium，彻底禁用 fallback
    icon_path = os.path.join(os.path.dirname(__file__), 'icon.ico')
    webview.start(gui='edgechromium', debug=False, icon=icon_path)