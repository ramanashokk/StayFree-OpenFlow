# Contributing to OpenFlow

Thanks for helping! Here's how to get started.

## Setup

```bash
git clone https://github.com/yourusername/openflow
cd openflow
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python src/main.py
```

## Project structure

```
openflow/
├── src/
│   ├── main.py          # Entry point, wires everything together
│   ├── audio.py         # Mic capture (sounddevice)
│   ├── transcriber.py   # Whisper transcription + AI cleanup
│   ├── injector.py      # Paste text into focused app
│   ├── hotkey.py        # Global key listener (pynput)
│   ├── tray.py          # System tray icon (pystray)
│   └── config.py        # Config file loading (~/.openflow/config.toml)
├── requirements.txt
├── README.md
└── CONTRIBUTING.md
```

## Good first issues

- Add sound feedback on record start/stop (a short beep via `sounddevice`)
- Add `--list-devices` CLI flag
- Test and document Windows-specific setup steps
- Add support for the `f13`/`f14` keys as hotkeys (popular with StreamDecks)
- Write a setup.py / pyproject.toml for pip install

## Guidelines

- Keep dependencies minimal
- Core transcription must stay offline-capable
- Don't break the hold-to-talk UX — it must be instant
- Test on at least one platform before PRing
