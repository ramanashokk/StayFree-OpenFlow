"""
Text injection — pastes transcribed text into the currently focused app.

Strategies:
  clipboard  — saves clipboard, copies text, Cmd/Ctrl+V, restores clipboard
  xdotool    — Linux only, uses xdotool type (more reliable in some apps)
"""

import sys
import time
import threading
import pyperclip
import pyautogui
from config import Config


class TextInjector:
    def __init__(self, config: Config):
        self.config = config
        self._lock = threading.Lock()

    def inject(self, text: str):
        with self._lock:
            method = self.config.injection_method
            if method == "xdotool" and sys.platform == "linux":
                self._inject_xdotool(text)
            else:
                self._inject_clipboard(text)

    def _inject_clipboard(self, text: str):
        """Save clipboard → copy text → paste → restore clipboard."""
        try:
            previous = pyperclip.paste()
        except Exception:
            previous = ""

        try:
            pyperclip.copy(text)
            time.sleep(self.config.paste_delay_ms / 1000)

            if sys.platform == "darwin":
                pyautogui.hotkey("command", "v")
            else:
                pyautogui.hotkey("ctrl", "v")

            # Give paste time to complete before restoring
            time.sleep(0.05)
        finally:
            try:
                if previous:
                    pyperclip.copy(previous)
            except Exception:
                pass

    def _inject_xdotool(self, text: str):
        """Use xdotool for direct key typing on Linux."""
        import subprocess
        # Escape special chars for xdotool
        safe = text.replace("'", r"\'")
        subprocess.run(
            ["xdotool", "type", "--clearmodifiers", "--delay", "0", "--", text],
            check=False,
        )
