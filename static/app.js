const voiceLib = () => import("https://esm.sh/@elevenlabs/client");

const app = document.getElementById("app");
const S = { kind: "shop", type: null, listed: null, place: null, lat: null, lng: null, rivals: null, fields: null, area: "" };
const REF = new URLSearchParams(location.search).get("ref") || "";
const SESSION = (() => { try { let x = localStorage.getItem("pw_s"); if (!x) { x = Math.random().toString(36).slice(2, 12); localStorage.setItem("pw_s", x); } return x; } catch { return Math.random().toString(36).slice(2, 12); } })();
const post = (p, b) => api(p, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(b) });
let CFG = {};
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const api = async (p, o) => (await fetch(p, o)).json();
const view = (html) => { app.innerHTML = html; window.scrollTo(0, 0); };

async function boot() {
  CFG = await api("/api/config");
  voiceLib().catch(() => {});
  landing();
  refreshStats(); setInterval(refreshStats, 10000);
}

async function refreshStats() {
  try {
    const s = await api("/api/stats");
    const el = document.getElementById("stats"); if (!el) return;
    el.innerHTML = `<span><b>${s.shops_checked}</b> shops checked</span><span><b>${s.onboarded}</b> owners verified</span><span><b>${s.pay_interest}</b> ready to pay ₹99</span>`;
    const r = (s.recent || [])[0], rc = document.getElementById("recent");
    if (r && rc) { const mins = Math.max(1, Math.round((Date.now() - Date.parse(r.created_at)) / 60000));
      rc.textContent = `A ${r.shop_type || "shop"}${r.area ? " in " + r.area : ""} just ${r.kind === "pay_interest" ? "reserved the ₹99 pack" : "verified and started"} · ${mins < 60 ? mins + " min ago" : "today"}`; }
  } catch {}
}

function landing() {
  view(`
    <div class="stats" id="stats"></div>
    <h1>Get your shop found on Google.</h1>
    <p class="lead">See how many shops near you are on Google in 10 seconds. Then talk for two minutes and Pinwala prepares your profile. You approve everything.</p>
    <p class="recent" id="recent"></p>
    <div class="langs"><span class="chip on">English</span><span class="chip soon">বাংলা · soon</span><span class="chip soon">हिंदी · soon</span></div>
    <div class="card"><h2>Check your street: is your shop on Google Maps?</h2>
      <button class="btn primary" id="yes">Yes, find my shop</button>
      <button class="btn dark" id="no">No, not yet</button></div>`);
  document.getElementById("yes").onclick = () => { S.listed = true; findShop(); };
  document.getElementById("no").onclick = () => { S.listed = false; newShop(); };
}

function locate() {
  return new Promise((res) => navigator.geolocation
    ? navigator.geolocation.getCurrentPosition((p) => res({ lat: p.coords.latitude, lng: p.coords.longitude }), () => res(null), { timeout: 8000 })
    : res(null));
}

function findShop() {
  view(`<h2>Find your shop</h2>
    <div class="card"><input id="q" placeholder="Shop name and area, e.g. Anand Sweets Koramangala" autocomplete="off">
      <ul class="list" id="res"></ul><p class="muted">Not found? <a href="#" id="notfound">Add it as a new shop</a></p></div>`);
  let t; const q = document.getElementById("q"); q.focus();
  q.oninput = () => { clearTimeout(t); t = setTimeout(async () => {
    if (q.value.trim().length < 3) return;
    const r = await api(`/api/autocomplete?q=${encodeURIComponent(q.value)}`);
    document.getElementById("res").innerHTML = r.suggestions.map((s) => `<li data-id="${esc(s.id)}">${esc(s.text)}</li>`).join("")
      || `<li class="muted">No match yet, keep typing</li>`;
    document.querySelectorAll("#res li[data-id]").forEach((li) => li.onclick = () => pickPlace(li.dataset.id));
  }, 300); };
  document.getElementById("notfound").onclick = (e) => { e.preventDefault(); S.listed = false; newShop(); };
}

async function pickPlace(id) {
  view(`<p class="center">Opening your listing…</p>`);
  const p = await api(`/api/place/${id}`);
  if (p.error) return view(`<p class="err">Couldn't open that listing.</p><button class="btn ghost" onclick="location.reload()">Start again</button>`);
  S.place = p; S.lat = p.lat; S.lng = p.lng; S.area = (p.address || "").split(",").slice(-4, -3)[0]?.trim() || ""; S.kind = /sweet|candy|confection|mithai/i.test(p.category) ? "sweet shop" : p.category.toLowerCase();
  snapshot();
}

