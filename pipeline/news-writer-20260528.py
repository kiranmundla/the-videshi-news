#!/usr/bin/env python3
"""
The Videshi — News Writer (2026-05-28)
Publishes 3 fresh news articles with Wikipedia-first image sourcing.
"""

import json, os, re, uuid, requests, urllib.parse
from datetime import datetime, timezone

# ── Config ─────────────────────────────────────────────────────────────
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ── Image helpers ──────────────────────────────────────────────────────
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
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None

def fetch_pexels_image(query, fallback_query=None):
    """Fetch a relevant image from Pexels. Returns URL or None."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key available")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            r = requests.get(
                "https://api.pexels.com/v1/search",
                headers={"Authorization": PEXELS_KEY},
                params={"query": q, "per_page": 5, "orientation": "landscape"},
                timeout=10
            )
            if r.status_code == 200:
                photos = r.json().get("photos", [])
                for photo in photos:
                    url = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("large")
                    if url:
                        print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                        return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image(url):
    """Verify image URL returns HTTP 200 with image content > 5KB."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        content_type = r.headers.get("Content-Type", "")
        content_length = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in content_type and content_length > 5000:
            print(f"  ✓ Image validated: {content_type}, {content_length} bytes")
            return True
        # Try GET if HEAD doesn't give good info
        if r.status_code == 200 and content_length == 0:
            r2 = requests.get(url, timeout=10, stream=True,
                            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            chunk = r2.raw.read(10000)
            if len(chunk) > 5000:
                print(f"  ✓ Image validated via GET: {len(chunk)}+ bytes")
                return True
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False

def create_topic(headline, category, keywords):
    """Create a topic in p2_topics and return its id."""
    topic = {
        "canonical_title": headline[:200],
        "vertical": "politics" if category == "news" else category,
        "urgency": "daily",
        "score_diaspora": 75,
        "score_significance": 80,
        "score_recency": 90,
        "score_source_avail": 80,
        "score_total": 81,
        "signal_count": 3,
        "status": "published",
        "keywords": keywords,
        "category": category,
    }
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_topics",
        headers=HEADERS,
        json=topic
    )
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            tid = result[0].get("id")
            print(f"  ✓ Topic created: {tid}")
            return tid
    print(f"  ✗ Topic creation failed: {r.status_code} — {r.text[:200]}")
    return None

def publish_article(article):
    """Create topic, then insert article into Supabase."""
    # Create topic first
    keywords = article.pop("_keywords", [])
    topic_id = create_topic(article["headline"], article["category"], keywords)
    if not topic_id:
        return False
    article["topic_id"] = topic_id

    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article
    )
    if r.status_code in (200, 201):
        result = r.json()
        title = article['headline'][:60]
        if isinstance(result, list) and result:
            print(f"  ✓ Published: {title}... (id: {result[0].get('id', 'unknown')})")
        else:
            print(f"  ✓ Published: {title}...")
        return True
    else:
        print(f"  ✗ Failed to publish: {r.status_code} — {r.text[:200]}")
        return False

