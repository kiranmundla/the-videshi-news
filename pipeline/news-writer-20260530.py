#!/usr/bin/env python3
"""
The Videshi — News Writer (2026-05-30 evening batch)
Three articles:
  1. EB-2 Green Card freeze for India FY2026
  2. Karachi water crisis and Indus Waters Treaty suspension
  3. US GDP revised down to 1.6% — NRI impact
"""

import json, os, re, sys, uuid, requests, urllib.parse
from datetime import datetime, timezone

# ── Supabase config ─────────────────────────────────────────────
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ── Pexels config ───────────────────────────────────────────────
PEXELS_KEY = None
pexels_env = os.path.expanduser("~/workspace/.env.pexels")
if os.path.exists(pexels_env):
    for line in open(pexels_env):
        if line.startswith("PEXELS_API_KEY="):
            PEXELS_KEY = line.strip().split("=", 1)[1].strip('"').strip("'")

# ── Image skip list ─────────────────────────────────────────────
SKIP_LIST = set()
skip_path = os.path.join(os.path.dirname(__file__), "image-skip-list.json")
if os.path.exists(skip_path):
    SKIP_LIST = set(json.load(open(skip_path)))


def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(" ", "_"))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10,
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
    """Fetch an image from Pexels using curl (urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key found")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            import subprocess
            result = subprocess.run(
                ["curl", "-sS", f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5",
                 "-H", f"Authorization: {PEXELS_KEY}"],
                capture_output=True, text=True, timeout=15,
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


def validate_image_url(url):
    """Validate that the URL returns a real image > 5KB."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        content_type = r.headers.get("Content-Type", "")
        content_length = int(r.headers.get("Content-Length", 0))
        if "image" in content_type and content_length > 5000:
            return True
        # Some servers don't return Content-Length on HEAD, try GET
        if "image" in content_type and content_length == 0:
            r2 = requests.get(url, timeout=10, stream=True,
                              headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                return True
    except Exception as e:
        print(f"  ⚠ Image validation failed for {url[:60]}: {e}")
    return False


def sb_insert(table, row):
    """Insert a row into Supabase and return the response."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers=HEADERS,
        json=row,
    )
    if r.status_code not in (200, 201):
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return None
    data = r.json()
    return data[0] if isinstance(data, list) else data


def sb_patch(table, match, updates):
    """Patch a row in Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/{table}?{match}"
    r = requests.patch(url, headers=HEADERS, json=updates)
    if r.status_code not in (200, 204):
        print(f"  ✗ Patch failed ({r.status_code}): {r.text[:300]}")


# ═══════════════════════════════════════════════════════════════
# ARTICLE 1: EB-2 Green Card Freeze
# ═══════════════════════════════════════════════════════════════

article1 = {
    "headline": "The US Has Run Out of EB-2 Green Cards for Indians This Year. No More Approvals Until October.",
    "subheadline": "The State Department confirmed that all EB-2 immigrant visa numbers for India-born applicants have been exhausted for FY2026, freezing final residency approvals for thousands of skilled professionals.",
    "slug": "eb2-green-card-india-quota-exhausted-fy2026-freeze-october-reset-20260530",
    "category": "news",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": json.dumps([
        {"name": "US Department of State / USCIS Joint Notification", "url": "https://travel.state.gov/"},
        {"name": "Murthy Law Firm", "url": "https://www.murthy.com/"},
        {"name": "VisaVerge", "url": "https://www.visaverge.com/"},
        {"name": "Reuters", "url": "https://www.reuters.com/"}
    ]),
    "body": """The pipeline for Indian professionals seeking permanent residency in the United States through the EB-2 visa category has hit a hard wall. In a joint notification released this week, the US Department of State and US Citizenship and Immigration Services confirmed that all available immigrant visa numbers in the Employment-Based Second Preference category for India-born applicants have been completely exhausted for fiscal year 2026.

The freeze is immediate and absolute. No new EB-2 green cards can be issued to Indian nationals — whether through consular processing abroad or adjustment of status within the United States — until the annual quota resets on October 1, 2026, the start of the new fiscal year.

## What the Numbers Show

The EB-2 category covers professionals with advanced degrees and individuals with exceptional ability — the backbone of the Indian tech workforce in America. The Final Action Date for EB-2 India has retrogressed sharply to September 2013, meaning even applicants who filed their petitions more than 12 years ago are now stuck in the queue.

This is not a new phenomenon. The EB-2 India category has hit its annual ceiling in previous fiscal years as well, most recently in FY2024 when the quota was exhausted in September. But the FY2026 exhaustion coming in late May — four full months before the fiscal year ends — signals accelerating demand pressure against a statutory cap that has remained unchanged for decades.

The per-country limit, which caps any single nation at roughly 7% of the total 140,000 employment-based green cards issued annually, has long been the structural bottleneck for Indian and Chinese applicants. With Indian nationals consistently representing the largest share of EB-2 petitions, the math simply does not work.

## The Human Cost

For the tens of thousands of Indian professionals affected, the freeze means another period of limbo. Many have been living in the United States for years — sometimes more than a decade — on H-1B work visas, paying taxes, buying homes, raising American-born children, and contributing to the economy while waiting for a green card that remains perpetually out of reach.

The practical consequences are significant. Without permanent residency, these professionals cannot freely change employers without risking their place in the queue. Their spouses on H-4 dependent visas face restrictions on employment. Their children, who may have grown up entirely in America, risk "aging out" of their parents' green card applications when they turn 21, potentially losing their immigration status in the only country they have known.

Immigration attorneys have confirmed that there is no workaround. Murthy Law Firm, one of the most prominent firms serving Indian immigrants, noted that affected applicants "must wait until the new fiscal year" — full stop. No priority bumping, no emergency provisions, no administrative discretion.

## The Broader Immigration Picture

The EB-2 freeze arrives at a particularly fraught moment for legal immigration in the United States. The $100,000 H-1B fee introduced by the Trump administration in September 2025 has already reshaped employer calculations around sponsoring Indian workers. US consulates across India have been canceling and rescheduling H-1B visa appointments, sometimes pushing them out by 90 to 120 days.

Meanwhile, the EB-2 for countries other than India and China remains current — meaning applicants from virtually every other nation face no such backlog. The disparity has fueled years of legislative advocacy by Indian-American groups pushing for the elimination of per-country caps, but no bill has cleared both chambers of Congress.

The Fairness for High-Skilled Immigrants Act and similar proposals have repeatedly stalled, caught between competing interests: tech companies that want faster green cards for their workers, labor groups that worry about wage depression, and lawmakers who see immigration reform as politically radioactive.

## What Comes Next

When the new fiscal year begins on October 1, fresh EB-2 visa numbers will be allocated, and USCIS will resume adjudicating pending I-485 adjustment applications. How quickly the dates advance will depend on actual demand and whether any spillover from unused EB-1 numbers flows into the EB-2 category.

For now, the message to the hundreds of thousands of Indian professionals in the American immigration pipeline is familiar: wait. Again.

The EB-2 freeze is not a policy choice that anyone voted for. It is the mechanical result of a statutory framework designed in 1990, applied to a 2026 labor market that bears no resemblance to the one Congress envisioned. Every year the system runs to exhaustion. Every year, the same professionals absorb the consequences. And every year, the reset button is hit on October 1 — not to fix the problem, but to restart the clock on the same one.""",
    "image_url": None,
    "image_attribution": None,
    "diaspora_angle": "The EB-2 freeze directly affects hundreds of thousands of Indian professionals in the US on H-1B visas waiting for permanent residency. Many have lived in America for over a decade, paid taxes, raised children, and built careers while stuck in a queue that resets annually.",
    "vertical": "immigration",
    "tags": ["eb-2", "green-card", "visa-freeze", "uscis", "immigration-backlog", "indian-professionals"],
    "urgency": "high",
    "score_total": 90,
    "is_featured": False,
    "is_editorial": False,
}


