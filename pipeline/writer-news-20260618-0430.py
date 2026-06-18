#!/usr/bin/env python3
"""News writer for The Videshi — 2026-06-18 04:30 UTC run.

Story: The US and Iran signed a 14-point memorandum of understanding on
June 17, 2026 (announced at the G7 in Evian) to end the nearly four-month
war, lift the US naval blockade within 30 days, and reopen the Strait of
Hormuz with toll-free passage for commercial vessels for 60 days. Brent
crude has fallen ~25% from its early-June peak (~$101) to the high-$70s.
Diaspora angle: India imports ~80%+ of its crude, a fifth of the world's
oil moves through Hormuz, ~9 million Indians live and work in the Gulf,
and three Indian seafarers were just killed in a US strike on a tanker
off Oman. Cheaper oil eases India's import bill, inflation and rupee
pressure; the ceasefire restores safety for Indian mariners and Gulf
workers. Sources: Reuters, USA Today, Washington Examiner, The Sun,
NY Post, Hindu BusinessLine — all June 2026.
"""

import os
import subprocess
from datetime import datetime, timezone
import requests

UA = "TheVideshi/1.0 (thevideshi.com)"


def curl_download(url):
    try:
        out = "/tmp/_videshi_hero_news0430.jpg"
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
    # Wikimedia Commons: an oil tanker taking on crude in the Persian Gulf
    # (US Navy photo, public domain). Specifically relevant to a story about
    # Gulf oil shipping and the reopening of the Strait of Hormuz.
    src = ("https://upload.wikimedia.org/wikipedia/commons/thumb/8/84/"
           "US_Navy_051111-N-8163B-032_An_oil_tanker_docked_to_the_Al_Basrah_Oil_Terminal_"
           "%28ABOT%29_takes_on_crude_oil_in_the_Persian_Gulf.jpg/"
           "1280px-US_Navy_051111-N-8163B-032_An_oil_tanker_docked_to_the_Al_Basrah_Oil_Terminal_"
           "%28ABOT%29_takes_on_crude_oil_in_the_Persian_Gulf.jpg")
    img_bytes = curl_download(src)
    if img_bytes:
        pub = upload_to_supabase(img_bytes, "persian-gulf-oil-tanker-hormuz-deal-20260618.jpg")
        if pub and validate_get(pub):
            return pub
    if validate_get(src):
        return src
    return None


