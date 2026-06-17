# StayFree OpenFlow 🎙️

> AI-powered voice dictation. Free forever. No subscriptions.

A full-featured Wispr Flow alternative — built as a single HTML file, deployable anywhere, with zero backend. Your API key stays in your browser. No server, no tracking, no paywalls.

---

## Features

- **Voice dictation** — Click mic or hold `Space` to record, release to transcribe
- **Groq Whisper** (`whisper-large-v3`) — Same engine pros use, free tier is very generous
- **Browser speech fallback** — Works without any API key via Web Speech API
- **AI post-processing** — 4 modes: Clean up · Bullet points · Email draft · Raw transcript
- **Floating mic widget** — Always-visible overlay, Wispr-style
- **AI Rewrite tool** — Paste any text, rewrite in 5 styles
- **Paste & Clean** — Dump messy notes, get structured output
- **History** — All transcriptions saved locally in browser (up to 200 items)
- **Dark / Light mode**
- **Language selector** — EN, HI, ES, FR, DE, ZH, AR, PT, JA, Auto-detect
- **Model selector** — Llama 3.3 70B, Llama 3.1 8B, Mixtral 8x7B, Gemma 2 9B
- **Installable PWA** — Add to home screen on Android/iOS/Desktop

---

## Live Demo

👉 **[ramanashokk.github.io/StayFree-OpenFlow](https://ramanashokk.github.io/StayFree-OpenFlow)**

---

## Setup

### 1. Get a free Groq API key

Sign up at [console.groq.com](https://console.groq.com) — free tier includes:
- **6,000 requests/minute** for Whisper transcription
- **Generous limits** for LLaMA / Mixtral cleanup

### 2. Add your key in the app

Open the app → ⚙️ Settings → Groq API Key → paste your key → Save.

The key is stored only in your browser's `localStorage`. It never leaves your device.

### 3. Use it

| Action | How |
|---|---|
| Start recording | Click 🎙️ or hold `Space` |
| Stop recording | Click again or release `Space` |
| Cancel | `Escape` |
| Copy result | `📋 Copy` button or auto-copy toggle |

---

## Deploy Your Own

### GitHub Pages (simplest)

```bash
git clone https://github.com/ramanashokk/StayFree-OpenFlow
cd stayfree-openflow
# drop your index.html + manifest.json here
git add .
git commit -m "deploy"
git push
```

Then: **Settings → Pages → Branch: main → Save**

Live at `https://ramanashokk.github.io/StayFree-OpenFlow`

### Netlify / Vercel

Drag and drop the `index.html` file into [netlify.com/drop](https://netlify.com/drop) — live in 10 seconds.

---

## File Structure

```
stayfree-openflow/
├── index.html       ← Entire app (single file, no dependencies)
├── manifest.json    ← PWA manifest (installable)
├── icon-192.png     ← App icon (add your own)
├── icon-512.png     ← App icon (add your own)
└── README.md
```

---

## Tech Stack

| Layer | What |
|---|---|
| Transcription | Groq Whisper Large v3 |
| AI cleanup | Groq LLaMA 3.3 70B / Mixtral / Gemma |
| Frontend | Vanilla HTML + CSS + JS (zero dependencies) |
| Storage | Browser `localStorage` |
| Hosting | GitHub Pages |

No Node.js. No build step. No npm install. Open the HTML file and it works.

---

## Privacy

- **Your audio** is sent to Groq's API for transcription (see [groq.com/privacy](https://groq.com/privacy))
- **Your API key** is stored only in your browser, never on any server
- **Your transcriptions** are stored only in your browser's localStorage
- **This app** has no analytics, no telemetry, no ads

---

## Part of the StayFree ecosystem

| Product | Description | Status |
|---|---|---|
| [StayFree Text](https://ramanashokk.github.io/Stayfree) | Voice dictation with premium tier | Live |
| [**StayFree OpenFlow**](https://ramanashokk.github.io/StayFree-OpenFlow) | Voice dictation, fully free | Live |

---

## License

MIT — use it, fork it, deploy it, sell it. No restrictions.

---

*Built by [@ramanashokk](https://github.com/ramanashokk)*
