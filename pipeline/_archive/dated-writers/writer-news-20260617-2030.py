#!/usr/bin/env python3
"""News writer for The Videshi — 2026-06-17 20:30 UTC run.

Story: Forbes published its inaugural "Forbes 250: America's Most Successful
Immigrants" list (June 10-12, 2026), timed to the US 250th anniversary. India
is the single most-represented country of origin, with ~32 honorees across the
full list (NRI Pulse tabulation) — ahead of Canada (18), Israel (15), China
(14) and the UK (14). Honorees span Vinod Khosla (14th, highest Indian-origin),
Naval Ravikant, Sundar Pichai, Satya Nadella, Nikesh Arora, Arvind Krishna,
Shantanu Narayen, Indra Nooyi, Abhijit Banerjee (Nobel), Padma Lakshmi, etc.
Historic list honors Har Gobind Khorana, Bhagat Singh Thind, Dalip Singh Saund,
Paramahansa Yogananda — but conspicuously omits Subrahmanyan Chandrasekhar.
Diaspora angle: a landmark national recognition of Indian-American achievement
arriving in the same season as tighter US visa scrutiny.
(Forbes, American Kahani / NRI Pulse, The Local Report, Cold Spring Harbor Lab,
Mandatory — June 2026)
"""

import os
import subprocess
from datetime import datetime, timezone
import requests

UA = "TheVideshi/1.0 (thevideshi.com)"


def curl_download(url):
    try:
        out = "/tmp/_videshi_hero_news2030.jpg"
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
    # Wikipedia: Sundar Pichai (2023, cropped) — CC, most recognizable Indian-origin
    # honoree on the Forbes 250 living list. Use originalimage full-res source.
    src = ("https://upload.wikimedia.org/wikipedia/commons/"
           "c/c3/Sundar_Pichai_-_2023_%28cropped%29.jpg")
    img_bytes = curl_download(src)
    if img_bytes:
        pub = upload_to_supabase(img_bytes, "sundar-pichai-forbes250-immigrants-20260617.jpg")
        if pub and validate_get(pub):
            return pub
    if validate_get(src):
        return src
    return None


