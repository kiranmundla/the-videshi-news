#!/usr/bin/env python3 -u
"""Geocode backfill for scrape-muslimguide rows inserted with null coords."""
import json
import os
import subprocess
import sys
import time
import urllib.parse

GKEY = os.environ.get("GOOGLE_PLACES_API_KEY", "")
SB_URL = os.environ.get("SUPABASE_URL", "")
SB_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
HDRS = ["-H", f"apikey: {SB_KEY}", "-H", f"Authorization: Bearer {SB_KEY}"]

if not GKEY:
    print("ERROR: GOOGLE_PLACES_API_KEY not set", file=sys.stderr)
    sys.exit(1)


def sb_get(url):
    out = subprocess.run(["curl", "-sS", url] + HDRS,
                         capture_output=True, text=True)
    return json.loads(out.stdout or "[]")


def sb_patch(row_id, lat, lon):
    out = subprocess.run(
        ["curl", "-sS", "-X", "PATCH",
         f"{SB_URL}/rest/v1/directory_listings?id=eq.{row_id}"] + HDRS +
        ["-H", "Content-Type: application/json",
         "-d", json.dumps({"latitude": lat, "longitude": lon})],
        capture_output=True, text=True)
    return out.returncode == 0


def geocode(address):
    time.sleep(0.15)
    url = ("https://maps.googleapis.com/maps/api/geocode/json?" +
           urllib.parse.urlencode({"address": address, "key": GKEY}))
    try:
        out = subprocess.run(["curl", "-sS", "--max-time", "15", url],
                             capture_output=True, text=True)
        d = json.loads(out.stdout or "{}")
        if d.get("status") == "OK" and d.get("results"):
            loc = d["results"][0]["geometry"]["location"]
            return loc["lat"], loc["lng"]
        return None, d.get("status", "unknown")
    except Exception as e:
        return None, "EXC:" + str(e)[:50]


def main():
    rows, offset = [], 0
    while True:
        batch = sb_get(
            f"{SB_URL}/rest/v1/directory_listings"
            "?select=id,name,address,city,state,zip&source=eq.scrape-muslimguide"
            f"&latitude=is.null&limit=1000&offset={offset}")
        rows.extend(batch)
        if len(batch) < 1000:
            break
        offset += 1000
    print(f"rows needing geocode: {len(rows)}", flush=True)

    ok, fail = 0, 0
    for i, r in enumerate(rows):
        addr = ", ".join(p for p in
                         [r.get("address"), r.get("city"), r.get("state"), r.get("zip")]
                         if p)
        lat, lon = geocode(addr)
        if lat is not None and sb_patch(r["id"], lat, lon):
            ok += 1
        else:
            fail += 1
            if fail <= 5:
                print(f"  FAIL: {r['name'][:40]} | {addr[:60]} | {lon}", flush=True)
        if (i + 1) % 200 == 0:
            print(f"  {i+1}/{len(rows)} ok={ok} fail={fail}", flush=True)
    print(f"DONE ok={ok} fail={fail}", flush=True)


if __name__ == "__main__":
    main()
