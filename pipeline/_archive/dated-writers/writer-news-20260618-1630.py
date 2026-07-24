#!/usr/bin/env python3
"""News writer for The Videshi — 2026-06-18 16:30 UTC run.

Story: The US-Iran war officially ended — Trump and Pezeshkian signed the
memorandum of understanding on Wednesday June 17, bringing it into effect
two days early, calling for the immediate reopening of the Strait of Hormuz
and the lifting of the US blockade of Iranian ports. On Thursday June 18,
three Saudi-flagged supertankers carrying 6 million barrels crossed the
strait; Brent fell another ~2% to below $78, its lowest since the war began.
For India — the world's third-largest oil importer, ~90% import-dependent —
this is the lifting of the single biggest macro headwind of 2026: the rupee
hit a six-week high (~94.29/$), FPIs turned net buyers after 13 straight
selling sessions, and economists are talking about revising FY27 GDP growth
back up to 6.9% and inflation back down to 4.6%.

Distinct from prior coverage: earlier articles covered the ANTICIPATION
(Strait reopening deal nearing, wholesale inflation hitting 9.68%, MPC's
breather). THIS story is the morning-after turnaround — war signed and in
effect, tankers actually crossing, oil at war-low, markets and rupee
reversing — and frames it through the NRI investor/remittance lens.

Diaspora angle: NRIs are the marginal investor and the dollar lifeline for
India. A stronger rupee, a reversing FPI tide, and easing inflation reshape
the calculus on FCNR-B deposits, equity exposure and remittance timing.

Sources: Reuters (rupee/markets/tankers), LiveMint (oil-stock impact, MPC).
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


def curl_download(url, out="/tmp/_videshi_hero_news1630.jpg"):
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
    # Wikimedia Commons: Bombay Stock Exchange at Dalal Street — the natural
    # visual anchor for a story about Indian markets and the rupee rallying.
    src = ("https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/"
           "BSE_building_at_Dalal_Street.JPG/1280px-BSE_building_at_Dalal_Street.JPG")
    img_bytes = curl_download(src)
    if img_bytes:
        pub = upload_to_supabase(img_bytes, "bse-dalal-street-iran-war-ends-rupee-20260618.jpg")
        if pub and validate_get(pub):
            return pub
    if validate_get(src):
        return src
    return None


def article():
    print("\n=== Article: Iran war ends, India's macro headwind lifts ===")

    img_url = source_hero_image()
    if not img_url:
        print("  \u26a0 no valid hero image")

    slug = "iran-war-ends-oil-crashes-rupee-rallies-india-nri-investors-20260618"

    body = """For more than three months, the war between the United States and Iran sat on the Indian economy like a stone. It pushed up the price of every barrel of oil the country imports, dragged the rupee toward record lows, and gave foreign investors one more reason to pull their money out of Mumbai. On Wednesday, that stone began to lift.

President Donald Trump and Iran's President Masoud Pezeshkian signed a memorandum of understanding to end the conflict, bringing the deal into force two days earlier than expected. It calls for the immediate reopening of the Strait of Hormuz \u2014 the narrow channel through which about a fifth of the world's oil moves \u2014 and the lifting of the US blockade on Iranian ports. By Thursday morning, three Saudi-flagged supertankers carrying six million barrels of crude were already sailing through the strait, and benchmark Brent crude had fallen another 2% to below $78 a barrel, its lowest level since the fighting began.

## Why this matters more to India than almost anyone

India imports close to 90% of the oil it burns, which makes it one of the most exposed major economies on earth to a Gulf supply shock. When Brent spiked to nearly $120 during the war, it widened India's trade deficit, fed into inflation, and weakened the rupee, which sank to 96.96 to the dollar on May 20. "India has been one of the worst affected countries by the war, and therefore we have most to gain," said Rohit Aggarwal of Ro Fund Management.

The reversal has been swift. The rupee climbed to 94.29 per dollar this week, its strongest since early May, before settling around 94.5. The Nifty 50 and the Sensex have strung together their best run in months, gaining around 4% in three sessions. Most telling of all, foreign portfolio investors \u2014 who had dumped a record $30.8 billion of Indian equities in 2026 and sold for 13 straight sessions \u2014 turned net buyers this week.

