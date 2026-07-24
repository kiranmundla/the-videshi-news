#!/usr/bin/env python3
"""Image sourcing for 3 sports articles — 2026-05-19."""

import os, json, requests, subprocess

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}
BUCKET = "article-images"

# Article IDs from the writer run
A1_ID = "a701395c-ab0d-4975-af45-6bf204758d4a"  # Aaron Rai
A2_ID = "794adefb-a0fa-41a1-96c5-293ac96fc044"  # Bumrah/Afghanistan
A3_ID = "b34a726b-d488-4d05-8ebe-a67d50f208eb"  # IPL Playoff

def download(url: str, path: str) -> bool:
    """Download image to path, return True if successful."""
    try:
        r = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code == 200 and len(r.content) > 1000:
            with open(path, "wb") as f:
                f.write(r.content)
            print(f"  Downloaded {path} ({len(r.content)} bytes)")
            return True
        else:
            print(f"  FAILED {url}: {r.status_code}, {len(r.content)} bytes")
            return False
    except Exception as e:
        print(f"  FAILED {url}: {e}")
        return False

def upload_to_supabase(local_path: str, remote_name: str) -> str:
    """Upload file to Supabase storage, return public URL."""
    with open(local_path, "rb") as f:
        data = f.read()
    
    url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET}/{remote_name}"
    r = requests.post(
        url,
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
        print(f"  Uploaded → {public_url}")
        return public_url
    else:
        print(f"  Upload FAILED: {r.status_code} {r.text[:200]}")
        return ""

def update_article(article_id: str, updates: dict):
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}",
        headers=HEADERS, json=updates,
    )
    if r.status_code < 300:
        print(f"  ✅ Article {article_id[:8]} updated")
    else:
        print(f"  ❌ Update failed: {r.status_code} {r.text[:200]}")

# ═══════════════════════════════════════════════════════════════════
# ARTICLE 1: Aaron Rai — Hero: Aronimink course, Gallery: Aronimink action
# ═══════════════════════════════════════════════════════════════════
print("\n═══ ARTICLE 1: Aaron Rai PGA Championship ═══")

# Clean temp files
for f in [f"/tmp/{A1_ID}_hero.jpg", f"/tmp/{A1_ID}_g1.jpg"]:
    if os.path.exists(f): os.remove(f)

hero1_url = "https://upload.wikimedia.org/wikipedia/commons/9/91/BMW_Aronimink_Golf_Final_%28436%29_%2843754635125%29.jpg"
gallery1_url = "https://upload.wikimedia.org/wikipedia/commons/5/52/Chinnaswamy_Stadium.jpg"  # Not relevant — use another Aronimink

# Try another Aronimink image  
gallery1a_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/BMW_Aronimink_Golf_Final_%28436%29_%2843754635125%29.jpg/1024px-BMW_Aronimink_Golf_Final_%28436%29_%2843754635125%29.jpg"

if download(hero1_url, f"/tmp/{A1_ID}_hero.jpg"):
    hero1_public = upload_to_supabase(f"/tmp/{A1_ID}_hero.jpg", f"{A1_ID}.jpg")
    if hero1_public:
        update_article(A1_ID, {
            "image_url": hero1_public,
            "image_attribution": "Photo: Michael Stokes / Flickr / CC BY 2.0",
            "image_caption": "Aronimink Golf Club in Newtown Square, Pennsylvania — the venue where Aaron Rai made history as the first Englishman to win the PGA Championship since 1919",
        })
else:
    print("  Skipping hero for Article 1")

# No gallery for Aaron Rai — the only specific images are copyrighted press photos
# Using the article's strong text to carry the story
print("  No additional free-use Aaron Rai images available — following 'no image > wrong image' rule")


# ═══════════════════════════════════════════════════════════════════
# ARTICLE 2: Bumrah/Afghanistan — Hero: Bumrah PMO photo, Gallery: Trent Bridge
# ═══════════════════════════════════════════════════════════════════
print("\n═══ ARTICLE 2: Bumrah Rested / Afghanistan ═══")

