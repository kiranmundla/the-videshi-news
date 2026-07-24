#!/usr/bin/env python3
"""News writer for The Videshi — 2026-06-18 14:30 UTC run.

Story: At the G7 summit in Évian, UK PM Keir Starmer announced £1.3bn
($1.74bn) in clean-energy/AI investment from French and Indian companies,
creating 1,400+ jobs in Manchester, Leeds and Birmingham. Indian share:
Atri Energy Transition (£300m, grid-scale battery storage + advanced
manufacturing) and Hexaware Technologies (£25m, UK expansion). InfraVia
(France) provided £1bn. Distinct from already-published Modi-Paris,
Fed, and EU-India FTA stories.

Diaspora angle: Indian firms now exporting capital and creating jobs in
British cities with some of the UK's largest Indian-origin populations —
the diaspora as a node in a capital flow, not just a labour flow.

Sources: Reuters, Morningstar/PA, AInvest, Hillingdon Times.
"""

import os
import subprocess
from datetime import datetime, timezone
import requests

UA = "TheVideshi/1.0 (thevideshi.com)"


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


def curl_download(url, out="/tmp/_videshi_hero_news1430.jpg"):
    try:
        r = subprocess.run(
            ["curl", "-sS", "-A", UA, "-o", out, "-w", "%{http_code}", url],
            capture_output=True, text=True, timeout=60,
        )
        if r.stdout.strip().endswith("200") and os.path.exists(out):
            with open(out, "rb") as f:
                data = f.read()
            if len(data) > 5000:
                return data
    except Exception as e:
        print("  curl_download err", e)
    return None


def upload_to_supabase(img_bytes, filename):
    url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
    headers = {
        "Authorization": f"Bearer {SB_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true",
    }
    try:
        r = requests.post(url, data=img_bytes, headers=headers, timeout=40)
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
        r = requests.get(url, headers={"User-Agent": UA}, timeout=20, stream=True, allow_redirects=True)
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
        headers=HEADERS_SB, json=article, timeout=25,
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
    # Wikimedia Commons: UK grid-scale battery storage facility (Hunterston),
    # topically exact for an article about Indian investment in UK battery storage.
    src = ("https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/"
           "Hunterston_Battery_Storage_Facility_-_geograph.org.uk_-_8311501.jpg/"
           "1280px-Hunterston_Battery_Storage_Facility_-_geograph.org.uk_-_8311501.jpg")
    img_bytes = curl_download(src)
    if img_bytes:
        pub = upload_to_supabase(img_bytes, "uk-grid-battery-storage-g7-india-20260618.jpg")
        if pub and validate_get(pub):
            return pub
    if validate_get(src):
        return src
    return None


