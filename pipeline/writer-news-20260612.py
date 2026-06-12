#!/usr/bin/env python3
"""News writer for The Videshi — 2026-06-12 morning batch."""

import json, os, re, sys, time, uuid
from datetime import datetime, timezone

import requests

# ── ENV ──────────────────────────────────────────────────────────────────
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
load_env(os.path.expanduser("~/workspace/.env.pexels"))

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY   = os.environ.get("PEXELS_API_KEY", "")

HEADERS_SB = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

UA = "TheVideshi/1.0 (thevideshi.com)"

# ── IMAGE HELPERS ────────────────────────────────────────────────────────
def fetch_wikipedia_person_image(person_name):
    encoded = person_name.replace(" ", "_")
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA}, timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:100]}")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia error for '{person_name}': {e}")
    return None


def fetch_wikimedia_commons(query, limit=5):
    """Search Wikimedia Commons. Returns list of image URLs."""
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": "1200",
        "format": "json",
    }
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params, headers={"User-Agent": UA}, timeout=15,
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for p in pages.values():
                ii = p.get("imageinfo", [{}])[0]
                url = ii.get("thumburl") or ii.get("url")
                mime = ii.get("mime", "")
                w = ii.get("width", 0)
                if url and "image" in mime and w >= 400:
                    results.append(url)
            if results:
                print(f"  ✓ Commons found {len(results)} images for '{query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Commons error for '{query}': {e}")
    return []


def fetch_pexels(query, per_page=5):
    """Search Pexels for landscape/editorial photos. Returns list of image URLs."""
    if not PEXELS_KEY:
        return []
    try:
        r = requests.get(
            "https://api.pexels.com/v1/search",
            params={"query": query, "per_page": per_page, "orientation": "landscape"},
            headers={"Authorization": PEXELS_KEY},
            timeout=10,
        )
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            urls = [p["src"]["large2x"] for p in photos if p.get("src", {}).get("large2x")]
            if urls:
                print(f"  ✓ Pexels found {len(urls)} images for '{query}'")
            return urls
    except Exception as e:
        print(f"  ⚠ Pexels error for '{query}': {e}")
    return []


def validate_image(url):
    """Check image URL returns HTTP 200 with image content > 5KB."""
    try:
        r = requests.head(url, headers={"User-Agent": UA}, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Try GET for servers that don't support HEAD properly
        if r.status_code != 200 or "image" not in ct:
            r2 = requests.get(url, headers={"User-Agent": UA}, timeout=10, stream=True, allow_redirects=True)
            ct2 = r2.headers.get("Content-Type", "")
            chunk = r2.raw.read(6000)
            r2.close()
            if r2.status_code == 200 and "image" in ct2 and len(chunk) > 5000:
                return True
    except Exception:
        pass
    return False


# ── SUPABASE INSERT ──────────────────────────────────────────────────────
def insert_article(article):
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS_SB,
        json=article,
        timeout=20,
    )
    if r.status_code in (200, 201):
        data = r.json()
        if isinstance(data, list) and data:
            print(f"  ✅ Inserted: {data[0].get('headline','?')[:80]}")
            return data[0]
        print(f"  ✅ Inserted (raw): {r.text[:120]}")
        return data
    else:
        print(f"  ❌ Insert failed ({r.status_code}): {r.text[:300]}")
        return None


# ── ARTICLE DEFINITIONS ─────────────────────────────────────────────────

