"""
Configuration — reads from ~/.openflow/config.toml, falls back to defaults.
"""

import os
import tomllib
from pathlib import Path
from dataclasses import dataclass, field
from typing import Literal


CONFIG_DIR = Path.home() / ".openflow"
CONFIG_FILE = CONFIG_DIR / "config.toml"

DEFAULT_CONFIG = """
# OpenFlow Configuration
# Edit this file and restart OpenFlow to apply changes.

[general]
hotkey = "shift_r"          # Key to hold while speaking
language = "en"             # Transcription language (e.g. "en", "es", "hi", "zh")
sound_feedback = true       # Play a sound when recording starts/stops

[transcription]
model = "base"              # Whisper model: tiny, base, small, medium, large-v3
device = "auto"             # "cpu", "cuda", or "auto"
compute_type = "int8"       # "int8", "float16", "float32"

[ai_cleanup]
enabled = true              # Run AI cleanup (remove fillers, fix punctuation)
provider = "openai"         # "openai", "anthropic", or "none"
# api_key = ""              # Uncomment and set your key (or use env var)
remove_fillers = true       # Remove "um", "uh", "like", etc.
fix_punctuation = true      # Auto-punctuate sentences

[audio]
sample_rate = 16000
channels = 1
device_index = -1           # -1 = system default microphone

[injection]
method = "clipboard"        # "clipboard" or "xdotool" (Linux only)
paste_delay_ms = 50         # Delay before paste (increase if injection is unreliable)
"""


@dataclass
class Config:
    # General
    hotkey: str = "shift_r"
    language: str = "en"
    sound_feedback: bool = True

    # Transcription
    model: str = "base"
    device: str = "auto"
    compute_type: str = "int8"

    # AI Cleanup
    ai_cleanup_enabled: bool = True
    ai_provider: str = "openai"
    ai_api_key: str = ""
    remove_fillers: bool = True
    fix_punctuation: bool = True

    # Audio
    sample_rate: int = 16000
    channels: int = 1
    device_index: int = -1

    # Injection
    injection_method: str = "clipboard"
    paste_delay_ms: int = 50

    def __post_init__(self):
        self._ensure_config_file()
        self._load()

    def _ensure_config_file(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        if not CONFIG_FILE.exists():
            CONFIG_FILE.write_text(DEFAULT_CONFIG)
            print(f"[OpenFlow] Created default config at {CONFIG_FILE}")

    def _load(self):
        try:
            with open(CONFIG_FILE, "rb") as f:
                data = tomllib.load(f)

            g = data.get("general", {})
            self.hotkey = g.get("hotkey", self.hotkey)
            self.language = g.get("language", self.language)
            self.sound_feedback = g.get("sound_feedback", self.sound_feedback)

            t = data.get("transcription", {})
            self.model = t.get("model", self.model)
            self.device = t.get("device", self.device)
            self.compute_type = t.get("compute_type", self.compute_type)

            a = data.get("ai_cleanup", {})
            self.ai_cleanup_enabled = a.get("enabled", self.ai_cleanup_enabled)
            self.ai_provider = a.get("provider", self.ai_provider)
            self.ai_api_key = a.get("api_key", "") or os.environ.get(
                "OPENAI_API_KEY" if self.ai_provider == "openai" else "ANTHROPIC_API_KEY", ""
            )
            self.remove_fillers = a.get("remove_fillers", self.remove_fillers)
            self.fix_punctuation = a.get("fix_punctuation", self.fix_punctuation)

            au = data.get("audio", {})
            self.sample_rate = au.get("sample_rate", self.sample_rate)
            self.channels = au.get("channels", self.channels)
            self.device_index = au.get("device_index", self.device_index)

            inj = data.get("injection", {})
            self.injection_method = inj.get("method", self.injection_method)
            self.paste_delay_ms = inj.get("paste_delay_ms", self.paste_delay_ms)

        except Exception as e:
            print(f"[OpenFlow] Config error: {e} — using defaults")
