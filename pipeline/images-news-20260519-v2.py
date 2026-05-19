#!/usr/bin/env python3
"""Image sourcing for 4 news articles — 2026-05-19 (v2 with retries)"""
import os, json, requests, time, glob
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}
BUCKET = "article-images"

session = requests.Session()
retry = Retry(total=3, backoff_factor=2, status_forcelist=[429, 500, 502, 503, 504])
session.mount("https://", HTTPAdapter(max_retries=retry))

def sb_patch(path, data):
    r = session.patch(f"{SUPABASE_URL}/rest/v1/{path}", headers=HEADERS, json=data, timeout=30)
    r.raise_for_status()
    return r.json() if r.text else None

def download(url, path):
    time.sleep(2)
    r = session.get(url, headers={"User-Agent": "TheVideshiNewsBot/1.0 (https://thevideshi.com; editorial@thevideshi.com)"}, timeout=60)
    r.raise_for_status()
    with open(path, "wb") as f:
        f.write(r.content)
    print(f"   Downloaded {len(r.content)} bytes → {os.path.basename(path)}")
    return len(r.content)

def upload_to_supabase(local_path, remote_name):
    ct = "image/png" if remote_name.endswith('.png') else "image/jpeg"
    with open(local_path, "rb") as f:
        data = f.read()
    
    url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET}/{remote_name}"
    for attempt in range(3):
        try:
            r = session.post(url, headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": ct,
                "x-upsert": "true"
            }, data=data, timeout=60)
            if r.status_code in (200, 201):
                public_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{remote_name}"
                print(f"   ✅ Uploaded → {remote_name}")
                return public_url
            else:
                print(f"   ⚠️ Upload attempt {attempt+1} failed: {r.status_code}")
        except Exception as e:
            print(f"   ⚠️ Upload attempt {attempt+1} error: {e}")
        time.sleep(3)
    print(f"   ❌ Upload failed after 3 attempts")
    return None

def clean_tmp(article_id):
    for f in glob.glob(f"/tmp/{article_id}_*"):
        os.remove(f)

def process_article(aid, hero_info, gallery_info):
    """Process images for one article.
    hero_info: (url, filename_ext, attribution, caption)
    gallery_info: [(url, filename_ext, attribution_caption), ...]
    """
    print(f"\n🖼️  Processing {aid}")
    clean_tmp(aid)
    
    hero_url, hero_ext, hero_attr, hero_cap = hero_info
    try:
        download(hero_url, f"/tmp/{aid}_hero{hero_ext}")
        hero_pub = upload_to_supabase(f"/tmp/{aid}_hero{hero_ext}", f"{aid}{hero_ext}")
    except Exception as e:
        print(f"   ❌ Hero download failed: {e}")
        hero_pub = None
    
    gallery = []
    for i, (g_url, g_ext, g_caption) in enumerate(gallery_info, 1):
        try:
            download(g_url, f"/tmp/{aid}_g{i}{g_ext}")
            g_pub = upload_to_supabase(f"/tmp/{aid}_g{i}{g_ext}", f"{aid}_g{i}{g_ext}")
            if g_pub:
                gallery.append({"url": g_pub, "caption": g_caption})
        except Exception as e:
            print(f"   ⚠️ Gallery {i} failed: {e}")
    
    update = {}
    if hero_pub:
        update["image_url"] = hero_pub
        update["image_attribution"] = hero_attr
        update["image_caption"] = hero_cap
    if gallery:
        update["gallery_images"] = gallery
    
    if update:
        sb_patch(f"p2_articles?id=eq.{aid}", update)
        print(f"   ✅ Article updated (hero={'yes' if hero_pub else 'no'}, gallery={len(gallery)})")
    
    clean_tmp(aid)

# ── ARTICLE 1: Australia VET ──
process_article(
    "87f64657-68f6-438e-9127-756bf03c3be7",
    hero_info=(
        "https://upload.wikimedia.org/wikipedia/commons/d/d6/Central_TAFE%2C_Perth%2C_Western_Australia.jpg",
        ".jpg",
        "Nachoman-au / Wikimedia Commons (CC BY-SA 3.0)",
        "Central TAFE campus in Perth — Australia's vocational education sector, which serves hundreds of thousands of international students, now faces a year-long freeze on new provider registrations."
    ),
    gallery_info=[]
)

