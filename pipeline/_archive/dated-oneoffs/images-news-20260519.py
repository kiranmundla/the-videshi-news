#!/usr/bin/env python3
"""Image sourcing for 4 news articles — 2026-05-19"""
import os, json, requests, subprocess

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}
BUCKET = "article-images"

def sb_patch(path, data):
    r = requests.patch(f"{SUPABASE_URL}/rest/v1/{path}", headers=HEADERS, json=data)
    r.raise_for_status()
    return r.json() if r.text else None

def download(url, path):
    """Download a file from URL to local path."""
    import time
    time.sleep(1.5)  # Be polite to Wikimedia
    r = requests.get(url, headers={"User-Agent": "TheVideshiNewsBot/1.0 (https://thevideshi.com; editorial@thevideshi.com)"}, timeout=30)
    r.raise_for_status()
    with open(path, "wb") as f:
        f.write(r.content)
    print(f"   Downloaded {len(r.content)} bytes → {path}")
    return len(r.content)

def upload_to_supabase(local_path, remote_name):
    """Upload image to Supabase storage bucket."""
    # Detect content type
    if remote_name.endswith('.png'):
        ct = "image/png"
    else:
        ct = "image/jpeg"
    
    with open(local_path, "rb") as f:
        data = f.read()
    
    url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET}/{remote_name}"
    r = requests.post(url, headers={
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": ct,
        "x-upsert": "true"
    }, data=data)
    
    if r.status_code in (200, 201):
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{remote_name}"
        print(f"   ✅ Uploaded → {public_url}")
        return public_url
    else:
        print(f"   ❌ Upload failed: {r.status_code} {r.text[:200]}")
        return None

def clean_tmp(article_id):
    """Clean temp files for this article."""
    import glob
    for f in glob.glob(f"/tmp/{article_id}_*"):
        os.remove(f)

# ──────────────────────────────────────────────────────────────────
# ARTICLE 1: Australia VET (87f64657-68f6-438e-9127-756bf03c3be7)
# ──────────────────────────────────────────────────────────────────
AID1 = "87f64657-68f6-438e-9127-756bf03c3be7"
print(f"\n🖼️  Article 1: Australia VET ({AID1})")
clean_tmp(AID1)

hero1_url = "https://upload.wikimedia.org/wikipedia/commons/d/d6/Central_TAFE%2C_Perth%2C_Western_Australia.jpg"
download(hero1_url, f"/tmp/{AID1}_hero.jpg")
hero1_pub = upload_to_supabase(f"/tmp/{AID1}_hero.jpg", f"{AID1}.jpg")

if hero1_pub:
    sb_patch(f"p2_articles?id=eq.{AID1}", {
        "image_url": hero1_pub,
        "image_attribution": "Nachoman-au / Wikimedia Commons (CC BY-SA 3.0)",
        "image_caption": "Central TAFE campus in Perth — Australia's vocational education sector, which serves hundreds of thousands of international students, now faces a year-long freeze on new provider registrations."
    })
    print(f"   ✅ Article 1 hero updated")

# ──────────────────────────────────────────────────────────────────
# ARTICLE 2: Alhind UAE (8fbb5cba-0434-4c81-9ee3-538988f5d1af)
# ──────────────────────────────────────────────────────────────────
AID2 = "8fbb5cba-0434-4c81-9ee3-538988f5d1af"
print(f"\n🖼️  Article 2: Alhind UAE ({AID2})")
clean_tmp(AID2)

# Hero: Modi addressing Indian community in Dubai
hero2_url = "https://upload.wikimedia.org/wikipedia/commons/9/90/The_Prime_Minister%2C_Shri_Narendra_Modi_addressing_the_gathering_at_the_Indian_Community_Reception%2C_in_Dubai_Cricket_Stadium%2C_UAE_on_August_17%2C_2015.jpg"
download(hero2_url, f"/tmp/{AID2}_hero.jpg")
hero2_pub = upload_to_supabase(f"/tmp/{AID2}_hero.jpg", f"{AID2}.jpg")

# Gallery: Abu Dhabi view
g2_url = "https://upload.wikimedia.org/wikipedia/commons/4/41/A_view_from_Lake_Park_in_Abu_Dhabi%2C_UAE.JPG"
download(g2_url, f"/tmp/{AID2}_g1.jpg")
g2_pub = upload_to_supabase(f"/tmp/{AID2}_g1.jpg", f"{AID2}_g1.jpg")

gallery2 = []
if g2_pub:
    gallery2.append({"url": g2_pub, "caption": "Abu Dhabi skyline — the UAE is home to more than 4.3 million Indians, the country's largest expatriate community, all of whom rely on consular services for passport and visa needs. Photo: Wikimedia Commons (CC BY-SA 4.0)"})

if hero2_pub:
    sb_patch(f"p2_articles?id=eq.{AID2}", {
        "image_url": hero2_pub,
        "image_attribution": "Prime Minister's Office, Government of India (GODL-India)",
        "image_caption": "PM Modi addresses the Indian community at Dubai Cricket Stadium in 2015 — over 4.3 million Indians in the UAE will see their passport and visa services shift to a new provider from July 1.",
        "gallery_images": gallery2
    })
    print(f"   ✅ Article 2 hero + gallery updated")

# ──────────────────────────────────────────────────────────────────
# ARTICLE 3: Google-Blackstone TPU (3a5fda51-70be-4265-8378-446c40705a17)
# ──────────────────────────────────────────────────────────────────
AID3 = "3a5fda51-70be-4265-8378-446c40705a17"
print(f"\n🖼️  Article 3: Google-Blackstone TPU ({AID3})")
clean_tmp(AID3)

