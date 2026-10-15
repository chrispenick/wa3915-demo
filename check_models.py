#!/usr/bin/env python3
"""Check which Gemini models are available via a Vocareum API key.

Vocareum proxies only a subset of Gemini endpoints and does not expose
/v1beta/models (model listing). This script probes each model directly
with a minimal generateContent call and reports status.

Usage:
    uv run python check_models.py
"""
import os
import sys
import time
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("GEMINI_API_KEY", "")
BASE_URL = os.environ.get("GOOGLE_GEMINI_BASE_URL", "https://generativelanguage.googleapis.com").rstrip("/")

if not API_KEY:
    print("ERROR: GEMINI_API_KEY not set (check your .env)")
    sys.exit(1)

try:
    import requests
except ImportError:
    print("ERROR: requests not installed — run: uv add requests")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Models to probe — (google_name, vocareum_alias_or_same)
# google_name   : canonical Google model ID
# voc_name      : alias to try on Vocareum (same if no known alias)
# ---------------------------------------------------------------------------
PROBE_MODELS: list[tuple[str, str]] = [
    # Gemini 1.0
    ("gemini-1.0-pro",            "gemini-1.0-pro"),
    ("gemini-1.0-pro-001",        "gemini-1.0-pro-001"),
    # Gemini 1.5
    ("gemini-1.5-pro",            "gemini-1.5-pro"),
    ("gemini-1.5-pro-001",        "gemini-1.5-pro-001"),
    ("gemini-1.5-pro-002",        "gemini-1.5-pro-002"),
    ("gemini-1.5-flash",          "gemini-1.5-flash"),
    ("gemini-1.5-flash-001",      "gemini-1.5-flash-001"),
    ("gemini-1.5-flash-002",      "gemini-1.5-flash-002"),
    ("gemini-1.5-flash-8b",       "gemini-1.5-flash-8b"),
    # Gemini 2.0
    ("gemini-2.0-flash",          "gemini-2.0-flash"),
    ("gemini-2.0-flash-001",      "gemini-2.0-flash-001"),
    ("gemini-2.0-flash-lite",     "gemini-2.0-flash-lite"),
    ("gemini-2.0-flash-lite-001", "gemini-2.0-flash-lite-001"),
    # Gemini 2.5
    ("gemini-2.5-flash",          "gemini-2.5-flash"),
    ("gemini-2.5-pro",            "gemini-2.5-pro"),
    # Vocareum-reported alias from .env (non-standard Google name)
    ("-",                         "gemini-3.5-flash"),
]


def probe(model_id: str) -> tuple[str, str]:
    """Try generateContent. Returns (status, note)."""
    url = f"{BASE_URL}/v1beta/models/{model_id}:generateContent"
    payload = {"contents": [{"parts": [{"text": "Reply with one word: ready"}]}]}
    try:
        r = requests.post(url, params={"key": API_KEY}, json=payload, timeout=20)
        if r.status_code == 200:
            # Extract the actual reply to confirm it worked
            try:
                reply = r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                return "OK", f'replied: "{reply[:40]}"'
            except Exception:
                return "OK", "(response parsed but text not extracted)"
        err = r.json().get("error", {})
        msg = err.get("message", r.text[:100])
        return f"HTTP {r.status_code}", msg[:100]
    except requests.exceptions.Timeout:
        return "TIMEOUT", "request timed out after 20s"
    except Exception as e:
        return "ERROR", str(e)[:100]


def main():
    print(f"Endpoint : {BASE_URL}")
    print(f"API key  : {API_KEY[:8]}...{API_KEY[-4:]}")
    print(f"Probing {len(PROBE_MODELS)} models...\n")

    rows = []
    for google_name, voc_name in PROBE_MODELS:
        alias_flag = "" if google_name == voc_name or google_name == "-" else f" (alias for {google_name}?)"
        sys.stdout.write(f"  testing {voc_name:<35}")
        sys.stdout.flush()
        status, note = probe(voc_name)
        note_full = note + alias_flag if alias_flag else note
        print(f"{status:<12} {note_full}")
        rows.append((google_name, voc_name, status, note_full))
        time.sleep(0.4)

    # ---------------------------------------------------------------------------
    print()
    print(f"{'Model Name (Google)':<32} {'Model Name (Vocareum)':<32} {'Status':<12} Notes")
    print("-" * 110)
    for google_name, voc_name, status, note in rows:
        g = google_name if google_name != "-" else "(no Google equivalent)"
        print(f"{g:<32} {voc_name:<32} {status:<12} {note}")

    ok = [r for r in rows if r[2] == "OK"]
    print(f"\nAvailable (OK): {len(ok)} / {len(rows)}")
    if ok:
        print("Working models:")
        for _, voc_name, _, _ in ok:
            print(f"  ADK_MODEL={voc_name}")


if __name__ == "__main__":
    main()
