# Pinwala — Product Requirements

24 Oct 2026 · Shipra Shreya
**Master copy.** The step-by-step flow is frozen in [USER_JOURNEY.md](USER_JOURNEY.md) v2; this PRD follows it. Updated at the venue after the AI Builders Day rules were announced: about 5 hours of build, a hard stop at 4:30 PM, and a required AgenticOrg agent, Pine Labs payment and real users.

Pinwala turns one photo and one voice note into a ready Google listing and posts. English today; Bangla and Hindi are next. Then it guides him through getting it live on Google. Built for AI Builders Day '26, **Track 2 · AI for Commerce** ("Every Business Is a Store"), and designed to outlive it.

## Hackathon rules that shape this PRD

| Rule | What it means for Pinwala |
| --- | --- |
| Challenge starts 10:15 · **tracks lock 12:30** · **submissions close 5:00 PM** | Our hard stops: **build freeze 3:45**, testing 3:45–4:15, **submission 4:15–4:30** |
| **Product:** live on a public URL | Hosted on Replit |
| **Team:** 1+ agent on **AgenticOrg**, a human approves | Pinwala Profile Agent prepares the profile; a Pinwala reviewer approves it in AgenticOrg Approvals (the owner also approves his details in the app) |
| **Money:** Pine Labs payments that work | ₹99 Listing Pack, real Pine Labs checkout (journey step 9) |
| **Users:** 20 free or 5 paying | Shop owners reached through shared links (any chat app) with `?ref=` tracking |
| **Submit:** live URL, proof of life, **2-minute demo video**, **LinkedIn + X or Instagram posts** (compulsory) | Done between 4:15 and 4:30; video recorded during testing |
| **Track 2 deliverable:** "One order, end to end": a real customer from first message to payment or signup | One real shop owner going landing page → listing → ₹99 payment |
| Judging, round 1 (table): Problem & Insight 25 · Ambition 15 · Agentic Depth 15 · **Traction 25** · Demo & Polish 20 | Users are worth as much as the problem; start sharing the link early |
| Judging, round 2 (top 10 on stage, 7:00): 20 · 20 · 20 · **Traction 30** · 10 | |
| Credits: AgenticOrg (required), Replit, ElevenLabs + Vobiz, Pine Labs, Render, Greptile | Replit for hosting; ElevenLabs available for voice later |
| "Who owns what we build? You do." | Pinwala is Shipra's |

## Name: Pinwala

**Decided.** Pinwala is the helper who puts your pin on the map, the way the doodhwala brings the milk. "Pinwala ko bolo." Other options considered: Haazir, Signboard, Awaaz, Nukkad, Saamne. Still open: domain and trademark check.

## Problem and opportunity

Small shops lose customers they never see: people who search "sweet shop near me" and find the twelve competitors who are listed. The owner feels no pain because walk-ins and regulars keep coming, so he has no reason to act.

Why existing answers fail him:

- **Google's own setup is a wall.** Long forms, English, category guessing, then verification.
- **Audits don't sell.** A report tells a busy owner what is wrong and leaves the work with him.
- **Agencies cost too much.** A local digital agency charges roughly ₹5,000–15,000 a month (approximate, to verify before the pitch).

The opportunity: an assistant that does the work from a photo and a voice note, and asks him only to approve. This matches the track's insight: agents give a small business the operations of a big one while keeping it personal.

## Product promise

**One line:** Show us your shop and talk for 10 seconds. Your Google listing is ready, in your language.

| It is | It is not |
| --- | --- |
| An assistant that writes the listing and posts | An audit or a score |
| Voice-first: English today, Bangla and Hindi next | Another form to fill in |
| Approve-then-act: the owner taps yes | A bot that acts in his name without asking |
| Grounded in real Google data about his street | Generic marketing tips |

## Users

| Persona | Who | What wins them |
| --- | --- | --- |
| **Bapi-da, the unlisted owner** (primary) | Kolkata-style mishti shop in Koramangala. Bengali-first, types little, sends voice notes all day | Going from invisible to listed with one voice note |
| **The helper** (main user today, while the app is English-only) | His son, daughter or shop assistant holding the phone | A flow simple enough to finish for him in 2 minutes |
| **Meena, already listed but neglected** | Salon with old photos, no hours, unanswered reviews | Seeing what's missing, and ready-made posts |
| **Pine Labs** (channel, later) | Payments partner to lakhs of merchants (approximate, to verify) | A reason for merchants to keep the terminal |