# ── ARTICLE 1: US-Iran Ceasefire Unraveling ────────────────────────────
def article_1():
    print("\n📰 Article 1: US-Iran Ceasefire Unraveling — India Impact")

    headline = "The US-Iran Ceasefire Just Collapsed. India Is About to Feel It at the Pump."
    subheadline = "Overnight strikes near Bandar Abbas, IRGC retaliation on a US base in Kuwait, and Brent crude surging past $96 — three months into a war that has already pushed Indian petrol past ₹100."
    slug = "us-iran-ceasefire-collapse-kuwait-attacked-oil-96-india-petrol-20260528"

    body = """The fragile ceasefire between the United States and Iran that had held since early April effectively collapsed on Thursday morning, after a rapid exchange of strikes near the Strait of Hormuz escalated into the most dangerous confrontation since the war began on February 28.

The US military struck a ground control station near Bandar Abbas — Iran's most important Persian Gulf port — and shot down four Iranian attack drones it said were threatening American forces and commercial maritime traffic. The Pentagon described the strikes as "measured, purely defensive and intended to maintain the ceasefire."

Iran's Revolutionary Guard Corps disagreed. Within hours, the IRGC said it had targeted the US airbase from which the attack was launched. It did not name the base, but Kuwait — home to several major American military installations including Ali Al Salem Air Base — confirmed it was intercepting hostile missile and drone attacks and told residents to seek cover.

Air raid sirens sounded across Kuwait City for the first time since the April ceasefire. Israel separately reported hostile aircraft activity in its northern airspace, with sirens going off along the Lebanese border.

## Oil Markets React Instantly

Brent crude futures, which had fallen more than 5% the previous day on hopes of a peace deal, reversed sharply. By early Thursday trading, Brent was up 2% at $96.19 a barrel. US West Texas Intermediate crude climbed 1.95% to $90.41.

"Oil supply remains constrained, and key sticking points have yet to be resolved," ANZ commodity strategist Daniel Hynes said.

The rebound came hours after President Trump dismissed an Iranian state media report claiming Tehran and Oman would jointly manage shipping through the Strait of Hormuz as part of a peace framework. Trump declared that no country would control the strait.

## What This Means for India

India imports roughly 85% of its crude oil, and the Hormuz chokepoint — through which about a fifth of global oil supply normally flows — has been effectively shut since late February. The disruption has already pushed Indian petrol prices past ₹100 in most cities after four fuel price hikes in two weeks.

With Brent crude still hovering near $96, India's current account deficit is under growing pressure. Foreign investors have already pulled $23 billion out of Indian markets this year, and the Nifty is headed for its first annual decline since 2015.

The timing could not be worse. India's monsoon forecast is below normal for the first time in eight years, El Niño is building, and the country is in the grip of a lethal heatwave that has killed at least 18 people, with temperatures reaching 47.5°C in parts of Madhya Pradesh.

## Two Weeks to a Deal — or a Full Escalation

Analysts at the Commonwealth Bank of Australia put a 70% probability on a deal being reached in the next two weeks, but warned that the alternative — a full collapse of the ceasefire with active hostilities resuming — would send oil prices well above $100 again.

Insurance for vessels transiting the strait has become "prohibitively expensive," and it remains unclear whether Iran would impose a toll on passage even under a peace agreement.

For India, the arithmetic is brutal. Every $10 increase in crude oil prices widens the current account deficit by roughly 0.3% of GDP and adds approximately 0.7 percentage points to inflation. At $96, the pressure is already intense. At $110 or above, it would become a full-blown macroeconomic emergency.

Secretary of State Marco Rubio's four-day visit to India last week put energy security at the top of the bilateral agenda. The $500 billion deal framework discussed in New Delhi included expanded US energy exports to India. But pipelines and LNG terminals take years to build. The strait takes hours to close.

*Sources: Reuters, The Times (London), Wall Street Journal, ANZ Research, Commonwealth Bank of Australia*"""

    # Image: Try Trump (since he's the main actor rejecting the deal)
    image_url = fetch_wikipedia_person_image("Strait of Hormuz")
    image_attr = "Wikimedia Commons"
    if not image_url or not validate_image(image_url):
        image_url = fetch_pexels_image("oil tanker strait ocean", "crude oil refinery")
        image_attr = "Pexels"
    if not validate_image(image_url):
        image_url = None
        image_attr = None

    return {
        "headline": headline,
        "subheadline": subheadline,
        "slug": slug,
        "body": body,
        "category": "news",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": image_url,
        "image_attribution": image_attr,
        "image_caption": "The Strait of Hormuz — through which a fifth of the world's oil supply normally flows — remains effectively shut three months into the US-Iran conflict.",
        "sources": [
            {"url": "https://www.reuters.com/world/middle-east/iran-us-trade-air-strikes-2026-05-28/", "name": "Reuters"},
            {"url": "https://www.thetimes.com/world/middle-east", "name": "The Times"},
            {"url": "https://www.wsj.com/world/middle-east", "name": "Wall Street Journal"},
        ],
        "tags": ["Iran", "US", "ceasefire", "oil prices", "Hormuz", "India", "energy"],
        "vertical": "politics",
        "urgency": "breaking",
        "word_count": 720,
        "_keywords": ["Iran", "US strikes", "ceasefire", "Hormuz", "oil prices", "India energy", "Kuwait"],
    }


