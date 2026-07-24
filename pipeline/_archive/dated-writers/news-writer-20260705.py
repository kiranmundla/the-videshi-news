#!/usr/bin/env python3
"""News writer for July 5, 2026 — 2 articles: India-Russia gasoline, USISPF trade deal summit"""

import json, os, subprocess, sys, urllib.parse, requests, re, hashlib
from datetime import datetime, timezone

# Load env
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ[k.strip()] = v.strip().strip('"').strip("'")

load_env(os.path.expanduser('~/.env.supabase'))
SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def supabase_insert(article):
    """Insert article into p2_articles"""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article
    )
    if r.status_code in (200, 201):
        data = r.json()
        if data:
            print(f"  ✓ Inserted: {data[0].get('slug', 'unknown')}")
            return data[0]
    print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
    return None

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia."""
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
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None

def fetch_wikimedia_commons_images(search_query, limit=5):
    """Search Wikimedia Commons for images."""
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": search_query,
        "gsrnamespace": 6,
        "gsrlimit": limit,
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": 1200,
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
                info_list = page.get("imageinfo", [])
                if info_list:
                    info = info_list[0]
                    mime = info.get("mime", "")
                    if mime.startswith("image/") and "svg" not in mime:
                        thumb = info.get("thumburl") or info.get("url")
                        original = info.get("url")
                        width = info.get("thumbwidth") or info.get("width", 0)
                        if width >= 400:
                            results.append({
                                "title": page.get("title", ""),
                                "thumb_url": thumb,
                                "original_url": original,
                                "width": width,
                                "height": info.get("thumbheight") or info.get("height", 0)
                            })
            return sorted(results, key=lambda x: x["width"], reverse=True)[:3]
    except Exception as e:
        print(f"  ⚠ Commons search error: {e}")
    return []

def fetch_pexels_image(query):
    """Fetch image from Pexels. Only for generic scenes, NOT for named people."""
    api_key = os.environ.get("PEXELS_API_KEY", "")
    if not api_key:
        # Try to load from .env.pexels
        pexels_env = os.path.expanduser("~/workspace/.env.pexels")
        if os.path.exists(pexels_env):
            load_env(pexels_env)
            api_key = os.environ.get("PEXELS_API_KEY", "")
    if not api_key:
        print("  ⚠ No Pexels API key")
        return None
    
    try:
        result = subprocess.run([
            "curl", "-sS", "-H", f"Authorization: {api_key}",
            f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=3&orientation=landscape"
        ], capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            if photos:
                url = photos[0]["src"]["large2x"]
                print(f"  ✓ Pexels image: {url[:80]}...")
                return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None

def validate_image(url):
    """Validate image URL returns 200 with image content-type and >5KB."""
    try:
        r = requests.head(url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=10, allow_redirects=True)
        if r.status_code == 200:
            ct = r.headers.get("Content-Type", "")
            cl = int(r.headers.get("Content-Length", "0") or "0")
            if "image" in ct and cl > 5000:
                return True
        # HEAD may fail on Wikimedia; try GET
        r = requests.get(url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=10, stream=True, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", "0") or "0")
        if r.status_code == 200 and "image" in ct:
            if cl > 5000:
                return True
            # Read a chunk to check size
            chunk = r.raw.read(10000)
            if len(chunk) > 5000:
                return True
    except Exception as e:
        print(f"  ⚠ Image validation error for {url[:60]}...: {e}")
    return False

def commons_relevance_ok(title, headline, topic):
    """Gate: does the Commons file title match the article's subject?"""
    # Stop words to exclude from keyword matching
    stop = {"the","a","an","in","on","at","of","to","for","and","or","is","are","was","were",
            "with","from","by","as","its","their","this","that","these","those","file","image",
            "photo","picture","jpg","jpeg","png","svg","wikimedia","commons","view","general",
            "new","old","day","year","city","country","people","world","social","media","india",
            "indian","news","united","states","national","public","official","government"}
    
    # Extract distinctive keywords from headline/topic
    words = re.findall(r'[a-zA-Z]{4,}', f"{headline} {topic}".lower())
    distinctive = [w for w in words if w not in stop]
    
    if not distinctive:
        return True  # Can't filter, allow
    
    title_lower = title.lower()
    hits = sum(1 for w in distinctive if w in title_lower)
    return hits >= 1

