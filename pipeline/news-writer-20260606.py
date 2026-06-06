#!/usr/bin/env python3
"""
News writer for The Videshi - June 6, 2026 batch
Topics:
1. NITI Aayog semiconductor roadmap - India's ISM 2.0, $206B demand by 2035
2. US-India trade deal: first tranche by mid-July (Piyush Goyal)
3. Indian Americans meet DOJ/FBI on hate crimes against Hindus in Silicon Valley
"""

import json
import os
import requests
import subprocess
import sys
import time
import urllib.parse
from datetime import datetime, timezone

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, _, val = line.partition('=')
                    key = key.replace('export ', '').strip()
                    val = val.strip().strip('"').strip("'")
                    os.environ[key] = val

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

UA = "TheVideshi/1.0 (thevideshi.com)"

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
                })
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} images found for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error: {e}")
    return []

def fetch_pexels_image(query):
    """Search Pexels for an image using curl (Python urllib gets 403)."""
    try:
        result = subprocess.run(
            ["curl", "-sS", f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=3",
             "-H", f"Authorization: {PEXELS_KEY}"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            if photos:
                url = photos[0].get("src", {}).get("large2x") or photos[0].get("src", {}).get("large")
                if url:
                    print(f"  ✓ Pexels image found for '{query}': {url[:80]}...")
                    return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None

def validate_image(url):
    """Validate that an image URL returns HTTP 200 with content-type image/* and >5KB."""
    try:
        # Use curl for validation to avoid issues
        result = subprocess.run(
            ["curl", "-sS", "-I", "-L", "--max-time", "10", url],
            capture_output=True, text=True, timeout=15
        )
        output = result.stdout.lower()
        if "200" in output and "content-type: image/" in output:
            # Check content-length
            for line in output.split('\n'):
                if 'content-length:' in line:
                    size = int(line.split(':')[1].strip())
                    if size > 5000:
                        print(f"  ✓ Image validated: {url[:60]}... ({size} bytes)")
                        return True
                    else:
                        print(f"  ✗ Image too small: {size} bytes")
                        return False
            # No content-length header but 200 + image content-type — accept it
            print(f"  ✓ Image validated (no content-length): {url[:60]}...")
            return True
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False

def insert_article(article):
    """Insert an article into Supabase."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=30
    )
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            print(f"  ✓ Published: {result[0].get('headline', '')[:60]}...")
            return True
        print(f"  ✓ Published: {article['headline'][:60]}...")
        return True
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:200]}")
        return False

def get_best_image(person_names=None, commons_queries=None, pexels_query=None):
    """Multi-source image search. Returns (url, attribution) or (None, None)."""
    candidates = []

    # Wikipedia person images
    if person_names:
        for name in person_names:
            img = fetch_wikipedia_person_image(name)
            if img and validate_image(img):
                candidates.append((img, "Wikimedia Commons", f"wikipedia:{name}"))

    # Wikimedia Commons
    if commons_queries:
        for q in commons_queries:
            results = fetch_wikimedia_commons_images(q, limit=3)
            for r in results:
                url = r.get("url") or r.get("original_url")
                if url and validate_image(url):
                    candidates.append((url, "Wikimedia Commons", f"commons:{q}"))
                    break  # Take first valid per query
            time.sleep(1)  # Rate limit

    # Pexels fallback
    if pexels_query and not candidates:
        img = fetch_pexels_image(pexels_query)
        if img and validate_image(img):
            candidates.append((img, "Pexels", f"pexels:{pexels_query}"))

    if candidates:
        # Prefer Wikipedia/Commons over Pexels
        wiki = [c for c in candidates if "Wikimedia" in c[1]]
        if wiki:
            return wiki[0][0], wiki[0][1]
        return candidates[0][0], candidates[0][1]

    return None, None


# ============================================================
# ARTICLE 1: NITI Aayog Semiconductor Roadmap + ISM 2.0
# ============================================================
def write_article_1():
    print("\n=== Article 1: NITI Aayog Semiconductor Roadmap ===")

    headline = "India Just Published Its Semiconductor Roadmap. The Target: Half the Country's Chip Demand by 2035."
    subheadline = "NITI Aayog's 'Future of India's Semiconductor Industry' plan lays out a path from consumer to producer — with ISM 2.0, three Indian startups heading to France, and $206 billion in projected demand."
    slug = "niti-aayog-semiconductor-roadmap-ism-2-chip-demand-206-billion-2035-20260606"
    category = "news"

    body = """India has spent decades as one of the world's largest consumers of semiconductors. Now the government wants to make them at home.

NITI Aayog's Frontier Tech Hub released a strategy document this week titled "Future of India's Semiconductor Industry," laying out a roadmap to capture a significant share of India's own chip demand within the next decade. The plan lands alongside the India Semiconductor Mission 2.0, announced in the 2026–27 Union Budget, which targets advanced manufacturing at 3-nanometre and 2-nanometre technology nodes.

## The Scale of the Bet

India's semiconductor demand is projected to reach $206 billion by 2035, according to the Ministry of Electronics and Information Technology. Under the new roadmap, domestic plants are expected to meet roughly half of that demand by fiscal year 2035 — a radical shift for a country that currently imports the vast majority of its chips.

Finance Minister Nirmala Sitharaman called the roadmap "a clear declaration of India's intent to move decisively from being a major consumer of chips to becoming an indispensable part of the global semiconductor value chain." The plan focuses on advanced packaging, compound semiconductors, wide-bandgap materials, and AI-native chip design — segments where India believes it can build defensible positions rather than chasing established leaders.

## Factories Are Already Rising

The strategy does not exist in a vacuum. Tata Electronics, in partnership with Taiwan's Powerchip Semiconductor Manufacturing Corp, is building a fabrication plant in Dholera, Gujarat, with an investment of approximately ₹91,000 crore. Micron Technology is constructing an assembly and test facility in Sanand. Foxconn has committed to chip packaging operations.

Under ISM 1.0, the government allocated ₹76,000 crore in incentives. ISM 2.0 expands that with a focus on indigenous design capabilities, workforce development, and deeper integration into the global supply chain. The Design Linked Incentive scheme has already supported 24 startups and facilitated 16 tape-outs, including six chips fabricated at advanced foundry nodes.

## The Diaspora Connection

For the estimated 1.5 million Indians working in the global semiconductor industry — many of them in design centres across Silicon Valley, Austin, and Munich — the roadmap signals a viable path home. Ashwini Vaishnaw, the IT Minister, framed the mission in generational terms: "As the Prime Minister guided us, this is a 20-year journey."

Three Indian semiconductor startups — VerveSemi, AGNIT Semiconductors, and Netrasemi — have been selected to represent the country at Bharat Innovates 2026 in Nice, France, from June 14 to 16. It is the kind of showcase that would have been unthinkable five years ago, when Indian founders had to begin investor meetings by explaining what a semiconductor was.

## Why It Matters Now

The timing is shaped by geopolitics as much as economics. Global dependence on Taiwan for advanced chip fabrication has become a strategic vulnerability that every major economy is trying to hedge. The U.S. CHIPS Act, Europe's Chips Act, and Japan's semiconductor revival plan have all poured billions into onshoring production. India's entry into this race is late but not without advantages: a deep engineering talent pool, a growing domestic market, and a government willing to offer 20-year tax holidays for semiconductor ventures.

The risk is execution. India has announced chip ambitions before — a 2014 fab proposal never broke ground. The difference this time, proponents argue, is that actual construction is underway and real money is flowing.

Intel signed a memorandum of understanding in late May to establish an advanced packaging glass-core substrate manufacturing facility in eastern India. Reliance and Adani have committed roughly $110 billion and $100 billion respectively to AI and data infrastructure. The ecosystem is no longer theoretical.

Whether India can close the gap between roadmap and reality will depend on navigating power supply constraints, water availability for fabs, customs bottlenecks, and the sheer complexity of semiconductor manufacturing. But the direction of travel is unmistakable: India is building, not just buying."""

    # Image sourcing
    img_url, img_attr = get_best_image(
        person_names=["Ashwini Vaishnaw"],
        commons_queries=["India semiconductor fab", "NITI Aayog"],
        pexels_query="semiconductor chip manufacturing"
    )

    if not img_url:
        print("  ⚠ No valid image found, trying additional search...")
        img_url, img_attr = get_best_image(
            pexels_query="microchip semiconductor wafer"
        )

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "slug": slug,
        "body": body,
        "category": category,
        "vertical": "technology",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": img_url or "",
        "image_caption": "Ashwini Vaishnaw, India's IT Minister, has called the semiconductor mission a 20-year journey" if img_attr == "Wikimedia Commons" and img_url else "A semiconductor wafer during fabrication — India aims to produce half its chip demand domestically by 2035",
        "image_attribution": img_attr or "",
        "is_editorial": False,
        "sources": json.dumps([
            "NITI Aayog Frontier Tech Hub semiconductor roadmap release",
            "Ministry of Electronics and Information Technology (MeitY)",
            "Reuters India",
            "YourStory Bharat Innovates 2026 coverage",
            "DIGITIMES Asia"
        ])
    }

    return insert_article(article)


# ============================================================
# ARTICLE 2: US-India Trade Deal by Mid-July
# ============================================================
def write_article_2():
    print("\n=== Article 2: US-India Trade Deal by Mid-July ===")

    headline = "India and the US Are '99 Percent Done' on a Trade Deal. The First Tranche Could Land by Mid-July."
    subheadline = "Commerce Minister Piyush Goyal says both sides are 'fast-moving towards closing all open ends' after a week of intensive talks in New Delhi — even as Washington slaps a new 12.5% tariff proposal on Indian imports."
    slug = "us-india-trade-deal-first-tranche-mid-july-piyush-goyal-brendan-lynch-20260606"
    category = "news"

    body = """India and the United States are on the verge of executing the first phase of a bilateral trade agreement, Commerce and Industry Minister Piyush Goyal said on Friday, putting a mid-July target on a deal that has been months in the making.

"By sometime in the middle of next month or so, we should be in a position to execute a very, very vibrant first tranche," Goyal told reporters in Visakhapatnam after a seafood exports workshop. He described the initial phase as one that "will give preferential access to India over our competitors."

## The Negotiations

A U.S. trade delegation led by chief negotiator Brendan Lynch was in New Delhi from June 2 to 4 for intensive talks with India's chief negotiator Darpan Jain, an additional secretary in the Department of Commerce. The discussions covered trade in goods, non-tariff measures, customs facilitation, and economic security alignment.

The framework for the deal was announced during Prime Minister Narendra Modi's visit to Washington on February 3, and U.S. Ambassador to India Sergio Gor recently said that 99 percent of the details had been finalised. "Small commas and full stops are being discussed," Goyal said, adding that a higher-level U.S. delegation — likely led by U.S. Trade Representative Jamieson Greer — is expected in India by the end of June.

President Trump, speaking at the White House on Thursday, struck a conciliatory note: "For years, India took advantage of the United States... But we will get to a deal. I like your Prime Minister a lot."

## The Complication

The warm words contrast with a sharp move from Washington earlier in the week. On Wednesday, the U.S. proposed an additional 12.5 percent tariff on imports from India under Section 301 proceedings, citing the country's alleged failure to curb goods made with forced labour. India was among 60 economies named in the action.

India's Commerce Ministry said it "remains engaged" with the U.S. on the Section 301 proceedings while pursuing the trade framework in parallel. The dual-track approach — negotiating a preferential deal while facing punitive tariffs — reflects the broader complexity of the U.S.-India trade relationship, which hit $191 billion in bilateral goods trade last year.

## What NRIs Should Watch

For the Indian diaspora, particularly those in trade, manufacturing, and agriculture, the first tranche could have tangible effects. The deal is expected to lower barriers for Indian exports in sectors where the country has competitive advantages — textiles, seafood, pharmaceuticals, and IT services — while potentially opening India's market to more American agricultural products and defence equipment.

The agreement also has implications for the rupee. With the currency under pressure from elevated oil prices and record foreign fund outflows triggered by the Iran war, a trade deal that boosts dollar inflows through exports could provide a stabilising anchor. The Reserve Bank of India held rates steady on Friday and separately announced measures to attract foreign capital, including scrapping capital gains tax on government bond interest for foreign institutional investors.

## The Bigger Picture

The U.S. and India reached an initial understanding on a trade deal in February, but negotiations slowed after the Supreme Court struck down Trump's sweeping tariff measures. They gathered pace again this week, and both sides now appear to be racing against a political clock: Trump faces midterm pressures at home, while Modi's government wants to demonstrate that its diplomatic relationship with Washington yields economic results.

The initial trade deal was once considered slow-moving by the standards of both governments. Goyal reframed it on Friday as something more like a sprint: "We had excellent discussions," he said. "We are fast-moving towards closing all the open ends."

If the mid-July target holds, it would make this the fastest bilateral trade agreement India has executed since the India-Oman Comprehensive Economic Partnership Agreement, which was announced the same week and zeroed out tariffs on 98 percent of bilateral trade."""

    # Image sourcing
    img_url, img_attr = get_best_image(
        person_names=["Piyush Goyal"],
        commons_queries=["India US trade agreement", "Piyush Goyal minister"],
        pexels_query="India USA trade flags"
    )

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "slug": slug,
        "body": body,
        "category": category,
        "vertical": "economy",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": img_url or "",
        "image_caption": "Commerce Minister Piyush Goyal confirmed the mid-July timeline for the first phase of the bilateral trade pact" if "Wikimedia" in (img_attr or "") else "India and the US are racing to finalise the first tranche of a bilateral trade agreement by mid-July",
        "image_attribution": img_attr or "",
        "is_editorial": False,
        "sources": json.dumps([
            "Reuters India",
            "Press Trust of India via Outlook Business",
            "Bloomberg Law",
            "IANS via The Indian Eye",
            "White House pool report"
        ])
    }

    return insert_article(article)


# ============================================================
# ARTICLE 3: Indian Americans Meet DOJ/FBI on Hindu Hate Crimes
# ============================================================
def write_article_3():
    print("\n=== Article 3: Indian Americans Meet DOJ/FBI on Hindu Hate Crimes ===")

    headline = "Silicon Valley's Indian Americans Just Took the Hate Crime Crisis to the FBI's Door"
    subheadline = "Two dozen community leaders met senior DOJ, FBI, and local police officials this week in San Francisco, demanding action after a wave of vandalism targeting Hindu and Jain temples across California."
    slug = "silicon-valley-indian-americans-doj-fbi-hate-crimes-hindu-temples-california-20260606"
    category = "news"

    body = """A group of prominent Indian Americans in Silicon Valley held an extraordinary meeting this week with senior officials from the Department of Justice, the FBI, and local police departments to demand action on what they describe as a mounting crisis of hate crimes targeting the Hindu community in California.

The meeting, organised by community leader Ajai Jain Bhutoria, brought together roughly two dozen Indian Americans at the table with Vincent Plair and Harpreet Singh Mokha from the DOJ's Community Relations Service, FBI field agents, and police officials from San Francisco, Milpitas, Fremont, and Newark.

## A Pattern of Attacks

The meeting follows a sharp escalation in anti-Hindu vandalism across the Bay Area. Three Hindu temples have been vandalised in three weeks, with graffiti targeting the community spray-painted on walls and entrances. At least one incident involved Khalistan-related slogans, raising concerns about the spillover of geopolitical tensions onto American soil.

During the meeting, Indian Americans expressed what multiple attendees described as "deep displeasure and dissatisfaction" that law enforcement agencies have been unable to take meaningful action against individuals and groups they allege are using U.S. soil to promote activities hostile to India.

The Department of Justice announced in late May that it had opened a civil rights investigation into the temple attacks, making it the first federal probe into anti-Hindu hate crimes in the Bay Area. But community members say the response has been too slow and the pattern too clear to dismiss as isolated incidents.

## The National Context

The Silicon Valley meeting reflects a broader anxiety across the Indian American community. Nationally, anti-Hindu hate crimes have risen sharply over the past two years, according to data compiled by the Hindu American Foundation. The organisation documented more than 180 incidents in 2025, ranging from temple vandalism and online threats to physical assaults — a figure that advocacy groups say significantly undercounts the actual number because many incidents go unreported.

California, home to the largest concentration of Indian Americans in the country, has been a particular flashpoint. The state's South Asian population spans religious, linguistic, and political lines, and tensions between Hindu and Sikh diaspora groups over the Khalistan movement have surfaced repeatedly in community spaces, city council meetings, and now, law enforcement briefings.

## What the Community Is Asking For

Attendees at the San Francisco meeting outlined several demands: faster federal investigation of the temple attacks, greater local police presence around places of worship, the designation of the vandalism as hate crimes rather than property damage, and a broader investigation into whether the attacks are coordinated.

They also raised the question of foreign influence, arguing that some of the anti-India rhetoric circulating in diaspora communities is being amplified by networks operating from outside the United States. The DOJ officials reportedly took note of the concerns but made no specific commitments during the meeting.

## Why It Matters for NRIs

For the roughly 4.8 million Indian Americans in the United States — including more than 600,000 in California alone — the hate crime debate touches on questions of belonging, safety, and political representation. The community has become the wealthiest and most educated immigrant group in the country, with outsized influence in technology, medicine, and finance. But that economic success has not insulated it from targeted hostility.

The meeting also underscores a generational shift. First-generation immigrants who might have quietly tolerated slights are now organising, meeting federal law enforcement, and demanding institutional accountability. Bhutoria, who has been involved in Democratic Party politics and community organising for years, framed the meeting as a turning point: the community is no longer willing to wait for the next incident before raising its voice.

The DOJ's Community Relations Service, which was created under the Civil Rights Act of 1964, typically mediates disputes and builds trust between law enforcement and communities. Its involvement signals that the federal government recognises the severity of the situation — even if concrete enforcement actions have yet to follow.

For Silicon Valley's Indian Americans, the message is clear: the temples are not just buildings. They are the community's most visible institutions, and an attack on them is experienced as an attack on the community itself."""

    # Image sourcing
    img_url, img_attr = get_best_image(
        commons_queries=["Hindu temple California", "Hindu temple United States", "Silicon Valley Indian community"],
        pexels_query="Hindu temple United States"
    )

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "slug": slug,
        "body": body,
        "category": category,
        "vertical": "diaspora",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": img_url or "",
        "image_caption": "A Hindu temple in California — three Bay Area temples have been vandalised in three weeks" if img_url else "",
        "image_attribution": img_attr or "",
        "is_editorial": False,
        "sources": json.dumps([
            "The Indian Eye San Francisco bureau",
            "Department of Justice Community Relations Service",
            "Hindu American Foundation hate crime data",
            "FBI field office reports",
            "Census Bureau American Community Survey"
        ])
    }

    return insert_article(article)


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print(f"News writer starting at {datetime.now(timezone.utc).isoformat()}")
    print(f"Supabase URL: {SUPABASE_URL[:30]}...")

    results = []
    results.append(("Semiconductor Roadmap", write_article_1()))
    results.append(("US-India Trade Deal", write_article_2()))
    results.append(("Hindu Hate Crimes DOJ", write_article_3()))

    print("\n=== SUMMARY ===")
    for name, success in results:
        status = "✓ Published" if success else "✗ Failed"
        print(f"  {status}: {name}")

    failed = sum(1 for _, s in results if not s)
    if failed:
        print(f"\n⚠ {failed} article(s) failed to publish")
        sys.exit(1)
    else:
        print(f"\n✓ All {len(results)} articles published successfully")
