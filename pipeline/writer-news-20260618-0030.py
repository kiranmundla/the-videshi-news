#!/usr/bin/env python3
"""News writer for The Videshi — 2026-06-18 00:30 UTC run.

Story: The July 2026 Visa Bulletin (released by DOS on June 16, 2026) closes
the door on EB-2 India. India's EB-2 employment-based category is now listed
"Unavailable" — meaning no new EB-2 India adjustment-of-status applications
can be filed for the rest of fiscal year 2026 (through Sept 30). DOS confirmed
on May 22, 2026 that EB-2 India had hit its FY-2026 per-country annual limit.
EB-1 India also retrogressed (to Oct 15, 2022), and EB-5 Unreserved India went
"Unavailable" too. The lone bit of relief: EB-3 India advanced two weeks to
Jan 1, 2014, and EB-5 set-aside categories (rural/HUA/infrastructure) remain
current. The bulletin's own warning text flags more retrogression to come.
Diaspora angle: hundreds of thousands of Indian H-1B professionals waiting in
the EB-2 green card queue just lost their filing window for months; the
decades-long India backlog gets concretely worse.
(Sources: US DOS July 2026 Visa Bulletin / travel.state.gov; Murthy Law Firm;
Fragomen; Ogletree Deakins / JDSupra; WR Immigration / Wolfsdorf — June 2026)
"""

import os
import subprocess
from datetime import datetime, timezone
import requests

UA = "TheVideshi/1.0 (thevideshi.com)"


def curl_download(url):
    try:
        out = "/tmp/_videshi_hero_news0030.jpg"
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
    # Wikimedia Commons: the U.S. State Department headquarters (Harry S.
    # Truman Building) in Washington — the agency that issues the monthly
    # Visa Bulletin. CC-licensed, permanent upload.wikimedia.org URL.
    src = ("https://upload.wikimedia.org/wikipedia/commons/"
           "c/c9/The_United_States_State_Department_Headquarters_Building.jpg")
    img_bytes = curl_download(src)
    if img_bytes:
        pub = upload_to_supabase(img_bytes, "us-state-department-visa-bulletin-20260618.jpg")
        if pub and validate_get(pub):
            return pub
    if validate_get(src):
        return src
    return None


def article():
    print("\n=== Article: July 2026 Visa Bulletin — EB-2 India unavailable ===")

    img_url = source_hero_image()
    if not img_url:
        print("  \u26a0 no valid hero image")

    slug = "july-2026-visa-bulletin-eb2-india-unavailable-green-card-backlog-h1b-20260618"

    body = """For hundreds of thousands of Indian professionals waiting on an American green card, the U.S. State Department just slammed a door shut. The July 2026 Visa Bulletin, released on June 16, lists the EB-2 employment-based category for India as "Unavailable" — meaning no new EB-2 India applications can be filed for the rest of the fiscal year, which runs through September 30.

It is one of the bluntest setbacks in years for the country that already faces the longest employment-based green card queue in the world, and it lands squarely on the H-1B engineers, doctors and researchers who form the backbone of the Indian diaspora's professional class in the United States.

## What "Unavailable" actually means

The Visa Bulletin is the monthly schedule the State Department uses to ration immigrant visas under annual numerical caps. Each category carries a "final action date," and only applicants whose priority date falls before that cutoff can have their green card approved. When a category is marked "U" for Unavailable, the line stops moving entirely — no approvals, and in this case no new adjustment-of-status filings either, until the category reopens in a future fiscal year.

EB-2, the second employment-based preference, covers workers holding advanced degrees or with exceptional ability. It is the lane most H-1B holders in skilled tech and healthcare roles rely on. The shutdown was foreshadowed: on May 22, the State Department announced that EB-2 India had already reached its FY-2026 per-country annual limit. The July bulletin makes that exhaustion official.

## A broader retrogression for India

EB-2 was not the only blow. The EB-1 category for India, reserved for priority workers, multinational managers and people of extraordinary ability, retrogressed to a final action date of October 15, 2022 — moving backward by two months from the June bulletin. The EB-5 unreserved investor category for India also flipped to Unavailable.

The one bright spot was modest. EB-3, which covers skilled workers and professionals, advanced two weeks for India to January 1, 2014. The EB-5 set-aside categories — rural, high-unemployment and infrastructure — remain current for all countries, leaving them among the few immediately usable pathways for Indian investors with the capital to pursue them.

The bulletin's own language warns there may be more pain ahead. The State Department noted that high demand and number use by India-chargeable applicants in EB-1 and EB-2 made the retrogression necessary to hold within FY-2026 limits, and cautioned that further retrogressions, or additional categories becoming unavailable, may be required before the fiscal year ends.

## Why the backlog keeps getting worse

The root cause is structural. U.S. law caps the share of employment-based green cards any single country can receive each year at roughly 7 percent, regardless of population or demand. Because Indians file an outsized number of applications, they pile up against that per-country ceiling year after year. Analysts have long estimated that an Indian professional joining the EB-2 queue today could wait decades for a green card under current rules.

Each month the bulletin advances by days or weeks while the line behind it grows by far more. An "Unavailable" designation is what happens when even that trickle is cut off because the annual allotment is simply spent.

## What it means for the diaspora

For Indian families living the H-1B reality, the consequences are immediate and personal. An EB-2 applicant who hoped to file an adjustment of status this summer — the step that unlocks work authorization and travel permission for the whole family and protects children from "aging out" of dependent status at 21 — now has to wait. Job changes, promotions and relocation decisions all hinge on where a worker sits in this queue, and the queue just froze.

It also sharpens a debate already roiling the community. The retrogression arrives the same month a federal court struck down the Trump administration's $100,000 H-1B fee and as Washington and New Delhi work toward a trade deal, with visa policy hovering over the talks. Skilled-immigration advocates have for years pushed Congress to scrap or raise the per-country cap, arguing it punishes nationals of large countries for the accident of where they were born. Bills to do exactly that have repeatedly stalled.

Until something changes legislatively, the math will keep producing months like this one. For the Indian diaspora, the July bulletin is a reminder that the hardest part of building a life in America is often not getting the job — it is getting permission to stay."""

    return {
        "headline": "EB-2 India Just Went 'Unavailable.' The Green Card Door Closes for Months.",
        "subheadline": "The State Department's July 2026 Visa Bulletin halts new EB-2 India green card filings for the rest of the fiscal year, with EB-1 and EB-5 for India also retrogressing — a fresh blow to the H-1B professionals stuck in the world's longest backlog.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "immigration",
        "status": "review",
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": "The U.S. State Department's Harry S. Truman Building in Washington, the agency that issues the monthly Visa Bulletin governing green card availability.",
        "image_attribution": "Wikimedia Commons",
        "diaspora_angle": "Hundreds of thousands of Indian H-1B professionals in the EB-2 green card queue just lost their filing window for the rest of the fiscal year, concretely worsening the world's longest employment-based backlog and freezing job, travel and family decisions for diaspora households.",
        "sources": [
            "U.S. Department of State \u2014 Visa Bulletin for July 2026 (travel.state.gov, released June 16, 2026)",
            "Murthy Law Firm \u2014 July 2026 Visa Bulletin (June 16, 2026)",
            "Fragomen, Del Rey, Bernsen & Loewy LLP \u2014 United States: July 2026 Visa Bulletin analysis (June 2026)",
            "Ogletree Deakins / JDSupra \u2014 USCIS Requires Final Action Dates for Employment-Based Filings (June 2026)",
            "WR Immigration (Wolfsdorf Rosenthal) \u2014 Visa Bulletin retrogression analysis for India EB-1 and EB-2 (June 2026)",
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
