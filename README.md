# Pinwala

A shop owner sends one photo and one voice note, in his own language, and gets back a ready Google listing, his first posts, and a voice reply in his language. Built for AI Builders Day '26 (Track 2, Commerce).

Stack: FastAPI + vanilla JS, Docker on Render. Gemini (audio + vision), Sarvam (Indian-language speech), Google Places API (New), Twilio WhatsApp sandbox.

## Run locally

```bash
/opt/homebrew/bin/python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env    # then fill in keys
.venv/bin/uvicorn app.main:app --port 8000 --reload --reload-dir app
```

`/api/health` shows which keys are configured (true/false only).

## Night-before checks

```bash
.venv/bin/python scripts/check_keys.py    # PASS/FAIL/SKIP per API
.venv/bin/python scripts/stt_test.py      # Gemini vs Sarvam on samples/*
```

## Deploy (Render)

Push to GitHub, then on Render: New → Blueprint → pick the repo (reads `render.yaml`). Fill in the secret env vars, then set `PUBLIC_BASE_URL` to the Render URL once it exists (Twilio needs it to fetch the voice reply).

## Build order (24 Oct)

1. Core flow: `/intake` takes photo + voice, returns a listing (JSON) and the Maps-style card
2. Places check: already listed? competitors within 1 km
3. WhatsApp via Twilio + voice reply (Sarvam Bulbul)
4. Content Studio: posts, Instagram caption, WhatsApp Status, review replies
5. Rival Watch / heatmap (stretch)
6. Pine Labs receipt QR → Google review link
