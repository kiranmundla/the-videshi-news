#!/usr/bin/env python3
"""News writer for The Videshi — 2026-06-16 16:30 UTC run (Kotak TOP report: 1 in 5 ultra-rich Indians migrating abroad while keeping citizenship)."""

import os
import subprocess
from datetime import datetime, timezone
import requests


def curl_download(url):
    """Wikimedia rate-limits Python requests (429) but serves curl fine."""
    try:
        out = "/tmp/_videshi_hero.jpg"
        r = subprocess.run(
            ["curl", "-sS", "-A", UA, "-o", out, "-w", "%{http_code}", url],
            capture_output=True, text=True, timeout=40,
        )
        if r.stdout.strip().endswith("200") and os.path.exists(out):
            with open(out, "rb") as f:
                data = f.read()
            if len(data) > 5000:
                return data
    except Exception as e:
        print("  curl_download err", e)
    return None


def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


load_env(os.path.expanduser("~/.env.supabase"))

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

HEADERS_SB = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

UA = "TheVideshi/1.0 (thevideshi.com)"


def upload_to_supabase(img_bytes, filename):
    url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
    headers = {
        "Authorization": f"Bearer {SB_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true",
    }
    try:
        r = requests.post(url, data=img_bytes, headers=headers, timeout=30)
        if r.status_code in (200, 201):
            public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  \u2713 Uploaded to Supabase: {public_url[:70]}...")
            return public_url
        print(f"  \u274c Upload failed ({r.status_code}): {r.text[:200]}")
        return None
    except Exception as e:
        print("  upload err", e)
        return None


def validate_get(url):
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=15, stream=True, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        chunk = r.raw.read(8000)
        r.close()
        return r.status_code == 200 and "image" in ct and len(chunk) > 5000
    except Exception as e:
        print("  validate err", e)
        return False


def insert_article(article):
    r = requests.post(
        f"{SB_URL}/rest/v1/p2_articles",
        headers=HEADERS_SB, json=article, timeout=20,
    )
    if r.status_code in (200, 201):
        data = r.json()
        if isinstance(data, list) and data:
            print(f"  \u2705 Inserted: {data[0].get('headline','?')[:80]}")
            return data[0]
        print(f"  \u2705 Inserted (raw): {r.text[:120]}")
        return data
    print(f"  \u274c Insert failed ({r.status_code}): {r.text[:300]}")
    return None


def source_hero_image():
    # Dubai skyline with Burj Khalifa — the top destination for migrating wealthy Indians (Wikimedia Commons)
    src = ("https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/"
           "Burj_Khalifa_from_a_ferry%2C_Dubai.jpg/"
           "1280px-Burj_Khalifa_from_a_ferry%2C_Dubai.jpg")
    img_bytes = curl_download(src)
    if img_bytes:
        pub = upload_to_supabase(img_bytes, "dubai-skyline-burj-khalifa-uhni-migration-20260616.jpg")
        if pub and validate_get(pub):
            return pub
    if validate_get(src):
        return src
    return None


