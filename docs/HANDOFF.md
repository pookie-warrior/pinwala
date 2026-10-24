# Pinwaala — handoff

Updated 24 Oct 2026, at the venue. The build continues in Shipra's **personal** Claude account (LKS doesn't allow custom connectors), so that session starts with none of the planning history. Read this file, then [PRD.md](PRD.md) and [USER_JOURNEY.md](USER_JOURNEY.md).

## Where things stand

- **Live URL:** https://pinwaala.replit.app (deploying)
- **Folder:** `~/Pinwaala` · **Repo:** [pookie-warrior/pinwala](https://github.com/pookie-warrior/pinwala) (private). The remote is tied to the pookie-warrior account, so pushes work even while the GitHub CLI's active account is Shushi-1427.
- **Planning is frozen:** PRD (scope, timeline, architecture) and User Journey v2. Build from those.
- **Code:** only last night's placeholder (FastAPI health check + one static page) plus test scripts. Nothing from the journey is built yet.
- **Hard stops:** build freeze 3:45 · testing 3:45–4:15 · submission 4:15–4:30 (submissions close 5:00). Track 2 locks at 12:30.

## Decided (summary; details in the docs)

- **Mobile-first web app**, English only; বাংলা, हिंदी and WhatsApp shown as *coming soon*.
- **Branch on entry:** "Is your shop on Google Maps?" → find my shop (search / near me / link) **or** photo + pin, on one map screen.
- **Instant rivals snapshot** from Google Places, before the voice agent.
- **ElevenLabs voice agent** (~6 questions, given the snapshot). 2:00 PM go/no-go; backup is on-screen questions answered by voice notes.
- **Sarvam Document AI** reads the shop photo; **n8n Cloud** merges everything.
- **Owner approves** his details (approval 1, counts as a user) → **verifies his phone by a missed call** to Pinwaala's Vobiz number `+91 80 6426 9429` (tested 24 Oct, works, ₹0; Firebase SMS fallback) → **₹99 Pine Labs**. Telegram is optional, for updates.
- **Vobiz:** the XML Application *Pinwaala missed call test* still points at a deleted test address; switch its answer URL to `https://pinwaala.replit.app/api/vobiz/answer` when that endpoint exists.
- **AgenticOrg "Pinwaala Profile Agent"** prepares the profile / fixes pack → **Pinwaala reviewer approves in AgenticOrg** (approval 2). First test whether the owner's tap can be passed to AgenticOrg's approve API instead.
- **New shops:** draft → verification code entered in the app (approval 3) → live → ownership invite to his Gmail, **all simulated today**. **Existing shops:** report + fixes released.

## Do next, in order

1. **Organisers (now):** AgenticOrg login or invite (don't create a second organisation), confirm hackathon use is covered by AgenticOrg's licence, confirm API keys + Approvals are enabled. Ask the Pine Labs desk for checkout credentials and a sample.
2. **AgenticOrg:** add a Gemini key under Settings → AI credentials; create an API key (Settings → API Keys); create the Pinwaala Profile Agent (setup steps in the PRD's architecture section).
3. **Replit:** import the repo, add Secrets, get the public URL (see README → Deploy).
4. **Keys:** Firebase project with phone sign-in (SMS fallback; add `pinwaala.replit.app` as an authorised domain), Google Places (own key, or confirm Replit's Maps connector covers Places API (New)), ElevenLabs, Sarvam, Telegram bot token (@BotFather), Supabase project, n8n Cloud (check the personal account's n8n connector points to the Cloud trial, not `auto.snowfig.com`).
5. **Sarvam photo test:** 2–3 real signboard photos through Document AI Extract, to see whether it can tell the type of shop.
6. **Build** in the PRD's order; send the link to shop owners at 1:30.

## Open questions

- [ ] AgenticOrg access, licence, features enabled (organisers)
- [ ] Places: own key or Replit's connector
- [ ] Does AgenticOrg allow approving by API with our key (owner as approver)?
- [ ] Domain and trademark check for Pinwaala

## What's in the repo

| Path | What |
| --- | --- |
| `docs/PRD.md`, `docs/USER_JOURNEY.md` | The plan (master copies) |
| `app/main.py`, `app/config.py` | Placeholder FastAPI app (`/api/health`) + `.env` loader |
| `static/index.html` | Placeholder page |
| `scripts/check_keys.py` | PASS/FAIL/SKIP for Gemini, Places, Sarvam (Twilio shows SKIP; not used) |
| `scripts/stt_test.py` | Speech-to-text comparison on `samples/*` |
| `Dockerfile`, `render.yaml` | Render fallback |
| `.claude/` | impeccable design skill + agents, dev-server config (`pinwala`) |

Not in git: `.env`, `samples/*`, `.venv/`, `.claude/settings.local.json`, impeccable's engine binary (reinstall with `npx impeccable install --providers=claude --scope=project`).

## Prompt to paste into the new session

> Read docs/HANDOFF.md, docs/PRD.md and docs/USER_JOURNEY.md in ~/Pinwaala. We're building Pinwaala for AI Builders Day today; hard build freeze at 3:45. Start with the PRD's build order, item 1. Run /impeccable init first using the PRD's design direction.
