#!/usr/bin/env python3
"""News writer for The Videshi — 2026-06-17 22:30 UTC run.

Story: The H-1B housing bust in the Dallas-Fort Worth suburbs. For a decade,
Indian tech workers on H-1B visas drove a historic housing boom in Collin
County boomtowns — Frisco, Prosper, Celina — buying up to 70% of new builds.
In the past year that buyer segment has collapsed to under 20-30%, driven by
the Trump administration's $100,000 H-1B fee, consular-processing shift,
tech layoffs, and Texas state-level crackdowns (Abbott's order barring public
agencies from new H-1B petitions until May 2027). Redfin: home prices in
Collin County suburbs fell ~9% YoY in February vs ~4% across the metro.
Celina's population tripled in 5 years; some owners now underwater, listing at
a loss, removing religious items to attract non-Indian buyers; some handing
back keys. A federal court struck down the $100k fee last week — uncertain
whether it revives demand.
Diaspora angle: a concrete, dollars-and-cents illustration of how US visa
policy is reshaping where and whether Indian families can put down roots.
(Bloomberg Big Take / Prashant Gopal, HousingWire, Propmodo, VisaVerge,
India Weekly — June 2026)
"""

import os
import subprocess
from datetime import datetime, timezone
import requests

UA = "TheVideshi/1.0 (thevideshi.com)"


def curl_download(url):
    try:
        out = "/tmp/_videshi_hero_news2230.jpg"
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
    # Wikimedia Commons: Frisco Square, Frisco TX — a flagship Collin County
    # boomtown development at the heart of the H-1B housing story. CC-licensed.
    src = ("https://upload.wikimedia.org/wikipedia/commons/"
           "b/ba/Frisco_June_2019_13_%28Frisco_Square%29.jpg")
    img_bytes = curl_download(src)
    if img_bytes:
        pub = upload_to_supabase(img_bytes, "frisco-texas-h1b-housing-bust-20260617.jpg")
        if pub and validate_get(pub):
            return pub
    if validate_get(src):
        return src
    return None


def article():
    print("\n=== Article: H-1B housing bust in Dallas suburbs ===")

    img_url = source_hero_image()
    if not img_url:
        print("  \u26a0 no valid hero image")

    slug = "h1b-visa-crackdown-dallas-suburbs-housing-bust-frisco-celina-prosper-indian-buyers-20260617"

    body = """For a decade, the boomtowns north of Dallas told one of the great immigrant success stories in America. In Frisco, Prosper and Celina, Indian software engineers on H-1B visas bought new four- and five-bedroom houses by the thousands, many with puja rooms and spice kitchens built in. Now those same suburbs are showing what happens when the people who powered a housing boom are forced to leave.

Home prices in the Collin County suburbs north of Dallas fell almost 9% in February from a year earlier, according to Redfin data, more than double the roughly 4% decline across the wider Dallas-Fort Worth metro. Builders who once sold the majority of their inventory to international buyers are now sitting on unsold homes, cutting prices and dangling incentives. The reversal is sharp enough that economists have a name for it: the H-1B housing bust.

## A boom built on one buyer group

The scale of the dependence is hard to overstate. Ted Wilson, principal at the Texas research firm Residential Strategies, told HousingWire that between 2021 and 2025, roughly 70% to 75% of new-home sales in Celina — about 40 miles north of Dallas — went to international buyers, many of them H-1B holders who had laid down roots in the area. By the end of last year, that segment had collapsed to just 15% to 20% of buyers.

The numbers behind the growth were staggering. Celina's population grew 276.8% between 2020 and 2025, from just over 16,000 residents to more than 64,000. Collin County recorded the largest percentage increase in Indian residents among large US counties, climbing to an average of more than 116,000 in the five years through 2024, up from 70,000 in the preceding period. For the four years ended September 2024, the Dallas-Fort Worth area received almost 32,000 new H-1B approvals — more than Silicon Valley, Seattle, San Francisco or Washington, and second only to New York.

## What changed

Several forces hit at once. The Trump administration's $100,000 fee on new overseas H-1B petitions made sponsoring a worker far costlier, while a shift toward consular processing injected fresh uncertainty into how long a worker can remain in the country while pursuing a green card. Tech layoffs and the rise of AI-driven automation thinned the ranks of the very engineers who fueled demand. And at the state level, Texas Governor Greg Abbott's order barred public agencies and universities from filing new H-1B petitions until May 31, 2027, narrowing a major hiring gateway.

The combined effect changed the math of buying a home. Families who once felt secure enough to take on an $800,000 mortgage now treat their immigration status as strictly temporary — and act accordingly.

## Homes on the market for the wrong reasons

The result is a different kind of housing signal than a normal slowdown. Homes are coming up for sale not because owners are trading up, but because immigration status and employer costs shifted within months. One homeowner who bought in late 2023 for $895,000 dropped his asking price to $873,000 and removed religious items from view to appeal to all buyer types, according to reporting by Bloomberg. Another buyer who financed an $800,000 home almost entirely with debt now owes more than the property is worth and may simply hand back the keys. An immigration lawyer in Dallas said more clients are facing long commutes, relocations to other cities, or returns to India.

Local builders, caught flat-footed, are offering upgrades and discounted mortgage rates to move inventory. The pullback also threatens the property-tax base that was supposed to fund the schools and roads planned during the five-year growth streak.

## A reprieve — but how much?

There may be a partial reprieve. Last week, a federal court in Massachusetts struck down the Trump administration's $100,000 H-1B fee, and the housing industry is watching closely to see whether the ruling revives a once-reliable segment of buyer demand. But the broader crackdown — consular processing, the Texas order, and the chilling effect on long-term planning — remains in place, and confidence is not restored by a single court decision.

For the diaspora, North Texas is the clearest illustration yet of how Washington's visa decisions ripple into the most personal choices a family makes: whether to buy a home, where to raise children, and whether to stay at all. The puja rooms and spice kitchens were never just amenities. They were a bet that this was home for good — and that bet is now being repriced, one listing at a time."""

    return {
        "headline": "Indian Tech Workers Built the Dallas Suburbs. Now the H-1B Crackdown Is Emptying Them.",
        "subheadline": "Home prices in the Collin County boomtowns north of Dallas have fallen nearly 9% as Indian H-1B buyers — once up to 75% of new-home sales — pull back amid the $100,000 visa fee, layoffs and a Texas crackdown.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "immigration",
        "status": "review",
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": "Frisco Square in Frisco, Texas, one of the Collin County boomtowns north of Dallas where Indian H-1B workers drove a decade-long housing surge.",
        "image_attribution": "Wikimedia Commons",
        "diaspora_angle": "North Texas is the clearest dollars-and-cents example yet of how US visa policy is reshaping where — and whether — Indian families can put down roots, with homes once bought as a permanent stake now being sold at a loss as workers face departure.",
        "sources": [
            "Bloomberg / The Big Take \u2014 How H-1B Restrictions Popped Dallas' Housing Bubble (reported by Prashant Gopal & Tanaz Meghjani, June 2026)",
            "HousingWire \u2014 Demand stop-loss: Can a court ruling revive H-1B buyer mojo? (June 2026)",
            "Propmodo \u2014 Visa Policy Shifts Trigger Home Price Declines in Fast-Growing Suburbs (June 2026)",
            "VisaVerge \u2014 2026 H-1B Visa Rule Changes: Impact on Texas Housing Market (June 2026)",
            "India Weekly \u2014 North Texas housing market feels impact as Indian H-1B workers face uncertainty (June 2026)",
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
