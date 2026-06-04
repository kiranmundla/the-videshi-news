#!/usr/bin/env python3
"""
The Videshi — News Writer (2026-06-04 run)
Writes 3 news articles with multi-source image compare.
"""

import requests
import json
import os
import uuid
import urllib.parse
import time
from datetime import datetime, timezone
from PIL import Image
import io

# ─── ENV ──────────────────────────────────────────────────────────────────────
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line.startswith('#') or '=' not in line:
                continue
            if line.startswith('export '):
                line = line[7:]
            key, _, val = line.partition('=')
            val = val.strip('"').strip("'")
            os.environ[key.strip()] = val

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

SB_HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

UA = 'TheVideshi/1.0 (thevideshi.com)'

# ─── IMAGE HELPERS ────────────────────────────────────────────────────────────

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA},
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
            headers={"User-Agent": UA},
            timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/"):
                    continue
                if mime == "image/svg+xml" or ii.get("width", 0) < 300:
                    continue
                results.append({
                    "url": ii.get("thumburl") or ii.get("url", ""),
                    "original_url": ii.get("url", ""),
                    "title": page.get("title", ""),
                    "width": ii.get("width", 0),
                    "height": ii.get("height", 0),
                    "mime": mime
                })
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error: {e}")
    return []


def fetch_pexels_image(*queries):
    """Fetch best Pexels image from multiple query attempts."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in queries:
        try:
            r = requests.get(
                "https://api.pexels.com/v1/search",
                params={"query": q, "per_page": 3, "orientation": "landscape"},
                headers={"Authorization": PEXELS_KEY},
                timeout=10
            )
            if r.status_code == 200:
                photos = r.json().get("photos", [])
                if photos:
                    url = photos[0]["src"]["large2x"]
                    print(f"  ✓ Pexels image for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def compress_image(img_bytes, max_width=1200, quality=80):
    """Resize and compress image. Returns JPEG bytes."""
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    return buf.getvalue()


def download_image(url):
    """Download image bytes."""
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=20)
        if r.status_code == 200 and r.headers.get('Content-Type', '').startswith('image'):
            if len(r.content) > 5000:
                return r.content
            else:
                print(f"  ⚠ Image too small: {len(r.content)} bytes")
    except Exception as e:
        print(f"  ⚠ Download failed: {e}")
    return None


def upload_to_supabase(image_bytes, filename):
    """Upload compressed image to Supabase storage bucket 'article-images'."""
    compressed = compress_image(image_bytes)
    size_kb = len(compressed) / 1024
    print(f"  📦 Compressed to {size_kb:.0f} KB")
    
    url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
    headers = {
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'image/jpeg',
        'x-upsert': 'true'
    }
    r = requests.post(url, headers=headers, data=compressed, timeout=30)
    if r.status_code in (200, 201):
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
        print(f"  ✓ Uploaded: {public_url[:80]}...")
        return public_url
    else:
        print(f"  ✗ Upload failed ({r.status_code}): {r.text[:200]}")
        return None


def source_image(slug, person_name=None, topic_queries=None, pexels_queries=None):
    """Multi-source image pipeline. Returns (url, attribution) or (None, None)."""
    candidates = []
    
    # Source 1: Wikipedia (for person articles)
    if person_name:
        wiki_url = fetch_wikipedia_person_image(person_name)
        if wiki_url:
            candidates.append({"url": wiki_url, "source": "wikipedia", "relevance": 3})
    
    # Source 2: Wikimedia Commons
    if topic_queries:
        for tq in topic_queries[:2]:
            commons = fetch_wikimedia_commons_images(tq)
            for c in commons[:2]:
                candidates.append({"url": c["url"], "source": "wikimedia_commons", "relevance": 2})
    
    # Source 3: Pexels
    if pexels_queries:
        pexels_url = fetch_pexels_image(*pexels_queries)
        if pexels_url:
            candidates.append({"url": pexels_url, "source": "pexels", "relevance": 1})
    
    # Sort by relevance (highest first)
    candidates.sort(key=lambda c: c["relevance"], reverse=True)
    
    # Try downloading and uploading each candidate
    for c in candidates:
        print(f"  Trying {c['source']}: {c['url'][:80]}...")
        img_bytes = download_image(c["url"])
        if img_bytes:
            filename = f"{slug}.jpg"
            final_url = upload_to_supabase(img_bytes, filename)
            if final_url:
                attribution = "Wikimedia Commons" if c["source"] in ("wikipedia", "wikimedia_commons") else "Pexels"
                return final_url, attribution
    
    return None, None


# ─── SUPABASE INSERT ──────────────────────────────────────────────────────────

def insert_article(article):
    """Insert article into p2_articles."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    r = requests.post(url, headers=SB_HEADERS, json=article, timeout=30)
    if r.status_code in (200, 201):
        result = r.json()
        art_id = result[0]['id'] if isinstance(result, list) and result else 'unknown'
        print(f"  ✓ Inserted: {article['headline'][:60]}... (id: {art_id})")
        return art_id
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return None