def article_uhni_migration():
    print("\n=== Article: 1 in 5 ultra-rich Indians migrating abroad ===")

    img_url = source_hero_image()
    if not img_url:
        print("  \u26a0 no valid hero image")

    slug = "one-in-five-ultra-rich-indians-migrating-abroad-keeping-citizenship-kotak-top-of-pyramid-report-20260616"

    body = """India's wealthiest citizens are not renouncing their passports. They are quietly buying a second home in Dubai, London or Lisbon — and keeping the Indian one too.

One in five of India's ultra-high-net-worth individuals is either already in the process of migrating abroad or actively planning to, according to the latest edition of Kotak Private Banking's "Top of the Pyramid" report. Crucially, almost all of them intend to keep their Indian citizenship even as they settle permanently somewhere else. They are not leaving India behind so much as adding a second base to their lives.

## What the numbers say

The report, prepared with survey results and analysis of 150 ultra-HNIs across the country, found that "1 in 5 Ultra-HNIs surveyed are currently in the process of or plan to migrate, most of whom intend to reside in their chosen host country permanently while retaining their Indian citizenship." India does not allow dual citizenship, so for most of these families the destination of choice is residency — a golden visa, a long-term permit, a green card track — rather than a new passport.

Two age groups stand out. Those between 36 and 40, at the peak of their earning years, and those above 61, thinking about succession and where to spend their later decades, are the most likely to consider relocation. Professionals are more inclined to move than entrepreneurs or those who inherited their wealth, a sign that the migration impulse is strongest among people whose income travels with them.

## A wealthier, more global elite

The backdrop is a rapidly expanding pool of Indian wealth. The number of ultra-HNIs in India is projected to reach 4.3 lakh by 2028, with combined wealth of around 359 trillion rupees. As that fortune grows, it is increasingly being parked outside the country: nearly one-third of India's ultra-rich now hold global assets, with a heavy tilt toward residential real estate abroad. For many, the overseas property is not just an investment — it is the anchor of a future residency plan.

The report describes an Indian ultra-HNI who is "embracing a global identity" and transcending borders for a mix of reasons: better infrastructure, cleaner air, world-class schooling for children, business diversification, and the simple desire for an exit option in an uncertain world. Equities reflect the same outward turn — ultra-HNIs allocate roughly a third of their portfolios to stocks, and global equities, particularly in the United States, are gaining ground against domestic holdings.

## Not a new urge, but a sharper one

The desire to live abroad is not new. India's Ministry of External Affairs has reported that more than 2.5 million Indians migrate to other countries every year, and the country already has one of the largest diasporas in the world — over 32 million non-resident Indians and persons of Indian origin spread across the globe. What is changing is who is leaving and how. The new wave at the top of the pyramid is not the student chasing a degree or the engineer chasing a job. It is the founder, the inheritor and the senior professional, moving with capital, choosing residency over citizenship, and keeping one foot firmly in India.

## Why it matters to the diaspora

For the existing diaspora, this trend reshapes the community they belong to. The Indians arriving in Dubai, Singapore, London and Lisbon over the next few years will increasingly be wealthy, investing in property, and capable of seeding businesses and philanthropy in their adopted cities. That changes the texture of NRI life — the schools, the temples, the cultural institutions and the political weight of the community all shift upmarket.

It also carries an economic message for India. A fifth of the country's richest families planning a foot abroad — while carefully keeping their citizenship — is both a vote of confidence in India's wealth-creation engine and a quiet hedge against its frustrations. The money is being made at home and increasingly stored, and lived in, abroad. For policymakers courting NRI deposits and diaspora investment, the challenge is to make sure these globally mobile families keep sending capital back, not just keeping their passports."""

    return {
        "headline": "One in Five of India's Ultra-Rich Is Moving Abroad. Almost None Are Giving Up Their Indian Passport.",
        "subheadline": "Kotak Private Banking's latest Top of the Pyramid report finds 20% of ultra-high-net-worth Indians are migrating or planning to — choosing permanent residency in Dubai, London and Lisbon while keeping their citizenship at home.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "diaspora",
        "status": "review",
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": "The Dubai skyline with the Burj Khalifa, one of the top destinations for migrating wealthy Indians.",
        "image_attribution": "Wikimedia Commons",
        "diaspora_angle": "A fifth of India's ultra-rich are settling abroad while keeping their Indian citizenship, reshaping the NRI community in cities like Dubai, London and Lisbon into a wealthier, property-owning cohort and raising the stakes for how India keeps their capital flowing home.",
        "sources": ["Kotak Private Banking 'Top of the Pyramid' Report", "The Indian Eye", "FinTech BizNews", "Ministry of External Affairs (India)"],
        "published_at": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    art = article_uhni_migration()
    wc = len(art["body"].split())
    print(f"  word count: {wc}")
    if wc < 400:
        print("  \u274c word count below floor, aborting")
    elif not art["image_url"]:
        print("  \u274c no hero image, aborting")
    else:
        insert_article(art)
