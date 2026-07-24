#!/usr/bin/env python3
"""News writer for The Videshi — 2026-06-16 22:30 UTC run.

Story: India's government rice stocks hit a record 68.43M tonnes and wheat a
five-year peak of 53.41M tonnes as of June 1, giving the world's biggest rice
exporter a grain buffer against the El Nino monsoon — the reassuring
counter-narrative to weeks of monsoon/inflation doom coverage. (Reuters, Jun 16)
"""

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
    # CWC Godown operated by the Food Corporation of India for stocking
    # foodgrains — directly on-topic government grain storage (Wikimedia, CC BY-SA 4.0)
    src = ("https://upload.wikimedia.org/wikipedia/commons/thumb/1/16/"
           "CWC_Godown%2C_Bamanheri_operated_by_Food_Corporation_of_India_for_stocking_foodgrains.jpg/"
           "1280px-CWC_Godown%2C_Bamanheri_operated_by_Food_Corporation_of_India_for_stocking_foodgrains.jpg")
    img_bytes = curl_download(src)
    if img_bytes:
        pub = upload_to_supabase(img_bytes, "fci-grain-godown-record-rice-wheat-stocks-20260616.jpg")
        if pub and validate_get(pub):
            return pub
    if validate_get(src):
        return src
    return None


def article_grain_stocks():
    print("\n=== Article: India record rice/wheat stocks vs El Nino ===")

    img_url = source_hero_image()
    if not img_url:
        print("  \u26a0 no valid hero image")

    slug = "india-record-rice-stocks-wheat-five-year-peak-el-nino-grain-buffer-20260616"

    body = """For weeks the headlines out of India have been about a faltering monsoon, a strengthening El Nino and rising food prices. This week brought the other side of the ledger — and it is unusually reassuring. India is sitting on the largest cushion of grain it has ever held going into summer.

Government warehouses held a record 68.43 million metric tonnes of rice, including unmilled paddy, as of June 1, official data released on Tuesday showed. That is up 15 per cent from a year ago and roughly five times the government's own target of 13.5 million tonnes for July 1. Wheat stocks stood at 53.41 million tonnes, the highest since 2021 and nearly double the 27.6-million-tonne target, lifted by a surprisingly large procurement drive that swept up about 35 million tonnes from farmers this season.

## A buffer built for exactly this moment

The timing matters. India's meteorological department is forecasting the weakest monsoon since 2015, with rains already delayed and central and northern regions running dry, as an El Nino weather pattern reshapes weather across the world. In years past, that combination would have stoked fears of shortages, panic procurement and a fresh round of export bans.

This year the math looks different. "Rice stocks are more than adequate. That should give the government the confidence to continue exports despite forecasts of below-normal rainfall, which could affect production," a New Delhi-based dealer at a global trading firm told Reuters. A Mumbai-based dealer put it more bluntly: with 35 million tonnes of wheat in hand, the government "is now in a comfortable position and can release stocks aggressively into the market to keep prices in check."

The cushion was filled by two consecutive record harvests. Rice and wheat production hit all-time highs in the 2025/26 crop year — 154.02 million tonnes of rice and 120.66 million tonnes of wheat — after ample rainfall last year encouraged farmers to expand the area they planted.

## Why a record stockpile travels overseas

India accounts for around 40 per cent of the world's rice exports, and it scrapped the last of its export curbs on the grain in March 2025. A record domestic buffer is what makes continued shipments possible even in a drought year, and the US Department of Agriculture now forecasts Indian rice exports could reach a record 25 million tonnes in the current marketing year.

That is the line that connects a godown in Uttar Pradesh to a grocery aisle in New Jersey. When India holds enough rice to keep exporting through a weak monsoon, the basmati and sona masoori on diaspora shelves in the United States, Britain, Canada and the Gulf stay both available and relatively stable in price. The last time India clamped down on rice exports, in 2023, NRI shoppers saw bags vanish and prices spike within days, and viral videos of long queues outside Indian grocery stores in the US captured the anxiety. A record buffer is the best insurance against a repeat.

## Comfort now, caution later

None of this makes India immune to El Nino. The Food and Agriculture Organization has warned that the pattern could weaken the summer monsoon and stress rainfed crops such as rice and maize during the critical kharif sowing season; during the 2015-16 El Nino, India's rice output fell about one per cent and maize four per cent. Economists note, too, that the most weather-sensitive items — pulses, oilseeds, fruit and vegetables — are not the ones sitting in government godowns, so a bad monsoon can still push up the price of a tomato or a bag of dal even while the rice mountain stands tall.

But the structural picture has shifted. More than half of India's cropped area is now irrigated, up from 40 per cent in 2010-11, and reservoir levels this year are running above the decadal average — both of which blunt the link between a single weak monsoon and a food crisis. For a diaspora that watches India's weather with one eye on its own kitchen budget, this week's data is a rare piece of good news in a worrying season: the granary is full, the export taps are open, and the cushion is the biggest it has ever been."""

    return {
        "headline": "India Is Heading Into a Weak Monsoon With Its Biggest Grain Cushion Ever. That's Good News on the Diaspora Grocery Shelf.",
        "subheadline": "Government rice stocks hit a record 68.43 million tonnes and wheat a five-year peak as El Nino threatens the monsoon. The buffer lets the world's biggest rice exporter keep shipping — and keep NRI grocery prices stable.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "diaspora",
        "status": "review",
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": "A Central Warehousing Corporation godown at Bamanheri, operated by the Food Corporation of India for stocking foodgrains.",
        "image_attribution": "Prabhat1729, CC BY-SA 4.0, via Wikimedia Commons",
        "diaspora_angle": "India's record grain buffer means the world's biggest rice exporter can keep shipping through a weak El Nino monsoon — protecting basmati and sona masoori supply and prices on diaspora grocery shelves in the US, UK, Canada and the Gulf, and guarding against a repeat of the 2023 export-ban panic.",
        "sources": [
            "Reuters — India's rice stocks climb to record high; wheat inventories at five-year peak (June 16, 2026)",
            "Reuters — India File: Searing El Nino tests crop buffers (June 16, 2026)",
            "USDA Foreign Agricultural Service — India Grain and Feed Annual (April 2026)",
            "The Hindu Business Line — El Nino may hit India's monsoon, rice and maize output: FAO",
        ],
        "published_at": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    art = article_grain_stocks()
    wc = len(art["body"].split())
    print(f"  word count: {wc}")
    if wc < 400:
        print("  \u274c word count below floor, aborting")
    elif not art["image_url"]:
        print("  \u274c no hero image, aborting")
    else:
        insert_article(art)
