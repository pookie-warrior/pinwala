# Pinwaala — AI Builders Day '26 submission kit

Track 2 · AI for Commerce · Live: **https://pinwaala.replit.app** · Repo: `pookie-warrior/pinwala` (private)

Numbers below are real as of 17:58 IST. **Re-read the live counter on the landing page before posting and replace every `[N]`.**

---

## 1. One-liner

**Pinwaala gets India's small shops found on Google: the owner talks for two minutes in English, Hindi or Bengali, an AI agent prepares his Google profile, and a human approves it before anything goes out in his name.**

## 2. Company Stack checklist

| Requirement | Status | Evidence |
| --- | --- | --- |
| **Product** · live on a public URL | ✅ | https://pinwaala.replit.app (all 7 integrations configured, `/api/health`) |
| **Team** · 1+ agent on AgenticOrg, a human approves | ✅ | *Pinwaala Profile Agent* (`a64642fd-…`), confidence floor 99% + `confidence <= 1` → **every run waits in Approvals**. Runs are started automatically by the app via the AgenticOrg API when an owner approves; Shipra approves/rejects in the Approvals queue (correlation IDs e.g. `run_46397055d0fe`, `run_b757ae84c5f7`) |
| **Money** · Pine Labs payments | ⚠️ Partial | Pine Labs merchant sign-up needs GST, so checkout isn't live. In-app **"Reserve my Listing Pack · ₹99"** records verified intent ("ready to pay" counter). Say this honestly |
| **Users** · 20 free or 5 paying | ⚠️ In progress | Live counter: `[N]` shops checked · `[N]` owners verified (phone verified by Vobiz call, once per number) · `[N]` ready to pay ₹99 |

## 3. Proof of life (paste into the form)

- Live app: https://pinwaala.replit.app — counter on the landing page is backed by Supabase events (no fake numbers).
- Real usage as of 17:58: **2 shops checked, 1 owner verified (beauty salon, Kalyan Nagar), 3 completed voice conversations (~5 min)**. Update with the live counter.
- Integrations verified end to end today:
  - **Google Places API (New)** — find-my-shop autocomplete, place details, rivals within 1 km (text search; ~0.5 s).
  - **ElevenLabs voice agent** — English/Hindi/Bengali, language locked per call, live transcript, 11 fields extracted in English; 3 simulated test runs + real calls.
  - **Vobiz** — phone verification: Pinwaala calls, owner presses 1 (`Digits: 1` received) and free missed call to 080 6426 9429 (rejected unanswered, ₹0).
  - **AgenticOrg** — Pinwaala Profile Agent prepares the Google Business Profile JSON; every run stops for human approval (`hitl_triggered`).
  - **Supabase** — events for the live counter; phone numbers stored only as a hash + last 4 digits.
- Screenshots to attach: AgenticOrg approval card (summary + Approve/Reject), the live counter, the rivals map, a live transcript in Hindi/Bengali.

## 4. 2-minute demo video — shot list

Record on your phone screen (Android: screen recorder; iPhone: Control Centre → Screen Recording with mic on).

| Time | Show | Say |
| --- | --- | --- |
| 0:00–0:12 | Landing page with live counter | "India has 6 crore small businesses. Most can't be found on Google because setting it up is long, English-only and form-heavy. This is Pinwaala." |
| 0:12–0:30 | No → Sweets → area → **rivals map: "20+ sweet shops within 1 km are on Google. You're not, yet."** | "In 10 seconds, the owner sees exactly what he's missing: every rival around him on Google." |
| 0:30–0:42 | Verify screen → missed call → ✓ | "One free missed call verifies his number through Vobiz. No forms, no OTP typing." |
| 0:42–1:15 | Pick **বাংলা/हिंदी** → voice chat with **live transcript** | "He just talks, in his own language. Our ElevenLabs agent knows his street already and asks six questions." |
| 1:15–1:30 | Summary card (heard / needs confirmation) → Yes, this is my shop | "It never guesses. Anything it didn't hear is flagged for him to confirm. He approves." |
| 1:30–1:48 | Switch to **AgenticOrg Approvals** → card with summary → **Approve** | "Our AgenticOrg agent prepares his Google profile, and a human at Pinwaala approves it before anything goes out in his name." |
| 1:48–2:00 | Done screen → **Reserve ₹99** → counter ticks up | "₹99 for the Listing Pack, Pine Labs checkout next. [N] shops checked today. Pinwaala: get found." |

