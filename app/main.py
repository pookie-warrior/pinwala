"""Pinwala web app: find shop / pin, rivals snapshot, ElevenLabs voice agent, summary, Vobiz press-1 verification."""
from __future__ import annotations

import hashlib
import json
import threading
import logging
import math
import os
import re
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles

from . import config  # noqa: F401  (loads .env)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("pinwala")

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(os.getenv("DATA_DIR", ROOT / "data"))
DATA.mkdir(parents=True, exist_ok=True)
SHOPS = DATA / "shops.jsonl"

AGENT_ID = os.getenv("ELEVENLABS_AGENT_ID", "agent_8901m5pps90see9ryvcw36zjwzf9")
VOBIZ_FROM = os.getenv("VOBIZ_NUMBER", "918064269429")
KEYS = ("GOOGLE_PLACES_API_KEY", "ELEVENLABS_API_KEY", "VOBIZ_AUTH_ID", "VOBIZ_AUTH_TOKEN", "AGENTICORG_API_KEY",
        "SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY")
AO_BASE = os.getenv("AGENTICORG_BASE_URL", "https://agenticorg.hackathon.pinelabs.com")
AO_AGENT = os.getenv("AGENTICORG_AGENT_ID", "a64642fd-f0a9-4ad7-badd-dda53fccd4ce")

SHOP_TYPES = {"Sweets": "sweet shop", "Grocery": "grocery store", "Bakery": "bakery", "Salon": "beauty salon",
              "Tailor": "tailor", "Medical": "pharmacy", "Restaurant": "restaurant", "Other": "shop"}

app = FastAPI(title="Pinwala")
verifications: dict[str, dict] = {}
reviews: dict[str, dict] = {}


# ------------------------------------------------------------------ helpers

def http(method: str, url: str, body: dict | None = None, headers: dict | None = None, timeout: int = 30):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Content-Type": "application/json", **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, {"error": e.read().decode(errors="replace")[:300]}


def places(path: str, body: dict | None, mask: str, method: str = "POST"):
    return http(method, f"https://places.googleapis.com/v1/{path}", body,
                {"X-Goog-Api-Key": os.getenv("GOOGLE_PLACES_API_KEY", ""), "X-Goog-FieldMask": mask})


def base_url(req: Request) -> str:
    env = os.getenv("PUBLIC_BASE_URL")
    if env and "localhost" not in env:
        return env.rstrip("/")
    proto = req.headers.get("x-forwarded-proto", req.url.scheme)
    return f"{proto}://{req.headers.get('host')}"


def save(record: dict):
    with SHOPS.open("a") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def last10(n: str) -> str:
    return re.sub(r"\D", "", n or "")[-10:]


# ------------------------------------------------------------------ API: health / stats

@app.get("/api/health")
def health():
    return {"ok": True, "keys": {k: bool(os.getenv(k)) for k in KEYS}}


# ------------------------------------------------------------------ events (Supabase) for the live counter

def sb(method: str, path: str, body=None, prefer: str = ""):
    url, key = os.getenv("SUPABASE_URL", "").rstrip("/"), os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    if not url or not key:
        return 0, None
    h = {"apikey": key, "Authorization": f"Bearer {key}"}
    if prefer:
        h["Prefer"] = prefer
    return http(method, f"{url}/rest/v1/{path}", body, h, timeout=10)


def phone_hash(phone: str) -> str:
    return hashlib.sha256(("pinwala:" + last10(phone)).encode()).hexdigest()


def log_event(kind: str, **kw):
    def go():
        st, r = sb("POST", "pinwala_events", {"kind": kind, **{k: v for k, v in kw.items() if v is not None}},
                   prefer="return=minimal")
        if st not in (200, 201, 204):
            log.warning("event %s not saved: %s %s", kind, st, r)
    threading.Thread(target=go, daemon=True).start()


_stats_cache = {"at": 0.0, "data": None}


