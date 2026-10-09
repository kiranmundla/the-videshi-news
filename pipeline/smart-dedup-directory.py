#!/usr/bin/env python3
"""Smart dedup for directory_listings based on contact info.

Catches duplicates the exact-match dedup misses:
1. Same phone number, different name variations ("Remax Accord" vs "RE/MAX Accord")
2. Same address (street + city), different names
3. Same website, different names
4. Fuzzy name match (high similarity) in same city + same category

Keeps the record with the most complete data (photos, rating, reviews, description).
Dry run by default; --apply to delete.
"""
import json, subprocess, os, sys, re
from collections import defaultdict
from difflib import SequenceMatcher

SUPABASE_URL = os.environ['SUPABASE_URL'].rstrip('/')
KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']

def curl_get(path):
    out = subprocess.run(
        ["curl", "-sS", f"{SUPABASE_URL}{path}",
         "-H", f"apikey: {KEY}", "-H", f"Authorization: Bearer {KEY}"],
        capture_output=True, text=True, timeout=120)
    return json.loads(out.stdout)

def curl_delete(ids):
    deleted = 0
    for i in range(0, len(ids), 50):
        batch = ids[i:i+50]
        id_list = ",".join(f'"{x}"' for x in batch)
        subprocess.run(
            ["curl", "-sS", "-X", "DELETE",
             f"{SUPABASE_URL}/rest/v1/directory_listings?id=in.({id_list})",
             "-H", f"apikey: {KEY}", "-H", f"Authorization: Bearer {KEY}",
             "-H", "Prefer: return=minimal"],
            capture_output=True, text=True, timeout=60)
        deleted += len(batch)
    return deleted

def norm_phone(p):
    if not p: return ""
    d = re.sub(r'\D', '', p)
    return d[-10:] if len(d) >= 10 else d

def norm_name(n):
    if not n: return ""
    n = n.lower().strip()
    # Remove business suffixes and normalize separators
    n = re.sub(r'\b(llc|inc|corp|co|ltd|pllc|pa|pc)\b\.?', '', n)
    n = re.sub(r'[/&]', ' ', n)
    n = re.sub(r'[^\w\s]', '', n)
    n = re.sub(r'\s+', ' ', n).strip()
    return n

def norm_addr(a):
    if not a: return ""
    a = a.lower().strip()
    a = re.sub(r'[^\w\s]', '', a)
    a = re.sub(r'\s+', ' ', a).strip()
    return a

def norm_url(u):
    if not u: return ""
    u = u.lower().strip()
    u = re.sub(r'^https?://', '', u)
    u = re.sub(r'^www\.', '', u)
    u = u.rstrip('/').split('?')[0].split('#')[0]
    return u

def completeness(r):
    """Score how complete a record is. Higher = keep this one."""
    score = 0
    if r.get('google_place_id'): score += 10
    if r.get('phone'): score += 3
    if r.get('website'): score += 3
    if r.get('address'): score += 2
    if r.get('description'): score += 2
    if r.get('rating'): score += 2
    if r.get('photos'): score += 1
    if r.get('latitude') and r.get('longitude'): score += 2
    # Prefer older (original) on tie
    return score

def name_similarity(a, b):
    return SequenceMatcher(None, norm_name(a), norm_name(b)).ratio()

def contact_match(a, b):
    """True if two rows share at least one contact signal (phone, address, website)."""
    pa, pb = norm_phone(a.get('phone')), norm_phone(b.get('phone'))
    if pa and pb and len(pa) >= 10 and pa == pb:
        return True
    aa = norm_addr(a.get('address'))
    ab = norm_addr(b.get('address'))
    ca = (a.get('city') or '').lower().strip()
    cb = (b.get('city') or '').lower().strip()
    if aa and ab and len(aa) > 10 and ca and aa == ab and ca == cb:
        return True
    sa, sb = norm_url(a.get('website')), norm_url(b.get('website'))
    if sa and sb and '.' in sa and sa == sb:
        return True
    return False

print("Fetching all listings...", flush=True)
all_rows = []
offset = 0
while True:
    batch = curl_get(
        f"/rest/v1/directory_listings?"
        f"select=id,name,phone,address,city,state,category,website,"
        f"google_place_id,rating,description,photos,latitude,longitude,created_at"
        f"&order=id&limit=1000&offset={offset}")
    if not batch: break
    all_rows.extend(batch)
    offset += 1000
    if len(batch) < 1000: break
print(f"  Total: {len(all_rows)}", flush=True)

# --- Pass 1: Same phone number (strongest signal) ---
print("\nPass 1: same phone number...", flush=True)
by_phone = defaultdict(list)
for r in all_rows:
    p = norm_phone(r.get('phone'))
    if p and len(p) >= 10:
        by_phone[p].append(r)

# --- Pass 2: Same website ---
print("Pass 2: same website...", flush=True)
by_site = defaultdict(list)
for r in all_rows:
    s = norm_url(r.get('website'))
    if s and '.' in s:
        by_site[s].append(r)

# --- Pass 3: Same normalized address + city ---
print("Pass 3: same address...", flush=True)
by_addr = defaultdict(list)
for r in all_rows:
    a = norm_addr(r.get('address'))
    city = (r.get('city') or '').lower().strip()
    if a and len(a) > 10 and city:
        by_addr[(a, city)].append(r)

