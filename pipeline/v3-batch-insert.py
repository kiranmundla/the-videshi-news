#!/usr/bin/env python3
"""V3 batch article inserter. Reads articles from /tmp/v3-articles.json, finds images, uploads, and inserts."""
import json, os, sys, subprocess, re, time, urllib.parse
from datetime import datetime, timezone

def load_env(*paths):
    for p in paths:
        p = os.path.expanduser(p)
        if os.path.exists(p):
            with open(p) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

load_env("~/workspace/.env.supabase", "~/workspace/.env.pexels")

SB_URL = os.environ.get("SUPABASE_URL", "")
SB_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")

def sb_post(endpoint, data):
    payload = json.dumps(data)
    cmd = ["curl", "-sS", "--max-time", "30", "-X", "POST",
           f"{SB_URL}/rest/v1/{endpoint}",
           "-H", f"apikey: {SB_KEY}",
           "-H", f"Authorization: Bearer {SB_KEY}",
           "-H", "Content-Type: application/json",
           "-H", "Prefer: return=representation",
           "-d", payload]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=35)
    if r.returncode != 0:
        return None, f"curl error {r.returncode}"
    try:
        result = json.loads(r.stdout)
        if isinstance(result, list) and len(result) > 0:
            return result[0], None
        elif isinstance(result, dict) and "id" in result:
            return result, None
        else:
            return None, f"Unexpected response: {r.stdout[:200]}"
    except:
        return None, f"JSON parse error: {r.stdout[:200]}"

def sb_patch(endpoint, data):
    payload = json.dumps(data)
    cmd = ["curl", "-sS", "--max-time", "20", "-X", "PATCH",
           f"{SB_URL}/rest/v1/{endpoint}",
           "-H", f"apikey: {SB_KEY}",
           "-H", f"Authorization: Bearer {SB_KEY}",
           "-H", "Content-Type: application/json",
           "-d", payload]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
    return r.returncode == 0

