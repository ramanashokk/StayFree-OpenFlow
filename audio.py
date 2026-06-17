"""
Audio capture — records from mic while hotkey is held, returns numpy array.
"""

import numpy as np
import sounddevice as sd
import threading
from config import Config


class AudioRecorder:
    def __init__(self, config: Config):
        self.config = config
        self._frames = []
        self._recording = False
        self._lock = threading.Lock()

    def start(self):
        """Begin capturing audio from the microphone."""
        with self._lock:
            if self._recording:
                return
            self._frames = []
            self._recording = True

        device = None if self.config.device_index == -1 else self.config.device_index

        self._stream = sd.InputStream(
            samplerate=self.config.sample_rate,
            channels=self.config.channels,
            dtype="float32",
            device=device,
            callback=self._callback,
        )
        self._stream.start()
        print("[OpenFlow] Recording...")

    def _callback(self, indata, frames, time, status):
        if status:
            print(f"[OpenFlow] Audio status: {status}")
        if self._recording:
            self._frames.append(indata.copy())

    def stop(self) -> np.ndarray | None:
        """Stop recording and return audio as a flat float32 numpy array."""
        with self._lock:
            if not self._recording:
                return None
            self._recording = False

        try:
            self._stream.stop()
            self._stream.close()
        except Exception as e:
            print(f"[OpenFlow] Stream close error: {e}")

        if not self._frames:
            return None

        audio = np.concatenate(self._frames, axis=0).flatten()
        duration = len(audio) / self.config.sample_rate
        print(f"[OpenFlow] Captured {duration:.1f}s of audio")

        # Ignore very short recordings (likely accidental key presses)
        if duration < 0.5:
            print("[OpenFlow] Too short, ignoring")
            return None

        return audio

    @staticmethod
    def list_devices():
        """Print available audio input devices."""
        print(sd.query_devices())