function newShop() {
  const types = CFG.shop_types || [];
  view(`<h2>Tell us about your shop</h2>
    <div class="card"><p class="muted">What kind of shop?</p>
      <div class="grid">${types.map((t) => `<button data-t="${t}">${t}</button>`).join("")}</div>
      <p class="muted" style="margin-top:16px">Where is it?</p>
      <button class="btn dark" id="gps">📍 I'm at my shop, use my location</button>
      <input id="area" placeholder="Or type your area, e.g. Koramangala, Bengaluru">
      <p class="err" id="e"></p>
      <button class="btn primary" id="go">See shops near me</button></div>`);
  document.querySelectorAll(".grid button").forEach((b) => b.onclick = () => {
    document.querySelectorAll(".grid button").forEach((x) => x.classList.remove("on")); b.classList.add("on"); S.type = b.dataset.t; });
  document.getElementById("gps").onclick = async () => {
    const at = await locate(); if (at) { S.lat = at.lat; S.lng = at.lng; document.getElementById("gps").textContent = "✓ Location found"; }
    else document.getElementById("e").textContent = "Couldn't get your location. Type your area instead."; };
  document.getElementById("go").onclick = async () => {
    const e = document.getElementById("e");
    if (!S.type) return (e.textContent = "Pick the kind of shop first.");
    S.kind = CFG.kinds[S.type];
    if (S.lat == null) {
      const area = document.getElementById("area").value.trim();
      if (!area) return (e.textContent = "Use your location or type your area.");
      const r = await api(`/api/autocomplete?q=${encodeURIComponent(area)}`);
      if (!r.suggestions.length) return (e.textContent = "Couldn't find that area. Try a bigger landmark.");
      const p = await api(`/api/place/${r.suggestions[0].id}`); S.lat = p.lat; S.lng = p.lng; S.area = area.split(",")[0];
    }
    snapshot();
  };
}

async function snapshot() {
  view(`<p class="center">Checking Google Maps near you…</p>`);
  const r = await api(`/api/rivals?lat=${S.lat}&lng=${S.lng}&kind=${encodeURIComponent(S.kind)}&exclude=${S.place ? S.place.id : ""}`);
  S.rivals = r;
  const top = r.rivals[0];
  const n = r.capped ? `${r.count}+` : r.count;
  const dots = r.rivals.map((x) => {
    const dx = (x.lng - S.lng) / 0.0186 * 100 + 50, dy = 50 - (x.lat - S.lat) / 0.018 * 100;
    return `<span class="pin" style="left:${Math.max(3, Math.min(97, dx))}%;top:${Math.max(4, Math.min(96, dy))}%"></span>`;
  }).join("");
  const p = S.place;
  const missing = p ? ["phone", "website", "hours"].filter((k) => !p[k]) : [];
  view(`<h2>${p ? esc(p.name) : "Your shop vs. Google"}</h2>
    <div class="card">
      <div class="map">${dots}<span class="pin me" style="left:50%;top:50%"></span></div>
      ${p
        ? `<p><b>${p.rating ?? "–"}★</b> from <b>${p.reviews}</b> reviews · ${p.photos} photos${missing.length ? ` · missing: ${missing.join(", ")}` : ""}</p>`
        : `<p><span class="big">${n}</span><br>${esc(S.kind)}s within 1 km are on Google. <b>You're not, yet.</b></p>`}
      ${top ? `<p class="muted">Most-reviewed nearby: ${top.rating}★ from ${top.reviews.toLocaleString()} reviews</p>` : ""}
    </div>
    <button class="btn primary" id="talk">🎙️ Save this &amp; tell Pinwala about your shop</button>
    <button class="btn ghost" id="share">Know a shop owner? Send them this</button>`);
  document.getElementById("talk").onclick = () => (S.vid ? talk() : verify());
  post("/api/event/checked", { session: SESSION, kind: S.kind, area: S.area, listed: !!S.place, rival_count: r.count, ref: REF });
  document.getElementById("share").onclick = async () => {
    const url = `${location.origin}/?ref=share`, text = `Is your shop on Google Maps? ${n} ${S.kind}s near here already are. Check in 10 seconds: ${url}`;
    if (navigator.share) { try { await navigator.share({ title: "Pinwala", text, url }); return; } catch {} }
    window.open(`https://t.me/share/url?url=${encodeURIComponent(url)}&text=${encodeURIComponent(text)}`, "_blank");
  };
}

