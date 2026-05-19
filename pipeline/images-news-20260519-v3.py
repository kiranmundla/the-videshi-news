#!/usr/bin/env python3
"""Upload images to Supabase storage and update articles."""

import json, os, sys, requests

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
BUCKET = "article-images"

def upload_image(local_path, remote_name):
    """Upload image to Supabase storage bucket."""
    with open(local_path, "rb") as f:
        data = f.read()
    
    url = f"{SB_URL}/storage/v1/object/{BUCKET}/{remote_name}"
    headers = {
        "apikey": SB_KEY,
        "Authorization": f"Bearer {SB_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true",
    }
    r = requests.post(url, headers=headers, data=data)
    if r.status_code in (200, 201):
        public_url = f"{SB_URL}/storage/v1/object/public/{BUCKET}/{remote_name}"
        print(f"  ✓ Uploaded {remote_name} ({len(data)} bytes)")
        return public_url
    else:
        print(f"  ✗ Failed {remote_name}: {r.status_code} {r.text[:200]}")
        return None

def sb_patch(table, filter_str, data):
    headers = {
        "apikey": SB_KEY,
        "Authorization": f"Bearer {SB_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }
    r = requests.patch(f"{SB_URL}/rest/v1/{table}?{filter_str}", headers=headers, json=data)
    r.raise_for_status()

# ── ARTICLE 1: Rubio / Quad (4ddf45ec-ab72-4812-bc4e-1b9bd9291f13) ──
print("\n=== Article 1: Rubio / Quad ===")
art1_id = "4ddf45ec-ab72-4812-bc4e-1b9bd9291f13"

hero1 = upload_image("/tmp/4ddf45ec_hero.jpg", f"{art1_id}.jpg")
g1_1 = upload_image("/tmp/4ddf45ec_g1.jpg", f"{art1_id}_g1.jpg")

if hero1:
    gallery1 = []
    if g1_1:
        gallery1.append({"url": g1_1, "caption": "External Affairs Minister S. Jaishankar at the 15th BRICS Summit. He will preside over the Quad foreign ministers' meeting in New Delhi on May 26."})
    
    sb_patch("p2_articles", f"id=eq.{art1_id}", {
        "image_url": hero1,
        "image_attribution": "US Department of State / Public Domain",
        "image_caption": "US Secretary of State Marco Rubio, who will arrive in India on May 23 for a four-day visit culminating in the Quad foreign ministers' meeting in New Delhi.",
        "gallery_images": json.dumps(gallery1) if gallery1 else None,
    })
    print(f"  ✓ Updated article {art1_id[:12]}")

# ── ARTICLE 2: Google I/O (0d4a4fd6-a701-4a7d-a210-b33522c07664) ──
print("\n=== Article 2: Google I/O ===")
art2_id = "0d4a4fd6-a701-4a7d-a210-b33522c07664"

hero2 = upload_image("/tmp/0d4a4fd6_hero.jpg", f"{art2_id}.jpg")

if hero2:
    sb_patch("p2_articles", f"id=eq.{art2_id}", {
        "image_url": hero2,
        "image_attribution": "European Commission / Lukasz Kobus / CC BY 4.0",
        "image_caption": "Google CEO Sundar Pichai, who unveiled Gemini 3.5 Flash, a 24/7 personal AI agent called Spark, and $180 billion in infrastructure plans at Google I/O 2026.",
    })
    print(f"  ✓ Updated article {art2_id[:12]}")

# ── ARTICLE 3: Adani (328f0c51-c64d-405d-818c-395bfd037a61) ──
print("\n=== Article 3: Adani ===")
art3_id = "328f0c51-c64d-405d-818c-395bfd037a61"

hero3 = upload_image("/tmp/328f0c51_hero.jpg", f"{art3_id}.jpg")
g1_3 = upload_image("/tmp/328f0c51_g1.jpg", f"{art3_id}_g1.jpg")

if hero3:
    gallery3 = []
    if g1_3:
        gallery3.append({"url": g1_3, "caption": "Then-US Secretary of State John Kerry greets Adani Group Chairman Gautam Adani at the Vibrant Gujarat Summit. The Adani Group's global operations now face heightened scrutiny under US sanctions law."})
    
    sb_patch("p2_articles", f"id=eq.{art3_id}", {
        "image_url": hero3,
        "image_attribution": "Gautam Adani / CC BY 3.0 via Wikimedia Commons",
        "image_caption": "Gautam Adani, chairman of Adani Enterprises, which agreed to pay $275 million to the US Treasury to settle allegations of Iran sanctions violations.",
        "gallery_images": json.dumps(gallery3) if gallery3 else None,
    })
    print(f"  ✓ Updated article {art3_id[:12]}")

print("\n✓ All images uploaded and articles updated!")
