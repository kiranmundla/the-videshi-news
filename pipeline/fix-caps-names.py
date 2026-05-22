#!/usr/bin/env python3
"""
Fix ALL-CAPS names in directory_listings by title-casing them,
preserving common professional suffixes.
"""

import os
import re
import requests

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

# Suffixes that should stay uppercase
PRESERVE_UPPER = {
    "MD", "DDS", "DO", "LLC", "PLLC", "PLC", "DPM", "OD", "DMD", "PC", "PA",
    "DBA", "INC", "NP", "RN", "LLP", "DC", "PT", "DPT", "OB/GYN",
    "II", "III", "IV", "JR", "SR", "PhD", "MBBS", "MS", "MPH",
    "USA", "VJ", "CPA",
}

def smart_title_case(name: str) -> str:
    """Title case but preserve known professional/legal suffixes."""
    words = name.title().split()
    result = []
    for w in words:
        # Strip leading/trailing punctuation for comparison
        clean = re.sub(r"^[,.:;]+|[,.:;]+$", "", w).upper()
        if clean in PRESERVE_UPPER:
            # Restore the uppercase version, keeping original punctuation
            prefix = re.match(r"^([,.:;]*)", w)
            suffix = re.search(r"([,.:;]*)$", w)
            p = prefix.group(1) if prefix else ""
            s = suffix.group(1) if suffix else ""
            result.append(p + clean + s)
        elif w == "Indian'S":
            result.append("Indian's")
        else:
            result.append(w)
    return " ".join(result)


def main():
    # Fetch all listings
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/directory_listings",
        headers=HEADERS,
        params={"select": "id,name", "limit": "5000"},
    )
    r.raise_for_status()
    listings = r.json()

    # Find ALL-CAPS names (length > 5 to avoid things like "ABC")
    caps_listings = [l for l in listings if l["name"] == l["name"].upper() and len(l["name"]) > 5]
    print(f"Found {len(caps_listings)} ALL-CAPS listings\n")

    ok = 0
    for l in caps_listings:
        new_name = smart_title_case(l["name"])
        print(f"  {l['name']}")
        print(f"  → {new_name}\n")

        r = requests.patch(
            f"{SUPABASE_URL}/rest/v1/directory_listings?id=eq.{l['id']}",
            headers=HEADERS,
            json={"name": new_name},
        )
        if r.status_code < 300:
            ok += 1
        else:
            print(f"  ERROR: {r.status_code} {r.text[:200]}")

    print(f"Done: {ok}/{len(caps_listings)} fixed")


if __name__ == "__main__":
    main()
