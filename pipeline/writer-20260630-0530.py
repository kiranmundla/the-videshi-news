#!/usr/bin/env python3
"""
Videshi News Writer — 2026-06-30 05:30 PDT run
Writes 2 articles:
1. Apple accuses India's CCI of 'copy-pasting' rivals' antitrust claims
2. India's rupee posts first quarterly gain in five quarters
"""

import json, os, sys, subprocess, urllib.parse, time, re, hashlib
from datetime import datetime, timezone

# --- Load env ---
def load_env(path):
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                k = k.replace('export ', '').strip()
                v = v.strip().strip('"').strip("'")
                os.environ[k] = v

load_env('~/.env.supabase')

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}
UA = "TheVideshi/1.0 (thevideshi.com)"


def curl_get(url, headers=None):
    """GET via curl (proxy-friendly)."""
    cmd = ["curl", "-sS", "-A", UA, "--max-time", "15"]
    if headers:
        for k, v in headers.items():
            cmd += ["-H", f"{k}: {v}"]
    cmd.append(url)
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return r.stdout


def fetch_wikipedia_person_image(person_name):
    """Fetch person image from Wikipedia REST API."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}"
    try:
        raw = curl_get(url)
        data = json.loads(raw)
        img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
        if img:
            print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
            return img
    except Exception as e:
        print(f"  ⚠ Wikipedia error for '{person_name}': {e}")
    return None


def fetch_wikimedia_commons(query, limit=5):
    """Search Wikimedia Commons for CC-licensed images."""
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": "1200",
        "format": "json"
    }
    qs = urllib.parse.urlencode(params)
    url = f"https://commons.wikimedia.org/w/api.php?{qs}"
    try:
        raw = curl_get(url)
        data = json.loads(raw)
        pages = data.get("query", {}).get("pages", {})
        results = []
        for pid, page in sorted(pages.items(), key=lambda x: x[1].get("index", 999)):
            ii = page.get("imageinfo", [{}])[0]
            thumb = ii.get("thumburl") or ii.get("url")
            width = ii.get("thumbwidth") or ii.get("width", 0)
            if thumb and width >= 400:
                results.append({
                    "url": thumb,
                    "title": page.get("title", ""),
                    "width": width
                })
        return results
    except Exception as e:
        print(f"  ⚠ Commons error for '{query}': {e}")
    return []


def fetch_pexels_image(query):
    """Search Pexels for a stock image. Only for generic topics, NOT persons."""
    api_key = os.environ.get("PEXELS_API_KEY", "")
    if not api_key:
        print("  ⚠ No PEXELS_API_KEY")
        return None
    encoded = urllib.parse.quote(query)
    url = f"https://api.pexels.com/v1/search?query={encoded}&per_page=3&orientation=landscape"
    try:
        raw = curl_get(url, headers={"Authorization": api_key})
        data = json.loads(raw)
        photos = data.get("photos", [])
        if photos:
            best = photos[0]
            img_url = best.get("src", {}).get("large2x") or best.get("src", {}).get("original")
            if img_url:
                print(f"  ✓ Pexels image: {img_url[:80]}...")
                return img_url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None


def verify_image_url(url):
    """Verify URL returns image >5KB."""
    cmd = ["curl", "-sS", "-o", "/dev/null", "-w", "%{http_code} %{size_download} %{content_type}", 
           "-A", UA, "--max-time", "10", url]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        parts = r.stdout.strip().split()
        if len(parts) >= 2:
            code = parts[0]
            size = float(parts[1])
            if code == "200" and size > 5000:
                return True
            print(f"  ⚠ Image verify failed: code={code}, size={size}")
    except Exception as e:
        print(f"  ⚠ Image verify error: {e}")
    return False


# Commons relevance gate (from AGENTS.md)
_COMMONS_STOP = {"the","a","an","and","or","for","in","on","at","to","of","is","are","was","were",
    "has","have","had","by","with","from","that","this","will","be","it","not","but","can","do",
    "its","new","how","why","what","who","when","where","just","over","also","into","after","may",
    "been","than","said","set","get","put","let","big","old","no","so","up","out","all","now",
    "one","two","day","year","time","long","made","make","back","first","last","very","most","more",
    "much","some","only","even","same","other","each","every","people","social","media","could",
    "would","should","about","their","they","them","these","those","here","there","such","like",
    "next","take","come","give","keep","tell","find","call","work","part","life","world","know",
    "says","says","upon","under"}

def commons_relevance_ok(title, headline, topic):
    """Check if Commons file title is relevant to the headline/topic."""
    title_lower = title.lower()
    headline_lower = headline.lower()
    
    # Extract distinctive keywords from headline+topic
    words = set(re.findall(r'[a-z]{4,}', f"{headline_lower} {topic.lower()}"))
    distinctive = words - _COMMONS_STOP
    
    if not distinctive:
        return True  # All-generic headline, don't over-filter
    
    # Require at least 1 distinctive keyword in file title
    for kw in distinctive:
        if kw in title_lower:
            return True
    return False


def insert_article(article):
    """Insert article into Supabase."""
    payload = json.dumps(article)
    cmd = [
        "curl", "-sS", "-X", "POST",
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        "-H", f"apikey: {SUPABASE_KEY}",
        "-H", f"Authorization: Bearer {SUPABASE_KEY}",
        "-H", "Content-Type: application/json",
        "-H", "Prefer: return=representation",
        "-d", payload
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    try:
        resp = json.loads(r.stdout)
        if isinstance(resp, list) and len(resp) > 0:
            print(f"  ✓ Inserted: {resp[0].get('slug', '?')}")
            return True
        else:
            print(f"  ✗ Insert response: {r.stdout[:300]}")
            return False
    except:
        print(f"  ✗ Insert error: {r.stdout[:300]}")
        return False


# ============================================================
# ARTICLE 1: Apple vs India CCI Antitrust
# ============================================================
def write_apple_cci_article():
    print("\n=== Article 1: Apple vs CCI Antitrust ===")
    
    # Image: Apple logo / Apple Park from Commons (not a person article)
    print("  Sourcing image...")
    
    # Try Commons first for Apple + antitrust / competition theme
    commons_results = fetch_wikimedia_commons("Apple Park headquarters Cupertino")
    img_url = None
    img_caption = None
    img_attr = None
    
    for c in commons_results:
        if commons_relevance_ok(c["title"], "Apple CCI antitrust India", "apple technology"):
            img_url = c["url"]
            img_caption = "Apple Park, the company's headquarters in Cupertino, California"
            img_attr = "Wikimedia Commons"
            print(f"  ✓ Using Commons: {c['title']}")
            break
    
    if not img_url:
        # Try Pexels for generic Apple/tech
        img_url = fetch_pexels_image("Apple store technology")
        if img_url:
            img_caption = "An Apple Store displaying the company's products"
            img_attr = "Pexels"
    
    if img_url and not verify_image_url(img_url):
        print("  ⚠ Image failed verification, trying alternate...")
        # Try another Commons search
        alt = fetch_wikimedia_commons("Competition Commission of India")
        for c in alt:
            if verify_image_url(c["url"]):
                img_url = c["url"]
                img_caption = "India's Competition Commission of India (CCI) regulates antitrust matters"
                img_attr = "Wikimedia Commons"
                break
        else:
            img_url = None
    
    slug = "apple-accuses-india-cci-copy-pasting-antitrust-app-store-phonpe-paytm-20260630"
    
    body = """Apple has accused India's competition regulator of building its antitrust case on the back of its rivals' legal filings rather than conducting an independent investigation — a claim that, if upheld, could upend one of the most closely watched tech-regulation battles in Asia.

