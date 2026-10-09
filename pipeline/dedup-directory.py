#!/usr/bin/env python3
"""Dedup directory_listings: find and remove duplicate businesses.
Matches on normalized name + phone, or normalized name + city+state.
Keeps the oldest/most complete record, deletes the rest.
"""
import json, subprocess, os, sys, re
from collections import defaultdict

SUPABASE_URL = os.environ['SUPABASE_URL'].rstrip('/')
KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']

def curl_get(path):
    out = subprocess.run(
        ["curl", "-sS", f"{SUPABASE_URL}{path}",
         "-H", f"apikey: {KEY}", "-H", f"Authorization: Bearer {KEY}"],
        capture_output=True, text=True, timeout=60)
    return json.loads(out.stdout)

def curl_delete(ids):
    """Delete by IDs in batches."""
    deleted = 0
    for i in range(0, len(ids), 50):
        batch = ids[i:i+50]
        id_list = ",".join(f'"{x}"' for x in batch)
        out = subprocess.run(
            ["curl", "-sS", "-X", "DELETE",
             f"{SUPABASE_URL}/rest/v1/directory_listings?id=in.({id_list})",
             "-H", f"apikey: {KEY}", "-H", f"Authorization: Bearer {KEY}",
             "-H", "Prefer: return=minimal"],
            capture_output=True, text=True, timeout=60)
        deleted += len(batch)
    return deleted

def normalize_name(n):
    if not n: return ""
    n = n.lower().strip()
    # Remove common suffixes/prefixes that cause false splits
    n = re.sub(r'\s+', ' ', n)
    n = re.sub(r'[^\w\s/&.-]', '', n)
    return n.strip()

def normalize_phone(p):
    if not p: return ""
    return re.sub(r'\D', '', p)[-10:]  # last 10 digits

# Page through all listings
print("Fetching all listings...", flush=True)
all_rows = []
offset = 0
PAGE = 1000
while True:
    batch = curl_get(f"/rest/v1/directory_listings?select=id,name,phone,city,state,created_at,google_place_id&order=id&limit={PAGE}&offset={offset}")
    if not batch: break
    all_rows.extend(batch)
    offset += PAGE
    print(f"  {len(all_rows)} fetched...", flush=True)
    if len(batch) < PAGE: break

print(f"\nTotal: {len(all_rows)} listings")

# Group by normalized name+phone
groups = defaultdict(list)
for r in all_rows:
    name = normalize_name(r.get('name'))
    phone = normalize_phone(r.get('phone'))
    city = (r.get('city') or '').strip().lower()
    state = (r.get('state') or '').strip().lower()
    if not name: continue
    # Primary key: name+phone (if phone exists)
    # Secondary: name+city+state (if no phone)
    if phone:
        key = ('phone', name, phone)
    elif city:
        key = ('loc', name, city, state)
    else:
        key = ('name', name)
    groups[key].append(r)

# Find duplicates
to_delete = []
for key, rows in groups.items():
    if len(rows) > 1:
        # Keep the one with google_place_id (richer data), else oldest
        rows.sort(key=lambda r: (0 if r.get('google_place_id') else 1, r.get('created_at') or ''))
        keep = rows[0]
        for dup in rows[1:]:
            to_delete.append(dup['id'])

print(f"Duplicate groups: {sum(1 for g in groups.values() if len(g)>1)}")
print(f"Rows to delete: {len(to_delete)}")
print(f"Dup rate: {len(to_delete)/len(all_rows)*100:.1f}%")

if '--apply' in sys.argv and to_delete:
    print(f"\nDeleting {len(to_delete)} duplicates...", flush=True)
    deleted = curl_delete(to_delete)
    print(f"Deleted: {deleted}")
elif to_delete:
    print("\nDry run — use --apply to delete")
    # Show samples
    shown = 0
    for key, rows in groups.items():
        if len(rows) > 1 and shown < 5:
            print(f"  DUP: {rows[0].get('name')} ({len(rows)}x)")
            shown += 1
