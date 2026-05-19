#!/usr/bin/env python3
"""Upload downloaded images to Supabase for sports articles."""

import os, json, requests

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}
BUCKET = "article-images"

A1_ID = "a701395c-ab0d-4975-af45-6bf204758d4a"  # Aaron Rai
A2_ID = "794adefb-a0fa-41a1-96c5-293ac96fc044"  # Bumrah

def upload(local_path: str, remote_name: str) -> str:
    with open(local_path, "rb") as f:
        data = f.read()
    r = requests.post(
        f"{SUPABASE_URL}/storage/v1/object/{BUCKET}/{remote_name}",
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "image/jpeg",
            "x-upsert": "true",
        },
        data=data,
    )
    if r.status_code in (200, 201):
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{remote_name}"
        print(f"  ✅ Uploaded {remote_name} ({len(data)} bytes)")
        return public_url
    else:
        print(f"  ❌ Upload failed for {remote_name}: {r.status_code} {r.text[:200]}")
        return ""

def update_article(aid: str, updates: dict):
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{aid}",
        headers=HEADERS, json=updates,
    )
    print(f"  {'✅' if r.status_code < 300 else '❌'} Article {aid[:8]} updated ({r.status_code})")

# ── Article 1: Aaron Rai ────────────────────────────────────────────────────
print("=== Article 1: Aaron Rai ===")
hero1 = upload(f"/tmp/{A1_ID}_hero.jpg", f"{A1_ID}.jpg")
if hero1:
    update_article(A1_ID, {
        "image_url": hero1,
        "image_attribution": "Photo: Michael Stokes / Flickr / CC BY 2.0",
        "image_caption": "Aronimink Golf Club in Newtown Square, Pennsylvania — the venue where Aaron Rai made history as the first Englishman to win the PGA Championship since 1919",
    })

# ── Article 2: Bumrah/Afghanistan ───────────────────────────────────────────
print("\n=== Article 2: Bumrah/Afghanistan ===")
hero2 = upload(f"/tmp/{A2_ID}_hero.jpg", f"{A2_ID}.jpg")
g1 = upload(f"/tmp/{A2_ID}_g1.jpg", f"{A2_ID}_g1.jpg")
g2 = upload(f"/tmp/{A2_ID}_g2.jpg", f"{A2_ID}_g2.jpg")

if hero2:
    gallery = []
    if g1:
        gallery.append({
            "url": g1,
            "caption": "India's Test cricket team in action at Trent Bridge — the squad for Afghanistan features several new faces in Bumrah's absence"
        })
    if g2:
        gallery.append({
            "url": g2,
            "caption": "Shubman Gill, who will captain India in both the Test and ODI series against Afghanistan starting June 6 in New Chandigarh"
        })
    update_article(A2_ID, {
        "image_url": hero2,
        "image_attribution": "Photo: Prime Minister's Office, India / GODL-India",
        "image_caption": "Jasprit Bumrah at the Prime Minister's Office in New Delhi — the fast bowler has been rested from the Afghanistan series as part of the BCCI's workload management programme",
        "gallery_images": gallery if gallery else None,
    })

# Clean up
for prefix in [A1_ID, A2_ID]:
    for suffix in ["_hero.jpg", "_g1.jpg", "_g2.jpg"]:
        path = f"/tmp/{prefix}{suffix}"
        if os.path.exists(path):
            os.remove(path)

print("\n✅ All images uploaded and articles updated.")