In a June 25 submission to the Competition Commission of India (CCI) reviewed by Reuters, the iPhone maker alleged that the regulator's investigation team had engaged in "copy-pasting" submissions from opponents in the case, including Tinder-owner Match Group, Walmart-backed payments app PhonePe, and Indian fintech giant Paytm.

"The Director General made no effort whatsoever to independently verify or critically assess these statements, often parroting them verbatim," Apple said in the filing, its sharpest attack yet on the regulator's credibility.

## The Case Against Apple

The dispute traces back to 2021, when several entities — including the Alliance of Digital India Foundation (ADIF) and Match Group — filed complaints alleging that Apple's App Store policies restricted competition. Specifically, they accused Apple of mandating the use of its proprietary in-app payment system, which takes a commission of up to 30% on digital transactions, effectively locking developers into its ecosystem.

In 2024, CCI investigators privately concluded that Apple had engaged in "abusive conduct" on its iOS platform. The tech giant has consistently denied the allegations.

In its latest submission, Apple also claimed the CCI investigation "blindly replicated" a graphic on worldwide consumer spending on mobile apps drawn from a 2024 European Union ruling against the company — "even though India faced different market conditions." A Reuters review of the footnotes found both reports referenced data from Statista, an online research platform.

## Apple Calls Itself a 'Minuscule Player'

