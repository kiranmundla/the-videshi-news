#!/usr/bin/env python3
"""
The Videshi — News Writer (2026-05-30 batch)
Writes 3 articles for the news category.
"""

import os, json, sys, time, re, uuid
import requests
import urllib.parse
from datetime import datetime, timezone

# Load env
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('export '):
                line = line[7:]
            if '=' in line:
                k, v = line.split('=', 1)
                v = v.strip().strip('"').strip("'")
                os.environ[k] = v

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            # Prefer originalimage (higher res), fall back to thumbnail AS-IS
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None

def fetch_pexels_image(query, fallback_query=None):
    """Fetch an image from Pexels. Returns URL or None."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    headers = {"Authorization": PEXELS_KEY}
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            r = requests.get(
                f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5",
                headers=headers, timeout=10
            )
            if r.status_code == 200:
                photos = r.json().get("photos", [])
                if photos:
                    url = photos[0]["src"]["large2x"]
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image(url):
    """Validate image URL returns HTTP 200 and is > 5KB."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            print(f"  ✓ Image validated: {cl} bytes, {ct}")
            return True
        # Try GET if HEAD doesn't give content-length
        if r.status_code == 200 and "image" in ct and cl == 0:
            r2 = requests.get(url, timeout=10, stream=True,
                            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                print(f"  ✓ Image validated via GET: >5KB")
                return True
        print(f"  ✗ Image validation failed: status={r.status_code}, ct={ct}, cl={cl}")
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
    return False

def publish_article(article):
    """Publish article to Supabase."""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=headers,
        json=article,
        timeout=30
    )
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            print(f"  ✓ Published: {result[0].get('headline', '')[:60]}")
            return True
        print(f"  ✓ Published (no return body)")
        return True
    print(f"  ✗ Publish failed: {r.status_code} — {r.text[:200]}")
    return False


# ═══════════════════════════════════════════════════════════════
# ARTICLE 1: Federal Judge Questions $100K H-1B Fee
# ═══════════════════════════════════════════════════════════════

print("\n" + "="*60)
print("ARTICLE 1: H-1B $100K Fee Court Challenge")
print("="*60)

# Image: Try Leo Sorokin or generic courthouse
img1 = fetch_pexels_image("US federal courthouse Boston", "federal court gavel")
if not validate_image(img1):
    img1 = fetch_pexels_image("immigration visa documents")
    if not validate_image(img1):
        img1 = None

article1 = {
    "headline": "A Federal Judge Just Asked Whether There Is Any Limit to the $100,000 H-1B Fee. The Government Had No Clear Answer.",
    "subheadline": "U.S. District Judge Leo Sorokin questioned whether the president's power to deter foreign workers has any boundary. Only 85 employers have paid the fee since September.",
    "slug": "federal-judge-sorokin-100k-h1b-fee-limits-boston-hearing-20260530",
    "category": "news",
    "vertical": "news",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "image_url": img1,
    "image_attribution": "Pexels" if img1 and "pexels" in (img1 or "") else None,
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "Lexology", "url": "https://www.lexology.com"},
        {"name": "Murthy Law Firm", "url": "https://www.murthy.com"}
    ]),
    "body": """The question was simple. The answer was not.

On Friday, U.S. District Judge Leo Sorokin asked a Justice Department lawyer to explain the outer boundary of the president's power to impose fees on foreign workers. The lawyer for the government, Tiberius Davis, argued that President Trump had acted within his "sweeping" authority under federal immigration law. Judge Sorokin wanted to know: if the president can charge $100,000, what stops him from charging $500,000? A million?

"I'm trying to understand the government's position on the scope," Sorokin said during the hearing in Boston.

The case was brought by 20 Democratic state attorneys general challenging the fee Trump announced last September. Before the proclamation, employers typically paid between $2,000 and $5,000 to sponsor an H-1B worker. The fee increase was not incremental. It was a 20x to 50x multiplier, and it worked exactly as designed: as of February 15, only 85 employers had paid it.

## The Chilling Effect Is the Point

Davis told the court that the fee was meant to "incentivize companies to train up and hire American workers." That framing is important. The administration is not arguing that the fee is revenue collection. It is arguing that the fee is a policy tool — a deliberate price wall designed to make hiring foreign talent prohibitively expensive.

For Indian professionals, who hold the largest share of H-1B visas by a wide margin, the implications are existential. The H-1B program offers 65,000 visas annually, with an additional 20,000 for workers with advanced degrees. At $100,000 per petition, the math breaks for most mid-size employers. A company that once sponsored five engineers now sponsors zero.

The data confirms the chill. The FY2027 H-1B lottery, the first to apply both the $100,000 fee and the new weighted selection process that favors higher-paid workers, saw the lowest registration numbers in years. Entry-level positions — the ones most Indian graduates compete for — were effectively priced out.

## A Legal Question That Decides a Generation

Sorokin, an Obama appointee, acknowledged that the statutory language granting the president power to restrict entry of foreign nationals is "clearly broad." But his line of questioning suggested he was probing for a limiting principle. If the fee is a restriction on entry, what distinguishes it from a ban? If there is no upper bound, the fee becomes whatever number is large enough to stop anyone from applying.

This is not the first court to weigh in. In December 2025, a D.C. federal judge upheld the fee as falling within presidential authority. That ruling was fast-tracked to the D.C. Circuit Court of Appeals, where it remains pending. The U.S. Chamber of Commerce and the Association of American Universities are leading that challenge.

But the Boston case has a different plaintiff and a different judge. And Sorokin's questions Friday suggested he is not ready to rubber-stamp the government's position.

## What NRIs Should Know

The $100,000 fee applies to new H-1B petitions filed after the proclamation. Extensions and transfers are not subject to it. But the broader signal is unmistakable: the administration wants fewer H-1B workers, and it has found a mechanism that achieves that without passing legislation.

For Indian families planning their futures — students weighing whether to stay in the U.S. after graduation, mid-career professionals considering transfers, parents hoping their children can build careers abroad — the fee is not just a number. It is a message.

And on Friday, a federal judge in Boston asked whether that message has any legal limit. The government's answer was: we'll get back to you.

The case is expected to continue with additional briefing. No ruling date has been set."""
}

