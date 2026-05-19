#!/usr/bin/env python3
"""Upload images to Supabase storage and update articles."""
import os, json, requests
from pathlib import Path

# Load env
for line in (Path.home() / ".env.supabase").read_text().strip().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ[k.strip()] = v.strip()

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
BUCKET = "article-images"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
}

def upload_image(local_path, remote_name):
    """Upload image to Supabase storage bucket."""
    with open(local_path, "rb") as f:
        data = f.read()
    
    url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET}/{remote_name}"
    r = requests.post(
        url,
        headers={
            **HEADERS,
            "Content-Type": "image/jpeg",
            "x-upsert": "true"
        },
        data=data
    )
    if r.status_code in (200, 201):
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{remote_name}"
        print(f"  ✅ Uploaded {remote_name}")
        return public_url
    else:
        print(f"  ❌ Upload failed {remote_name}: {r.status_code} {r.text[:200]}")
        return None

def update_article(article_id, updates):
    """Update article fields."""
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}",
        headers={
            **HEADERS,
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        },
        json=updates
    )
    print(f"  Article {article_id[:8]} update: {r.status_code}")

# ════════════════════════════════════════════
# ARTICLE 1: USF murder case
# ════════════════════════════════════════════
AID1 = "ec2f95da-625d-4d2a-a82e-46df1ae5a823"
print(f"\n📸 Article 1: {AID1}")
url1 = upload_image("/tmp/ec2f95da_hero.jpg", f"{AID1}.jpg")
if url1:
    update_article(AID1, {
        "image_url": url1,
        "image_attribution": "Wikimedia Commons / CC BY-SA 4.0",
        "image_caption": "The USF Muma College of Business on the Tampa campus, where Bristy and Limon were doctoral students"
    })

# ════════════════════════════════════════════
# ARTICLE 2: Assam UCC
# ════════════════════════════════════════════
AID2 = "922ba9f1-7617-4692-be0b-b021025a27b3"
print(f"\n📸 Article 2: {AID2}")
url2 = upload_image("/tmp/922ba9f1_hero.jpg", f"{AID2}.jpg")
if url2:
    update_article(AID2, {
        "image_url": url2,
        "image_attribution": "Government of Assam / GODL-India",
        "image_caption": "Assam Chief Minister Himanta Biswa Sarma, who announced the UCC Bill days after being sworn in for a second term"
    })

# ════════════════════════════════════════════
# ARTICLE 3: Wadhwani-Gates
# ════════════════════════════════════════════
AID3 = "60f23d3b-4f11-47c5-86dd-a4b01ef86d3c"
print(f"\n📸 Article 3: {AID3}")
url3_hero = upload_image("/tmp/60f23d3b_hero.jpg", f"{AID3}.jpg")
url3_g1 = upload_image("/tmp/60f23d3b_g1.jpg", f"{AID3}_g1.jpg")
if url3_hero:
    gallery = []
    if url3_g1:
        gallery.append({"url": url3_g1, "caption": "The IIT Bombay campus from Sameer Hill — one of the institutions where WIN has already established a Centre of Excellence"})
    update_article(AID3, {
        "image_url": url3_hero,
        "image_attribution": "Wikimedia Commons / CC BY-SA 3.0",
        "image_caption": "The main building at IIT Bombay, where Wadhwani Innovation Network has established one of its flagship Centres of Excellence",
        "gallery_images": gallery
    })

# ════════════════════════════════════════════
# ARTICLE 4: California software tax
# ════════════════════════════════════════════
AID4 = "7af385b3-c6e2-4499-888a-168d3e48ef3d"
print(f"\n📸 Article 4: {AID4}")
url4 = upload_image("/tmp/7af385b3_hero.jpg", f"{AID4}.jpg")
if url4:
    update_article(AID4, {
        "image_url": url4,
        "image_attribution": "Office of the Governor of California / Public Domain",
        "image_caption": "Governor Gavin Newsom, whose proposed 8.25% digital software tax has drawn fierce opposition from Silicon Valley"
    })

# Clean up temp files
import glob
for f in glob.glob("/tmp/ec2f95da*") + glob.glob("/tmp/922ba9f1*") + glob.glob("/tmp/60f23d3b*") + glob.glob("/tmp/7af385b3*"):
    os.remove(f)
    
print("\n✅ Image sourcing complete")