Apple's argument hinges partly on market share. The company said it holds under 6% of India's smartphone market — up from about 4% when the CCI began its probe — and described itself as a "minuscule player" in a market overwhelmingly dominated by Android-powered devices from Samsung, Xiaomi, and other manufacturers.

The company warned that "forced alterations to Apple's carefully designed App Store could disrupt its integrated business model" and that "the imposition of remedies would create regulatory uncertainty and could deter investments in India's digital economy."

It also objected to the CCI's stance on penalties. The regulator maintains that any fine can be calculated based on Apple's global turnover, while Apple argues the penalty should reflect only its relevant revenue within India — a difference that could amount to billions of dollars.

## Why Google's Playbook Matters

Apple is not the first tech giant to challenge the CCI's methods. In 2023, Alphabet's Google made similar arguments during its own antitrust battle, claiming that Indian investigators had copied parts of a European ruling. The CCI rejected the charge — "We have not cut, copy and pasted," it said at the time — and ultimately forced Google to make significant changes to how it promoted its Android operating system in India.

That precedent does not bode well for Apple's defence, though legal observers note the company's significantly smaller market share in India could differentiate its case.

Senior CCI officials are scheduled to hold a closed-door hearing with all parties on July 21, a session that could set the direction for the case through the remainder of the year.

## What This Means for the Diaspora

For the tens of thousands of Indian-origin professionals working at Apple, Google, and other Big Tech firms in the United States, the case highlights how their employers' business models are increasingly colliding with India's growing regulatory assertiveness. The CCI's willingness to take on the world's most valuable company signals that India intends to write its own rulebook for the digital economy — one that could reshape how app stores, digital payments, and platform ecosystems operate in the world's most populous nation.

The outcome could also reverberate through India's vibrant startup ecosystem. Homegrown apps like PhonePe and Paytm — both of which feature prominently in the case — have long argued that Apple's 30% commission makes it prohibitively expensive for Indian developers to build sustainable businesses on iOS. A ruling against Apple could open the door to alternative payment systems and lower fees, potentially levelling the playing field for Indian startups competing on a global stage.