def get_best_image(person_name=None, commons_query=None, pexels_query=None, headline="", topic=""):
    """Multi-source image search: Wikipedia person > Commons > Pexels."""
    # Source 1: Wikipedia person image
    if person_name:
        img = fetch_wikipedia_person_image(person_name)
        if img and validate_image(img):
            return img, "Wikimedia Commons", f"Wikipedia portrait of {person_name}"
    
    # Source 2: Wikimedia Commons
    if commons_query:
        results = fetch_wikimedia_commons_images(commons_query)
        for r in results:
            url = r.get("thumb_url") or r.get("original_url")
            if url and commons_relevance_ok(r["title"], headline, topic):
                if validate_image(url):
                    # Build caption from title
                    cap = r["title"].replace("File:", "").rsplit(".", 1)[0].replace("_", " ")
                    return url, "Wikimedia Commons", cap
    
    # Source 3: Pexels (generic only, NEVER for named people)
    if pexels_query and not person_name:
        img = fetch_pexels_image(pexels_query)
        if img and validate_image(img):
            return img, "Pexels", pexels_query.title()
    
    return None, None, None


#############################################################
# ARTICLE 1: India's Gasoline Reaching Russia
#############################################################
def build_article_1():
    print("\n=== Article 1: India's Gasoline Reaching Russia ===")
    
    headline = "Indian-Made Gasoline Is Reaching Russia Through Traders. New Delhi Says It Has Nothing to Do With It."
    subheadline = "As Ukrainian drone strikes cripple a third of Russia's refining capacity, fuel from Nayara Energy — 49% owned by Rosneft — is sailing north via intermediaries. India's oil minister insists no Indian company is selling directly. The distinction may not hold for long."
    slug = "india-nayara-gasoline-russia-traders-ukraine-drone-strikes-fuel-shortage-20260705"
    
    body = """India finds itself at the centre of a geopolitical fuel puzzle it would rather not solve.

At least 60,000 metric tons of gasoline produced in India have been dispatched to Russia by sea, Reuters reported this week, citing multiple industry sources. Two tankers, each carrying 30,000 to 40,000 tons, left India's western coast in late June. The fuel originated from Nayara Energy's 400,000-barrel-per-day refinery at Vadinar, Gujarat — a facility that is 49 per cent owned by Russia's largest oil company, Rosneft.

A tanker invoice reviewed by Reuters showed the vessel Agni loaded with gasoline at Vadinar and sailed for Fujairah, a common transhipment hub. But vessel tracking data revealed it had passed Fujairah entirely and was moving north through the Suez Canal — a route consistent with a Russian destination.

India's Oil Minister Hardeep Singh Puri was forced to address the reports within hours. His formulation was careful: "Indian companies are not selling fuels to Russia," he said at a media briefing. But he conceded it was "possible that Indian-origin refined fuel is sold to Russia via traders."

## Why Russia Needs Indian Fuel

The scale of Russia's fuel crisis is staggering. Ukraine's drone campaign has knocked offline an estimated 30 per cent of Russian refining capacity — a sustained assault on infrastructure that Moscow initially dismissed as localised bottlenecks. President Vladimir Putin acknowledged on national television that fuel shortages were real, calling for government intervention to stabilise the market.

In the southern port city of Novorossiysk, gasoline sales to private motorists have been suspended entirely. In the Black Sea resort of Anapa, Cossacks have been deployed at petrol stations to prevent fights. In Krasnodar, police have arrested people for illegally reselling fuel. Across Russia's 11 time zones, queues, rationing, and record price increases have become routine.

Moscow is importing 400,000 tons of gasoline monthly from multiple countries, including Belarus, which has tripled its supply. Russia's parliament passed emergency amendments to subsidise fuel imports, pegged to Indian delivery costs.

## The Nayara Connection

Nayara Energy occupies an unusual position in India's oil landscape. It is India's second-largest private refiner, operating one of the country's most sophisticated refineries. But since European Union sanctions imposed last July complicated its payment channels, Nayara has relied on traders for both crude imports and refined-fuel exports. Its Vadinar refinery now processes exclusively Russian crude — other suppliers withdrew after the sanctions took effect.

The company did not respond to Reuters' request for comment. But trade data compiled by analytics firm Kpler tells a broader story: India's gasoline exports surged 84 per cent in June, from 169,000 barrels per day to 311,000 bpd. Of that total, 90,700 bpd went to "unknown destinations" — a Kpler designation for shipments whose tracking data cannot determine a final port.

"We are not seeing any gasoline cargoes loaded from India signalling Russia as their discharge destination," said Nikhil Dubey, Kpler's lead refining analyst. The cargoes appear to be routed through intermediaries, a pattern that mirrors how Russian crude initially reached India through similar opaque channels.

## The Diplomatic Tightrope

For New Delhi, the timing could scarcely be worse. India and the United States are in the advanced stages of negotiating a Bilateral Trade Agreement — one that U.S. officials described just days ago as "very, very close" to conclusion. India is also fighting a separate U.S. tariff battle: the Section 301 forced-labour investigation that could impose an additional 12.5 per cent duty on Indian exports.

India's position on Russia has always been pragmatic rather than principled. New Delhi never joined Western sanctions, continued buying discounted Russian crude in enormous quantities, and abstained from UN votes condemning the invasion. But directly fuelling Russia's war machine — even through intermediaries — raises the stakes considerably.

The trader intermediary structure gives India plausible deniability, but Washington may not find the distinction persuasive. Previous rounds of sanctions enforcement have focused on exactly this kind of indirect supply chain, and American officials have signalled they will scrutinise commodities routed through third parties.

## What This Means for the Diaspora

For the five-million-strong Indian diaspora in the United States, the story has practical implications. The ongoing India-US trade negotiations could face political headwinds if lawmakers perceive India as actively sustaining Russia's war effort, even indirectly. Any delay in the trade deal directly affects Indian exporters, IT companies operating in the American market, and the broader economic relationship that supports diaspora livelihoods.

Indian energy stocks — including Nayara's parent Rosneft and companies like Reliance, Indian Oil Corporation, and BPCL that dominate India's refining sector — face potential reputational and compliance risks. NRI investors with exposure to these stocks should watch how Washington responds.

The broader question is whether India's carefully balanced neutrality on Russia can survive the escalation of indirect supply chains. As one Western diplomat put it to Reuters: "The question is no longer whether India is trading with Russia. It's whether India is supplying Russia's war machine. That's a different conversation."

*Sources: Reuters, Kpler, Outlook Business, OilPrice.com*"""

    # Image sourcing
    print("  Sourcing image...")
    # Try Commons for oil refinery / tanker
    img_url, img_attr, img_cap = get_best_image(
        commons_query="Nayara Energy Vadinar refinery Gujarat",
        pexels_query="oil refinery industrial",
        headline=headline,
        topic="India gasoline Russia fuel"
    )
    if not img_url:
        img_url, img_attr, img_cap = get_best_image(
            commons_query="oil tanker ship gasoline",
            pexels_query="oil refinery industrial port",
            headline=headline,
            topic="India gasoline fuel export"
        )
    
    if not img_url:
        print("  ⚠ No suitable image found, trying Pexels generic refinery")
        img_url = fetch_pexels_image("oil refinery industrial")
        img_attr = "Pexels"
        img_cap = "An oil refinery at dusk"
    
    article = {
        "headline": headline,
        "subheadline": subheadline,
        "slug": slug,
        "body": body,
        "category": "news",
        "vertical": "geopolitics",
        "status": "review",
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": img_cap or "An oil refinery complex",
        "image_attribution": img_attr or "Pexels",
        "diaspora_angle": "India-Russia fuel trade complicates the India-US trade deal that directly affects five million Indian Americans and Indian exporters.",
        "sources": json.dumps(["Reuters", "Kpler", "Outlook Business", "OilPrice.com", "The Hindu Business Line"]),
        "published_at": datetime.now(timezone.utc).isoformat(),
        "tags": ["India", "Russia", "gasoline", "Nayara Energy", "Rosneft", "Ukraine", "fuel shortage", "sanctions", "trade", "geopolitics"]
    }
    
    return article