@app.get("/api/stats")
def stats():
    if _stats_cache["data"] and time.time() - _stats_cache["at"] < 5:
        return _stats_cache["data"]
    out = {"shops_checked": 0, "onboarded": 0, "pay_interest": 0, "recent": []}
    for kind in ("shop_checked", "onboarded", "pay_interest"):
        sel = "phone_hash" if kind != "shop_checked" else "id"
        st, rows = sb("GET", f"pinwala_events?select={sel}&kind=eq.{kind}&limit=10000")
        if st == 200 and isinstance(rows, list):
            out["shops_checked" if kind == "shop_checked" else kind] = (
                len(rows) if kind == "shop_checked" else len({r["phone_hash"] for r in rows if r.get("phone_hash")}))
    st, rows = sb("GET", "pinwala_events?select=kind,shop_type,area,created_at&kind=in.(onboarded,pay_interest)"
                  "&order=created_at.desc&limit=3")
    if st == 200 and isinstance(rows, list):
        out["recent"] = rows
    _stats_cache.update(at=time.time(), data=out)
    return out


@app.post("/api/event/checked")
async def event_checked(req: Request):
    b = await req.json()
    log_event("shop_checked", session_id=b.get("session"), shop_type=b.get("kind"), area=b.get("area"),
              ref=b.get("ref"), detail={"listed": b.get("listed"), "rival_count": b.get("rival_count")})
    return {"ok": True}


@app.post("/api/event/pay")
async def event_pay(req: Request):
    b = await req.json()
    x = verifications.get(b.get("vid", ""))
    if not x or x["status"] != "verified":
        return JSONResponse({"error": "Verify your number first"}, 400)
    log_event("pay_interest", session_id=b.get("session"), phone_hash=phone_hash(x["phone"]),
              phone_last4=x["phone"][-4:], shop_type=b.get("kind"), area=b.get("area"), ref=b.get("ref"),
              detail={"price": 99, "record": b.get("record")})
    return {"ok": True}


# ------------------------------------------------------------------ API: Google Places

@app.get("/api/autocomplete")
def autocomplete(q: str, lat: float = 12.9716, lng: float = 77.5946):
    st, b = places("places:autocomplete", {"input": q, "includedRegionCodes": ["in"],
                   "locationBias": {"circle": {"center": {"latitude": lat, "longitude": lng}, "radius": 5000}}}, "*")
    out = [{"id": s["placePrediction"]["placeId"], "text": s["placePrediction"]["text"]["text"]}
           for s in b.get("suggestions", []) if "placePrediction" in s] if st == 200 else []
    return {"suggestions": out[:6]}


@app.get("/api/place/{pid}")
def place(pid: str):
    st, b = places(f"places/{pid}", None, "id,displayName,formattedAddress,location,nationalPhoneNumber,websiteUri,rating,"
                   "userRatingCount,regularOpeningHours.weekdayDescriptions,photos,reviews,googleMapsUri,"
                   "primaryTypeDisplayName", method="GET")
    if st != 200:
        return JSONResponse({"error": "place lookup failed"}, 502)
    return {"id": b["id"], "name": b["displayName"]["text"], "address": b.get("formattedAddress"),
            "lat": b["location"]["latitude"], "lng": b["location"]["longitude"],
            "category": (b.get("primaryTypeDisplayName") or {}).get("text", "shop"),
            "rating": b.get("rating"), "reviews": b.get("userRatingCount", 0),
            "phone": bool(b.get("nationalPhoneNumber")), "website": bool(b.get("websiteUri")),
            "hours": bool((b.get("regularOpeningHours") or {}).get("weekdayDescriptions")),
            "photos": len(b.get("photos", [])), "maps": b.get("googleMapsUri"),
            "review_link": f"https://search.google.com/local/writereview?placeid={b['id']}"}


@app.get("/api/rivals")
def rivals(lat: float, lng: float, kind: str = "shop", exclude: str = ""):
    dlat, dlng = 0.009, 0.009 / max(math.cos(math.radians(lat)), 0.2)
    st, b = places("places:searchText", {"textQuery": kind, "pageSize": 20, "locationRestriction": {"rectangle": {
        "low": {"latitude": lat - dlat, "longitude": lng - dlng}, "high": {"latitude": lat + dlat, "longitude": lng + dlng}}}},
        "places.id,places.displayName,places.rating,places.userRatingCount,places.location")
    ps = [p for p in (b.get("places", []) if st == 200 else []) if p["id"] != exclude]
    out = [{"name": p["displayName"]["text"], "rating": p.get("rating"), "reviews": p.get("userRatingCount", 0),
            "lat": p["location"]["latitude"], "lng": p["location"]["longitude"]} for p in ps]
    out.sort(key=lambda r: -(r["reviews"] or 0))
    return {"count": len(out), "capped": len(out) >= 19, "rivals": out}


