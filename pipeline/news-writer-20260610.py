#!/usr/bin/env python3
"""
News writer for The Videshi — June 10, 2026 evening batch
3 articles: H-1B fee ruling, Section 301 trade, India bond tax reforms
"""

import json
import os
import re
import subprocess
import sys
import time
import urllib.parse
from datetime import datetime, timezone

# Load env
env_path = os.path.expanduser("~/.env.supabase")
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            os.environ[key.strip()] = val.strip().strip('"').strip("'")

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

PEXELS_KEY = None
pexels_path = os.path.expanduser("~/.env.pexels") if os.path.exists(os.path.expanduser("~/.env.pexels")) else None
if pexels_path:
    with open(pexels_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                if "PEXELS" in key.upper():
                    PEXELS_KEY = val.strip().strip('"').strip("'")


def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    import requests
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None


def fetch_wikimedia_commons_images(search_query, limit=5):
    """Search Wikimedia Commons for CC-licensed images."""
    import requests
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": search_query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": "1200",
        "format": "json"
    }
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params,
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for page_id, page in pages.items():
                imageinfo = page.get("imageinfo", [{}])[0]
                url = imageinfo.get("thumburl") or imageinfo.get("url")
                if url and imageinfo.get("mime", "").startswith("image/"):
                    width = imageinfo.get("width", 0)
                    height = imageinfo.get("height", 0)
                    results.append({
                        "url": url,
                        "title": page.get("title", ""),
                        "width": width,
                        "height": height
                    })
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error for '{search_query}': {e}")
    return []