# ═══════════════════════════════════════════════════════════════
# ARTICLE 2: Karachi Water Crisis / Indus Waters Treaty
# ═══════════════════════════════════════════════════════════════

article2 = {
    "headline": "Seventy Percent of Karachi Has No Reliable Water. India's Indus Treaty Suspension Is Only Part of the Story.",
    "subheadline": "Pakistan's financial capital faces a severe water crisis as the Indus Waters Treaty remains in abeyance. But the real causes run deeper than geopolitics.",
    "slug": "karachi-water-crisis-indus-waters-treaty-suspension-india-pakistan-20260530",
    "category": "news",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": json.dumps([
        "Times of India",
        "The Daily Jagran",
        "ARY News (Pakistan)",
        "Archynetys / ANI News",
        "India Tribune / MEA briefing"
    ]),
    "body": """Nearly 70 percent of Karachi's 30 million residents are facing a severe water crisis as of late May 2026, forcing millions to rely on expensive private tankers during the scorching pre-monsoon heat. The shortage, now in its second month, has become a flashpoint in the ongoing standoff between India and Pakistan over the Indus Waters Treaty — though the reality on the ground is considerably more complicated than either government acknowledges.

## The Scale of the Crisis

The numbers are staggering. Karachi requires over 1,080 million gallons of water daily for its population, but faces a shortfall of more than 400 million gallons every day. Some estimates put the gap even wider, with demand exceeding 1,250 million gallons against a daily supply of only around 650 million gallons.

The worst-hit neighborhoods — Gulistan-e-Jauhar, Gulshan-e-Iqbal, Azizabad, Liaquatabad, North Nazimabad, and North Karachi — have been without consistent municipal water supply for weeks. Residents report waiting days for a single tanker delivery, with prices that can consume a significant share of a working family's income. The crisis coincides with Eid al-Adha preparations, compounding the hardship.

The city depends on a precarious mix of sources: Keenjhar Lake, Haleji Lake, Hub Dam, and Dumlottee wells. But the delivery infrastructure — more than 10,000 kilometers of pipelines — is riddled with leaks and suffers from decades of poor maintenance. When the official system fails, a thriving water tanker mafia steps in, operating what some estimates value as a $500 million annual industry in stolen and resold public water.

## The Treaty Connection

The crisis has reignited debate about India's suspension of the Indus Waters Treaty, the 1960 agreement that divided six Himalayan rivers between the two countries. Under the treaty, Pakistan received the western rivers — the Indus, Jhelum, and Chenab — while India received the eastern rivers — the Ravi, Beas, and Sutlej.

India declared the treaty in abeyance on April 23, 2025, one day after the Pahalgam terror attack that killed 26 civilians. The suspension gave India greater latitude over the western rivers, allowing it to halt mandatory site visits by Pakistani officials, stop sharing certain flow data, and accelerate long-delayed hydroelectric projects.

At an international water conference in Tajikistan's capital Dushanbe this week, Pakistan's Climate Change Minister Musadik Malik warned that India was attempting to "politicize shared water resources" and urged adherence to international mediation mechanisms. Pakistan has rejected India's suspension as illegal and is pursuing the matter through the Permanent Court of Arbitration, which has continued to assert jurisdiction despite India's boycott of the proceedings.

India's response has been blunt. Foreign Secretary Vikram Misri said India adhered to the treaty for 65 years "despite so many provocations from Pakistan" and that Islamabad repeatedly rejected calls for renegotiation. "The conditions have now changed. This treaty was based on the engineering techniques of the 50s and 60s," Misri said. "Technological changes and advancements have to be taken into account."

## The Real Problem Is Closer to Home

But experts caution against drawing a straight line between the treaty suspension and Karachi's water woes. India currently lacks the storage and diversion infrastructure to significantly hold back the massive flows of the western rivers. The immediate physical impact of the abeyance on Pakistan's actual water supply has been limited.

Karachi's crisis is fundamentally a story of domestic failure. The city's population has roughly tripled in three decades, but its water infrastructure has barely expanded. Decades of underinvestment, unchecked urbanization, political patronage networks that control water distribution, and a tanker mafia that profits from scarcity have created a system that was already failing before the treaty suspension.

The Indus basin itself is under strain from forces larger than any treaty. Climate change is accelerating glacial melt in the Karakoram and Hindu Kush ranges that feed the Indus system. Monsoon patterns are becoming more erratic. And both India and Pakistan face growing water demands from populations that have multiplied far beyond what the 1960 agreement envisioned.

## A Water Weapon — or a Structural Collapse?

For India, the treaty suspension is leverage — a tool to pressure Pakistan on terrorism. For Pakistan, it is an existential threat that validates every fear about upstream control. For Karachi's residents, it is a convenient scapegoat for a crisis that would exist with or without the treaty dispute.

The truth sits uncomfortably between these narratives. India's suspension does add strategic uncertainty to Pakistan's water planning. But Karachi's crisis is the product of governance failures that no treaty — in force or suspended — can fix.

What both countries cannot ignore is the trajectory. The Indus basin serves over 300 million people across both nations. Climate projections suggest water availability could decline by 30 to 40 percent in coming decades. The treaty, designed for a world of stable glaciers and predictable monsoons, may need to be rethought regardless of who attacked whom in Pahalgam.

Until then, Karachi waits for tankers.""",
    "image_url": None,
    "image_attribution": None,
    "diaspora_angle": "The Indus Waters Treaty was a cornerstone of India-Pakistan relations that the diaspora followed closely. Its suspension signals a new phase in India's strategic posture, while the Karachi crisis exposes how infrastructure failures — not just geopolitics — drive water scarcity in the subcontinent.",
    "vertical": "geopolitics",
    "tags": ["indus-waters-treaty", "karachi", "water-crisis", "india-pakistan", "pahalgam", "climate-change"],
    "urgency": "medium",
    "score_total": 82,
    "is_featured": False,
    "is_editorial": False,
}