def article_1():
    """Trump-Iran deal — Strait of Hormuz to reopen — India impact."""
    print("\n═══ Article 1: Trump-Iran Deal / Strait of Hormuz ═══")

    # Image: Trump — Wikipedia
    img_url = fetch_wikipedia_person_image("Donald Trump")
    img_caption = "US President Donald Trump at the White House"
    img_attr = "Wikimedia Commons"

    # If Wikipedia fails, try Commons
    if not img_url or not validate_image(img_url):
        commons = fetch_wikimedia_commons("Strait of Hormuz oil tanker")
        for c in commons:
            if validate_image(c):
                img_url = c
                img_caption = "Oil tankers near the Strait of Hormuz, a critical global energy route"
                img_attr = "Wikimedia Commons"
                break

    if not img_url or not validate_image(img_url):
        pexels = fetch_pexels("oil tanker ocean shipping")
        for p in pexels:
            if validate_image(p):
                img_url = p
                img_caption = "An oil tanker at sea — the Strait of Hormuz carries a fifth of the world's oil supply"
                img_attr = "Pexels"
                break

    slug = "trump-iran-deal-signing-weekend-strait-hormuz-reopen-india-oil-rupee-20260612"

    body = """Trump said the words India has been waiting to hear since February: "It should be done pretty quickly."

On Thursday evening, the US president cancelled planned strikes on Iran and announced that a peace agreement was essentially finalised. Vice President JD Vance could fly to Europe as soon as this weekend for a signing ceremony. The Strait of Hormuz, Trump said, "will officially open as soon as we sign."

If that happens, it would end one of the most disruptive energy crises in a generation — one that has cost the global economy an estimated 13 million barrels per day in lost Middle East exports, pushed Brent crude above $93, sent the Indian rupee to record lows, and killed three Indian sailors this week alone.

## What the Deal Reportedly Covers

Trump told reporters in the Oval Office that the deal means "Iran will never have a nuclear weapon." He said discussions had been "approved by all parties involved, including the United States, Israel, Saudi Arabia, UAE, Qatar, Turkey, Pakistan, Bahrain, Kuwait, Jordan, Egypt, and others."

The naval blockade of Iranian ports will remain in effect until the documents are signed. Qatar's Sheikh Tamim acknowledged "progress in the proposals under discussion" but stopped short of confirming a done deal. Iran's Foreign Ministry spokesperson Esmaeil Baghaei said Tehran had "not yet made a final decision" and would not compromise on its red lines.

## What It Means for India

The stakes for New Delhi could not be higher. India is the world's third-largest oil importer, and the closure of the Strait of Hormuz since early March has forced refiners to scramble for alternative supplies from Latin America, Africa, and the UAE's Fujairah storage facilities.

**Oil prices are already falling.** Brent crude dropped 2.9% to $90.38 on Thursday and continued sliding to $89.17 in Asian trade on Friday — its lowest in two months. West Texas Intermediate fell below $86. If a deal holds, traders expect oil to test the low $80s, which would be a massive reprieve for India's import bill and the rupee.

**The rupee is expected to rally.** Traders are calling for the currency to open at 95.25-95.30 on Friday, recovering from Thursday's close of 95.76. The Reserve Bank of India has already rolled out concessional swap facilities and incentivised NRI deposits to attract dollar inflows. A durable oil decline would supercharge those efforts.

**Indian sailors remain at risk until the ink is dry.** Three Indian sailors died this week when the US struck the tanker Settebello off Oman. A third tanker, the Jalveer, was hit on Thursday. India's foreign ministry has demanded the attacks "cease and end." More than 300,000 Indian seafarers work in global shipping fleets, and many transit the Gulf.

## The Catch

Trump has signalled imminent deals before. In April, a ceasefire was announced with fanfare — it lasted weeks before both sides resumed strikes. Iran's IRGC declared the Strait "closed to all vessels" just hours before Trump's about-face on Thursday. The market rallied, but retail investors on Stocktwits remained bearish, sceptical that the deal would hold.

As one Reuters analyst put it: "This could, of course, be yet another false dawn."

## Why This Matters for NRIs

For the 18 million Indians living abroad, especially the 700,000-plus in the Gulf states, the war has been a daily reality — from rising food prices and disrupted flights to anxiety over family members working in maritime and energy sectors. A deal that reopens the Strait and brings oil below $80 would ease inflation globally, strengthen the rupee, and make remittances more valuable.

But until JD Vance lands in Europe with a pen, India is watching the fine print — and keeping its agencies on "heightened alert."

*Sources: Reuters, Wall Street Journal, New York Post, MarketWatch, Associated Press*"""

    return {
        "headline": "Trump Says Iran Deal Is 'All Wrapped Up.' India Is Not Celebrating Yet.",
        "subheadline": "The US president says a signing could come this weekend and the Strait of Hormuz will reopen. Oil has already crashed below $87. But Tehran says it has not agreed to anything.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "geopolitics",
        "status": "review",
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": img_caption,
        "image_attribution": img_attr,
        "diaspora_angle": "A deal reopening the Strait of Hormuz would crash oil prices, strengthen the rupee, ease inflation for NRIs in the Gulf, and reduce the risk to 300,000 Indian seafarers working in global shipping.",
        "sources": ["Reuters", "Wall Street Journal", "New York Post", "MarketWatch", "Associated Press"],
        "published_at": datetime.now(timezone.utc).isoformat(),
    }


