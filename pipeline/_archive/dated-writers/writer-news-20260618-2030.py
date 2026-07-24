#!/usr/bin/env python3
"""News writer for The Videshi — 2026-06-18 20:30 UTC run.

Story: The DHS "Duration of Status" final rule. For 30+ years, F-1/J-1
students have been admitted for "Duration of Status" — no fixed end date,
free to stay as long as they make academic progress, with their university's
Designated School Official (DSO) handling extensions. On May 5, 2026, DHS
sent a FINAL rule to OMB that would scrap D/S and admit students for a FIXED
period capped at four years. Anyone needing longer — PhDs (5-8 yrs typical),
OPT/STEM-OPT workers, program-changers — must file Form I-539 with USCIS,
pay a fee, give biometrics, and prove eligibility under discretionary
standards. OMB review is the last step before Federal Register publication;
NAFSA expects the rule could be effective for students arriving Fall 2026.

Distinct from prior coverage: existing pieces cover the 6.9% enrollment
DROP (a past-year statistic), the H-1B $100k fee saga, EB-2 retrogression,
and the July visa bulletin. THIS is the structural D/S-to-fixed-term rule —
a separate, decades-in-the-making regulatory change now at the final
publication step, hitting students mid-degree, not just new arrivals.

Diaspora angle: Indians are the single largest source of US international
students and ~half of all OPT/STEM-OPT participants; this rule reshapes the
study-to-work pipeline that built much of the US tech diaspora.

Sources: ICEF Monitor, Bloomberg Law, NAFSA, Reddy Neumann Brown PC,
Yale OISS, Ogletree Deakins.
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


def curl_download(url, out="/tmp/_videshi_hero_news2030.jpg"):
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
    # Wikimedia Commons: USCIS headquarters — the agency that, under the new
    # rule, takes over the power to grant student extensions. Exactly the
    # institution at the center of the story.
    src = ("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/"
           "USCIS_HQ_Groundbreaking_Ceremony_%2838096348641%29.jpg/"
           "1280px-USCIS_HQ_Groundbreaking_Ceremony_%2838096348641%29.jpg")
    img_bytes = curl_download(src)
    if img_bytes:
        pub = upload_to_supabase(img_bytes, "uscis-duration-of-status-rule-f1-students-20260618.jpg")
        if pub and validate_get(pub):
            return pub
    if validate_get(src):
        return src
    return None


def article():
    print("\n=== Article: DHS Duration of Status final rule ===")

    img_url = source_hero_image()
    if not img_url:
        print("  \u26a0 no valid hero image")

    slug = "dhs-duration-of-status-final-rule-omb-f1-students-four-year-limit-opt-india-20260618"

    body = """For more than three decades, an Indian student arriving in the United States on an F-1 visa was admitted for something called "Duration of Status." There was no fixed expiry date stamped on the I-94. As long as the student stayed enrolled and made academic progress, they could stay \u2014 finish a bachelor's, roll into a master's, push through a PhD, then move on to a year of Optional Practical Training and, for STEM graduates, two more. The paperwork was light and the university's own international office handled extensions.

That entire architecture is now one signature away from disappearing.

On May 5, 2026, the Department of Homeland Security sent a **final rule** to the White House's Office of Management and Budget that would scrap Duration of Status for F (student), J (exchange visitor) and I (foreign media) visa holders and replace it with a fixed admission period capped at **four years**. OMB review is the last procedural step before publication in the Federal Register. The rule takes effect 60 days after it is published \u2014 and the administration has made clear it wants the change in place for students arriving this fall.

## What actually changes

Today, a Designated School Official (DSO) at a student's own university can extend their stay, approve a transfer, or update the record when they move from a master's into a doctorate. Under the final rule, that authority shifts entirely to **US Citizenship and Immigration Services**. Any student whose program runs past their fixed end date \u2014 or who wants to start OPT \u2014 would have to file Form I-539, pay a fee, submit biometrics, and prove continued eligibility to a federal officer empowered to "use discretion" in saying no.