# ═══════════════════════════════════════════════════════════════
# ARTICLE 3: US GDP Revised Down — NRI Impact
# ═══════════════════════════════════════════════════════════════

article3 = {
    "headline": "The US Economy Grew Just 1.6 Percent Last Quarter. That Is Worse Than Anyone Expected.",
    "subheadline": "A sharp downward revision to first-quarter GDP, driven by weaker consumer spending and the Iran war's inflationary toll, signals trouble ahead for hiring, mortgages, and the Indian professionals who depend on both.",
    "slug": "us-gdp-revised-down-1-6-percent-q1-2026-iran-war-nri-impact-20260530",
    "category": "news",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": json.dumps([
        {"name": "US Bureau of Economic Analysis", "url": "https://www.bea.gov/"},
        {"name": "Reuters", "url": "https://www.reuters.com/"},
        {"name": "Wall Street Journal", "url": "https://www.wsj.com/"},
        {"name": "MarketWatch", "url": "https://www.marketwatch.com/"},
        {"name": "Gallup", "url": "https://www.gallup.com/"}
    ]),
    "body": """The US economy grew considerably less than previously estimated in the first quarter of 2026, a revision that landed with a thud on Thursday and confirmed what many Americans — including the roughly 4.8 million Indian-origin residents navigating the job market, mortgage rates, and immigration queues — already sensed: the economic ground is shifting beneath their feet.

Gross domestic product increased at an annualized rate of just 1.6 percent in the January-March quarter, the Commerce Department's Bureau of Economic Analysis reported in its second estimate. That is a significant downgrade from the 2.0 percent pace initially reported a month ago, and well below what economists had expected.

## What Changed

The revision was driven by two factors. Consumer spending, which accounts for more than two-thirds of the US economy, grew at only 1.4 percent — down from the previously reported 1.6 percent. Spending on services like healthcare was revised lower, though durable goods spending was nudged slightly higher.

Business investment in equipment remained robust at 17.2 percent growth, reflecting the AI infrastructure boom that continues to pour capital into data centers and chips. But the headline GDP figure tells the story of an economy where a narrow band of AI-driven spending is masking weakness almost everywhere else.

Corporate profits grew at a $40.4 billion rate in the first quarter — a dramatic slowdown from the $246.9 billion pace in the previous quarter. Gross domestic income, an alternative measure of economic activity, grew at just 0.9 percent.

"The expansion continues to rest on affluent consumers, AI-driven investment and asset price appreciation," said Gregory Daco, chief economist at EY-Parthenon. "These pillars are masking an increasingly uneven economic foundation."

## The Iran War Factor

The revision captures the economy before the full inflationary impact of the Iran war. The conflict, which began with US and Israeli strikes on February 28, has effectively choked the Strait of Hormuz — the passage through which roughly one-fifth of global oil trade flows. Brent crude has traded around $90-100 per barrel for months, a level that translates directly into higher gasoline, food, and transportation costs for American households.

The war's economic toll is now showing up across multiple indicators. The Gallup Economic Confidence Index plunged to -45 in May, the lowest since October 2022. Only 16 percent of Americans describe economic conditions as "excellent or good." Seventy-six percent say conditions are getting worse — the highest reading since May 2023.

Consumer sentiment has fallen to record lows. Inflation has returned as the second most-cited national problem, with 15 percent of Americans naming it their top concern, up from 8 percent in February.

## What This Means for NRIs

For the Indian diaspora in the United States, the GDP revision carries specific implications across several fronts.

**Hiring and H-1B decisions.** Slowing growth reduces the urgency for companies to hire — and by extension, to sponsor expensive H-1B visas. The $100,000 fee introduced in September 2025 already raised the bar for employers. Weaker growth gives companies another reason to pause, defer, or downsize their foreign worker pipelines. Tech layoffs, which have been a persistent feature since 2023, may not be over.

**Mortgage rates.** The Federal Reserve's next move is now a genuine coin flip. The central bank has signaled it may need to raise rates to combat the Iran-war-driven inflation, which would push mortgage rates higher. For Indian-American families — disproportionately concentrated in expensive housing markets like the Bay Area, Seattle, and the Northeast corridor — higher rates mean higher monthly payments on already stretched budgets.

**Remittances.** India received $129 billion in remittances in the 2025 fiscal year, more than any other country. A slowdown in US wage growth and employment, combined with a stronger dollar, could reduce the purchasing power of dollars sent home. For families in India who depend on these transfers, the impact compounds.

**Green card timing.** The EB-2 visa quota for India was exhausted this week, freezing final approvals until October. A weaker economy does not directly affect the immigration backlog, but it shapes the political environment. Anti-immigration rhetoric intensifies when jobs feel scarce, and congressional appetite for reforms like eliminating per-country caps shrinks when voters are anxious about their own employment.

## The Second Quarter Will Be Worse

Economists broadly expect the second quarter — April through June — to show even weaker growth as the full impact of higher energy prices works through the economy. The Iran war ceasefire negotiations, which appeared close to producing a 60-day extension this week, could provide relief if the Strait of Hormuz reopens. But even optimistic scenarios project months before shipping normalizes and energy prices meaningfully decline.

The Federal Reserve, caught between slowing growth and rising inflation, faces its own version of the immigrant's dilemma: no good options, only trade-offs.

For the millions of Indian professionals who built their American lives on the assumption of a growing, dynamic economy — an economy that rewards skill, creates opportunity, and eventually, grudgingly, offers a path to permanence — the 1.6 percent figure is a reminder that the ground they stand on was never as solid as it appeared.""",
    "image_url": None,
    "image_attribution": None,
    "diaspora_angle": "A slowing US economy directly impacts the 4.8 million Indian-origin Americans through hiring freezes, H-1B sponsorship pullbacks, higher mortgage rates, reduced remittance purchasing power, and a political environment less receptive to immigration reform. India received $129B in remittances in FY2025 — any US economic slowdown ripples directly to families back home.",
    "vertical": "economy",
    "tags": ["us-gdp", "economy", "iran-war", "inflation", "nri-mortgages", "remittances", "h1b-hiring"],
    "urgency": "high",
    "score_total": 85,
    "is_featured": False,
    "is_editorial": False,
}


