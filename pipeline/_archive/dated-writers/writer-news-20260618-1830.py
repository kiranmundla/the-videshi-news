#!/usr/bin/env python3
"""News writer for The Videshi — 2026-06-18 18:30 UTC run.

Story: India is the exclusive AI Country Partner at VivaTech 2026 in Paris
(June 17-20), with its largest-ever national pavilion featuring 30 deep-tech
startups selected from the Bharat Innovates 2026 cohort. PM Modi attended on
Thursday June 18 alongside Macron; Commerce Minister Piyush Goyal inaugurated
the India Pavilion on Wednesday. The 30 startups were narrowed from 120 (and
ultimately ~3,000 applications) and span AI, EV powertrains, fashion-tech,
digital learning, manufacturing safety and more. Backed by the IndiaAI
Startups Global Acceleration Program and HEC Paris / Station F, this anchors
the India-France Year of Innovation 2026.

Distinct from prior coverage: existing Paris articles cover Modi's diaspora
welcome ("Modi thanks the diaspora first") and the broader G7/France-bridge
geopolitics. THIS story is the tech/startup substance — India as AI Country
Partner, the 30-startup pavilion, the deep-tech funding picture — framed for
the diaspora's tech professionals, founders and investors.

Diaspora angle: Indian-origin technologists, founders and VCs across the US,
UK and Europe are the natural bridge for these 30 startups seeking global
customers and capital; VivaTech is where that diaspora network turns into
deal flow.

Sources: DD India, IANS/newkerala, The Indian Awaaz, Energetica India,
HEC Paris, YourStory.
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


def curl_download(url, out="/tmp/_videshi_hero_news1830.jpg"):
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
        "apikey": SB_KEY,
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
    # Wikimedia Commons: the VivaTech 2025 show floor in Paris — the exact
    # event venue, a year prior, for a story about the India Pavilion there.
    src = ("https://upload.wikimedia.org/wikipedia/commons/a/aa/"
           "Paris_-_Salon_VivaTech_2025_-_1.jpg")
    img_bytes = curl_download(src)
    if img_bytes:
        pub = upload_to_supabase(img_bytes, "vivatech-2026-india-pavilion-startups-20260618.jpg")
        if pub and validate_get(pub):
            return pub
    if validate_get(src):
        return src
    return None


def article():
    print("\n=== Article: India as AI Country Partner at VivaTech 2026 ===")

    img_url = source_hero_image()
    if not img_url:
        print("  \u26a0 no valid hero image")

    slug = "india-ai-country-partner-vivatech-2026-paris-30-deeptech-startups-diaspora-20260618"

    body = """When the doors of VivaTech opened in Paris this week, the largest national pavilion on the floor did not belong to the host country, or to Germany, the event's official country of honour. It belonged to India \u2014 named the exclusive AI Country Partner of Europe's biggest technology fair for its tenth-anniversary edition, running June 17 to 20.

Prime Minister Narendra Modi walked the pavilion on Thursday alongside French President Emmanuel Macron, the final stop on a European tour that took him from the G7 summit in \u00c9vian to the heart of the continent's startup scene. A day earlier, Commerce and Industry Minister Piyush Goyal had inaugurated the India Pavilion, calling it "a testament to Bharat's growing stature as a global innovation hub."

## Thirty startups, three thousand applications

The centrepiece is a cohort of 30 Indian startups \u2014 the largest contingent the country has ever sent to VivaTech. They were not picked at random. The 30 were narrowed from 120 finalists under Bharat Innovates 2026, the Ministry of Education's flagship innovation programme, which itself sifted through more than 3,000 applications across 13 thematic areas.

The result is a deliberately broad shop window. There is Tsuyo Manufacturing, building indigenous electric-vehicle powertrains as the global mobility industry shifts to electrification. There is Daten & Wissen, whose computer-vision systems turn factory and construction-site cameras into real-time safety and operational monitors. Others are working on visual trend intelligence for fashion and beauty, job-simulation platforms to ready workers for an AI economy, and multilingual voice AI built for India's dozens of languages.

"As the global mobility industry undergoes a transformative shift towards electrification, platforms like VivaTech offer invaluable opportunities to showcase India's deep-tech capabilities," said Vijay Kumar, founder of Tsuyo Manufacturing, one of the selected 30.