for f in [f"/tmp/{A2_ID}_hero.jpg", f"/tmp/{A2_ID}_g1.jpg", f"/tmp/{A2_ID}_g2.jpg"]:
    if os.path.exists(f): os.remove(f)

bumrah_hero = "https://upload.wikimedia.org/wikipedia/commons/0/02/Jasprit_Bumrah_in_PMO_New_Delhi.jpg"
bumrah_g1 = "https://upload.wikimedia.org/wikipedia/commons/3/3b/England_v_India%2C_Trent_Bridge_%2844180102251%29.jpg"
gill_g2 = "https://upload.wikimedia.org/wikipedia/commons/8/80/Shubman_Gill_2023.jpg"

if download(bumrah_hero, f"/tmp/{A2_ID}_hero.jpg"):
    hero2_public = upload_to_supabase(f"/tmp/{A2_ID}_hero.jpg", f"{A2_ID}.jpg")
    if hero2_public:
        gallery_images = []
        
        if download(bumrah_g1, f"/tmp/{A2_ID}_g1.jpg"):
            g1_public = upload_to_supabase(f"/tmp/{A2_ID}_g1.jpg", f"{A2_ID}_g1.jpg")
            if g1_public:
                gallery_images.append({
                    "url": g1_public,
                    "caption": "India's Test cricket team in action at Trent Bridge — the squad for Afghanistan features several new faces in Bumrah's absence"
                })
        
        if download(gill_g2, f"/tmp/{A2_ID}_g2.jpg"):
            g2_public = upload_to_supabase(f"/tmp/{A2_ID}_g2.jpg", f"{A2_ID}_g2.jpg")
            if g2_public:
                gallery_images.append({
                    "url": g2_public,
                    "caption": "Shubman Gill, who will captain India in both the Test and ODI series against Afghanistan starting June 6 in New Chandigarh"
                })

        update_article(A2_ID, {
            "image_url": hero2_public,
            "image_attribution": "Photo: Prime Minister's Office, India / GODL-India",
            "image_caption": "Jasprit Bumrah at the Prime Minister's Office in New Delhi — the fast bowler has been rested from the Afghanistan series as part of the BCCI's workload management programme",
            "gallery_images": gallery_images if gallery_images else None,
        })

# ═══════════════════════════════════════════════════════════════════
# ARTICLE 3: IPL Playoff — Hero: Chinnaswamy Stadium
# ═══════════════════════════════════════════════════════════════════
print("\n═══ ARTICLE 3: IPL 2026 Playoff Picture ═══")

for f in [f"/tmp/{A3_ID}_hero.jpg", f"/tmp/{A3_ID}_g1.jpg"]:
    if os.path.exists(f): os.remove(f)

chinnaswamy = "https://upload.wikimedia.org/wikipedia/commons/5/52/Chinnaswamy_Stadium.jpg"

if download(chinnaswamy, f"/tmp/{A3_ID}_hero.jpg"):
    hero3_public = upload_to_supabase(f"/tmp/{A3_ID}_hero.jpg", f"{A3_ID}.jpg")
    if hero3_public:
        update_article(A3_ID, {
            "image_url": hero3_public,
            "image_attribution": "Photo: Aniket Suryavanshi / Flickr / CC BY 2.0",
            "image_caption": "M. Chinnaswamy Stadium in Bengaluru, home of table-toppers Royal Challengers Bengaluru — the IPL 2026 final will be held at the Narendra Modi Stadium in Ahmedabad on May 31",
        })

# Clean up temp files
for prefix in [A1_ID, A2_ID, A3_ID]:
    for suffix in ["_hero.jpg", "_g1.jpg", "_g2.jpg", ".jpg"]:
        path = f"/tmp/{prefix}{suffix}"
        if os.path.exists(path):
            os.remove(path)

print("\n✅ Image sourcing complete for all 3 articles.")
