#!/usr/bin/env python3
"""
News writer for The Videshi — 2026-05-28 evening run
3 articles: Quad critical minerals, India power grid crisis, India stock market Taiwan threat
"""
import os, json, sys, time, uuid, re
import requests
import urllib.parse
from datetime import datetime, timezone

# ── Environment ──────────────────────────────────────────────────────
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ── Helper functions ─────────────────────────────────────────────────

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
    """Fetch a relevant image from Pexels using curl (Python urllib gets 403)."""
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            import subprocess
            result = subprocess.run(
                ["curl", "-sS", "-H", f"Authorization: {PEXELS_API_KEY}",
                 f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape"],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for photo in photos:
                url = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("large")
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def upload_image_to_supabase(image_url, filename):
    """Download image and upload to Supabase storage bucket 'article-images'."""
    try:
        r = requests.get(image_url, timeout=15, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        if r.status_code != 200:
            print(f"  ⚠ Image download failed: HTTP {r.status_code}")
            return None
        content_type = r.headers.get("Content-Type", "")
        if not content_type.startswith("image/"):
            print(f"  ⚠ Not an image: {content_type}")
            return None
        if len(r.content) < 5000:
            print(f"  ⚠ Image too small: {len(r.content)} bytes")
            return None

        # Upload to Supabase storage
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        upload_r = requests.post(
            upload_url,
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": content_type,
                "x-upsert": "true",
            },
            data=r.content,
            timeout=30,
        )
        if upload_r.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Supabase upload failed: {upload_r.status_code} {upload_r.text[:200]}")
            return None
    except Exception as e:
        print(f"  ⚠ Image upload error: {e}")
        return None


def publish_article(article):
    """Insert article into Supabase p2_articles table."""
    art_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    payload = {
        "id": art_id,
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "body": article["body"],
        "slug": article["slug"],
        "category": "news",
        "status": "published",
        "published_at": now,
        "created_at": now,
        "updated_at": now,
        "sources": json.dumps(article["sources"]),
        "image_url": article.get("image_url"),
        "image_attribution": article.get("image_attribution", "The Videshi"),
        "image_caption": article.get("image_caption", ""),
        "diaspora_angle": article.get("diaspora_angle", ""),
        "vertical": article.get("vertical", "general"),
        "tags": "{" + ",".join(article.get("tags", [])) + "}",
        "urgency": article.get("urgency", "medium"),
        "score_total": article.get("score_total", 80),
    }

    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=payload,
        timeout=15,
    )
    if r.status_code in (200, 201):
        print(f"✅ Published: {article['headline'][:60]}... (id: {art_id[:8]})")
        return art_id
    else:
        print(f"❌ Failed to publish: {r.status_code} {r.text[:300]}")
        return None


# ── Article 1: Quad $20 Billion Critical Minerals ───────────────────

article1 = {
    "headline": "The Quad Just Pledged $20 Billion to Break China's Grip on Critical Minerals. India Is at the Centre.",
    "subheadline": "The US, Japan, Australia and India want to build alternative supply chains for lithium, cobalt and rare earths. The plan is unprecedented — and long overdue.",
    "slug": "quad-20-billion-critical-minerals-india-china-supply-chains-20260528",
    "sources": [
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "IBTimes Singapore", "url": "https://www.ibtimes.sg/quads-20-billion-china-challenge-how-india-us-japan-australia-plan-break-beijings-critical-87005"},
        {"name": "US State Department Joint Statement", "url": "https://www.state.gov"},
        {"name": "IEA Energy Technology Perspectives 2026", "url": "https://www.iea.org"}
    ],
    "body": """The four nations of the Quad — the United States, India, Japan and Australia — have announced a $20 billion framework to secure critical mineral supply chains, in what amounts to the most ambitious coordinated attempt yet to challenge China's stranglehold on the materials that power the modern economy.

The initiative, unveiled at the Quad Foreign Ministers' Meeting on May 26, targets minerals essential to semiconductors, electric vehicle batteries, clean energy systems, defence equipment and artificial intelligence. Its stated goal: to build supply chains rooted in "trusted partners, not strategic adversaries."

## Why It Matters

China currently dominates critical mineral processing at a scale that leaves every other economy dangerously exposed. According to the International Energy Agency's Energy Technology Perspectives 2026 report, China controls between 60 and 85 per cent of production capacity across key supply chain stages. That dominance is not expected to shift meaningfully before 2030.

The vulnerability is not theoretical. The IEA estimates that a one-month halt in Chinese battery supply chains could cut electric vehicle production outside China by $17 billion. A similar disruption in solar exports would reduce global solar manufacturing output by around $1 billion per month, with India and Southeast Asia among the hardest hit.

China's clean energy exports topped $165 billion in 2025. Its cost advantages — driven by lower labour costs, automation, subsidies and cheap energy — continue to widen the gap.

## What the Quad Is Proposing

At the heart of the framework is a plan to mobilise up to $20 billion in government and private sector support for mining, processing and recycling projects with a "Quad nexus" — meaning ventures located in member countries, operated by Quad-based firms, or directly supplying Quad markets.

The financial architecture includes export credit agencies, development finance institutions, loans, guarantees, insurance, subsidies and mechanisms to attract private capital. In a joint statement, the four nations said they intend "to support the development of secure critical minerals supply chains, which are essential for advanced technologies, economic growth, and the resilience of our industrial bases."

Beyond investment, the framework seeks to harmonise regulatory approaches. Quad members plan to share best practices on licensing and permitting systems, explore ways to streamline approval timelines, and strengthen tools to review transactions involving critical minerals that pose national security risks.

Recycling is another major pillar. The partners will collaborate on recovering critical minerals from electronic waste and scrap materials, develop mineral recycling technologies, and simplify export and import procedures for waste materials.

## India's Role

For India, the initiative arrives at a strategic inflection point. The country is positioning itself as a processing hub for lithium, cobalt, rare earths and other minerals critical to its own industrial ambitions — and the Quad framework provides both capital and geopolitical cover for that push.

India's participation also reflects a broader diplomatic calculation. As the Quad's only member in South Asia and one of the largest consumers of imported minerals, India stands to benefit disproportionately from diversified supply chains. The framework gives New Delhi access to technology transfer, financing and regulatory alignment that would be difficult to secure bilaterally.

## The Diaspora Angle

For the estimated 5.4 million Indian Americans and the wider NRI community, the initiative has direct implications. Many work in the semiconductor, clean energy, defence and AI industries that depend on these minerals. Supply chain disruptions from China have already affected chip availability, EV production timelines and renewable energy project costs across the United States.

The Quad minerals push also opens investment and business opportunities. Indian-origin professionals in mining technology, materials science and supply chain logistics are likely to see increased demand as the four nations ramp up domestic processing capacity.

## What Happens Next

The Quad has been criticised in the past for producing more communiqués than results. Whether this $20 billion commitment translates into operational mines, functional processing plants and genuine supply diversification will depend on execution — something that has historically been the grouping's weakest suit.

But the urgency is real. With the Iran war disrupting energy supply chains, AI demand accelerating the need for rare earth magnets and advanced chips, and China showing no reluctance to use mineral exports as leverage, the Quad may finally have the pressure it needs to move from ambition to action.""",
    "image_caption": "The Quad Foreign Ministers' Meeting unveiled a $20 billion critical minerals framework",
    "diaspora_angle": "Indian Americans working in semiconductor, clean energy, defence and AI industries are directly affected by mineral supply chain vulnerabilities. The Quad framework opens investment and business opportunities for Indian-origin professionals in mining technology, materials science and supply chain logistics.",
    "vertical": "geopolitics",
    "tags": ["quad", "critical-minerals", "china", "india", "supply-chain", "ai", "semiconductors"],
    "urgency": "high",
    "score_total": 88
}