# ── ARTICLE 2: Alhind UAE ──
process_article(
    "8fbb5cba-0434-4c81-9ee3-538988f5d1af",
    hero_info=(
        "https://upload.wikimedia.org/wikipedia/commons/9/90/The_Prime_Minister%2C_Shri_Narendra_Modi_addressing_the_gathering_at_the_Indian_Community_Reception%2C_in_Dubai_Cricket_Stadium%2C_UAE_on_August_17%2C_2015.jpg",
        ".jpg",
        "Prime Minister's Office, Government of India (GODL-India)",
        "PM Modi addresses the Indian community at Dubai Cricket Stadium in 2015 — over 4.3 million Indians in the UAE will see their passport and visa services shift to a new provider from July 1."
    ),
    gallery_info=[
        (
            "https://upload.wikimedia.org/wikipedia/commons/4/41/A_view_from_Lake_Park_in_Abu_Dhabi%2C_UAE.JPG",
            ".jpg",
            "Abu Dhabi skyline — the UAE is home to more than 4.3 million Indians, the country's largest expatriate community. Photo: Wikimedia Commons (CC BY-SA 4.0)"
        )
    ]
)

# ── ARTICLE 3: Google-Blackstone TPU ──
process_article(
    "3a5fda51-70be-4265-8378-446c40705a17",
    hero_info=(
        "https://upload.wikimedia.org/wikipedia/commons/9/99/TPU_v4.png",
        ".png",
        "Jouppi et al. / Wikimedia Commons (CC BY 4.0)",
        "Google's TPU v4 chip — the custom silicon at the heart of the new Blackstone-Google joint venture, which aims to offer 500 megawatts of AI compute capacity by 2027."
    ),
    gallery_info=[
        (
            "https://upload.wikimedia.org/wikipedia/commons/9/9a/Blackstone_HQ_-_345_Park_Avenu.jpg",
            ".jpg",
            "Blackstone headquarters at 345 Park Avenue, New York — the world's largest alternative asset manager is committing $5 billion in equity to the TPU cloud venture. Photo: Americasroof / Wikimedia Commons (CC BY-SA 3.0)"
        ),
        (
            "https://upload.wikimedia.org/wikipedia/commons/b/be/Tensor_Processing_Unit_3.0.jpg",
            ".jpg",
            "Google's third-generation Tensor Processing Unit — TPUs have been in production for over a decade and power Gemini, Search, and workloads for top AI labs worldwide. Photo: Zinskauf / Wikimedia Commons (CC BY-SA 4.0)"
        )
    ]
)

# ── ARTICLE 4: WPI Inflation ──
process_article(
    "9302a96a-0433-43bd-a0dc-24bec8a38412",
    hero_info=(
        "https://upload.wikimedia.org/wikipedia/commons/e/e0/IndianOil_Fueling_Station_Kapsi.jpg",
        ".jpg",
        "KeenHopper / Wikimedia Commons (CC BY-SA 4.0)",
        "An Indian Oil fuel station — with crude petroleum inflation at 88% and fuel prices surging, India's wholesale inflation has hit a 42-month high of 8.3%."
    ),
    gallery_info=[
        (
            "https://upload.wikimedia.org/wikipedia/commons/f/f6/General_Post_Office_and_Reserve_Bank_of_India%2C_Kolkata%2C_India.jpg",
            ".jpg",
            "The Reserve Bank of India building in Kolkata — the RBI faces an increasingly difficult balancing act between supporting economic growth and containing inflation. Photo: Vyacheslav Argenberg / Wikimedia Commons (CC BY 4.0)"
        ),
        (
            "https://upload.wikimedia.org/wikipedia/commons/7/7f/Bharat_Petroleum_Petrol_Pump_near_Nagpur.jpg",
            ".jpg",
            "A Bharat Petroleum fuel pump near Nagpur — petrol and diesel inflation jumped to 32.4% and 25.19% respectively in April. Photo: Ganesh Dhamodkar / Wikimedia Commons (CC BY-SA 4.0)"
        )
    ]
)

print("\n✅ Image sourcing complete")
