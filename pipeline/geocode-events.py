#!/usr/bin/env python3
"""Geocode events missing lat/lon via Nominatim."""
import json, os, sys, time
sys.stdout.reconfigure(line_buffering=True)
import requests

ENV_FILE = os.path.expanduser("~/.env.supabase")
if os.path.exists(ENV_FILE):
    for line in open(ENV_FILE):
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
REST = f"{SB_URL}/rest/v1"
HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
}

def geocode(venue, city, state=""):
    query = f"{venue}, {city}"
    if state:
        query += f", {state}"
    query += ", USA"
    params = {"q": query, "format": "json", "limit": 1, "countrycodes": "us"}
    headers = {"User-Agent": "TheVideshi/1.0 (events geocoder)"}
    try:
        r = requests.get("https://nominatim.openstreetmap.org/search",
                         params=params, headers=headers, timeout=10)
        if r.status_code == 200 and r.json():
            return float(r.json()[0]["lat"]), float(r.json()[0]["lon"])
        # Fallback: just city
        params["q"] = f"{city}, {state}, USA" if state else f"{city}, USA"
        r = requests.get("https://nominatim.openstreetmap.org/search",
                         params=params, headers=headers, timeout=10)
        if r.status_code == 200 and r.json():
            return float(r.json()[0]["lat"]), float(r.json()[0]["lon"])
    except Exception as e:
        print(f"  Error: {e}")
    return None, None

r = requests.get(
    f"{REST}/events?select=id,title,venue_name,city,state&latitude=is.null&longitude=is.null",
    headers=HEADERS, timeout=15,
)
events = r.json()
print(f"Geocoding {len(events)} events...")

geocoded = failed = 0
for ev in events:
    lat, lon = geocode(ev.get("venue_name",""), ev.get("city",""), ev.get("state",""))
    if lat and lon:
        ur = requests.patch(
            f"{REST}/events?id=eq.{ev['id']}",
            headers={**HEADERS, "Prefer": "return=minimal"},
            json={"latitude": lat, "longitude": lon},
            timeout=10,
        )
        if ur.status_code in (200, 204):
            geocoded += 1
        else:
            failed += 1
    else:
        failed += 1
        print(f"  Failed: {ev.get('title','?')[:50]} | {ev.get('venue_name','')} | {ev.get('city','')}")
    time.sleep(1.1)

print(f"\nGeocoded: {geocoded}, Failed: {failed}")