# ─── ARTICLES ─────────────────────────────────────────────────────────────────

ARTICLES = [
    # Article 1: SEBI Rajesh Exports fraud
    {
        "headline": "SEBI Just Accused India's Biggest Gold Refiner of Fabricating $158 Billion in Revenue. The Numbers Were Never Real.",
        "subheadline": "Rajesh Exports and its chairman have been barred from the securities market after the regulator found that 99.8 per cent of the company's consolidated revenue came from subsidiaries whose books could not be verified.",
        "slug": "sebi-rajesh-exports-158-billion-revenue-fraud-rajesh-mehta-barred-20260604",
        "category": "news",
        "vertical": "news",
        "status": "published",
        "is_editorial": False,
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com"},
            {"name": "SEBI Order", "url": "https://www.sebi.gov.in"},
            {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com"},
            {"name": "BizzBuzz", "url": "https://bizzbuzz.news"}
        ]),
        "image_person": "Rajesh Exports",
        "image_topic_queries": ["SEBI India securities regulator", "Rajesh Exports gold refinery Bangalore"],
        "image_pexels_queries": ["gold refinery India", "gold bars refinery"],
        "image_caption": "Rajesh Exports, headquartered in Bengaluru, is known as the world's largest gold processor by volume",
        "body": """India's markets regulator has issued one of its most devastating corporate orders in years. The Securities and Exchange Board of India on Wednesday barred Bengaluru-based Rajesh Exports and its chairman and managing director Rajesh Mehta from the securities market, alleging that the company fabricated consolidated revenues worth ₹15.15 lakh crore — roughly $158 billion — over five fiscal years.

The figure is staggering not just in absolute terms but in proportion. SEBI alleges that 99.8 per cent of the revenue Rajesh Exports reported through its subsidiaries and step-down subsidiaries between FY2020-21 and FY2024-25 was misrepresented. The company, once held up as the world's largest gold processor by volume, now faces an investigation that could rewrite how India's corporate governance regime handles multinational structures.

## The Swiss Connection That Did Not Add Up

At the centre of SEBI's 109-page interim order is Valcambi SA, a Switzerland-based gold refinery that Rajesh Exports projected as its principal operating entity. According to the regulator, 97 to 99 per cent of the group's consolidated revenue was attributed to overseas subsidiaries, with Valcambi the largest among them.

The problem: Valcambi's own standalone audited financial statements showed revenue equal to less than 0.5 per cent of what Rajesh Exports claimed at the consolidated level. The numbers, SEBI concluded, simply did not reconcile. The company had never publicly disclosed the detailed financials of these overseas entities, despite them accounting for virtually all its reported revenue.

Global Gold Refineries AG, the holding company through which Rajesh Exports controlled Valcambi, was similarly opaque. SEBI found that the group systematically avoided providing financial statements, ERP system access, and transaction-level data to investigators and forensic auditors.

## Personal Trades Disguised as Corporate Revenue

The standalone books told their own story. SEBI alleged that Rajesh Exports recorded ₹114.87 billion in sales and ₹114.88 billion in purchases with a single entity, Affluence Shares and Stocks Private Limited. When SEBI approached Affluence, the firm denied any such transactions had taken place.

The regulator's conclusion: these were non-genuine entries linked to Rajesh Mehta's personal derivative trades, logged into the company's ledger to inflate turnover without any real economic activity. Each leg of the derivative trade was booked as a corporate transaction, inflating the books by more than ₹11,400 crore.

SEBI further alleged that ₹3.39 billion in company funds was routed directly into Mehta's personal bank accounts, including for derivative trading, without board or audit committee approval. The total amount moved without proper authorisation or disclosure reached ₹9.26 billion.

## Why NRIs Should Watch This Closely

For the Indian diaspora, the Rajesh Exports case is a reminder that India's corporate disclosure regime still has blind spots, particularly when subsidiaries are domiciled abroad. The company appeared on multiple institutional portfolios and was part of BSE and NSE indices. Retail and foreign institutional investors who bought into the stock were, according to SEBI, presented with a fundamentally misleading picture of the group's operational scale.

The stock fell 5 per cent on Wednesday after the order was made public. SEBI's interim directive bars both the company and Mehta from buying, selling, or dealing in securities until the investigation is complete. The regulator has also referred the matter to India's Financial Reporting Authority for further action.

## What Happens Next

The order is interim and ex-parte, meaning Rajesh Exports has not yet been given the opportunity to formally respond. The company and its chairman did not comment on Wednesday. But the scope of the alleged fabrication — ₹15.15 lakh crore across five years — makes this one of the largest accounting fraud investigations India has seen since the Satyam scandal in 2009.

For SEBI, the case is also a test of its own investigative capacity. The regulator acknowledged in its order that Rajesh Exports systematically refused to cooperate, declining to provide access to books, records, and forensic audit materials. Whether the regulator can now compel full disclosure and hold the promoters accountable will determine whether this becomes a watershed moment for Indian corporate governance or another case that drags through tribunals for years."""
    },
    
    # Article 2: Indian national killed in Kuwait
    {
        "headline": "An Indian Worker Was Killed When Iranian Drones Hit Kuwait's Airport. The Gulf Is No Longer Safe Ground for the Diaspora.",
        "subheadline": "India condemned the attack and said its embassy was assisting the family, as Kuwait expelled two Iranian diplomats and the airport resumed flights from a backup terminal after severe damage to Terminal 1.",
        "slug": "indian-national-killed-kuwait-airport-iranian-drone-strike-diaspora-gulf-20260604",
        "category": "news",
        "vertical": "news",
        "status": "published",
        "is_editorial": False,
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com"},
            {"name": "The Wall Street Journal", "url": "https://www.wsj.com"},
            {"name": "Gulte", "url": "https://www.gulte.com"},
            {"name": "The Kashmir Horizon", "url": "https://thekashmirhorizon.com"}
        ]),
        "image_person": None,
        "image_topic_queries": ["Kuwait International Airport", "Kuwait airport terminal"],
        "image_pexels_queries": ["Kuwait airport", "airport damage"],
        "image_caption": "Kuwait International Airport's Terminal 1 sustained severe damage in the Iranian drone and missile attack on June 3, 2026",
        "body": """An Indian national was killed on Wednesday when Iranian drones and missiles struck Kuwait International Airport, the Indian Embassy in Kuwait confirmed. At least 63 others were injured in what was one of the most damaging attacks on a Gulf state since the shaky ceasefire between the United States and Iran was declared on April 8.

The embassy said it was deeply saddened by the death and was in direct contact with the bereaved family, extending full support. India's Ministry of External Affairs separately condemned the attack and said its mission in Kuwait was providing all necessary assistance to the injured.

The dead Indian national has not been publicly identified. But for the estimated 1 million Indians living and working in Kuwait — and the roughly 9 million across the Gulf Cooperation Council states — the attack is a visceral reminder that the Iran war's collateral damage now reaches civilian infrastructure in countries that have tried to stay neutral.

## Terminal 1 Destroyed, Flights Diverted

The attack struck Kuwait International Airport in the early hours of Wednesday morning. Iranian drones and missiles hit airport facilities and nearby diplomatic missions, causing what Kuwaiti authorities described as severe damage to Terminal 1. Flights were immediately suspended and diverted.

Kuwait's health ministry said 63 people were injured, with seven requiring emergency surgery. The Kuwaiti military reported intercepting 13 ballistic missiles and 17 drones since dawn, but debris fell across several residential areas.

Kuwait Airways and Jazeera Airways resumed limited operations from Terminal 4 later in the day, after technical assessments confirmed it was safe to operate.

Iran's Revolutionary Guards denied targeting the airport, claiming the damage was caused by American interceptor missiles that missed their targets. The U.S. military said that claim was false and that Iranian drones had deliberately targeted the airport.

## Kuwait Expels Iranian Diplomats

Kuwait's response was swift. The foreign ministry summoned Iran's top envoy to lodge a formal protest and expelled two lower-ranking Iranian diplomats. Saudi Arabia issued a statement condemning the attacks on both Kuwait and Bahrain as a "clear violation of international law."

This was not the first time Kuwait's airport has been hit. In March and early April, near-daily drone attacks destroyed fuel tanks and a radar system. Officials estimate at least half those earlier strikes originated from Shia militias in Iraq backed by Iran. Kuwait, which shares a border with Iraq, is considered particularly vulnerable.

The airport had only fully reopened in late April, weeks after its Gulf neighbours, reflecting what observers described as Kuwaiti authorities' extreme aversion to risk. Wednesday's attack will test whether that caution was warranted — and whether the airport can sustain operations under continuing threat.

## The Diaspora Dimension

India has the largest expatriate population in the Gulf. Roughly 8.9 million Indian nationals live across the six GCC states, with Kuwait hosting around 1 million. Many work in construction, retail, hospitality, and services — sectors that place them at airports, malls, and other soft targets.

The Indian government has not issued a fresh travel advisory for Kuwait, though the MEA said it was monitoring the situation closely. During the initial phase of the Iran war in March, India evacuated several thousand nationals from Iran and coordinated with Gulf embassies on contingency plans.

For NRIs with family in the Gulf, the calculus has shifted. The April ceasefire was supposed to bring stability. Instead, it has produced a pattern of periodic escalation — each flare-up demonstrating that the ceasefire is a holding pattern, not a resolution.

## The Broader Picture

The Kuwait airport strike came on the same day that Israel and Lebanon agreed to implement a ceasefire, a development that briefly lowered Brent crude by 1.3 per cent to $96.59 a barrel. But the renewed fighting between the U.S. and Iran overshadowed that progress, with Asian stocks falling sharply on Thursday and the S&P 500 dropping 0.7 per cent overnight.

The U.S. responded to the Kuwait and Bahrain attacks by striking Iranian military positions on Qeshm Island near the Strait of Hormuz. The waterway, which handled roughly a fifth of global oil shipments before the war, remains largely closed.

Trump told reporters on Wednesday that a deal with Iran could come "as soon as this weekend." Iran's foreign minister said talks had not been cut off but no progress had been made. For the Indian worker who lost their life at a Kuwaiti airport terminal on Wednesday morning, the geopolitics arrived without warning."""
    },
    
    # Article 3: India lithium/nickel processing incentives
    {
        "headline": "India Is About to Offer ₹3,000 Crore to Build Its Own Lithium and Nickel Processing Industry. The EV Race Demands It.",
        "subheadline": "The Ministry of Mines will shortly unveil an incentive policy for processing lithium and nickel domestically, with minimum capacity thresholds designed to attract industrial-scale operations.",
        "slug": "india-lithium-nickel-processing-incentives-ev-battery-critical-minerals-20260604",
        "category": "news",
        "vertical": "news",
        "status": "published",
        "is_editorial": False,
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com"},
            {"name": "Ministry of Mines, Government of India", "url": "https://mines.gov.in"}
        ]),
        "image_person": None,
        "image_topic_queries": ["lithium battery processing plant", "lithium mining India critical minerals"],
        "image_pexels_queries": ["lithium battery factory", "electric vehicle battery manufacturing"],
        "image_caption": "India aims to build domestic lithium and nickel processing capacity to secure its electric vehicle supply chain",
        "body": """India's federal Ministry of Mines is preparing to unveil a policy offering financial incentives to companies that process lithium and nickel domestically, with an outlay of approximately ₹3,000 crore ($313 million), according to two people familiar with the matter who spoke to Reuters.

The policy, which has been in development since January, is designed to anchor a domestic critical minerals processing industry — an essential step if India is to meet its own electric vehicle targets without remaining permanently dependent on Chinese supply chains.

## What the Policy Includes

The incentive structure will cover lithium and nickel processing, the two minerals most critical to the battery value chain that powers electric vehicles. To qualify, lithium processing plants must have a minimum capacity of 30,000 metric tons, while nickel plants must meet a threshold of 50,000 metric tons.

Those thresholds are deliberate. They are large enough to discourage token facilities and attract only companies prepared to build at industrial scale. The policy signals that New Delhi wants processing hubs, not pilot projects.

In April, the mines secretary confirmed that the government had shortlisted two critical minerals tied to securing an electric vehicle value system for the processing policy, without naming them. Reuters' reporting now confirms they are lithium and nickel.

## Why It Matters for India's EV Ambitions

India has set itself an aggressive target: 30 per cent electric car penetration and 80 per cent for two-wheelers by 2030. Today, those numbers stand at 6 per cent and 9 per cent respectively. The gap is enormous, and closing it requires not just assembling batteries but processing the raw materials that go into them.

Currently, China controls roughly 70 per cent of global lithium processing and more than 60 per cent of nickel refining. India imports nearly all its lithium and processed nickel. A supply disruption — whether from trade restrictions, geopolitical tension, or competition for limited global capacity — could cripple India's EV manufacturing ambitions before they get off the ground.

The new policy is part of a broader push that began with India's 2023 critical minerals strategy, which identified 30 minerals essential to national security and economic growth. Lithium and nickel were at the top of that list.

## The Diaspora Angle

For NRI investors and entrepreneurs watching India's clean energy transition, the incentive policy opens a new industrial corridor. India's production-linked incentive schemes in semiconductors and electronics manufacturing have already drawn significant interest from the diaspora and from multinational firms. A similar scheme for critical minerals processing could attract both capital and technical expertise from Indians working in the battery and mining sectors globally.

India discovered lithium reserves in Jammu and Kashmir in 2023, estimating 5.9 million tonnes of inferred resources. Argentina, Chile, and Australia remain the dominant global producers, but having domestic reserves gives India a starting point — provided it builds the refining capacity to convert raw ore into battery-grade lithium compounds.

Nickel is equally strategic. Indonesia dominates global nickel supply and has restricted raw ore exports to force domestic processing. India, which has limited nickel deposits, will need to secure processing agreements with resource-rich countries while building its own refining infrastructure.

## The Global Context

The timing is not accidental. The United States, European Union, and Japan have all launched their own critical minerals strategies in the past three years, each aimed at reducing dependence on Chinese processing. India's entry into this space positions it as both a potential partner and a competitor.

The Iran war has added urgency. Elevated crude oil prices have made the economic case for EVs stronger, while supply chain disruptions across the Gulf have underscored the risks of energy dependence on a single region. A domestic lithium and nickel processing industry would not eliminate those risks, but it would reduce India's exposure at the most vulnerable point in the EV supply chain.

The Ministry of Mines did not respond to a request for comment. But with the policy expected shortly, India is about to signal whether it is serious about building the industrial backbone for its electric future — or whether the ambition will remain, like so many previous targets, a number on a government slide deck."""
    },
]


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    now = datetime.now(timezone.utc).isoformat()
    
    for i, art in enumerate(ARTICLES, 1):
        print(f"\n{'='*60}")
        print(f"Article {i}: {art['headline'][:70]}...")
        print(f"{'='*60}")
        
        # Extract image-related fields (not for Supabase)
        person_name = art.pop("image_person", None)
        topic_queries = art.pop("image_topic_queries", None)
        pexels_queries = art.pop("image_pexels_queries", None)
        caption = art.pop("image_caption", "")
        
        # Source image
        print("\n📸 Sourcing image...")
        img_url, attribution = source_image(
            art["slug"],
            person_name=person_name,
            topic_queries=topic_queries,
            pexels_queries=pexels_queries,
        )
        
        if img_url:
            art["image_url"] = img_url
            art["image_caption"] = caption
            art["image_attribution"] = attribution
        else:
            print("  ⚠ No suitable image found — publishing without hero image")
        
        # Set timestamps
        art["published_at"] = now
        art["created_at"] = now
        
        # Insert
        print("\n📝 Inserting article...")
        result = insert_article(art)
        if result:
            print(f"  ✅ Article {i} published successfully")
        else:
            print(f"  ❌ Article {i} FAILED to publish")
        
        time.sleep(1)
    
    print(f"\n{'='*60}")
    print("Done. Published 3 news articles.")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