const LANGS = { en: "English", hi: "Hindi", bn: "Bengali" };
function opening() {
  const r = S.rivals, top = r.rivals[0], n = r.count, L = S.lang || "en";
  const rev = top ? top.reviews.toLocaleString("en-IN") : "";
  if (L === "hi") return S.place
    ? `नमस्ते! मैं पिनवाला हूँ। मुझे Google पर ${S.place.name} मिली, जिसके ${S.place.reviews} रिव्यू हैं।${top ? ` आस-पास सबसे ज़्यादा रिव्यू वाली दुकान के ${rev} रिव्यू हैं।` : ""} चलिए आपकी लिस्टिंग और बेहतर बनाते हैं। सबसे पहले, आपकी दुकान में लोगों को सबसे ज़्यादा क्या पसंद है?`
    : `नमस्ते! मैं पिनवाला हूँ। आपके आस-पास Google पर आपके जैसी ${n} दुकानें दिख रही हैं।${top ? ` सबसे ज़्यादा रिव्यू वाली दुकान के ${rev} रिव्यू हैं।` : ""} चलिए आपकी दुकान को भी मैप पर लाते हैं। सबसे पहले, आपकी दुकान में लोगों को सबसे ज़्यादा क्या पसंद है?`;
  if (L === "bn") return S.place
    ? `নমস্কার! আমি পিনওয়ালা। Google-এ ${S.place.name} পেয়েছি, ${S.place.reviews}টি রিভিউ সহ।${top ? ` কাছাকাছি সবচেয়ে বেশি রিভিউ পাওয়া দোকানের ${rev}টি রিভিউ।` : ""} চলুন আপনার লিস্টিং আরও ভালো করি। প্রথমে বলুন, আপনার দোকানের কোন জিনিস লোকে সবচেয়ে বেশি ভালোবাসে?`
    : `নমস্কার! আমি পিনওয়ালা। আপনার কাছাকাছি Google-এ আপনার মতো ${n}টি দোকান আছে।${top ? ` সবচেয়ে বেশি রিভিউ পাওয়া দোকানের ${rev}টি রিভিউ।` : ""} চলুন আপনার দোকানটাও ম্যাপে তুলি। প্রথমে বলুন, আপনার দোকানের কোন জিনিস লোকে সবচেয়ে বেশি ভালোবাসে?`;
  const topTxt = top ? ` The busiest has ${rev} reviews.` : "";
  return S.place
    ? `Namaste! I'm Pinwala. I found ${S.place.name} on Google with ${S.place.reviews} reviews.${topTxt} Let's make your listing stronger. First, what do you sell that people love most?`
    : `Namaste! I'm Pinwala. I can see ${n} ${S.kind}s near you on Google.${topTxt} Let's get your shop on the map. First, what do you sell that people love most?`;
}

function pickLanguage() {
  view(`<h2>Which language should Pinwala speak?</h2><div class="card">
    <button class="btn primary" data-l="en">English</button>
    <button class="btn primary" data-l="hi">हिंदी · Hindi</button>
    <button class="btn primary" data-l="bn">বাংলা · Bengali</button>
    <p class="muted">You can mix in other words. Pinwala will reply in the language you pick.</p></div>`);
  document.querySelectorAll("[data-l]").forEach((b) => b.onclick = () => { S.lang = b.dataset.l; talk(); });
}

