#!/usr/bin/env python3
"""News writer for The Videshi — 2026-06-18 12:30 UTC run.

Story: The Federal Reserve, in Kevin Warsh's debut meeting as Chair on June 17,
2026, held the benchmark rate steady at 3.50%-3.75% in a unanimous 12-0 vote,
but flipped its outlook from dovish to hawkish: the new dot plot shows nine of
19 officials now expect at least one 25bp HIKE in 2026 (vs. March, when 12 of
19 expected cuts and none expected hikes). Warsh dropped forward guidance (a
terse 132-word statement), launched five "blue-ribbon" task forces to overhaul
Fed communications, the $6.7T balance sheet, data sources, jobs/productivity
(incl. AI), and inflation models. Inflation projected at 3.6% by end-2026 (US
CPI hit 4.2% in May). "We will deliver price stability," Warsh said.
Diaspora angle: a higher-for-longer (or hiking) Fed keeps the dollar firm and
US mortgage/borrowing costs elevated for the millions of Indian professionals
in the US, while simultaneously pressuring the rupee and shaping the returns
on NRI dollar deposits the RBI just sweetened to 7%. The dollar's strength vs
the rupee is the single biggest variable for remittances home.
Sources: TheStreet, Investopedia, NPR/WAMC, Fox Business, CoinCentral.
"""

import os
import subprocess
from datetime import datetime, timezone
import requests

UA = "TheVideshi/1.0 (thevideshi.com)"


def curl_download(url):
    try:
        out = "/tmp/_videshi_hero_news1230.jpg"
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
    # Wikipedia official portrait of Kevin Warsh (originalimage, full res).
    src = ("https://upload.wikimedia.org/wikipedia/commons/7/77/"
           "Official_portrait_of_Kevin_M._Warsh_%28cropped%29.jpg")
    img_bytes = curl_download(src)
    if img_bytes:
        pub = upload_to_supabase(img_bytes, "kevin-warsh-fed-chair-portrait-20260618.jpg")
        if pub and validate_get(pub):
            return pub
    if validate_get(src):
        return src
    return None


