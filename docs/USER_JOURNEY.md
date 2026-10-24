# Pinwaala — User Journey v2 (frozen)

Frozen: 24 Oct 2026, AI Builders Day, after the venue rules. Owner: Shipra Shreya.
Replaces v1 (single path). **Changes after this point need an explicit decision. The build follows this file.**

**Mobile-first:** one question or action per screen, big tap targets, works one-handed on 4G. **Screens in English** (বাংলা and हिंदी screens shown as *Coming soon*); **the voice agent speaks English, Hindi and Bengali**, switching to the language the owner speaks. WhatsApp shown as *Coming soon*; Phone verified by **Pinwaala calling him: he answers and presses 1** (Vobiz, no code); fallback: he gives Pinwaala a missed call; Telegram is optional, for one-way updates; no chat today. No login screen before he sees value.

## The journey at a glance

```
Landing: "Is your shop on Google Maps?"
   ├─ YES → find my shop (search / near me / paste link)
   └─ NO  → shop photo → drop pin on map
          ↓ (both)
Instant rivals snapshot (map + numbers)
          ↓
Voice agent conversation (ElevenLabs; knows the snapshot)
          ↓
Summary → approve or edit          ← human approval 1 · counts as a "user"
          ↓
Verify number: Pinwaala calls, press 1 (Vobiz) → fallback: missed call to Pinwaala (₹0) → then SMS code (Firebase) → optional: Telegram updates
          ↓
Sent to n8n → profile data prepared (Sarvam reads photo, ElevenLabs fields, merged)
          ↓
Outcome screen (3 tiles) → Pay ₹99 (Pine Labs)
          ↓
AgenticOrg "Pinwaala Profile Agent" prepares the profile / fixes pack
          ↓
Pinwaala reviewer approves in AgenticOrg Approvals   ← human approval 2
          ↓
NEW shop:      draft profile → verification started → enter code in app (approval 3) → live (simulated) → ownership invite to Gmail
EXISTING shop: full report + fixes pack released
          ↓
Telegram updates at each stage (one-way)
```

## Decisions

