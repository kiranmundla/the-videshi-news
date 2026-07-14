#!/usr/bin/env python3
"""
NPI Registry Pipeline for The Videshi Directory
Queries the public NPI Registry API for all doctors by specialty + state,
filters for Indian-origin names, and inserts into directory_listings.
"""

import json
import os
import re
import sys
import time
import subprocess
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(__file__))
from indian_surnames_extended import is_indian_name

# ── Config ──────────────────────────────────────────────────────────

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

NPI_BASE = "https://npiregistry.cms.hhs.gov/api/"
NPI_VERSION = "2.1"
PAGE_SIZE = 200
MAX_SKIP = 5000  # safety cap per specialty+state combo
REQUEST_DELAY = 0.4  # seconds between API calls

SPECIALTIES = {
    "Pediatrics":               "Pediatrician",
    "Family Medicine":          "Primary Care",
    "Internal Medicine":        "Primary Care",
    "Obstetrics & Gynecology":  "OB/GYN",
    "Dentist":                  "Dentist",
    "Dermatology":              "Dermatologist",
    "Cardiology":               "Cardiologist",
    "Psychiatry & Neurology":   "Psychiatrist / Mental Health",
    "Ophthalmology":            "Ophthalmologist",
    "Orthopedic Surgery":       "Orthopedic Surgeon",
}

STATES = [
    "AL","AK","AZ","AR","CA","CO","CT","DC","DE","FL",
    "GA","HI","ID","IL","IN","IA","KS","KY","LA","ME",
    "MD","MA","MI","MN","MS","MO","MT","NE","NV","NH",
    "NJ","NM","NY","NC","ND","OH","OK","OR","PA","RI",
    "SC","SD","TN","TX","UT","VT","VA","WA","WV","WI","WY",
]

CATEGORY = "Doctors & Healthcare"

# ── Helpers ─────────────────────────────────────────────────────────