#############################################################
# ARTICLE 2: USISPF Summit / India-US Trade Deal
#############################################################
def build_article_2():
    print("\n=== Article 2: USISPF Summit — Trade Deal ===")
    
    headline = "Washington Says a Historic India-US Trade Deal Is 'Very Very Close.' India Says Not Until It Gets Better Terms Than Pakistan."
    subheadline = "At the USISPF summit in Washington, American officials project imminent success on a $500 billion trade target. But India's Commerce Minister has drawn an unmovable red line: no deal unless Indian tariffs fall below Pakistan's. The gap is 2.5 percentage points — and it could take months to close."
    slug = "usispf-summit-india-us-trade-deal-pakistan-tariff-red-line-kwatra-30-trillion-20260705"
    
    body = """Two capitals, one deal, and a gulf of expectations that refuses to close.

In Washington this past week, U.S. Deputy Assistant Secretary Bethany Poulos Morrison told an audience that the historic India-US trade agreement was "very, very close" to being finalised. The administration, she said, was driving toward its "Mission 500" target — $500 billion in bilateral trade by 2030 — with "a real sense of urgency."

In London, at the India Global Forum's UK-India Week, Union Commerce Minister Piyush Goyal delivered a different message entirely. India, he said, will not sign the Bilateral Trade Agreement until Washington guarantees Indian exporters a tariff rate lower than Pakistan's. The current rate on Indian goods stands at 12.5 per cent. Pakistan's rate is 10 per cent. No Indian political leader, Goyal implied, could accept that arithmetic.

"The whole deal was centred around that competitive advantage we got with that 18 per cent over our neighbours and competing countries," Goyal explained. "We were lower than all our neighbouring countries and all our ASEAN countries other than Singapore. That is why the deal was attractive for us."

## The 2.5-Point Problem

The gap sounds trivial — 2.5 percentage points between India's 12.5 per cent tariff and Pakistan's 10 per cent. But as Mukesh Aghi, President of the US-India Strategic Partnership Forum, explained ahead of the USISPF Leadership Summit, the issue is fundamentally political.

"No political leader in India will accept that because it would essentially cost them elections," Aghi said. "The tariff on India at the moment is 12.5 per cent, while Pakistan's is 10 per cent. That has to be sorted out."

The irritant goes beyond economics. India pushed back earlier this year against suggestions that U.S. trade incentives were linked to the India-Pakistan ceasefire. New Delhi's Ministry of External Affairs stated flatly that trade "didn't come up" in those discussions. Now the tariff disparity adds a second layer of discomfort: even while India was engaged in military tensions with Pakistan, Washington was offering Islamabad a more favourable commercial arrangement.

## The Summit's Other Story: $30 Trillion by 2047

The USISPF Leadership Summit was not all friction. Indian Ambassador Vinay Mohan Kwatra delivered what amounted to a national pitch, outlining India's trajectory from its current $4.3 trillion economy to $7 trillion by 2030, $14 trillion by the mid-2030s, and $25 to $30 trillion by 2047.

"India is an indispensable anchor of the global order," Kwatra declared, describing the growth path as the product of three converging forces: India's focus on domestic economic growth, the global disruptions that have created new opportunities, and a set of "hugely transformative measures" that have accelerated India's rise.

Bharti Enterprises founder Sunil Bharti Mittal, who received the USISPF 2026 Leadership Award alongside Fairfax Financial's V. Prem Watsa and RTX's Christopher Calio, struck a more personal note. Addressing U.S. Commerce Secretary Howard Lutnick directly, he said: "I'm hoping, Secretary Lutnick, that if not in days, but in a few weeks, that India and the US will have a trade deal that we in the industry have been looking forward to."

Mittal described the nearly five-million-strong Indian diaspora as "a beautiful bridge between India and the US, helping the strategic relationship develop between the two nations, be that trade, defence, or indeed higher technologies."

## Behind Closed Doors: Chips, Minerals, and AI

Away from the speeches, the summit's most consequential session may have been a closed-door roundtable organised by the Indian Embassy alongside USISPF and the Silverado Policy Accelerator. Ambassador Kwatra, MeitY Secretary S. Krishnan, and U.S. Deputy Under Secretary of Commerce Bill Guidera brought together Indian and American companies working on semiconductors, critical minerals, and artificial intelligence.

The discussions focused on what officials called "durable demand signals" — essentially, guarantees that both governments would create predictable markets for jointly developed technology. Additional Secretary Nagaraj Naidu from India's Ministry of External Affairs and Deputy Assistant Secretary Christopher Saldana from the U.S. Department of Energy also participated, reflecting the breadth of the technology partnership.

Aghi framed the critical minerals dimension in strategic terms: "What we saw last year was a strong message — you can't depend on China for critical minerals because you risk being held hostage to their supply chain." Under the emerging framework, India would anchor processing and raw material sourcing while the United States would provide capital and technology.

## Section 301 Looms Over Everything

The summit's optimistic tone was shadowed by an approaching deadline. On July 8, Indian government representatives and industry bodies including FICCI and CII will appear before the U.S. Trade Representative at a public hearing to challenge a proposed 12.5 per cent tariff under Section 301 of the Trade Act. The investigation — which targets 60 countries for allegedly failing to address forced labour in supply chains — could layer an additional duty on top of India's existing tariff exposure.

India has called the findings "legally flawed" and argued that its domestic labour regime is comprehensive. But the hearing will test whether India's diplomatic confidence at USISPF translates into legal resilience in a Washington hearing room.

## Why the Diaspora Should Care

For Indian Americans, the stakes of the trade deal extend beyond macroeconomic projections. A concluded agreement would stabilise tariff uncertainty for Indian IT firms that employ hundreds of thousands across the United States. It would clarify the regulatory environment for Global Capability Centres — the offshore engineering hubs that are the fastest-growing segment of U.S.-India commercial ties. And it would signal that the world's two largest democracies can do business on terms both find fair.

The $500 billion target sounds ambitious, but the numbers are trending in the right direction. As Ambassador Kwatra noted: India's growth is "not a product of chance" — it is the result of structural reforms that make the country a predictable partner. The question is whether the politics of a 2.5 percentage-point tariff gap can catch up with the economics of a $500 billion opportunity.

*Sources: USISPF, Reuters, The Indian EYE, The Hindu Business Line, India Global Forum*"""

    # Image sourcing — try Kwatra or USISPF
    print("  Sourcing image...")
    img_url, img_attr, img_cap = get_best_image(
        person_name="Vinay Mohan Kwatra",
        commons_query="India United States trade summit diplomacy",
        pexels_query="business summit diplomacy",
        headline=headline,
        topic="India US trade deal USISPF summit"
    )
    
    if not img_url:
        # Try Piyush Goyal
        img_url, img_attr, img_cap = get_best_image(
            person_name="Piyush Goyal",
            headline=headline,
            topic="India trade"
        )
    
    if not img_url:
        img_url, img_attr, img_cap = get_best_image(
            person_name="Sunil Bharti Mittal",
            headline=headline,
            topic="India telecom business"
        )
    
    if not img_url:
        print("  ⚠ No person image found, trying generic")
        img_url = fetch_pexels_image("diplomatic summit business conference")
        img_attr = "Pexels"
        img_cap = "A high-level diplomatic summit"
    
    article = {
        "headline": headline,
        "subheadline": subheadline,
        "slug": slug,
        "body": body,
        "category": "news",
        "vertical": "trade",
        "status": "review",
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": img_cap or "India-US diplomatic engagement",
        "image_attribution": img_attr or "Pexels",
        "diaspora_angle": "The India-US trade deal directly affects five million Indian Americans, Indian IT firms operating in the US, and the regulatory environment for Global Capability Centres.",
        "sources": ["USISPF", "Reuters", "The Indian EYE", "The Hindu Business Line", "India Global Forum"],
        "published_at": datetime.now(timezone.utc).isoformat(),
        "tags": ["India", "United States", "trade deal", "USISPF", "tariff", "Pakistan", "Kwatra", "Piyush Goyal", "Sunil Bharti Mittal", "AI", "semiconductors"]
    }
    
    return article


#############################################################
# MAIN
#############################################################
if __name__ == "__main__":
    articles = []
    
    a1 = build_article_1()
    articles.append(a1)
    
    a2 = build_article_2()
    articles.append(a2)
    
    # Insert all
    print("\n=== Inserting articles ===")
    success = 0
    for art in articles:
        result = supabase_insert(art)
        if result:
            success += 1
    
    print(f"\n✓ Done: {success}/{len(articles)} articles inserted")