# ── Article 2: India Power Grid Crisis ──────────────────────────────

article2 = {
    "headline": "Twenty-One Indian Power Plants Are Running on Less Than a Week of Coal. The Grid Has Never Been This Fragile.",
    "subheadline": "Coal India is scrambling to ramp up supplies as El Niño pushes electricity demand to a record 270.8 GW. Blackouts are already hitting several states.",
    "slug": "india-power-grid-coal-crisis-21-plants-el-nino-heatwave-270gw-20260528",
    "sources": [
        {"name": "Reuters", "url": "https://www.reuters.com/business/energy/coal-india-asks-units-ramp-up-supplies-heatwave-fuels-record-power-demand-2026-05-26/"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com"},
        {"name": "Central Electricity Authority of India", "url": "https://cea.nic.in"},
        {"name": "NativePlanet", "url": "https://www.nativeplanet.com"}
    ],
    "body": """India's power grid is under the most severe strain it has ever faced. Twenty-one thermal power plants are operating with coal stocks sufficient for less than a week's consumption, even as electricity demand has shattered all previous records at 270.8 gigawatts.

State-run Coal India, the world's largest coal miner, has directed all eight of its subsidiaries to maximise dispatches using every available transport mode, including dedicated rail links that move coal directly from mines to power plants. The urgency is unmistakable: several regions are already experiencing blackouts, mainly at night when renewable output drops to zero.

## The Numbers Are Alarming

The Central Electricity Authority, which advises the federal power ministry, classifies any plant with less than seven days of coal stock as critically low. Twenty-one plants currently fall below that threshold — a number that has been climbing steadily as the El Niño-driven heatwave extends into its fourth consecutive week.

Peak power demand hit 270.8 GW last week, shattering the previous record. Despite India having installed 228 GW of non-fossil fuel capacity — solar, wind, hydro and nuclear — coal still generates more than 70 per cent of the country's electricity. When the sun sets and the wind dies, coal is all that stands between 1.4 billion people and darkness.

Coal India's own production has not helped. Output fell 9.7 per cent in April to 56.1 million metric tons, driven by seasonal mining disruptions and transport bottlenecks. The company says it holds 168 million tons of coal overall, including 47.6 million tons at power plants — enough for roughly 19 days of consumption at current burn rates.

But those aggregate numbers mask severe regional disparities. Plants in logistically challenging areas — northeastern India, parts of central India, remote Rajasthan — are the ones running critically low, precisely because they are hardest to resupply quickly.

## Scheduled Blackouts

On May 28, scheduled power outages hit Delhi-NCR, Bengaluru and Chennai simultaneously. In all three cities, blackouts were planned between 12 PM and 6 PM — peak afternoon hours when air conditioning demand is highest and heat exposure is most dangerous.

The irony is brutal. India is cutting power during the exact hours when people most need it to survive temperatures that have crossed 48°C in fifty cities. Health authorities have warned that wet-bulb temperatures in parts of northern India are approaching human survival limits — the threshold beyond which the body can no longer cool itself through sweat.

For tens of millions of Indians without backup power, a scheduled blackout during a 48°C afternoon is not an inconvenience. It is a medical emergency.

## Why Renewables Cannot Save This

India's 228 GW of non-fossil capacity is impressive on paper but structurally inadequate for the current crisis. Solar output drops to zero at exactly the hour when demand peaks — the early evening, when offices are still running, homes turn on air conditioners, and the grid transitions from solar to thermal.

Battery storage, which could bridge this gap, remains negligible. India has less than 5 GW of grid-scale battery capacity, a fraction of what would be needed to smooth the evening ramp. The result is a daily cliff: solar generation falls off, coal plants struggle to ramp up fast enough, and the grid frequency drops below the 50 Hz target.

The Iran war has made everything worse. Jet fuel and crude oil prices have spiked, pushing up the cost of coal transport by rail and road. Plants that relied on imported coal are paying 31 per cent more than they were at the start of the year, according to global coal price indices.

## What NRIs Should Know

If you have family in India — particularly elderly parents, grandparents, or relatives in smaller cities — this is the moment to check in. The combination of extreme heat and unreliable power is genuinely dangerous for vulnerable populations.

Air conditioning is not a luxury in a 48°C heatwave. It is the difference between survival and heatstroke. If your family's area is experiencing scheduled outages, consider helping them source inverters, battery backups or generators. Urban areas like Delhi-NCR, Bengaluru and Chennai are affected, but tier-2 and tier-3 cities are likely worse off.

The grid crisis also underscores a broader structural challenge. India's electricity infrastructure was built for a different climate. El Niño patterns, intensified by global warming, are producing heatwaves that exceed the system's design capacity. This is not a one-summer problem. It is a permanent shift that India's grid has not yet adapted to.""",
    "image_caption": "India's electricity demand has hit a record 270.8 GW as heatwave strains the grid",
    "diaspora_angle": "NRIs with elderly family in India should check in urgently. The combination of 48°C heat and scheduled blackouts is dangerous for vulnerable populations. Urban areas like Delhi-NCR, Bengaluru and Chennai are affected, but smaller cities may be worse off.",
    "vertical": "energy",
    "tags": ["coal-india", "power-grid", "heatwave", "el-nino", "blackouts", "energy-crisis"],
    "urgency": "high",
    "score_total": 90
}

# ── Article 3: India Stock Market & Taiwan Threat ───────────────────

article3 = {
    "headline": "Foreign Investors Have Pulled $24 Billion From India This Year. Taiwan Is About to Steal Its Spot.",
    "subheadline": "India's stock market is on track for its first annual decline in over a decade as TSMC-powered Taiwan closes within $30 billion of overtaking it in global market cap rankings.",
    "slug": "india-stock-market-foreign-outflows-24-billion-taiwan-tsmc-fifth-spot-20260528",
    "sources": [
        {"name": "Reuters", "url": "https://www.reuters.com/world/asia-pacific/indias-fifth-spot-global-market-cap-list-under-threat-taiwan-closes-2026-05-26/"},
        {"name": "Copley Fund Research", "url": "https://copleyresearch.com"},
        {"name": "SEBI", "url": "https://www.sebi.gov.in"},
        {"name": "Reuters Markets", "url": "https://www.reuters.com"}
    ],
    "body": """India's position as the world's fifth-largest stock market is under immediate threat. Taiwan's total market capitalisation has surged to $4.89 trillion, within touching distance of India's $4.92 trillion — a gap so narrow that a single bad week for Mumbai could hand Taipei the ranking.

The reversal is dramatic. As recently as August 2024, India was the darling of emerging market fund managers, commanding average portfolio weights of 17.47 per cent. That figure has now plummeted to 9.94 per cent — the first time India has dipped below 10 per cent since January 2021, according to Copley Fund Research.

"India has moved from being the darling of emerging markets to the runt of the litter among Asia's Big Four," Copley said in its May report.

## The Numbers

Foreign portfolio investors have pulled $24.18 billion from Indian equities so far in 2026, surpassing the record annual outflows set in all of 2025. In almost perfect symmetry, foreign investors have poured approximately $25 billion into Taiwan over the same period.

The Nifty 50 is down about 8.5 per cent for the year. The BSE Sensex has fared even worse, dropping 10.8 per cent. Both indices are on track for their first annual decline in over a decade.

India's share of the MSCI Global Standard index has fallen to 12.3 per cent from a peak of 21 per cent in September 2024. That decline triggers a self-reinforcing cycle: as India's MSCI weight drops, passive funds tracking the index automatically reduce their exposure, which pushes prices lower, which reduces India's weight further.

## Why Taiwan Is Winning

One company explains most of the divergence: Taiwan Semiconductor Manufacturing Company. TSMC shares have surged over 44 per cent in 2026, powered by insatiable global demand for AI chips. The stock now accounts for roughly 42 per cent of Taiwan's benchmark index.

"The Indian market does not offer direct equivalents to AI trade and companies such as TSMC, Nvidia or large-scale AI infrastructure businesses," said Manish Bhandari, CEO and Portfolio Manager at Vallum Capital.

India's economy is diversified, services-heavy and consumption-driven. Those qualities made it attractive when global investors were looking for stability. But in 2026, the market wants exposure to artificial intelligence — and India does not have it.

## Multiple Headwinds

The AI gap is not the only problem. India is absorbing a cascade of negative shocks:

**Oil prices.** India imports more than 80 per cent of its crude oil. The Iran war has pushed Brent crude above $90, inflating input costs for every sector of the economy and widening the current account deficit.

**Geopolitical risk.** The India-Pakistan tensions earlier this year, combined with uncertainty around US tariffs and the ongoing Iran conflict, have raised India's risk premium among global allocators.

**Monsoon uncertainty.** The India Meteorological Department has forecast a below-normal monsoon for the first time in eight years, with El Niño building. Agriculture employs roughly 42 per cent of India's workforce, and a bad monsoon translates directly into weaker rural consumption, lower GDP growth and political instability.

**Weak earnings.** Corporate earnings growth has disappointed relative to expectations, giving foreign investors little reason to stay in a market that is still trading at premium valuations by emerging market standards.

## What NRI Investors Should Consider

SEBI Chairman Tuhin Kanta Pandey acknowledged the challenge on Tuesday, noting that "India is a diversified economy but Taiwan is concentrated on certain companies. These companies are attracting foreign flows at this time."

The implication is that India's structural disadvantage — the absence of a TSMC-equivalent — is not something policy can fix quickly. Building AI infrastructure companies takes years. In the meantime, NRI investors with significant Indian equity exposure may want to reassess their portfolio balance.

The $24 billion outflow is not retail panic. It is institutional capital — pension funds, sovereign wealth funds, mutual funds — making a deliberate reallocation from India to markets with AI exposure. That kind of structural shift does not reverse on sentiment alone.

Indian markets were closed on Thursday for Eid ul-Adha, giving investors a pause. But when trading resumes, the question is whether the Nifty has found a floor — or whether the slide has further to go.

For NRIs who have been adding to Indian positions on the assumption that India's growth story is unassailable, the message from global capital markets is sobering: growth alone is no longer enough. In 2026, you also need chips.""",
    "image_caption": "India's stock market is under pressure as foreign investors pull record amounts",
    "diaspora_angle": "NRI investors with significant Indian equity exposure should reassess portfolio balance. The $24 billion outflow is institutional reallocation from India to AI-exposed markets like Taiwan — a structural shift that does not reverse on sentiment alone.",
    "vertical": "markets",
    "tags": ["stock-market", "fii-outflows", "taiwan", "tsmc", "nifty", "sensex", "msci"],
    "urgency": "high",
    "score_total": 92
}

# ── Main execution ──────────────────────────────────────────────────

def main():
    articles = [article1, article2, article3]

    for i, article in enumerate(articles, 1):
        print(f"\n{'='*60}")
        print(f"Article {i}: {article['headline'][:60]}...")
        print(f"{'='*60}")

        # Source image
        img_url = None

        if i == 1:
            # Quad minerals — try Pexels for "mining minerals"
            img_url = fetch_pexels_image("lithium mining minerals", "rare earth minerals processing")
        elif i == 2:
            # Power grid — try Pexels for "power plant coal India"
            img_url = fetch_pexels_image("coal power plant cooling towers", "electricity transmission towers India")
        elif i == 3:
            # Stock market — try Wikipedia for SEBI Chairman or use Pexels
            img_url = fetch_pexels_image("stock market trading floor India", "stock exchange digital screen")

        if img_url:
            filename = f"{article['slug']}.jpg"
            final_url = upload_image_to_supabase(img_url, filename)
            if final_url:
                article["image_url"] = final_url
                article["image_attribution"] = "The Videshi"
            else:
                article["image_url"] = img_url  # Use direct Pexels URL (permanent)
                article["image_attribution"] = "Pexels"
        else:
            print(f"  ⚠ No image found — publishing without image")
            article["image_url"] = None

        # Publish
        art_id = publish_article(article)
        if art_id:
            print(f"  → Slug: {article['slug']}")
        time.sleep(1)

    print(f"\n{'='*60}")
    print(f"Done. Published {len(articles)} articles.")


if __name__ == "__main__":
    main()
