#!/usr/bin/env python3
"""Seed visa_sightings table with sample community reports."""
import requests, os, json
from datetime import datetime, timedelta, timezone

# Load env
for envfile in [os.path.expanduser("~/workspace/.env.supabase")]:
    with open(envfile) as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                os.environ[k] = v

URL = os.environ["SUPABASE_URL"]
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": KEY,
    "Authorization": f"Bearer {KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal",
}

now = datetime.now(timezone.utc)

sightings = [
    {
        "consulate": "mumbai",
        "visa_type": "H-1B",
        "slots_date_start": "2026-09-15",
        "slots_date_end": "2026-09-20",
        "description": "Saw 4 H-1B interview slots at Mumbai for Sep 15-20. Grabbed one at 1:30 AM IST. They went fast — maybe 6 minutes before all gone.",
        "reporter_name": "Rahul",
        "reporter_email": "rahul@example.com",
        "verified": True,
        "status": "published",
        "created_at": (now - timedelta(hours=2)).isoformat(),
    },
    {
        "consulate": "hyderabad",
        "visa_type": "B1/B2",
        "slots_date_start": "2026-11-01",
        "slots_date_end": "2026-11-15",
        "description": "B1/B2 slots opened at Hyderabad for November first two weeks. Saw about 8 available when I checked at 11:45 PM IST Wednesday.",
        "reporter_name": "Priya",
        "reporter_email": "priya@example.com",
        "verified": True,
        "status": "published",
        "created_at": (now - timedelta(hours=5)).isoformat(),
    },
    {
        "consulate": "new_delhi",
        "visa_type": "H-1B",
        "slots_date_start": "2026-10-07",
        "slots_date_end": "2026-10-10",
        "description": "New Delhi dropped a small batch of H-1B slots for early October. Only 3-4 visible when I refreshed. Booked Oct 8.",
        "reporter_name": "Arjun",
        "reporter_email": "arjun@example.com",
        "verified": True,
        "status": "published",
        "created_at": (now - timedelta(hours=10)).isoformat(),
    },
    {
        "consulate": "chennai",
        "visa_type": "F-1",
        "slots_date_start": "2026-07-20",
        "slots_date_end": "2026-07-25",
        "description": "Chennai F-1 slots for late July just appeared! About 10+ slots for Jul 20-25. First time seeing availability in weeks.",
        "reporter_name": "Sneha",
        "reporter_email": "sneha@example.com",
        "verified": True,
        "status": "published",
        "created_at": (now - timedelta(hours=18)).isoformat(),
    },
    {
        "consulate": "kolkata",
        "visa_type": "H-1B",
        "slots_date_start": "2026-08-12",
        "slots_date_end": "2026-08-14",
        "description": "Kolkata has H-1B slots for mid-August. Fewer people check Kolkata so slots lasted longer — still available 20 min after I saw them.",
        "reporter_name": "Vikram",
        "reporter_email": "vikram@example.com",
        "verified": True,
        "status": "published",
        "created_at": (now - timedelta(hours=24)).isoformat(),
    },
    {
        "consulate": "mumbai",
        "visa_type": "L-1",
        "slots_date_start": "2026-09-22",
        "slots_date_end": "2026-09-26",
        "description": "L-1 slots at Mumbai for last week of September. My company's immigration team flagged these at midnight. Booked Sep 23.",
        "reporter_name": "Ananya",
        "reporter_email": "ananya@example.com",
        "verified": True,
        "status": "published",
        "created_at": (now - timedelta(hours=30)).isoformat(),
    },
    {
        "consulate": "hyderabad",
        "visa_type": "H-4",
        "slots_date_start": "2026-10-15",
        "slots_date_end": "2026-10-20",
        "description": "H-4 dependent visa slots at Hyderabad for Oct 15-20. Managed to book same date as my spouse's H-1B appointment.",
        "reporter_name": "Meera",
        "reporter_email": "meera@example.com",
        "verified": True,
        "status": "published",
        "created_at": (now - timedelta(hours=36)).isoformat(),
    },
    {
        "consulate": "new_delhi",
        "visa_type": "B1/B2",
        "slots_date_start": "2026-12-01",
        "slots_date_end": "2026-12-10",
        "description": "Big batch of B1/B2 slots dropped at New Delhi for December. Saw 15+ slots spread across first 10 days. Parents finally got an appointment!",
        "reporter_name": "Karthik",
        "reporter_email": "karthik@example.com",
        "verified": True,
        "status": "published",
        "created_at": (now - timedelta(hours=48)).isoformat(),
    },
    {
        "consulate": "chennai",
        "visa_type": "H-1B",
        "slots_date_start": "2026-08-05",
        "slots_date_end": "2026-08-08",
        "description": "Chennai released H-1B slots for early August during the Wednesday midnight window. Checked at exactly 12:01 AM IST and saw 5-6 slots.",
        "reporter_name": "Deepak",
        "reporter_email": "deepak@example.com",
        "verified": True,
        "status": "published",
        "created_at": (now - timedelta(hours=60)).isoformat(),
    },
    {
        "consulate": "mumbai",
        "visa_type": "F-1",
        "slots_date_start": "2026-07-10",
        "slots_date_end": "2026-07-15",
        "description": "F-1 student visa slots at Mumbai for mid-July. If you're a fall admit, these are perfect. Saw ~12 slots, booked Jul 12.",
        "reporter_name": "Riya",
        "reporter_email": "riya@example.com",
        "verified": True,
        "status": "published",
        "created_at": (now - timedelta(hours=70)).isoformat(),
    },
]

resp = requests.post(
    f"{URL}/rest/v1/visa_sightings",
    headers=HEADERS,
    json=sightings,
)
print(f"Seed sightings: {resp.status_code}")
if resp.status_code not in (200, 201):
    print(resp.text[:300])
else:
    print(f"  ✓ {len(sightings)} sample sightings inserted")
