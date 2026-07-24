#!/usr/bin/env python3
"""Fix images for the 3 PM2 news articles (2026-06-15).
Wikimedia 429s Python requests but curl works (see AGENTS.md). Pexels via curl.
Download -> upload to Supabase storage 'article-images' -> patch article image_url."""
import os, json, subprocess, urllib.parse, requests
from pathlib import Path

def load_env(path):
    p = Path(path).expanduser()
    if not p.exists():
        return
    for line in p.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, _, v = line.partition('=')
            os.environ[k.strip().replace('export ', '')] = v.strip().strip('"').strip("'")

load_env('~/.env.supabase')
load_env('~/workspace/.env.pexels')

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')
BUCKET = "article-images"
UA = "TheVideshi/1.0 (thevideshi.com)"

H = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}


def commons_candidates(query, limit=8):
    params = {
        "action": "query", "generator": "search", "gsrsearch": query,
        "gsrnamespace": "6", "gsrlimit": str(limit), "prop": "imageinfo",
        "iiprop": "url|size|mime", "iiurlwidth": "1200", "format": "json"
    }
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)
    try:
        out = subprocess.run(["curl", "-sS", "-A", UA, url],
                             capture_output=True, text=True, timeout=20).stdout
        data = json.loads(out)
        pages = data.get("query", {}).get("pages", {})
        res = []
        for _, page in pages.items():
            ii = page.get("imageinfo", [{}])[0]
            u = ii.get("thumburl") or ii.get("url")
            if u and "image" in ii.get("mime", "") and ii.get("width", 0) > 300:
                res.append({"url": u, "title": page.get("title", "")})
        return res
    except Exception as e:
        print(f"  commons err: {e}")
        return []


def pexels_url(query):
    if not PEXELS_KEY:
        return None
    try:
        out = subprocess.run(
            ["curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
             f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=5&orientation=landscape"],
            capture_output=True, text=True, timeout=20).stdout
        data = json.loads(out)
        for p in data.get("photos", []):
            u = p.get("src", {}).get("large2x") or p.get("src", {}).get("large")
            if u:
                return u
    except Exception as e:
        print(f"  pexels err: {e}")
    return None


def download(url, dest):
    """curl download; returns True if file >5KB and looks like an image."""
    r = subprocess.run(["curl", "-sS", "-L", "-A", UA, "-o", dest, url],
                       capture_output=True, text=True, timeout=40)
    if not os.path.exists(dest):
        return False
    sz = os.path.getsize(dest)
    # sniff content type
    ft = subprocess.run(["file", "-b", "--mime-type", dest], capture_output=True, text=True).stdout.strip()
    ok = sz > 5000 and ft.startswith("image/")
    print(f"    dl {sz}b {ft} -> {'OK' if ok else 'reject'}")
    return ok


def upload(local, remote):
    with open(local, "rb") as f:
        data = f.read()
    ext = os.path.splitext(local)[1].lower()
    ct = "image/png" if ext == ".png" else "image/jpeg"
    url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET}/{remote}"
    r = requests.post(url, headers={**H, "Content-Type": ct, "x-upsert": "true"}, data=data, timeout=60)
    if r.status_code in (200, 201):
        return f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{remote}"
    print(f"  upload fail {r.status_code}: {r.text[:200]}")
    return None


def patch(slug, image_url, caption, attribution):
    url = f"{SUPABASE_URL}/rest/v1/p2_articles?slug=eq.{slug}"
    payload = {"image_url": image_url, "image_caption": caption, "image_attribution": attribution}
    r = requests.patch(url, headers={**H, "Content-Type": "application/json", "Prefer": "return=minimal"},
                       json=payload, timeout=20)
    print(f"  patch {slug}: {r.status_code}")
    return r.status_code in (200, 204)


def source_and_set(slug, commons_queries, keyword_sets, captions, pexels_q, pexels_caption, idx):
    print(f"\n=== {slug} ===")
    # try commons queries
    for q, kws, cap in zip(commons_queries, keyword_sets, captions):
        for c in commons_candidates(q):
            tl = c["title"].lower()
            if any(k in tl for k in kws):
                dest = f"/tmp/news_img_{idx}.jpg"
                if download(c["url"], dest):
                    pub = upload(dest, f"news-pm2-{idx}-{slug[:40]}.jpg")
                    if pub:
                        return patch(slug, pub, cap, "Wikimedia Commons")
    # fallback pexels
    pu = pexels_url(pexels_q)
    if pu:
        dest = f"/tmp/news_img_{idx}.jpg"
        if download(pu, dest):
            pub = upload(dest, f"news-pm2-{idx}-{slug[:40]}.jpg")
            if pub:
                return patch(slug, pub, pexels_caption, "Pexels")
    print("  !! no image found")
    return False


if __name__ == "__main__":
    source_and_set(
        "india-dgs-restricts-seafarer-deployment-gulf-conflict-zones-settebello-20260615",
        ["Strait of Hormuz tanker", "oil tanker Gulf of Oman", "crude oil tanker ship"],
        [["tanker", "hormuz", "oil", "ship", "strait"],
         ["tanker", "oman", "gulf", "ship", "vessel"],
         ["tanker", "ship", "vessel", "oil", "crude"]],
        ["An oil tanker in the Strait of Hormuz, where Indian-crewed vessels have come under attack",
         "A commercial tanker in the Gulf of Oman, near where the MT Settebello was struck",
         "An oil tanker at sea; India has restricted seafarer deployment to Gulf conflict zones"],
        "oil tanker ship ocean", "An oil tanker at sea", 1)

    source_and_set(
        "india-gcc-boom-bengaluru-n-able-2-36-million-workforce-2026-20260615",
        ["Bengaluru skyline", "Bangalore city skyline", "Bengaluru IT building"],
        [["bengaluru", "bangalore", "skyline", "city"],
         ["bangalore", "bengaluru", "skyline", "building", "city"],
         ["bengaluru", "bangalore", "building", "tech", "it", "office", "tower"]],
        ["The Bengaluru skyline, India's premier technology hub and centre of its GCC boom",
         "Bengaluru, home to hundreds of global capability centres",
         "An office tower in Bengaluru, the heart of India's GCC ecosystem"],
        "bangalore city skyline india", "The Bengaluru city skyline", 2)

    source_and_set(
        "us-embassy-india-assures-more-student-visa-appointments-opening-day-rush-20260615",
        ["Embassy United States New Delhi", "US visa document passport", "university campus students"],
        [["embassy", "united states", "delhi", "consulate"],
         ["visa", "passport", "united states", "document"],
         ["university", "campus", "students", "college", "graduation"]],
        ["The US Embassy in New Delhi, which reopened student visa appointment scheduling this week",
         "A US visa; Indian students are the largest group of international students in the US",
         "International students on a university campus"],
        "university campus students graduation", "International students on a university campus", 3)
