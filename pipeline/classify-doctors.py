#!/usr/bin/env python3
"""
Classify Doctors & Healthcare listings into subcategories
based on name + description keywords.
"""

import os
import re
import requests
from collections import Counter

# ---------- Config ----------

def load_env():
    env = {}
    for path in [os.path.expanduser("~/.env.supabase"), os.path.expanduser("~/workspace/.env.supabase")]:
        if os.path.exists(path):
            for line in open(path):
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    env[k] = v
    return env

ENV = load_env()
SUPABASE_URL = ENV["SUPABASE_URL"]
SERVICE_KEY = ENV["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SERVICE_KEY,
    "Authorization": f"Bearer {SERVICE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal",
}

# ---------- Subcategory rules ----------
# Order matters — first match wins. More specific patterns go first.

SUBCATEGORY_RULES = [
    ("Dentist", [
        r"dental", r"dentist", r"\bdds\b", r"\bdmd\b", r"orthodont",
        r"endodont", r"periodont", r"oral\s*surg",
    ]),
    ("Urgent Care", [
        r"urgent\s*care", r"walk[\s-]*in\s*clinic", r"immediate\s*care",
        r"emergency\s*(room|clinic|doctor|care)",
    ]),
    ("Pediatrician", [
        r"pediatric", r"paediatr", r"pediatrician", r"\bchildren\b",
        r"child\s*(health|care|doctor)", r"\bkids\b",
    ]),
    ("OB/GYN", [
        r"ob/?gyn", r"obstetric", r"gynecolog", r"women'?s\s*health",
    ]),
    ("Cardiologist", [
        r"cardiol", r"\bheart\b",
    ]),
    ("Dermatologist", [
        r"dermatol", r"\bskin\s*(care|doctor|clinic)\b",
    ]),
    ("Ophthalmologist", [
        r"ophthalmol", r"eye\s*doctor", r"optometr", r"\bvision\s*(care|center)\b",
        r"\beye\s*(care|center|clinic)\b",
    ]),
    ("Orthopedic", [
        r"orthoped", r"orthopaed", r"sports\s*medicine",
    ]),
    ("Psychiatrist / Mental Health", [
        r"psychiat", r"psycholog", r"mental\s*health", r"\btherapist\b",
        r"\bcounselor\b", r"\bcounseling\b", r"behavioral",
    ]),
    ("Ayurveda & Holistic", [
        r"ayurved", r"holistic", r"homeopath", r"naturopath", r"acupunctur",
        r"unani", r"siddha",
    ]),
    ("Surgeon", [
        r"surgeon", r"surgery",  # oral surgery already caught by Dentist above
    ]),
    ("Primary Care", [
        r"primary\s*care", r"family\s*(medicine|practice|doctor|physician)",
        r"internal\s*medicine", r"general\s*(practice|physician|practitioner)",
        r"\bgp\b",
    ]),
]


def classify(name: str, description: str) -> str:
    """Return the best subcategory for a listing."""
    text = f"{name} {description or ''}".lower()
    for subcat, patterns in SUBCATEGORY_RULES:
        for pat in patterns:
            if re.search(pat, text):
                return subcat
    return "General / Other"


def main():
    # Fetch all Doctors & Healthcare listings
    url = f"{SUPABASE_URL}/rest/v1/directory_listings"
    params = {
        "select": "id,name,description,subcategory",
        "category": "eq.Doctors & Healthcare",
        "limit": "2000",
    }
    r = requests.get(url, headers=HEADERS, params=params)
    r.raise_for_status()
    listings = r.json()
    print(f"Found {len(listings)} Doctors & Healthcare listings\n")

    counts = Counter()
    updates = []

    for listing in listings:
        subcat = classify(listing["name"], listing.get("description") or "")
        counts[subcat] += 1
        if listing.get("subcategory") != subcat:
            updates.append({"id": listing["id"], "subcategory": subcat})

    # Print summary
    print("SUBCATEGORY BREAKDOWN:")
    for subcat, count in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {count:4d}  {subcat}")
    print()

    # Update in Supabase
    print(f"Updating {len(updates)} listings...")
    ok = 0
    err = 0
    for upd in updates:
        r = requests.patch(
            f"{SUPABASE_URL}/rest/v1/directory_listings?id=eq.{upd['id']}",
            headers=HEADERS,
            json={"subcategory": upd["subcategory"]},
        )
        if r.status_code < 300:
            ok += 1
        else:
            err += 1
            print(f"  ERROR updating {upd['id']}: {r.status_code} {r.text[:200]}")

    print(f"\nDone: {ok} updated, {err} errors")


if __name__ == "__main__":
    main()