## 5. LinkedIn post

> Today at **AI Builders Day** (Airtribe × Pine Labs) I built **Pinwaala** 📍, an AI assistant that gets India's small shops found on Google.
>
> Walk outside any shop in Bengaluru and search "sweet shop near me": 20+ show up within a kilometre. Thousands of neighbourhood shops don't, because Google's setup is long, English-only and form-heavy.
>
> Pinwaala replaces the form with a conversation:
> 🗺️ In 10 seconds, the owner sees every rival around him on Google
> 📞 One free missed call verifies his number (Vobiz)
> 🎙️ He talks for two minutes in English, Hindi or Bengali; our ElevenLabs voice agent extracts his shop details
> 🤖 An AgenticOrg agent prepares his Google Business Profile, and **a human approves it** before anything goes out in his name
>
> Live now: https://pinwaala.replit.app — [N] shops checked so far. Try it, or send it to a shop owner you know.
>
> Next: Pine Labs checkout for the ₹99 Listing Pack, and Google partner access to create profiles directly.
>
> #AIBuildersDay #Airtribe #PineLabs #AgenticAI #ElevenLabs #SmallBusiness #Bengaluru

## 6. X post

> Built Pinwaala 📍 at #AIBuildersDay: small shops talk for 2 min in English/हिंदी/বাংলা → AI prepares their Google profile → a human approves. Missed-call verification via Vobiz, AgenticOrg agent, ElevenLabs voice. Try it 👉 https://pinwaala.replit.app @airtribe @PineLabs

## 7. Judging: talking points by criterion

| Criterion | One line |
| --- | --- |
| **Problem & insight** | Being on Google is the shopfront of 2026, and the setup is an English form. Owners already live on voice notes. |
| **Ambition & originality** | Voice-first, multilingual onboarding with the owner's actual street as the hook; agency model (Pinwaala creates, owner owns, Pinwaala manages) once Google partner access comes. |
| **Agentic depth** | Two agents: ElevenLabs interviewer (context-aware, language-locked, extracts 11 fields) → AgenticOrg profile agent (JSON profile, flags conflicts) → **human approval gate** before acting in the merchant's name. |
| **Traction** | Live counter, verified users only, once per phone number. State the number honestly. |
| **Demo & polish** | Mobile-first "jeweller's box" design; live transcript; one-tap verification. |

**Likely questions**
- *Can you actually create Google profiles?* Not yet: Google's Business Profile API needs partner approval. Today we prepare the profile and guide the owner; the owner always owns it, Pinwaala manages.
- *Why should a shop owner pay?* ₹99 once for a ready-made profile, posts and review QR; then ₹499/month for weekly posts and review replies. A local agency charges ₹5,000+.
- *Where's Pine Labs?* Merchant onboarding needs GST; we capture verified ₹99 intent now and plug in Pine Labs checkout next. Distribution: bundle with Pine Labs terminals so merchants keep the machine.
- *What stops the AI inventing things?* Every field is tagged heard / on signboard / needs confirmation, and two humans approve: the owner, then a Pinwaala reviewer on AgenticOrg.

## 8. Next hour: get real users

1. Send the link to every shop owner you know (WhatsApp/Telegram): "Check if your shop is on Google — 10 seconds: https://pinwaala.replit.app"
2. Walk the venue: builders and mentors can do the 10-second rivals check for their own neighbourhood (counts as *shops checked*).
3. Ask 3–5 people to complete the missed call (counts as *owners verified*) and tap Reserve (counts as *ready to pay*).
4. Screenshot the counter just before 7:00 for the stage.