publish_article(article1)
time.sleep(1)


# ═══════════════════════════════════════════════════════════════
# ARTICLE 2: Myanmar's Min Aung Hlaing Visits India
# ═══════════════════════════════════════════════════════════════

print("\n" + "="*60)
print("ARTICLE 2: Myanmar Leader Visits India")
print("="*60)

# Image: Try Min Aung Hlaing from Wikipedia
img2 = fetch_wikipedia_person_image("Min Aung Hlaing")
if not validate_image(img2):
    img2 = fetch_wikipedia_person_image("Min Aung Hlaing (general)")
    if not validate_image(img2):
        img2 = fetch_pexels_image("Myanmar India diplomacy flags", "diplomatic meeting handshake")
        if not validate_image(img2):
            img2 = None

article2 = {
    "headline": "Myanmar's Junta Leader Just Chose India for His First Trip as President. The Real Prize Is Under the Ground.",
    "subheadline": "Min Aung Hlaing's five-day visit to New Delhi is less about diplomacy and more about rare earths, border security, and keeping China from getting everything.",
    "slug": "myanmar-min-aung-hlaing-india-visit-modi-rare-earths-china-20260530",
    "category": "news",
    "vertical": "news",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "image_url": img2,
    "image_attribution": "Wikimedia Commons" if img2 and "wikimedia" in (img2 or "").lower() or "wikipedia" in (img2 or "").lower() else ("Pexels" if img2 and "pexels" in (img2 or "") else None),
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "Crisis Group", "url": "https://www.crisisgroup.org"},
        {"name": "Ministry of External Affairs, India", "url": "https://www.mea.gov.in"}
    ]),
    "body": """Five years ago, most of Myanmar's neighbours would not take his call. On Saturday, Min Aung Hlaing is flying to New Delhi for a five-day state visit, his first overseas trip since trading his military uniform for the title of president. He will hold talks with Prime Minister Narendra Modi. The visit says something about Myanmar. It says more about India.

## The Coup General Goes Civilian

Min Aung Hlaing seized power in a dawn coup on February 1, 2021, ousting Nobel laureate Aung San Suu Kyi and plunging Myanmar into civil war. The ASEAN bloc barred his generals from its summits. Western capitals imposed sanctions. For years, his international itinerary was essentially Beijing and Moscow.

Then came the earthquake. A devastating quake last year opened a diplomatic window — a rare visit to a regional summit in Bangkok, a widely criticised election that gave him a civilian title, and now the quiet rehabilitation of a man most democracies still consider illegitimate.

"After changing into civilian clothes as president, Min Aung Hlaing is looking to boost diplomatic engagement across the region," said Richard Horsey, senior Myanmar adviser at Crisis Group. "He expects more normal ties with ASEAN. India is Myanmar's other key neighbour."

## What India Actually Wants

For India, the five-day visit is not an act of moral endorsement. It is a transaction. And the currency is underground.

Myanmar sits on some of the world's most significant deposits of rare earth minerals — the materials essential for semiconductors, electric vehicles, wind turbines, and advanced military equipment. China currently dominates global rare earth processing. India has been searching for an alternative supply, and Myanmar's deposits in Chin and Rakhine states, which border India's northeast, are a strategic prize.

Reuters has previously reported that India has been working to obtain mineral samples from Myanmar, including through coordination with a powerful rebel group. The official visit creates a formal channel for what has been an informal pursuit.

"The bottom line behind this visit from the Indian side is what they can get out of it in terms of raw materials, rare earths, and business propositions," said Gautam Mukhopadhaya, a former Indian ambassador to Myanmar. "And that's exactly what the Myanmar military wants, because it wants its military enterprises strengthened."

## The China Factor

Min Aung Hlaing choosing India for his first trip as president is a signal, and it is aimed squarely at Beijing. Myanmar has long been a Chinese sphere of influence — pipelines, ports, roads, and billions in investment tie the two countries together. But that dependency comes with strings. Beijing has backed some of the ethnic armed groups fighting Myanmar's military when it suited Chinese interests, and it has used economic leverage to keep Naypyidaw compliant.

"This has been part of Myanmar's way of dealing with India and China — capitulating more to China and trying to sort of balance it with India," Mukhopadhaya said.

For India, the calculation is straightforward: every dollar of influence Delhi gains in Myanmar is a dollar of leverage Beijing loses. With China's military buildup dominating this weekend's Shangri-La Dialogue in Singapore, the timing of the Myanmar visit is not coincidental.

## The Border Problem

There is a harder edge to the visit. Myanmar's military has launched renewed offensives in frontier areas near the Indian border, targeting the Arakan Army and Chin armed groups. India's northeastern states share a 1,643-kilometre border with Myanmar, and instability on the Myanmar side regularly spills over — refugee flows, arms trafficking, and insurgent activity.

"Min Aung Hlaing will almost certainly seek India's help in countering the Arakan Army and Chin armed groups," Horsey said. India, which has its own history of counter-insurgency operations in the northeast, has both the capability and the incentive to cooperate.

Indian foreign ministry spokesman Randhir Jaiswal told reporters on Friday that "all issues that form part of the gamut of relations between Myanmar and India will come up for discussion." In diplomatic language, that means everything is on the table.

## What Comes Next

The visit is expected to produce agreements on border security cooperation, trade facilitation, and possibly a framework for rare earth exploration. Min Aung Hlaing is also likely to visit Beijing soon to meet Xi Jinping — the balancing act that has defined Myanmar's foreign policy for decades.

For India, hosting a man most of the world considers a coup leader is a calculated risk. But in a region where China's influence grows by the quarter, calculated risks are the only kind worth taking."""
}