def curl_get(url):
    """GET via curl (proxy-safe)."""
    r = subprocess.run(
        ["curl", "-sS", "--max-time", "30", url],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        raise RuntimeError(f"curl failed: {r.stderr}")
    return json.loads(r.stdout)


def supabase_post(path, data, method="POST", extra_headers=None):
    """POST/PATCH to Supabase REST API via curl."""
    url = f"{SUPABASE_URL}/rest/v1/{path}"
    headers = [
        "-H", f"apikey: {SUPABASE_KEY}",
        "-H", f"Authorization: Bearer {SUPABASE_KEY}",
        "-H", "Content-Type: application/json",
    ]
    if extra_headers:
        for h in extra_headers:
            headers += ["-H", h]
    cmd = ["curl", "-sS", "--max-time", "15", "-X", method, url] + headers + ["-d", json.dumps(data)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r


def check_existing(name, city, state, subcategory):
    """Check if a similar listing already exists."""
    # URL-encode the name for the query
    import urllib.parse
    name_enc = urllib.parse.quote(name, safe="")
    city_enc = urllib.parse.quote(city, safe="") if city else ""
    url = (
        f"{SUPABASE_URL}/rest/v1/directory_listings"
        f"?name=ilike.*{name_enc}*&city=ilike.{city_enc}&state=eq.{state}"
        f"&category=eq.{CATEGORY}&select=id&limit=1"
    )
    cmd = [
        "curl", "-sS", "--max-time", "10", url,
        "-H", f"apikey: {SUPABASE_KEY}",
        "-H", f"Authorization: Bearer {SUPABASE_KEY}",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    try:
        results = json.loads(r.stdout)
        return len(results) > 0
    except Exception:
        return False


def make_slug(name, city, state):
    """Generate a URL-friendly slug."""
    raw = f"{name} {city} {state}".lower()
    raw = re.sub(r"[^a-z0-9]+", "-", raw).strip("-")
    return raw[:120]


def make_description(name, specialty, city, state, credential=""):
    """Template-based AI description."""
    cred = f", {credential}" if credential else ""
    return (
        f"Dr. {name}{cred} specializes in {specialty.lower()} in {city}, {state}, "
        f"serving the local community including Indian-American families."
    )


def format_phone(raw):
    """Format phone from NPI (10 digits) to (xxx) xxx-xxxx."""
    if not raw:
        return None
    digits = re.sub(r"\D", "", raw)
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    return raw


def format_zip(raw):
    """NPI gives 9-digit zips; take first 5."""
    if not raw:
        return None
    digits = re.sub(r"\D", "", raw)
    return digits[:5] if len(digits) >= 5 else raw


# ── NPI Query ──────────────────────────────────────────────────────

def query_npi(state, taxonomy, skip=0):
    """Query NPI registry for one page of results."""
    import urllib.parse
    params = urllib.parse.urlencode({
        "version": NPI_VERSION,
        "state": state,
        "taxonomy_description": taxonomy,
        "enumeration_type": "NPI-1",
        "limit": PAGE_SIZE,
        "skip": skip,
    })
    url = f"{NPI_BASE}?{params}"
    return curl_get(url)


def extract_doctor(npi_record, subcategory, taxonomy_desc):
    """Extract directory listing fields from an NPI record."""
    basic = npi_record.get("basic", {})
    first = basic.get("first_name", "").strip()
    last = basic.get("last_name", "").strip()

    if not first or not last:
        return None

    if not is_indian_name(first, last):
        return None

    credential = basic.get("credential", "").strip()
    npi_number = npi_record.get("number", "")

    # Get LOCATION address
    addrs = npi_record.get("addresses", [])
    loc = next((a for a in addrs if a.get("address_purpose") == "LOCATION"), None)
    if not loc:
        loc = addrs[0] if addrs else {}

    city = (loc.get("city") or "").strip().title()
    state = (loc.get("state") or "").strip().upper()
    if not city or not state:
        return None

    addr1 = (loc.get("address_1") or "").strip().title()
    addr2 = (loc.get("address_2") or "").strip().title()
    address = f"{addr1}, {addr2}".rstrip(", ") if addr2 else addr1

    # Build display name
    display_name = f"{first.title()} {last.title()}"
    if credential:
        # Clean credential
        cred = credential.replace(".", "").strip()
        display_name = f"Dr. {first.title()} {last.title()}, {cred}"
    else:
        display_name = f"Dr. {first.title()} {last.title()}"

    return {
        "name": display_name,
        "category": CATEGORY,
        "subcategory": subcategory,
        "address": address,
        "city": city,
        "state": state,
        "zip": format_zip(loc.get("postal_code")),
        "phone": format_phone(loc.get("telephone_number")),
        "source": "npi_registry",
        "slug": make_slug(f"{first} {last}", city, state),
        "verified": False,
        "featured": False,
        "ai_description": make_description(
            f"{first.title()} {last.title()}", taxonomy_desc, city, state, credential
        ),
    }


# ── Main Pipeline ──────────────────────────────────────────────────

def run_pipeline(states=None, specialties=None):
    states = states or STATES
    specialties = specialties or SPECIALTIES

    stats = {
        "total_npi_scanned": 0,
        "total_indian_matched": 0,
        "total_inserted": 0,
        "total_skipped_existing": 0,
        "total_api_errors": 0,
        "by_state": {},
        "by_specialty": {},
    }

    all_doctors = []  # collect before bulk insert
    seen_keys = set()  # (name_lower, city_lower, state, subcategory) dedup

    total_combos = len(states) * len(specialties)
    combo_idx = 0

    for state in states:
        state_stats = {"scanned": 0, "matched": 0, "inserted": 0}

        for taxonomy, subcategory in specialties.items():
            combo_idx += 1
            skip = 0
            specialty_matches = 0

            while skip <= MAX_SKIP:
                try:
                    data = query_npi(state, taxonomy, skip)
                except Exception as e:
                    print(f"  ⚠ API error {state}/{taxonomy} skip={skip}: {e}")
                    stats["total_api_errors"] += 1
                    time.sleep(2)
                    break

                results = data.get("results") or []
                result_count = data.get("result_count", 0)

                if not results:
                    break

                stats["total_npi_scanned"] += len(results)
                state_stats["scanned"] += len(results)

                for rec in results:
                    doc = extract_doctor(rec, subcategory, taxonomy)
                    if doc:
                        key = (doc["name"].lower(), doc["city"].lower(), doc["state"], doc["subcategory"])
                        if key not in seen_keys:
                            seen_keys.add(key)
                            all_doctors.append(doc)
                            specialty_matches += 1

                if len(results) < PAGE_SIZE:
                    break

                skip += PAGE_SIZE
                time.sleep(REQUEST_DELAY)

            stats["total_indian_matched"] += specialty_matches
            state_stats["matched"] += specialty_matches

            spec_key = subcategory
            if spec_key not in stats["by_specialty"]:
                stats["by_specialty"][spec_key] = 0
            stats["by_specialty"][spec_key] += specialty_matches

            if combo_idx % 10 == 0 or specialty_matches > 0:
                print(f"[{combo_idx}/{total_combos}] {state}/{taxonomy}: "
                      f"{specialty_matches} Indian matches")

            time.sleep(REQUEST_DELAY)

        stats["by_state"][state] = state_stats
        matched = state_stats["matched"]
        if matched > 0:
            print(f"  ✓ {state}: {matched} Indian doctors found ({state_stats['scanned']} scanned)")

    # ── Bulk insert ────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"Scan complete. {stats['total_indian_matched']} Indian doctors found "
          f"from {stats['total_npi_scanned']} NPI records.")
    print(f"Inserting into directory_listings...")

    batch = []
    batch_size = 50  # insert in batches

    for doc in all_doctors:
        # Check if already exists
        if check_existing(doc["name"], doc["city"], doc["state"], doc["subcategory"]):
            stats["total_skipped_existing"] += 1
            continue

        batch.append(doc)

        if len(batch) >= batch_size:
            _insert_batch(batch, stats)
            batch = []
            time.sleep(0.3)

    # Insert remaining
    if batch:
        _insert_batch(batch, stats)

    # ── Summary ────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"PIPELINE COMPLETE")
    print(f"  NPI records scanned:   {stats['total_npi_scanned']}")
    print(f"  Indian matches:        {stats['total_indian_matched']}")
    print(f"  Inserted (new):        {stats['total_inserted']}")
    print(f"  Skipped (existing):    {stats['total_skipped_existing']}")
    print(f"  API errors:            {stats['total_api_errors']}")
    print(f"\nBy specialty:")
    for spec, count in sorted(stats["by_specialty"].items(), key=lambda x: -x[1]):
        print(f"  {spec}: {count}")
    print(f"\nTop states:")
    top_states = sorted(stats["by_state"].items(), key=lambda x: -x[1]["matched"])[:20]
    for st, d in top_states:
        if d["matched"] > 0:
            print(f"  {st}: {d['matched']} matched / {d['scanned']} scanned")

    # Save summary JSON
    summary_path = os.path.join(os.path.dirname(__file__), "npi-pipeline-summary.json")
    with open(summary_path, "w") as f:
        json.dump({
            "run_at": datetime.now(timezone.utc).isoformat(),
            "total_scanned": stats["total_npi_scanned"],
            "total_matched": stats["total_indian_matched"],
            "total_inserted": stats["total_inserted"],
            "total_skipped": stats["total_skipped_existing"],
            "by_specialty": stats["by_specialty"],
            "by_state": {k: v for k, v in stats["by_state"].items() if v["matched"] > 0},
        }, f, indent=2)
    print(f"\nSummary saved to {summary_path}")

    return stats


def _insert_batch(batch, stats):
    """Insert a batch of listings."""
    r = supabase_post(
        "directory_listings",
        batch,
        method="POST",
        extra_headers=["Prefer: return=minimal", "Prefer: resolution=ignore-duplicates"],
    )
    if r.returncode == 0 and ("error" not in r.stdout.lower() or r.stdout.strip() == ""):
        stats["total_inserted"] += len(batch)
    else:
        # Try one-by-one on batch failure
        for doc in batch:
            r2 = supabase_post(
                "directory_listings",
                doc,
                method="POST",
                extra_headers=["Prefer: return=minimal"],
            )
            if r2.returncode == 0 and ("error" not in r2.stdout.lower() or r2.stdout.strip() == ""):
                stats["total_inserted"] += 1
            else:
                print(f"  ⚠ Insert failed for {doc['name']}: {r2.stdout[:200]}")


# ── CLI ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="NPI Doctor Pipeline")
    parser.add_argument("--states", nargs="+", help="Specific states (default: all)")
    parser.add_argument("--specialties", nargs="+", help="Specific taxonomy names")
    parser.add_argument("--dry-run", action="store_true", help="Scan only, no DB insert")
    args = parser.parse_args()

    states = args.states if args.states else None
    specs = None
    if args.specialties:
        specs = {k: v for k, v in SPECIALTIES.items() if k in args.specialties}

    if args.dry_run:
        # Monkey-patch insert to no-op
        def _noop_batch(b, s):
            s["total_inserted"] += len(b)
        _insert_batch = _noop_batch
        check_existing_orig = check_existing
        def check_existing(n, c, s, sc):
            return False

    run_pipeline(states=states, specialties=specs)