| # | Decision | Frozen choice |
| --- | --- | --- |
| 1 | Entry question | "Is your shop on Google Maps?" Yes / No, on the landing page |
| 2 | Finding an existing shop | Search by name (suggestions as he types) → "This is my shop". Alternatives: "Near me" list from GPS; paste a Maps link (with a 3-step picture guide) |
| 3 | Location for a new shop | Same map screen: GPS pin if he's at the shop, else search a landmark/area; he drags the pin to his door and confirms |
| 4 | When rivals appear | Right after the shop/pin is known, before the voice agent |
| 5 | Voice agent | ElevenLabs agent *Pinwaala Shop Interviewer* (setup: [ELEVENLABS_AGENT.md](ELEVENLABS_AGENT.md)); given the snapshot as context at the start; **English, Hindi, Bengali** with a voice per language (auto-switches); extracted fields always in English. AgenticOrg's own voice platform is not usable (server errors on Integrations/Bindings), so voice stays on ElevenLabs |
| 6 | Agent backup (if not working by ~2 PM) | Same questions on screen, one per screen, each answered by a short voice note |
| 7 | Photo reading | Sarvam Document AI (Extract) on the shop photo |
| 8 | Conversation → fields | ElevenLabs Data collection (10 fields, values in English); empty = not heard → *needs confirmation* |
| 9 | Order | Fields extracted **before** approval; data goes to n8n **after** approval |
| 10 | What counts as a user | Approved their listing (human approval 1) |
| 11 | ₹99 for a new shop | Pinwaala creates a draft profile in its own account and starts verification (simulated today) |
| 12 | ₹99 for an existing shop | Report + fixes pack: full competitor report, written fixes, 3 posts, review QR card |
| 13 | Verification code (simulated) | Entered in the web app, not Telegram |
| 14 | Ownership | Owner becomes primary owner via an invite to his Gmail; Pinwaala stays manager |
| 15 | Telegram | One-way updates after payment; chat later |
| 16 | Referrer | `?ref=<name>` in the link, saved with the user |
| 17 | AgenticOrg agent | "Pinwaala Profile Agent": takes the approved fields + snapshot (JSON) from n8n, returns the Google profile (new) or report + fixes (existing) as JSON. Gemini model; no tools |
| 18 | AgenticOrg approval | Every run waits in AgenticOrg **Approvals** for a Pinwaala reviewer (Shipra today). Approve → continue; reject with note → owner told what to fix. **First test** passing the owner's own tap to AgenticOrg's approve API (`POST /api/v1/approvals/{id}/decide`); if AgenticOrg blocks it (requester can't self-approve), keep the Pinwaala reviewer |
| 19 | Getting the result back | AgenticOrg can't call us back, so n8n checks the run status every few seconds until it's approved or rejected |
| 20 | Phone verification | **No login screen.** At step 5, after approval. **Main: Pinwaala calls, press 1** (Vobiz outbound): he types his number → taps **Call me to verify** → Pinwaala calls from `080 6426 9429` → *"Hello, this is Pinwaala. Press 1 to confirm this is your number."* → he presses 1 → ✓ verified. **Tested 24 Oct: works** (`Digits: 1` received; ~12 s call, billed as 1 minute). **Fallback: missed call to Pinwaala** (inbound): **Give a missed call** opens his dialer with `080 6426 9429`; rejected while ringing, ₹0. **Tested 24 Oct with two phones: works.** Then **SMS code via Firebase**. Last resort: typed number, *unverified* (can still pay; flagged in AgenticOrg review) |
| 21 | Telegram | **Optional**, not used for verification: *"Get updates on Telegram"* one tap after verifying |
| 22 | Returning users | No phone login today; the same phone number on the same device resumes progress (kept 24 h) |
| 23 | Vobiz setup | Number **+91 80 6426 9429** (purchased with promo credits) attached to XML Application *Pinwaala missed call test* (inbound). Its answer URL must point to our app (e.g. `https://pinwaala.replit.app/api/vobiz/answer`); test addresses are deleted. Outbound calls are placed by API with the account's Auth ID + Token (in `.env`, never in git) |

**Defaults assumed (change if wrong):** rivals snapshot is called straight from the web app, not n8n (speed); agent asks about 6 questions, 3 minutes max; photo required for new shops, optional for existing; Gmail required for new shops, optional for existing; data stored in Supabase.

## Steps

### 1. Landing

- Logo, headline: *"Get your shop found on Google."*
- **Is your shop on Google Maps?** → **Yes, find it** / **No, not yet** / small link *"Not sure? Check"* (goes to the Yes search; no match → No path)
- Language row: English (active) · বাংলা · हिंदी (*Coming soon*)
- Trust line: *Free to try · no login · you approve everything*

### 2a. YES: find my shop

- Search box: *"Your shop's name and area"* → suggestions with address → **This is my shop**
- **Near me** button → GPS → businesses within ~200 m → pick one
- **Paste Maps link** (fallback) → 3-step picture guide: *Google Maps → your shop → Share → Copy link*
- Not found → *"Looks like you're not on Google yet"* → switch to 2b

### 2b. NO: photo + pin

- **Shop photo:** *"Take a photo with your signboard visible"* (camera or gallery; shrunk on the phone)
- **Location:** *"Are you at your shop now?"* Yes → GPS pin · No → search a landmark/area → **drag the pin to your door** → Confirm
- **Type of shop:** quick picker (Sweets, Grocery, Salon, Tailor, Medical, Restaurant, Other), so rivals can be found right away

### 3. Instant snapshot (≈1–2 seconds)

- **New shop:** map with rival pins (slate) and his pin (marigold, *not on Google yet*). *"12 sweet shops within 1 km are on Google. The top one: 4.6★, 2,300 reviews."*
- **Existing shop:** scorecard vs top 3 nearby: rating, reviews, hours listed, phone, website, photos (up to 10 counted)
- Button: **Tell us about your shop (2 min)** → step 4

### 4. Voice agent conversation

- Starts with the snapshot: *"I can see 12 sweet shops near you. What makes yours different?"*
- About 6 questions: what you sell · opening hours · phone number · who your customers are · what you want more of (calls, walk-ins, orders) · which nearby shop you compete with most
- Max ~3 minutes; he can end early
- Mic blocked → backup flow (decision 6)
- Behind the scenes: Sarvam reads the photo (new shops) while he talks

### 5. Summary → approve or edit (human approval 1)

- Card with every field, each tagged *heard*, *on your signboard*, or *needs confirmation* (signboard and answers disagree, or missing)
- Tap any field to edit
- Must be confirmed: name, type of shop, pin, phone, hours
- Contact: owner's name, **Gmail** (*"the one on your phone: Settings → Google"*)
- After **Yes, this is my shop**: **Verify your number**
  1. He types his 10-digit number → taps **Call me to verify**
  2. Screen: *"We're calling you now from 080 6426 9429. Pick up and press 1."*
  3. His phone rings; he answers and hears *"Hello, this is Pinwaala. Press 1 to confirm this is your number."*
  4. He presses **1** → hears *"Thank you, your number is verified"* → the screen turns ✓ verified (the app checks every second)
- **Missed the call, pressed another key, or it went to voicemail?** → screen offers **Call me again** or **Give us a missed call instead**:
  - *"Give a missed call from this number to verify. It's free, and we won't pick up."* → button opens his dialer with `080 6426 9429` → rejected while ringing → ✓ verified
  - A call from a different number → *"We got a call from a different number. Call from the number you typed, or change it."*
- **Still not verified?** → **Send me an SMS code instead** (Firebase) → 6-digit code
- **Still stuck?** → continue with the typed number, marked *unverified*
- Optional: **Get updates on Telegram** (one tap); WhatsApp: *coming soon*
- Consent line: *"I own or run this shop and allow Pinwaala to set up its Google profile."*
- **Yes, this is my shop** → counted as a user

### 6. Send to n8n

- Photo, conversation fields, Sarvam results, location, Google place ID (existing) → n8n
- n8n merges them into the Google profile data: category, description, hours, attributes, 3 posts; for existing shops, the fixes list and competitor report

### 7. Outcome screen

| **What we found** | **What we'll do** | **What you get for ₹99** |
| --- | --- | --- |
| New: *"12 rivals nearby; you're invisible"* · Existing: *"#5 of 12 by reviews; 3 of 7 basics missing"* | Preview of his profile card + top 3 fixes | New: Google profile created + verification + 3 posts + review QR. Existing: full report + written fixes + 3 posts + review QR. Both: updates in the app (and on Telegram if connected) |

- Button: **Unlock for ₹99**
- Small print: *"If Google can't verify your shop, we refund or credit your ₹99."*

### 8. Pay ₹99 (Pine Labs checkout)

- Pine Labs checkout → success screen + receipt

### 8b. Agent prepares + Pinwaala review (human approval 2)

- Right after payment, the screen shows *"Our team is checking your profile. We'll update this page (and Telegram, if connected) in a few minutes."*
- n8n sends the approved data to the AgenticOrg agent → the run waits in **AgenticOrg Approvals**
- The reviewer sees one item per shop, e.g. **"Submit Google profile: Bapi Sweets, Koramangala"**, with each field, its source (signboard / voice / owner pin / agent-written) and mismatches highlighted; plus *owner approved ✓ · paid ✓ · phone verified ✓/✗ · Gmail*
- **Reviewer checklist (~30 s):**
  1. Real shop? Real shopfront photo; pin in a sensible place
  2. Matches what he said? Name, phone, hours agree with voice + signboard; mismatches fixed first
  3. Agent's writing safe and true? No invented claims or superlatives, right category, nothing offensive
  4. Follows Google's rules? No keywords stuffed in the name, one profile per shop
- **Approve** → continue to 9a / 9b · **Reject with note** → owner gets the note in the app (and on Telegram if connected) (e.g. *"Please confirm your phone number"*); nothing is sent
- Existing shops: the reviewer approves the report + fixes before they're released

### 9a. After payment: new shop (simulated today)

1. *"Your Google profile is created as a draft."*
2. *"Verification started. Google is sending a code to your shop's phone."*
3. 5-digit code box → **Submit** (human approval 3)
4. *"Your shop is live on Google"* (labelled *simulated: pending Google partner access*)
5. *"Ownership invite sent to your Gmail. Accept it to own your profile."*
6. Posts (Copy) and review QR (download)

### 9b. After payment: existing shop

- Full competitor report, written fixes (copy buttons), 3 posts, review QR card (links to his real review page)

### 10. Telegram updates

- Optional, connected at step 5 → one-way messages (the app shows the same progress for everyone): continue-where-you-left-off link · payment received · being checked by our team · approved, verification started (or: *please fix X*) · live · ownership invite sent
- WhatsApp: *coming soon*

## Inputs

| Input | New shop | Existing shop | Source |
| --- | --- | --- | --- |
| On Google? | Yes | Yes | Landing button |
| Shop on Google | — | Required | Search / near me / link |
| Shop photo | Required | Optional | Camera or gallery |
| Pin location | Required | From Google | GPS or landmark + drag |
| Type of shop | Required | From Google | Picker, confirmed in summary |
| What he sells, hours, phone, customers, goals, main rival | From conversation | From conversation | Voice agent |
| Owner name, phone | Required | Required | Summary step |
| Gmail | Required | Optional | Summary step |
| Consent | Required | Required | Summary step |
| Referrer | Automatic | Automatic | `?ref=` |

## Edge cases

| Case | Behaviour |
| --- | --- |
| Can't find his shop in search | Offer near me, then paste link, then switch to the No path |
| GPS blocked or wrong | Landmark search + drag the pin |
| Signboard and answers disagree | Field marked *needs confirmation* |
| Agent can't hear / he goes silent | Agent asks again once, then offers the voice-note backup |
| Mic blocked | Voice-note backup; then typing |
| No Gmail | Show how to find it on his phone; allow "add later" (ownership invite waits) |
| Payment fails | Retry; nothing unlocked |
| Reviewer rejects | Owner gets the note; fixes in the app; resubmits (no new payment) |
| Review takes long | App shows *"checking"*; Telegram update when done if connected |
| No Telegram | Nothing lost: verification is by phone call; progress shows in the app |
| Doesn't answer our call / voicemail / presses another key | Offer **Call me again** or the missed-call fallback |
| Missed call from a different number | Not verified; asked to call from the typed number or change it |
| Neither call works within ~2 minutes | Offer the SMS code (Firebase); then continue unverified |
| Vobiz down | SMS code (Firebase) |
| Too many "call me" taps | Max 3 calls per number per 10 minutes (each outbound call is billed as at least 1 minute) |
| Shares a different number than the shop's | Fine: the shop phone for Google stays as he confirmed it; the shared number is his contact |
| Leaves halfway | Progress kept on the phone for 24 hours |

## Data

- **Stored:** photo, fields, pin, Google place ID, owner name, phone (+ verified flag and method: press-1 call / missed call / SMS / unverified), Telegram user id (if connected), Gmail, consent, referrer, payment status, Telegram link
- **Not stored after processing:** raw audio
- **Never stored or logged:** verification codes

## Later (not today)

Real Google profile creation and verification through Pinwaala's organization account (after API access), Telegram/WhatsApp two-way chat (forward the code, edit by voice), বাংলা and हिंदी, QR posters, weekly posts, review replies, ₹499/month assistant.