## The dividend the diaspora has been waiting for

For non-resident Indians, this is not an abstract macro story. NRIs are among the swing investors in Indian markets and the steady source of the dollar deposits that help fund the country's external account. The same forces that battered the rupee through the war \u2014 expensive oil, capital flight, a yawning current-account gap \u2014 are exactly the ones now going into reverse, and that changes the arithmetic for anyone abroad weighing where to park their money.

A stronger, steadier rupee cuts both ways for the diaspora. It makes each dollar of remittances buy fewer rupees back home, but it also signals that the high-yield bets India has been dangling \u2014 the dollar deposit rates banks doubled to around 7%, the FCNR-B accounts the Reserve Bank has been pushing \u2014 are now sitting on far firmer ground. The currency risk that made those returns look fragile a month ago has eased considerably.

## Economists are already revising the numbers up

When the RBI set policy on June 5, it cut its FY27 growth forecast to 6.6% from 6.9% and raised its inflation projection to 5.1% from 4.6%, explicitly blaming the war and elevated crude. With the conflict now over and oil falling, several strategists expect those revisions to flip. "Now with Brent crude sharply correcting to the $78 level, the macro headwind is out of the way," said V.K. Vijayakumar of Geojit Investments, who sees GDP growth climbing back toward 6.9% and corporate earnings growing 12% to 15% in FY27.

The relief reaches well beyond the trading screen. Lower crude eases costs across swathes of corporate India \u2014 paints, plastics, tyres, chemicals \u2014 and softens the imported-inflation pressure that had the RBI's rate-setters sounding so cautious. "The fact that your freight costs will come down, metal prices and chemical prices, all of that will start easing off a bit, reducing the risk of generalized inflation," said Gaura Sen Gupta, chief economist at IDFC First Bank.

## The caution that remains

No one is declaring the all-clear. The peace deal opens a 60-day window to negotiate a final settlement, and analysts are skeptical the two sides can resolve the hardest questions in that time. Israeli airstrikes continued in Lebanon even after Trump's signature, a reminder that the region's instability has not vanished. And India still faces its own home-grown risks, chief among them a monsoon forecast to come in weak this year.

But for a diaspora that has watched the rupee slide and Indian markets underperform their emerging-market peers all year, the message from this week is unmistakable. The single biggest external drag on India's economy in 2026 is fading, and the money \u2014 foreign and NRI alike \u2014 is beginning to flow back the other way."""

    return {
        "headline": "The Iran War Just Ended. India Had the Most to Lose \u2014 and Now the Most to Gain.",
        "subheadline": "With the war signed off and oil crashing below $78, the rupee has hit a six-week high and foreign money is flowing back into Mumbai. For NRI investors, the biggest macro headwind of 2026 is lifting.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "economy",
        "status": "review",
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": "The Bombay Stock Exchange building on Dalal Street in Mumbai, where Indian shares have rallied on the end of the Iran war.",
        "image_attribution": "Wikimedia Commons",
        "diaspora_angle": "NRIs are among the swing investors and dollar-deposit lifeline for India's markets; the end of the war is strengthening the rupee, reversing foreign outflows and easing inflation \u2014 reshaping the calculus on FCNR-B deposits, equity exposure and when to send money home.",
        "sources": [
            "Reuters \u2014 Rupee nearly flat as oil-led rally faces off against dollar demand; Fed verdict looms (June 17, 2026)",
            "Reuters \u2014 First tankers cross strait under Iran deal; Israeli strikes raise doubt in Lebanon (June 18, 2026)",
            "LiveMint \u2014 US-Iran ceasefire deal: How could falling oil prices impact the Indian stock market? (June 2026)",
            "LiveMint \u2014 US-Iran truce makes life easier for India's MPC, just a tad (June 2026)",
            "Reuters \u2014 Indian shares extend gains on US-Iran peace deal (June 2026)",
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