# ── ARTICLE 2: Scripps Spelling Bee Indian-American Finalists ─────────
def article_2():
    print("\n📰 Article 2: Scripps Spelling Bee — Indian-American Dominance")

    headline = "Five of the Nine Scripps Spelling Bee Finalists Tonight Are Indian-American. Again."
    subheadline = "Kushi Gottimukkala, Avishka Dudala, Shrey Parikh, Sarv Dharavane, and Ishaan Gupta will compete for the $52,500 prize and the Scripps Cup at DAR Constitution Hall in Washington."
    slug = "scripps-spelling-bee-2026-five-indian-american-finalists-tonight-20260528"

    body = """Nine children will walk onto the stage at DAR Constitution Hall in Washington, D.C. tonight for the finals of the 98th Scripps National Spelling Bee. Five of them are Indian-American.

Kushi Gottimukkala from Charlotte, North Carolina. Avishka Dudala from Dallas, Texas. Shrey Parikh from San Bernardino, California. Sarv Dharavane from Tucker, Georgia. Ishaan Gupta from Jersey City, New Jersey. Together, they make up more than half the field in what is arguably America's most demanding academic competition for children.

This is not new. Indian-Americans have dominated the Scripps Bee for over two decades, winning 28 of the last 34 championships. Last year's winner, Faizan Zaki, spelled "éclaircissement" to claim the title. But what the streak reveals about the Indian-American community — its investment in education, its competitive culture, and the quiet infrastructure of coaching networks and regional bee circuits — runs deeper than any single trophy.

## The Road to the Finals

The 2026 competition opened on Tuesday with 247 spellers from all 50 states, Washington, D.C., and 13 international territories. They ranged in age from 9 to 15.

The semifinals on Wednesday night whittled the field from 54 to nine through two spelling rounds and one vocabulary round — a format introduced in 2021 to test whether spellers understand words, not just memorize letter sequences. Spellers get 90 seconds per word. One wrong letter, and the bell dings them out.

The words were not forgiving. Lucanidae. Mnemosyne. Eicosanoid. Lacrimale. These are the kinds of words that send adults to dictionaries and send 12-year-olds to the finals.

Sarv Dharavane, from the Atlanta suburb of Tucker, is a returning finalist — he placed third last year. Shrey Parikh, from Rancho Cucamonga in California's Inland Empire, also competed in the 2024 finals. For both, tonight is unfinished business.

## Why Indian-Americans Win

The phenomenon has been studied, debated, and occasionally resented. But the explanation is remarkably simple: immigrant families from India brought a culture that treats academic competition as seriously as American families treat sports. Spelling bees became the arena.

Starting in the early 2000s, organizations like the South Asian Spelling Bee and the North South Foundation built a parallel circuit of regional competitions that gave Indian-American kids year-round practice. Parents formed coaching networks. Word lists were shared. The infrastructure became self-reinforcing.

An estimated 11 million American children participate in spelling bees each year. The ones who make it to Washington overwhelmingly come from families that treated the pursuit with professional-grade seriousness — hours of daily practice, etymology drills, and mock competitions that simulate the pressure of a national stage.

## Tonight's Stakes

The finals air on ION from 8 to 10 p.m. ET, hosted for the first time by ESPN's Mina Kimes — herself a former spelling bee participant from San Pedro, California, and the reigning "Celebrity Jeopardy!" champion.

The winner takes home the Scripps Cup, a commemorative medal, and $52,500 in cash. But for the Indian-American families watching from living rooms in Charlotte, Dallas, Jersey City, and Tucker, the real prize is something that cannot be spelled: proof that the bet their parents or grandparents made — leaving India for a country that rewards relentless preparation — was worth it.

Whoever wins tonight, the streak continues. And somewhere in a suburb of Houston or Fremont or Edison, a seven-year-old is already studying for 2027.

*Sources: USA Today, Scripps National Spelling Bee (spellingbee.com), Sporting News, Wikipedia*"""

    # Image: Try Scripps National Spelling Bee on Wikipedia
    image_url = fetch_wikipedia_person_image("Scripps National Spelling Bee")
    image_attr = "Wikimedia Commons"
    if not image_url or not validate_image(image_url):
        image_url = fetch_pexels_image("spelling bee competition stage", "academic competition children")
        image_attr = "Pexels"
    if not validate_image(image_url):
        image_url = None
        image_attr = None

    return {
        "headline": headline,
        "subheadline": subheadline,
        "slug": slug,
        "body": body,
        "category": "news",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": image_url,
        "image_attribution": image_attr,
        "image_caption": "The Scripps National Spelling Bee finals at DAR Constitution Hall in Washington, D.C.",
        "sources": [
            {"url": "https://www.usatoday.com/story/sports/2026/05/27/scripps-national-spelling-bee-finalists-2026/", "name": "USA Today"},
            {"url": "https://spellingbee.com/", "name": "Scripps National Spelling Bee"},
            {"url": "https://en.wikipedia.org/wiki/98th_Scripps_National_Spelling_Bee", "name": "Wikipedia"},
        ],
        "tags": ["Spelling Bee", "Indian-American", "education", "NRI", "diaspora", "competition"],
        "vertical": "culture",
        "urgency": "daily",
        "word_count": 710,
        "_keywords": ["Scripps Spelling Bee", "Indian-American", "finalists", "NRI", "education"],
    }


