"""Pinwala web server. Tonight: health check + placeholder page only; features come after kickoff."""
from __future__ import annotations

import logging
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from . import config  # noqa: F401  (loads .env)

logging.basicConfig(level=logging.INFO)

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(os.getenv("DATA_DIR", ROOT / "data"))
DATA.mkdir(parents=True, exist_ok=True)

KEYS = ("GEMINI_API_KEY", "SARVAM_API_KEY", "GOOGLE_PLACES_API_KEY", "TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN")

app = FastAPI(title="Pinwala")


@app.get("/api/health")
def health():
    # Reports which keys are configured (never their values), so a deploy can be checked at a glance.
    return {"ok": True, "keys": {k: bool(os.getenv(k)) for k in KEYS}}


app.mount("/", StaticFiles(directory=ROOT / "static", html=True), name="static")
