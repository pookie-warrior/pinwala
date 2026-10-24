# Pinwala

Get your shop found on Google. A shop owner says whether he's already on Google Maps, finds his shop or drops a pin, sees his rivals instantly, talks to a voice agent for two minutes, approves the result, and pays ₹99 to have his Google profile prepared (new shops) or get a competitor report and fixes (existing shops). A Pinwala reviewer approves every profile in AgenticOrg before anything is done in the owner's name.

Built for AI Builders Day '26, Track 2 · AI for Commerce. Repo: `pookie-warrior/pinwala` (private).

**Start here:** [docs/PRD.md](docs/PRD.md) (scope, timeline, architecture) · [docs/USER_JOURNEY.md](docs/USER_JOURNEY.md) (frozen journey v2) · [docs/HANDOFF.md](docs/HANDOFF.md) (status and next steps)

## Stack

| Piece | Choice |
| --- | --- |
| Web app | Python 3.12 FastAPI + vanilla JS, mobile-first, hosted on Replit |
| Find shop / rivals | Google Places API (New) |
| Voice agent | ElevenLabs agent + web SDK |
| Photo reading | Sarvam Document AI (Extract) |
| Orchestration | n8n Cloud |
| Agent + human approval | AgenticOrg |
| Payment | Pine Labs checkout |
| Updates | Telegram bot (one-way) |
| Data | Supabase |

English only for now; বাংলা, हिंदी and WhatsApp are shown as *coming soon*. Real Google profile creation is simulated until Google grants Business Profile API access.

## Run locally

```bash
/opt/homebrew/bin/python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env    # then fill in keys
.venv/bin/uvicorn app.main:app --port 8000 --reload --reload-dir app
```

`/api/health` shows which keys are configured (true/false only, never values).

## Checks

```bash
.venv/bin/python scripts/check_keys.py    # PASS/FAIL/SKIP per API
.venv/bin/python scripts/stt_test.py      # speech-to-text test on samples/*
```

## Design

Design direction ("the jeweller's box") is in the PRD. The impeccable design skill is installed in `.claude/` (telemetry off). Its engine binary isn't in git; on a new machine run `npx impeccable install --providers=claude --scope=project`.

## Deploy

Replit: import this repo from GitHub, add the keys as Replit Secrets, run `uvicorn app.main:app --host 0.0.0.0 --port 8000`, then deploy. `Dockerfile` and `render.yaml` stay as a Render fallback.
