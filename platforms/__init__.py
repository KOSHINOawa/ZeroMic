import sys


def get_platform():
    if sys.platform == 'win32':
        from .windows import WindowsPlatform
        return WindowsPlatform()
    elif sys.platform == 'linux':
        from .linux import LinuxPlatform
        return LinuxPlatform()
    elif sys.platform == 'darwin':
        from .macos import MacOSPlatform
        return MacOSPlatform()
    else:
        raise RuntimeError(f"不支持的操作系统: {sys.platform}")
