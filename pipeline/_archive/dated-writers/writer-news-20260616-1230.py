#!/usr/bin/env python3
"""News writer for The Videshi — 2026-06-16 12:30 UTC run (Rubio-Jaishankar Delhi presser: visas + anti-India racism)."""

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
    # Official US State Dept photo of Rubio meeting Jaishankar (Wikimedia Commons, public domain)
    src = ("https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/"
           "Secretary_Rubio_Meets_with_Indian_External_Affairs_Minister_%2854280239167%29.jpg/"
           "1280px-Secretary_Rubio_Meets_with_Indian_External_Affairs_Minister_%2854280239167%29.jpg")
    try:
        r = requests.get(src, headers={"User-Agent": UA}, timeout=30)
        if r.status_code == 200 and len(r.content) > 5000:
            pub = upload_to_supabase(r.content, "rubio-jaishankar-meeting-20260616.jpg")
            if pub and validate_get(pub):
                return pub
    except Exception as e:
        print("  hero err", e)
    # Fallback: use the wikimedia URL directly if upload failed but URL is valid
    if validate_get(src):
        return src
    return None


def article_rubio_jaishankar():
    print("\n=== Article: Rubio-Jaishankar Delhi presser (visas + racism) ===")

    img_url = source_hero_image()
    if not img_url:
        print("  \u26a0 no valid hero image")

    slug = "rubio-jaishankar-delhi-press-conference-visa-anti-india-racism-stupid-people-quad-20260616"

    body = """Marco Rubio came to New Delhi to talk about defence frameworks, the Quad and a long-awaited trade deal. What the Indian diaspora heard, instead, was one sentence: "Every country in the world has stupid people."

The remark, delivered by the US Secretary of State at a joint press conference with External Affairs Minister S. Jaishankar at Hyderabad House on Sunday, was Rubio's answer to a direct question about the wave of racist abuse aimed at Indians and Indian-Americans online and in public life over the past year. It went viral within minutes, and for many in the community it crystallised a discomfort that has been building for months: the sense that the relationship at the top is warm while the experience on the ground is anything but.

## What Rubio actually said

Pressed by a reporter on hate directed at Indian-Americans, Rubio said he would take the comments "very seriously" but framed them as the work of isolated cranks rather than a systemic problem. "I'm sure there are stupid people here; there are stupid people in the United States who make dumb comments all the time," he said, adding that the US "is a very welcoming country" that "has been enriched by people who come to our country from all over the world." He pointed to his own family history, noting that his parents migrated from Cuba in 1956.

For a diaspora that has watched figures with large platforms question H-1B workers, mock Indian names and accents, and tie immigration to cultural anxiety, the "stupid people" framing landed awkwardly. It acknowledged the abuse without committing the State Department to do anything about it.

## The visa answer that matters more

Beneath the viral moment was the substance most working NRIs were waiting on: visas. Asked about recent changes to the J-1, F-1 and H-1B programmes, Rubio insisted the overhaul was "not India-specific."

"The changes that are happening now, or the modernisation of our migration system into the United States, are not India-specific; it is global, it's being applied across the world," he said. He cited the roughly 20 million people who entered the US illegally in recent years as the reason for the broader crackdown, and stressed that "everything that you do as a country needs to be in your national interest, and that includes your immigration policy."

Crucially, Rubio admitted that the transition would create "friction points" — diplomatic language for the appointment backlogs, processing delays and uncertainty that Indian students and tech workers have been living with. He also made a point of praising Indian capital, noting that Indian companies have invested more than $20 billion in the US economy and saying Washington wants that figure to keep climbing.

Jaishankar, standing beside him, was blunter about the irritant. He raised the delays affecting legal Indian travellers and students seeking US visas — the very population that forms the backbone of the diaspora's professional class and feeds the pipeline of future migration.

## The deal beneath the optics

The visit was, on paper, a strategic success. Jaishankar confirmed that the two countries had renewed their 10-year major defence partnership framework and signed a comprehensive underwater domain awareness roadmap, with both sides emphasising a "Make in India" approach to future defence manufacturing. On trade, he said negotiators were pushing for an early interim agreement that could pave the way for the broader bilateral deal first floated during Prime Minister Narendra Modi's Washington visit in early 2025 — a US team is expected in Delhi shortly.

Rubio, for his part, swatted away suggestions that the relationship had cooled. "The US-India relationship has not lost any momentum," he said, calling India "one of our most important strategic partners in the world." On Pakistan, he insisted Washington's dealings with Islamabad did not come "at the expense" of ties with Delhi. On the Quad, he thanked Jaishankar for hosting last month's foreign ministers' meeting and described the grouping as four maritime democracies able to "influence global events."

## Why it matters to the diaspora

The press conference captured the central tension of the moment for non-resident Indians: the governments are closer than ever, but the lived experience of migration is getting harder and the public mood in parts of the US is turning colder. A defence framework and a trade deal do little for the family waiting eight months for a student visa appointment, or the H-1B holder watching the rules shift mid-career.

Rubio's "stupid people" line will be remembered as the soundbite. But the more consequential admission was the one about "friction points" — a quiet acknowledgement from America's top diplomat that, for Indians trying to study, work and build a life in the US, the road ahead is going to stay bumpy for a while yet."""

    return {
        "headline": "Rubio Calls Anti-India Racism the Work of 'Stupid People.' For the Diaspora, the Visa Answer Mattered More.",
        "subheadline": "At a New Delhi presser with Jaishankar, the US Secretary of State downplayed hate aimed at Indian-Americans while admitting the visa overhaul will create 'friction points' for the students and H-1B workers who form the diaspora's backbone.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "diaspora-immigration",
        "status": "review",
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": "US Secretary of State Marco Rubio meets Indian External Affairs Minister S. Jaishankar.",
        "image_attribution": "Wikimedia Commons",
        "diaspora_angle": "Rubio's 'stupid people' remark on anti-India racism went viral, but his admission that the J-1, F-1 and H-1B overhaul will create 'friction points' is what directly affects Indian students and tech workers in the US.",
        "sources": ["Times of India", "WION", "U.S. Department of State", "PTI"],
        "published_at": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    art = article_rubio_jaishankar()
    wc = len(art["body"].split())
    print(f"  word count: {wc}")
    if wc < 400:
        print("  \u274c word count below floor, aborting")
    else:
        insert_article(art)
