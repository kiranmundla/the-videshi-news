#!/usr/bin/env python3
"""News writer for The Videshi — 2026-06-16 14:30 UTC run (Modi's historic first-ever Slovakia visit + diaspora)."""

import os
from datetime import datetime, timezone
import requests


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
    # Official PIB photo of Modi & Fico at Bratislava Castle (Wikimedia Commons, GODL-India)
    src = ("https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/"
           "Prime_Minister_of_Bharat%2C_Shri_Narendra_Damodardas_Modi_with_the_Prime_Minister_of_Slovakia%2C_Mr._Robert_Fico_at_the_Bratislava_Castle.jpg/"
           "1280px-Prime_Minister_of_Bharat%2C_Shri_Narendra_Damodardas_Modi_with_the_Prime_Minister_of_Slovakia%2C_Mr._Robert_Fico_at_the_Bratislava_Castle.jpg")
    try:
        r = requests.get(src, headers={"User-Agent": UA}, timeout=30)
        if r.status_code == 200 and len(r.content) > 5000:
            pub = upload_to_supabase(r.content, "modi-fico-bratislava-castle-20260616.jpg")
            if pub and validate_get(pub):
                return pub
    except Exception as e:
        print("  hero err", e)
    if validate_get(src):
        return src
    return None


def article_modi_slovakia():
    print("\n=== Article: Modi's historic Slovakia visit ===")

    img_url = source_hero_image()
    if not img_url:
        print("  \u26a0 no valid hero image")

    slug = "modi-first-indian-pm-slovakia-visit-fico-comprehensive-partnership-diaspora-bratislava-20260616"

    body = """No Indian prime minister had ever set foot in Slovakia. On the night of June 14, that changed — and the people waiting up to mark the moment were not Slovak officials. They were Indians.

When Narendra Modi landed in Bratislava at 2:18 a.m., a crowd of the city's Indian residents had gathered at the airport and outside his hotel, chanting "Modi, Modi" and "Bharat Mata Ki Jai" into the early-morning cold. For a community that numbers only a few thousand in a country of 5.4 million, the first-ever visit by an Indian head of government was less a diplomatic footnote than a validation — proof that the place they had quietly built lives in over the past decade now registered back home.

## A first since 1993

Modi's two-day state visit, from June 14 to 16, marked the first time an Indian prime minister has travelled to Slovakia since the country gained independence in 1993. It came at the invitation of Slovak Prime Minister Robert Fico and built on a warming of ties that has accelerated over the past year: President Droupadi Murmu visited Bratislava in April 2025, and Slovak President Peter Pellegrini travelled to India for the AI Impact Summit in February 2026.

Slovakia is the second leg of a six-day European tour that began in France on June 13 and ends with Modi attending the G7 Summit in Evian on June 17, where he is expected to meet US President Donald Trump. But the Slovakia stop carried a symbolic weight the others did not, simply because no Indian leader had ever made it.

## What was signed

The substance matched the symbolism. After talks at Bratislava Castle, India and Slovakia upgraded their relationship to a Comprehensive Partnership, and the two sides signed agreements spanning defence and trade. Fico congratulated Modi on becoming India's longest-serving elected prime minister, calling the milestone a "political miracle," and Modi reciprocated by inviting the Slovak leader to visit India.

The economic logic is straightforward. Slovakia is one of the most industrialised economies in Central Europe — its automobile sector, per capita, is among the largest in the world — and Indian workers and engineers have become a visible part of that workforce. India's ambassador to Slovakia, Apoorva Srivastava, framed the visit as one that would strengthen not just political relations but economic security and people-to-people contacts.

## The welcome that mattered

The official choreography leaned heavily on culture. Modi was received in the Slovak tradition of bread and salt, a gesture of hospitality and goodwill that he accepted with folded hands. Folk performers from the Lucnica Ensemble sang "Vande Mataram," a moment Modi shared on X. He and President Pellegrini attended a yoga session at the Presidential Palace, and the two prime ministers paid tribute at a memorial to fallen soldiers.

But it was the diaspora reception that drew the most emotion. At the Grand Hotel River Park, where Modi stayed, community members described the encounter in personal terms. "Eyes filled with emotion, heart filled with pride," said Rajendra Prasad, who said he was able to shake the prime minister's hand. An Indian-origin restaurant in Bratislava, run by a chef who has lived in Slovakia for a decade, prepared meals for the visiting delegation.

The next morning, Modi posted his thanks. "Yesterday evening's welcome in Bratislava was truly special," he wrote. "I am grateful to the Indian community for their warmth and affection. Such gestures reflect the enduring bonds that connect our people and strengthen the India-Slovakia friendship."

## Why it matters to the diaspora

For the broader Indian diaspora, the Slovakia visit is a reminder that the map of where Indians live and work is being redrawn. The traditional anchors — the US, the UK, Canada, the Gulf — still dominate, but a steady stream of skilled workers has been moving into Central and Eastern Europe, drawn by manufacturing jobs, easier work pathways, and labour shortages that Western Europe cannot fill on its own. One community member told reporters that the local Indian population, around 6,000 at the time of President Murmu's visit, is expected to grow sharply now that the prime minister has come.

That growth is the real story beneath the bread-and-salt ceremony. A first-ever prime ministerial visit signals to Indian students and professionals that a smaller, less obvious destination is now on New Delhi's radar — and that the consular support, trade frameworks, and bilateral attention that make a country liveable for migrants are beginning to follow them there."""

    return {
        "headline": "Modi Becomes the First Indian PM to Visit Slovakia. The People Who Waited Up for Him Were the Diaspora.",
        "subheadline": "On a historic first visit since Slovakia's 1993 independence, India and Slovakia upgraded ties to a Comprehensive Partnership and signed defence and trade deals — but it was the airport crowd of Indian workers that captured the moment.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "diaspora",
        "status": "review",
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": "Prime Minister Narendra Modi with Slovak Prime Minister Robert Fico at Bratislava Castle.",
        "image_attribution": "Wikimedia Commons",
        "diaspora_angle": "The first-ever visit by an Indian PM to Slovakia signals that Central Europe is becoming a real destination for Indian skilled workers, and that India's consular and trade support is beginning to follow the diaspora to smaller, non-traditional countries.",
        "sources": ["IANS", "Jagran Josh", "Dainik Bhaskar (English)", "Reuters"],
        "published_at": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    art = article_modi_slovakia()
    wc = len(art["body"].split())
    print(f"  word count: {wc}")
    if wc < 400:
        print("  \u274c word count below floor, aborting")
    else:
        insert_article(art)
