#!/usr/bin/env python3
"""Seed Exhibitions & Roadshows events (M1, 2026-10-18).

All entries verified live on organizer sites on 2026-10-18:
- DAMAC NJ/NY: https://www.aredxb.com/roadshows (Allegiance Real Estate)
- India Property Expo America: https://www.indiapropertyexpousa.com/ FAQ

Usage:
    python3 seed-roadshow-events.py [CATEGORY]

CATEGORY defaults to "Exhibitions & Roadshows". Until
pipeline/migration-events-roadshows-category.sql is applied, the
events_category_check constraint rejects that value; seed with
"Other" as the interim category and re-run with the real category
afterwards — existing rows (matched by source_id) are PATCHed to the
given category, missing rows are inserted.
"""
import json
import os
import subprocess
import sys

URL = os.environ["SUPABASE_URL"].rstrip("/")
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = ["-H", f"apikey: {KEY}", "-H", f"Authorization: Bearer {KEY}",
           "-H", "Content-Type: application/json"]
CATEGORY = sys.argv[1] if len(sys.argv) > 1 else "Exhibitions & Roadshows"

EVENTS = [
    {
        "title": "DAMAC Dubai Property Roadshow — New Jersey",
        "date": "2026-11-14", "end_date": None, "time": None,
        "venue_name": "Venue shared on invitation — request via the organizer's roadshow page",
        "city": "New Jersey", "state": "NJ",
        "description": "DAMAC Properties brings its Dubai real estate roadshow to New Jersey, hosted by Allegiance Real Estate. Meet the DAMAC team in person, explore off-plan and ready Dubai developments, payment plans and Golden Visa eligibility. Attendance is by invitation — request yours on the organizer's roadshow page.",
        "ticket_url": "https://www.aredxb.com/roadshows",
        "source": "web", "source_id": "aredxb-damac-new-jersey-2026-11-14",
        "price_range": "Free — by invitation",
        "organizer": "Allegiance Real Estate for DAMAC Properties",
        "slug": "damac-dubai-property-roadshow-new-jersey-2026-11-14",
        "is_featured": False, "venue_images": [],
    },
    {
        "title": "DAMAC Dubai Property Roadshow — New York",
        "date": "2026-11-15", "end_date": None, "time": None,
        "venue_name": "Venue shared on invitation — request via the organizer's roadshow page",
        "city": "New York", "state": "NY",
        "description": "DAMAC Properties brings its Dubai real estate roadshow to New York, hosted by Allegiance Real Estate. Meet the DAMAC team in person, explore off-plan and ready Dubai developments, payment plans and Golden Visa eligibility. Attendance is by invitation — request yours on the organizer's roadshow page.",
        "ticket_url": "https://www.aredxb.com/roadshows",
        "source": "web", "source_id": "aredxb-damac-new-york-2026-11-15",
        "price_range": "Free — by invitation",
        "organizer": "Allegiance Real Estate for DAMAC Properties",
        "slug": "damac-dubai-property-roadshow-new-york-2026-11-15",
        "is_featured": False, "venue_images": [],
    },
    {
        "title": "India Property Expo America 2026 — Chicago",
        "date": "2026-10-24", "end_date": "2026-10-25", "time": None,
        "venue_name": "Private 5-star venue — address emailed to confirmed RSVPs",
        "city": "Chicago", "state": "IL",
        "description": "America's India property exhibition tour stops in Greater Chicago. Meet 35+ RERA-verified Indian developers (Godrej, Lodha, Sobha, Prestige, Oberoi and more), explore 500+ projects across 35+ Indian cities, and book free 1-on-1 consultations plus NRI tax clinic, GIFT City and home-loan sessions. RSVP-only and free — the venue address is emailed to confirmed guests.",
        "ticket_url": "https://www.indiapropertyexpousa.com/",
        "source": "web", "source_id": "india-property-expo-america-chicago-2026",
        "price_range": "Free",
        "organizer": "India Property Expo USA",
        "slug": "india-property-expo-america-2026-chicago-2026-10-24",
        "is_featured": False, "venue_images": [],
    },
    {
        "title": "India Property Expo America 2026 — Seattle",
        "date": "2026-11-07", "end_date": "2026-11-08", "time": None,
        "venue_name": "Private 5-star venue — address emailed to confirmed RSVPs",
        "city": "Seattle", "state": "WA",
        "description": "America's India property exhibition tour stops in Greater Seattle. Meet 35+ RERA-verified Indian developers (Godrej, Lodha, Sobha, Prestige, Oberoi and more), explore 500+ projects across 35+ Indian cities, and book free 1-on-1 consultations plus NRI tax clinic, GIFT City and home-loan sessions. RSVP-only and free — the venue address is emailed to confirmed guests.",
        "ticket_url": "https://www.indiapropertyexpousa.com/",
        "source": "web", "source_id": "india-property-expo-america-seattle-2026",
        "price_range": "Free",
        "organizer": "India Property Expo USA",
        "slug": "india-property-expo-america-2026-seattle-2026-11-07",
        "is_featured": False, "venue_images": [],
    },
    {
        "title": "India Property Expo America 2026 — Atlanta",
        "date": "2026-11-14", "end_date": "2026-11-15", "time": None,
        "venue_name": "Private 5-star venue — address emailed to confirmed RSVPs",
        "city": "Atlanta", "state": "GA",
        "description": "America's India property exhibition tour stops in Atlanta. Meet 35+ RERA-verified Indian developers (Godrej, Lodha, Sobha, Prestige, Oberoi and more), explore 500+ projects across 35+ Indian cities, and book free 1-on-1 consultations plus NRI tax clinic, GIFT City and home-loan sessions. RSVP-only and free — the venue address is emailed to confirmed guests.",
        "ticket_url": "https://www.indiapropertyexpousa.com/",
        "source": "web", "source_id": "india-property-expo-america-atlanta-2026",
        "price_range": "Free",
        "organizer": "India Property Expo USA",
        "slug": "india-property-expo-america-2026-atlanta-2026-11-14",
        "is_featured": False, "venue_images": [],
    },
]


