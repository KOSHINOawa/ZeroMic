import ctypes
import subprocess
import os
import urllib.request
import zipfile
import tempfile


class WindowsPlatform:
    @property
    def gui_backend(self) -> str:
        return 'edgechromium'

    @property
    def driver_display_name(self) -> str:
        return 'CABLE Output (VB-Audio Virtual Cable)'

    @property
    def driver_match_keyword(self) -> str:
        return 'cable input'

    def get_webview_env(self) -> dict[str, str]:
        return {
            'WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS': (
                '--ignore-certificate-errors '
                '--use-fake-ui-for-media-stream '
                '--autoplay-policy=no-user-gesture-required'
            ),
        }

    def is_admin(self) -> bool:
        try:
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        except Exception:
            return False

    def is_driver_installed(self) -> bool:
        try:
            cmd = 'powershell -Command "Get-CimInstance Win32_SoundDevice | Select-Object -Property Name"'
            output = subprocess.check_output(cmd, shell=True, text=True)
            return 'VB-Audio Virtual' in output or 'CABLE' in output
        except Exception:
            return False

    def install_driver(self) -> tuple[bool, str]:
        if self.is_driver_installed():
            return True, '虚拟声卡已安装'

        if not self.is_admin():
            return False, '权限不足，请关闭程序后，右键选择「以管理员身份运行」。'

        try:
            download_url = 'https://x19.fp.ps.netease.com/file/69f5f04aa4b381a43364a834LmYUuSiN07'
            temp_dir = tempfile.mkdtemp()
            zip_path = os.path.join(temp_dir, 'vbcable.zip')

            req = urllib.request.Request(download_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response, open(zip_path, 'wb') as out_file:
                out_file.write(response.read())

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            setup_exe = os.path.join(temp_dir, 'VBCABLE_Setup_x64.exe')
            subprocess.run([setup_exe, '-i', '-h'], check=True)

            return True, '安装成功！'
        except Exception as e:
            return False, f'安装异常: {str(e)}'

    def uninstall_driver(self) -> tuple[bool, str]:
        setup_path = r'C:\Program Files\VB\CABLE\VBCABLE_Setup_x64.exe'

        if not os.path.exists(setup_path):
            return False, '未找到卸载程序，可能已被手动卸载。'

        try:
            process = subprocess.run([setup_path, '-u', '-h'], check=False)
            if process.returncode in [0, 1, 2]:
                return True, '卸载成功！'
            else:
                return False, f'卸载程序返回了异常状态码: {process.returncode}'
        except Exception as e:
            return False, f'卸载时发生异常: {str(e)}'

    def get_post_install_warning(self) -> str:
        return ('Windows 可能已自动将默认播放设备切换为 CABLE Input，'
                '导致电脑暂时没有声音。\n'
                '请点击电脑右下角的喇叭图标，手动将播放设备切换回原来的扬声器。')