def article():
    print("\n=== Article: US-Iran deal reopens Strait of Hormuz ===")

    img_url = source_hero_image()
    if not img_url:
        print("  \u26a0 no valid hero image")

    slug = "us-iran-deal-reopens-strait-of-hormuz-india-oil-diaspora-relief-20260618"

    body = """The longest energy supply shock in modern history is ending, and India may be its quietest big winner. On Wednesday, on the sidelines of the G7 summit in Evian, France, the United States and Iran signed a 14-point memorandum of understanding to halt their nearly four-month war, lift the American naval blockade and reopen the Strait of Hormuz — the narrow waterway that carries roughly a fifth of the world's oil and that India depends on for the bulk of its crude.

"It's signed," President Donald Trump told reporters as he left a dinner with French President Emmanuel Macron at Versailles. Within hours, oil markets had already delivered their verdict: Brent crude slipped to the high-$70s a barrel on Thursday, down about 25 percent from its early-June peak above $101 and far below the roughly $144 it touched in April when the strait was choked off.

## What the deal actually does

The framework, hammered out over weeks with Pakistan acting as a key mediator, is a starting point rather than a finished peace. Under its terms, the U.S. will dismantle the naval blockade it imposed in April within 30 days, while Iran will arrange "safe passage of commercial vessels with no charge for 60 days" from the Persian Gulf to the Sea of Oman, beginning immediately as it clears mines and other hazards. Washington will waive sanctions on Iranian oil exports and unfreeze some Iranian assets, and the two sides will spend the next 60 days negotiating the harder questions — Iran's nuclear program and a proposed $300 billion reconstruction fund — that the document deliberately leaves open.

Critics have warned that the vague language around Hormuz, Lebanon and Iranian assets leaves room for fresh disputes, and shippers remain cautious: confidence to fully resume transit could take weeks, with insurers waiting for written guarantees before rates fall. Vessels that have sat idle in warm Gulf water for more than 100 days will need their algae-caked hulls scrubbed before they can sail at speed.

## Why the diaspora should care

For India, the stakes run deeper than a headline oil price. The country imports more than 80 percent of the crude it consumes, and the Gulf producers that feed its refineries — Saudi Arabia, Iraq, Kuwait, the UAE and Qatar — all ship through Hormuz. When the strait closed in late February, India faced a triple squeeze: surging crude prices, soaring shipping insurance premiums and freight rates, and the inflationary pressure that ripples through everything from diesel to cooking gas to fertiliser. A sustained drop in oil eases the import bill, cools inflation and takes pressure off a rupee that importers have been defending for months.

The human stakes are even rawer. An estimated nine million Indians live and work across the Gulf, and Indian nationals crew a large share of the world's merchant vessels — including those that ply Hormuz. That reality turned tragic just last week, when three Indian seafarers were killed in a U.S. strike on the tanker Settebello off the coast of Oman, prompting New Delhi to summon the American chargé d'affaires in protest. When Prime Minister Narendra Modi sat down with Trump at the G7, he raised the deaths directly, noting that hundreds of thousands of Indians work on ships worldwide. "Their safety is of utmost importance to us," Modi said, adding that he was confident "the issue of seafarers will receive the highest priority" as the agreement is implemented.

## The road ahead

The relief, if it holds, will not arrive overnight. Analysts at Société Générale estimate that even with a late-June reopening, meaningful normalisation of oil flows to Asian buyers may not materialise until September, once tankers sail back into the Gulf and shut-in fields restart. The International Energy Agency went further, cautioning that this year's crisis could flip into a glut by 2027 as Middle East barrels flood back to market.

For the millions of Indians whose livelihoods, savings and household budgets are tied to the Gulf — the oil that powers India's economy, the wages remitted home, the seafarers who keep the cargo moving — the signing in Evian is the first piece of unambiguously good news in months. The fine print is unfinished and the peace is fragile. But after a winter and spring of war, the lights along one of the world's most important shipping lanes are flickering back on."""

    return {
        "headline": "The US and Iran Just Signed a Deal to Reopen the Strait of Hormuz. India Has Quietly Been Waiting for This.",
        "subheadline": "A 14-point memorandum signed at the G7 ends a four-month war, lifts the US naval blockade and reopens the waterway that carries a fifth of the world's oil. For India \u2014 80% dependent on imported crude, with nine million citizens in the Gulf \u2014 cheaper oil and safer seas land squarely on the diaspora.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "geopolitics",
        "status": "review",
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": "An oil tanker takes on crude at the Al Basrah Oil Terminal in the Persian Gulf, the export region that feeds the bulk of India's oil imports through the Strait of Hormuz.",
        "image_attribution": "Wikimedia Commons",
        "diaspora_angle": "India imports over 80% of its crude through the Strait of Hormuz and has roughly nine million citizens working in the Gulf \u2014 including the seafarers killed off Oman last week \u2014 so a deal that reopens the strait and lowers oil prices eases India's inflation, rupee and remittance pressures all at once.",
        "sources": [
            "Reuters \u2014 Oil slips again as US, Iran sign peace deal (June 18, 2026)",
            "USA Today \u2014 What's in the US-Iran deal? Here's what to know about the agreement (June 2026)",
            "Washington Examiner \u2014 US and Iran digitally re-sign deal to end war and open Strait of Hormuz (June 17, 2026)",
            "Associated Press / Audacy \u2014 Trump has nothing but praise for Modi at G7 after tensions over US military strike, trade (June 17, 2026)",
            "The Hindu BusinessLine \u2014 Hormuz reopening to ease oil supply risks for India (June 2026)",
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
