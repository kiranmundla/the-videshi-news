#!/usr/bin/env python3
"""News writer for The Videshi — 2026-06-18 08:30 UTC run.

Story: At the G7 summit in Evian, France (June 17, 2026), European Commission
President Ursula von der Leyen and European Council President Antonio Costa,
after meeting PM Modi, confirmed the EU and India will FORMALLY SIGN the
India-EU Free Trade Agreement ("the mother of all deals") by the END OF 2026,
and accelerate work on a separate investment agreement. Negotiations concluded
Jan 27, 2026 at the 16th India-EU Summit. The FTA cuts duties on ~99% of Indian
exports to the EU and ~97% of EU exports to India; covers ~2 billion people and
~a quarter of global GDP; ~€4bn/yr saved for EU exporters; EU exports to India
forecast to double by 2032. Signing this year could let it enter force in 2027.
Bundled with it: stepped-up security & defence cooperation, IMEC connectivity
corridor, and a separate mobility pact easing movement for skilled workers and
students. Diaspora angle: the mobility chapter and the broader web of India's
trade deals (UK CETA live July 15, EU sign by end-2026, US interim deal in
talks) mean smoother professional/student mobility into Europe for NRIs.
Sources: Reuters, IANS/ianslive, ANI/Daily Prabhat, PTI/europesays, MEA.
"""

import os
import subprocess
from datetime import datetime, timezone
import requests

UA = "TheVideshi/1.0 (thevideshi.com)"


def curl_download(url):
    try:
        out = "/tmp/_videshi_hero_news0830.jpg"
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
    # Wikimedia Commons: the actual Evian G7 meeting between Modi, Costa and
    # von der Leyen — the precise event this article is about.
    src = ("https://upload.wikimedia.org/wikipedia/commons/7/77/"
           "Prime_Minister_of_Bharat%2C_Shri_Narendra_Damodardas_Modi_meets_the_"
           "President_of_the_European_Council_Mr._Ant%C3%B3nio_Costa_and_the_"
           "President_of_the_European_Commission%2C_Ms._Ursula_von_der_Leyen_in_Evian.jpg")
    img_bytes = curl_download(src)
    if img_bytes:
        pub = upload_to_supabase(img_bytes, "modi-costa-vonderleyen-evian-eu-india-fta-20260618.jpg")
        if pub and validate_get(pub):
            return pub
    if validate_get(src):
        return src
    return None


