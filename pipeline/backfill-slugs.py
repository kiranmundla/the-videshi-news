#!/usr/bin/env python3
"""Backfill missing slugs for directory_listings.
Generates URL-safe slugs from name + city, ensures uniqueness.
"""
import json, subprocess, os, sys, re

SUPABASE_URL = os.environ['SUPABASE_URL'].rstrip('/')
KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']

def curl_get(path):
    out = subprocess.run(
        ["curl", "-sS", f"{SUPABASE_URL}{path}",
         "-H", f"apikey: {KEY}", "-H", f"Authorization: Bearer {KEY}"],
        capture_output=True, text=True, timeout=60)
    return json.loads(out.stdout)

def curl_patch(path, data):
    out = subprocess.run(
        ["curl", "-sS", "-X", "PATCH", f"{SUPABASE_URL}{path}",
         "-H", f"apikey: {KEY}", "-H", f"Authorization: Bearer {KEY}",
         "-H", "Content-Type: application/json",
         "-H", "Prefer: return=minimal",
         "-d", json.dumps(data)],
        capture_output=True, text=True, timeout=30)
    return out.returncode == 0

def make_slug(name, city, state, existing):
    base = re.sub(r'[^a-z0-9]+', '-', (name or 'listing').lower()).strip('-')
    if city:
        city_part = re.sub(r'[^a-z0-9]+', '-', city.lower()).strip('-')
        base = f"{base}-{city_part}"
    slug = base[:80]
    # Ensure uniqueness
    n = 2
    candidate = slug
    while candidate in existing:
        candidate = f"{slug}-{n}"
        n += 1
    existing.add(candidate)
    return candidate

# Get all existing slugs
print("Fetching existing slugs...", flush=True)
existing = set()
offset = 0
while True:
    batch = curl_get(f"/rest/v1/directory_listings?select=slug&limit=1000&offset={offset}")
    if not batch: break
    for r in batch:
        if r.get('slug'): existing.add(r['slug'])
    offset += 1000
    if len(batch) < 1000: break
print(f"  {len(existing)} existing slugs")

# Get listings with null slugs
print("\nFetching null-slug listings...", flush=True)
nulls = []
offset = 0
while True:
    batch = curl_get(f"/rest/v1/directory_listings?select=id,name,city,state&slug=is.null&limit=1000&offset={offset}")
    if not batch: break
    nulls.extend(batch)
    offset += 1000
    print(f"  {len(nulls)} found...", flush=True)
    if len(batch) < 1000: break

print(f"\nBackfilling {len(nulls)} slugs...")
fixed = 0
for r in nulls:
    slug = make_slug(r.get('name'), r.get('city'), r.get('state'), existing)
    if '--apply' in sys.argv:
        if curl_patch(f"/rest/v1/directory_listings?id=eq.{r['id']}", {"slug": slug}):
            fixed += 1
    else:
        fixed += 1  # dry run count

print(f"{'Fixed' if '--apply' in sys.argv else 'Would fix'}: {fixed}")
