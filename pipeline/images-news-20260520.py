#!/usr/bin/env python3
"""Download images from Wikimedia Commons and upload to Supabase for 3 articles."""
import json, os, subprocess, sys, urllib.parse, time

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
BUCKET = "article-images"

def get_commons_url(filename):
    """Get direct image URL from Wikimedia Commons."""
    encoded = urllib.parse.quote(filename.replace("File:", ""))
    url = f"https://commons.wikimedia.org/w/api.php?action=query&titles=File:{encoded}&prop=imageinfo&iiprop=url&format=json"
    result = subprocess.run(["curl", "-s", url], capture_output=True, text=True)
    try:
        data = json.loads(result.stdout)
        pages = data.get("query", {}).get("pages", {})
        for page in pages.values():
            info = page.get("imageinfo", [{}])[0]
            return info.get("url")
    except:
        pass
    return None

def download_image(url, filepath):
    """Download image to local path."""
    result = subprocess.run(
        ["curl", "-s", "-L", "-o", filepath, "-H", 
         "User-Agent: TheVideshi/1.0 (https://thevideshi.com; contact@thevideshi.com)",
         url],
        capture_output=True, text=True, timeout=30
    )
    return os.path.exists(filepath) and os.path.getsize(filepath) > 1000

def upload_to_supabase(filepath, dest_path):
    """Upload to Supabase Storage."""
    content_type = "image/jpeg"
    if filepath.endswith(".png"):
        content_type = "image/png"
    elif filepath.endswith(".svg"):
        content_type = "image/svg+xml"
    elif filepath.endswith(".webp"):
        content_type = "image/webp"
    
    result = subprocess.run([
        "curl", "-s", "-X", "POST",
        f"{SB_URL}/storage/v1/object/{BUCKET}/{dest_path}",
        "-H", f"apikey: {SB_KEY}",
        "-H", f"Authorization: Bearer {SB_KEY}",
        "-H", f"Content-Type: {content_type}",
        "--data-binary", f"@{filepath}"
    ], capture_output=True, text=True)
    
    public_url = f"{SB_URL}/storage/v1/object/public/{BUCKET}/{dest_path}"
    return public_url

def update_article(article_id, data):
    """Patch article in Supabase."""
    subprocess.run([
        "curl", "-s", "-X", "PATCH",
        f"{SB_URL}/rest/v1/p2_articles?id=eq.{article_id}",
        "-H", f"apikey: {SB_KEY}",
        "-H", f"Authorization: Bearer {SB_KEY}",
        "-H", "Content-Type: application/json",
        "-H", "Prefer: return=minimal",
        "-d", json.dumps(data)
    ], capture_output=True, text=True)


# Clean temp files first
for f in os.listdir("/tmp"):
    if f.endswith((".jpg", ".png", ".webp", ".svg")) and "_" in f:
        try: os.remove(f"/tmp/{f}")
        except: pass

# ══════════════════════════════════════════════════════════
# ARTICLE 1: Amazon H-1B (nri-world)
# ══════════════════════════════════════════════════════════
ART1 = "5561cf6a-c086-46c2-bd5c-2427ab28814a"
print(f"\n=== Article 1: Amazon H-1B ===")

images_a1 = [
    ("Amazon Spheres 2018.jpg", "hero", "The Amazon Spheres at the company's Seattle headquarters — a symbol of the tech giant's growing ambitions even as it lays off thousands"),
    ("Day 1 Tower Seattle WA Jan 17.jpg", "g1", "Amazon's Day 1 Tower in Seattle, where corporate employees have faced multiple rounds of layoffs since late 2025"),
    ("H-1B Visa Updates.jpg", "g2", "H-1B visa documentation — the gateway through which hundreds of thousands of Indian tech workers enter the American workforce"),
]

gallery_a1 = []
hero_url_a1 = None

for filename, suffix, caption in images_a1:
    url = get_commons_url(filename)
    if not url:
        print(f"  ❌ No URL for {filename}")
        continue
    
    ext = ".jpg"
    if ".png" in url.lower(): ext = ".png"
    elif ".webp" in url.lower(): ext = ".webp"
    
    local = f"/tmp/{ART1}_{suffix}{ext}"
    if download_image(url, local):
        dest = f"{ART1}{'_' + suffix if suffix != 'hero' else ''}{ext}"
        pub_url = upload_to_supabase(local, dest)
        print(f"  ✅ {suffix}: {filename} → {pub_url[:80]}...")
        
        if suffix == "hero":
            hero_url_a1 = pub_url
        else:
            gallery_a1.append({"url": pub_url, "caption": caption})
    else:
        print(f"  ❌ Download failed: {filename}")
    time.sleep(0.5)

