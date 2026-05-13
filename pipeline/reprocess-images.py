#!/usr/bin/env python3
"""Reprocess existing article images to proper 16:9 1200x675 JPEG.

Usage:
  python3 reprocess-images.py              # reprocess Supabase images that aren't 1200x675
  python3 reprocess-images.py --fix-wikipedia  # fix articles still on Wikipedia URLs
"""

import io, os, sys, time, requests
from PIL import Image, ImageEnhance

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
UA = "TheVideshi/1.0 (news aggregator; contact@thevideshi.com)"

TARGET_W, TARGET_H = 1200, 675

def smart_crop_16_9(img):
    target_ratio = 16.0 / 9.0
    current_ratio = img.width / img.height
    if abs(current_ratio - target_ratio) < 0.05 and img.width >= TARGET_W - 10:
        return img
    if current_ratio > target_ratio:
        new_width = int(img.height * target_ratio)
        left = (img.width - new_width) // 2
        img = img.crop((left, 0, left + new_width, img.height))
    else:
        new_height = int(img.width / target_ratio)
        portrait_ratio = img.height / img.width
        if portrait_ratio > 1.3:
            top_bias = 0.15
        elif portrait_ratio > 1.0:
            top_bias = 0.25
        else:
            top_bias = 0.3
        top = int((img.height - new_height) * top_bias)
        img = img.crop((0, top, img.width, top + new_height))
    return img

def enhance_image(img):
    img = ImageEnhance.Sharpness(img).enhance(1.15)
    img = ImageEnhance.Contrast(img).enhance(1.05)
    img = ImageEnhance.Color(img).enhance(1.05)
    return img

def process_to_jpeg(raw_bytes):
    img = Image.open(io.BytesIO(raw_bytes))
    if img.mode != "RGB":
        img = img.convert("RGB")
    # Check if already correct size
    if img.width == TARGET_W and img.height == TARGET_H:
        return None  # already good
    img = smart_crop_16_9(img)
    img = img.resize((TARGET_W, TARGET_H), Image.LANCZOS)
    img = enhance_image(img)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=88, optimize=True)
    return buf.getvalue()

def upload_to_supabase(filename, jpeg_bytes):
    url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
    resp = requests.post(url, headers={
        **HEADERS,
        "Content-Type": "image/jpeg",
        "x-upsert": "true",
    }, data=jpeg_bytes, timeout=30)
    resp.raise_for_status()

def fetch_articles(filter_field=None, filter_like=None):
    url = f"{SUPABASE_URL}/rest/v1/p2_articles?select=id,headline,image_url&status=eq.published"
    if filter_field and filter_like:
        url += f"&{filter_field}=like.{filter_like}"
    resp = requests.get(url, headers={**HEADERS, "Accept": "application/json"}, timeout=30)
    resp.raise_for_status()
    return resp.json()

def update_article_image(article_id, image_url):
    url = f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}"
    body = {"image_url": image_url}
    resp = requests.patch(url, headers={
        **HEADERS,
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }, json=body, timeout=30)
    resp.raise_for_status()

def reprocess_supabase():
    print("=" * 60)
    print("🖼  Reprocessing Supabase Storage images to 1200×675")
    print("=" * 60)
    articles = fetch_articles("image_url", f"*supabase.co/storage*")
    print(f"Found {len(articles)} articles with Supabase images\n")
    
    skipped = reprocessed = errors = 0
    for i, art in enumerate(articles, 1):
        title = art["headline"][:50]
        img_url = art["image_url"]
        # Extract filename from URL
        filename = img_url.split("/article-images/")[-1]
        
        try:
            resp = requests.get(img_url, timeout=30, headers={"User-Agent": UA})
            resp.raise_for_status()
            
            result = process_to_jpeg(resp.content)
            if result is None:
                print(f"  [{i}/{len(articles)}] ✅ Already 1200×675: {title}")
                skipped += 1
            else:
                upload_to_supabase(filename, result)
                kb = len(result) // 1024
                print(f"  [{i}/{len(articles)}] 🔄 Reprocessed ({kb}KB): {title}")
                reprocessed += 1
                time.sleep(0.3)
        except Exception as e:
            print(f"  [{i}/{len(articles)}] ❌ Error: {title} — {e}")
            errors += 1
    
    print(f"\nDone: {reprocessed} reprocessed, {skipped} already good, {errors} errors")

def fix_wikipedia():
    print("=" * 60)
    print("🌐 Fixing articles with Wikipedia/Wikimedia URLs")
    print("=" * 60)
    
    all_articles = fetch_articles()
    wiki_articles = [a for a in all_articles if a.get("image_url") and 
                     ("wikipedia" in a["image_url"] or "wikimedia" in a["image_url"] or "upload.wikimedia" in a["image_url"])]
    print(f"Found {len(wiki_articles)} articles with Wikipedia URLs\n")
    
    fixed = nulled = errors = 0
    for i, art in enumerate(wiki_articles, 1):
        title = art["headline"][:50]
        img_url = art["image_url"]
        
        try:
            resp = requests.get(img_url, timeout=30, headers={"User-Agent": UA})
            if resp.status_code == 404:
                print(f"  [{i}/{len(wiki_articles)}] 🗑  404, clearing: {title}")
                update_article_image(art["id"], None)
                nulled += 1
                continue
            resp.raise_for_status()
            
            result = process_to_jpeg(resp.content)
            jpeg_bytes = result if result else resp.content
            filename = f"{art['id']}.jpg"
            upload_to_supabase(filename, jpeg_bytes)
            new_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            update_article_image(art["id"], new_url)
            kb = len(jpeg_bytes) // 1024
            print(f"  [{i}/{len(wiki_articles)}] ✅ Downloaded & uploaded ({kb}KB): {title}")
            fixed += 1
            time.sleep(0.5)
        except Exception as e:
            print(f"  [{i}/{len(wiki_articles)}] ❌ Error: {title} — {e}")
            errors += 1
    
    print(f"\nDone: {fixed} fixed, {nulled} cleared (404), {errors} errors")

if __name__ == "__main__":
    if "--fix-wikipedia" in sys.argv:
        fix_wikipedia()
    else:
        reprocess_supabase()
