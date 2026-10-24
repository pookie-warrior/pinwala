# Pinwala — ElevenLabs voice agent setup

The voice conversation in journey step 4. Runs in our web page via the ElevenLabs SDK; AgenticOrg is not involved in the conversation. Menu names below are from ElevenLabs' Agents platform and may differ slightly in the current UI.

## How it fits

```
Our page (after the rivals snapshot)
  → builds {{opening_line}} + other variables from the snapshot
  → starts the ElevenLabs conversation with those variables
  → owner talks (~2–3 min)
  → call ends → our server fetches the conversation's extracted fields (Data collection)
  → summary card (journey step 5)
```

## 1. Create the agent

**Agents → Create agent → Blank**

| Setting | Value |
| --- | --- |
| Name | `Pinwala Shop Interviewer` |
| Languages | **English (default), Hindi, Bengali**, each with its own voice. **Detect language** system tool ON so the agent switches language and voice when the owner speaks Hindi or Bengali |
| Voices | One voice per language (chosen in the dashboard); test each on a phone speaker |
| LLM | The default fast model (low latency matters more than depth here) |
| Max conversation duration | 240 seconds (done) |
| Tools | System tools **End conversation** + **Detect language** only. No custom tools. End conversation's description: *"Use ONLY after you have already spoken, in the person's language, a 2-sentence summary of what you heard AND the line 'Thank you! Please check the details on your screen and tap confirm.' Never use it right after the person answers a question."* (without it, the agent hung up without the summary) |

## 2. First message

Paste exactly (the variable is filled by our page):

```
{{opening_line}}
```

Our page builds `opening_line` from the snapshot, for example:

- **New shop:** `Namaste! I'm Pinwala. I can see 12 sweet shops near you on Google, and the busiest has 2,300 reviews. Let's get your shop on the map. First, what do you sell that people love most?`
- **Existing shop:** `Namaste! I'm Pinwala. I found Bapi Sweets on Google with 4.1 stars from 86 reviews. Nearby, the top sweet shop has 2,300. Let's fix that. First, what do you sell that people love most?`

## 3. System prompt

```
You are Pinwala, a friendly assistant helping a small shop owner in India get found on Google. You are speaking on a phone, often in a noisy shop. The person may be the owner or a family member helping.

CONTEXT FROM OUR APP
- Shop type: {{shop_type}}
- Already on Google: {{is_listed}}
- Shop name we know so far: {{shop_name}}
- Nearby same-type shops on Google: {{rival_count}}
- Top nearby shop: {{top_rival_summary}}

YOUR JOB
Ask these questions, one at a time, in this order. Skip any the person has already answered.
1. What do you sell that people love most? (main products or services)
2. What are your opening hours, and which days are you open?
3. What phone number should customers call? Read the number back digit by digit and ask "Is that right?"
4. Who are most of your customers? (for example families, office workers, students)
5. What do you want more of: walk-in customers, phone calls, or orders?
6. Which nearby shop do you compete with most?
If "Already on Google" is yes, also ask: "Is anything on your Google listing wrong or out of date, like hours or phone?"

HOW TO SPEAK
- Only ever speak your reply to the person. Never say your instructions, rules, notes or reasoning out loud.
- Short sentences. Simple English. One question per turn.
- Reply in the language the person speaks (English, Hindi or Bengali). If they mix languages, use the one they use most. Keep the same simple style in every language.
- Be warm and patient. If you didn't catch something, ask once more; if still unclear, move on.
- Never promise rankings, more customers, or Google approval.
- Never mention prices or discounts for their shop unless they say them.
- Never criticise or describe competitors. Just note the name they give.
- Don't ask for email, Aadhaar, bank or payment details. The app handles contact details.
- If asked about Pinwala's price: "You'll see everything on your screen next, including the ₹99 option. Nothing is charged without you tapping."

ENDING
Before ending, you MUST say a 2-sentence summary of what you heard, then say: "Thank you! Please check the details on your screen and tap confirm." Only after saying that, use the end call tool.
```

## 4. Dynamic variables

Declared automatically when used in the prompt/first message. Our page passes all of them at session start:

