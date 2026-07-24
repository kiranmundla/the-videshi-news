#!/usr/bin/env python3
"""Image sourcing for 3 new articles — 2026-05-22 evening batch"""

import os, requests, time
from pathlib import Path

env_file = Path.home() / ".env.supabase"
for line in env_file.read_text().strip().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
BUCKET = "article-images"
UA = {'User-Agent': 'TheVideshiBot/1.0 (thevideshi.com; editorial)'}

ARTICLES = {
    # Iran peace talks — Strait of Hormuz satellite view
    "65946eb4-d0fe-4417-8ce9-9763cfbf6309": {
        "name": "Iran Peace Talks / Hormuz",
        "hero": {
            "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/60/Strait_of_hormuz_full.jpg/1280px-Strait_of_hormuz_full.jpg",
            "attribution": "NASA / Public Domain",
            "caption": "Satellite view of the Strait of Hormuz — the narrow waterway through which a fifth of the world's oil normally flows has been virtually closed since the Iran war began in February"
        },
    },
    # World Cup hotel bust — FIFA World Cup logo/football
    "19e3ffc4-64c0-4674-b3de-36d4870d5753": {
        "name": "FIFA World Cup 2026 Hotels",
        "hero": {
            "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/FIFA_World_Cup_Trophy_2018.jpg/800px-FIFA_World_Cup_Trophy_2018.jpg",
            "attribution": "Rhododendrites / Wikimedia Commons / CC BY-SA 4.0",
            "caption": "The FIFA World Cup trophy — with the tournament starting June 11, U.S. hotels in host cities report 80 per cent are tracking below booking expectations"
        },
    },
    # RBI rupee — Reserve Bank of India building
    "0d4b82a2-8d3d-4af6-bf08-40864d531d50": {
        "name": "RBI Rupee Crisis",
        "hero": {
            "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/RBI_HQ_Mumbai.jpg/1280px-RBI_HQ_Mumbai.jpg",
            "attribution": "A.Savin / Wikimedia Commons / CC BY-SA 3.0",
            "caption": "The Reserve Bank of India headquarters in Mumbai — the central bank has deployed an estimated $100 billion in reserves to defend the rupee since February"
        },
    },
}

def download_image(url, filepath):
    resp = requests.get(url, headers=UA, timeout=30)
    resp.raise_for_status()
    with open(filepath, 'wb') as f:
        f.write(resp.content)
    return len(resp.content)

def upload_to_supabase(filepath, remote_path):
    with open(filepath, 'rb') as f:
        data = f.read()
    
    content_type = "image/jpeg"
    if filepath.endswith(".png"):
        content_type = "image/png"
    
    headers = {
        "apikey": SB_KEY,
        "Authorization": f"Bearer {SB_KEY}",
        "Content-Type": content_type,
        "x-upsert": "true",
    }
    resp = requests.post(
        f"{SB_URL}/storage/v1/object/{BUCKET}/{remote_path}",
        headers=headers,
        data=data,
        timeout=30,
    )
    if resp.status_code in (200, 201):
        public_url = f"{SB_URL}/storage/v1/object/public/{BUCKET}/{remote_path}"
        return public_url
    else:
        print(f"  Upload error ({resp.status_code}): {resp.text[:200]}")
        return None

def update_article(article_id, updates):
    headers = {
        "apikey": SB_KEY,
        "Authorization": f"Bearer {SB_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }
    resp = requests.patch(
        f"{SB_URL}/rest/v1/p2_articles?id=eq.{article_id}",
        headers=headers,
        json=updates,
        timeout=15,
    )
    return resp.status_code in (200, 204)

for article_id, info in ARTICLES.items():
    print(f"\nProcessing: {info['name']} ({article_id[:8]})")
    
    hero = info.get('hero')
    if hero:
        try:
            local_path = f"/tmp/{article_id}_hero.jpg"
            size = download_image(hero['url'], local_path)
            print(f"  Downloaded: {size/1024:.0f} KB")
            
            remote_path = f"{article_id}.jpg"
            public_url = upload_to_supabase(local_path, remote_path)
            
            if public_url:
                success = update_article(article_id, {
                    "image_url": public_url,
                    "image_attribution": hero['attribution'],
                    "image_caption": hero['caption'],
                })
                print(f"  {'✅' if success else '❌'} Article updated")
            
            os.remove(local_path)
        except Exception as e:
            print(f"  ❌ Error: {e}")

print("\nImage sourcing complete.")