def article_2():
    """USCIS green card adjustment of status policy change."""
    print("\n═══ Article 2: USCIS Green Card Policy Change ═══")

    # Image: USCIS / immigration — Wikimedia Commons
    img_url = None
    img_caption = ""
    img_attr = ""

    commons = fetch_wikimedia_commons("USCIS immigration office United States")
    for c in commons:
        if validate_image(c):
            img_url = c
            img_caption = "A US Citizenship and Immigration Services facility"
            img_attr = "Wikimedia Commons"
            break

    if not img_url:
        commons2 = fetch_wikimedia_commons("US green card immigration")
        for c in commons2:
            if validate_image(c):
                img_url = c
                img_caption = "The US immigration system processes hundreds of thousands of green card applications annually"
                img_attr = "Wikimedia Commons"
                break

    if not img_url:
        pexels = fetch_pexels("US passport immigration documents")
        for p in pexels:
            if validate_image(p):
                img_url = p
                img_caption = "Immigration documents — USCIS has reframed in-country green card processing as 'extraordinary relief'"
                img_attr = "Pexels"
                break

    slug = "uscis-adjustment-of-status-extraordinary-relief-green-card-india-h1b-impact-20260612"

    body = """For decades, hundreds of thousands of immigrants in the United States — a disproportionate number of them Indian — have applied for green cards without leaving the country. A single USCIS memo has now put that entire process in jeopardy.

On May 21, US Citizenship and Immigration Services issued a policy memorandum that reframes "adjustment of status" — the process of applying for permanent residency from within the US — as a form of "extraordinary relief." The memo pushes applicants toward consular processing abroad, effectively telling people who have lived, worked, and paid taxes in America for years that they should go home and apply from there.

## What Changed

Under existing immigration law, people already in the US on valid work visas like the H-1B can file for a green card through adjustment of status. It is a standard, well-established pathway — not a loophole, not a special favour. Congress wrote it into the Immigration and Nationality Act.

The USCIS memo does not change the law. Instead, it reinterprets how officers should exercise "discretion" when evaluating these applications. By labelling the in-country pathway as extraordinary rather than routine, the memo signals to adjudicators that they should scrutinise applications more aggressively and consider denying cases that would previously have been approved on their merits.

"Officers may now look more heavily at discretionary factors in the person's case and could deny adjustment of status even where the person otherwise qualifies," said Vanessa Alonso, a San Antonio immigration attorney.

Javier Hidalgo, public affairs director at immigration nonprofit RAICES, was blunter: "If you want to communicate a directive to your asylum officers without explicitly saying it, that's basically what they've done."

## Why Indians Are Hit Hardest

India accounts for the largest share of the employment-based green card backlog in the United States. As of early 2026, more than 1.1 million Indian nationals are in the EB-2 and EB-3 queues, with wait times stretching beyond 50 years for some categories due to per-country caps.

These are not people gaming the system. They are software engineers, doctors, researchers, and business managers who entered on H-1B visas, were sponsored by their employers, and have been waiting — legally, patiently — for their turn. Many have US-born children, mortgages, and deep community ties.

The new memo threatens to upend their plans. If adjustment of status becomes functionally unavailable, applicants would need to travel to a US consulate abroad for an interview. That means:

**Longer waits.** US consulates are already severely backlogged. Adding hundreds of thousands of green card interviews to their dockets would extend processing times by years.

**Family separation.** Applicants would need to leave the US — potentially for months — while their cases are processed. Spouses and children could be stranded on either side.

**Job instability.** Leaving the US during the green card process can jeopardise employment authorisation, especially for those on H-1B extensions tied to pending applications.

**No consulates in some countries.** The memo acknowledges no exception for nationals from the 75-plus countries where US consular services are limited or nonexistent.

## The Legal Challenge

Immigration attorneys across the country are preparing court challenges. Farhad Sethna, an Ohio immigration lawyer, argued in the Akron Beacon Journal that the policy "raises serious concerns about discriminatory intent" and is "detrimental to the US national interest."

The legal argument is straightforward: Congress created adjustment of status as a co-equal pathway to permanent residency. An agency memo cannot unilaterally relabel it as exceptional. Legal experts expect injunctions to be filed within weeks.

## What You Can Do

Immigration attorneys are advising affected applicants to file their adjustment of status applications as quickly as possible, before the memo's full effects take hold. Those with pending cases should consult legal counsel about whether their applications might be affected. Anyone considering a trip abroad should weigh the risks carefully.

For the Indian diaspora in the US, this is not an abstract policy debate. It is a direct threat to the legal immigration pathway that millions have relied on — and a reminder that even playing by the rules offers no guarantee of stability.

*Sources: Akron Beacon Journal, San Antonio Current, USCIS Policy Memorandum (May 21, 2026), RAICES*"""

    return {
        "headline": "USCIS Just Made It Harder to Get a Green Card Without Leaving the US. Indians Have the Most to Lose.",
        "subheadline": "A new memo reframes adjustment of status as 'extraordinary relief' and pushes applicants toward consular processing abroad — a move that could add years to the wait for over a million Indians.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "immigration",
        "status": "review",
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": img_caption,
        "image_attribution": img_attr,
        "diaspora_angle": "Over 1.1 million Indian nationals in the US employment-based green card backlog face longer waits, family separation, and job instability if adjustment of status becomes functionally unavailable.",
        "sources": ["Akron Beacon Journal", "San Antonio Current", "USCIS", "RAICES"],
        "published_at": datetime.now(timezone.utc).isoformat(),
    }


