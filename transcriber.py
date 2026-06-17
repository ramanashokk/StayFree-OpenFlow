"""
Transcription — converts audio to text using faster-whisper (local, offline).
Optionally runs AI cleanup to remove filler words and fix punctuation.
"""

import numpy as np
from config import Config


FILLER_WORDS = {
    "um", "uh", "ah", "er", "hmm", "like", "you know", "i mean",
    "sort of", "kind of", "basically", "literally", "actually",
    "right", "okay so", "so yeah",
}

CLEANUP_PROMPT = """You are a transcription cleanup assistant. 
Fix the following raw speech transcription:
- Remove filler words (um, uh, ah, like, you know, etc.)
- Fix punctuation and capitalization
- Fix obvious transcription errors
- Preserve the original meaning and all content exactly
- Do NOT summarize or rephrase — only clean up
- Return ONLY the cleaned text, nothing else.

Raw transcription:
{text}"""


class Transcriber:
    def __init__(self, config: Config):
        self.config = config
        self._model = None
        self._load_model()

    def _load_model(self):
        print(f"[OpenFlow] Loading Whisper model '{self.config.model}'...")
        try:
            from faster_whisper import WhisperModel
            device = self.config.device
            if device == "auto":
                try:
                    import torch
                    device = "cuda" if torch.cuda.is_available() else "cpu"
                except ImportError:
                    device = "cpu"

            self._model = WhisperModel(
                self.config.model,
                device=device,
                compute_type=self.config.compute_type,
            )
            print(f"[OpenFlow] Whisper ready on {device}")
        except ImportError:
            print("[OpenFlow] faster-whisper not installed. Run: pip install faster-whisper")
            self._model = None

    def transcribe(self, audio: np.ndarray) -> str:
        if self._model is None:
            return ""

        segments, info = self._model.transcribe(
            audio,
            language=self.config.language if self.config.language != "auto" else None,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500),
        )

        text = " ".join(seg.text.strip() for seg in segments).strip()
        print(f"[OpenFlow] Raw: {text!r}")

        if not text:
            return ""

        if self.config.ai_cleanup_enabled and self.config.ai_api_key:
            text = self._ai_cleanup(text)
        elif self.config.remove_fillers:
            text = self._basic_cleanup(text)

        print(f"[OpenFlow] Final: {text!r}")
        return text

    def _basic_cleanup(self, text: str) -> str:
        """Simple filler-word removal without an API call."""
        import re
        words = text.lower().split()
        cleaned = [w for w in text.split() if w.lower().strip(",.!?") not in FILLER_WORDS]
        result = " ".join(cleaned)
        # Collapse multiple spaces
        result = re.sub(r" +", " ", result).strip()
        return result

    def _ai_cleanup(self, text: str) -> str:
        """Use an LLM to clean up the transcription."""
        try:
            if self.config.ai_provider == "openai":
                return self._cleanup_openai(text)
            elif self.config.ai_provider == "anthropic":
                return self._cleanup_anthropic(text)
        except Exception as e:
            print(f"[OpenFlow] AI cleanup failed: {e} — using raw text")
        return text

    def _cleanup_openai(self, text: str) -> str:
        from openai import OpenAI
        client = OpenAI(api_key=self.config.ai_api_key)
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": CLEANUP_PROMPT.format(text=text)}],
            max_tokens=1000,
            temperature=0.1,
        )
        return resp.choices[0].message.content.strip()

    def _cleanup_anthropic(self, text: str) -> str:
        import anthropic
        client = anthropic.Anthropic(api_key=self.config.ai_api_key)
        resp = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1000,
            messages=[{"role": "user", "content": CLEANUP_PROMPT.format(text=text)}],
        )
        return resp.content[0].text.strip()
