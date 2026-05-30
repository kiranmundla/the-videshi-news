#!/usr/bin/env python3
"""
Videshi lifestyle-health + markets-finance writer.
Generates 2 articles (1 lifestyle-health, 1 markets-finance).
"""

import json, os, sys, uuid, subprocess, urllib.parse, re, requests
from datetime import datetime, timezone

# ── Supabase config ──────────────────────────────────────────────────────────
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

def sb_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

def sb_insert(table, row):
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers=sb_headers(),
        json=row,
        timeout=30
    )
    if r.status_code not in (200, 201):
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:500]}")
        return None
    data = r.json()
    return data[0] if isinstance(data, list) else data

# ── Image sourcing ───────────────────────────────────────────────────────────
def fetch_pexels_image(query, fallback_query=None):
    """Fetch image from Pexels using curl."""
    pexels_key = os.environ.get("PEXELS_API_KEY")
    if not pexels_key:
        env_path = os.path.expanduser("~/workspace/.env.pexels")
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    if "PEXELS_API_KEY" in line and "=" in line:
                        pexels_key = line.strip().split("=", 1)[1].strip().strip('"').strip("'")
    if not pexels_key:
        print("  ⚠ No Pexels API key found")
        return None

    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ["curl", "-sS", "-H", f"Authorization: {pexels_key}",
                 f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape"],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for p in photos:
                url = p.get("src", {}).get("large2x") or p.get("src", {}).get("original")
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image_url(url):
    """Validate image URL returns 200 with image content-type and >5KB."""
    try:
        result = subprocess.run(
            ["curl", "-sS", "-I", "-L", "--max-time", "10", url],
            capture_output=True, text=True, timeout=15
        )
        headers = result.stdout.lower()
        has_image_type = "content-type: image/" in headers
        cl_match = re.search(r'content-length:\s*(\d+)', headers)
        size_ok = True
        if cl_match:
            size_ok = int(cl_match.group(1)) > 5000
        has_200 = "200 ok" in headers or "http/2 200" in headers
        return has_200 and has_image_type and size_ok
    except:
        return False

# ── Article definitions ──────────────────────────────────────────────────────
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

articles = []

# ── ARTICLE 1: lifestyle-health — AI cognitive decline ────────────────────────
articles.append({
    "headline": "Just 10 Minutes of AI Use Can Measurably Weaken Your Problem-Solving Skills. A New Study Says the Damage May Compound Over Time.",
    "subheadline": "Participants who asked ChatGPT for direct answers performed significantly worse when the tool was taken away. Those who used it for hints did not. The distinction matters for every knowledge worker in the diaspora.",
    "slug": "ai-use-10-minutes-cognitive-decline-problem-solving-study-south-asian-tech-professionals-20260530",
    "category": "lifestyle-health",
    "vertical": "health",
    "urgency": "daily",
    "tags": ["AI", "cognitive decline", "problem solving", "ChatGPT", "brain health", "tech workers"],
    "diaspora_angle": "Indian Americans are the most tech-forward ethnic group in the US, with disproportionate representation in engineering, data science, and product management — exactly the roles where AI tools are most deeply embedded. The study's findings directly challenge the efficiency narrative that many diaspora professionals have built their careers around.",
    "topic_title": "AI Use and Cognitive Decline: 10-Minute Study",
    "body": """The pitch for artificial intelligence in the workplace has always been efficiency. Automate the mundane. Free up the mind for higher-order thinking. A study published this week suggests the opposite may be happening — and that it takes remarkably little exposure to start.

Researchers found that just 10 to 15 minutes of interaction with an AI assistant produced measurable impairments in participants' ability to solve problems independently. The effect was not subtle. When the AI was removed, those who had used it performed significantly worse than those who had never been given access to it at all.

## The Study

The experiment was straightforward. Participants were divided into two groups. One group solved a series of reasoning and comprehension problems with access to an AI tool. The other worked without it. After the assisted phase, both groups were given a new set of problems — this time, nobody had AI access.

The results were striking. Participants who had used AI showed a sharp drop in their solve rate and a significant increase in the number of problems they simply skipped. The researchers described it as a measurable erosion of "independent performance and persistence — capacities that are foundational to life-long learning."

## How You Use It Matters

The study's most important finding was not that AI hurts cognition across the board. It was that the *way* people used it determined the damage.

Sixty-one per cent of AI-assisted participants reported asking the tool directly for solutions — essentially outsourcing the thinking entirely. This group showed the sharpest decline in independent performance. But the remaining participants, who used AI for hints, clarification, or partial guidance rather than complete answers, did not experience the same cognitive drop.

The distinction is critical. Using AI as a crutch degrades your ability to think without it. Using it as a scaffold — a tool that supports but does not replace reasoning — appears to leave cognitive function intact.

## The Compounding Risk

The researchers warned that their findings likely understate the real-world problem. If 10 minutes of AI interaction produces measurable erosion, the cumulative effects of daily use over months or years "may be profound and difficult to reverse."

A survey conducted last year found that 56 per cent of American adults use AI tools, with 28 per cent using them at least once a week. Among South Asian professionals in the US tech sector, the adoption rate is almost certainly higher. Indian Americans are disproportionately represented in engineering, data science, and product management roles where AI tools like ChatGPT, Copilot, and Claude are now embedded into daily workflows.

Previous research has suggested that heavy AI reliance could contribute to what some neuroscientists have called a "dementia crisis" — not dementia caused by AI directly, but a weakening of the brain systems responsible for curiosity, sustained attention, high-order reasoning, and executive function. Critics counter that similar fears were raised about calculators, GPS, and smartphones, none of which triggered a cognitive apocalypse.

The study authors acknowledge the comparison but argue that AI is fundamentally different. "Current AI systems represent a new kind of cognitive scaffold," they wrote. "One that solves anything, rarely refuses to help, and delivers answers instantly."

## What This Means for the Diaspora

For Indian American professionals — a community that has built its economic identity on intellectual rigour and problem-solving ability — the implications are worth sitting with. The same tools that make you faster at work may be quietly making you worse at thinking.

The study does not argue for abandoning AI. It argues for using it deliberately. Ask for frameworks, not answers. Request explanations, not solutions. Treat it as a sparring partner, not a substitute. The difference between those two approaches, according to this research, is the difference between cognitive growth and cognitive erosion.

The most productive people in any field have always been the ones who do the hard thinking themselves. AI does not change that. If anything, it raises the stakes.

**Sources:** New York Post (May 28, 2026); Frontiers in Education (2026); Sternberg, R.J., "Does AI increase cognitive abilities, decrease them, or a little bit of each?"
""",
    "sources": ["New York Post (May 28, 2026)", "Frontiers in Education (2026)", "Sternberg R.J. (2026)"],
    "image_query": "person thinking problem solving brain",
    "image_fallback": "artificial intelligence technology thinking"
})

# ── ARTICLE 2: markets-finance — Oil forecasts / structural shift ─────────────
articles.append({
    "headline": "Oil Analysts Have Raised Their 2026 Forecasts for the Third Time. The Era of $60 Brent May Be Over.",
    "subheadline": "Brent is now forecast to average $90.44 a barrel this year, up 40 per cent from February estimates. Middle East crude exports have halved. Even a ceasefire will not undo the structural damage quickly. Here is what NRI investors should understand.",
    "slug": "oil-price-forecast-2026-brent-90-iran-war-india-nri-rupee-inflation-impact-20260530",
    "category": "markets-finance",
    "vertical": "finance",
    "urgency": "daily",
    "tags": ["oil prices", "Brent crude", "Iran war", "India economy", "rupee", "NRI investors", "RBI", "Strait of Hormuz"],
    "diaspora_angle": "For NRIs with India exposure through mutual funds, NRE/NRO deposits, or direct equity holdings, elevated oil prices are the single biggest macro variable. A weaker rupee erodes dollar-denominated returns on Indian assets, remittances buy less due to fuel-driven domestic inflation, and rate-sensitive sectors face headwinds if the RBI is forced to hike.",
    "topic_title": "Oil Price Forecasts Raised Again — NRI Impact",
    "body": """A monthly Reuters poll of 33 economists and analysts, published on Friday, shows that the consensus forecast for Brent crude in 2026 has been raised for the third consecutive time since the Iran war began at the end of February. The average forecast now stands at $90.44 per barrel, up from $86.38 last month and $63.85 in February — a 40 per cent increase in three months.

US crude (WTI) is seen averaging $84.63 per barrel, up from $60.38 before the conflict.

For India — the world's third-largest crude importer — these numbers are not abstract. They are the single largest variable driving the rupee, inflation, the current account deficit, and by extension the returns on virtually every asset class that NRI investors hold.

## What Happened to Oil

The mechanics are simple but the consequences are vast. When the US and Israel struck Iran on February 28, the Strait of Hormuz — a narrow waterway carrying roughly a fifth of the world's oil and gas supply — was effectively closed to normal shipping. Brent and WTI hit four-year highs above $126 and $119 respectively.

Data from Kpler shows that monthly crude oil exports from the Middle East have dropped from an average of about 18.3 million barrels per day before the crisis to less than half that level — approximately 8.8 million bpd since March.

Oil prices have since pulled back from their peaks. Brent fell 19 per cent in May, touching $92 a barrel on Friday — its lowest in six weeks — on reports that the US and Iran have reached a tentative agreement to extend a ceasefire by 60 days and lift restrictions on shipping through the Strait.

But analysts are nearly unanimous that a ceasefire does not mean a return to normal.

## Why $60 Oil May Not Come Back

"Oil getting back to the $60 level is effectively off the table even if this latest peace deal somehow gets resolved," said Ben McMillan, chief investment officer at IDX Advisors. "There's a recovery period for oil supply of at least three months in the best case, probably six months before we get everything back online, and then there's going to be this baked-in geopolitical risk premium for oil that is going to endure for years."

ING analysts noted that even if the Strait were reopened, ship owners may hesitate to send vessels back into the Persian Gulf, fearing the ceasefire could collapse and trap ships again. Upstream production recovery will be gradual, not instantaneous.

Commerzbank has set its year-end Brent forecast at $85 a barrel, assuming the Strait remains closed to normal shipping for another two months. Surabhi Menon at EIU in India said prices may inch higher through July but are unlikely to reach record levels, assuming the war stays in its current state.

Japan, which relies heavily on Middle Eastern oil, registered a 66 per cent drop in crude oil imports in its latest monthly data. India has not published comparable figures yet, but the pattern is similar: a scramble for non-Gulf supply at premium prices.

## What This Means for India

Every $10 increase in Brent crude widens India's current account deficit by approximately 0.4 per cent of GDP. At $90 versus the pre-war $60, that is a roughly 1.2 per cent of GDP hit — a figure that explains much of the rupee's 5-6 per cent decline this year.

The rupee hit 97 per dollar on May 22 before RBI intervention pulled it back to 95 on Friday. The central bank has been burning through forex reserves to defend the currency — reserves fell to a one-year low of $681 billion — and a growing number of economists now expect at least one rate hike before year-end.

Elevated oil prices have also kept foreign investors away. Between March and May, overseas investors pulled over $24 billion from Indian debt and equities on a net basis. India's lack of an AI trade narrative — unlike the US, Taiwan, or South Korea — has made it harder to attract growth-seeking capital.

The RBI's monetary policy decision on June 5 is the next inflection point. Most economists polled by Reuters expect rates to stay unchanged at 5.25 per cent. But Capital Economics' base case is that the repo rate rises to 6.00 per cent before year-end, contingent on the crisis ending and energy prices falling back. "The risk," said Shilan Shah at Capital Economics, "is that it doesn't."

## What NRI Investors Should Consider

For NRIs with India exposure through mutual funds, NRE/NRO deposits, or direct equity holdings, the calculus has shifted.

**Rupee-denominated returns are being eroded.** A 5-6 per cent rupee depreciation wipes out a significant portion of nominal returns when converted to dollars, pounds, or Canadian dollars. If the rupee weakens further, the effective yield on NRE deposits — currently around 7 per cent — drops to 1-2 per cent in dollar terms.

**Rate-sensitive sectors are vulnerable.** If the RBI does hike, banking margins may benefit but real estate, infrastructure, and rate-sensitive consumption stocks will face headwinds.

**Energy importers are hurting; energy producers are not.** ONGC, Oil India, and Coal India have seen divergent performance. Downstream companies like Indian Oil and BPCL face margin compression from elevated crude costs that the government may not fully pass through to consumers.

**Remittances are cheaper to send but buy less.** A weaker rupee means more rupees per dollar sent home, but domestic inflation — driven partly by fuel costs — reduces purchasing power on the other end.

The bottom line: oil is not going back to $60 in any reasonable scenario. The structural premium is real. India's economy, currency, and markets are priced for that reality, but whether they are priced enough is the open question heading into June.

**Sources:** Reuters (May 30, 2026); MarketWatch (May 30, 2026); Capital Economics (May 2026); ING Commodities Research (May 2026)
""",
    "sources": ["Reuters (May 30, 2026)", "MarketWatch (May 30, 2026)", "Capital Economics (May 2026)", "ING Commodities Research (May 2026)"],
    "image_query": "oil barrel crude oil refinery industrial",
    "image_fallback": "petroleum oil tanker shipping"
})

# ── Process and insert ───────────────────────────────────────────────────────
print(f"\n{'='*60}")
print(f"Videshi Lifestyle/Markets Writer — {now}")
print(f"{'='*60}\n")

for i, article in enumerate(articles, 1):
    print(f"\n--- Article {i}/{len(articles)}: {article['headline'][:60]}... ---")
    
    art_id = str(uuid.uuid4())
    topic_id = str(uuid.uuid4())
    
    # Image sourcing
    img_url = fetch_pexels_image(article["image_query"], article.get("image_fallback"))
    
    if img_url:
        if validate_image_url(img_url):
            print(f"  ✓ Image validated")
        else:
            print(f"  ✗ Image validation failed, dropping image")
            img_url = None
    
    # Word count
    word_count = len(article["body"].split())
    print(f"  Word count: {word_count}")
    if word_count < 400:
        print(f"  ✗ REJECTED: Below 400 word minimum")
        continue
    
    # Headline length
    headline_len = len(article["headline"])
    print(f"  Headline length: {headline_len} chars")
    if headline_len > 200:
        print(f"  ⚠ Headline too long, truncating")
        article["headline"] = article["headline"][:197] + "..."
    
    # Create topic first
    topic_row = {
        "id": topic_id,
        "canonical_title": article["topic_title"],
        "vertical": article["vertical"],
        "urgency": article["urgency"],
        "score_diaspora": 8,
        "score_significance": 7,
        "score_recency": 9,
        "score_source_avail": 8,
        "score_total": 32,
        "signal_count": 3,
        "status": "published",
        "keywords": article["tags"],
        "category": article["category"],
    }
    
    topic_result = sb_insert("p2_topics", topic_row)
    if not topic_result:
        print(f"  ✗ Failed to create topic, trying article without topic...")
        # Try inserting article anyway with a random topic_id - won't work with FK constraint
        continue
    print(f"  ✓ Topic created: {topic_id}")
    
    # Insert article
    row = {
        "id": art_id,
        "topic_id": topic_id,
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "slug": article["slug"],
        "category": article["category"],
        "vertical": article["vertical"],
        "urgency": article["urgency"],
        "tags": article["tags"],
        "diaspora_angle": article["diaspora_angle"],
        "body": article["body"].strip(),
        "sources": json.dumps(article["sources"]),
        "word_count": word_count,
        "status": "published",
        "published_at": now,
        "image_url": img_url,
        "image_attribution": "Pexels" if img_url and "pexels" in (img_url or "").lower() else None,
        "is_featured": False,
        "score_total": 32,
    }
    
    result = sb_insert("p2_articles", row)
    if result:
        print(f"  ✓ Published: {article['slug']}")
        print(f"    ID: {art_id}")
        print(f"    Category: {article['category']}")
    else:
        print(f"  ✗ Failed to publish: {article['slug']}")

print(f"\n{'='*60}")
print("Writer run complete.")
print(f"{'='*60}")
