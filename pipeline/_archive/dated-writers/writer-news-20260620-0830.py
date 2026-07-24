#!/usr/bin/env python3
"""News writer for The Videshi — 2026-06-20 08:30 UTC run.

Story: On Wednesday, June 17, 2026, India and the United Kingdom announced that
the Comprehensive Economic and Trade Agreement (CETA) and the accompanying
Double Contribution Convention (DCC) on social security will both enter into
force on July 15, 2026 — confirmed after Modi and Starmer met on the sidelines
of the G7 summit in France. CETA gives ~99% of Indian exports duty-free access
to the UK; the DCC exempts Indian professionals on temporary UK postings from
paying into UK National Insurance for up to FIVE years (up from three), with
75,000+ Indian professionals and 900+ companies expected to benefit. The FTA
was signed July 2025 but implementation was delayed ~12 months over the UK's
steel safeguards / carbon border (CBAM) dispute. Businesses get 28 days to
prepare and must register to claim tariff cuts.

Distinct from prior coverage: the feed has a UK-India trade item from June 19
22:45 ("entering the home stretch") that is about the *US* trade deal, plus a
generic 10-year e-visa travel piece. There is NO news-category article on the
UK-India CETA confirmation, the July 15 date, or — crucially — the Double
Contribution Convention's National Insurance exemption, which is the single
biggest diaspora-pocketbook angle. This is fresh.

Diaspora angle: tens of thousands of Indian IT and professional-services
workers on intra-company transfers and short-term UK assignments will stop
losing ~12% of salary to UK National Insurance they could never reclaim — a
direct, recurring pay rise for the very NRIs The Videshi serves, plus cheaper
Indian goods (textiles, food, leather) on UK shelves for the resident diaspora.

Sources: GOV.UK ("The countdown begins", June 17, 2026); Reuters ("UK-India
trade deal worth over $6 billion to start July 15"); India Ministry of Commerce
via Livemint/Capital Market (CETA + DCC enter force July 15, 5-year exemption);
Madhyamam/Bloomberg ("We did it" Modi-Starmer exchange, CBAM delay backstory).
"""

import os
from datetime import datetime, timezone
import urllib.parse
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

# Hero: PM Modi receives UK PM Sir Keir Starmer in Mumbai, Oct 9, 2025.
# Wikimedia Commons, GODL-India (Government Open Data License - India).
# Downloaded from Commons and re-hosted on Supabase storage for permanence.
# Verified HTTP 200, image/jpeg, 235,478 bytes, 1280x859.
HERO_URL = ("https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/"
            "public/article-images/news-india-uk-fta-july15-20260620.jpg")


def validate_get(url):
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=20,
                         stream=True, allow_redirects=True)
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
            print(f"  Inserted: {data[0].get('headline','?')[:80]}")
            return data[0]
        print(f"  Inserted (raw): {r.text[:120]}")
        return data
    print(f"  Insert failed ({r.status_code}): {r.text[:300]}")
    return None