# Hero: TPU v4
hero3_url = "https://upload.wikimedia.org/wikipedia/commons/9/99/TPU_v4.png"
download(hero3_url, f"/tmp/{AID3}_hero.png")
hero3_pub = upload_to_supabase(f"/tmp/{AID3}_hero.png", f"{AID3}.png")

# Gallery 1: Blackstone HQ
g3a_url = "https://upload.wikimedia.org/wikipedia/commons/9/9a/Blackstone_HQ_-_345_Park_Avenu.jpg"
download(g3a_url, f"/tmp/{AID3}_g1.jpg")
g3a_pub = upload_to_supabase(f"/tmp/{AID3}_g1.jpg", f"{AID3}_g1.jpg")

# Gallery 2: TPU 3.0
g3b_url = "https://upload.wikimedia.org/wikipedia/commons/b/be/Tensor_Processing_Unit_3.0.jpg"
download(g3b_url, f"/tmp/{AID3}_g2.jpg")
g3b_pub = upload_to_supabase(f"/tmp/{AID3}_g2.jpg", f"{AID3}_g2.jpg")

gallery3 = []
if g3a_pub:
    gallery3.append({"url": g3a_pub, "caption": "Blackstone headquarters at 345 Park Avenue, New York — the world's largest alternative asset manager is committing $5 billion in equity to the TPU cloud venture. Photo: Americasroof / Wikimedia Commons (CC BY-SA 3.0)"})
if g3b_pub:
    gallery3.append({"url": g3b_pub, "caption": "Google's third-generation Tensor Processing Unit — TPUs have been in production for over a decade and power Gemini, Search, and workloads for top AI labs worldwide. Photo: Zinskauf / Wikimedia Commons (CC BY-SA 4.0)"})

if hero3_pub:
    sb_patch(f"p2_articles?id=eq.{AID3}", {
        "image_url": hero3_pub,
        "image_attribution": "Jouppi et al. / Wikimedia Commons (CC BY 4.0)",
        "image_caption": "Google's TPU v4 chip — the custom silicon at the heart of the new Blackstone-Google joint venture, which aims to offer 500 megawatts of AI compute capacity by 2027.",
        "gallery_images": gallery3
    })
    print(f"   ✅ Article 3 hero + gallery updated")

# ──────────────────────────────────────────────────────────────────
# ARTICLE 4: WPI Inflation (9302a96a-0433-43bd-a0dc-24bec8a38412)
# ──────────────────────────────────────────────────────────────────
AID4 = "9302a96a-0433-43bd-a0dc-24bec8a38412"
print(f"\n🖼️  Article 4: WPI Inflation ({AID4})")
clean_tmp(AID4)

# Hero: Indian Oil fuel station
hero4_url = "https://upload.wikimedia.org/wikipedia/commons/e/e0/IndianOil_Fueling_Station_Kapsi.jpg"
download(hero4_url, f"/tmp/{AID4}_hero.jpg")
hero4_pub = upload_to_supabase(f"/tmp/{AID4}_hero.jpg", f"{AID4}.jpg")

# Gallery 1: RBI Kolkata
g4a_url = "https://upload.wikimedia.org/wikipedia/commons/f/f6/General_Post_Office_and_Reserve_Bank_of_India%2C_Kolkata%2C_India.jpg"
download(g4a_url, f"/tmp/{AID4}_g1.jpg")
g4a_pub = upload_to_supabase(f"/tmp/{AID4}_g1.jpg", f"{AID4}_g1.jpg")

# Gallery 2: Bharat Petroleum
g4b_url = "https://upload.wikimedia.org/wikipedia/commons/7/7f/Bharat_Petroleum_Petrol_Pump_near_Nagpur.jpg"
download(g4b_url, f"/tmp/{AID4}_g2.jpg")
g4b_pub = upload_to_supabase(f"/tmp/{AID4}_g2.jpg", f"{AID4}_g2.jpg")

gallery4 = []
if g4a_pub:
    gallery4.append({"url": g4a_pub, "caption": "The Reserve Bank of India building in Kolkata — the RBI faces an increasingly difficult balancing act between supporting economic growth and containing inflation, with its June 5 policy meeting under close watch. Photo: Vyacheslav Argenberg / Wikimedia Commons (CC BY 4.0)"})
if g4b_pub:
    gallery4.append({"url": g4b_pub, "caption": "A Bharat Petroleum fuel pump near Nagpur — petrol and diesel inflation jumped to 32.4% and 25.19% respectively in April, driven by crude oil prices breaching $100 per barrel. Photo: Ganesh Dhamodkar / Wikimedia Commons (CC BY-SA 4.0)"})

if hero4_pub:
    sb_patch(f"p2_articles?id=eq.{AID4}", {
        "image_url": hero4_pub,
        "image_attribution": "KeenHopper / Wikimedia Commons (CC BY-SA 4.0)",
        "image_caption": "An Indian Oil fuel station — with crude petroleum inflation at 88% and fuel prices surging, India's wholesale inflation has hit a 42-month high of 8.3%.",
        "gallery_images": gallery4
    })
    print(f"   ✅ Article 4 hero + gallery updated")

# Cleanup
for aid in [AID1, AID2, AID3, AID4]:
    clean_tmp(aid)

print("\n✅ Image sourcing complete for all 4 articles")