Out of scope for now: chains, businesses with no shopfront, ads management.

## Today's scope (frozen)

**What ships by 3:45 PM** follows [USER_JOURNEY.md](USER_JOURNEY.md) v2. Build order is priority order.

| # | What | Journey step | Real or simulated |
| --- | --- | --- | --- |
| 1 | **Landing + branch:** "Is your shop on Google Maps?" (mobile-first, English; বাংলা/हिंदी *coming soon*) | 1 | Real |
| 2 | **Find my shop** (search by name / near me / paste link) and **photo + pin** for new shops, on one map screen | 2a, 2b | Real |
| 3 | **Instant rivals snapshot** from Google Places (map + numbers / scorecard) | 3 | Real |
| 4 | **ElevenLabs voice agent** (~6 questions, knows the snapshot) + field extraction; Sarvam Document AI reads the photo | 4 | Real (backup: on-screen questions + voice notes) |
| 5 | **Summary → owner approves** (human approval 1) + contact, Gmail, consent | 5 | Real |
| 6 | **n8n** merges everything into profile data; **outcome screen** (3 tiles) | 6–7 | Real |
| 7 | **₹99 Pine Labs checkout** + Telegram connect | 8, 8b | **Real payment** |
| 8 | **AgenticOrg Pinwala Profile Agent** prepares the profile / fixes pack → **Pinwala reviewer approves in AgenticOrg** (human approval 2) | 8b | Real agent + real approval |
| 9 | **After approval:** new shop → verification code in app (approval 3) → live → ownership invite (**simulated**); existing shop → report + fixes released | 9a, 9b | Google steps simulated |
| 10 | **Telegram one-way updates** at each stage | 10 | Real |

**Not today:** বাংলা/हिंदी, WhatsApp, two-way Telegram chat, Vobiz phone calls, QR posters, real Google publishing, Rival Watch heatmap, weekly posts.

**Cut order if behind:** item 4 falls back to on-screen questions + voice notes (decided at 2 PM); item 9 shows the simulated steps as one screen instead of animated stages; item 3 for existing shops shows numbers without the map. Items 5, 7, 8 are the hackathon requirements and never get cut.

## Timeline (today)

| Time | What |
| --- | --- |
| Now | **Ask the organisers:** AgenticOrg login/invite, licence covered, API keys + Approvals enabled. Add a Gemini key in AgenticOrg |
| 12:30 | **Track locks: Track 2** |
| 12:00 – 1:30 | Items 1–3 live on Replit (landing, find/pin, rivals snapshot). ElevenLabs agent created in parallel |
| **1:30** | **Send the link to the first shop owners** |
| 1:30 – 2:15 | Item 4 (voice agent in the page) + item 5 (summary + approve) |
| **2:00** | **Voice agent go/no-go**; switch to the backup if not working |
| 2:15 – 3:00 | Items 6–7 (n8n merge, outcome screen, Pine Labs checkout) |
| 3:00 – 3:45 | Items 8–10 (AgenticOrg agent + approval, simulated Google steps, Telegram updates). Test the approve-by-API option (10 min) |
| **3:45** | **Build freeze** |
| 3:45 – 4:15 | Testing on real phones; record the 2-minute video |
| 4:15 – 4:30 | Submit: live URL, proof of life, video, LinkedIn + X posts |
| 5:15 / 7:00 | Round 1 at our table / top 10 on stage |

## Product vision (after today)

Five modules mirror Beacon's structure for any business. Today ships the first one.

| Module | Beacon equivalent | What the owner gets |
| --- | --- | --- |
| **Voice Listing** (today) | GBP setup | Photo + voice note → listing + posts, guided onto Google |
| **Rival Watch + near-me heatmap** | Radar | Top nearby competitors compared; where he shows up for "near me" searches (labelled estimate) |
| **Content Studio** | Article Studio | Weekly posts from his photos; review replies in each reviewer's language |
| **Pine Labs review loop** | (new) | A QR on the receipt that opens his Google review page |
| **Everywhere Check** | Off-page cockpit | Justdial, Zomato, Swiggy, Practo, IndiaMART: missing or mismatched details |