def article():
    print("\n=== Article: Forbes 250 Most Successful Immigrants — India dominates ===")

    img_url = source_hero_image()
    if not img_url:
        print("  \u26a0 no valid hero image")

    slug = "forbes-250-most-successful-immigrants-india-most-represented-khosla-pichai-nadella-20260617"

    body = """When Forbes set out to name America's most successful immigrants for the country's 250th birthday, one nation finished first — and it was not the one that has sent the most people. India is the single most-represented country of origin on the inaugural "Forbes 250: America's Most Successful Immigrants," published this month, with roughly 32 honorees across the full list, according to a tabulation by NRI Pulse. That puts India ahead of Canada (18), Israel (15), China (14) and the United Kingdom (14).

The list, split into living immigrants and the greatest historic ones, is topped overall by Arnold Schwarzenegger and Elon Musk. But scan down the rankings and the Indian-origin names accumulate fast — in venture capital, semiconductors, cloud computing, economics, food, and the C-suites of the world's largest companies.

## The investors and the chief executives

The highest-placed Indian-origin honoree is Vinod Khosla at No. 14. He arrived from New Delhi in 1976, co-founded Sun Microsystems, and built Khosla Ventures into one of Silicon Valley's most influential early-stage firms, with bets on DoorDash, Stripe, Affirm and OpenAI, for which his firm was the first institutional backer. Forbes pegs his net worth near $14 billion.

Close behind in spirit is Naval Ravikant (27th), the New Delhi-born co-founder of AngelList who backed Uber and Twitter early, and Hemant Taneja (31st) of General Catalyst. The most recognizable names to a general audience are the men running big tech: Sundar Pichai of Alphabet, born in Madurai, at 55th; Satya Nadella of Microsoft, born in Hyderabad, at 89th; Nikesh Arora of Palo Alto Networks at 155th; Arvind Krishna of IBM at 219th; and Shantanu Narayen of Adobe at 221st.

Sanjay Mehrotra (44th), who founded SanDisk before leading Micron to a trillion-dollar valuation, and Jay Chaudhry (93rd), who grew up in a Himalayan village without electricity and built the cloud-security firm Zscaler, round out a cohort whose companies touch nearly every corner of the digital economy.

## Beyond the boardroom

The list reaches past technology. Abhijit Banerjee (59th), the Mumbai-born MIT economist, won the 2019 Nobel Prize for pioneering randomized trials to fight poverty. Padma Lakshmi (64th) built a career across television and food culture. The two Indian-origin women on the list reflect that range: Neerja Sethi (91st), who co-founded the IT firm Syntel in her apartment and later pledged to give away $1.3 billion, and Indra Nooyi (248th), the Chennai-born former PepsiCo chief who now sits on Amazon's board.

Several builders trace classic immigrant arcs. Jyoti Bansal (127th) waited seven years for a green card before founding AppDynamics, sold to Cisco for $3.7 billion. Rakesh Gangwal (230th) ran US Airways before co-founding IndiGo, now India's largest airline. Pakistani-origin honorees feature prominently too, led by Shahid Khan at 11th — who arrived with $500, bought the company that once employed him, and owns the Jacksonville Jaguars.

## The historic list — and a glaring omission

Forbes also honored historic figures. Har Gobind Khorana, the Punjab-born Nobel laureate who cracked part of the genetic code at the University of Wisconsin, is recognized at 49th among historic immigrants. So are Bhagat Singh Thind, the World War I veteran whose Supreme Court case helped open citizenship to Indian-born Americans; Dalip Singh Saund, the first Indian American elected to Congress; and Paramahansa Yogananda, who introduced millions of Americans to yoga.

One name is conspicuously absent: Subrahmanyan Chandrasekhar. The Nobel-winning astrophysicist spent 58 years at the University of Chicago, gave his name to the Chandrasekhar limit and to NASA's Chandra X-ray Observatory, and is by most measures among the most consequential immigrant scientists in American history. His omission, critics note, is the one real gap in an otherwise sweeping tribute.

## Why the diaspora should care

The timing is what gives the list its charge. It lands in a season of tighter visa scrutiny, H-1B fee fights and falling Indian student enrollment — a moment when the value of skilled immigration is being openly contested in Washington. For Indian Americans, a marquee national ranking that places their community at the top is both a point of pride and a pointed argument: the people powering Google, Microsoft, Adobe, IBM, Micron and a long list of startups all arrived as immigrants. As the country marks 250 years, the list is a reminder of who helped build the modern American economy — and what is at stake in the debate over who gets to come next."""

    return {
        "headline": "Forbes Named America's Most Successful Immigrants. India Topped Every Other Country.",
        "subheadline": "Roughly 32 Indian-origin honorees — from Vinod Khosla and Sundar Pichai to Indra Nooyi and a Nobel laureate — lead Forbes' 250th-anniversary list, even as one towering name is left off.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "diaspora",
        "status": "review",
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": "Alphabet CEO Sundar Pichai, born in Madurai, is among roughly 32 Indian-origin honorees on Forbes' inaugural list of America's most successful immigrants.",
        "image_attribution": "Wikimedia Commons",
        "diaspora_angle": "A landmark Forbes ranking places Indian-origin immigrants at the top of America's success story just as the US tightens visas and H-1B rules — making the list both a celebration and an argument for the value of skilled Indian migration.",
        "sources": [
            "Forbes \u2014 Forbes 250: America's Most Successful Immigrants (June 10\u201312, 2026)",
            "American Kahani / NRI Pulse \u2014 India at the Top: South Asians on Forbes' Most Successful Immigrants List (June 2026)",
            "The Local Report \u2014 America's 'Most Successful Immigrants': 26 Indian-American leaders including Sundar Pichai, Satya Nadella (June 2026)",
            "Cold Spring Harbor Laboratory \u2014 Krainer included in Forbes' Most Successful Immigrants list (June 15, 2026)",
            "Mandatory \u2014 Melania Trump Ranked Among America's 250 Greatest Living Immigrants (June 2026)",
        ],
        "published_at": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    art = article()
    wc = len(art["body"].split())
    print(f"  word count: {wc}")
    if wc < 400:
        print("  \u274c word count below floor, aborting")
    elif not art["image_url"]:
        print("  \u274c no hero image, aborting")
    else:
        insert_article(art)
