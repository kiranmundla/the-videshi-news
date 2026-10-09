#!/usr/bin/env python3
"""
One-time backfill: geocode directory listings missing lat/lng.

Finds listings in Supabase directory_listings with an address but null
latitude/longitude, geocodes them via Google Geocoding API, and PATCHes
the coordinates back.

Cost: ~$5 per 1,000 calls (Google Geocoding API, separate from Places budget).
~8,500 listings => ~$43 one-time.

Usage:
    python3 -u pipeline/geocode-backfill.py [--dry-run] [--limit N]

State: pipeline/.state/geocode-backfill.json (resume checkpoint)
"""

import json
import os
import subprocess
import sys
import time
import urllib.parse

# ── Env ──────────────────────────────────────────────────────────────
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

load_env(os.path.expanduser("~/workspace/.env.google-ai"))
load_env(os.path.expanduser("~/workspace/.env.supabase"))

GKEY = os.environ.get("GOOGLE_PLACES_API_KEY") or os.environ.get("GOOGLE_API_KEY", "")
SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
SB_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

if not GKEY:
    print("FATAL: no Google API key (GOOGLE_PLACES_API_KEY/GOOGLE_API_KEY)", flush=True)
    sys.exit(1)
if not SUPABASE_URL or not SB_KEY:
    print("FATAL: SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY not set", flush=True)
    sys.exit(1)

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          ".state", "geocode-backfill.json")
GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"
# Conservative rate: 5/sec (API allows 50 QPS)
RATE_DELAY = 0.2


def curl_json(url, headers=None, timeout=20):
    cmd = ["curl", "-sS", "--max-time", str(timeout)]
    if headers:
        for k, v in headers.items():
            cmd += ["-H", f"{k}: {v}"]
    cmd.append(url)
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5)
        if r.returncode != 0:
            return None
        return json.loads(r.stdout)
    except Exception as e:
        print(f"  curl error: {e}", flush=True)
        return None


def sb_headers():
    return {"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}",
            "Content-Type": "application/json", "Prefer": "return=minimal"}


def fetch_null_coord_listings():
    """All listings with an address but null lat/lng."""
    out = []
    off = 0
    base = f"{SUPABASE_URL}/rest/v1/directory_listings"
    while True:
        url = (f"{base}?select=id,slug,name,address,city,state,zip"
               f"&latitude=is.null&address=not.is.null"
               f"&order=id.asc&limit=1000&offset={off}")
        data = curl_json(url, headers={"apikey": SB_KEY,
                                       "Authorization": f"Bearer {SB_KEY}"})
        if not data or not isinstance(data, list):
            break
        out.extend(data)
        if len(data) < 1000:
            break
        off += 1000
    return out


def geocode(address):
    q = urllib.parse.quote_plus(address)
    url = f"{GEOCODE_URL}?address={q}&key={GKEY}"
    data = curl_json(url)
    if not data:
        return None, "HTTP_ERROR"
    status = data.get("status")
    if status == "OK" and data.get("results"):
        loc = data["results"][0]["geometry"]["location"]
        return (loc["lat"], loc["lng"]), None
    return None, status


def patch_coords(row_id, lat, lng):
    url = f"{SUPABASE_URL}/rest/v1/directory_listings?id=eq.{row_id}"
    cmd = ["curl", "-sS", "-o", "/dev/null", "-w", "%{http_code}",
           "--max-time", "20", "-X", "PATCH", url]
    for k, v in sb_headers().items():
        cmd += ["-H", f"{k}: {v}"]
    cmd += ["-d", json.dumps({"latitude": lat, "longitude": lng})]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
        return r.stdout.strip() in ("200", "204")
    except Exception:
        return False


def load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except Exception:
        return {"done_ids": [], "failed": {}}


def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def build_address(row):
    """Best-effort full address for geocoding."""
    parts = [row.get("address") or ""]
    city, state, zipc = row.get("city"), row.get("state"), row.get("zip")
    tail = ", ".join(p for p in [city, state] if p)
    if tail:
        parts.append(tail)
    if zipc:
        parts.append(zipc)
    parts.append("USA")
    return ", ".join(p for p in parts if p)


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    print("Fetching listings missing coordinates...", flush=True)
    listings = fetch_null_coord_listings()
    print(f"  {len(listings)} listings need geocoding", flush=True)
    if args.limit:
        listings = listings[:args.limit]
        print(f"  (limited to {args.limit})", flush=True)

    state = load_state()
    done = set(state["done_ids"])
    todo = [r for r in listings if r["id"] not in done]
    print(f"  {len(done)} already done, {len(todo)} remaining", flush=True)

    if args.dry_run:
        print("\nDry run — first 5 addresses that would be geocoded:", flush=True)
        for r in todo[:5]:
            print(f"  - {build_address(r)}", flush=True)
        est = len(todo) * 5 / 1000
        print(f"\nEstimated cost: ${est:.2f} ({len(todo)} calls @ $5/1k)", flush=True)
        return

    ok = fail = 0
    for i, row in enumerate(todo):
        addr = build_address(row)
        (latlng, err) = geocode(addr)
        if latlng:
            if patch_coords(row["id"], latlng[0], latlng[1]):
                ok += 1
                done.add(row["id"])
            else:
                fail += 1
                state["failed"][str(row["id"])] = "PATCH_FAILED"
        else:
            fail += 1
            state["failed"][str(row["id"])] = err or "UNKNOWN"
            if err in ("OVER_QUERY_LIMIT", "REQUEST_DENIED"):
                print(f"  FATAL geocode error: {err} — stopping", flush=True)
                break
        if (i + 1) % 50 == 0:
            state["done_ids"] = sorted(done)
            save_state(state)
            print(f"  ...{i+1}/{len(todo)} ({ok} ok, {fail} failed)", flush=True)
        time.sleep(RATE_DELAY)

    state["done_ids"] = sorted(done)
    save_state(state)
    print(f"\nDone: {ok} geocoded, {fail} failed", flush=True)
    if state["failed"]:
        from collections import Counter
        print("Failure reasons:", dict(Counter(state["failed"].values())), flush=True)


if __name__ == "__main__":
    main()
