#!/usr/bin/env python3
"""
News Writer — The Videshi
Generates 3 news articles with proper image sourcing and inserts into Supabase.
"""

import os, sys, json, time, uuid, re, subprocess
from datetime import datetime, timezone

# Load env
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, val = line.split('=', 1)
                val = val.strip().strip('"').strip("'")
                os.environ[key] = val

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

import requests
from PIL import Image
import io

# ==================== IMAGE HELPERS ====================

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

def upload_to_supabase(img_bytes, filename):
    """Upload image to Supabase storage bucket 'article-images'. Returns public URL."""
    url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true"
    }
    r = requests.post(url, headers=headers, data=img_bytes, timeout=30)
    if r.status_code in (200, 201):
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
        print(f"  ✓ Uploaded to Supabase: {filename} ({len(img_bytes)} bytes)")
        return public_url
    else:
        print(f"  ✗ Upload failed ({r.status_code}): {r.text[:200]}")
        return None

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    import urllib.parse
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
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": search_query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata",
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
        print(f"  ⚠ Wikimedia Commons error for '{search_query}': {e}")
    return []

def fetch_pexels_image(query):
    """Fetch an image from Pexels using curl (urllib gets 403)."""
    try:
        result = subprocess.run(
            ['curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
             f'https://api.pexels.com/v1/search?query={requests.utils.quote(query)}&per_page=3&orientation=landscape'],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            if photos:
                url = photos[0]['src']['large2x'] + '?auto=compress&cs=tinysrgb&w=1200'
                print(f"  ✓ Pexels image found for '{query}': {url[:80]}...")
                return url
    except Exception as e:
        print(f"  ⚠ Pexels error for '{query}': {e}")
    return None

def download_image(url):
    """Download an image, return bytes or None."""
    try:
        r = requests.get(url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=20)
        if r.status_code == 200 and r.headers.get('Content-Type', '').startswith('image'):
            if len(r.content) > 5000:
                return r.content
            else:
                print(f"  ⚠ Image too small ({len(r.content)} bytes), skipping")
    except Exception as e:
        print(f"  ⚠ Download error: {e}")
    return None

def source_image(slug, person_name=None, topic_queries=None, pexels_query=None):
    """Multi-source image search. Returns (supabase_url, attribution) or (None, None)."""
    candidates = []
    
    # Source 1: Wikipedia (for person articles)
    if person_name:
        wiki_url = fetch_wikipedia_person_image(person_name)
        if wiki_url:
            candidates.append({"url": wiki_url, "source": "wikipedia", "priority": 1})
    
    # Source 2: Wikimedia Commons
    if topic_queries:
        for q in topic_queries:
            results = fetch_wikimedia_commons_images(q, limit=3)
            for r in results[:2]:
                candidates.append({"url": r["url"], "source": "wikimedia_commons", "priority": 2})
            if results:
                break
    
    # Source 3: Pexels
    if pexels_query:
        pexels_url = fetch_pexels_image(pexels_query)
        if pexels_url:
            candidates.append({"url": pexels_url, "source": "pexels", "priority": 3})
    
    # Pick best and upload
    for c in sorted(candidates, key=lambda x: x["priority"]):
        img_bytes = download_image(c["url"])
        if img_bytes:
            compressed = compress_image(img_bytes)
            if len(compressed) > 5000:
                filename = f"{slug}.jpg"
                final_url = upload_to_supabase(compressed, filename)
                if final_url:
                    attr = "Wikimedia Commons" if c["source"] in ("wikipedia", "wikimedia_commons") else "Pexels"
                    return final_url, attr
    
    print(f"  ✗ No usable image found for '{slug}'")
    return None, None

# ==================== SUPABASE INSERT ====================

def insert_article(article):
    """Insert article into Supabase p2_articles table."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    r = requests.post(url, headers=headers, json=article, timeout=30)
    if r.status_code in (200, 201):
        result = r.json()
        art_id = result[0]['id'] if isinstance(result, list) and result else 'unknown'
        print(f"  ✓ Inserted article: {article['headline'][:60]}... (id={art_id})")
        return art_id
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return None

# ==================== ARTICLES ====================

articles_to_write = [
    {
        "headline": "Nine Hundred Tankers Went Dark to Cross the Strait of Hormuz. India Is One of the Countries Paying for Passage.",
        "subheadline": "Two-thirds of outbound oil tankers are switching off tracking systems to slip through Iran's blockade. Some are paying Tehran up to $2 million per crossing — and India, China, Pakistan, and Japan are among those using the corridor.",
        "slug": "dark-tankers-hormuz-india-iran-tolls-oil-smuggling-pgsa-20260605",
        "category": "news",
        "vertical": "news",
        "body": """Three months into the Strait of Hormuz closure, a shadow fleet has emerged.

Nearly 900 outbound tankers have transited the strait by switching off their Automatic Identification Systems, effectively vanishing from satellite tracking before reappearing days later near their destinations. Shipping analytics firm Vortexa estimates that roughly 65 per cent of all outbound laden tankers in May crossed in "dark" mode — a tactic long used by Iran to evade Western sanctions, now adopted on an industrial scale by commercial carriers desperate to move crude.

## The Numbers Tell a Story of Quiet Acceleration

The volume of oil trapped on tankers inside the Persian Gulf has fallen from a peak of 184 million barrels on 22 March to roughly 148 million barrels this week, according to data from trade intelligence firm Kpler. That implies an average drawdown of about 500,000 barrels per day. But since the start of May, the pace has picked up sharply to 710,000 barrels per day — strong evidence that more oil is leaving the Gulf than satellite-visible traffic alone would suggest.

Exactly which routes these tankers are taking remains unclear. Many are believed to be using corridors designated by Iran, which has formalised its grip on the strait through the newly established Persian Gulf Strait Authority. The PGSA, created last month, oversees a new protocol for transits that includes vetting by Iranian authorities and, in some cases, fees.

## India Among the Countries Using Iranian Corridors

Vessels linked to India, China, Pakistan, and Japan have made use of Iran's supervised passage, with Tehran claiming dozens of ships were transiting under its guidance in recent days. Some carriers are reportedly paying tolls of up to $2 million per voyage for guaranteed safe passage through waters believed to be mined and within range of Iranian drones and fast-attack craft.

For India, the world's third-largest oil consumer, the arrangement carries uncomfortable implications. The strait normally carries more than 40 per cent of India's crude imports. With that chokepoint effectively closed since the US-Israeli strikes on Iran began on 28 February, Indian refiners have scrambled to diversify — increasing purchases from Venezuela, Brazil, Angola, and Nigeria while maintaining Russian flows of roughly 1.9 million barrels per day.

But some cargoes still need to come through the Gulf, and the dark-transit system offers the only available route. The US Navy has supported roughly 70 ship crossings in the last three weeks, mostly through corridors hugging Oman's coastline. Ships exiting Iranian ports, however, face the risk of interception from the American blockade along the Gulf of Oman, with US Central Command having intercepted 133 ships to date.

## Washington Has Sanctioned Iran's Strait Authority

The United States has sanctioned the PGSA and prohibited shipping companies from striking deals with Tehran. The White House has also threatened secondary sanctions against companies that pay fees to Iran for safe passage — a warning that puts Indian carriers and refiners in a difficult position.

The opacity is also distorting global oil pricing. With reduced visibility into cargo movements and destinations, it is harder for traders to gauge the flows underpinning benchmark pricing. Brent crude was hovering near $95 a barrel on Friday, roughly unchanged, as markets weighed the Hezbollah rejection of a Lebanon ceasefire against lingering hopes for a US-Iran deal.

## The Diaspora Feels It at the Pump

For the 8.9 million Indians in the Gulf and the millions more in the US and Europe, the supply disruption is not abstract. Fuel prices have risen across Asia, and the Indian rupee — already Asia's worst-performing currency in 2026 — is under sustained pressure from high energy import costs. The RBI on Friday held rates steady at 5.25 per cent while unveiling measures to support the faltering currency, including scrapping capital gains tax for foreign holders of government bonds and sweetening dollar deposit schemes for NRIs.

The longer the Hormuz chokepoint stays closed, the more entrenched the dark-transit system becomes. And the more dependent India gets on arrangements it cannot publicly acknowledge.

*Sources: Reuters, Kpler shipping data, Vortexa analytics, New York Post, CNN*""",
        "person_name": None,
        "image_topic_queries": ["Strait of Hormuz oil tanker", "Hormuz strait ships", "oil tanker Persian Gulf"],
        "pexels_query": "oil tanker ship ocean",
        "image_caption": "Oil tankers near the Strait of Hormuz, a chokepoint for a fifth of global oil supply",
        "sources_list": ["Reuters", "Kpler", "Vortexa", "New York Post", "CNN"]
    },
    {
        "headline": "The US Wants India to Go Nuclear. This Time, the Private Sector Is Leading.",
        "subheadline": "US Ambassador Sergio Gor says Washington and New Delhi are pushing civil nuclear cooperation to 'new levels' — with private companies, not governments, building the reactors India needs to power its AI ambitions.",
        "slug": "us-india-civil-nuclear-partnership-private-sector-sergio-gor-20260605",
        "category": "news",
        "vertical": "news",
        "body": """The pitch was unusually direct. Speaking to a room of Indian business leaders at the CITI 2026 India event in Mumbai, US Ambassador Sergio Gor did not wrap his message in diplomatic hedging.

"We are pushing our civil nuclear sector partnership to new levels," he said. "This is a very big growth area over the next few years."

The statement marks a shift in how Washington talks about nuclear energy with India. For two decades, since the landmark 2005 India-US nuclear deal, the partnership has been defined by government-to-government agreements, liability disputes, and stalled reactor projects. Gor's framing was different. He spoke of private-sector-led solutions, financial services backing, and decades-long commercial partnerships — the language of a market opening, not a strategic concession.

## From Government Deals to Private Capital

The ambassador said his mission had recently hosted member companies of the US Nuclear Energy Institute in India to demonstrate "how a vibrant private sector-led civil nuclear industry can contribute to safe and secure civil nuclear power meeting India's projected power demand."

India's electricity demand is projected to nearly double by 2040, driven by urbanisation, industrial expansion, and — critically — the explosive growth of AI data centres. Reliance Industries has committed roughly $110 billion over seven years to AI computing infrastructure. Adani Group has pledged $100 billion for renewable-energy-powered AI data centres. Both plans are running into the same constraint: India does not have enough power.

Nuclear offers what solar and wind cannot: continuous baseload power in a compact footprint. A single nuclear plant can run at 90 per cent capacity around the clock, something no renewable installation can match without massive storage investments.

## The TRUST Initiative and Critical Minerals

Gor explicitly linked nuclear energy to the broader TRUST Initiative, launched by both countries in February 2025, which targets strategic technologies including AI, semiconductors, quantum computing, and critical minerals.

"Together, we will undertake efforts to protect sensitive supply chains from coercive market practices and reduce our collective vulnerability to single source monopolies," he said, referencing the recently signed US-India Critical Minerals Framework.

The subtext is China. Beijing dominates global nuclear fuel enrichment and processing, just as it dominates rare earths and battery materials. A US-India nuclear axis — one that includes private American reactor builders like NuScale, TerraPower, and X-energy — would create an alternative supply chain for a technology that is suddenly in demand worldwide.

## What Has Changed

Several things have shifted since the last attempt at US-India nuclear cooperation stalled. India's liability law, once the deal-killer for American companies, was modified in 2024 to create a clearer insurance-backed framework. The Hormuz crisis has made energy security a first-order concern for New Delhi. And the AI infrastructure boom has created a commercial demand signal that did not exist five years ago.

Gor pointed to high-level engagement as evidence of Washington's seriousness, citing visits by Secretary of State Marco Rubio and other cabinet officials. He quoted Rubio's remarks at the Freedom 250 event: "If I think about all of the key issues and all of the key opportunities of the modern economy, India and the United States together, are perfectly positioned to work together."

## The Diaspora Angle

For Indian Americans in the technology and energy sectors, the nuclear push opens a new corridor. NRIs working at American nuclear companies — and there are thousands across the US national laboratory system, GE Hitachi, Westinghouse, and the emerging small modular reactor firms — may find themselves bridging the two sides of this partnership in the same way that the IT diaspora did in the 1990s.

The ambassador said the embassy is taking a "results driven" approach to identify sectoral opportunities. Whether that means real contracts or just more MoUs will depend on how quickly both governments can clear the regulatory and commercial ground for private capital to flow.

*Sources: The Indian Eye, Ministry of External Affairs, Reuters, Hindustan Times*""",
        "person_name": "Sergio Gor",
        "image_topic_queries": ["India nuclear power plant", "Kudankulam nuclear power plant", "US India nuclear cooperation"],
        "pexels_query": "nuclear power plant cooling tower",
        "image_caption": "A nuclear power facility — India is looking to private US firms to expand its reactor fleet",
        "sources_list": ["The Indian Eye", "Ministry of External Affairs", "Reuters", "Hindustan Times"]
    },
    {
        "headline": "India Used the Shangri-La Dialogue to Talk to Everyone. That Was the Point.",
        "subheadline": "In Singapore, Defence Secretary Rajesh Kumar Singh held meetings with US INDOPACOM, NATO's military chief, the Swedish defence ministry, the Netherlands, and Singapore's president — all in 48 hours. India's message: strategic autonomy is not isolation.",
        "slug": "india-shangri-la-dialogue-2026-defence-diplomacy-indopacom-nato-20260605",
        "category": "news",
        "vertical": "news",
        "body": """India's Defence Secretary Rajesh Kumar Singh arrived at the Shangri-La Dialogue in Singapore last week with a schedule that read like a geopolitical speed-dating card. In the space of 48 hours, he met the Commander of US Indo-Pacific Command, the Chair of the NATO Military Committee, Sweden's State Secretary for Defence, the Chief of Defence of the Netherlands, a bipartisan US Congressional delegation, Singapore's President, and a room full of think-tank analysts.

The sheer breadth of the engagement tells a story that no single bilateral readout can.

## The US Meeting: Military-to-Military

Singh's session with Admiral Samuel J Paparo, Commander of US INDOPACOM, focused on strengthening military-to-military cooperation and addressing emerging security challenges in the Indo-Pacific. The Ministry of Defence said the discussion "reaffirmed the shared commitment towards deepening India-US strategic defence ties."

This is not new language, but the context has changed. The US-Iran war has reshaped the security architecture of the Indo-Pacific, with American naval assets now concentrated in the Gulf of Oman and the Strait of Hormuz rather than the South China Sea and Western Pacific. For India, which shares maritime concerns in both theatres, the recalibration matters.

The meeting with a bipartisan delegation from the US Congress — described by the ministry as covering emerging threats, strategic cooperation, and a free and open Indo-Pacific — added a legislative dimension to what is usually a military conversation.

## The NATO Meeting: A Careful Signal

Singh's interaction with NATO Admiral Giuseppe Cavo Dragone, Chair of the NATO Military Committee, carried a different kind of signal. India is not a NATO member, not a NATO partner, and has historically maintained distance from the alliance. But the meeting happened, and the readout spoke of "constructive engagement with key multilateral defence organisations."

Observers at the ORF think tank noted that India's willingness to engage NATO at this level, while simultaneously maintaining ties with Russia (still a major defence supplier), reflects what they called "issue-based partnerships that stop short of formal alliance commitments." The think tank's analysis of the Shangri-La Dialogue concluded that India is positioning itself as "an independent pole in the international system."

## Europe and the Nordics: Defence Tech

The meetings with Sweden's Peter Sandwall and the Netherlands' General Onno Eichelsheim focused on defence technology, innovation, and bilateral training. Both are notable because they signal India's interest in diversifying its defence industrial base beyond the traditional triumvirate of Russia, France, and the US.

Sweden's defence industry — anchored by Saab, which makes the Gripen fighter jet and advanced radar systems — has been courting Indian procurement contracts for years. The Netherlands has strengths in naval engineering and cybersecurity. For India, which has declared 2026 the "Year of Networking and Data Centricity" for its armed forces, these are precisely the capabilities it needs.

## Singapore: The Host and the Hub

Singh's meeting with Singapore President Tharman Shanmugaratnam at the Istana reception was about bilateral strategic ties and areas of mutual interest. Singapore is India's second-largest trading partner in ASEAN and a hub for Indian defence procurement logistics.

The meeting also underscored Singapore's role as the venue where India can engage the world's defence establishment without the formality of a bilateral state visit.

## What India Is Saying by Talking to Everyone

The Shangri-La Dialogue has always been a venue where countries signal their intentions through their schedule of meetings. India's 2026 schedule — US, NATO, Europe, ASEAN — says that strategic autonomy is not the same thing as strategic isolation. New Delhi is comfortable engaging everyone, committing to no one bloc, and building a network of defence partnerships calibrated to specific capabilities rather than ideological alignment.

As the ORF analysis put it: "While Washington is encouraging greater coalition-building to balance China, and Beijing is advocating alternative models of global governance, India continues to position itself as an independent pole in the international system."

In Singapore last week, that pole was busy.

*Sources: Ministry of Defence (India), The Indian Eye, Observer Research Foundation, DVIDS*""",
        "person_name": None,
        "image_topic_queries": ["Shangri-La Dialogue Singapore 2026", "Shangri-La Hotel Singapore defence", "India defence secretary Singapore"],
        "pexels_query": "Singapore Shangri-La hotel conference",
        "image_caption": "The Shangri-La Dialogue in Singapore, Asia's premier defence summit",
        "sources_list": ["Ministry of Defence (India)", "The Indian Eye", "Observer Research Foundation", "DVIDS"]
    }
]

# ==================== MAIN ====================

def main():
    print(f"\n{'='*60}")
    print(f"The Videshi — News Writer")
    print(f"Run time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"Articles to write: {len(articles_to_write)}")
    print(f"{'='*60}\n")
    
    results = []
    
    for i, art in enumerate(articles_to_write, 1):
        print(f"\n--- Article {i}/{len(articles_to_write)}: {art['headline'][:60]}... ---\n")
        
        # Source image
        print("  Sourcing image...")
        img_url, img_attr = source_image(
            slug=art["slug"],
            person_name=art.get("person_name"),
            topic_queries=art.get("image_topic_queries"),
            pexels_query=art.get("pexels_query")
        )
        
        # Build article payload
        now_iso = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S+00:00')
        
        payload = {
            "headline": art["headline"],
            "subheadline": art["subheadline"],
            "slug": art["slug"],
            "body": art["body"].strip(),
            "category": art["category"],
            "vertical": art["vertical"],
            "status": "published",
            "published_at": now_iso,
            "is_editorial": False,
            "sources": art.get("sources_list", []),
        }
        
        if img_url:
            payload["image_url"] = img_url
            payload["image_caption"] = art.get("image_caption", "")
            payload["image_attribution"] = img_attr
        
        # Insert
        print("  Inserting article...")
        art_id = insert_article(payload)
        
        if art_id:
            results.append({"id": art_id, "headline": art["headline"], "slug": art["slug"]})
        
        time.sleep(1)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"RESULTS: {len(results)}/{len(articles_to_write)} articles published")
    for r in results:
        print(f"  ✓ {r['slug']}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