def article():
    print("\n=== Article: Indian firms fund UK clean energy at G7 ===")

    img_url = source_hero_image()
    if not img_url:
        print("  \u26a0 no valid hero image")

    slug = "indian-firms-uk-clean-energy-investment-g7-jobs-atri-hexaware-20260618"

    body = """When Keir Starmer stepped up at the G7 summit in \u00c9vian this week to announce £1.3 billion in fresh investment for Britain, the headline number belonged as much to New Delhi as to Paris. Of the package the UK prime minister unveiled \u2014 clean-energy and artificial-intelligence projects expected to create more than 1,400 jobs in Manchester, Leeds and Birmingham \u2014 a substantial slice is Indian money, flowing into British cities that are home to some of the country's largest Indian-origin communities.

Two Indian companies anchor the Indian contribution. Atri Energy Transition, a clean-energy investor, will put more than £300 million into large-scale battery storage and advanced manufacturing in the UK. Hexaware Technologies, the Mumbai-listed IT services firm, will invest a further £25 million to expand its British operations. The remaining £1 billion comes from the French private-equity house InfraVia Capital Partners, which is backing battery storage and a "flexible energy platform" designed to be switched on when wind and solar output dips.

## The diaspora as a capital exporter

For decades, the story of Indians and Britain has been told mostly in one direction: people moving from the subcontinent to the UK to study, to work, to settle. The G7 announcement is a marker of how thoroughly that script has been rewritten. India is now among the largest sources of inward investment into the United Kingdom, and the jobs these projects create will land disproportionately in the Midlands and the North \u2014 in Leicester, Birmingham and Greater Manchester, cities whose economies and high streets have been shaped by generations of Indian migrants.

That matters to the diaspora in a way a dry investment figure rarely captures. When an Indian firm builds a battery plant in Birmingham, it is not only New Delhi's balance sheet at work; it is also the creation of skilled, well-paid roles in communities where British Indians are heavily represented. The capital flow and the labour flow, once separate stories, are increasingly the same one.

## Why batteries, and why now

The investments are squarely aimed at the weak point of every advanced economy's energy transition: storage. Wind and solar are cheap to generate but maddening to schedule, producing too much power on blustery afternoons and too little on still winter evenings. Grid-scale batteries soak up the surplus and release it on demand, smoothing the gap. Atri's pledge to fund "large-scale battery storage and advanced manufacturing" plugs directly into a British target of attracting more than £30 billion a year in clean-energy investment by 2035.

Starmer framed the deals as insulation against a turbulent world. "The world is more dangerous than it has been for a generation, with conflict abroad washing up on our shores," he said in \u00c9vian, citing the energy-price shocks rippling out of the Middle East. "These investments will create thousands of high-skilled jobs, back British innovation and strengthen our energy system so families are better protected from global shocks."

## A widening India-UK economic lattice

The timing is not incidental. The announcement lands just weeks before the India-UK free trade agreement is due to switch on in mid-July, a pact that will cut tariffs across goods and services and ease the movement of professionals between the two countries. Layered on top of that trade architecture, the G7 investments suggest a relationship deepening on multiple fronts at once \u2014 trade rules, capital, and the clean-energy supply chain all moving in the same direction.

For Hexaware, the £25 million is an incremental expansion of an existing British footprint in IT services, the sector where Indian firms have long been fixtures of the UK corporate landscape. For Atri, the £300 million is a bolder bet on Britain as a place to manufacture and store energy, not just to write code. Together they signal that Indian capital increasingly sees the UK not merely as a market to sell into, but as a place to build.

## What NRIs should watch

For Indians in Britain, the practical upside is jobs and local investment in the regions where the community is concentrated. For the wider diaspora and for investors back home, the deals are a useful tell about where Indian corporate ambition is heading: outward, into Western infrastructure and clean tech, and increasingly into the physical economy rather than purely services. As the India-UK trade deal comes into force and bilateral ties thicken, expect more announcements like this one \u2014 and more of the diaspora's home country showing up not as a source of workers, but as a source of capital."""

    return {
        "headline": "Indian Firms Just Put Hundreds of Millions Into Britain at the G7. The Jobs Land Where the Diaspora Lives.",
        "subheadline": "At the G7 summit, Keir Starmer unveiled £1.3 billion in clean-energy and AI investment \u2014 with Atri Energy Transition and Hexaware bringing Indian capital into Manchester, Leeds and Birmingham, flipping the old migration script.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "economy",
        "status": "review",
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": "A grid-scale battery energy storage facility in the UK, the kind of infrastructure Indian investment will help expand.",
        "image_attribution": "Wikimedia Commons",
        "diaspora_angle": "Indian companies are now exporting capital into British cities with large Indian-origin populations, creating skilled jobs in Manchester, Leeds and Birmingham \u2014 a sign the diaspora's home country is becoming a source of investment, not just migrants, just weeks before the India-UK trade deal takes effect.",
        "sources": [
            "Reuters \u2014 UK secures $1.7 billion in investments from Indian, French companies at G7 (June 16, 2026)",
            "Morningstar / PA \u2014 UK PM Starmer unveils GBP1 billion French and Indian investments at G7 (June 16, 2026)",
            "AInvest \u2014 UK Attracts £1.3 Billion Investment in Clean Energy and AI Projects from French and Indian Firms (June 16, 2026)",
            "Hillingdon Times \u2014 Starmer unveils £1 billion French and Indian investments at G7 (June 2026)",
        ],
        "published_at": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    art = article()
    wc = len(art["body"].split())
    print(f"  word count: {wc}")
    hl = len(art["headline"])
    print(f"  headline chars: {hl}")
    if wc < 400:
        print("  \u274c word count below floor, aborting")
    elif not art["image_url"]:
        print("  \u274c no hero image, aborting")
    elif len(art["headline"]) > 200:
        print("  \u274c headline too long, aborting")
    else:
        insert_article(art)