def curl(args, data=None, method=None):
    cmd = ["curl", "-s", "-w", "\n%{http_code}"] + args
    if method:
        cmd += ["-X", method]
    if data is not None:
        cmd += ["-d", json.dumps(data)]
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    body, _, code = out.stdout.rpartition("\n")
    return int(code), body


def main():
    for ev in EVENTS:
        row = dict(ev, category=CATEGORY)
        code, body = curl([f"{URL}/rest/v1/events?select=id,category&source_id=eq.{ev['source_id']}"] + HEADERS)
        existing = json.loads(body) if code == 200 and body else []
        if existing:
            if existing[0]["category"] == CATEGORY:
                print(f"OK (already {CATEGORY}): {ev['source_id']}")
                continue
            code, body = curl([f"{URL}/rest/v1/events?source_id=eq.{ev['source_id']}"] + HEADERS,
                              data={"category": CATEGORY}, method="PATCH")
            if code in (200, 204):
                print(f"PATCHED category -> {CATEGORY}: {ev['source_id']}")
            else:
                print(f"PATCH FAILED ({code}): {ev['source_id']}: {body[:300]}")
                sys.exit(1)
            continue
        code, body = curl([f"{URL}/rest/v1/events"] + HEADERS + ["-H", "Prefer: return=representation"], data=row)
        if code in (200, 201):
            r = json.loads(body)[0]
            print(f"INSERTED: {ev['title']} | {r['id']} | {r['slug']} | category={r['category']}")
        else:
            print(f"INSERT FAILED ({code}): {ev['source_id']}: {body[:300]}")
            sys.exit(1)


if __name__ == "__main__":
    main()