def article():
    print("\n=== Article: Warsh's first Fed meeting, hawkish turn ===")

    img_url = source_hero_image()
    if not img_url:
        print("  \u26a0 no valid hero image")

    slug = "warsh-fed-debut-rates-steady-hawkish-dot-plot-overhaul-nri-dollar-20260618"

    body = """The man Donald Trump hand-picked to cut interest rates just told the country, on his first day in the chair, that he is in no hurry to do any such thing. "Persistently high prices are a burden for the American people," Kevin Warsh said on Wednesday, fronting his debut press conference as chairman of the Federal Reserve. "This committee will deliver price stability." It was the language of an inflation hawk, not a rate-cutter — and for the millions of Indians whose financial lives straddle the dollar and the rupee, every word of it matters.

The Federal Open Market Committee voted 12-0 to hold the benchmark federal funds rate at 3.50%-3.75%, its first unanimous decision since June 2025. The hold itself was expected; markets had priced near-certain odds of no change. The surprise was the turn in the outlook. As recently as March, 12 of the Fed's 19 officials expected at least one rate cut in 2026 and not a single one penciled in a hike. The new "dot plot" released Wednesday flipped that picture on its head: nine of the 19 now expect at least one quarter-point increase this year, eight see no change, and only one still forecasts a cut.

## From insurance cuts to inflation watch

The reversal is the work of one thing above all: the war between the United States and Iran, and the energy-price shock it sent through the global economy. American consumer prices were up 4.2% in May from a year earlier, the highest reading in more than three years, and the Fed now projects inflation will still sit at 3.6% by the end of 2026 — well above its 2% target, which it has now missed for five straight years. The "insurance" rate cuts the Fed delivered in the closing months of 2025 to cushion a softening labour market are firmly in the rear-view mirror.

A tentative US-Iran deal to reopen the Strait of Hormuz has pulled oil back below $80 a barrel in recent days, but Warsh signalled the central bank is not ready to treat the relief as durable. Half the committee wants the option to raise rates before the year is out. Goldman Sachs Asset Management's Kay Haigh called the Fed's path to avoiding hikes "narrow," with "a high premium on the incoming inflation data." Bloomberg Economics went further, dropping its call for any 2026 cut entirely.

## A new chair who wants to rebuild the machine

Warsh, a 56-year-old lawyer and former Fed governor who resigned from the board in 2011, used his debut to signal that he intends to reshape the institution, not just steer it. He scrapped the Fed's forward guidance — the post-meeting statement ran a terse 132 words — and announced five "blue-ribbon" task forces of outside consultants to review the Fed's communications, its $6.7 trillion balance sheet, its data sources, the way it measures jobs and productivity (including the use of artificial intelligence), and the models it uses for inflation. Recommendations are due by year-end. He played down the hawkish dots as mere "estimations," joking that members submitted them "with pencils — those kind with big erasers."

## Why the diaspora should read the dots

For the Indian community in America, a Fed that leans toward higher-for-longer has a direct and double-edged effect. On one side, it keeps US borrowing costs elevated: mortgages, car loans, and credit lines stay expensive for the H-1B engineer in Dallas or the green-card-holding doctor in New Jersey weighing a home purchase. On the other, a firmer dollar — the natural consequence of a hawkish Fed — stretches further when sent home. Every cent the dollar gains against the rupee lifts the value of remittances, which Indians abroad send back to the tune of more than $100 billion a year, the largest such flow of any country on earth.

That same dollar strength, though, is exactly what New Delhi has been fighting. The rupee touched a record low near 97 to the dollar last month before the Reserve Bank of India rolled out measures to draw dollars back in, including reviving a 2013-style window to mobilise funds from non-resident Indians and doubling dollar-deposit rates for NRIs to around 7%. A Fed that holds firm or hikes makes those NRI deposits more attractive in absolute terms but also keeps the rupee under pressure — a tension that lands squarely on the diaspora's balance sheet.

The bottom line from Warsh's first meeting is that the era of cheap money many had penciled in for 2026 is, for now, cancelled. For Indians who earn in dollars and care in rupees, the new chair's promise to "deliver price stability" is less a slogan than a forecast for the cost of everything from a Bay Area mortgage to the money wired to parents in Pune."""

    return {
        "headline": "Trump's Pick to Cut Rates Just Signalled Hikes Instead. The NRI Dollar Hangs on It.",
        "subheadline": "In Kevin Warsh's debut as Fed chair, the central bank held rates steady but flipped its outlook from cuts to hikes \u2014 a hawkish turn that firms the dollar, raises US borrowing costs, and reshapes what the diaspora's money is worth back home.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "economy",
        "status": "review",
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": "Kevin Warsh, who chaired his first Federal Open Market Committee meeting as Federal Reserve chairman on June 17, 2026.",
        "image_attribution": "Wikimedia Commons",
        "diaspora_angle": "A hawkish Fed keeps the dollar firm and US borrowing costs high for Indians living in America, while pressuring the rupee and shaping returns on the 7% NRI dollar deposits the RBI just rolled out \u2014 directly affecting the value of the $100 billion-plus diaspora sends home each year.",
        "sources": [
            "TheStreet \u2014 Warsh Unveils Sweeping Fed Overhaul in Debut Meeting (June 17, 2026)",
            "Investopedia \u2014 Fed Keeps Interest Rates Steady as Warsh Announces Plans to Overhaul Operations (June 17, 2026)",
            "WAMC / NPR \u2014 Kevin Warsh debuts as Fed chair, holding interest rates steady (June 17, 2026)",
            "Fox Business \u2014 Federal Reserve leaves interest rates unchanged as Warsh era begins (June 17, 2026)",
            "Reuters \u2014 Indian rupee, oil and the Strait of Hormuz coverage (June 2026)",
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