async function talk() {
  if (!S.lang) return pickLanguage();
  view(`<h2>Talk to Pinwala</h2><div class="orb" id="orb"></div>
    <p class="center" id="st">Allow the microphone to start.</p>
    <p class="center muted">Pinwala will speak ${LANGS[S.lang]}.</p>
    <button class="btn ghost" id="end">End conversation</button>`);
  const st = document.getElementById("st"), orb = document.getElementById("orb");
  let conv, cid, connected = false, mode = "listening", finishing = false; const startedAt = Date.now();
  const hangUp = () => { if (conv) { try { conv.endSession(); } catch {} } };
  try {
    await navigator.mediaDevices.getUserMedia({ audio: true });
    st.textContent = "Connecting…";
    const { Conversation } = await voiceLib();
    const top = S.rivals.rivals[0];
    conv = await Conversation.startSession({
      agentId: CFG.agent_id,
      connectionType: "websocket",
      overrides: { agent: { language: S.lang } },
      clientTools: {
        // Agent calls this after its closing line; hang up only once it has finished speaking.
        finish_call: async () => { finishing = true; if (mode === "listening") setTimeout(hangUp, 1200); setTimeout(hangUp, 20000); },
      },
      dynamicVariables: {
        opening_line: opening(), language_name: LANGS[S.lang], shop_type: S.kind, is_listed: S.place ? "yes" : "no",
        shop_name: S.place ? S.place.name : "not known yet", rival_count: String(S.rivals.count),
        top_rival_summary: top ? `${top.rating} stars, ${top.reviews} reviews` : "none found",
      },
      onConnect: () => { connected = true; st.textContent = "Listening…"; orb.classList.add("live"); },
      onModeChange: (m) => { mode = m.mode; st.textContent = m.mode === "speaking" ? "Pinwala is speaking…" : "Listening…";
        if (finishing && m.mode === "listening") setTimeout(hangUp, 800); },
      onDisconnect: () => { orb.classList.remove("live");
        if (!connected || Date.now() - startedAt < 5000) { st.innerHTML = `<span class="err">Couldn't connect. Please try again.</span>`; document.getElementById("end").textContent = "Try again"; document.getElementById("end").onclick = talk; return; }
        finish(cid); },
      onError: (e) => { st.textContent = "Connection problem. Please try again."; console.error(e); },
    });
    cid = conv.getId();
  } catch (e) {
    st.innerHTML = `<span class="err">Couldn't start: ${esc(e.message || e)}</span>`;
  }
  document.getElementById("end").onclick = () => conv && conv.endSession();
}

let finished = false;
async function finish(cid) {
  if (finished || !cid) return; finished = true;
  view(`<p class="center">Preparing your summary…</p>`);
  for (let i = 0; i < 15; i++) {
    const r = await api(`/api/conversation/${cid}`);
    if (r.ready) { S.fields = r.fields; return summary(); }
    await new Promise((ok) => setTimeout(ok, 2000));
  }
  view(`<p class="err">Your summary is taking longer than usual.</p><button class="btn primary" id="retry">Try again</button>`);
  document.getElementById("retry").onclick = () => { finished = false; finish(cid); };
}

