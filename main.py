"""
OpenFlow - Open source voice dictation
Hold Right Shift to record. Release to transcribe and inject text.
"""

import threading
import queue
import sys
import signal
from audio import AudioRecorder
from transcriber import Transcriber
from injector import TextInjector
from hotkey import HotkeyListener
from tray import TrayApp
from config import Config


def main():
    config = Config()
    audio_recorder = AudioRecorder(config)
    transcriber = Transcriber(config)
    injector = TextInjector(config)
    audio_queue = queue.Queue()

    def on_recording_complete(audio_data):
        """Called when user releases hotkey — transcribe and inject."""
        audio_queue.put(audio_data)

    def transcription_worker():
        while True:
            audio_data = audio_queue.get()
            if audio_data is None:
                break
            try:
                text = transcriber.transcribe(audio_data)
                if text and text.strip():
                    injector.inject(text.strip())
            except Exception as e:
                print(f"[OpenFlow] Transcription error: {e}")
            finally:
                audio_queue.task_done()

    worker = threading.Thread(target=transcription_worker, daemon=True)
    worker.start()

    hotkey = HotkeyListener(
        key=config.hotkey,
        on_press=audio_recorder.start,
        on_release=lambda: on_recording_complete(audio_recorder.stop()),
    )

    tray = TrayApp(config, hotkey)

    def shutdown(sig=None, frame=None):
        print("\n[OpenFlow] Shutting down...")
        audio_queue.put(None)
        hotkey.stop()
        tray.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    print(f"[OpenFlow] Running. Hold {config.hotkey} to dictate.")
    hotkey.start()
    tray.run()  # blocks on main thread


if __name__ == "__main__":
    main()