**Agency model (once Google grants Business Profile API access):** Pinwala creates the profile from the voice note, starts verification, and the owner just forwards Google's code on Telegram (later WhatsApp) and taps to approve. **The owner stays the owner; Pinwala is the manager.** Google decides how each shop is verified (SMS, phone call, video, postcard); Pinwala guides it but never skips it.

## UX and visual direction

**"The jeweller's box."** Deep lacquered green, warm ivory and one marigold accent, like a mithai box or a jeweller's ledger. Classy and Indian without cliché, and nothing like the purple-to-blue look of generic AI tools.

| Role | Colour | Use |
| --- | --- | --- |
| Lacquer | #0F2A24 | Background, header |
| Ivory | #F6F0E4 | Cards, the listing sheet |
| Marigold | #E8A33D | The one accent: his pin, primary button, "live" moments |
| Ink | #1D2421 | Text on ivory, never pure black |
| Rival | #7C8A86 | Competitor pins, so he stands out |

- **Gloss with restraint:** a soft sheen on the listing card and receipt; no dark glows, heavy shadows or blur everywhere.
- **Type:** upright serif for display (candidate: Fraunces); **Anek** (Latin, Bangla, Devanagari) for UI, so Bangla and Hindi slot in later without a font change. No Inter, no system default, no italic display text.
- **Motion:** ease-out, 200–400 ms, no bounce; respect reduced-motion.
- **Signature moment:** the pin drop. Competitors' slate pins are already on the map; his marigold pin drops in: "You + 12 sweet shops."
- **Mobile first:** big buttons, one action per screen, works one-handed.
- **impeccable** is installed in the project (telemetry off): `/impeccable init` with this PRD, `shape`/`craft` per screen, `audit` + `npx impeccable detect static/` before the build freeze.

## Technical architecture

The web app on Replit is what the owner sees. Keys stay on servers, never on the phone.

```
Owner's phone (web app on Replit, mobile-first)
  ├─ Google Places ── find his shop / rivals snapshot (called from the web app, for speed)
  ├─ ElevenLabs voice agent (their web SDK in our page) ── conversation + extracted fields
  ├─ owner approves (1) → Pine Labs checkout ₹99 → Telegram connect
  ▼
n8n Cloud
  ├─ Sarvam Document AI (Extract) ── reads the shop photo (async: submit, poll, fetch)
  ├─ merge photo + conversation + Places → profile data
  ├─ AgenticOrg: agents.run("Pinwala Profile Agent", inputs=JSON)
  │     └─ run waits in AgenticOrg Approvals → Pinwala reviewer approves (2)
  ├─ poll run status until approved / rejected
  └─ Telegram one-way updates + update the web app
Supabase ── shops, fields, consent, payments, referrers, live counter
```

| Piece | Choice | Notes |
| --- | --- | --- |
| Web app | Python FastAPI (in `~/Pinwala`) on Replit | Mobile-first; HTTPS needed for mic, camera, GPS |
| Find shop / rivals | Google Places API (New): autocomplete, nearby search, place details | Own key, or Replit's Maps connector if it covers Places (New). Short Maps links resolved on the server |
| Voice agent | ElevenLabs agent + web SDK | Given the snapshot when the call starts; extracts named fields at the end (verify in ElevenLabs settings) |
| Photo reading | Sarvam Document AI, Extract with a field schema | JPG/PNG, Bengali/Hindi/English; async; 10 requests/min |
| Orchestration | n8n Cloud trial | Separate from Beacon |
| Agent + approval | AgenticOrg | No ElevenLabs/Vobiz integration exists; agent is text-in/JSON-out. API key from Settings → API Keys (admin only). Python SDK `client.agents.run(...)` → `status`, `output`. No callbacks: poll |
| Payment | Pine Labs checkout + confirmation | |
| Updates | Telegram bot, one-way | |
| Data | Supabase | |

**AgenticOrg agent setup:** Agents → Create Virtual Employee → Persona *Pinwala Profile Agent* → Prompt (prepare Google profile or report + fixes from JSON; return JSON only; never invent; mark missing fields *needs_confirmation*) → Behavior: Gemini, no tools, approval required on every run → create in test mode, test, promote.

## AI behaviour rules