# ------------------------------------------------------------------ API: ElevenLabs results

@app.get("/api/conversation/{cid}")
def conversation(cid: str):
    st, b = http("GET", f"https://api.elevenlabs.io/v1/convai/conversations/{cid}",
                 headers={"xi-api-key": os.getenv("ELEVENLABS_API_KEY", "")})
    if st != 200:
        return JSONResponse({"ready": False}, 200)
    res = (b.get("analysis") or {}).get("data_collection_results") or {}
    if not res:
        return {"ready": False}
    return {"ready": True, "fields": {k: (v or {}).get("value") for k, v in res.items()}}


# ------------------------------------------------------------------ API: approve + Vobiz press-1 verification

@app.post("/api/approve")
async def approve(req: Request):
    body = await req.json()
    rec = {"id": uuid.uuid4().hex[:10], "at": time.strftime("%Y-%m-%d %H:%M:%S"), **body}
    save(rec)
    reviews[rec["id"]] = {"status": "sending"}
    threading.Thread(target=send_to_agenticorg, args=(rec,), daemon=True).start()
    return {"ok": True, "id": rec["id"]}


def send_to_agenticorg(rec: dict):
    """Pinwala Profile Agent on AgenticOrg; every run stops for human approval (hitl_triggered)."""
    f = rec.get("fields") or {}
    shop = {"shop_type": rec.get("kind"), "heard": {k: v for k, v in f.items() if v},
            "signboard": None, "pin": {"lat": rec.get("lat"), "lng": rec.get("lng")},
            "existing_listing": {"place_id": rec.get("place_id")} if rec.get("listed") else None,
            "rivals": rec.get("rivals"), "rivals_within_1km": rec.get("rival_count"),
            "owner_name": rec.get("owner") or None}
    task = "Prepare the Google Business Profile for this shop. Input JSON:\n" + json.dumps(shop, ensure_ascii=False)
    st, d = http("POST", f"{AO_BASE}/api/v1/agents/{AO_AGENT}/run",
                 {"action": "process", "inputs": {"task": task}, "context": {"pinwala_id": rec["id"]}},
                 {"Authorization": f"Bearer {os.getenv('AGENTICORG_API_KEY', '')}"}, timeout=120)
    if st != 200:
        log.warning("agenticorg run failed %s %s", st, d)
        reviews[rec["id"]] = {"status": "failed"}
        return
    out = d.get("output")
    if isinstance(out, str):
        try:
            out = json.loads(out)
        except ValueError:
            out = {}
    out = out if isinstance(out, dict) else {}
    posts = [p for p in (out.get("posts") or []) if isinstance(p, str) and p.strip()]
    reviews[rec["id"]] = {"status": d.get("status"), "confidence": d.get("confidence"),
                          "correlation_id": d.get("correlation_id"), "post": posts[0] if posts else None,
                          "description": (out.get("profile") or {}).get("description"),
                          "needs_confirmation": out.get("needs_confirmation") or []}
    log.info("agenticorg %s -> %s %s", rec["id"], d.get("status"), d.get("correlation_id"))


@app.get("/api/review/{rid}")
def review(rid: str):
    return reviews.get(rid, {"status": "unknown"})


