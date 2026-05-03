class BasePlatform:
    """平台抽象基类，定义各平台必须实现的接口。"""

    @property
    def use_system_browser(self) -> bool:
        """True 表示用系统浏览器打开桌面页面，False 表示用 pywebview 内嵌窗口。"""
        return False

    @property
    def gui_backend(self) -> str | None:
        """pywebview 的 gui 参数。None 表示自动检测。"""
        return None

    @property
    def driver_display_name(self) -> str:
        """前端 UI 中显示的虚拟设备名称。"""
        raise NotImplementedError

    @property
    def driver_match_keyword(self) -> str:
        """在前端 enumerateDevices 中匹配设备的关键词（小写）。"""
        raise NotImplementedError

    def get_webview_env(self) -> dict[str, str]:
        """启动 pywebview 前需要设置的环境变量。"""
        return {}

    def is_admin(self) -> bool:
        raise NotImplementedError

    def is_driver_installed(self) -> bool:
        raise NotImplementedError

    def install_driver(self) -> tuple[bool, str]:
        """返回 (成功, 消息)"""
        raise NotImplementedError

    def uninstall_driver(self) -> tuple[bool, str]:
        """返回 (成功, 消息)"""
        raise NotImplementedError

    def get_post_install_warning(self) -> str:
        """驱动安装后的提醒文案。"""
        return ""
