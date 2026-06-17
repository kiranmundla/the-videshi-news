#!/usr/bin/env python3
"""News writer for The Videshi — 2026-06-17 06:30 UTC run.

Story: Modi and Carney met on the sidelines of the G7 Summit in Evian, France
on June 16, their fourth meeting in under a year, and agreed to conclude an
India-Canada CEPA in 2026, launch GSOIA security-information talks, deepen
energy/AI/talent-mobility cooperation, and announce "Raisina Americas." Carney
invited Modi to visit Canada in 2026. Major reset for the ~2.8M-strong Indian
diaspora in Canada after the 2023 Nijjar rupture. (MEA readout, Reuters,
LiveMint, ANI — Jun 16, 2026)
"""

import os
import subprocess
from datetime import datetime, timezone
import requests

UA = "TheVideshi/1.0 (thevideshi.com)"


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
    # On-topic Commons photo of the actual Modi-Carney bilateral at the
    # Evian G7 (Prime Minister's Office, India; GODL-India license).
    src = ("https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/"
           "Prime_Minister_of_Bharat%2C_Shri_Narendra_Damodardas_Modi_meets_"
           "the_Prime_Minister_of_Canada%2C_Mr._Mark_Carney.jpg/"
           "1280px-Prime_Minister_of_Bharat%2C_Shri_Narendra_Damodardas_Modi_meets_"
           "the_Prime_Minister_of_Canada%2C_Mr._Mark_Carney.jpg")
    img_bytes = curl_download(src)
    if img_bytes:
        pub = upload_to_supabase(img_bytes, "modi-carney-g7-evian-bilateral-20260617.jpg")
        if pub and validate_get(pub):
            return pub
    if validate_get(src):
        return src
    return None


def article_modi_carney():
    print("\n=== Article: Modi-Carney G7 reset ===")

    img_url = source_hero_image()
    if not img_url:
        print("  \u26a0 no valid hero image")

    slug = "modi-carney-g7-evian-india-canada-cepa-2026-diaspora-reset-20260617"

    body = """Less than three years ago, India and Canada were expelling each other's diplomats and freezing trade talks. On Tuesday, on the sidelines of the G7 Summit in Evian, France, their prime ministers sat down for the fourth time in under a year and agreed to finish a free-trade deal before the year is out. It is one of the fastest diplomatic turnarounds in recent memory between two democracies, and for the nearly 2.8 million people of Indian origin in Canada, it touches almost every part of daily life.

Prime Minister Narendra Modi and Canadian Prime Minister Mark Carney committed to concluding negotiations on a Comprehensive Economic Partnership Agreement (CEPA) in 2026, according to readouts from both governments. "It was a delight to meet Prime Minister Carney on the sidelines of the Evian G7 Summit," Modi wrote on X afterwards. "In less than a year, it is our fourth meeting, indicating our commitment to strong India-Canada ties." Carney, for his part, described India as the world's fastest-growing major economy and "a global technology and commerce powerhouse," saying both countries were moving quickly to unlock new partnerships in energy, talent and artificial intelligence.

## How far the relationship had fallen

The thaw is striking precisely because of how cold things had become. In September 2023, then-prime minister Justin Trudeau publicly alleged that Indian government agents were involved in the killing of Hardeep Singh Nijjar, a Canadian citizen and Khalistani separatist, in British Columbia. New Delhi rejected the accusation as "politically motivated" and "absurd." Both sides expelled diplomats, India briefly suspended visa services for Canadians, and trade negotiations that had been close to a deal collapsed. Relations sank to their lowest point in decades.

Carney's election last year reset the tone. A former central banker who ran the Bank of England and the Bank of Canada, he named India a priority partner during his campaign and made restoring the relationship an early goal. Tuesday's meeting built on his March visit to India and a series of leader-level contacts since.

## What the two leaders actually agreed

Beyond the headline trade target, the readouts list a dense agenda. The leaders agreed to launch negotiations on a General Security of Information Agreement (GSOIA), a foundational pact that allows two countries to share classified defence and intelligence material. They reviewed commercial arrangements in liquefied natural gas, liquefied petroleum gas and metallurgical coal, areas where energy-rich Canada and energy-hungry India are natural partners. They welcomed recent meetings of the Joint Science and Technology Committee and the Consular Dialogue, and looked ahead to fresh talks on defence, finance and migration.

The two governments also announced "Raisina Americas," a new platform for dialogue and exchanges, and India backed Canada's bid to become a Dialogue Partner of the Indian Ocean Rim Association. Crucially, Carney invited Modi to visit Canada in 2026 — an invitation Modi accepted in principle, with both sides agreeing to work out a date through diplomatic channels. A prime ministerial visit would be the clearest signal yet that the rupture is behind them.

## Why the diaspora is watching closely

Few foreign-policy stories land as directly on Indian-Canadian kitchen tables as this one. Canada is home to roughly 2.8 million people of Indian origin and, before the freeze, more than 400,000 Indian students — a population that powers Canadian campuses, the tech corridors of Toronto and Vancouver, and a remittance pipeline back to India. The 2023 standoff threw visa processing, study-permit timelines and family travel into uncertainty almost overnight.

A revived relationship promises the opposite: smoother consular services, a migration dialogue aimed at predictable rules for students and skilled workers, and the prospect of a CEPA that could lower costs for businesses run by the diaspora on both sides. The Canada-India Talent and Innovation Strategy, which the leaders reaffirmed, is explicitly about skill development and educational ties — the lifeblood of the student community.

Two sensitive issues still hang over the warmth. New Delhi continues to press Ottawa for tougher action against Khalistani extremist activity on Canadian soil, and the underlying questions raised by the Nijjar case have not vanished. But for a community whose lives straddle both countries, the direction of travel — toward a signed trade deal, a leaders' visit and normalised services — is the news that matters most this week."""

    return {
        "headline": "India and Canada Just Set a 2026 Deadline to Sign a Trade Deal. Three Years Ago They Were Expelling Diplomats.",
        "subheadline": "Modi and Carney met for the fourth time in under a year at the Evian G7, committing to finish a CEPA in 2026, open defence-intelligence talks and a prime ministerial visit \u2014 a reset that lands directly on Canada's 2.8-million-strong Indian diaspora.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "diaspora",
        "status": "review",
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": "Prime Minister Narendra Modi meets Canadian Prime Minister Mark Carney on the sidelines of the G7 Summit in Evian, France, on June 16, 2026.",
        "image_attribution": "Prime Minister's Office (India), GODL-India, via Wikimedia Commons",
        "diaspora_angle": "Canada is home to nearly 2.8 million people of Indian origin and hundreds of thousands of Indian students; the Modi-Carney reset promises a CEPA, a migration dialogue and normalised consular services that directly affect their visas, studies, businesses and family travel after the 2023 diplomatic freeze.",
        "sources": [
            "Ministry of External Affairs / PMO India \u2014 PM meets Prime Minister Mark Carney of Canada on the sidelines of the G7 Summit (June 16, 2026)",
            "Reuters \u2014 Canada cites progress with India after Carney-Modi meeting (June 16, 2026)",
            "LiveMint \u2014 India, Canada push to conclude trade pact this year, deepen strategic ties (June 16, 2026)",
            "ANI / NewKerala \u2014 Modi, Carney Review Energy Ties at G7 Summit (June 16, 2026)",
        ],
        "published_at": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    art = article_modi_carney()
    wc = len(art["body"].split())
    print(f"  word count: {wc}")
    if wc < 400:
        print("  \u274c word count below floor, aborting")
    elif not art["image_url"]:
        print("  \u274c no hero image, aborting")
    else:
        insert_article(art)
