#!/usr/bin/env python3
"""News writer for The Videshi — 2026-06-16 10:30 UTC run (RBI FCNR(B) NRI deposit rate surge)."""

import os
from datetime import datetime, timezone
import requests


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

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

HEADERS_SB = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

UA = "TheVideshi/1.0 (thevideshi.com)"


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
        f"{SUPABASE_URL}/rest/v1/p2_articles",
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


def article_fcnr():
    print("\n=== Article: RBI FCNR(B) NRI deposit rate surge ===")

    img_url = ("https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/"
               "article-images/rbi-fcnr-nri-deposits-20260616.jpg")
    img_caption = "The Reserve Bank of India headquarters in Mumbai, which is subsidising hedging costs to draw NRI dollar deposits."
    img_attr = "Wikimedia Commons"
    if not validate_get(img_url):
        print("  \u26a0 primary image failed validation")
        img_url = None

    slug = "rbi-fcnr-deposit-rates-jump-nri-dollar-deposits-7-percent-rupee-20260616"

    body = """For years, the foreign-currency deposit was the dull, slightly disappointing corner of every NRI's financial life. You parked dollars in an Indian bank, earned barely 3 percent, and told yourself the point was safety, not yield. That calculation has just been turned upside down. Indian banks have abruptly raised interest rates on dollar deposits for non-resident Indians to between 6 and 7.1 percent \u2014 more than double the old levels \u2014 and for once the bank, not the depositor, is carrying the currency risk.

The trigger is a set of measures the Reserve Bank of India unveiled on June 5 to halt the slide of the rupee, which is down about 6 percent this year and touched record lows in May, making it Asia's second-worst-performing currency. To pull dollars into the country, the central bank agreed to absorb the full hedging cost on fresh three-to-five-year Foreign Currency Non-Resident (Bank), or FCNR(B), deposits raised through September 30, and exempted them from the cash reserve and statutory liquidity requirements that normally lock up a slice of every deposit. Strip out those costs and banks can suddenly afford to pay NRIs far more.

## The numbers are striking

State Bank of India, the country's largest lender, lifted rates by as much as 300 basis points, now offering 5.25 to 5.75 percent on three-to-five-year tenures for deposits up to a million dollars, and up to 6 percent above that. HDFC Bank, the largest private lender, raised rates by 235 to 265 basis points to 6 percent. AU Small Finance Bank went furthest at 7.1 percent on three-year money, while Yes Bank set 7 to 7.1 percent across three-to-five-year terms. The jump is dramatic precisely because the old rates hovered around 3 percent.

For an NRI weighing where to keep dollar savings, the contrast with a US savings account or short-dated Treasury \u2014 and with the currency risk that usually shadows any India play \u2014 has rarely looked this favourable. The deposits are dollar-denominated, so you are repaid in dollars and shielded from a sinking rupee, and on FCNR(B) accounts the interest is exempt from Indian income tax for non-residents. The RBI itself is now eating the hedging cost that used to quietly erode the headline rate.

## Why India is courting NRI money

This is not generosity; it is need. India is fighting a weak balance of payments. Foreign portfolio investors pulled record sums out of Indian equities this year, net foreign direct investment has thinned to a trickle, and the Gulf conflict has pushed up the oil import bill. Diaspora money is the steadiest pillar left standing: India received nearly $138 billion in remittances in 2024, the most of any country in the world and roughly double Mexico's tally. Now the RBI wants the diaspora's savings too, not just its remittances. Officials and economists estimate the package could attract anywhere from $30 billion to $70 billion and lift the rupee toward the 92-93 range against the dollar. RBI Deputy Governor Rohit Jain has openly urged banks to step up mobilisation of these deposits.

The last time the central bank pulled a lever like this was 2013, during the Federal Reserve's "taper tantrum," when a concessional swap facility helped HDFC Bank alone raise $3.4 billion. The echo of that crisis-era playbook tells you how seriously Mumbai views the current pressure on the currency.

## The fine print NRIs should read

There are catches. The subsidised swap covers only US dollar deposits, so rates on pound, euro, Australian, Canadian and Singapore dollar FCNR accounts have not moved. The window is finite \u2014 the hedging support runs only to September 30, which is why banks are pushing hard now. And bankers warn of a churn problem: NRIs holding older, lower-rate FCNR(B) deposits may break them early to roll into the new higher-paying ones, which can trigger premature-withdrawal penalties and means the "fresh" inflows the RBI wants may partly be old money recycled rather than new dollars arriving.

For the diaspora, the practical takeaway is simple. If you hold idle dollars and have been ignoring Indian deposits because the yield was insulting, the math has changed for a limited time. A 6-7 percent return on a dollar deposit, with the currency risk underwritten by India's central bank and the interest tax-free in India, is the most attractive this product has looked in over a decade. Whether it lasts past September is the open question \u2014 and the reason the offers are landing in NRI inboxes with such urgency right now.

*Sources: Reuters, Mint, The Hindu Businessline*"""

    return {
        "headline": "Indian Banks Just Doubled Dollar Deposit Rates for NRIs to 7%. The RBI Is Footing the Risk.",
        "subheadline": "To defend a sliding rupee, the Reserve Bank is absorbing the hedging cost on three-to-five-year FCNR deposits \u2014 letting banks pay NRIs 6 to 7.1 percent on dollars, more than double the old rate. The catch: the window closes September 30.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "economy",
        "status": "review",
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": img_caption,
        "image_attribution": img_attr,
        "diaspora_angle": "NRIs can now earn 6-7.1% on dollar-denominated FCNR deposits in Indian banks \u2014 more than double the old rate, with the currency risk underwritten by the RBI and the interest tax-free in India \u2014 but only on US-dollar deposits booked before September 30.",
        "sources": ["Reuters", "Mint", "The Hindu Businessline"],
        "published_at": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    art = article_fcnr()
    wc = len(art["body"].split())
    print(f"  word count: {wc}")
    insert_article(art)
