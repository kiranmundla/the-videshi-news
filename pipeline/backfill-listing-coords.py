#!/usr/bin/env python3 -u
"""Backfill lat/lon for directory_listings rows missing coordinates.

Uses Google Geocoding API ($5/1000 — the cheap one, NOT Places Text Search).
For zip-only addresses, falls back to zippopotam.us (free) for zip centroids.

Cost: ~$0.005/geocode. 6,669 rows ≈ $33, within the $200/mo free credit.

Usage:
  set -a; source ~/workspace/.env.google-ai; source ~/workspace/.env.supabase; set +a
  python3 -u pipeline/backfill-listing-coords.py [--limit N] [--dry-run]

Env required: GOOGLE_PLACES_API_KEY (works for Geocoding), SUPABASE_URL,
SUPABASE_SERVICE_ROLE_KEY.
"""
import json
import os
import subprocess
import sys
import time
import urllib.parse

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
GKEY = os.environ.get("GOOGLE_PLACES_API_KEY", "")

GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"
DELAY_S = 0.12  # ~8/sec, well under Geocoding rate limits


def curl_json(url, method="GET", data=None, headers=None):
    cmd = ["curl", "-sS", "-X", method, url]
    for k, v in (headers or {}).items():
        cmd += ["-H", f"{k}: {v}"]
    if data is not None:
        cmd += ["-H", "Content-Type: application/json", "-d", json.dumps(data)]
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    return json.loads(out.stdout or "{}")


def sb_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
    }


def fetch_null_rows(limit=None):
    rows = []
    offset = 0
    page = 1000
    host = SUPABASE_URL
    while True:
        n = min(page, limit - len(rows)) if limit else page
        if n <= 0:
            break
        url = (f"{host}/rest/v1/directory_listings"
               f"?select=id,name,address,city,state,zip"
               f"&latitude=is.null&limit={n}&offset={offset}")
        batch = curl_json(url, headers=sb_headers())
        if not isinstance(batch, list) or not batch:
            break
        rows.extend(batch)
        offset += len(batch)
        if len(batch) < n:
            break
    return rows


def geocode_google(row):
    """Full-address geocode via Google Geocoding API."""
    addr = ", ".join(
        p for p in (row.get("address"), row.get("city"),
                    row.get("state"), row.get("zip")) if p
    )
    params = urllib.parse.urlencode({"address": addr, "key": GKEY})
    d = curl_json(f"{GEOCODE_URL}?{params}")
    if d.get("status") == "OK" and d.get("results"):
        loc = d["results"][0]["geometry"]["location"]
        return loc["lat"], loc["lng"], "google"
    return None, None, d.get("status", "unknown")


def geocode_zip_fallback(row):
    """Free zip-centroid fallback via zippopotam."""
    z = (row.get("zip") or "").strip()[:5]
    if not z.isdigit():
        return None, None, "no-zip"
    d = curl_json(f"https://api.zippopotam.us/us/{z}")
    try:
        p = d["places"][0]
        return float(p["latitude"]), float(p["longitude"]), "zippopotam"
    except Exception:
        return None, None, "zip-not-found"


def patch_row(row_id, lat, lon):
    url = f"{SUPABASE_URL}/rest/v1/directory_listings?id=eq.{row_id}"
    h = sb_headers()
    h["Prefer"] = "return=minimal"
    curl_json(url, method="PATCH",
              data={"latitude": lat, "longitude": lon}, headers=h)


def main():
    dry = "--dry-run" in sys.argv
    limit = None
    for a in sys.argv:
        if a.startswith("--limit"):
            limit = int(a.split("=")[1])

    if not SUPABASE_KEY or not GKEY:
        print("missing SUPABASE_SERVICE_ROLE_KEY or GOOGLE_PLACES_API_KEY", flush=True)
        sys.exit(1)

    rows = fetch_null_rows(limit)
    print(f"rows needing coords: {len(rows)}", flush=True)

    stats = {"google": 0, "zippopotam": 0, "failed": 0}
    google_calls = 0
    for i, r in enumerate(rows):
        lat, lon, src = geocode_google(r)
        google_calls += 1
        time.sleep(DELAY_S)
        if lat is None:
            # fall back to zip centroid (free)
            lat, lon, src = geocode_zip_fallback(r)
            time.sleep(0.2)
        if lat is None:
            stats["failed"] += 1
            print(f"  FAIL {r['id']} {r.get('name','')[:40]} ({src})", flush=True)
            continue
        stats[src] += 1
        if not dry:
            patch_row(r["id"], lat, lon)
        if (i + 1) % 500 == 0:
            print(f"  ...{i+1}/{len(rows)} (google={stats['google']} zip={stats['zippopotam']} fail={stats['failed']})",
                  flush=True)

    cost = google_calls * 0.005
    print(f"done: google={stats['google']} zippopotam={stats['zippopotam']} "
          f"failed={stats['failed']}", flush=True)
    print(f"google geocode calls: {google_calls} ≈ ${cost:.2f}", flush=True)
    if dry:
        print("(dry run — no writes)", flush=True)


if __name__ == "__main__":
    main()
