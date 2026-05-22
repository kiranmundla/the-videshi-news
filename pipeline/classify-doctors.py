#!/usr/bin/env python3
"""Classify Doctors & Healthcare listings into subcategories based on name + description keywords."""

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

RULES = [
    ("Urgent Care", [
        r"\burgent\s+care\b", r"\bwalk[\s-]in\s+clinic\b", r"\bimmediate\s+care\b",
        r"\bemergency\b(?!.*\bdental\b)"
    ]),
    ("Dentist", [
        r"\bdental\b", r"\bdentist\b", r"\bdds\b", r"\bdmd\b",
        r"\borthodont", r"\bendodont", r"\bperiodont", r"\boral\s+surg"
    ]),
    ("Pediatrician", [
        r"\bpediatric", r"\bpediatrician\b", r"\bchildren'?s?\s+(hospital|clinic|health)\b"
    ]),
    ("OB/GYN", [
        r"\bob/?gyn\b", r"\bobgyn\b", r"\bobstetric", r"\bgynecolog",
        r"\bwomen'?s?\s+health\b", r"\bmaternity\b", r"\bfertility\b", r"\bivf\b"
    ]),
    ("Cardiologist", [
        r"\bcardiol", r"\bheart\s+(specialist|doctor|clinic|center|care)\b",
        r"\bcardiac\b", r"\bcardiovascular\b"
    ]),
    ("Dermatologist", [
        r"\bdermatol", r"\bskin\s+(clinic|care|center|doctor|specialist)\b"
    ]),
    ("Ophthalmologist", [
        r"\bophthalmol", r"\beye\s+(doctor|clinic|care|center|specialist)\b",
        r"\boptometr", r"\bvision\s+(center|clinic|care)\b", r"\bretina\b"
    ]),
    ("Orthopedic", [
        r"\borthoped", r"\borthopaed", r"\bsports\s+medicine\b",
        r"\bjoint\s+(specialist|replacement)\b"
    ]),
    ("Psychiatrist / Mental Health", [
        r"\bpsychiat", r"\bpsycholog", r"\bmental\s+health\b",
        r"\btherapist\b", r"\bcounselor\b", r"\bcounseling\b",
        r"\bbehavioral\s+health\b"
    ]),
    ("Ayurveda & Holistic", [
        r"\bayurved", r"\bholistic\b", r"\bhomeopath", r"\bnaturopath",
        r"\bacupunctur", r"\bunani\b", r"\bsiddha\b", r"\byoga\s+therap"
    ]),
    ("Surgeon", [
        r"\bsurgeon\b", r"\bsurgery\b", r"\bsurgical\b"
    ]),
    ("Primary Care", [
        r"\bprimary\s+care\b", r"\bfamily\s+(medicine|practice|doctor|physician)\b",
        r"\binternal\s+medicine\b", r"\bgeneral\s+pract", r"\bgeneral\s+physician\b",
        r"\bfamily\s+health\b"
    ]),
]


def classify(name, description):
    text = f"{name} {description or ''}".lower()
    for subcategory, patterns in RULES:
        for pat in patterns:
            if re.search(pat, text):
                return subcategory
    return "General / Other"


def fetch_all_doctors():
    """Fetch all Doctors & Healthcare listings with pagination."""
    all_listings = []
    offset = 0
    batch_size = 1000
    while True:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/directory_listings",
            params={
                'select': 'id,name,description,subcategory',
                'category': 'eq.Doctors & Healthcare',
                'limit': batch_size,
                'offset': offset,
            },
            headers=headers,
            timeout=15
        )
        if r.status_code != 200:
            print(f"Error fetching at offset {offset}: {r.status_code}")
            break
        batch = r.json()
        all_listings.extend(batch)
        print(f"  Fetched {len(batch)} at offset {offset} (total: {len(all_listings)})")
        if len(batch) < batch_size:
            break
        offset += batch_size
    return all_listings


def main():
    print("Fetching all Doctors & Healthcare listings (paginated)...")
    listings = fetch_all_doctors()
    print(f"Total: {len(listings)}\n")

    # Classify all
    updates = []
    counts = {}
    for listing in listings:
        new_sub = classify(listing['name'], listing.get('description'))
        counts[new_sub] = counts.get(new_sub, 0) + 1
        old_sub = listing.get('subcategory')
        if old_sub != new_sub:
            updates.append((listing['id'], listing['name'], new_sub))

    print(f"Need to update {len(updates)} listings\n")
    print("Subcategory breakdown:")
    for sub, count in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {count:4d}  {sub}")

    # Batch updates by subcategory
    by_sub = {}
    for lid, name, sub in updates:
        by_sub.setdefault(sub, []).append((lid, name))

    print(f"\nUpdating...")
    updated = 0
    for sub, items in by_sub.items():
        for i in range(0, len(items), 50):
            batch = items[i:i+50]
            ids = [item[0] for item in batch]
            id_filter = ",".join(ids)
            r = requests.patch(
                f"{SUPABASE_URL}/rest/v1/directory_listings?id=in.({id_filter})",
                headers=headers,
                json={"subcategory": sub},
                timeout=15
            )
            if r.status_code < 300:
                updated += len(batch)
                print(f"  ✓ {len(batch):3d} → {sub}")
            else:
                print(f"  ✗ Batch failed for {sub}: {r.status_code}")
                for lid, name in batch:
                    r2 = requests.patch(
                        f"{SUPABASE_URL}/rest/v1/directory_listings?id=eq.{lid}",
                        headers=headers,
                        json={"subcategory": sub},
                        timeout=10
                    )
                    if r2.status_code < 300:
                        updated += 1

    print(f"\nDone! Updated {updated} listings")


if __name__ == "__main__":
    main()
