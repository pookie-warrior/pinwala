"""Ping every API the build needs and say PASS / FAIL / SKIP for each. Never prints key values.

    .venv/bin/python scripts/check_keys.py
"""
from __future__ import annotations

import io
import os
import wave

from _http import basic_auth, call, post_json, post_multipart, short


def gemini():
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        return "SKIP", "GEMINI_API_KEY not set"
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    st, body = post_json(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                         {"contents": [{"parts": [{"text": "Reply with the single word: ok"}]}]},
                         {"x-goog-api-key": key}, timeout=30)
    if st == 200:
        return "PASS", f"{model} answered"
    hint = " (model name may be retired: set GEMINI_MODEL)" if st == 404 else ""
    return "FAIL", f"HTTP {st}: {short(body)}{hint}"


def places():
    key = os.getenv("GOOGLE_PLACES_API_KEY")
    if not key:
        return "SKIP", "GOOGLE_PLACES_API_KEY not set"
    st, body = post_json("https://places.googleapis.com/v1/places:searchText",
                         {"textQuery": "bakery in Jayanagar 4th Block, Bengaluru", "pageSize": 3},
                         {"X-Goog-Api-Key": key, "X-Goog-FieldMask": "places.id,places.displayName"}, timeout=30)
    if st == 200:
        names = [p["displayName"]["text"] for p in body.get("places", [])]
        return "PASS", f"found {len(names)}: {', '.join(names)}"
    return "FAIL", (f"HTTP {st}: {short(body)}  (check: Places API (New) enabled, billing on, "
                    "key not restricted to other APIs)")


def sarvam():
    key = os.getenv("SARVAM_API_KEY")
    if not key:
        return "SKIP", "SARVAM_API_KEY not set"
    buf = io.BytesIO()  # 1 s of silence is enough to prove auth + endpoint
    with wave.open(buf, "wb") as w:
        w.setnchannels(1), w.setsampwidth(2), w.setframerate(16000), w.writeframes(b"\0\0" * 16000)
    st, body = post_multipart("https://api.sarvam.ai/speech-to-text",
                              {"model": os.getenv("SARVAM_STT_MODEL", "saarika:v2.5"), "language_code": "unknown"},
                              {"file": ("silence.wav", buf.getvalue(), "audio/wav")},
                              {"api-subscription-key": key}, timeout=30)
    if st == 200:
        return "PASS", "speech-to-text endpoint answered"
    return "FAIL", f"HTTP {st}: {short(body)}"


def twilio():
    sid, tok = os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN")
    if not (sid and tok):
        return "SKIP", "TWILIO_ACCOUNT_SID / TWILIO_AUTH_TOKEN not set"
    st, body = call(f"https://api.twilio.com/2010-04-01/Accounts/{sid}.json",
                    headers={"Authorization": basic_auth(sid, tok)}, timeout=30)
    if st == 200:
        return "PASS", f"account status: {body.get('status')}"
    return "FAIL", f"HTTP {st}: {short(body)}"


if __name__ == "__main__":
    for name, fn in (("Gemini", gemini), ("Places", places), ("Sarvam", sarvam), ("Twilio", twilio)):
        try:
            verdict, note = fn()
        except Exception as e:  # network/DNS errors should not hide the other checks
            verdict, note = "FAIL", f"{type(e).__name__}: {e}"
        print(f"{verdict:4}  {name:7} {note}")