if hero_url_a1:
    update_data = {
        "image_url": hero_url_a1,
        "image_attribution": "Wikimedia Commons (CC BY-SA 4.0)",
        "image_caption": images_a1[0][2],
    }
    if gallery_a1:
        update_data["gallery_images"] = gallery_a1
    update_article(ART1, update_data)
    print(f"  ✅ Article updated with {1 + len(gallery_a1)} images")

# ══════════════════════════════════════════════════════════
# ARTICLE 2: Rupee / RBI (markets-finance)
# ══════════════════════════════════════════════════════════
ART2 = "c0f27614-dce0-4103-b9f2-61c63023157e"
print(f"\n=== Article 2: Rupee / RBI ===")

images_a2 = [
    ("Tower and building of Reserve Bank of India, Mumbai 02.jpg", "hero", "The Reserve Bank of India's headquarters in Mumbai — the central bank announced a $5 billion emergency swap to stem the rupee's slide"),
    ("Reserve Bank of India Building.jpg", "g1", "The RBI's historic building — the institution has spent tens of billions defending the rupee since the Iran conflict erupted in February"),
    ("2016 Indian currency note demonetisation.jpg", "g2", "Indian currency notes — the rupee has lost more than 7 per cent of its value against the dollar in 2026, making it Asia's worst performer"),
]

gallery_a2 = []
hero_url_a2 = None

for filename, suffix, caption in images_a2:
    url = get_commons_url(filename)
    if not url:
        print(f"  ❌ No URL for {filename}")
        continue
    
    ext = ".jpg"
    if ".png" in url.lower(): ext = ".png"
    
    local = f"/tmp/{ART2}_{suffix}{ext}"
    if download_image(url, local):
        dest = f"{ART2}{'_' + suffix if suffix != 'hero' else ''}{ext}"
        pub_url = upload_to_supabase(local, dest)
        print(f"  ✅ {suffix}: {filename[:50]}... → uploaded")
        
        if suffix == "hero":
            hero_url_a2 = pub_url
        else:
            gallery_a2.append({"url": pub_url, "caption": caption})
    else:
        print(f"  ❌ Download failed: {filename}")
    time.sleep(0.5)

if hero_url_a2:
    update_data = {
        "image_url": hero_url_a2,
        "image_attribution": "Wikimedia Commons (CC BY-SA 4.0)",
        "image_caption": images_a2[0][2],
    }
    if gallery_a2:
        update_data["gallery_images"] = gallery_a2
    update_article(ART2, update_data)
    print(f"  ✅ Article updated with {1 + len(gallery_a2)} images")

# ══════════════════════════════════════════════════════════
# ARTICLE 3: IT Pricing (technology)
# ══════════════════════════════════════════════════════════
ART3 = "cf966089-0621-4b1a-8fa1-d3cbc385ada7"
print(f"\n=== Article 3: IT Pricing ===")

images_a3 = [
    ("Cognizant Technology Solutions office, Calcutta.jpg", "hero", "Cognizant's offices in Kolkata — the company has introduced tokenized rate cards that price AI-led work alongside human effort"),
    ("ITPL Bangalore 1.jpg", "g1", "The International Tech Park in Bangalore — epicentre of India's IT services industry now navigating the shift from billable hours to AI tokens"),
    ("Infosys Mysore Campus.jpg", "g2", "The Infosys campus in Mysore — India's IT giants collectively employ 5.4 million people whose roles are being redefined by AI"),
]

gallery_a3 = []
hero_url_a3 = None

for filename, suffix, caption in images_a3:
    url = get_commons_url(filename)
    if not url:
        print(f"  ❌ No URL for {filename}")
        continue
    
    ext = ".jpg"
    if ".png" in url.lower(): ext = ".png"
    
    local = f"/tmp/{ART3}_{suffix}{ext}"
    if download_image(url, local):
        dest = f"{ART3}{'_' + suffix if suffix != 'hero' else ''}{ext}"
        pub_url = upload_to_supabase(local, dest)
        print(f"  ✅ {suffix}: {filename[:50]}... → uploaded")
        
        if suffix == "hero":
            hero_url_a3 = pub_url
        else:
            gallery_a3.append({"url": pub_url, "caption": caption})
    else:
        print(f"  ❌ Download failed: {filename}")
    time.sleep(0.5)

if hero_url_a3:
    update_data = {
        "image_url": hero_url_a3,
        "image_attribution": "Wikimedia Commons (CC BY-SA 4.0)",
        "image_caption": images_a3[0][2],
    }
    if gallery_a3:
        update_data["gallery_images"] = gallery_a3
    update_article(ART3, update_data)
    print(f"  ✅ Article updated with {1 + len(gallery_a3)} images")

print("\n=== Image sourcing complete ===")
