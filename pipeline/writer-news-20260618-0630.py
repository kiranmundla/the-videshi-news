#!/usr/bin/env python3
"""News writer for The Videshi — 2026-06-18 06:30 UTC run.

Story: On June 17, 2026, at the G7 summit in Evian, France, the UK and India
announced the India-UK Comprehensive Economic and Trade Agreement (CETA) and
the accompanying Double Contribution Convention (DCC) will enter into force on
July 15, 2026 — the fastest-ever turnaround from signature to entry-into-force
for India, after a ~12-month delay over the UK's steel safeguards and Carbon
Border Adjustment Mechanism. Confirmed after a Modi-Starmer meeting.
Diaspora angle: The DCC exempts ~75,000 Indian detached workers (and ~900
employers) on short-term UK visas from paying UK National Insurance for up to
3 years; Indian govt estimates an average IT professional saves ₹30-40 lakh
over a 3-year stint. Tariff cuts: whisky 150%->40%, autos 100%->10% (quota),
cosmetics up to 22% removed. Sources: GOV.UK, Reuters, Livemint, The Hindu
BusinessLine, ICAEW, MEA — all June 2026 / 2025-26.
"""

import os
import subprocess
from datetime import datetime, timezone
import requests

UA = "TheVideshi/1.0 (thevideshi.com)"


def curl_download(url):
    try:
        out = "/tmp/_videshi_hero_news0630.jpg"
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
    # Wikimedia Commons: Modi and Starmer addressing a joint press meet —
    # an official PMO/government photo of the two leaders whose deal is the
    # subject of this article. Specifically relevant.
    src = ("https://upload.wikimedia.org/wikipedia/commons/thumb/9/99/"
           "Prime_Minister_of_Bharat%2C_Shri_Narendra_Damodardas_Modi_and_the_Prime_Minister_"
           "of_the_United_Kingdom%2C_Sir_Keir_Starmer_addressing_a_joint_press_meet.jpg/"
           "1280px-Prime_Minister_of_Bharat%2C_Shri_Narendra_Damodardas_Modi_and_the_Prime_Minister_"
           "of_the_United_Kingdom%2C_Sir_Keir_Starmer_addressing_a_joint_press_meet.jpg")
    img_bytes = curl_download(src)
    if img_bytes:
        pub = upload_to_supabase(img_bytes, "modi-starmer-uk-india-fta-dcc-20260618.jpg")
        if pub and validate_get(pub):
            return pub
    if validate_get(src):
        return src
    return None