## A bilateral bet dressed up as a trade fair

The pavilion is the visible tip of something more structured. India's presence anchors the India-France Year of Innovation 2026, a framework Modi and Macron announced earlier this year, and several of the startups arrived through the IndiaAI Startups Global Acceleration Program, run in partnership with the HEC Paris incubator at Station F, the sprawling Paris startup campus.

"India offers key advantages for the AI era," Goyal told the gathering, ticking off a young population, a deep pool of STEM graduates, robust public digital infrastructure and democratic governance. France, for its part, gets early access to a fast-growing market and a partner in its own push for "sovereign" AI that does not depend entirely on American cloud giants.

## The numbers behind the moment

India's deep-tech base has been maturing fast. The country now hosts more than 4,200 deep-tech startups, including over 550 founded in 2025 alone, according to the Nasscom-Zinnov India Tech Startup Report. Deep-tech funding rose 37% last year to $2.3 billion, with artificial intelligence accounting for roughly 91% of the capital deployed.

New Delhi has been pouring public money into the gap. In July 2025 the Union Cabinet approved a \u20b91 lakh crore (roughly $12 billion) Research, Development and Innovation Fund aimed squarely at private-sector R&D, including equity stakes in startups. The aim is to push more capital toward the hard, slow, capital-hungry work of building chips, batteries, drones and quantum systems \u2014 the kind of technology that is difficult to copy and, when it works, far more defensible than another consumer app.

## Why the diaspora should be watching

For Indians abroad, this is not a distant photo-op. The 30 founders in Paris are hunting for exactly what the diaspora is unusually well placed to supply: global customers, design partners and capital. Indian-origin technologists run engineering teams across Silicon Valley, London and continental Europe; Indian-origin partners sit in venture funds on both sides of the Atlantic. VivaTech is where that network can turn into purchase orders and term sheets.

It also reframes a familiar diaspora debate. For years the story of Indian tech talent abroad was one of brain drain \u2014 the best engineers leaving and not coming back. A pavilion full of founders building frontier technology in India, courted by a G7 host nation, points to a more two-way traffic: capital, ideas and customers flowing back toward home-grown companies, with the diaspora as the conduit rather than the destination.

The hard part comes after the fair closes on Saturday. Pavilions generate headlines; deep tech needs years of patient capital and real customers to survive. But for a country that spent a decade being known abroad mainly for its software services, standing as the AI partner of Europe's flagship tech event \u2014 with the biggest pavilion in the hall \u2014 is a marker of how far the ambition has travelled."""

    return {
        "headline": "India Just Brought the Biggest Pavilion to Europe's Top Tech Fair \u2014 and 30 Startups to Prove the Point",
        "subheadline": "Named the exclusive AI Country Partner at VivaTech 2026 in Paris, India sent its largest-ever delegation: 30 deep-tech startups picked from 3,000. For the diaspora's founders and investors, it is a network waiting to be used.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "tech",
        "status": "review",
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": "The VivaTech show floor in Paris, where India set up its largest-ever national pavilion as the 2026 AI Country Partner.",
        "image_attribution": "Wikimedia Commons",
        "diaspora_angle": "The 30 Indian startups in Paris are hunting for global customers and capital \u2014 exactly what Indian-origin technologists, founders and VCs across the US, UK and Europe are best placed to supply, making the diaspora the natural conduit for India's deep-tech push abroad.",
        "sources": [
            "DD India \u2014 India emerges as a global startup hub at VivaTech 2026 (June 2026)",
            "IANS / newkerala \u2014 India showcasing startup strength, digital growth and AI leadership at Viva Tech 2026: Piyush Goyal (June 17, 2026)",
            "The Indian Awaaz \u2014 VivaTech 2026: India, France Reaffirm Strategic Ties in AI & Digital Infrastructure (June 17, 2026)",
            "Energetica India \u2014 Tsuyo Manufacturing Selected Among Top 30 Indian Startups for VivaTech 2026 in Paris (June 17, 2026)",
            "HEC Paris \u2014 IndiaAI Startups Global: Demo Day with Incubateur HEC Paris at Station F",
            "YourStory \u2014 India to showcase 120 deep-tech startups in Nice: inside the Bharat Innovates 2026 cohort (2026)",
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