*Sources: Reuters, 9to5Mac, MacRumors, Inc42, Analytics Insight*"""

    article = {
        "headline": "Apple Calls India's Antitrust Case Against It 'Copy-Pasted.' The Regulator Has Heard That Before.",
        "subheadline": "In its sharpest filing yet, Apple accuses the CCI of lifting rivals' claims verbatim instead of running its own investigation. Google tried the same argument — and lost.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "tech",
        "status": "review",
        "is_editorial": False,
        "sources": json.dumps(["Reuters", "9to5Mac", "MacRumors", "Inc42", "Analytics Insight"]),
        "image_url": img_url,
        "image_caption": img_caption,
        "image_attribution": img_attr,
        "diaspora_angle": "Indian-origin tech professionals at Apple and Google face scrutiny of their employers' practices, while Indian startups like PhonePe and Paytm push for fairer app store rules that could reshape India's digital economy.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }
    
    if not img_url:
        print("  ⚠ No image found, article will have null image")
        article["image_url"] = None
        article["image_caption"] = None
        article["image_attribution"] = None
    
    return insert_article(article)


# ============================================================
# ARTICLE 2: Rupee's First Quarterly Gain in Five Quarters
# ============================================================
def write_rupee_quarterly_article():
    print("\n=== Article 2: Rupee Quarterly Gain ===")
    
    # Image: Indian rupee notes/coins from Commons
    print("  Sourcing image...")
    
    commons_results = fetch_wikimedia_commons("Indian rupee banknote currency")
    img_url = None
    img_caption = None
    img_attr = None
    
    for c in commons_results:
        if commons_relevance_ok(c["title"], "Indian rupee quarterly gain", "rupee currency"):
            img_url = c["url"]
            img_caption = "Indian rupee banknotes — the currency posted its first quarterly gain since early 2025"
            img_attr = "Wikimedia Commons"
            print(f"  ✓ Using Commons: {c['title']}")
            break
    
    if not img_url:
        img_url = fetch_pexels_image("Indian rupee currency notes")
        if img_url:
            img_caption = "Indian rupee banknotes — the currency logged its best quarterly performance in over a year"
            img_attr = "Pexels"
    
    if img_url and not verify_image_url(img_url):
        print("  ⚠ Image failed verification")
        img_url = None
    
    slug = "india-rupee-first-quarterly-gain-five-oil-crash-goldman-upgrade-nri-remittance-20260630"
    
    body = """Three months ago, the Indian rupee was in freefall. It had tumbled to a record low near 97 against the dollar, oil was trading above $120 a barrel, and the Reserve Bank of India was burning through foreign exchange reserves at a pace that alarmed traders and policymakers alike.

On Tuesday, as the June quarter drew to a close, the rupee settled at 94.66 per dollar — modestly lower on the day, but up roughly 0.2% for the quarter. It is the currency's first quarterly gain since March 2025, ending a streak of four consecutive quarters of depreciation that had wiped out years of relative stability.

## What Changed

The turnaround has three distinct drivers, each reinforcing the others.

**Oil's dramatic retreat.** Brent crude, which had surged past $126 a barrel in April on fears that the Iran conflict would permanently disrupt shipping through the Strait of Hormuz, fell to about $73 on Tuesday — a drop of more than 42% from its peak. The fragile interim peace deal between the United States and Iran, which halted direct attacks and reopened partial shipping access, was the catalyst. For oil-import-dependent India, which buys more than 80% of its crude from overseas, the relief has been immediate and significant.

**A policy blitz from New Delhi and the RBI.** The government scrapped the 12.5% long-term capital gains tax and a 20% withholding tax on bond interest income for foreign investors earlier this month. The RBI extended a subsidised forex swap facility for banks' overseas borrowings and broadened the pool of securities eligible under the Fully Accessible Route to include longer-dated sovereign debt. The combined effect: a record $3 billion of net foreign investment into Indian government bonds in June alone — more than the entire January-to-May period combined.

**Goldman Sachs upgrades India.** Citing the improved macro backdrop, Goldman Sachs raised its 2026 growth forecast for India by 30 basis points, lowered its inflation projection by 20 basis points, and now expects a balance of payments surplus of 0.7% of GDP — a sharp reversal from the deficit it had forecast just weeks earlier.

## The Remittance Equation