def article():
    print("\n=== Article: India-UK CETA + DCC enters force July 15 ===")

    slug = ("india-uk-trade-deal-ceta-double-contribution-convention-"
            "july-15-national-insurance-exemption-20260620")

    body = """For the better part of a year, the most ambitious trade deal India has ever signed sat finished but dormant — agreed, celebrated, and then stuck. On Wednesday, the wait ended. India and the United Kingdom confirmed that their Comprehensive Economic and Trade Agreement (CETA), and the social-security pact that travels with it, will both come into force on **July 15, 2026**.

The breakthrough came on the sidelines of the G7 summit in France, where Prime Minister Narendra Modi met his British counterpart, Sir Keir Starmer. Bloomberg caught the moment the two leaders realised it was done. "We did it," Modi said. "We did it. Yes, yes, yes, I hear. We got it over the line," Starmer replied. "So this is good."

## What actually changes

On paper, CETA is a tariff story, and a big one. India's commerce ministry says nearly **99% of Indian export lines** will get immediate duty-free access to the British market — covering almost the entire value of bilateral trade. Duties of up to 70% on processed food, 21.5% on marine products, 18% on engineering goods and auto components, 16% on leather and footwear, 12% on textiles and clothing, and 8% on chemicals and pharmaceuticals all drop to zero.

British exporters get their own wins. India will cut tariffs on Scotch whisky from 150% to 40%, on cars from 100% to 10% under a quota, and eliminate duties of up to 22% on cosmetics. The UK government estimates the deal could lift British GDP by £4.8 billion and wages by £2.2 billion a year over the long run, calling it "the most comprehensive trade deal India has ever brought into force."

## The clause that lands in NRI pay slips

But for the diaspora, the headline buried in the fine print is not about whisky or marine exports. It is the **Double Contribution Convention (DCC)** — the social-security agreement that takes effect the very same day.

Until now, an Indian professional sent on a temporary posting to Britain had to pay UK National Insurance — roughly an extra slice of salary — on top of contributing back home, with little hope of ever drawing a UK pension from it. The DCC ends that double charge. Indian workers on temporary assignment will be exempt from UK social-security contributions, and the exemption window has been stretched from three years to **five**.

New Delhi expects more than **75,000 Indian professionals and over 900 companies** to benefit — overwhelmingly in IT and professional services, the engine of the modern India-UK relationship. For an individual on a multi-year intra-company transfer, the saving runs into thousands of pounds a year. It is, in effect, a recurring raise for exactly the kind of worker The Videshi's readers know well.

## Why it was stuck — and why it moved

The agreement was first signed back in July 2025. Its implementation then stalled for roughly twelve months, snagged on Britain's proposed Carbon Border Adjustment Mechanism and a forthcoming steel-safeguard regime due to bite from July 1. Indian officials had openly floated reopening or delaying the pact over fears the new steel rules would erode their gains.

The G7 meeting cleared the logjam. Both governments completed their ratification procedures, and London set the clock running: businesses now have **28 days** to prepare, and must register to actually claim the tariff reductions. "The deal gives British exporters an edge over international competitors, and I would encourage all businesses to ensure they are properly prepared," said UK Business and Trade Secretary Peter Kyle.

## What it means for the diaspora

India-UK trade already touched roughly $56 billion in 2024-25 — without any free-trade pact at all. Both sides have set a target of doubling that by 2030, and CETA is the instrument meant to get them there.

For Non-Resident Indians, the deal cuts two ways at once. Resident NRIs in Britain will see cheaper Indian textiles, food and leather goods on the shelves as duties fall. And the wave of professionals who rotate between Bengaluru, Pune, Hyderabad and London — the human bandwidth of the relationship — will keep more of what they earn, for longer, the moment they land.

After a year in limbo, the countdown is finally real. On July 15, the paperwork becomes a pay rise.
"""

    return {
        "headline": "The India-UK Trade Deal Finally Has a Date — and a Quiet Win for NRI Pay Packets",
        "subheadline": "CETA and the Double Contribution Convention both take effect July 15. The tariff cuts grabbed the headlines, but the clause that exempts 75,000 Indian professionals from UK National Insurance for five years is the one diaspora workers will feel.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "economy",
        "status": "review",
        "is_editorial": False,
        "image_url": HERO_URL,
        "image_caption": "PM Narendra Modi receives UK Prime Minister Sir Keir Starmer in Mumbai, October 2025.",
        "image_attribution": "Wikimedia Commons",
        "diaspora_angle": "The trade deal's social-security pact exempts more than 75,000 Indian professionals on temporary UK postings from paying UK National Insurance for up to five years — a direct, recurring pay rise for the diaspora workers who shuttle between India and Britain.",
        "sources": [
            "GOV.UK \u2014 'The countdown begins: UK-India FTA enters into force on July 15th' (June 17, 2026)",
            "Reuters \u2014 'UK-India trade deal worth over $6 billion to start July 15' (June 17, 2026)",
            "India Ministry of Commerce & Industry via Livemint / Capital Market \u2014 'India-UK CETA and Double Contribution Convention to come into effect from 15 July' (5-year exemption, 99% duty-free lines)",
            "Madhyamam Online / Bloomberg \u2014 'India-UK free trade agreement to take effect from July 15' (Modi-Starmer 'We did it' exchange; CBAM/steel delay backstory)",
        ],
        "published_at": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    art = article()
    wc = len(art["body"].split())
    print(f"  word count: {wc}")
    print(f"  headline chars: {len(art['headline'])}")
    print(f"  subheadline chars: {len(art['subheadline'])}")
    if wc < 400:
        print("  word count below floor, aborting")
    elif len(art["headline"]) > 200:
        print("  headline too long, aborting")
    elif not validate_get(art["image_url"]):
        print("  hero image failed validation, aborting")
    else:
        insert_article(art)