def article_3():
    """ECB rate hike — war inflation goes global — NRI/India impact."""
    print("\n═══ Article 3: ECB Rate Hike / Global Inflation ═══")

    # Image: Christine Lagarde — Wikipedia
    img_url = fetch_wikipedia_person_image("Christine Lagarde")
    img_caption = "ECB President Christine Lagarde announced the rate hike on Thursday"
    img_attr = "Wikimedia Commons"

    if not img_url or not validate_image(img_url):
        commons = fetch_wikimedia_commons("European Central Bank Frankfurt building")
        for c in commons:
            if validate_image(c):
                img_url = c
                img_caption = "The European Central Bank headquarters in Frankfurt, Germany"
                img_attr = "Wikimedia Commons"
                break

    if not img_url or not validate_image(img_url):
        pexels = fetch_pexels("European Central Bank building Frankfurt")
        for p in pexels:
            if validate_image(p):
                img_url = p
                img_caption = "The European Central Bank — the first major central bank to raise rates in response to the Iran war energy shock"
                img_attr = "Pexels"
                break

    slug = "ecb-rate-hike-first-three-years-iran-war-inflation-india-nri-europe-impact-20260612"

    body = """The European Central Bank raised interest rates on Thursday for the first time in nearly three years. The decision tells you everything about where the Iran war is taking the global economy.

The ECB lifted its benchmark deposit rate by 25 basis points to 2.25%, a move that was widely expected but still marks a significant inflection point. It is the first rate increase since September 2023, and the first by any major central bank in direct response to the energy shock triggered by the US-Iran conflict.

"The war in the Middle East is generating inflation pressures," the ECB said in its statement, adding that the decision was "robust across a range of scenarios mapping out how the shock might evolve."

## The Numbers Behind the Decision

Eurozone inflation hit 3.2% in May, up sharply from 1.9% before the closure of the Strait of Hormuz in early March. Energy prices surged 11% year-on-year. The ECB raised its 2026 inflation projection to 3.0%, up from 2.6% in March, and lifted its 2027 forecast to 2.3%.

At the same time, growth is faltering. The ECB cut its 2026 GDP forecast to 0.8% from 0.9% and sees just 1.2% growth next year. The eurozone economy contracted 0.2% in the first quarter.

ECB President Christine Lagarde rejected the characterisation of this as an "insurance hike," insisting the decision was based on a thorough analysis. But she offered no forward guidance on further increases, saying only that the bank would "monitor attentively any further consequences of this major energy shock."

Financial markets now price in two more rate hikes over the coming year, potentially taking the deposit rate to 2.75% by early 2027.

## The Domino Effect

The ECB moved first, but it will not be the last. The Bank of Japan is widely expected to raise rates next week. The US Federal Reserve faces the most complex calculus — consumer inflation hit a three-year high of 4.2% in May, but rate hikes risk tipping a slowing economy into recession.

In the US, wholesale inflation (the Producer Price Index) also came in hotter than expected on Thursday. National average gasoline prices sit at $4.13 per gallon, up nearly 40% from pre-war levels.

The Bank of England, which meets next week, is expected to hold rates for now but faces growing pressure as UK energy costs continue to climb.

## What This Means for India

India's Reserve Bank has taken a different path — cutting rates and deploying unconventional tools to attract dollar inflows rather than fighting inflation with higher borrowing costs. Last week, the RBI announced concessional forex swap facilities for NRI deposits and allowed banks to offer leverage on foreign currency deposits, measures that have already prompted HDFC Bank, SBI, and others to raise NRI deposit rates by 200-300 basis points.

But the ECB's decision has consequences for India too.

**Higher global borrowing costs.** As major central banks tighten policy, the cost of external commercial borrowings for Indian companies rises. The RBI's swap facility partially offsets this, but the broader trend is unmistakable.

**Foreign capital outflows.** Higher eurozone rates make European bonds more attractive relative to emerging market assets. Foreign portfolio investors have already pulled a record $30.4 billion from Indian markets this year. The ECB hike adds another reason to stay away.

**Rupee pressure.** Every major central bank that raises rates while the RBI holds or cuts makes the interest rate differential less favourable for the rupee. The currency has already fallen 6% this year to record lows near 95.76.

## What NRIs in Europe Should Know

For the roughly 1.8 million people of Indian origin living in Europe, the rate hike has immediate personal implications.

**Mortgage costs.** Variable-rate mortgages across the eurozone will reprice higher. In countries like Ireland, the Netherlands, and Germany — where significant Indian professional communities have settled — monthly payments will increase.

**NRI deposit opportunity.** Indian banks are now offering 5.75-7.1% on three-to-five-year FCNR(B) deposits, with the RBI absorbing hedging costs. For NRIs earning in euros, converting to dollar deposits in Indian banks offers a meaningful yield premium over European savings accounts that still pay under 2%.

**Remittance maths.** A weaker rupee against the euro (if the ECB continues hiking while the RBI holds) makes remittances to India more valuable — a small silver lining for those sending money home.

The ECB's decision is a reminder that the Iran war is not just a geopolitical crisis contained to the Middle East. It is reshaping monetary policy, trade flows, and household budgets from Frankfurt to Mumbai to Mountain View.

*Sources: Reuters, Financial Times, FXStreet, European Central Bank, Reserve Bank of India*"""

    return {
        "headline": "The ECB Just Raised Rates for the First Time in Three Years. The Iran War Has Made Inflation Everyone's Problem.",
        "subheadline": "The European Central Bank hiked to 2.25% as eurozone inflation hit 3.2%. Indian banks are offering NRIs up to 7% on deposits. The Fed decides next week.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "economy",
        "status": "review",
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": img_caption,
        "image_attribution": img_attr,
        "diaspora_angle": "NRIs in Europe face higher mortgage costs, but can lock in 5.75-7.1% on Indian bank deposits — and the weakening rupee makes remittances more valuable.",
        "sources": ["Reuters", "European Central Bank", "FXStreet", "Financial Times", "Reserve Bank of India"],
        "published_at": datetime.now(timezone.utc).isoformat(),
    }


# ── MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    articles = [article_1, article_2, article_3]
    results = []

    for fn in articles:
        art = fn()
        if not art.get("image_url"):
            print(f"  ⚠ No valid image found for: {art['headline'][:60]}")
        result = insert_article(art)
        results.append(result)
        time.sleep(1)

    print("\n═══ SUMMARY ═══")
    for i, r in enumerate(results):
        if r:
            headline = r.get("headline", "?") if isinstance(r, dict) else "inserted"
            print(f"  {i+1}. ✅ {headline[:80]}")
        else:
            print(f"  {i+1}. ❌ FAILED")
