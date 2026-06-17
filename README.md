# OpenFlow 🎙️

**Free, open-source voice dictation for your entire computer.**

Hold a key → speak → release → text appears wherever your cursor is.

Works in any app: Notion, Gmail, Slack, VS Code, Terminal — anything with a text field.

---

## Features

- **Hold-to-talk** — hold `Right Shift` (configurable), speak, release
- **Local transcription** — powered by [faster-whisper](https://github.com/SYSTRAN/faster-whisper), runs 100% offline
- **AI cleanup** — optional LLM pass removes filler words, fixes punctuation (OpenAI or Anthropic)
- **Universal injection** — pastes into any focused app via clipboard
- **100+ languages** — anything Whisper supports
- **System tray** — lives quietly in your menubar/taskbar
- **No cloud required** — your voice never leaves your machine (unless you enable AI cleanup)

---

## Install

```bash
git clone https://github.com/yourusername/openflow
cd openflow
pip install -r requirements.txt
```

> **macOS:** You'll need to grant Accessibility and Microphone permissions in System Preferences.  
> **Linux:** You may need `sudo apt install xdotool` for xdotool injection mode.  
> **Windows:** Run as Administrator if hotkeys don't register.

---

## Run

```bash
python src/main.py
```

A tray icon appears. **Hold Right Shift to dictate.** Release to transcribe and inject.

---

## Configure

On first run, a config file is created at `~/.openflow/config.toml`. Right-click the tray icon → **Open Config** to edit it.

```toml
[general]
hotkey = "shift_r"       # Key to hold: shift_r, shift_l, ctrl_r, f13, caps_lock, ...
language = "en"          # Transcription language
sound_feedback = true

[transcription]
model = "base"           # tiny / base / small / medium / large-v3
device = "auto"          # cpu / cuda / auto
compute_type = "int8"

[ai_cleanup]
enabled = true
provider = "openai"      # openai / anthropic / none
# api_key = "sk-..."     # Or set OPENAI_API_KEY env var
remove_fillers = true
fix_punctuation = true

[audio]
device_index = -1        # -1 = default mic

[injection]
method = "clipboard"     # clipboard / xdotool (Linux)
paste_delay_ms = 50
```

### Model sizes

| Model    | Size  | Speed  | Accuracy |
|----------|-------|--------|----------|
| tiny     | 75MB  | ⚡⚡⚡⚡ | ★★☆☆☆   |
| base     | 145MB | ⚡⚡⚡  | ★★★☆☆   |
| small    | 460MB | ⚡⚡    | ★★★★☆   |
| medium   | 1.5GB | ⚡     | ★★★★☆   |
| large-v3 | 3GB   | 🐢     | ★★★★★   |

`base` is the best starting point. Use `large-v3` for maximum accuracy on a GPU.

---

## Privacy

- All transcription is local by default — nothing is sent anywhere
- AI cleanup is **opt-in** and requires your own API key
- No telemetry, no accounts, no subscriptions

---

## Roadmap

- [ ] Voice commands ("select all", "new line", "undo")
- [ ] Per-app context awareness (code mode, email mode)
- [ ] Custom vocabulary / word corrections
- [ ] GUI settings panel
- [ ] macOS/Windows installers

---

## Contributing

PRs welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## License

MIT