1. **No guessing.** Each field carries a source: *heard*, *on signboard*, *owner pin*, *agent-written*, or *needs confirmation*.
2. **Category from Google's list**, not free text.
3. **English for now**; process Hindi or Bangla if spoken, show everything in English.
4. **Warm, plain register.** No superlatives or claims he didn't make; no keywords stuffed into the shop name.
5. **Tool failure is not content failure.** If speech, Sarvam or Places fails, say so and ask again; never fill gaps.
6. **Nothing acts in his name without two approvals:** the owner's (his details) and Pinwala's reviewer in AgenticOrg (what the agent wrote). Codes need a third tap from the owner.
7. **Verification codes** are never stored or logged.
8. **Reports show only what Google's public data shows:** rating, reviews, up to 10 photos, hours, website, phone. Never search views, calls or ranking.

## Success metrics

| Metric | Today's target | Product target |
| --- | --- | --- |
| Real users (shops processed) | **20 free or 5 paying** | Weekly active shops |
| Paid Listing Packs (₹99, Pine Labs) | At least 1, aiming for 5 | Conversion to ₹499/month |
| One shop end to end (landing → payment) | **At least 1, on video** | — |
| Time from voice note to listing card | Under 15 seconds | Under 10 seconds |
| Invented facts | Zero | Zero |
| Languages working end to end | English | Bangla and Hindi next, then Kannada, Tamil, Telugu |

## Business model

| Tier | Price | What's in it |
| --- | --- | --- |
| **Free** | ₹0 | Listing card, "N shops near you" |
| **Listing Pack** (today) | **₹99 once** | Guided Google setup, 3 posts + Status + Instagram caption, review QR card; later "we submit for you" |
| **Assistant** (later) | ₹499 a month | Weekly posts, review replies, monthly "you vs. shops near you" |
| **Partner bundle** (later) | Paid by a payments partner | Assistant bundled with the terminal for merchant retention |

**Go-to-market:** link-forward growth in one neighbourhood (Telegram now, WhatsApp next) → payments-partner pilot (Pine Labs is the natural first) → more languages and cities.

## Risks and open questions

| Risk | Impact | Mitigation |
| --- | --- | --- |
| **AgenticOrg login still blocked** | Required item missing | Organisers now: hackathon workspace invite (don't create a second organisation) |
| AgenticOrg licence says organisations need a signed agreement | Compliance question | Confirm with organisers that hackathon use is covered |
| AgenticOrg API details undocumented (request format, results) | Integration slips | Use the Python SDK from n8n; 15 min to test; ask organisers for a sample |
| Approve-by-API blocked (requester can't self-approve) | Owner can't be the AgenticOrg approver | Pinwala reviewer approves in the dashboard (documented, works) |
| ElevenLabs agent setup or field extraction slips | Hero step missing | 2 PM go/no-go → on-screen questions + voice notes |
| Sarvam can't infer shop type from a photo | Weaker extraction | Type comes from the picker and the conversation |
| Pine Labs checkout takes longer | "Money" requirement missing | Start by 2:15; ask the Pine Labs desk early |
| Too few owners by 3:30 | Traction score | Send the link at 1:30 |
| Google Business Profile API needs approval | Can't publish for real | Simulated and labelled; honest in the pitch |

**Open questions**

- [ ] Organisers: AgenticOrg invite, licence, features enabled
- [ ] Places: own key or Replit's connector
- [ ] Domain and trademark check for Pinwala

## Demo (2-minute video, and the stage if top 10)

1. **Hook (15 s):** "Bapi-da has sold Kolkata mishti in Koramangala for 15 years. Search 'sweet shop near me' outside his door, and he doesn't exist."
2. **Snapshot (20 s):** "Not on Google" → photo → pin → the map fills with 12 rival pins instantly.
3. **Voice agent (30 s):** "I can see 12 sweet shops near you. What makes yours different?" A short conversation; the summary card fills in.
4. **Owner approves + pays (20 s):** "Yes, this is my shop" → ₹99 through Pine Labs.
5. **Agent + human check (20 s):** the AgenticOrg agent's prepared profile appears in Approvals; Shipra approves → Bapi-da's phone buzzes on Telegram: "Verification started."
6. **Proof (15 s):** "N shop owners used it today, M paid," from the live counter.
