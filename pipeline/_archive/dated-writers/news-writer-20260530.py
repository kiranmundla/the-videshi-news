#!/usr/bin/env python3
"""News writer for The Videshi — 2026-05-30 evening batch."""

import json, os, re, sys, time, uuid, urllib.parse
from datetime import datetime, timezone

import requests

# ── Env ──────────────────────────────────────────────────────────────
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

PEXELS_KEY = None
pexels_env = os.path.expanduser("~/workspace/.env.pexels")
if os.path.exists(pexels_env):
    for line in open(pexels_env):
        if line.startswith("PEXELS_API_KEY="):
            PEXELS_KEY = line.strip().split("=", 1)[1].strip().strip('"').strip("'")

# ── Helpers ──────────────────────────────────────────────────────────

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
    """Fetch a relevant image from Pexels."""
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
                for p in photos:
                    url = p.get("src", {}).get("large2x") or p.get("src", {}).get("large")
                    if url:
                        print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                        return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image_url(url):
    """Validate that image URL returns 200 with image content > 5KB."""
    if not url:
        return False
    # Check for banned sources
    banned = ['fbcdn.net', 'cdninstagram.com', 'lookaside.fbsbx.com']
    if any(b in url for b in banned):
        print(f"  ✗ Banned image source: {url[:60]}")
        return False
    banned_params = ['_nc_ht=', '_nc_cat=', 'ccb=']
    if any(p in url for p in banned_params):
        print(f"  ✗ Banned Meta URL params: {url[:60]}")
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Some servers don't support HEAD, try GET with range
        if r.status_code in (200, 405, 403):
            r2 = requests.get(url, timeout=10, stream=True,
                             headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            ct2 = r2.headers.get("Content-Type", "")
            if r2.status_code == 200 and "image" in ct2:
                chunk = r2.raw.read(6000)
                if len(chunk) >= 5000:
                    return True
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False


def upload_to_supabase_storage(image_url, filename):
    """Download image and upload to Supabase storage bucket."""
    try:
        r = requests.get(image_url, timeout=15,
                        headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        if r.status_code != 200 or len(r.content) < 5000:
            print(f"  ✗ Download failed or too small: {len(r.content)} bytes")
            return None

        ct = r.headers.get("Content-Type", "image/jpeg")
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        resp = requests.post(
            upload_url,
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": ct,
                "x-upsert": "true",
            },
            data=r.content,
            timeout=30,
        )
        if resp.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ✗ Upload failed ({resp.status_code}): {resp.text[:200]}")
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return None


def insert_article(article):
    """Insert article into p2_articles."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=30,
    )
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) else data.get("id")
        print(f"  ✓ Inserted article: {article['slug']} (id={art_id})")
        return art_id
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return None


def patch_article(art_id, patch):
    """Patch an article by ID."""
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{art_id}",
        headers=HEADERS,
        json=patch,
        timeout=15,
    )
    if r.status_code in (200, 204):
        print(f"  ✓ Patched article {art_id}")
    else:
        print(f"  ⚠ Patch failed ({r.status_code}): {r.text[:200]}")


# ── Articles ─────────────────────────────────────────────────────────

ARTICLES = [
    {
        "headline": "India and Canada Just Launched a Trade Forum and Set a $50 Billion Target. A Year Ago They Were Not Even Talking.",
        "subheadline": "Commerce Minister Piyush Goyal's three-day visit to Ottawa and Toronto marked the most significant reset in India-Canada ties since the Nijjar crisis, with both sides pushing for a comprehensive trade deal by year-end.",
        "slug": "india-canada-trade-forum-50-billion-target-goyal-carney-cepa-reset-20260530",
        "category": "news",
        "status": "published",
        "sources": json.dumps([
            "IANS — Piyush Goyal highlights 'renewed momentum' in India-Canada ties, May 30 2026",
            "The Indian Eye — India and Canada launch Trade and Investment Forum, May 30 2026",
            "The Indian Eye — India-Canada Foreign Ministers speak to strengthen ties, May 29 2026",
            "The Indian Eye — Canadian HC discusses defence cooperation with Indian Defence Secretary, May 30 2026",
            "Reuters — Canada-India Joint Statement 2026 Trade and Investment Forum"
        ]),
        "body": """Less than eighteen months ago, India and Canada were locked in one of the worst diplomatic standoffs in their shared history. Ambassadors had been expelled. Intelligence accusations flew across oceans. Trade talks were frozen. The relationship, built over decades of diaspora ties and economic interdependence, seemed to be unraveling in real time.

On Saturday, Commerce Minister Piyush Goyal posted a video titled "Glimpses of my highly productive visit to Canada" — a three-day trip that included meetings with Prime Minister Mark Carney, Foreign Minister Anita Anand, and Trade Minister Maninder Sidhu. The two countries formally launched the Canada-India Trade and Investment Forum, set a target of $50 billion in bilateral trade by 2030, and recommitted to finishing negotiations on a Comprehensive Economic Partnership Agreement by the end of this year.

The current bilateral trade stands at roughly $8.5 billion. The $50 billion target is not just ambitious — it is a statement of intent that would have been unthinkable during the Trudeau era's final months.

## What Changed

The answer is almost entirely about personnel. Justin Trudeau's public accusation that India was involved in the killing of Hardeep Singh Nijjar — a claim India called malicious and baseless — made normal diplomatic engagement impossible. Trudeau's departure and Mark Carney's election in early 2026 created the opening both sides needed.

Carney visited India in February 2026. The two governments signed five Memorandums of Understanding covering energy, critical minerals, technology, AI, talent, culture, and defence. The rhetoric shifted from accusation to aspiration almost overnight.

External Affairs Minister S. Jaishankar spoke with Anita Anand — Canada's new Foreign Minister, who has Indian heritage — and wished her "a very successful tenure." Anand responded by expressing interest in "strengthening Canada-India ties, deepening economic cooperation, and advancing shared priorities." The diplomatic language was deliberate and warm.

## The Trade Forum

The newly launched Canada-India Trade and Investment Forum is designed to be a permanent platform for business leaders from both countries to forge commercial partnerships. The joint statement released during Goyal's visit highlighted cooperation opportunities in clean energy, critical minerals, agri-food, advanced manufacturing, digital technologies, and skills development.

Sidhu confirmed that Canada would lead a Team Canada Trade Mission to India later this year — a direct signal that Canadian businesses see India as a growth market worth prioritizing.

What makes this significant is the breadth of sectors on the table. Canada has natural advantages in energy, mining, and agriculture that complement India's needs. India has a massive, young workforce and a growing consumer market that Canadian companies want access to. The CEPA, if concluded, would formalize these complementarities into binding market access commitments.

## The Defence Angle

The rapprochement extends beyond trade. On Saturday, Canada's High Commissioner to India, Christopher Cooter, met with Defence Secretary Rajesh Kumar Singh to discuss next steps in India-Canada defence cooperation — a follow-up to commitments made during Carney's February visit.

The two countries agreed to increase cooperation in maritime security and identify opportunities for bilateral and multilateral naval activities. Canada's self-identification as a Pacific nation — and its desire for deeper Indo-Pacific engagement — aligns with India's own strategic priorities in the region.

## What It Means for the Diaspora

For the estimated 2.1 million people of Indian origin living in Canada — the largest visible minority group in the country — the diplomatic freeze was deeply uncomfortable. Sikh-Hindu community tensions, inflamed by the political crisis, affected workplaces, neighborhoods, and families. The thaw will not erase those divisions overnight, but it removes the governmental layer of hostility that was making everyday coexistence harder.

The trade implications are equally direct. Indian students in Canada, Indian-origin business owners, tech workers moving between the two countries, and families split across borders all benefit from normalized relations. The CEPA, if it goes through, would reduce barriers to movement for business professionals — a category that disproportionately includes Indian nationals.

The $50 billion trade target is aspirational, but the direction is clear. After a year of silence, India and Canada are talking again. The question is whether this momentum survives the inevitable frictions that any relationship this complex will produce.""",
        "image_search_person": "Piyush Goyal",
        "image_fallback_query": "India Canada trade diplomacy meeting",
        "image_attribution": None,
    },
    {
        "headline": "India Just Forecast Its Weakest Monsoon in 11 Years. El Niño, Heatwaves, and the Iran War Are All Making It Worse.",
        "subheadline": "The India Meteorological Department revised its monsoon forecast downward to 90 percent of the long-period average as an El Niño develops, fuel prices climb, and the Finance Ministry warned of accelerating inflation.",
        "slug": "india-weakest-monsoon-11-years-el-nino-heatwave-inflation-imd-forecast-20260530",
        "category": "news",
        "status": "published",
        "sources": json.dumps([
            "Reuters — India warns of weakest monsoon in 11 years, inflation risks rise, May 29 2026",
            "Reuters — India says retail inflation may accelerate on weak monsoon, fuel price rise, May 30 2026",
            "India News Stream — Below-normal southwest monsoon likely; IMD forecasts deficient rainfall across India, May 29 2026",
            "The Hindu BusinessLine — IMD forecasts below-normal monsoon rainfall, above-normal heatwaves in June, May 29 2026"
        ]),
        "body": """The India Meteorological Department delivered its second-stage monsoon forecast on Friday, and the numbers are bleak. Total rainfall during the June-to-September season is now expected to hit just 90 percent of the long-period average — down from the 92 percent projected in April, and the weakest reading since 2015.

The revision matters because the monsoon is not just weather in India. It is the single most important variable in the lives of roughly 600 million people who depend on farming. It determines crop yields, food prices, reservoir levels, and the broader trajectory of rural demand in a nearly $4-trillion economy.

## The El Niño Factor

The downgrade is driven primarily by developing El Niño conditions in the equatorial Pacific Ocean. El Niño — the periodic warming of sea surface temperatures — is known to suppress monsoon activity over the Indian subcontinent by altering atmospheric circulation patterns.

M. Ravichandran, secretary in the earth sciences ministry, told reporters that an El Niño is "likely to develop soon" and that its intensity is expected to range between moderate and strong during the latter half of the monsoon season. The Indian Ocean Dipole, another key climate driver, is expected to remain neutral — offering no counterbalancing boost to rainfall.

The regional breakdown is particularly concerning. While Northeast India is expected to receive normal rainfall, three of the four homogenous zones — Northwest India, Central India, and South Peninsular India — are all projected to get below-normal precipitation. The monsoon core zone, which covers most of India's rain-fed agricultural belt, is also forecast to receive deficient rainfall.

## Heatwaves Before the Rain

The monsoon has not yet reached Kerala by its expected onset date of May 26, though conditions are favorable for its advance in the coming days. The delayed arrival means that several Indian states continue to bake under extreme heat.

Temperatures have soared above 45 degrees Celsius across parts of Uttar Pradesh, Haryana, Punjab, Bihar, Odisha, Chhattisgarh, Gujarat, and Andhra Pradesh. The IMD has warned of an above-normal number of heatwave days in June across these states — conditions that typically ease only when the monsoon arrives in force.

A UC Berkeley study published this week estimated that a single day of extreme heat kills approximately 3,400 people across India — a number that underscores the human cost of delayed and deficient monsoon seasons.

## The Inflation Squeeze

On Saturday, India's Finance Ministry released its monthly economic report and explicitly warned that retail inflation could rise as a result of the weak monsoon forecast combined with recent fuel price hikes.

The report identified the Strait of Hormuz disruption — a consequence of the ongoing Iran war — as the "single most consequential variable" for India's external and price outlook. Iran's effective closure of the strait has pushed up global energy prices, and India, which imports over 80 percent of its crude oil, is absorbing the shock through higher fuel costs that are now feeding into transport, food, and manufacturing prices.

"A significant rainfall deficit coupled with current geopolitical conditions could translate into food inflation, weakening rural demand and aggregate growth," the Finance Ministry report stated.

Gaura Sengupta, chief economist at IDFC First Bank, estimated that a deficient monsoon could push average inflation closer to 5.5 percent — well above April's reading of 3.48 percent and closer to the Reserve Bank of India's upper tolerance limit of 6 percent.

## What This Means for NRIs

For Indians living abroad who send money home, the cascading effects are worth watching. Higher inflation erodes the purchasing power of remittances. A weaker rupee — likely if the RBI is forced to navigate between growth support and inflation control — could offset some of that for dollar-earners, but it also signals macroeconomic stress.

Families in rural India, where many NRIs have roots, face the most direct impact. Crop failures from deficient rainfall mean lower farm incomes, higher vegetable and grain prices at local markets, and potential water shortages in regions that depend entirely on monsoon recharge for drinking water and irrigation.

The Finance Ministry's own language — "cautious resilience" — captures the precariousness. India's economy is not in crisis, but the combination of geopolitical energy shocks, an El Niño-weakened monsoon, and rising upstream costs creates a narrow path for policymakers trying to sustain growth without letting prices spiral.

The monsoon is expected to advance into Kerala within the next few days. How June unfolds — whether the rains arrive with enough volume to offset the late start — will determine whether this forecast becomes a manageable shortfall or a full-blown agricultural crisis.""",
        "image_search_person": None,
        "image_fallback_query": "India monsoon rain farmland agriculture",
        "image_attribution": None,
    },
    {
        "headline": "Anthropic Just Raised More Money in a Single Round Than Every Indian Startup Has Raised in Four Years Combined.",
        "subheadline": "Indian startup VC funding hit its lowest weekly level of 2026 at just $66 million, as global AI capital concentration accelerates and India's ecosystem struggles to produce a credible AI challenger.",
        "slug": "anthropic-65-billion-indian-startup-funding-crisis-vc-drought-ai-gap-20260530",
        "category": "news",
        "status": "published",
        "sources": json.dumps([
            "YourStory — Weekly funding roundup: VC inflow drops to lowest level for the year, May 30 2026",
            "Inc42 — Daily Indian Startup Funding Roundup, May 27 2026",
            "Storyboard18 — Tech layoffs top 45,000 in early 2026, US leads global job cuts",
            "DIGITIMES — Anthropic expands India leadership team, May 29 2026"
        ]),
        "body": """Here is a number that should keep every Indian tech founder and policymaker awake at night: Anthropic, a single artificial intelligence company based in San Francisco, just raised $65 billion at a valuation of $965 billion. According to data compiled by YourStory Research, the total venture capital funding raised by all Indian startups combined from 2022 through May 2026 comes to approximately $62 billion.

One company. One round. More than an entire country's startup ecosystem managed in four years.

## The Weekly Numbers

The comparison lands at a particularly painful moment. For the last week of May 2026, total VC funding into Indian startups came in at just $66 million across 16 transactions — the lowest weekly figure of the year and the fifth time this year that the total has dropped below $100 million.

Not a single deal in the week crossed $15 million. The largest disclosed round was Tiea Connectors, a precision manufacturing startup in Bengaluru, which raised ₹77 crore (roughly $8 million) in a Series A led by IvyCap Ventures. PhysicsWallah approved a ₹120 crore internal investment into its NBFC subsidiary.

These are respectable companies doing real things. But the scale gap with what is happening in American AI tells a story about where global capital is flowing — and where it is not.

## The AI Vacuum

The structural problem, as YourStory's analysis bluntly puts it, is that "there are no credible names from India as yet" in the AI startup race. With much of global investor attention — and increasingly, global capital — concentrating on AI companies, India's absence from the conversation is not just a branding problem. It is a funding problem.

The AI boom has created a gravity well. OpenAI, Anthropic, xAI, Mistral, and a handful of other companies are absorbing capital at a pace that dwarfs traditional venture investment. When Anthropic alone can raise $65 billion, the pool available for everything else — including Indian SaaS, fintech, e-commerce, and deep tech — shrinks in relative terms, even if it does not shrink in absolute terms.

Indian startups are also contending with a domestic investor base that has grown more cautious after the excesses of 2021-2022. The Byju's collapse — culminating in founder Byju Raveendran being sentenced to six months in prison by a Singapore court for contempt this week — remains a cautionary tale that has chilled risk appetite for high-burn consumer internet companies.

## Layoffs Continue

Globally, the tech sector has shed over 45,000 jobs in early 2026, with the United States accounting for the vast majority. India has recorded approximately 1,520 layoffs so far this year, with both startups and larger IT firms reducing headcount as global client spending slows.

Amazon alone cut 16,000 roles in January. Meta trimmed roughly 1,500 positions from Reality Labs. Salesforce and Autodesk each cut about 1,000 roles. The pattern is consistent: companies are trading headcount for AI infrastructure investment, betting that automation will deliver the productivity gains that hiring no longer can.

For Indian IT services companies — the Infosys, TCS, and Wipro ecosystem that employs millions — this shift is existential. If their largest clients are investing in AI tools that reduce the need for human-delivered services, the demand trajectory for traditional outsourcing changes fundamentally.

## Bright Spots, but Small

It is not all bleak. Anthropic itself is expanding its leadership team in India, appointing senior executives as adoption of its Claude AI models accelerates across Indian enterprises. The irony is not lost on observers: the company whose fundraise dwarfs India's entire startup ecosystem is looking to India for talent and customers, even as Indian founders struggle to attract a fraction of its capital.

Physis Capital, founded by former Inflection Point Ventures executives, announced the final close of its maiden ₹400 crore fund. Pushp Masale filed its draft prospectus for an IPO. The Supreme Court quashed a ₹202 crore CCI penalty on Amazon India. These are signs of a functioning ecosystem — but one that is operating at a fundamentally different scale than its American and Chinese counterparts.

## The Diaspora Dimension

For Indian-origin tech workers in Silicon Valley, Seattle, and other US hubs, the funding disparity creates a complicated calculation. Many harbor ambitions of returning to India to build companies. The current capital environment makes that harder. A Series A in India might get you $8 million; in the US, an AI startup at a similar stage might raise $50 million or more.

The talent pipeline is not the problem. Indian engineers are disproportionately represented at every major AI lab. The problem is capital formation and ecosystem depth — the density of specialized investors, the availability of large follow-on rounds, and the willingness of institutional capital to make concentrated bets on technology platforms.

Until India produces its own AI platforms that can command capital at global scale, the gap between what Indian founders can build and what they can fund will continue to widen. The Anthropic number is not just a data point. It is a mirror.""",
        "image_search_person": None,
        "image_fallback_query": "artificial intelligence startup venture capital funding",
        "image_attribution": None,
    },
]


# ── Main ─────────────────────────────────────────────────────────────

def main():
    print(f"\n{'='*60}")
    print(f"The Videshi News Writer — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"{'='*60}\n")

    for i, article in enumerate(ARTICLES, 1):
        print(f"\n--- Article {i}/{len(ARTICLES)}: {article['headline'][:70]}... ---\n")

        # Image sourcing
        img_url = None

        # Step 1: Wikipedia for person articles
        person = article.get("image_search_person")
        if person:
            print(f"  Trying Wikipedia for '{person}'...")
            img_url = fetch_wikipedia_person_image(person)
            if img_url:
                article["image_attribution"] = "Wikimedia Commons"

        # Step 2: Pexels fallback
        if not img_url:
            fallback = article.get("image_fallback_query")
            if fallback:
                print(f"  Trying Pexels for '{fallback}'...")
                img_url = fetch_pexels_image(fallback)
                if img_url:
                    article["image_attribution"] = "Pexels"

        # Step 3: Validate
        if img_url and validate_image_url(img_url):
            print(f"  Image validated ✓")
            # Upload to Supabase storage for permanence
            ext = "jpg"
            if ".png" in img_url.lower():
                ext = "png"
            filename = f"{article['slug']}.{ext}"
            stored_url = upload_to_supabase_storage(img_url, filename)
            if stored_url:
                img_url = stored_url
        elif img_url:
            print(f"  ✗ Image validation failed, dropping image")
            img_url = None

        # Build article record
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        record = {
            "headline": article["headline"],
            "subheadline": article["subheadline"],
            "slug": article["slug"],
            "category": article["category"],
            "status": article["status"],
            "body": article["body"],
            "sources": article["sources"],
            "published_at": now_iso,
            "image_url": img_url,
        }
        if article.get("image_attribution"):
            record["image_attribution"] = article["image_attribution"]

        # Remove None values
        record = {k: v for k, v in record.items() if v is not None}

        # Validate quality
        body_words = len(article["body"].split())
        headline_len = len(article["headline"])
        sub_len = len(article["subheadline"])
        print(f"  Quality check: {body_words} words, headline={headline_len}ch, subheadline={sub_len}ch")

        if body_words < 400:
            print(f"  ✗ REJECTED: body too short ({body_words} words)")
            continue
        if headline_len > 200:
            print(f"  ✗ REJECTED: headline too long ({headline_len} chars)")
            continue
        if sub_len < 15:
            print(f"  ✗ REJECTED: subheadline too short ({sub_len} chars)")
            continue

        # Insert
        art_id = insert_article(record)
        if art_id:
            print(f"  ✅ Published: {article['slug']}")
        else:
            print(f"  ❌ Failed to publish: {article['slug']}")

        time.sleep(1)

    print(f"\n{'='*60}")
    print("Done!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
