"""
System tray icon with right-click menu.
Uses pystray for cross-platform tray support.
"""

import sys
import threading
import subprocess
from pathlib import Path
from config import Config, CONFIG_FILE


try:
    import pystray
    from PIL import Image, ImageDraw
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False


def _create_icon_image(active=False):
    """Draw a simple mic icon as the tray image."""
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    color = (80, 200, 120) if active else (60, 60, 60)

    # Mic body
    draw.rounded_rectangle([20, 8, 44, 38], radius=10, fill=color)
    # Mic stand
    draw.arc([14, 26, 50, 52], start=0, end=180, fill=color, width=4)
    draw.line([32, 52, 32, 58], fill=color, width=4)
    draw.line([22, 58, 42, 58], fill=color, width=4)

    return img


class TrayApp:
    def __init__(self, config: Config, hotkey):
        self.config = config
        self.hotkey = hotkey
        self._icon = None
        self._enabled = True

    def _build_menu(self):
        if not TRAY_AVAILABLE:
            return None

        return pystray.Menu(
            pystray.MenuItem(
                f"Hold {self.config.hotkey.replace('_', ' ').title()} to dictate",
                None,
                enabled=False,
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Open Config", self._open_config),
            pystray.MenuItem("List Audio Devices", self._list_devices),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit OpenFlow", self._quit),
        )

    def _open_config(self, icon=None, item=None):
        if sys.platform == "darwin":
            subprocess.run(["open", str(CONFIG_FILE)])
        elif sys.platform == "win32":
            subprocess.run(["notepad", str(CONFIG_FILE)])
        else:
            editors = ["xdg-open", "gedit", "nano"]
            for ed in editors:
                try:
                    subprocess.Popen([ed, str(CONFIG_FILE)])
                    break
                except FileNotFoundError:
                    continue

    def _list_devices(self, icon=None, item=None):
        from audio import AudioRecorder
        AudioRecorder.list_devices()

    def _quit(self, icon=None, item=None):
        if self._icon:
            self._icon.stop()

    def run(self):
        if not TRAY_AVAILABLE:
            print("[OpenFlow] pystray/Pillow not installed — no tray icon. Press Ctrl+C to quit.")
            # Block main thread
            import signal
            signal.pause()
            return

        self._icon = pystray.Icon(
            "openflow",
            _create_icon_image(),
            "OpenFlow",
            self._build_menu(),
        )
        self._icon.run()

    def stop(self):
        if self._icon:
            self._icon.stop()