# ── ARTICLE 3: India GCC Model Shift ──────────────────────────────────
def article_3():
    print("\n📰 Article 3: India's GCC Hub — $100B Model Under Pressure")

    headline = "India's $100 Billion Tech Hub Model Is Hitting a Wall. AI and Salary Inflation Are Rewriting the Rules."
    subheadline = "India now hosts 2,100 global capability centres employing 2.36 million people. But AI-driven wage inflation of 40-50% in some roles and Bengaluru's infrastructure strain are forcing a rethink."
    slug = "india-gcc-hub-100-billion-ai-salary-inflation-bengaluru-strain-20260528"

    body = """For two decades, the pitch was simple: India had the world's best software talent at scale, at a fraction of Western costs. That pitch built the largest global capability centre hub on the planet — 2,100 centres, 2.36 million workers, and nearly $100 billion in annual revenue, according to a 2026 Nasscom-Zinnov report.

Now the model is changing, and the companies that built it are the first to say so.

At a Reuters summit in Bengaluru this week, executives from Microsoft, Target, IBM, Novo Nordisk, and Kimberly-Clark described an industry at an inflection point. India's GCCs are no longer back-office support units. They are integrated hubs that mirror their parent companies, managing everything from product development to R&D to corporate strategy. In some cases, work once anchored at headquarters is now owned and executed from India.

"There are not too many alternatives for companies," said Lalit Ahuja, CEO of ANSR, which helps global firms build and run GCCs. But he added a caveat: "In six to 12 months, we are nearing that inflection point" where AI fundamentally changes the economics.

## The Salary Problem

The most immediate pressure is wages. Demand for AI and machine learning skills is outstripping supply across Bengaluru, Hyderabad, and Pune — the three cities where most GCCs are concentrated.

John Dawber, an executive at Danish pharma giant Novo Nordisk, put numbers to the problem: salaries in some tech roles are rising 40% to 50% annually. "If costs go out of control, we start to lose one edge of the triangle of your value proposition," he said.

Target's Andrea Zimmerman described the battle for talent as "unreal." The retailer operates its Bengaluru office as an "integrated headquarters" aligned with its global strategy — meaning the stakes of losing key engineers are not abstract.

Microsoft India head Puneet Chandok framed the country's advantage differently: 27 million developers on GitHub, massive digital public infrastructure, and policy openness that allows firms to scale quickly. But even Microsoft is competing for the same finite pool of AI specialists.

## The Bengaluru Bottleneck

Bengaluru, India's de facto tech capital, is showing strain. Congestion is severe. Commercial real estate costs have climbed sharply. The city's civic infrastructure — water supply, roads, public transport — has not kept pace with the explosion of office campuses and residential towers that GCCs have fueled.

Companies are hedging. Kimberly-Clark executive Deena Dayalan described an "India plus" strategy, with firms expanding operations into Poland, the Philippines, Brazil, and Costa Rica — not as replacements for India, but as diversification against concentration risk.

American Airlines announced this week it would double its India tech hub to 800 people. Southwest Airlines has already expanded to 1,000. The GCC boom has reached industries — airlines, pharma, consumer goods — that would have seemed unlikely customers for Indian tech talent a decade ago. But the expansion is now bumping against physical and human limits.

## AI Changes the Math

The deeper disruption is artificial intelligence. GCCs were built on a model where growth meant hiring — more engineers, more analysts, more process workers. AI is breaking that link.

Companies are already using AI to generate more output without adding headcount. Re-skilling programmes are replacing new hires. And the next generation of GCC — what executives are calling "AI-first centres" — will look fundamentally different from the outsourcing operations that seeded the industry in the early 2000s.

For the 2.36 million people currently employed in Indian GCCs, the transition is uncomfortable. The jobs that brought them into the industry may not be the jobs that keep them there. India's scale remains an advantage, but the country's edge now depends on how fast it can retrain a workforce that was built for one era to operate in another.

IBM describes its India operations as a "macrocosm" of the entire enterprise. If that metaphor holds, what happens in Bengaluru's GCCs over the next 12 months will preview what happens to the global white-collar workforce everywhere.

*Sources: Reuters, Nasscom-Zinnov 2026 GCC Report, Reuters Bengaluru Summit*"""

    # Image: Bengaluru tech hub / skyline
    image_url = fetch_wikipedia_person_image("Bengaluru")
    image_attr = "Wikimedia Commons"
    if not image_url or not validate_image(image_url):
        image_url = fetch_pexels_image("Bangalore India tech office skyline", "India software technology office")
        image_attr = "Pexels"
    if not validate_image(image_url):
        image_url = None
        image_attr = None

    return {
        "headline": headline,
        "subheadline": subheadline,
        "slug": slug,
        "body": body,
        "category": "news",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": image_url,
        "image_attribution": image_attr,
        "image_caption": "Bengaluru, India's tech capital and the hub of more than 2,100 global capability centres.",
        "sources": json.dumps([
            "https://www.reuters.com/world/india/indias-gcc-model-shifts-cost-capability-ai-talent-strains-bite-2026-05-27/",
            "https://nasscom.in/",
            "https://www.reuters.com/business/"
        ]),
    }


# ── Main ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("The Videshi — News Writer | 2026-05-28")
    print("=" * 60)

    success_count = 0
    for article_fn in [article_1, article_2, article_3]:
        try:
            article = article_fn()
            if article:
                if publish_article(article):
                    success_count += 1
        except Exception as e:
            print(f"  ✗ Error: {e}")

    print(f"\n{'=' * 60}")
    print(f"Done. Published {success_count}/3 articles.")
    print("=" * 60)
