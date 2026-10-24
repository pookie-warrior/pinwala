# Pinwala — handoff (24 Oct 2026, ~01:00 IST)

Written at the end of the planning session in Shipra's LKS Claude account. The build continues in her **personal** Claude account (LKS doesn't allow custom connectors), so that session starts with none of this history. Read this file and [PRD.md](PRD.md) first.

## Decided

- **Product:** Pinwala. Owner sends a shopfront photo + voice note in his language → finished Google listing, posts, voice reply. AI Builders Day '26, Track 2 (Commerce, Pine Labs), 24 Oct, 9 AM–9 PM, Bengaluru. Goal: working demo + 20 real users.
- **Main channel: the web app** (installable to the home screen; mic + camera; WhatsApp-style chat UI). Results go out through **Share to WhatsApp** (phone share sheet). No WhatsApp integration. **Twilio is dropped.**
- **Scope is frozen** (PRD → "Frozen scope"): Voice Listing, Places check + rivals count, Content Studio, **Telegram bot (committed)**, Rival Watch, Pine Labs receipt QR. Each has a minimum version; enhancements only if their slot has room.
- **Demo languages: Bengali, Hindi, English.** The demo persona is Bapi-da, a Kolkata-style mishti shop in Koramangala.
- **Build and host:** Claude Code (personal account) builds in `~/Pinwala` → GitHub → **Replit** hosts the website. Logic in n8n Cloud, data in Supabase.
- **Logic in n8n Cloud trial**, separate from Beacon's `auto.snowfig.com`. Workflows are named `Pinwala – …`. The website forwards `/api/*` to n8n webhooks with a secret key, so the n8n address never shows.
- **Audio:** record WAV in the browser (Chrome's .webm isn't accepted by Gemini; n8n Cloud has no ffmpeg).
- **AI rule #1:** never invent a field. Each field is tagged *said*, *seen* or *needs confirmation*.
- **Design:** "jeweller's box" (lacquer green #0F2A24, ivory #F6F0E4, one marigold accent #E8A33D), Anek for UI + Indian scripts, upright serif display. **pbakaus/impeccable is installed in this project, telemetry off.** Run `/impeccable init` first in the new session.
- **Can't publish to Google** (the Business Profile API needs approval): drafts + copy buttons, and say so honestly in the pitch.

## Still open (decide first thing)

1. **n8n connector:** the personal account has a custom n8n connector. **Check which instance it points to.** It must be the new Cloud trial, not `auto.snowfig.com`.
2. **Speech-to-text route:** Gemini alone (one call: audio + photo → fields), or Sarvam Saarika first and then the LLM. Settled by `scripts/stt_test.py` on real Bengali notes.
3. **Voice reply:** Sarvam Bulbul or ElevenLabs. Generate the same Bengali sentence with both and pick by ear.
4. **Places key:** your own Google Cloud key (needed if n8n calls Places), or Replit's Google Maps connector (only usable from an app running on Replit). Check that it covers Places API (New).

## Tonight's checklist

Do 1, 4, 11 and 12 at minimum. Those are the ones that would block tomorrow.

1. Google Cloud: project → billing → enable **Places API (New)** → API key with a daily quota cap. (Skip only if you're going Replit-connector-only.)
2. Gemini API key (Google AI Studio).
3. Sarvam API key; check the free credits.
4. **n8n Cloud trial:** sign up → turn on the instance MCP server → connect it to the **personal** Claude account → add Gemini, Places and Sarvam credentials inside n8n.
5. Supabase: create a project called `pinwala`.
5b. **Telegram:** create the bot with @BotFather (name it Pinwala), copy the bot token, and add it as a Telegram credential in n8n Cloud.
5c. **Replit:** confirm the Google Maps connector covers Places API (New) and who pays for the calls.
6. GitHub: create an empty repo called `pinwala`.
7. Record 3 voice notes, ~10 s each (**Bengali**, Hindi, English), speaking like an owner: name, what you sell, area, hours. Put them in `samples/`.
8. Add 3 shopfront photos with readable signboards to `samples/`.
9. Record the demo "Bapi-da" voice note (Bengali) in a quiet room (backup for a noisy venue).
10. Copy `.env.example` to `.env` and fill it in.
11. Check the keys:
    ```bash
    cd ~/Pinwala && .venv/bin/python scripts/check_keys.py
    ```
12. Run the speech-to-text comparison:
    ```bash
    cd ~/Pinwala && .venv/bin/python scripts/stt_test.py
    ```
13. Message 5–10 shop owners you know so they're ready to try it tomorrow.
14. Check the event rules on code written before the event.
15. Charge laptop and phone, and test the phone hotspot.
16. Open a new Claude Code session (personal account) in `~/Pinwala` and run `/impeccable init`, giving it `docs/PRD.md`.

## What's already in `~/Pinwala`

| Path | What |
| --- | --- |
| `app/main.py` | Placeholder FastAPI app: `/api/health` (shows which keys are set, true/false only) + static page. To become: page + `/api/*` forwarding to n8n |
| `app/config.py` | Loads `.env` without extra packages |
| `static/index.html` | Placeholder page ("Pinwala") |
| `scripts/check_keys.py` | PASS/FAIL/SKIP for Gemini, Places, Sarvam (the Twilio check shows SKIP and can be ignored) |
| `scripts/stt_test.py` | Gemini vs Sarvam on `samples/*`, side by side; saves to `scripts/out/` |
| `Dockerfile`, `render.yaml` | Docker deploy files from when Render was the host. Replit is the host now; keep them as a fallback |
| `.claude/` | impeccable skills, agents and hooks; `launch.json` (dev server `pinwala`) |
| `docs/PRD.md` | Full PRD (master copy) |
| `.venv/` | Python 3.12 virtual environment with the packages installed |

Git is set up, but nothing is committed yet. The first commit and push go to the new `pinwala` repo once Shipra OKs it.

## Prompt to paste into the new session

> Read docs/HANDOFF.md and docs/PRD.md in ~/Pinwala. We're building Pinwala for AI Builders Day today. Here's my output from check_keys.py and stt_test.py: [paste]. Help me settle the open decisions, then start on the Intake workflow in n8n Cloud and the web app.
