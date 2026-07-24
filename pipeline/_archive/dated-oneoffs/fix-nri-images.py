import urllib.request
import json
import os
import time

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

headers_wiki = {
    "User-Agent": "TheVideshiBot/1.0 (https://thevideshi.com; editorial image fetch)"
}

images = [
    {
        "slug": "nyiff-2026-indian-film-festival-manhattan-nawazuddin-dil-chahta-hai-20260613",
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a3/Nawazuddin_Siddiqui_at_IFFK_2021_4_%28cropped%29.jpg/330px-Nawazuddin_Siddiqui_at_IFFK_2021_4_%28cropped%29.jpg",
        "filename": "nawazuddin-nyiff-2026.jpg"
    },
    {
        "slug": "srinath-ekkad-university-alabama-huntsville-engineering-dean-indian-or-20260613",
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/01/Engineering_Building_UAH.JPG/800px-Engineering_Building_UAH.JPG",
        "filename": "uah-engineering-building.jpg"
    }
]

for img in images:
    print(f"\n--- Downloading: {img['filename']} ---")
    req = urllib.request.Request(img["url"], headers=headers_wiki)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
            print(f"Downloaded {len(data)} bytes")
    except Exception as e:
        print(f"Failed with {img['url']}: {e}")
        # Try original size for UAH
        if "UAH" in img["filename"]:
            alt = "https://upload.wikimedia.org/wikipedia/commons/0/01/Engineering_Building_UAH.JPG"
            print(f"Trying original: {alt}")
            req2 = urllib.request.Request(alt, headers=headers_wiki)
            try:
                with urllib.request.urlopen(req2, timeout=15) as resp:
                    data = resp.read()
                    print(f"Downloaded {len(data)} bytes (original)")
            except Exception as e2:
                print(f"Also failed: {e2}")
                continue
        else:
            # Try IIFA image for Nawazuddin
            alt = "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Nawazuddin_Siddiqui_-_IIFA_2017_Green_Carpet_%2836349709816%29.jpg/800px-Nawazuddin_Siddiqui_-_IIFA_2017_Green_Carpet_%2836349709816%29.jpg"
            print(f"Trying IIFA alt: {alt}")
            req2 = urllib.request.Request(alt, headers=headers_wiki)
            try:
                with urllib.request.urlopen(req2, timeout=15) as resp:
                    data = resp.read()
                    print(f"Downloaded {len(data)} bytes (IIFA)")
            except Exception as e2:
                print(f"Also failed: {e2}")
                continue

    # Upload to Supabase storage
    path = f"article-images/{img['filename']}"
    upload_url = f"{SUPABASE_URL}/storage/v1/object/{path}"
    print(f"Uploading to Supabase: {path}")
    
    req_up = urllib.request.Request(upload_url, data=data, method="POST")
    req_up.add_header("Authorization", f"Bearer {SUPABASE_KEY}")
    req_up.add_header("apikey", SUPABASE_KEY)
    ct = "image/jpeg"
    req_up.add_header("Content-Type", ct)
    req_up.add_header("x-upsert", "true")
    
    try:
        with urllib.request.urlopen(req_up, timeout=15) as resp:
            result = resp.read().decode()
            print(f"Upload result: {result}")
    except Exception as e:
        print(f"Upload failed: {e}")
        if hasattr(e, 'read'):
            print(e.read().decode())
        continue

    # Get public URL
    public_url = f"{SUPABASE_URL}/storage/v1/object/public/{path}"
    print(f"Public URL: {public_url}")

    # Patch article
    patch_url = f"{SUPABASE_URL}/rest/v1/p2_articles?slug=eq.{img['slug']}"
    patch_data = json.dumps({"image_url": public_url}).encode()
    req_patch = urllib.request.Request(patch_url, data=patch_data, method="PATCH")
    req_patch.add_header("Authorization", f"Bearer {SUPABASE_KEY}")
    req_patch.add_header("apikey", SUPABASE_KEY)
    req_patch.add_header("Content-Type", "application/json")
    req_patch.add_header("Prefer", "return=minimal")
    
    try:
        with urllib.request.urlopen(req_patch, timeout=10) as resp:
            print(f"Patch status: {resp.status}")
    except Exception as e:
        print(f"Patch failed: {e}")
        if hasattr(e, 'read'):
            print(e.read().decode())

    time.sleep(2)  # Be polite to Wikimedia

print("\nDone!")