def fetch_pexels_image(query):
    """Search Pexels for a relevant image. Uses curl (Python urllib gets 403)."""
    if not PEXELS_KEY:
        return None
    try:
        cmd = [
            "curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
            f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=3&orientation=landscape"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            if photos:
                photo = photos[0]
                url = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("large")
                if url:
                    print(f"  ✓ Pexels image found for '{query}': {url[:80]}...")
                    return url
    except Exception as e:
        print(f"  ⚠ Pexels error for '{query}': {e}")
    return None


def validate_image_url(url):
    """Validate that an image URL returns HTTP 200 and is larger than 5KB."""
    if not url:
        return False
    # Check for banned sources
    banned = ["fbcdn.net", "cdninstagram.com", "lookaside.fbsbx.com", "_nc_ht=", "_nc_cat=", "ccb="]
    for b in banned:
        if b in url:
            print(f"  ✗ BANNED source detected: {b}")
            return False
    try:
        cmd = ["curl", "-sS", "-I", "-L", "--max-time", "10", url]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        headers = result.stdout.lower()
        if "200" in headers and "content-type: image" in headers:
            # Check size
            for line in headers.split("\n"):
                if "content-length:" in line:
                    size = int(line.split(":")[1].strip())
                    if size > 5000:
                        print(f"  ✓ Image validated: {size} bytes")
                        return True
                    else:
                        print(f"  ✗ Image too small: {size} bytes")
                        return False
            # No content-length but 200 + image type — likely okay (chunked)
            print("  ✓ Image validated (no content-length, but 200 + image type)")
            return True
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False


def insert_article(article):
    """Insert article into Supabase."""
    import requests
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    # Build sources as JSON string
    raw_sources = article.get("sources", [])
    if isinstance(raw_sources, list):
        sources_json = json.dumps([{"name": s} if isinstance(s, str) else s for s in raw_sources])
    else:
        sources_json = json.dumps(raw_sources)

    payload = {
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "body": article["body"],
        "slug": article["slug"],
        "category": article["category"],
        "vertical": article.get("vertical", "news"),
        "status": "review",
        "is_editorial": False,
        "image_url": article.get("image_url", ""),
        "image_caption": article.get("image_caption", ""),
        "image_attribution": article.get("image_attribution", ""),
        "sources": sources_json,
        "published_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/p2_articles",
            headers=headers,
            json=payload,
            timeout=15
        )
        if r.status_code in (200, 201):
            data = r.json()
            if isinstance(data, list) and data:
                art_id = data[0].get("id", "?")
            else:
                art_id = "?"
            print(f"  ✓ Inserted: {article['headline'][:60]}... (id={art_id})")
            return True
        else:
            print(f"  ✗ Insert failed ({r.status_code}): {r.text[:200]}")
            return False
    except Exception as e:
        print(f"  ✗ Insert error: {e}")
        return False


# ============================================================
# ARTICLE 1: H-1B $100K Fee Struck Down
# ============================================================
print("\n" + "="*60)
print("ARTICLE 1: H-1B $100K Fee Struck Down")
print("="*60)

# Image sourcing — this is about a judge/court ruling, try Wikipedia for Judge Sorokin or US District Court
# Better to search Commons for H-1B visa or US federal court
print("Sourcing image...")
img1_url = None
img1_caption = ""
img1_attribution = ""

# Try Wikimedia Commons for H-1B visa / US immigration court
commons_results = fetch_wikimedia_commons_images("H-1B visa United States immigration")
if commons_results:
    for r in commons_results:
        if validate_image_url(r["url"]):
            img1_url = r["url"]
            img1_caption = "US immigration and visa processing"
            img1_attribution = "Wikimedia Commons"
            break

if not img1_url:
    commons_results = fetch_wikimedia_commons_images("United States federal courthouse Boston")
    if commons_results:
        for r in commons_results:
            if validate_image_url(r["url"]):
                img1_url = r["url"]
                img1_caption = "US federal courthouse where the H-1B ruling was issued"
                img1_attribution = "Wikimedia Commons"
                break

if not img1_url:
    # Pexels fallback for generic visa/immigration scene (NOT about a named person)
    pexels_url = fetch_pexels_image("US visa immigration office")
    if pexels_url and validate_image_url(pexels_url):
        img1_url = pexels_url
        img1_caption = "US visa and immigration processing"
        img1_attribution = "Pexels"

article1 = {
    "headline": "A Federal Judge Just Killed Trump's $100,000 H-1B Fee. Congress Wants to Bring It Back.",
    "subheadline": "The ruling is a reprieve for Indian tech workers — but a Republican bill to codify the fee is already in motion, and the legal fight is headed to three appellate circuits.",
    "slug": "federal-judge-strikes-down-100k-h1b-fee-protect-act-congress-indian-workers-20260610",
    "category": "news",
    "vertical": "immigration",
    "image_url": img1_url or "",
    "image_caption": img1_caption,
    "image_attribution": img1_attribution,
    "sources": [
        "Associated Press",
        "Reuters",
        "Bloomberg Law",
        "Analytics Insight",
        "Daily Caller"
    ],
    "body": """A federal judge in Boston has struck down the Trump administration's $100,000 fee on new H-1B visa applications, calling it an unlawful tax that only Congress has the authority to impose.

U.S. District Court Judge Leo Sorokin sided with a coalition of 20 state attorneys general on Monday, ruling that the executive branch exceeded its authority and violated the Administrative Procedure Act. "The Court finds that the Policy imposes a tax on H-1B petitions without the requisite delegation by Congress," Sorokin wrote in his decision.

The ruling landed like a thunderclap across the Indian tech workforce in America. Nearly three-quarters of all H-1B approvals go to workers from India, and the $100,000 fee — introduced by Trump through a September 2025 proclamation — had effectively frozen the pipeline. Government data showed that by February 15 of this year, just 85 employers had actually paid the fee, down from tens of thousands of annual applications in prior years.

## What the Fee Did

Before the policy shift, sponsoring an H-1B worker cost employers between $2,000 and $5,000 depending on company size. Trump's proclamation raised that to $100,000 per application — a more than twentyfold increase that the administration justified as a way to prevent foreign workers from displacing Americans.

The states that sued — led by Massachusetts and California — argued the fee made it nearly impossible to recruit doctors, teachers, and university researchers. "Today's victory protects the integrity of the H-1B visa program as a tool to address severe labor shortages in vital industries," Massachusetts Attorney General Andrea Joy Campbell said.

The American Medical Association called the ruling "a victory for patients," noting that international medical graduates fill critical gaps in underserved and rural areas where physician shortages are most acute.

## The Legal Mess Is Just Beginning

Monday's decision directly contradicts an earlier federal court ruling in Washington, D.C., which upheld the fee after the U.S. Chamber of Commerce challenged it there. That case is now on appeal, with the higher fee still technically in effect until September 2026, when the proclamation is scheduled to expire. A third lawsuit — filed in San Francisco by religious groups and labor organisations — is still pending.

The result is a circuit split in the making. Three federal appellate courts may end up issuing conflicting rulings on the same fee, virtually guaranteeing the issue will land before the Supreme Court.

## Congress Is Already Moving

Within hours of the ruling, Republican Utah Rep. Mike Kennedy promoted the PROTECT Act, a bill that would codify the $100,000 fee at the congressional level — the exact fix the judge's ruling demands. Kennedy's legislation requires any H-1B applicant to pay "either prevailing rates or $100,000 at a base" and aims to compel companies to prioritise American-born workers before turning to foreign nationals.

"The ruling shows we needed somebody in Congress to actually take care of this," Kennedy told reporters.

The White House, meanwhile, expressed confidence the decision would be "reversed on appeal." The Department of Homeland Security called the ruling "blatant judicial activism."

## What This Means for Indian Workers

For the roughly 500,000 Indian nationals currently on H-1B visas — and the hundreds of thousands more waiting in the green card backlog — the ruling is meaningful but fragile. The fee remains in legal limbo across multiple courts, and the PROTECT Act could reimpose it through legislation that would survive the judicial challenge Judge Sorokin mounted.

The practical advice from immigration attorneys is unchanged: keep documentation current, monitor the July Visa Bulletin, and plan for the possibility that the fee returns in a new legal form before the year is out. The system is not fixed. But for the first time since September, the most punishing barrier to entry has a crack in it."""
}

print(f"Article 1 ready: {article1['headline'][:70]}...")
print(f"  Image: {'YES' if article1['image_url'] else 'NO'}")
print(f"  Word count: {len(article1['body'].split())}")


# ============================================================
# ARTICLE 2: India Rejects Section 301 Overcapacity Charge
# ============================================================
print("\n" + "="*60)
print("ARTICLE 2: India Rejects Section 301 Overcapacity Charge")
print("="*60)

# Image sourcing — about India trade / Amitabh Kumar
print("Sourcing image...")
img2_url = None
img2_caption = ""
img2_attribution = ""

# Try Wikipedia for USTR or India trade ministry
commons_results = fetch_wikimedia_commons_images("India United States trade meeting")
if commons_results:
    for r in commons_results:
        if validate_image_url(r["url"]):
            img2_url = r["url"]
            img2_caption = "India-US trade discussions"
            img2_attribution = "Wikimedia Commons"
            break

if not img2_url:
    commons_results = fetch_wikimedia_commons_images("India steel factory textile industry")
    if commons_results:
        for r in commons_results:
            if validate_image_url(r["url"]):
                img2_url = r["url"]
                img2_caption = "Indian steel and textile manufacturing"
                img2_attribution = "Wikimedia Commons"
                break

if not img2_url:
    pexels_url = fetch_pexels_image("India steel factory manufacturing")
    if pexels_url and validate_image_url(pexels_url):
        img2_url = pexels_url
        img2_caption = "Indian manufacturing and steel production"
        img2_attribution = "Pexels"

article2 = {
    "headline": "India Tells Washington: We Don't Have Overcapacity in Anything.",
    "subheadline": "As the US ramps up Section 301 investigations and proposes a 12.5% tariff tier for India, New Delhi is pushing back — with population math, cotton weather, and a trade deal that keeps slipping away.",
    "slug": "india-rejects-us-section-301-overcapacity-steel-textiles-trade-tariffs-20260610",
    "category": "news",
    "vertical": "politics",
    "image_url": img2_url or "",
    "image_caption": img2_caption,
    "image_attribution": img2_attribution,
    "sources": [
        "Reuters",
        "NBC Palm Springs / AP",
        "US Trade Representative"
    ],
    "body": """India's top trade negotiator pushed back on Wednesday against American allegations that the country is dumping excess steel and textiles into global markets, setting the stage for a sharpening confrontation as the US prepares to impose new tariffs under Section 301.

"Overcapacity is a country's perspective. We don't think we have overcapacity in anything," said Amitabh Kumar, India's additional trade secretary, responding to a US Trade Representative investigation that has named India among 16 countries accused of subsidising factories that overproduce beyond what their domestic markets can absorb.

The remarks came on the same day Washington released a sweeping Section 301 report covering 60 economies. The report proposes a minimum 10 percent tariff on goods from nations that have existing trade frameworks with the US — and a steeper 12.5 percent rate for countries that, in Washington's assessment, have failed to take even preliminary steps to eliminate forced labour from supply chains. India sits in the higher tier, alongside China, Japan, South Korea, and Brazil.

## The Overcapacity Argument

Washington's case against India rests on structural excess capacity in several industries: solar modules, petrochemicals, steel, and textiles. The US also points to India's $42 billion goods trade surplus with America in 2025 as evidence that Indian exports are displacing American production.

Kumar's rebuttal was blunt and demographic. India's per-capita textile consumption is among the lowest in the world, he said, particularly for man-made fibre and technical textiles. "This country has a hot climate, tropical climate. We wear cotton. How do we have overcapacity?"

On steel, Kumar noted that India is the world's second-largest producer but that per-capita consumption remains far below the global average. Output reflects development needs — roads, bridges, housing, metro systems — not a strategy to flood foreign markets.

Trade analysts say the overcapacity framing is strategic. Washington is using the threat of Section 301 tariffs to pressure India into opening its markets for American agricultural products, energy, and defence equipment — the same priorities that have dominated bilateral trade talks for years.

## The Tariff Timeline

The proposed tariffs are not immediate. The USTR has opened a public comment period that runs through July 6, 2026, followed by administrative hearings starting July 7. But the direction is clear: the US is rebuilding its tariff architecture around Section 301 — a legal mechanism with no statutory expiration dates or maximum percentage caps — after courts struck down earlier tariffs imposed under emergency powers.

For India, the 12.5 percent tier would compound the pain from existing tariffs and the broader economic drag from the Iran war, which has already lifted oil prices 30 percent, weakened the rupee, and forced the government to scramble for foreign currency.

## The Trade Deal That Keeps Slipping

New Delhi has been pushing for a bilateral trade deal that would give Indian exports preferential tariff rates versus competitors. But the negotiations have stalled repeatedly, clouded by the Section 301 investigations, disputes over agricultural market access, and the growing political cost of appearing soft on trade in either capital.

The irony is not lost on trade watchers. India's economy grew 7.8 percent in the March quarter — among the fastest in the world — and its domestic market is precisely the prize American exporters want access to. But the path to a deal runs through the same overcapacity allegations that Kumar spent Wednesday morning rejecting.

## What NRIs Should Watch

For the Indian diaspora in America, the Section 301 escalation has a direct pocketbook impact. A 12.5 percent tariff on Indian goods would raise prices on textiles, pharmaceuticals, and manufactured products that flow into the US market. Indian IT services, which are not covered by goods tariffs, remain unaffected for now — but the broader deterioration in the trade relationship raises the risk of future restrictions on services trade and visa access.

The public comment period closes July 6. The next round of formal hearings begins a day later. The window for de-escalation is narrow and closing."""
}

print(f"Article 2 ready: {article2['headline'][:70]}...")
print(f"  Image: {'YES' if article2['image_url'] else 'NO'}")
print(f"  Word count: {len(article2['body'].split())}")


# ============================================================
# ARTICLE 3: India Scraps Bond Taxes for Foreigners
# ============================================================
print("\n" + "="*60)
print("ARTICLE 3: India Scraps Bond Taxes for Foreigners")
print("="*60)

print("Sourcing image...")
img3_url = None
img3_caption = ""
img3_attribution = ""

# Try Wikimedia Commons for RBI or Indian bond market
commons_results = fetch_wikimedia_commons_images("Reserve Bank of India building Mumbai")
if commons_results:
    for r in commons_results:
        if validate_image_url(r["url"]):
            img3_url = r["url"]
            img3_caption = "Reserve Bank of India headquarters in Mumbai"
            img3_attribution = "Wikimedia Commons"
            break

if not img3_url:
    wiki_img = fetch_wikipedia_person_image("Reserve Bank of India")
    if wiki_img and validate_image_url(wiki_img):
        img3_url = wiki_img
        img3_caption = "Reserve Bank of India"
        img3_attribution = "Wikimedia Commons"

if not img3_url:
    commons_results = fetch_wikimedia_commons_images("Indian government bond market Bombay Stock Exchange")
    if commons_results:
        for r in commons_results:
            if validate_image_url(r["url"]):
                img3_url = r["url"]
                img3_caption = "Indian financial markets"
                img3_attribution = "Wikimedia Commons"
                break

if not img3_url:
    pexels_url = fetch_pexels_image("India financial district Mumbai stock exchange")
    if pexels_url and validate_image_url(pexels_url):
        img3_url = pexels_url
        img3_caption = "India's financial district in Mumbai"
        img3_attribution = "Pexels"


article3 = {
    "headline": "India Just Scrapped All Taxes on Foreign Bond Investments. A Billion Dollars Arrived in Three Days.",
    "subheadline": "The emergency reforms — zero withholding tax, zero capital gains — are India's bid to join the Bloomberg Global Aggregate Index and reverse $29 billion in foreign outflows.",
    "slug": "india-scraps-bond-tax-foreign-investors-bloomberg-index-billion-dollar-inflows-20260610",
    "category": "news",
    "vertical": "news",
    "image_url": img3_url or "",
    "image_caption": img3_caption,
    "image_attribution": img3_attribution,
    "sources": [
        "Reuters",
        "State Street Investment Management",
        "BNP Paribas Asset Management",
        "M&G Investments"
    ],
    "body": """India has eliminated all taxes on foreign investments in government bonds — scrapping both withholding and capital gains levies in a single stroke — and the money is already flowing in. More than $1 billion worth of Indian government debt was purchased by overseas investors in just three trading sessions after the announcement, compared to $1.6 billion in the entire year up to that point.

The reforms, unveiled on Friday as part of a broad emergency package, are designed to lure foreign capital back into an Indian debt market that has been hammered by the Iran war's oil shock, a weakening rupee, and $29 billion in foreign equity outflows since February.

"We believe that these changes are a game-changer for debt flows," said Jennifer Taylor, head of emerging market debt at State Street Investment Management, which manages about $5.6 trillion in assets globally.

## What Changed

The package goes well beyond tax cuts. Policymakers broadened the pool of government securities available to foreigners without investment limits, introduced incentives for banks to raise foreign currency deposits from non-resident Indians, and eased rules for Indian companies to tap overseas borrowings.

The measures are a direct response to the pressure on India's external balances. The country's oil-and-gas import bill jumped 53 percent in April alone, and before the reforms, HSBC had projected India's balance of payments deficit would balloon to $65 billion in fiscal 2027. Citi has since revised its forecast sharply, now expecting a $5 billion surplus — a $65 billion swing driven largely by the capital-account reforms.

Government bond yields have already fallen 10 to 30 basis points across the curve, with shorter maturities seeing the steepest declines.

## The Bloomberg Index Play

Investors say the reforms could prove even more consequential over the longer term by paving the way for India's inclusion in the Bloomberg Global Aggregate Index — the flagship global bond benchmark tracked by trillions of dollars in assets.

Bloomberg Index Services is expected to seek investor feedback later this month on whether Indian government bonds should be added. India's finance minister personally met with Reserve Bank of India officials ahead of the reforms to push for inclusion, according to a government official.

Niel Clement, portfolio manager for emerging market fixed income at BNP Paribas Asset Management (€1.6 trillion in assets), said the steps would "broaden opportunities for overseas investors, redirect flows to the onshore market, and provide a constructive boost to India's bid for inclusion."

M&G Investments, which manages £376 billion, said the tax exemptions have already boosted the near-term appeal of Indian government securities, and that Bloomberg index inclusion would be "a bigger driver of inflows" — similar to the transformative effect of India's entry into the JPMorgan emerging market debt index.

## The Risks That Remain

Not everyone is rushing in. Currency risk remains the elephant in the room. The rupee has fallen 5.86 percent this year, trailing only the Indonesian rupiah as Asia's worst performer, and the depreciation has eroded the carry appeal that typically draws foreign bond investors.

"The bigger issue for offshore investors is still the currency," said Rong Ren Goh, head of macro and thematics for Asian fixed income at Eastspring Investments. He added that many investors are waiting for clearer signs of rupee stability before raising allocations.

The broader backdrop is also challenging. Global interest-rate volatility is elevated, energy prices remain unpredictable as the Iran war enters its fourth month, and the Federal Reserve appears unlikely to cut rates anytime soon — with U.S. CPI data released Wednesday showing inflation at a three-year high of 4.2 percent.

## What This Means for NRIs

The reforms include specific incentives for non-resident Indians. Banks have been given concessional terms to mobilise NRI foreign currency deposits, which could translate into higher interest rates on FCNR and NRE accounts — a development already being flagged by Indian banks offering up to 7 percent on dollar deposits.

For NRIs with capital to deploy, the zero-tax regime on government bonds creates a new investment channel that did not exist a week ago. The question is whether the rupee stabilises enough to make the returns worth the currency risk — and whether Bloomberg's decision on index inclusion, expected in the coming weeks, provides the structural bid that turns a policy experiment into a permanent shift."""
}

print(f"Article 3 ready: {article3['headline'][:70]}...")
print(f"  Image: {'YES' if article3['image_url'] else 'NO'}")
print(f"  Word count: {len(article3['body'].split())}")


# ============================================================
# INSERT ALL ARTICLES
# ============================================================
print("\n" + "="*60)
print("INSERTING ARTICLES")
print("="*60)

articles = [article1, article2, article3]
success_count = 0
for i, art in enumerate(articles, 1):
    print(f"\n--- Article {i}: {art['headline'][:50]}...")
    if insert_article(art):
        success_count += 1
    time.sleep(1)

print(f"\n{'='*60}")
print(f"DONE: {success_count}/{len(articles)} articles inserted with status='review'")
print(f"{'='*60}")