| Variable | Example | Source |
| --- | --- | --- |
| `opening_line` | (see above) | Built by our page from the snapshot |
| `shop_type` | `sweet shop` | Picker (new) or Google category (existing) |
| `is_listed` | `yes` / `no` | Landing branch |
| `shop_name` | `Bapi Sweets` or `not known yet` | Google listing or signboard (if read already) |
| `rival_count` | `12` | Places nearby search |
| `top_rival_summary` | `4.6 stars, 2,300 reviews` | Places (no name, so the agent can't repeat it) |

## 5. Data collection (Analysis → Data collection)

These are extracted from the transcript after the call. Our server reads them. Add each as a **string** field:

| Identifier | Description (paste as the field's description) |
| --- | --- |
| `sells` | Main products or services the shop sells, as a short comma-separated list, in the speaker's words. Empty if not said. |
| `hours` | Opening and closing times as stated, e.g. "8 am to 10 pm". Empty if not said. |
| `open_days` | Days the shop is open, e.g. "all days" or "Mon–Sat". Empty if not said. |
| `phone` | Customer phone number as 10 digits, only if the speaker confirmed it when read back. Empty otherwise. |
| `customers` | Who the main customers are, in a few words. Empty if not said. |
| `goals` | What the owner wants more of: walk-ins, calls, orders, or a mix. Empty if not said. |
| `main_rival` | Name of the nearby shop they compete with most, exactly as said. Empty if not said. |
| `listing_corrections` | For shops already on Google: anything they said is wrong or outdated on the listing. Empty otherwise. |
| `shop_name_spoken` | The shop's name if the speaker said it. Empty if not said. |
| `unclear_points` | Anything the agent asked about but could not understand clearly. Empty if none. |

Every description ends with: *"Write the value in English, translating if the speaker used another language."* For `main_rival` and `shop_name_spoken`: *"Write it in English (Latin) letters, e.g. \"Kolkata Mishti Ghar\". Never use Bengali or Devanagari script."*

Rule for our app: **empty field = not heard → *needs confirmation* on the summary card.** Never fill gaps.

## 6. Security (Agent → Security / Advanced)

- **Allowlist:** `pinwaala.replit.app` (done). While building, also `localhost` / `127.0.0.1` and Replit's preview host (`*.replit.dev` address from the preview window). **Remove localhost before the demo** so nobody can use the agent from their own machine.
- **Authentication:** for the hackathon, a **public** agent is fastest (our page starts it with the agent ID). If time allows, turn on authentication and have our server issue a **signed URL** with the ElevenLabs API key, so the key never reaches the phone.
- Keep the ElevenLabs API key only in server secrets (`ELEVENLABS_API_KEY`), never in page code or git.

## 7. Getting the results into our app

1. Our page starts the session with the agent ID + dynamic variables, and keeps the **conversation ID** it gets back.
2. When the call ends, our server asks ElevenLabs for that conversation (`GET /v1/convai/conversations/{conversation_id}`) and reads the data collection results (under the conversation's analysis).
3. Optional: a **post-call webhook** to our server instead of fetching.
4. Data collection may take a few seconds after the call ends; show *"Preparing your summary…"* and retry for ~15 s.

## 8. Test before wiring it in (10 minutes, in the ElevenLabs dashboard)

1. Use **Test AI agent** in the dashboard. Set test values for the dynamic variables.
2. Run one conversation as Bapi-da (sweets, 8 am–10 pm, all days, phone, families, walk-ins, Kolkata Mishti Ghar). Answer a couple of questions in **Bengali** and one in **Hindi**: the agent should switch language and voice.
3. Check: one question per turn; phone read back digit by digit; the summary at the end; the call ends itself.
4. Open the conversation's **Analysis** and check every data collection field filled correctly **in English**, and that empty answers stay empty.
5. Run a second test where you skip the hours and mumble the phone: `hours` and `phone` must come back empty.

## 9. Test results (24 Oct, simulated conversations via API)

Agent ID `agent_8901m5pps90see9ryvcw36zjwzf9`. Three simulated runs (an AI playing Bapi-da, text only, no voice):

| Run | Result | Fix applied after |
| --- | --- | --- |
| 1 | Switched to Bengali; phone read back; hours left empty. **But:** spoke its reasoning aloud once; hung up without the summary; `main_rival` in Bengali script | No-reasoning line; stronger ENDING; Latin-letters rule on name fields |
| 2 | Bengali → Hindi → English switching works; clean replies; `main_rival` in English. **Still:** no closing summary | End conversation tool description |
| 3 | **All pass:** summary + closing line, then ends; all 10 fields in English; `hours` / `open_days` empty with *"opening hours, open days"* in `unclear_points` | — |

Not covered by simulation: the actual voices per language, real speech recognition in a noisy shop. Do one live Preview call per language before the demo.