function summary() {
  const f = S.fields, rows = [
    ["Shop name", S.place ? S.place.name : f.shop_name_spoken], ["Owner", f.owner_name], ["Type", S.kind], ["Sells", f.sells],
    ["Hours", [f.hours, f.open_days].filter(Boolean).join(", ")], ["Phone", f.phone || S.phone],
    ["Customers", f.customers], ["Wants more", f.goals], ["Main rival", f.main_rival],
  ];
  view(`<h2>Is this right?</h2><div class="card">
    ${rows.map(([k, v]) => `<div class="row"><span>${k}</span><span><b>${esc(v || "")}</b> ${v ? `<span class="tag">heard</span>` : `<span class="tag warn">needs confirmation</span>`}</span></div>`).join("")}
    ${f.unclear_points ? `<p class="muted">Couldn't catch: ${esc(f.unclear_points)}</p>` : ""}
    <p class="muted">Your name</p><input id="nm" placeholder="Your name" value="${esc(f.owner_name || "")}">
    <p class="muted">Gmail (the one on your phone)</p><input id="gm" type="email" placeholder="name@gmail.com">
    <label class="muted" style="display:flex;gap:8px;margin-top:12px"><input type="checkbox" id="ok" style="width:auto"> I own or run this shop and allow Pinwala to set up its Google profile.</label>
    <p class="err" id="e"></p>
    <button class="btn primary" id="yes">Yes, this is my shop</button></div>`);
  document.getElementById("yes").onclick = async () => {
    const e = document.getElementById("e");
    if (!document.getElementById("ok").checked) return (e.textContent = "Please tick the consent box.");
    const r = await api("/api/approve", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({
      listed: !!S.place, place_id: S.place?.id || null, kind: S.kind, lat: S.lat, lng: S.lng, fields: S.fields,
      owner: document.getElementById("nm").value, gmail: document.getElementById("gm").value,
      rivals: S.rivals.rivals.slice(0, 5), rival_count: S.rivals.count }) });
    S.recordId = r.id; done(true);
  };
}

function verify() {
  view(`<h2>Verify your number</h2><div class="card">
    <p>Save your result and talk to Pinwala. Verify your mobile number first, it takes one tap.</p>
    <input id="ph" inputmode="numeric" maxlength="10" placeholder="10-digit mobile number">
    <p class="err" id="e"></p>
    <button class="btn primary" id="miss">📞 Give a missed call · free, we won't pick up</button>
    <button class="btn dark" id="call">Or call me, I'll press 1</button>
    <p class="muted" id="hint">Call from the same number you typed. It rings once and cuts.</p></div>`);
  const e = document.getElementById("e"), ph = () => document.getElementById("ph").value;
  const record = { session: SESSION, kind: S.kind, area: S.area, ref: REF };
  const wait = async (vid, btn, label) => {
    for (let i = 0; i < 60; i++) {
      await new Promise((ok) => setTimeout(ok, 2000));
      const st = await api(`/api/verify/${vid}`);
      if (st.status === "verified") { S.vid = vid; S.phone = ph(); refreshStats(); return talk(); }
      if (st.status === "missed" || st.status === "failed") { e.textContent = "We didn't get a 1. Try again, or give us a missed call."; btn.textContent = label; return; }
    }
    e.textContent = "We haven't received your call yet. Try again."; btn.textContent = label;
  };
  document.getElementById("miss").onclick = async () => {
    e.textContent = "";
    const r = await post("/api/verify/missed", { phone: ph(), record });
    if (r.error) return (e.textContent = r.error);
    const b = document.getElementById("miss"); b.textContent = "Waiting for your missed call…";
    location.href = "tel:08064269429";
    wait(r.vid, b, "📞 Give a missed call · free, we won't pick up");
  };
  document.getElementById("call").onclick = async () => {
    e.textContent = "";
    const r = await post("/api/verify/call", { phone: ph(), record });
    if (r.error) return (e.textContent = r.error);
    const b = document.getElementById("call"); b.textContent = "Calling you now… pick up and press 1";
    wait(r.vid, b, "Or call me, I'll press 1");
  };
}

function done(verified) {
  view(`<h1>You're almost on Google.</h1>
    <div class="card">
      <div class="row"><span>Your details</span><span class="tag">approved by you</span></div>
      <div class="row"><span>Phone</span><span class="tag">${verified ? "verified ✓" : "unverified"}</span></div>
      <div class="row"><span>Google profile</span><span class="tag warn" id="ao">sending to our AgenticOrg agent…</span></div>
      <div class="row"><span>Human check</span><span class="tag warn">a Pinwala reviewer approves before anything goes out</span></div>
      <h2 style="margin-top:16px">Listing Pack · ₹99</h2>
      <p class="muted">Google profile set up + verification, 3 posts, review QR card for your counter.</p>
      <button class="btn primary" id="reserve" ${verified ? "" : "disabled"}>Reserve my Listing Pack · ₹99</button>
      <p class="muted" id="rnote">Pay when Pine Labs checkout opens. We'll message you first. No charge now.</p>
      ${S.place ? `<a class="btn dark" href="${esc(S.place.review_link)}" target="_blank" rel="noopener">Open your Google review link</a>` : ""}
      <p class="muted">Updates on Telegram and WhatsApp: coming soon.</p></div>`);
  pollReview();
  const rb = document.getElementById("reserve");
  if (rb) rb.onclick = async () => {
    const r = await post("/api/event/pay", { vid: S.vid, session: SESSION, kind: S.kind, area: S.area, ref: REF, record: S.recordId });
    if (r.error) return (document.getElementById("rnote").textContent = r.error);
    rb.textContent = "Reserved ✓ · ₹99"; rb.disabled = true;
    document.getElementById("rnote").textContent = "Thank you! You're on the list. We'll confirm before any payment.";
    refreshStats();
  };
}

async function pollReview() {
  const el = document.getElementById("ao");
  for (let i = 0; i < 40 && S.recordId; i++) {
    const r = await api(`/api/review/${S.recordId}`);
    if (r.status === "hitl_triggered") { el.textContent = `prepared · waiting for Pinwala reviewer (ref ${r.correlation_id})`; return; }
    if (r.status === "completed") { el.textContent = "prepared and approved"; el.classList.remove("warn"); return; }
    if (r.status === "failed") { el.textContent = "queued for manual preparation"; return; }
    await new Promise((ok) => setTimeout(ok, 1500));
  }
}

boot();