@app.post("/api/verify/call")
async def verify_call(req: Request):
    body = await req.json()
    phone = last10(body.get("phone", ""))
    if len(phone) != 10:
        return JSONResponse({"error": "Enter a 10-digit mobile number"}, 400)
    recent = [v for v in verifications.values() if v["phone"] == phone and time.time() - v["at"] < 600]
    if len(recent) >= 3:
        return JSONResponse({"error": "Too many calls. Try the missed-call option."}, 429)
    vid = uuid.uuid4().hex[:12]
    verifications[vid] = {"phone": phone, "status": "calling", "at": time.time(), "record": body.get("record") or {}}
    aid, tok = os.getenv("VOBIZ_AUTH_ID", ""), os.getenv("VOBIZ_AUTH_TOKEN", "")
    b = base_url(req)
    st, r = http("POST", f"https://api.vobiz.ai/api/v1/Account/{aid}/Call/", {
        "from": VOBIZ_FROM, "to": "91" + phone, "answer_url": f"{b}/api/vobiz/answer?v={vid}", "answer_method": "POST",
        "hangup_url": f"{b}/api/vobiz/hangup?v={vid}", "hangup_method": "POST",
        "time_limit": 60, "hangup_on_ring": 40, "caller_name": "Pinwala"}, {"X-Auth-ID": aid, "X-Auth-Token": tok})
    if st not in (200, 201):
        verifications[vid]["status"] = "failed"
        log.warning("vobiz call failed %s %s", st, r)
        return JSONResponse({"error": "Could not place the call"}, 502)
    return {"vid": vid}


@app.post("/api/verify/missed")
async def verify_missed(req: Request):
    """Register a pending missed-call verification; the inbound call's From number completes it."""
    body = await req.json()
    phone = last10(body.get("phone", ""))
    if len(phone) != 10:
        return JSONResponse({"error": "Enter a 10-digit mobile number"}, 400)
    vid = uuid.uuid4().hex[:12]
    verifications[vid] = {"phone": phone, "status": "awaiting_missed", "at": time.time(), "record": body.get("record") or {}}
    return {"vid": vid}


@app.get("/api/verify/{vid}")
def verify_status(vid: str):
    v = verifications.get(vid)
    return {"status": v["status"] if v else "unknown"}


@app.post("/api/vobiz/answer")
async def vobiz_answer(req: Request, v: str = ""):
    form = dict(await req.form())
    if not v:  # inbound missed call: verify by caller number, reject unanswered
        frm = last10(form.get("From", ""))
        for x in verifications.values():
            if x["phone"] == frm and x["status"] in ("awaiting_missed", "calling", "missed") and time.time() - x["at"] < 900:
                x["status"] = "verified"
                r = x.get("record") or {}
                log_event("onboarded", session_id=r.get("session"), phone_hash=phone_hash(frm), phone_last4=frm[-4:],
                          shop_type=r.get("kind"), area=r.get("area"), ref=r.get("ref"), detail={"method": "missed_call"})
        return Response("<Response><Hangup/></Response>", media_type="application/xml")
    act = f"{base_url(req)}/api/vobiz/keypress?v={v}"
    xml = (f'<Response><Gather inputType="dtmf" numDigits="1" executionTimeout="15" action="{act}" method="POST">'
           "<Speak>Hello, this is Pinwala. Press 1 to confirm this is your number.</Speak></Gather>"
           "<Speak>We did not get your answer. Goodbye.</Speak></Response>")
    return Response(xml, media_type="application/xml")


@app.post("/api/vobiz/keypress")
async def vobiz_keypress(req: Request, v: str = ""):
    form = dict(await req.form())
    x = verifications.get(v)
    if x and form.get("Digits") == "1":
        x["status"] = "verified"
        r = x.get("record") or {}
        log_event("onboarded", session_id=r.get("session"), phone_hash=phone_hash(x["phone"]), phone_last4=x["phone"][-4:],
                  shop_type=r.get("kind"), area=r.get("area"), ref=r.get("ref"), detail={"method": "press1", "record": r.get("id")})
        return Response("<Response><Speak>Thank you. Your number is verified.</Speak><Hangup/></Response>",
                        media_type="application/xml")
    if x:
        x["status"] = "missed"
    return Response("<Response><Speak>Okay. Goodbye.</Speak><Hangup/></Response>", media_type="application/xml")


@app.post("/api/vobiz/hangup")
async def vobiz_hangup(v: str = ""):
    x = verifications.get(v)
    if x and x["status"] == "calling":
        x["status"] = "missed"
    return Response("<Response/>", media_type="application/xml")


@app.get("/api/config")
def client_config():
    return {"agent_id": AGENT_ID, "shop_types": list(SHOP_TYPES), "vobiz_number": "080 6426 9429",
            "kinds": SHOP_TYPES}


app.mount("/", StaticFiles(directory=ROOT / "static", html=True), name="static")