def article():
    print("\n=== Article: EU-India FTA to be signed by end-2026 ===")

    img_url = source_hero_image()
    if not img_url:
        print("  \u26a0 no valid hero image")

    slug = "eu-india-free-trade-agreement-sign-end-2026-g7-evian-mobility-diaspora-20260618"

    body = """When the European Union's two most senior figures sat down with Narendra Modi on the shores of Lake Geneva this week, they did not announce a new deal. They put a date on an old one. After a meeting on the sidelines of the G7 summit in Evian, France, European Commission President Ursula von der Leyen and European Council President Antonio Costa said the India-EU free trade agreement — the one von der Leyen has taken to calling "the mother of all deals" — will be **formally signed before the end of 2026**.

"Since we have concluded the mother of all trade deals, we have been moving fast to deliver on our commitments," the two leaders wrote in near-identical posts on X. "We will sign the Free Trade Agreement by the end of the year. And accelerate work on an investment agreement. We will also step up security and defence cooperation. And join forces for better connectivity by advancing IMEC, the India-Middle East-Europe Corridor."

## From two decades of talks to a signature

The agreement has been a long time coming. India and the EU began negotiating in 2007, walked away in 2013, and only restarted in earnest in 2022. Negotiations were finally declared concluded on January 27, 2026, at the 16th India-EU Summit in New Delhi, where Modi hosted von der Leyen and Costa around Republic Day. Concluding the text is one thing; signing and ratifying it is another, and that is the step Evian has now pinned to a calendar. A signature this year would put the pact on track to enter into force in 2027.

The scale is hard to overstate. The deal binds together the world's most populous nation and a 27-member bloc, a market of roughly two billion people and close to a quarter of global GDP. By official accounts it will cut duties on about 99% of Indian exports to the EU and on more than 97% of the EU's exports to India. Brussels estimates European exporters alone will save up to €4 billion a year in tariffs, and that EU exports to India could double by 2032. For India, the prizes are duty-free access for labour-intensive exports — textiles, leather, footwear, gems and jewellery, pharmaceuticals — into one of its largest markets.

## The part the diaspora should read twice

For non-resident Indians, the most consequential clauses are not the ones about wine and cars. Alongside the trade text, India and the EU agreed a separate framework aimed at easing mobility for skilled workers and students — the kind of provision that governs how easily an Indian engineer, nurse, or graduate can move to and work across Europe. Brussels and New Delhi also signalled the partnership runs past commerce, into defence, supply-chain security, and the IMEC connectivity corridor meant to link India to Europe through the Gulf.

Read against the rest of the week's news, the picture sharpens. The India-UK trade pact and its social security convention switch on July 15. India's deal with the EU now has a year-end signing date. An interim agreement with the United States is still being negotiated. Taken together, India is assembling a web of trade and mobility arrangements across the West at a pace that would have seemed implausible even two years ago — and for the diaspora, each thread tends to mean lower friction, smoother movement, and more career optionality across borders.

## Why now

Much of this momentum traces back to Washington. As US President Donald Trump has wielded tariffs against allies and rivals alike, both Brussels and New Delhi have been pushed to diversify, to build alternatives, and to hedge against a more unpredictable American trade policy. Von der Leyen has framed the India deal explicitly as a measure of resilience in a "turbulent geopolitical context." For Indians watching from London, Frankfurt, or Toronto, the geopolitics matters less than the practical upshot: the European door, long studied and rarely opened, is finally being fitted with a working hinge.

The caveats are real. "Signed by the end of the year" is a political commitment, not an executed treaty, and ratification across 27 member states can be slow. The investment agreement that travels alongside the FTA is still being worked on. But after eighteen years of false starts, a date on the calendar is itself the news — and for the millions of Indians whose lives already straddle India and Europe, it is a date worth marking."""

    return {
        "headline": "After 18 Years, the India-EU Trade Deal Finally Has a Signing Date: End of 2026",
        "subheadline": "Meeting Modi at the G7 in Evian, the EU's top leaders pinned a date on \"the mother of all deals\" \u2014 a pact covering two billion people. Buried alongside it is a mobility framework the diaspora should read twice.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "geopolitics",
        "status": "review",
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": "Prime Minister Narendra Modi meets European Council President Antonio Costa and European Commission President Ursula von der Leyen on the sidelines of the G7 summit in Evian, France.",
        "image_attribution": "Wikimedia Commons",
        "diaspora_angle": "Alongside the trade text, India and the EU agreed a framework to ease mobility for skilled workers and students \u2014 part of a fast-growing web of India-West trade and mobility deals (UK live July 15, EU to be signed by end-2026) that lowers friction for NRIs moving and working across Europe.",
        "sources": [
            "Reuters \u2014 EU and India will formally sign free trade deal by end-2026, says EU chief (June 17, 2026)",
            "IANS / ianslive.in \u2014 G7 Summit: PM Modi discusses India-EU FTA & West Asia with EU leaders, says MEA (June 17, 2026)",
            "ANI / Daily Prabhat \u2014 India-EU to sign 'mother of all trade deals' by year-end, after G7 meet between PM Modi and European leaders (June 17, 2026)",
            "PTI / europesays.com \u2014 India, EU to sign FTA by end of 2026, says Von der Leyen after talks with PM Modi (June 17, 2026)",
            "Ministry of External Affairs (mea.gov.in) \u2014 readout of PM Modi's meeting with European Council President Antonio Costa and European Commission President Ursula von der Leyen, Evian (June 17, 2026)",
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