def article():
    print("\n=== Article: UK-India FTA + DCC enters force July 15 ===")

    img_url = source_hero_image()
    if not img_url:
        print("  \u26a0 no valid hero image")

    slug = "uk-india-trade-deal-dcc-national-insurance-july-15-diaspora-30-lakh-20260618"

    body = """For the roughly 75,000 Indians working in Britain on short-term assignments, one of the quiet indignities of the posting has been paying twice. Twice into a pension, twice into a social safety net — once at home in India, and again into a UK National Insurance system from which they would never see a penny back. On Wednesday, that double charge got an expiry date.

Meeting on the sidelines of the G7 summit in Evian, France, Prime Minister Narendra Modi and his British counterpart Keir Starmer confirmed that the India-UK Comprehensive Economic and Trade Agreement (CETA) — along with the social security pact that travels with it — will enter into force on **July 15, 2026**. "We did it," Modi was overheard telling Starmer. "We did it. Yes, yes, yes," Starmer replied. "We got it over the line."

## A deal a year in the making

The agreement is not new. It was signed in London in July 2025, but its implementation stalled for nearly a year over two sticking points: Britain's proposed Carbon Border Adjustment Mechanism (CBAM), a carbon tax on imports due in 2027, and new UK steel safeguard measures taking effect July 1 that cap tariff-free Indian steel and could hit some $775 million of Indian exports. With those concerns parked rather than fully resolved, both sides agreed to move ahead. The British government called it the quickest turnaround from signature to entry-into-force the UK has ever managed, and the most comprehensive trade deal India has ever brought into force. Businesses now have 28 days to register to claim the tariff benefits.

The headline numbers are substantial. London estimates the deal will lift UK GDP by £4.8 billion, raise real wages by £2.2 billion, and grow bilateral trade — already worth about $56 billion a year — by £25.5 billion annually over the long run. For Indian consumers, whisky tariffs drop from 150% to 40%, automotive tariffs from over 100% to 10% under a quota, and duties of up to 22% on cosmetics will be scrapped immediately or phased out. Indian exporters of textiles, leather, footwear, gems and jewellery, and processed foods gain duty-free or reduced-tariff access to the British market.

## The part that lands in NRI bank accounts

Buried in the fine print is the provision the diaspora will feel most directly: the **Double Contribution Convention (DCC)**, which comes into force the same day. Under it, Indian professionals sent to work temporarily in the UK — and the companies that employ them — are exempted from paying into Britain's National Insurance scheme for up to three years, so long as they keep contributing to India's Employees' Provident Fund back home.

The math is not trivial. By the Indian Labour Ministry's own pre-negotiation assessment, the combined employee-and-employer social security charge runs to roughly 23% of salary. For an average IT professional on a UK package, that worked out to £11,000-£12,000 a month flowing into a British system they would never draw from — money the ministry bluntly described as previously "confiscated." The government's estimate: an average worker now saves between **₹30 lakh and ₹40 lakh over a three-year stint**, money that stays in take-home pay or builds an Indian pension instead of vanishing.

Around 900 Indian employers — the IT services giants and consultancies that rotate staff through British client sites — also save, sharpening the cost competitiveness of Indian talent abroad. It is worth being precise about the limits: the DCC coordinates *which* country gets the contribution, not access to benefits. Indian detached workers will not build UK State Pension entitlement, and if a worker's family member takes a UK job, they pay UK National Insurance as normal.

## Why it matters beyond the payslip

For the Indian diaspora, the deal is a marker of a wider shift. India spent the spring stitching together trade arrangements on multiple fronts — concluding the "mother of all deals" with the European Union (which Brussels says it will formally sign by year-end), pressing toward an interim agreement with the United States, and now switching on the UK pact. For NRIs whose careers straddle two countries, that web of agreements increasingly means smoother mobility, lower friction, and more of their earnings staying in their own pockets.

The relief is not unconditional. The CBAM carbon levy still looms in 2027, and the steel safeguards remain a live irritant. But for the Indian engineer in Manchester or the consultant in Canary Wharf, July 15 marks the day a long-standing grievance — paying full freight into a system built for someone else — finally comes off the books."""

    return {
        "headline": "The UK-India Trade Deal Switches On July 15. The Real Win for NRIs Is Hidden in the Fine Print.",
        "subheadline": "After a year's delay, the India-UK trade pact and its social security convention come into force next month. For 75,000 Indians working in Britain, it ends the double social security charge \u2014 a saving the Indian government pegs at \u20b930-40 lakh over a three-year posting.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "economy",
        "status": "review",
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": "Prime Minister Narendra Modi and UK Prime Minister Sir Keir Starmer address a joint press meet during Starmer's India visit.",
        "image_attribution": "Wikimedia Commons",
        "diaspora_angle": "The Double Contribution Convention coming into force July 15 exempts around 75,000 Indian professionals in the UK from paying British National Insurance for up to three years \u2014 a saving the Indian government estimates at \u20b930-40 lakh per worker over a three-year posting.",
        "sources": [
            "GOV.UK \u2014 The countdown begins: UK-India FTA enters into force on July 15th (June 17, 2026)",
            "Reuters \u2014 UK-India trade deal worth over $6 billion to start July 15 (June 17, 2026)",
            "Livemint \u2014 India-UK trade pact, social security agreement to come into effect from 15 July (June 17, 2026)",
            "The Hindu BusinessLine \u2014 Expats to be richer by at least \u20b930-40 lakh after 3 years due to India-UK social security agreement",
            "ICAEW \u2014 Update on UK-India social security agreement (Double Contributions Convention)",
            "Ministry of External Affairs (mea.gov.in) \u2014 Signing of Agreement on Social Security between India and the United Kingdom (Feb 10, 2026)",
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