# --- Pass 4: Fuzzy name in same city + category ---
print("Pass 4: fuzzy name matching...", flush=True)
by_city_cat = defaultdict(list)
for r in all_rows:
    city = (r.get('city') or '').lower().strip()
    cat = r.get('category') or ''
    if city and r.get('name'):
        by_city_cat[(city, cat)].append(r)

# Collect all duplicate groups
dup_groups = []  # list of (reason, [rows])
seen_pairs = set()

def add_group(reason, rows):
    if len(rows) < 2: return
    # Deduplicate groups that share members
    ids = frozenset(r['id'] for r in rows)
    if ids in seen_pairs: return
    seen_pairs.add(ids)
    dup_groups.append((reason, rows))

def pairwise_groups(reason, rows, threshold):
    """Group pairs with name similarity >= threshold.

    Shared contact info alone is NOT a duplicate signal: different doctors
    at one clinic share a phone, and a medical building shares an address.
    Names must also match. Pairwise groups are merged into connected
    components by the union-find step below.
    """
    n = len(rows)
    if n < 2 or n > 300: return  # skip pathological groups (shared call centers)
    names = [norm_name(r.get('name')) for r in rows]
    for i in range(n):
        for j in range(i + 1, n):
            if name_similarity(names[i], names[j]) >= threshold:
                add_group(reason, [rows[i], rows[j]])

for phone, rows in by_phone.items():
    if len(rows) > 1:
        # 0.9: "Remax Accord" vs "RE/MAX Accord" normalizes identically;
        # "Dr. Adnan Khan" vs "Dr. Harun Khan" (colleagues) does not clear it
        pairwise_groups(f"same phone+name {phone}", rows, 0.9)

for site, rows in by_site.items():
    if len(rows) > 1:
        # 0.8: same website + similar name (avoid shared corporate/franchise sites)
        pairwise_groups(f"same website+name {site}", rows, 0.8)

for key, rows in by_addr.items():
    if len(rows) > 1:
        # 0.9: same building alone is not a duplicate signal
        pairwise_groups(f"same address+name {key[0][:30]}", rows, 0.9)

# Fuzzy: O(n^2) within city+category, but groups are small
for key, rows in by_city_cat.items():
    if len(rows) < 2 or len(rows) > 200: continue
    matched = set()
    for i in range(len(rows)):
        if rows[i]['id'] in matched: continue
        group = [rows[i]]
        for j in range(i+1, len(rows)):
            if rows[j]['id'] in matched: continue
            sim = name_similarity(rows[i].get('name'), rows[j].get('name'))
            # High threshold: 0.9+ means near-identical names.
            # Plus a contact-signal guard: a similar name ALONE in the same
            # city is not a duplicate — chains have multiple locations
            # ("Ghee Indian Kitchen – Dadeland" vs "– Wynwood") and different
            # doctors share similar names ("Bushra Shah" vs "Sushma Shah").
            # Require a shared contact signal, or an exact normalized name.
            if sim >= 0.9 and (
                norm_name(rows[i].get('name')) == norm_name(rows[j].get('name'))
                or contact_match(rows[i], rows[j])
            ):
                group.append(rows[j])
                matched.add(rows[j]['id'])
        if len(group) > 1:
            matched.add(rows[i]['id'])
            add_group(f"fuzzy name {key[0]}", group)

# Merge overlapping groups
print(f"\nFound {len(dup_groups)} candidate groups, merging overlaps...", flush=True)
# Union-find
parent = {}
def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x
def union(a, b):
    ra, rb = find(a), find(b)
    if ra != rb: parent[ra] = rb

all_ids = set()
for _, rows in dup_groups:
    for r in rows:
        all_ids.add(r['id'])
        parent.setdefault(r['id'], r['id'])

for _, rows in dup_groups:
    first = rows[0]['id']
    for r in rows[1:]:
        union(first, r['id'])

merged = defaultdict(list)
id_to_row = {r['id']: r for r in all_rows}
for lid in all_ids:
    merged[find(lid)].append(id_to_row[lid])

# Decide keep/delete for each merged group
to_delete = []
for gid, rows in merged.items():
    if len(rows) < 2: continue
    # Sort by completeness (desc), then oldest first
    rows.sort(key=lambda r: (-completeness(r), r.get('created_at') or ''))
    keep = rows[0]
    for dup in rows[1:]:
        to_delete.append(dup['id'])

print(f"\n{'='*50}")
print(f"Merged duplicate groups: {len([g for g in merged.values() if len(g)>1])}")
print(f"Rows to delete: {len(to_delete)}")
print(f"Rate: {len(to_delete)/len(all_rows)*100:.1f}%")

# Show samples
print(f"\nSample groups:")
shown = 0
for gid, rows in merged.items():
    if len(rows) > 1 and shown < 8:
        names = [f"{r.get('name')} ({r.get('phone') or 'no phone'})" for r in rows]
        print(f"  KEEP: {names[0]}")
        for n in names[1:]:
            print(f"  DEL:  {n}")
        print()
        shown += 1

if '--apply' in sys.argv and to_delete:
    print(f"Deleting {len(to_delete)} duplicates...", flush=True)
    deleted = curl_delete(to_delete)
    print(f"Deleted: {deleted}")
elif to_delete:
    print("Dry run — use --apply to delete")