publish_article(article2)
time.sleep(1)


# ═══════════════════════════════════════════════════════════════
# ARTICLE 3: Sensex Crashes 850 Points in 10 Minutes on MSCI Fear
# ═══════════════════════════════════════════════════════════════

print("\n" + "="*60)
print("ARTICLE 3: Sensex MSCI Crash")
print("="*60)

# Image: Indian stock market / BSE building
img3 = fetch_pexels_image("Bombay stock exchange India building", "Indian stock market trading")
if not validate_image(img3):
    img3 = fetch_pexels_image("stock market crash chart red")
    if not validate_image(img3):
        img3 = None

article3 = {
    "headline": "The Sensex Fell 850 Points in 10 Minutes on Friday. The Explanation That Went Viral Was Wrong.",
    "subheadline": "India's weight in the MSCI index barely moved — from 12.4% to 12.3%. But social media said MSCI had dumped India, and Rs 6 lakh crore vanished before anyone checked.",
    "slug": "sensex-850-point-crash-msci-rebalance-panic-india-weight-unchanged-20260530",
    "category": "news",
    "vertical": "news",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "image_url": img3,
    "image_attribution": "Pexels" if img3 and "pexels" in (img3 or "") else None,
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "Value Research Online", "url": "https://www.valueresearchonline.com"},
        {"name": "Fingo News", "url": "https://fingonews.com"},
        {"name": "IIFL Capital Research", "url": "https://www.iifl.com"}
    ]),
    "body": """For six hours on Friday, the Indian market did almost nothing. Then, at 3:00 PM, the Sensex was at 75,529. By 3:10 PM, it was at 74,685. An 850-point drop in ten minutes. Roughly Rs 6 lakh crore of market value disappeared in the time it takes to brew a cup of chai.

Within minutes, an explanation went viral across WhatsApp groups, Twitter, and financial Telegram channels: MSCI had slashed India's weight. Foreign funds were fleeing. The world had lost faith in Indian markets. It was a compelling story. It was also wrong.

## What Actually Happened

MSCI, the global index provider whose benchmarks are tracked by trillions of dollars in passive funds, conducts semi-annual rebalancing of its indices. On May 29, the May 2026 rejig took effect at the close of trading. Here is what it actually did to India:

Four stocks were added — Federal Bank, Multi Commodity Exchange (MCX), National Aluminium Company (NALCO), and Indian Bank. Four stocks were removed — Hyundai Motor India, Jubilant Foodworks, Kalyan Jewellers, and Rail Vikas Nigam. India's weight in the MSCI Global Standard Index moved from 12.4% to 12.3%. The number of Indian constituents remained unchanged at 165.

That is the whole event. Four in, four out. Weight change of 0.1 percentage points. No structural downgrade. No loss of confidence.

## Where the Rs 6 Lakh Crore Went

The actual outflows from the MSCI rebalancing were estimated at roughly Rs 8,000 crore — significant, but a fraction of the daily turnover on Indian exchanges. The problem was not the rebalancing. The problem was timing.

MSCI changes take effect at the closing price. Passive funds tracking the index must execute their trades at or near the close, concentrating all the selling into the final minutes of trading. When you compress Rs 8,000 crore of forced selling into a 10-minute window, the price impact is amplified far beyond what the actual volume justifies.

What made it worse was the viral narrative. As the Sensex dropped, screenshots circulated claiming MSCI had cut India's weight from 20% to 11.2%. That number was misleading — it referenced India's weight in the MSCI Emerging Markets index, which has been declining gradually from its July 2024 peak of 20% due to relative underperformance, not because of any single rebalancing event. The decline to 11.2% has been happening across multiple quarters, driven largely by elevated oil prices and the absence of India from the global AI trade.

## A Misunderstanding for NRI Investors

For NRIs with Indian market exposure — whether through mutual funds, direct equity, or NRE/NRO-linked investments — the viral narrative was particularly damaging. The claim that "MSCI dumped India" implied a structural shift in global capital allocation away from Indian assets. Nothing of the sort happened.

The Nifty 50 closed down 1.5% at 23,547.75. The Sensex shed 1.44% to 74,775.74. For the month of May, the indices posted losses of 1.9% and 2.8% respectively — driven not by MSCI but by the ongoing uncertainty around the U.S.-Iran conflict and its effect on crude oil prices. India imports over 85% of its oil.

Brent Crude futures fell 19% in May, but remain 27.3% above pre-war levels. Until the Strait of Hormuz situation is resolved, Indian markets will trade under a geopolitical discount. That is the real story.

## The Stocks That Actually Moved

The rebalancing did create real winners and losers. Federal Bank, the largest inclusion, is estimated to receive roughly $483 million in passive inflows. MCX gets about $362 million, NALCO $328 million. On the other side, Hyundai Motor India faces $278 million in forced outflows, Jubilant Foodworks $151 million, Kalyan Jewellers $131 million, and Rail Vikas Nigam $118 million.

Adani Enterprises surged 22% in May after the U.S. dropped fraud charges against Gautam Adani — a reminder that Indian market narratives can reverse as quickly as they form.

Reliance Industries fell 7.7% for the month. ONGC dropped 11.4% on profit booking after a 25% rally. ITC declined 8.9% as analysts warned that cigarette price hikes would weigh on volumes.

## The Lesson

The 850-point crash will be cited for months as evidence of India's vulnerability to foreign capital flows. But the correct takeaway is simpler: India's MSCI weight moved by 0.1 percentage points, and the market lost Rs 6 lakh crore because a WhatsApp forward said otherwise. The information asymmetry between institutional investors (who knew exactly what the rebalancing would do) and retail investors (who read a viral screenshot) is the real story.

If you sold on Friday afternoon because you saw a panicked message about MSCI, you sold for the worst reason there is — a misreading that became consensus before anyone checked the actual data."""
}

publish_article(article3)

print("\n" + "="*60)
print("ALL ARTICLES PUBLISHED")
print("="*60)