# ═══════════════════════════════════════════════════════════════
# IMAGE SOURCING
# ═══════════════════════════════════════════════════════════════

def source_images():
    """Source images for all three articles."""
    # Article 1: EB-2 — try Pexels with specific terms
    print("\n📸 Sourcing image for Article 1 (EB-2 Green Card)...")
    img1 = fetch_pexels_image("US visa passport stamp", "immigration documents passport")
    if img1 and validate_image_url(img1):
        article1["image_url"] = img1
        article1["image_attribution"] = "Pexels"
        print(f"  ✓ Article 1 image set")
    else:
        print(f"  ⚠ No valid image for Article 1, publishing without image")

    # Article 2: Karachi water crisis — try Pexels
    print("\n📸 Sourcing image for Article 2 (Karachi Water Crisis)...")
    img2 = fetch_pexels_image("water tanker truck city", "water crisis urban dry tap")
    if img2 and validate_image_url(img2):
        article2["image_url"] = img2
        article2["image_attribution"] = "Pexels"
        print(f"  ✓ Article 2 image set")
    else:
        print(f"  ⚠ No valid image for Article 2, publishing without image")

    # Article 3: US GDP — try Pexels
    print("\n📸 Sourcing image for Article 3 (US GDP)...")
    img3 = fetch_pexels_image("wall street stock market trading floor", "US economy financial district")
    if img3 and validate_image_url(img3):
        article3["image_url"] = img3
        article3["image_attribution"] = "Pexels"
        print(f"  ✓ Article 3 image set")
    else:
        print(f"  ⚠ No valid image for Article 3, publishing without image")


