#!/usr/bin/env python3
"""News writer for The Videshi — 2026-06-17 18:30 UTC run.

Story: The US Federal Reserve, in Kevin Warsh's first meeting as Chair, held
the federal funds rate at 3.50%-3.75% on June 17, 2026 (unanimous 12-0), but
its dot plot flipped hawkish: of 18 projections, 9 members now see a hike, 8 a
hold, only 1 a cut for the rest of 2026 — a sharp reversal from March, which
had implied a cut. Inflation remains roughly double the 2% target amid energy
shocks. Warsh signaled less forward guidance. Stocks fell, the dollar firmed.
Diaspora angle: a "higher-for-longer" dollar shapes NRI dollar/FCNR deposit
returns, US mortgage and student-loan costs for Indian families, the value of
remittances sent home, and the rupee's path.
(StockTitan, Investopedia, Reuters, USA Today, FXStreet — June 17, 2026)
"""

import os
import subprocess
from datetime import datetime, timezone
import requests

UA = "TheVideshi/1.0 (thevideshi.com)"


def curl_download(url):
    try:
        out = "/tmp/_videshi_hero_news1830.jpg"
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
    # Wikimedia Commons: Kevin Warsh at his swearing-in as Fed Chair, May 22, 2026
    # (US government / White House photo, public domain). Full-resolution original.
    src = ("https://upload.wikimedia.org/wikipedia/commons/f/ff/"
           "Federal_Reserve_Chair_Kevin_Warsh_delivers_remarks_at_his_swearing-in_ceremony_"
           "in_the_East_Room_of_the_White_House%2C_Friday%2C_May_22%2C_2026._%28Cropped%29.jpg")
    img_bytes = curl_download(src)
    if img_bytes:
        pub = upload_to_supabase(img_bytes, "kevin-warsh-fed-chair-swearing-in-20260617.jpg")
        if pub and validate_get(pub):
            return pub
    if validate_get(src):
        return src
    return None


def article():
    print("\n=== Article: Fed hawkish hold under Warsh — diaspora impact ===")

    img_url = source_hero_image()
    if not img_url:
        print("  \u26a0 no valid hero image")

    slug = "us-federal-reserve-warsh-first-meeting-hawkish-hold-dot-plot-hike-nri-dollar-20260617"

    body = """The US Federal Reserve did the expected on Wednesday and the unexpected in the same afternoon. It left interest rates exactly where they have been since December, then quietly told the world it may raise them next.

In Kevin Warsh's first meeting as Fed Chair, the Federal Open Market Committee voted unanimously, 12-0, to hold the benchmark federal funds rate in a range of 3.50% to 3.75%. Markets had priced that hold at roughly 97%, so the rate itself was never the story. The story was the dot plot.

## The forecast flipped from a cut to a hike

Every quarter, Fed policymakers submit anonymous projections for where they think rates should end the year. In March, the median dot still implied a cut in 2026. On Wednesday, that median flipped hawkish: of the 18 projections submitted, nine members now see room to hike before year-end, eight see rates holding steady, and only one sees a cut.

The reason is inflation that refuses to come down. The Fed described price growth as "elevated relative to the Committee's 2 percent goal" — it is running at roughly double the target — and tied part of that to supply shocks, including energy prices driven up by the conflict in West Asia. At the same time, the committee said job gains "have kept pace with the workforce" and unemployment "has changed little," removing the labour-market weakness that might otherwise argue for cuts.

"Economic activity is expanding at a solid pace despite elevated uncertainty," the statement said, before adding a blunt line that doubled as a mission statement for the new chair: "The Committee will deliver price stability."

## A new chair, a new style

The unanimous vote was itself a signal. At the April meeting the committee had split 8-4, its widest dissent in decades. Warsh, sworn in on May 22 after a 54-45 Senate confirmation, opened his tenure by pulling the room back together — and by trimming the script. Wednesday's statement was markedly shorter than April's, an early move toward Warsh's stated preference for less "forward guidance," the carefully calibrated hints that markets have leaned on for years.

Investors did not love what they heard. The S&P 500 fell about half a percent and the Nasdaq dropped close to 1% as traders absorbed a more hawkish stance than they had hoped for. The dollar, which softens when cuts loom, found a floor.

## Why the diaspora should care

For Indians in America and NRIs worldwide, a Fed that signals "higher for longer" reaches well beyond Wall Street.

The most immediate effect is on borrowing. US mortgage rates, auto loans, credit-card balances and private student loans all track the Fed's path. For the large community of Indian families buying first homes, financing education, or carrying H-1B-era debt, the prospect of rates staying elevated — or rising — means the cost of money in the US is not coming down soon.

The flip side is the dollar. A firmer dollar and high US yields make dollar-denominated savings more attractive, which is precisely the backdrop against which Indian banks have just lifted FCNR and NRE dollar-deposit rates to draw diaspora money home. A strong dollar also stretches the value of every remittance sent to family in India — flows that topped $138 billion last year, making India the world's largest recipient.

But there is a sting in the tail. A hawkish Fed tends to pressure emerging-market currencies, and the rupee, which had climbed to a six-week high this week on falling oil prices, gave up most of those gains as the decision landed. A weaker rupee helps NRIs converting dollars but raises the cost of imports for families back home and complicates the Reserve Bank of India's own balancing act.

## What to watch next

Warsh's first press conference was expected to offer less hand-holding than markets are used to, leaving them to read the data themselves. With the US-Iran interim peace deal easing the oil shock that helped push inflation up, the central question for the months ahead is whether fading energy prices cool inflation fast enough to take that projected hike off the table — or whether the dot plot was a warning the diaspora should plan around."""

    return {
        "headline": "The Fed Just Hinted Its Next Move Is a Hike, Not a Cut. The Diaspora's Dollars Hang on It.",
        "subheadline": "In Kevin Warsh's first meeting as chair, the Fed held rates but flipped its forecast hawkish — a shift that shapes NRI deposit returns, US mortgage costs, remittance values and the rupee all at once.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "economy",
        "status": "review",
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": "Kevin Warsh delivers remarks at his swearing-in as Federal Reserve Chair at the White House, May 22, 2026.",
        "image_attribution": "Wikimedia Commons",
        "diaspora_angle": "A 'higher-for-longer' Fed directly sets the dollar's strength, US borrowing costs for Indian families, the returns on NRI dollar deposits, the value of remittances sent to India, and the rupee's trajectory.",
        "sources": [
            "StockTitan \u2014 Fed Holds Rates at 3.50%-3.75% in June 2026, but the Dot Plot Flips Toward a Hike (June 17, 2026)",
            "Investopedia \u2014 Fed Meeting Today: Central Bankers Pencil In a Rate Hike For Later This Year (June 17, 2026)",
            "USA Today \u2014 Fed holds rates steady: Live updates on Kevin Warsh's first meeting as chair (June 17, 2026)",
            "Reuters \u2014 Rupee nearly flat as oil-led rally faces off against dollar demand; Fed verdict looms (June 17, 2026)",
            "FXStreet \u2014 Kevin Warsh opens first Fed meeting with rate hold expected (June 2026)",
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