For the roughly 18 million Indians living abroad, the rupee's trajectory is more than a macroeconomic data point. Every percentage point swing in the exchange rate translates directly into the purchasing power of the money they send home.

At the rupee's nadir near 97 in May, a $1,000 remittance bought about ₹97,000. At Tuesday's close of 94.66, the same transfer fetches about ₹94,660 — a difference of roughly ₹2,340, or about $25. Over a year of regular monthly transfers, that adds up.

The RBI's aggressive push to attract NRI deposits has added another dimension. Indian banks are now offering rates as high as 7.5% on foreign-currency non-resident (FCNR) deposits, up from about 5% just months ago. The combination of a stabilising currency and higher deposit rates has created what bankers describe as the most attractive inflow proposition for NRIs in years.

## Caveats and Risks

Traders caution that the rupee's gains are fragile. The dollar index rose 0.2% on Tuesday to 101.3, and expectations that the Federal Reserve will maintain a hawkish bias amid elevated U.S. inflation could keep the greenback firm.

"Investors are betting that labour market resilience will mean that the Fed will keep a hawkish bias intact for the next several quarters," DBS analysts said in a note.

India's monsoon deficit — rainfall is running 42% below normal for the season — looms as a domestic risk, with implications for food prices, rural demand, and the inflation outlook. If July rains do not pick up substantially, the RBI's room to ease monetary policy will narrow.

Portfolio outflows also remain a concern. Foreign investors net sold more than $2 billion of Indian equities on a single day last week, and the IT sector has been particularly hard-hit, falling 9.6% in June on fears that Fed rate hikes and AI disruption will compress client spending.

Still, the quarter's trajectory tells a story of resilience. The Sensex gained 2.3% in June, banking stocks surged over 6%, and the Nifty 50 rose 1.4% — all while small-caps climbed 4%. India's stock market, like its currency, has confounded the bears who were calling for a deeper reckoning just three months ago.

"The combination of lower crude, rupee stability and measures to draw foreign inflows has improved sentiment and liquidity," said Ajit Banerjee, president and chief investment officer at Shriram Life Insurance. "Markets should look better from the second half if no new risks emerge."

*Sources: Reuters, Goldman Sachs Research, DBS, Barclays, RBI*"""

    article = {
        "headline": "The Rupee Just Posted Its First Quarterly Gain in Over a Year. Here's What It Took.",
        "subheadline": "Oil's 42% crash, a record $3 billion bond surge, and a Goldman Sachs upgrade pulled India's currency back from the brink. NRI wallets feel the difference.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "economy",
        "status": "review",
        "is_editorial": False,
        "sources": json.dumps(["Reuters", "Goldman Sachs Research", "DBS", "Barclays", "RBI"]),
        "image_url": img_url,
        "image_caption": img_caption,
        "image_attribution": img_attr,
        "diaspora_angle": "The rupee's quarterly gain directly affects the purchasing power of remittances sent by 18 million NRIs, while RBI measures offering up to 7.5% on FCNR deposits create the most attractive NRI inflow proposition in years.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }
    
    if not img_url:
        print("  ⚠ No image found, article will have null image")
        article["image_url"] = None
        article["image_caption"] = None
        article["image_attribution"] = None
    
    return insert_article(article)


# ============================================================
# Main
# ============================================================
if __name__ == "__main__":
    print(f"=== Videshi Writer Run: {datetime.now(timezone.utc).isoformat()} ===")
    
    results = []
    results.append(("Apple CCI Antitrust", write_apple_cci_article()))
    results.append(("Rupee Quarterly Gain", write_rupee_quarterly_article()))
    
    print("\n=== Summary ===")
    for name, ok in results:
        print(f"  {'✓' if ok else '✗'} {name}")
    
    failed = sum(1 for _, ok in results if not ok)
    if failed:
        print(f"\n⚠ {failed} article(s) failed")
        sys.exit(1)
    else:
        print(f"\n✓ All {len(results)} articles inserted successfully")
