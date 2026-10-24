"""Compare Gemini (audio in, one call) vs Sarvam Saarika (speech-to-text) on real voice notes.

    .venv/bin/python scripts/stt_test.py                 # every audio file in samples/
    .venv/bin/python scripts/stt_test.py samples/bn_mishti_shop.ogg

Each file is converted to 16 kHz mono WAV with ffmpeg first (WhatsApp .opus and browser .webm
are not accepted everywhere). Results print side by side and are saved to scripts/out/.
Read the Bengali transcripts yourself: the question is which one gets the shop name,
area and hours right, not which one is faster.
"""
from __future__ import annotations

import base64
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from _http import post_json, post_multipart, short

ROOT = Path(__file__).resolve().parent.parent
AUDIO_EXT = {".ogg", ".opus", ".oga", ".m4a", ".mp3", ".wav", ".aac", ".webm", ".flac", ".mp4", ".amr"}
MAX_SECONDS = 30  # Sarvam's synchronous endpoint limit

PROMPT = """This is a voice note from a small shop owner in India describing their shop.
1. Transcribe it exactly, in the original script (Bengali in Bangla script, Hindi in Devanagari, etc.).
2. Give the BCP-47 language code (bn-IN, hi-IN, en-IN, kn-IN, ta-IN, ...). If they mix languages, give the main one.
3. Translate it to English.
4. Extract only what the speaker actually said. Use null for anything not said. Never guess."""

SCHEMA = {
    "type": "object",
    "properties": {
        "transcript": {"type": "string"},
        "language": {"type": "string"},
        "english": {"type": "string"},
        "shop_name": {"type": "string", "nullable": True},
        "what_they_sell": {"type": "string", "nullable": True},
        "area": {"type": "string", "nullable": True},
        "hours": {"type": "string", "nullable": True},
        "phone": {"type": "string", "nullable": True},
    },
    "required": ["transcript", "language", "english"],
}


def to_wav(src: Path) -> tuple[bytes, float]:
    with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-ac", "1", "-ar", "16000", tmp.name],
                       check=True)
        data = Path(tmp.name).read_bytes()
    return data, (len(data) - 44) / 32000  # 16-bit mono 16 kHz


def gemini(wav: bytes) -> dict:
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        return {"error": "GEMINI_API_KEY not set"}
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    t = time.time()
    st, body = post_json(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        {"contents": [{"parts": [{"text": PROMPT},
                                 {"inline_data": {"mime_type": "audio/wav", "data": base64.b64encode(wav).decode()}}]}],
         "generationConfig": {"responseMimeType": "application/json", "responseSchema": SCHEMA, "temperature": 0}},
        {"x-goog-api-key": key})
    secs = round(time.time() - t, 1)
    if st != 200:
        return {"error": f"HTTP {st}: {short(body)}", "seconds": secs}
    out = json.loads(body["candidates"][0]["content"]["parts"][0]["text"])
    return {**out, "seconds": secs, "model": model}


def sarvam(wav: bytes) -> dict:
    key = os.getenv("SARVAM_API_KEY")
    if not key:
        return {"error": "SARVAM_API_KEY not set"}
    model = os.getenv("SARVAM_STT_MODEL", "saarika:v2.5")
    t = time.time()
    st, body = post_multipart("https://api.sarvam.ai/speech-to-text",
                              {"model": model, "language_code": "unknown"},
                              {"file": ("note.wav", wav, "audio/wav")}, {"api-subscription-key": key})
    secs = round(time.time() - t, 1)
    if st != 200:
        return {"error": f"HTTP {st}: {short(body)}", "seconds": secs}
    return {"transcript": body.get("transcript"), "language": body.get("language_code"), "seconds": secs,
            "model": model}


def show(label: str, r: dict):
    print(f"  {label}")
    if "error" in r:
        print(f"    ERROR  {r['error']}")
        return
    print(f"    {r.get('seconds')} s · {r.get('language')} · {r.get('model')}")
    print(f"    {r.get('transcript')}")
    if r.get("english"):
        print(f"    EN: {r['english']}")
    fields = {k: r.get(k) for k in ("shop_name", "what_they_sell", "area", "hours", "phone") if k in r}
    if fields:
        print("    " + " | ".join(f"{k}={v}" for k, v in fields.items()))


def main(args: list[str]):
    files = [Path(a) for a in args] or sorted(p for p in (ROOT / "samples").iterdir()
                                              if p.suffix.lower() in AUDIO_EXT)
    if not files:
        sys.exit("No audio found. Put voice notes in samples/ (see samples/README.md) or pass file paths.")
    results = []
    for f in files:
        print(f"\n=== {f.name}")
        try:
            wav, dur = to_wav(f)
        except subprocess.CalledProcessError:
            print("  ffmpeg could not read this file, skipped")
            continue
        if dur > MAX_SECONDS:
            print(f"  {dur:.0f} s is over {MAX_SECONDS} s; trim it (owners' notes will be short anyway)")
            continue
        g, s = gemini(wav), sarvam(wav)
        show("Gemini (audio → transcript + fields in one call)", g)
        show("Sarvam Saarika (transcript only)", s)
        results.append({"file": f.name, "seconds_audio": round(dur, 1), "gemini": g, "sarvam": s})
    out = ROOT / "scripts" / "out"
    out.mkdir(exist_ok=True)
    path = out / f"stt_{time.strftime('%Y%m%d_%H%M%S')}.json"
    path.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(f"\nSaved {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main(sys.argv[1:])