# ═══════════════════════════════════════════════════════════════
# PUBLISH
# ═══════════════════════════════════════════════════════════════

def publish_article(article, label):
    """Insert an article into Supabase."""
    print(f"\n📝 Publishing: {label}")
    print(f"   Headline: {article['headline'][:80]}...")
    print(f"   Slug: {article['slug']}")
    print(f"   Category: {article['category']}")
    print(f"   Image: {'Yes' if article.get('image_url') else 'No'}")

    # Word count check
    word_count = len(article["body"].split())
    print(f"   Word count: {word_count}")
    if word_count < 400:
        print(f"   ✗ REJECTED: Article under 400 words ({word_count})")
        return None

    result = sb_insert("p2_articles", article)
    if result:
        art_id = result.get("id")
        print(f"   ✓ Published with ID: {art_id}")
        return art_id
    return None


def main():
    print("=" * 60)
    print("The Videshi — News Writer (2026-05-30 evening)")
    print("=" * 60)

    # Source images
    source_images()

    # Publish
    ids = []
    for article, label in [
        (article1, "Article 1: EB-2 Green Card Freeze"),
        (article2, "Article 2: Karachi Water Crisis"),
        (article3, "Article 3: US GDP Revised Down"),
    ]:
        art_id = publish_article(article, label)
        if art_id:
            ids.append(art_id)

    print(f"\n{'=' * 60}")
    print(f"✓ Published {len(ids)}/{3} articles")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
