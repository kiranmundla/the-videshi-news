#!/usr/bin/env python3
"""Fix ALL-CAPS names in directory_listings — title-case while preserving common suffixes."""

import os, re, sys, requests

sys.stdout.reconfigure(line_buffering=True)

env = {}
for line in open(os.path.expanduser("~/.env.supabase")):
    line = line.strip()
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        env[k] = v

SUPABASE_URL = env['SUPABASE_URL']
SERVICE_KEY = env['SUPABASE_SERVICE_ROLE_KEY']

headers = {
    'apikey': SERVICE_KEY,
    'Authorization': f'Bearer {SERVICE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=minimal'
}

PRESERVE = {
    'md': 'MD', 'dds': 'DDS', 'do': 'DO', 'dmd': 'DMD',
    'llc': 'LLC', 'pllc': 'PLLC', 'plc': 'PLC', 'llp': 'LLP',
    'pc': 'PC', 'pa': 'PA', 'inc': 'Inc',
    'dpm': 'DPM', 'od': 'OD', 'dvm': 'DVM',
    'phd': 'PhD', 'jd': 'JD', 'cpa': 'CPA', 'lcsw': 'LCSW',
    'facp': 'FACP', 'facs': 'FACS', 'cphq': 'CPHQ',
    'np': 'NP', 'rn': 'RN', 'mph': 'MPH',
    'ii': 'II', 'iii': 'III', 'iv': 'IV',
    'ob/gyn': 'OB/GYN', 'obgyn': 'OBGYN',
    'usa': 'USA', 'us': 'US', 'dba': 'DBA',
}


def smart_title(name):
    titled = name.title()
    words = titled.split()
    fixed = []
    for w in words:
        clean = re.sub(r'[.,;:()\[\]]', '', w).lower()
        if clean in PRESERVE:
            result = re.sub(r'[a-zA-Z/]+', lambda m: PRESERVE.get(m.group().lower(), m.group()), w, count=1)
            fixed.append(result)
        else:
            fixed.append(w)
    return ' '.join(fixed)


def fetch_all_listings():
    all_listings = []
    offset = 0
    while True:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/directory_listings",
            params={'select': 'id,name', 'limit': 1000, 'offset': offset},
            headers=headers, timeout=15
        )
        if r.status_code != 200:
            break
        batch = r.json()
        all_listings.extend(batch)
        if len(batch) < 1000:
            break
        offset += 1000
    return all_listings


def main():
    print("Fetching all directory listings...")
    listings = fetch_all_listings()
    print(f"Total: {len(listings)}")

    caps = [l for l in listings if l['name'] == l['name'].upper() and len(l['name']) > 5]
    print(f"ALL-CAPS names: {len(caps)}\n")

    updated = 0
    for listing in caps:
        old_name = listing['name']
        new_name = smart_title(old_name)
        if old_name == new_name:
            continue

        r = requests.patch(
            f"{SUPABASE_URL}/rest/v1/directory_listings?id=eq.{listing['id']}",
            headers=headers,
            json={"name": new_name},
            timeout=10
        )
        if r.status_code < 300:
            updated += 1
            print(f"  {old_name:50s} → {new_name}")
        else:
            print(f"  ✗ Failed: {old_name} — {r.status_code}")

    print(f"\nFixed {updated} names")


if __name__ == "__main__":
    main()
