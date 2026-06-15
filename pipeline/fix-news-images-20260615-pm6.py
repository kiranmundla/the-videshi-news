#!/usr/bin/env python3
"""Upgrade 2 PM6 news article images from generic Pexels to real Wikimedia Commons
photos of the actual subject (South Block/MEA, BSE building). curl download ->
Supabase storage upload -> patch. Wikimedia 429s Python requests; curl works."""
import os, subprocess, requests
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
SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
BUCKET = "article-images"
UA = "TheVideshi/1.0 (thevideshi.com)"
H = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}

def download(url, dest):
    subprocess.run(["curl", "-sS", "-L", "-A", UA, "-o", dest, url],
                   capture_output=True, text=True, timeout=60)
    if not os.path.exists(dest):
        return False
    sz = os.path.getsize(dest)
    ft = subprocess.run(["file", "-b", "--mime-type", dest], capture_output=True, text=True).stdout.strip()
    ok = sz > 5000 and ft.startswith("image/")
    print(f"    dl {sz}b {ft} -> {'OK' if ok else 'reject'}")
    return ok

def upload(local, remote):
    with open(local, "rb") as f:
        data = f.read()
    ct = "image/png" if local.lower().endswith(".png") else "image/jpeg"
    url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET}/{remote}"
    r = requests.post(url, headers={**H, "Content-Type": ct, "x-upsert": "true"}, data=data, timeout=90)
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

JOBS = [
    {
        "slug": "mea-repatriation-927000-indians-home-west-asia-multi-nation-transit-routes-20260615",
        "src": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/84/North_%26_South_Block%2C_New_Delhi_%2829473956940%29.jpg/1280px-North_%26_South_Block%2C_New_Delhi_%2829473956940%29.jpg",
        "remote": "north-south-block-new-delhi-mea-20260615.jpg",
        "caption": "North and South Block in New Delhi, where India's Ministry of External Affairs coordinates the West Asia repatriation effort",
        "attribution": "Wikimedia Commons",
    },
    {
        "slug": "indian-markets-rally-gulf-peace-rbi-nri-deposit-rate-hike-rupee-stabilise-20260615",
        "src": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/BSE_-_Bombay_Stock_Exchange_Building.jpg/1280px-BSE_-_Bombay_Stock_Exchange_Building.jpg",
        "remote": "bombay-stock-exchange-building-20260615.jpg",
        "caption": "The Bombay Stock Exchange building in Mumbai, where the Sensex rallied on news of the Gulf peace deal",
        "attribution": "Wikimedia Commons",
    },
]

for j in JOBS:
    print(f"\n=== {j['slug']} ===")
    dest = f"/tmp/{j['remote']}"
    if download(j["src"], dest):
        pub = upload(dest, j["remote"])
        if pub:
            patch(j["slug"], pub, j["caption"], j["attribution"])
        else:
            print("  upload failed, keeping existing image")
    else:
        print("  download failed, keeping existing image")
