"""Tiny stdlib HTTP helpers shared by the scripts (no requests/httpx dependency)."""
from __future__ import annotations

import base64
import json
import sys
import urllib.error
import urllib.request
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app import config  # noqa: E402,F401  (loads .env)


def call(url: str, *, data: bytes | None = None, headers: dict | None = None, method: str | None = None,
         timeout: int = 90) -> tuple[int, dict | str]:
    req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            status, body = r.status, r.read()
    except urllib.error.HTTPError as e:
        status, body = e.code, e.read()
    try:
        return status, json.loads(body)
    except ValueError:
        return status, body.decode(errors="replace")[:500]


def post_json(url: str, payload: dict, headers: dict | None = None, timeout: int = 90):
    return call(url, data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json", **(headers or {})}, timeout=timeout)


def post_multipart(url: str, fields: dict, files: dict[str, tuple[str, bytes, str]], headers: dict | None = None,
                   timeout: int = 90):
    boundary = uuid.uuid4().hex
    out = bytearray()
    for k, v in fields.items():
        out += f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
    for k, (fname, blob, ctype) in files.items():
        out += (f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"; filename="{fname}"\r\n'
                f'Content-Type: {ctype}\r\n\r\n').encode() + blob + b"\r\n"
    out += f"--{boundary}--\r\n".encode()
    return call(url, data=bytes(out), timeout=timeout,
                headers={"Content-Type": f"multipart/form-data; boundary={boundary}", **(headers or {})})


def basic_auth(user: str, pw: str) -> str:
    return "Basic " + base64.b64encode(f"{user}:{pw}".encode()).decode()


def short(body) -> str:
    """One-line error summary from an API error body."""
    if isinstance(body, dict):
        err = body.get("error", body)
        if isinstance(err, dict):
            return str(err.get("message") or err)[:200]
        return str(err)[:200]
    return str(body)[:200]