The rule carries a stack of other restrictions. The grace period after a program ends shrinks from 60 days to 30. Undergraduates cannot change major, program or level in their first year; graduate students cannot change programs at all. And a student who finishes a degree cannot use F-1 status to enroll in another program at the same or a lower level.

> "This is the most consequential change to student visas in three decades, and most international students do not yet realize what is coming."

## Why this lands hardest on Indians

India is the single largest source of international students in the United States, and the new regime aims squarely at the pathway most Indian students rely on. PhD programs routinely run five to eight years \u2014 well past the four-year cap \u2014 forcing doctoral candidates into mid-degree filings with USCIS officers who can deny them. Even more exposed is post-study work. Indians make up roughly **half** of all participants in OPT and STEM OPT, the bridge that has carried generations of Indian graduates from a campus lab into a Bay Area or Seattle tech job, and often onward to an H-1B and a green card.

USCIS director Joseph Edlow has said openly that he wants to "remove the ability for employment authorizations for F-1 students beyond the time that they are in school." A NAFSA survey found that **54%** of current international students would not have chosen the United States at all if OPT did not exist.

## A backlog meets a flood of new filings

The practical problem is timing. USCIS is already among the most backlogged agencies in the federal government. Routing every long-program student, every OPT applicant and every level-changer into that queue \u2014 each needing an approval before their clock runs out \u2014 risks leaving thousands in limbo, unable to work or even sure they can stay, while they wait months for an answer. NAFSA, which has led a sector-wide campaign against the rule, calls the shift a "sea change" and argues DHS could achieve its stated anti-fraud goals with modest fixes to the existing SEVIS tracking system instead.

DHS frames the overhaul as a national-security measure that gives the government more frequent checkpoints to monitor international students \u2014 a concept first floated during the first Trump administration and beaten back then by universities and hospitals.

## What happens next

Legal challenges are widely expected. Immigration litigators say that when the final rule publishes, DHS will have to show its rationale outweighs the documented harm to students and institutions, or risk being struck down as "arbitrary and capricious." Universities, meanwhile, are preparing in the dark: the text of the final rule stays secret until roughly 24 hours before it appears in the Federal Register.

For the diaspora, the stakes are not abstract. The study-to-work-to-residency pipeline that this rule reshapes is, in large part, the story of how the modern Indian-American professional class was built. Families weighing whether to send a child to a US campus this year are now doing that math against a four-year clock and a discretionary federal officer \u2014 and a growing number, education consultants in India report, are looking at the UK, Canada and Europe instead."""

    return {
        "headline": "The Biggest Change to US Student Visas in 30 Years Is One Signature Away \u2014 and It Hits Indians Hardest",
        "subheadline": "A final DHS rule sitting at the White House would scrap open-ended 'Duration of Status' for F-1 students and cap stays at four years, routing every PhD, OPT worker and program-changer through a backlogged USCIS. Indians \u2014 half of all OPT participants \u2014 stand most exposed.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "immigration",
        "status": "review",
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": "The US Citizenship and Immigration Services headquarters, the agency that would take over authority to grant student visa extensions under the new rule.",
        "image_attribution": "Wikimedia Commons",
        "diaspora_angle": "Indians are the largest group of US international students and roughly half of all OPT and STEM OPT participants, so a rule that caps student stays at four years and hands extension power to a backlogged USCIS strikes directly at the study-to-work pipeline that built much of the Indian-American professional class.",
        "sources": [
            "ICEF Monitor \u2014 US to end 'Duration of Status' for F, J, and I visas (May 2026)",
            "Bloomberg Law \u2014 White House Reviewing Rule to Limit Foreign Students' Status (RIN 1653-AA95, June 2026)",
            "NAFSA: Association of International Educators \u2014 Duration of Status Rule Portal (final rule submitted to OMB May 5, 2026)",
            "Reddy Neumann Brown PC \u2014 DHS Moves to End Duration of Status for F-1, J-1, and I Visa Holders (May 2026)",
            "Yale Office of International Students & Scholars \u2014 DHS Proposes to Replace Duration of Status with Fixed Periods of Stay",
            "Ogletree Deakins \u2014 DHS Rule Proposing Changes to F, J, and I Visa Programs Under Final Review (2026)",
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
