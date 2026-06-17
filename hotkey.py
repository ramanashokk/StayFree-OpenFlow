"""
Hotkey listener — detects hold/release of the configured key globally,
across all apps, using pynput.
"""

import threading
from pynput import keyboard
from config import Config


# Map friendly names → pynput Key objects
KEY_MAP = {
    "shift_r": keyboard.Key.shift_r,
    "shift_l": keyboard.Key.shift_l,
    "ctrl_r": keyboard.Key.ctrl_r,
    "ctrl_l": keyboard.Key.ctrl_l,
    "alt_r": keyboard.Key.alt_r,
    "alt_l": keyboard.Key.alt_l,
    "cmd": keyboard.Key.cmd,
    "f1": keyboard.Key.f1,
    "f2": keyboard.Key.f2,
    "f13": keyboard.Key.f13,
    "f14": keyboard.Key.f14,
    "f15": keyboard.Key.f15,
    "caps_lock": keyboard.Key.caps_lock,
}


class HotkeyListener:
    def __init__(self, key: str, on_press, on_release):
        self.target_key = KEY_MAP.get(key, keyboard.Key.shift_r)
        self._on_press = on_press
        self._on_release = on_release
        self._held = False
        self._listener = None

    def _handle_press(self, key):
        if key == self.target_key and not self._held:
            self._held = True
            try:
                self._on_press()
            except Exception as e:
                print(f"[OpenFlow] Press handler error: {e}")

    def _handle_release(self, key):
        if key == self.target_key and self._held:
            self._held = False
            try:
                self._on_release()
            except Exception as e:
                print(f"[OpenFlow] Release handler error: {e}")

    def start(self):
        self._listener = keyboard.Listener(
            on_press=self._handle_press,
            on_release=self._handle_release,
        )
        self._listener.start()

    def stop(self):
        if self._listener:
            self._listener.stop()

    @property
    def is_active(self):
        return self._listener is not None and self._listener.is_alive()
