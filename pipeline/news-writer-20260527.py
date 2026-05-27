#!/usr/bin/env python3
"""
The Videshi — News Writer (2026-05-27 evening batch)
Publishes 3 articles to the 'news' category.
"""

import json
import os
import re
import sys
import uuid
import requests
from datetime import datetime, timezone

# ── Supabase config ──────────────────────────────────────────────
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")


# ── Image helpers ────────────────────────────────────────────────
def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = person_name.replace(" ", "_")
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
    """Fetch an image from Pexels with specific search terms. Returns URL or None."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            r = requests.get(
                "https://api.pexels.com/v1/search",
                headers={"Authorization": PEXELS_KEY},
                params={"query": q, "per_page": 5, "orientation": "landscape"},
                timeout=10,
            )
            if r.status_code == 200:
                photos = r.json().get("photos", [])
                for p in photos:
                    url = p.get("src", {}).get("large2x") or p.get("src", {}).get("large")
                    if url:
                        print(f"  ✓ Pexels image for '{q}': {url[:80]}...")
                        return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image(url):
    """Check that an image URL returns 200 with image/* content-type and >5KB."""
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Try GET if HEAD didn't give good Content-Length
        if r.status_code == 200 and "image" in ct and cl == 0:
            r2 = requests.get(url, timeout=10, stream=True,
                              headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            chunk = r2.raw.read(6000)
            r2.close()
            if len(chunk) > 5000:
                return True
        print(f"  ⚠ Image validation failed: status={r.status_code} ct={ct} cl={cl}")
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False


def upload_image_to_supabase(image_url, filename):
    """Download image and upload to Supabase storage bucket 'article-images'."""
    try:
        r = requests.get(image_url, timeout=20,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        if r.status_code != 200 or len(r.content) < 5000:
            print(f"  ⚠ Failed to download image: status={r.status_code} size={len(r.content)}")
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
            print(f"  ⚠ Supabase upload failed: {resp.status_code} {resp.text[:200]}")
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return None


# ── Dedup check ──────────────────────────────────────────────────
def check_duplicate(slug_fragment):
    """Check if a similar article already exists in the last 3 days."""
    since = (datetime.now(timezone.utc)).strftime("%Y-%m-%dT00:00:00Z")
    # Check last 3 days
    from datetime import timedelta
    since_3d = (datetime.now(timezone.utc) - timedelta(days=3)).strftime("%Y-%m-%dT00:00:00Z")
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        params={
            "select": "headline,slug",
            "status": "eq.published",
            "published_at": f"gte.{since_3d}",
            "category": "eq.news",
            "slug": f"like.*{slug_fragment}*",
            "limit": "5",
        },
        timeout=15,
    )
    if r.status_code == 200:
        matches = r.json()
        if matches:
            print(f"  ⚠ Possible duplicate for '{slug_fragment}': {[m['slug'] for m in matches]}")
            return True
    return False


# ── Article publishing ───────────────────────────────────────────
def publish_article(article):
    """Insert article into Supabase p2_articles table."""
    payload = {
        "id": str(uuid.uuid4()),
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "body": article["body"],
        "slug": article["slug"],
        "category": "news",
        "vertical": article.get("vertical", "general"),
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": json.dumps(article.get("sources", [])),
        "image_url": article.get("image_url"),
        "image_attribution": article.get("image_attribution"),
    }
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=payload,
        timeout=20,
    )
    if r.status_code in (200, 201):
        result = r.json()
        art_id = result[0]["id"] if isinstance(result, list) else result.get("id", "unknown")
        print(f"  ✅ Published: {article['headline'][:60]}... (id={art_id})")
        return art_id
    else:
        print(f"  ❌ Publish failed: {r.status_code} {r.text[:300]}")
        return None


# ── ARTICLES ─────────────────────────────────────────────────────

articles = []

# ═══════════════════════════════════════════════════════════════════
# ARTICLE 1: India's AMCA Fifth-Generation Fighter Jet
# ═══════════════════════════════════════════════════════════════════

articles.append({
    "headline": "India Just Invited Three Private Companies to Build Its First Stealth Fighter Jet. The F-35 and Su-57 Were Not Invited.",
    "subheadline": "The ₹15,000 crore AMCA programme marks India's boldest bet yet on indigenous defence manufacturing — and a deliberate snub to Washington and Moscow.",
    "slug": "india-amca-stealth-fighter-jet-rfp-tata-lt-bharat-forge-20260527",
    "sources": ["Reuters", "ANI", "The Asia Live"],
    "image_person": "Advanced Medium Combat Aircraft",
    "image_pexels_query": "fighter jet military aircraft",
    "image_pexels_fallback": "Indian Air Force jet",
    "vertical": "defence",
    "body": """India's Ministry of Defence on Wednesday issued a formal Request for Proposal to three private-sector consortia to develop the Advanced Medium Combat Aircraft — the country's first indigenous fifth-generation stealth fighter jet. The move marks the most significant step yet in New Delhi's push to break its decades-long dependence on imported warplanes.

## Who's Building It

The three shortlisted bidders are all Indian: **Tata Advanced Systems**, a joint venture between **Larsen & Toubro and Bharat Electronics**, and a consortium of **Bharat Forge and BEML**. Notably absent from the bidding: Hindustan Aeronautics Limited (HAL), the state-owned monopoly that has built nearly every Indian military aircraft to date. The exclusion of HAL signals a decisive shift toward private-sector defence manufacturing under Prime Minister Narendra Modi's Atmanirbhar Bharat (self-reliant India) framework.

The bids open on June 11. The winning consortium is expected to develop five prototypes at a cost of approximately ₹15,000 crore ($1.57 billion), with the first flight targeted within 30 months of contract award. A new Core Integration Centre in Andhra Pradesh will house the flight testing programme.

## What the AMCA Is

The AMCA is designed to be a twin-engine, multirole stealth fighter capable of air supremacy, ground attack, and electronic warfare missions. Key features include internal weapons bays, low-observable radar cross-section, sensor fusion, supercruise capability, and a 10-hour continuous flight endurance. If it performs as designed, it would place India in an exclusive club of nations with operational fifth-generation fighters — currently limited to the United States, China, and Russia.

The programme has been in development under the Aeronautical Development Agency (ADA) for over a decade, but the issuance of a formal RFP to private bidders represents the transition from paper design to industrial reality.

## Why India Turned Down the F-35 and Su-57

Both the United States and Russia have aggressively pitched their own fifth-generation platforms to India. Washington offered the **Lockheed Martin F-35 Lightning II**, the world's most advanced operational fighter. Moscow countered with the **Sukhoi Su-57**, its own stealth contender. India declined both.

The reasoning is strategic rather than purely technical. Buying either platform would deepen dependency on a single foreign supplier for maintenance, spare parts, and upgrades over a 30-to-40-year service life. India's experience with its ageing fleet of Russian-made Sukhoi Su-30MKIs — which now constitute the backbone of the air force but have faced chronic spare-parts shortages — has reinforced the case for an indigenous alternative.

India's Air Force currently operates fewer than 30 fighter squadrons against a sanctioned strength of 42, a gap that grows more acute as older MiG-21s and MiG-27s are retired. The AMCA is not merely an ambition project — it is a force-structure necessity.

## Defence Production Is Already at Record Highs

The RFP arrives as India's defence production hits an all-time high of ₹1.54 trillion ($16.09 billion) in the financial year ending March 2025, according to government data. Defence exports have also surged, with India now supplying military hardware to over 85 countries including the Philippines, Armenia, and several African nations.

The private sector's share of defence production has grown from under 20% a decade ago to nearly 35% today. The AMCA programme, if executed on schedule, would cement that trajectory and potentially position Indian defence firms as exporters of next-generation platforms.

## The Diaspora Angle

For the roughly 4.4 million Indian Americans and the broader NRI community, the AMCA programme carries significance beyond its military dimensions. India's defence sector has historically been opaque, state-dominated, and notoriously slow. The entry of publicly listed firms like Tata, L&T, and Bharat Forge — companies whose shares trade on the BSE and NSE — opens a direct investment pathway for diaspora investors who have long been bullish on India's growth story but wary of its defence bureaucracy.

The programme also raises the profile of Indian engineering talent at a moment when the country's IT sector is under pressure from AI-driven disruption. Building a stealth fighter from scratch — with indigenous avionics, composites, and weapons integration — requires a different class of engineering entirely.

Serial production is targeted for the mid-2030s, with an eventual fleet of 120 to 250 aircraft for the Indian Air Force and Navy. If India pulls it off, the AMCA will be the most complex machine the country has ever built.""",
    "source": "The Videshi",
    "image_attribution": "Wikimedia Commons",
})

# ═══════════════════════════════════════════════════════════════════
# ARTICLE 2: India Stocks — First Yearly Drop in a Decade
# ═══════════════════════════════════════════════════════════════════

articles.append({
    "headline": "Foreign Investors Have Pulled $23 Billion Out of India This Year. The Nifty Is Headed for Its First Annual Drop Since 2015.",
    "subheadline": "A Reuters poll of 24 analysts says India's stock market darling status is over — for now. The AI boom, Iran war oil shock, and weak earnings are all working against it.",
    "slug": "india-stocks-first-yearly-drop-decade-foreign-investors-exit-nifty-20260527",
    "sources": ["Reuters", "Societe Generale", "Copley Fund Research"],
    "image_person": None,
    "image_pexels_query": "Bombay stock exchange Mumbai trading",
    "image_pexels_fallback": "India stock market Mumbai finance",
    "vertical": "economy",
    "body": """India's stock market is on track for its first annual decline in more than a decade, according to a Reuters poll of 24 equity analysts published Wednesday. The Nifty 50, already down approximately 8.5% in 2026, is forecast to close the year at 26,000 — a marginal 0.5% annual loss that would be its first negative year since 2015.

The Sensex is projected to finish at 84,150, with both benchmarks sharply downgraded from a February poll conducted before the U.S.-Israel war with Iran began.

## The $23 Billion Exodus

Foreign investors have sold more than $23 billion of Indian equities so far in 2026, surpassing the record annual outflows recorded last year. Meanwhile, they have poured approximately $25 billion into Taiwan, whose AI-heavy KOSPI-equivalent index has surged over 200% in the past year.

"Everyone wants returns at the end of the day," said **Rajat Agarwal**, Asia equity strategist at Societe Generale. "The returns are not there, earnings growth is almost negligible to very low. AI is where the flavour of the town is right now, and this is where India — not just we lack it, we are actually on the wrong side."

India's heavyweight IT stocks index, the Nifty IT, has fallen by more than a third since December 2024. The country's information technology sector — once the crown jewel that attracted billions in foreign portfolio investment — has been unable to ride the global AI wave the way Korean, Taiwanese, and American tech stocks have.

## The Valuation Problem

India trades at more than 20 times earnings, above most major European and emerging markets, while offering one of the world's lowest dividend yields. For years, that premium was justified by GDP growth rates north of 6% and a demographic dividend that promised decades of consumer expansion. But the Iran war's oil shock has rewritten the macro calculus.

India imports roughly 85% of its crude oil. The three-month closure of the Strait of Hormuz has sent Brent prices soaring, widened India's current account deficit, pushed the rupee to 95.68 against the dollar, and forced the Reserve Bank of India into a defensive posture. Goldman Sachs analysts now forecast 50 basis points of additional rate hikes for India in 2026.

## Domestic Buyers Are the Last Line of Defence

The market has not collapsed entirely thanks to domestic institutional investors (DIIs) and the systematic investment plan (SIP) revolution. Monthly SIP contributions have grown nearly tenfold over the past decade, creating a structural floor of domestic buying that foreign exits alone cannot overwhelm.

"It is thanks to local DIIs and liquidity from retail participants the market has held up," said **Aman Sethia**, head of treasury at Groww. "If this hadn't been in place, we would have seen the Nifty at around 19,000 or 20,000 over the last year."

But even the SIP engine is showing signs of fatigue. According to **Copley Fund Research**, average India weights in global funds tracked by the firm now stand at 9.94% — the first time India has dipped below 10% since January 2021, and a far cry from the highs of 17.47% in August 2024. India's fifth spot in global market capitalisation, valued at $4.92 trillion, is now under threat as Taiwan closes in.

## No AI Story, No Easy Fix

A slim majority of analysts — 13 of 24 — said a further correction was likely over the coming three months. The core problem is structural: India's corporate sector has not built significant AI capabilities or AI-linked revenue streams, leaving it out of the single largest wealth-creation cycle in global equity markets.

"A culture of innovation — that thing is absent in our country," said **Kishan Gupta**, director at CD Equisearch. "Our exports are not growing and we know import bills will swell now with high energy prices."

## What NRI Investors Should Watch

For the millions of diaspora investors who hold Indian equities through mutual funds, PMS schemes, or direct NRE/NRO demat accounts, the message from the poll is sobering but not catastrophic. The median forecast still expects a recovery to Nifty 27,000 by mid-2027 and 29,000 by end-2027 — roughly 20% upside from current levels over 18 months.

The near-term catalysts to watch: any resolution to the Iran-Hormuz crisis that brings oil prices back below $90, a stabilisation in the rupee, and the September quarter earnings season that could reveal whether India Inc. has any AI-adjacent growth story to tell. Until then, the world's fastest-growing major economy will keep losing the fight for global capital to markets that are growing faster in the one sector that matters most right now.""",
    "source": "The Videshi",
    "image_attribution": "Pexels",
})

# ═══════════════════════════════════════════════════════════════════
# ARTICLE 3: American Airlines Doubles India Tech Hub
# ═══════════════════════════════════════════════════════════════════

articles.append({
    "headline": "American Airlines Will Double Its India Tech Hub to 800 People. Southwest Just Expanded to 1,000. The GCC Boom Has Reached the Airlines.",
    "subheadline": "India now hosts over 2,100 global capability centres employing 2.36 million people and generating $100 billion in revenue. The latest entrants: America's two biggest domestic carriers.",
    "slug": "american-airlines-southwest-india-gcc-tech-hub-hyderabad-double-20260527",
    "sources": ["Reuters", "Nasscom-Zinnov 2026 Report"],
    "image_person": None,
    "image_pexels_query": "Hyderabad India technology office skyline",
    "image_pexels_fallback": "India technology hub office workers",
    "vertical": "technology",
    "body": """American Airlines plans to double headcount at its India technology hub to approximately 800 employees by early 2027, two people familiar with the matter told Reuters on Wednesday. The expansion comes just a week after rival Southwest Airlines announced plans to grow its Hyderabad global capability centre (GCC) to about 1,000 employees over the next few years.

The moves mark a new chapter in India's GCC story — one in which even America's legacy carriers, long focused on domestic operations, are building significant technology operations in India's southern tech corridor.

## From Back Office to Core Engineering

American Airlines established its Hyderabad hub in 2024 with roughly 400 staff focused on software engineering, artificial intelligence, and cybersecurity. The planned doubling would take the centre to 800 people working on core airline technology — not customer service scripts or data entry, but the digital infrastructure that keeps 6,700 daily flights in the air.

"Teams in Fort Worth, Phoenix and Hyderabad work closely with the business to digitize processes, deploy new tools that improve speed to market and business outcomes, and build a more resilient airline and better experience for team members and customers," American Airlines told Reuters.

The airline said it has increased both IT investment and U.S.-based technology headcount every year since 2021 — the India expansion is additive, not a replacement for domestic hiring.

## The $100 Billion Machine

India has emerged as the world's largest GCC hub by every metric that matters. According to the **2026 Nasscom-Zinnov report**, the country now hosts more than 2,100 global capability centres employing approximately 2.36 million people and generating nearly $100 billion in annual revenue.

The roster reads like a who's who of global capitalism: **JPMorgan Chase**, **Walmart**, **McDonald's**, **Nvidia**, **Eli Lilly**, and now the two largest U.S. domestic airlines. What started as a cost arbitrage play — hiring Indian engineers at a fraction of Silicon Valley salaries — has evolved into something more fundamental. These centres now handle engineering, R&D, finance, analytics, and strategic operations.

The shift reflects two converging forces. First, the cost of talent in the United States and Europe has risen sharply, particularly for AI and cybersecurity specialists. Second, macroeconomic uncertainty — driven by the Iran war's energy shock, rising interest rates, and trade policy volatility — has pushed companies to build geographically distributed teams that can absorb disruption.

## Hyderabad's Quiet Dominance

While Bengaluru remains India's startup capital and Mumbai its financial hub, Hyderabad has emerged as the preferred destination for GCC operations. The city's advantages include lower real estate costs than Bengaluru, a deep talent pipeline from institutions like the Indian School of Business, IIIT Hyderabad, and the University of Hyderabad, and a state government that has been aggressively courting multinational tech investment for over two decades.

Both American Airlines and Southwest chose Hyderabad over Bengaluru, Chennai, and Pune — the other top contenders. The city is now home to GCCs from Google, Microsoft, Amazon, Apple, Meta, Qualcomm, Wells Fargo, Deloitte, and dozens more.

## The Model Is Changing

The most significant shift in India's GCC story is functional, not geographic. A decade ago, these centres were synonymous with cost savings — companies moved low-value tasks offshore to trim margins. Today, the conversation has inverted. Companies are moving high-value work to India because the talent is genuinely competitive at the frontier.

American Airlines' Hyderabad hub works on AI and cybersecurity — not legacy mainframe maintenance. Southwest's centre builds operational technology. JPMorgan's India operations include quantitative research and risk modelling. Nvidia's Indian engineers work on GPU architecture and CUDA development.

This evolution carries implications for India's broader economic narrative. At a moment when the country's IT outsourcing giants — TCS, Infosys, Wipro, HCL Tech — are facing margin pressure and headcount reductions driven by AI automation, the GCC sector is growing in the opposite direction. The irony is sharp: the same AI revolution that threatens India's outsourcing model is fuelling the GCC model, because building and deploying AI requires exactly the kind of deep engineering talent that India's elite institutions produce.

## What It Means for the Diaspora

For Indian Americans working in U.S. aviation, finance, or technology, the GCC expansion creates two-way career pathways that did not exist a decade ago. Engineers who build systems in Fort Worth can rotate through Hyderabad; talent developed in India can eventually move into leadership roles at U.S. headquarters.

The broader signal is structural: India's place in the global economy is shifting from labour arbitrage to capability arbitrage. The question is whether the country can sustain the talent pipeline — and the infrastructure — to support a $100 billion sector that shows no signs of slowing down.""",
    "source": "The Videshi",
    "image_attribution": "Pexels",
})


# ── MAIN ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("The Videshi — News Writer (2026-05-27 evening)")
    print("=" * 60)

    for i, article in enumerate(articles, 1):
        print(f"\n{'─' * 50}")
        print(f"Article {i}: {article['headline'][:70]}...")
        print(f"{'─' * 50}")

        # Dedup check
        slug_core = article["slug"].replace("-20260527", "").split("-")[0:4]
        slug_fragment = "-".join(slug_core)
        if check_duplicate(slug_fragment):
            print(f"  ⏭ Skipping — possible duplicate found")
            continue

        # Image sourcing
        img_url = None
        attribution = "The Videshi"

        # Step 1: Try Wikipedia if person article
        if article.get("image_person"):
            img_url = fetch_wikipedia_person_image(article["image_person"])
            if img_url:
                attribution = "Wikimedia Commons"

        # Step 2: Pexels fallback
        if not img_url:
            img_url = fetch_pexels_image(
                article.get("image_pexels_query", ""),
                article.get("image_pexels_fallback", ""),
            )
            if img_url:
                attribution = "Pexels"

        # Step 3: Validate and upload
        final_image_url = None
        if img_url:
            if validate_image(img_url):
                # Upload to Supabase for permanence
                ext = "jpg"
                filename = f"{article['slug']}.{ext}"
                final_image_url = upload_image_to_supabase(img_url, filename)
                if not final_image_url:
                    # Use direct URL if upload fails (only for permanent sources)
                    if "upload.wikimedia.org" in img_url or "images.pexels.com" in img_url:
                        final_image_url = img_url
                        print(f"  ℹ Using direct URL as fallback")
            else:
                print(f"  ⚠ Image failed validation, trying without image")

        article["image_url"] = final_image_url
        article["image_attribution"] = attribution if final_image_url else None

        # Word count check
        word_count = len(article["body"].split())
        print(f"  📝 Word count: {word_count}")
        if word_count < 400:
            print(f"  ❌ Below 400-word floor! Skipping.")
            continue

        # Publish
        art_id = publish_article(article)
        if art_id and final_image_url:
            print(f"  🖼 Image: {final_image_url[:80]}...")

    print(f"\n{'=' * 60}")
    print("Done.")