def sb_get(endpoint):
    cmd = ["curl", "-sS", "--max-time", "20",
           f"{SB_URL}/rest/v1/{endpoint}",
           "-H", f"apikey: {SB_KEY}",
           "-H", f"Authorization: Bearer {SB_KEY}"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
    if r.returncode == 0:
        try:
            return json.loads(r.stdout)
        except:
            pass
    return None

def search_person_image(name):
    encoded = urllib.parse.quote(name.lower())
    result = sb_get(f"person_images?person_name_lower=eq.{encoded}&order=use_count.asc,last_used_at.asc.nullsfirst&limit=1")
    if result and len(result) > 0:
        return result[0]
    return None

def search_wikipedia_image(term):
    encoded = urllib.parse.quote(term.replace(" ", "_"))
    cmd = ["curl", "-sS", "--max-time", "15",
           f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
           "-H", "User-Agent: TheVideshi/1.0 (thevideshi.com)"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    if r.returncode == 0:
        try:
            data = json.loads(r.stdout)
            if "originalimage" in data:
                return data["originalimage"]["source"], data.get("title", term)
            elif "thumbnail" in data:
                return data["thumbnail"]["source"], data.get("title", term)
        except:
            pass
    return None, None

def search_pexels(query):
    if not PEXELS_KEY:
        return None, None
    encoded = urllib.parse.quote(query)
    cmd = ["curl", "-sS", "--max-time", "15",
           f"https://api.pexels.com/v1/search?query={encoded}&per_page=3&orientation=landscape",
           "-H", f"Authorization: {PEXELS_KEY}"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    if r.returncode == 0:
        try:
            data = json.loads(r.stdout)
            photos = data.get("photos", [])
            if photos:
                p = photos[0]
                url = p.get("src", {}).get("large2x") or p.get("src", {}).get("original")
                photographer = p.get("photographer", "Pexels")
                return url, photographer
        except:
            pass
    return None, None

def download_and_compress(url, slug):
    """Download image and compress to <= 200KB."""
    out_path = f"/tmp/{slug}.jpg"
    cmd = ["curl", "-sS", "--max-time", "30", "-L",
           "-A", "TheVideshi/1.0 (thevideshi.com)",
           "-o", out_path, url]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=35)
    if r.returncode != 0:
        return None
    
    # Check file size
    try:
        size = os.path.getsize(out_path)
    except:
        return None
    
    if size == 0:
        return None
    
    # Compress if needed using Python PIL
    if size > 200000:
        try:
            from PIL import Image
            compressed = f"/tmp/{slug}_compressed.jpg"
            img = Image.open(out_path)
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            # Resize if very large
            max_dim = 1200
            if max(img.size) > max_dim:
                img.thumbnail((max_dim, max_dim), Image.LANCZOS)
            quality = 70 if size > 500000 else 78
            img.save(compressed, "JPEG", quality=quality, optimize=True)
            if os.path.exists(compressed) and os.path.getsize(compressed) > 0:
                return compressed
        except Exception as e:
            print(f"  Compression error: {e}")
    
    return out_path

def upload_to_supabase(local_path, slug):
    """Upload image to Supabase storage."""
    storage_path = f"article-images/{slug}.jpg"
    url = f"{SB_URL}/storage/v1/object/article-images/{slug}.jpg"
    
    with open(local_path, "rb") as f:
        img_bytes = f.read()
    
    cmd = ["curl", "-sS", "--max-time", "30",
           "-X", "POST", url,
           "-H", f"apikey: {SB_KEY}",
           "-H", f"Authorization: Bearer {SB_KEY}",
           "-H", "Content-Type: image/jpeg",
           "-H", "x-upsert: true",
           "--data-binary", f"@{local_path}"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=35)
    
    if r.returncode == 0:
        try:
            data = json.loads(r.stdout)
            if "Key" in data or "Id" in data:
                public_url = f"{SB_URL}/storage/v1/object/public/article-images/{slug}.jpg"
                return public_url
        except:
            pass
    
    # Fallback: try PUT
    cmd2 = ["curl", "-sS", "--max-time", "30",
            "-X", "PUT", url,
            "-H", f"apikey: {SB_KEY}",
            "-H", f"Authorization: Bearer {SB_KEY}",
            "-H", "Content-Type: image/jpeg",
            "--data-binary", f"@{local_path}"]
    r2 = subprocess.run(cmd2, capture_output=True, text=True, timeout=35)
    if r2.returncode == 0:
        public_url = f"{SB_URL}/storage/v1/object/public/article-images/{slug}.jpg"
        return public_url
    
    return None

def count_words(html):
    text = re.sub(r'<[^>]+>', '', html)
    return len(text.split())

def process_article(article):
    slug = article["slug"]
    print(f"\n{'='*60}")
    print(f"Processing: {article['headline']}")
    print(f"  Category: {article['category']}")
    
    # Image sourcing
    image_url = None
    image_caption = article.get("image_caption", "")
    image_attribution = article.get("image_attribution", "")
    
    # Try person_images first
    for person in article.get("image_search_persons", []):
        pi = search_person_image(person)
        if pi:
            image_url = pi["image_url"]
            image_attribution = pi.get("attribution", f"Photo of {person}")
            print(f"  Image: person_images hit for '{person}'")
            # Update use count
            sb_patch(f"person_images?id=eq.{pi['id']}", {
                "use_count": pi.get("use_count", 0) + 1,
                "last_used_at": datetime.now(timezone.utc).isoformat()
            })
            break
    
    # Try Wikipedia
    if not image_url:
        for term in article.get("image_search_wiki", []):
            wiki_url, wiki_title = search_wikipedia_image(term)
            if wiki_url:
                image_url = wiki_url
                image_attribution = f"Wikimedia Commons"
                print(f"  Image: Wikipedia hit for '{term}'")
                break
    
    # Try Pexels
    if not image_url:
        for query in article.get("image_search_pexels", []):
            pexels_url, photographer = search_pexels(query)
            if pexels_url:
                image_url = pexels_url
                image_attribution = f"Photo by {photographer} / Pexels"
                print(f"  Image: Pexels hit for '{query}'")
                break
    
    # Download, compress, upload
    if image_url:
        local = download_and_compress(image_url, slug)
        if local:
            uploaded = upload_to_supabase(local, slug)
            if uploaded:
                image_url = uploaded
                print(f"  Image uploaded: {uploaded}")
            else:
                print(f"  WARNING: Upload failed, using original URL")
        else:
            print(f"  WARNING: Download/compress failed")
    else:
        print(f"  WARNING: No image found")
        image_url = ""
    
    # Calculate word count
    wc = count_words(article["body"])
    
    # Insert article
    now_iso = datetime.now(timezone.utc).isoformat()
    row = {
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "body": article["body"],
        "slug": slug,
        "category": article["category"],
        "vertical": article["category"],
        "kids_relevant": article.get("kids_relevant", False),
        "tags": article.get("tags", []),
        "sources": article.get("sources", []),
        "image_url": image_url,
        "image_caption": image_caption,
        "image_attribution": image_attribution,
        "word_count": wc,
        "diaspora_angle": article.get("diaspora_angle", ""),
        "topic_id": article.get("topic_id"),
        "status": "published",
        "published_at": now_iso,
        "article_type": "breaking"
    }
    
    result, error = sb_post("p2_articles", row)
    if error:
        print(f"  ERROR inserting: {error}")
        return False
    
    article_id = result.get("id")
    print(f"  Inserted: id={article_id}, {wc} words")
    
    # Update topic status
    if article.get("topic_id"):
        sb_patch(f"p2_topics?id=eq.{article['topic_id']}", {
            "status": "published",
            "last_article_id": article_id
        })
        print(f"  Topic updated")
    
    return True

def main():
    with open("/tmp/v3-articles.json") as f:
        articles = json.load(f)
    
    print(f"Processing {len(articles)} articles...")
    success = 0
    for a in articles:
        if process_article(a):
            success += 1
    
    print(f"\n{'='*60}")
    print(f"Done: {success}/{len(articles)} articles published")

if __name__ == "__main__":
    main()
