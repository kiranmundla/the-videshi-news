#!/usr/bin/env python3
"""
The Videshi — News Writer (May 27, 2026 morning run)
Publishes 3 news articles with proper images, dedup, and quality.
"""

import json, os, re, sys, time, uuid, urllib.parse
from datetime import datetime, timezone

import requests

# --- Config ---
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# --- Helpers ---

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
    """Fetch image from Pexels with curl-like headers."""
    if not PEXELS_API_KEY:
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            r = requests.get(
                "https://api.pexels.com/v1/search",
                params={"query": q, "per_page": 5, "orientation": "landscape"},
                headers={"Authorization": PEXELS_API_KEY},
                timeout=10
            )
            if r.status_code == 200:
                photos = r.json().get("photos", [])
                for photo in photos:
                    url = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("original")
                    if url:
                        print(f"  ✓ Pexels image for '{q}': {url[:80]}...")
                        return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image_url(url):
    """Validate that URL returns a real image > 5KB."""
    if not url:
        return False
    # Block banned sources
    banned = ['fbcdn.net', 'cdninstagram.com', 'lookaside.fbsbx.com']
    if any(b in url for b in banned):
        print(f"  ✗ BANNED source: {url[:60]}")
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if "image" in ct and cl > 5000:
            return True
        # Some servers don't return Content-Length on HEAD; try GET
        if "image" in ct and cl == 0:
            r2 = requests.get(url, timeout=10, stream=True,
                            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                return True
        print(f"  ✗ Image validation failed: ct={ct}, cl={cl}")
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
    return False


def sb_insert(table, data):
    """Insert into Supabase table."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers=HEADERS,
        json=data,
        timeout=30
    )
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            return result[0]
        return result
    print(f"  ✗ Insert error ({r.status_code}): {r.text[:200]}")
    return None


def check_duplicate(headline_keywords):
    """Check if a similar article was published recently."""
    try:
        three_days_ago = datetime.now(timezone.utc).strftime('%Y-%m-%dT00:00:00Z')
        # Rough timestamp for 3 days ago
        from datetime import timedelta
        ts = (datetime.now(timezone.utc) - timedelta(days=3)).strftime('%Y-%m-%dT00:00:00Z')
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/p2_articles",
            params={
                "select": "headline,slug",
                "status": "eq.published",
                "published_at": f"gte.{ts}",
                "category": "eq.news",
                "order": "published_at.desc",
                "limit": "50"
            },
            headers=HEADERS,
            timeout=15
        )
        if r.status_code == 200:
            existing = r.json()
            for art in existing:
                h = art.get("headline", "").lower()
                matches = sum(1 for kw in headline_keywords if kw.lower() in h)
                if matches >= 3:
                    print(f"  ⚠ Possible duplicate: {art['headline'][:80]}")
                    return True
    except Exception as e:
        print(f"  ⚠ Dedup check error: {e}")
    return False


# --- Articles ---

articles = []

# ============================================================
# ARTICLE 1: Iran-US Draft MoU Framework Revealed
# ============================================================

art1_headline = "Iran Says It Has the Text of a Draft Deal With the U.S. The Strait of Hormuz Would Reopen Within a Month."
art1_subheadline = "The unofficial framework envisions Iran managing ship traffic through the strait with Oman, a 60-day window for a binding UN Security Council resolution, and U.S. military withdrawal — but Tehran says it won't move without 'tangible verification.'"
art1_slug = "iran-us-draft-mou-hormuz-reopen-60-day-unsc-framework-india-oil-20260527"

art1_body = """Iranian state television on Tuesday revealed what it called a draft of an initial, unofficial framework for a memorandum of understanding between Tehran and Washington — the most detailed picture yet of what a deal to end the three-month-old war could look like.

## What the Framework Says

Under the proposed MoU, Iran would restore commercial shipping through the Strait of Hormuz to pre-war levels within one month. In exchange, the United States would withdraw military forces from Iran's vicinity and lift its naval blockade of Iranian ports.

The framework excludes military vessels entirely. Ship traffic through the strait would be managed by Iran in cooperation with Oman — a provision that effectively gives Tehran a gatekeeping role over the world's most critical oil chokepoint.

If a final agreement is reached within 60 days, the MoU could be approved as a binding United Nations Security Council resolution, according to Iranian state TV.

## Pakistan's Central Role

The emerging framework stems from indirect talks launched after the war began in February, with Pakistan playing a central mediating role between Tehran and Washington. Pakistan Army Chief Asim Munir has been repeatedly praised by President Trump for his mediation efforts — a dynamic that has rattled India, given the longstanding rivalry between New Delhi and Islamabad.

## Why It Matters for India

The Hormuz crisis has hit India harder than almost any other major economy. India imports roughly 85 percent of its crude oil, and the strait's near-total closure since February has sent petrol prices past ₹100 per litre, pushed the rupee to 95.68 against the dollar, and forced the country to scramble for alternative supplies from Venezuela, Brazil, Angola, and Nigeria.

A reopening of the strait within a month would provide immediate relief to Indian consumers and businesses. But the framework's provision for Iranian management of ship traffic — rather than a return to the pre-war status quo — introduces a new variable that could keep insurance premiums and shipping costs elevated.

The Reserve Bank of India has already signalled concern. Traders are pricing in up to 100 basis points of rate hikes if oil stays above $95 per barrel, and the RBI intervened in currency markets this week to support the rupee.

## The Sticking Points

Despite the detail in the draft, significant obstacles remain. The Institute for the Study of War assessed that talks are at a "major impasse":

- Iran is demanding the U.S. unfreeze $12 billion of $24 billion in frozen Iranian assets as a condition for signing the MoU — and has explicitly said it would use the money to rebuild its ballistic missile and drone programmes.
- Iran insists on retaining the right to enrich uranium on Iranian soil, while the U.S. demands serious commitments on the nuclear programme before any sanctions relief.
- Iran wants the deal to cover "all fronts," including Lebanon, where Israeli Prime Minister Netanyahu has announced a deepening operation against Hezbollah.

Supreme Leader Mojtaba Khamenei's guidance to the Iranian government on May 25 said Iran must "leverage the strait for economic gain" — a position fundamentally at odds with the free-navigation principles India and other major importers have insisted on.

## What Happens Next

Trump convened a full Cabinet meeting on Wednesday to discuss the war's endgame. Secretary of State Marco Rubio, speaking from Jaipur during his four-day India visit, said negotiating the deal's language could "take a few days."

For India's 1.4 billion people, every one of those days matters. Each week the strait remains closed adds roughly ₹2 to the price of a litre of petrol and drains an estimated $1.5 billion from India's foreign exchange reserves.

*Sources: Reuters, Washington Examiner, ISW, Livemint*"""

art1_keywords = ["iran", "draft", "deal", "hormuz", "mou", "framework"]

articles.append({
    "headline": art1_headline,
    "subheadline": art1_subheadline,
    "slug": art1_slug,
    "body": art1_body,
    "category": "news",
    "keywords": art1_keywords,
    "person_for_image": "Mojtaba Khamenei",
    "pexels_query": "strait of hormuz oil tanker ship",
    "pexels_fallback": "oil tanker shipping gulf",
    "sources": ["Reuters", "Washington Examiner", "ISW", "Livemint"],
    "image_attribution": None,
})

# ============================================================
# ARTICLE 2: Rubio's 4-Day India Visit
# ============================================================

art2_headline = "Rubio Spent Four Days in India Trying to Repair the Damage. Trump Called In to Say 'I Love India.' Here's What Actually Happened."
art2_subheadline = "The secretary of state visited four cities, took his wife to the Taj Mahal, and insisted the friction hadn't knocked the relationship off course. India's foreign minister had a two-word response: 'India First.'"
art2_slug = "rubio-four-day-india-visit-trump-i-love-india-jaishankar-india-first-20260527"

art2_body = """At a splashy U.S. Embassy celebration in New Delhi featuring Bollywood dance numbers and life-size cutouts of Trump officials, President Trump called in on speakerphone to deliver his message to more than 1,500 guests.

"I love India," he said. "We've never been closer to India. India can count on me 100 percent."

The call was part of a carefully choreographed four-day visit by Secretary of State Marco Rubio — his first trip to the country — designed to repair one of Washington's most important partnerships at a moment of genuine strain.

## The Rift

Beneath the pageantry, the relationship between the world's two largest democracies has been rattled by a cascade of Trump administration moves:

**Tariffs.** Trump imposed 50 percent tariffs on Indian goods last summer — the highest new tariffs for any country in Asia. The tariffs were later struck down by U.S. courts, but the signal they sent has not been forgotten.

**Immigration.** Changes to U.S. visa policy have hit Indian skilled workers and students disproportionately. Rubio acknowledged the impact was "disproportionate" on Indian engineers and tech workers but insisted the changes were "not targeted at India" and were "being applied globally."

**Pakistan.** Trump's enthusiastic embrace of Pakistan — India's longtime rival — has been particularly galling to New Delhi. Since Pakistan emerged as a key mediator between the U.S. and Iran in April, Trump has repeatedly praised Pakistan Army Chief Asim Munir.

**China.** Trump's summit with Chinese leader Xi Jinping and his less confrontational approach to Beijing in his second term has unsettled India, which has clashed with China multiple times along their contested Himalayan border. China is also an ally and weapons supplier to Pakistan, including jet fighters used in last year's India-Pakistan conflict.

**The 'Hellhole' Comment.** Just weeks before Rubio arrived, Trump reposted comments calling India a "hellhole" — drawing a rare rebuke from India's foreign ministry that followed Rubio throughout his visit.

## 'India First'

Rubio framed the friction as a natural consequence of Trump's America First agenda. "This is not about India, it's about the United States in terms of trade," he said.

External Affairs Minister S. Jaishankar offered a pointed counterpart at a joint press conference: "The Trump administration has been very forthright in putting forward its foreign policy outlook as America First. Now, where we are concerned, we have a view of India First."

The exchange captured the dynamic perfectly — two nations that need each other but refuse to subordinate their own interests.

## What Rubio Accomplished

Rubio visited four cities — New Delhi, Kolkata, Agra, and Jaipur — and attended the Quad meeting with Australia and Japan on his final day. Key outcomes:

- **Modi White House Invitation.** Rubio extended an invitation from Trump for Modi to visit the White House. The personal bond between the two leaders has been a buffer as tensions mounted, with both leaning on it heavily in public.
- **Quad Continuity.** The Quad announced a $20 billion critical minerals initiative and agreed to build a port in Fiji — signals that the grouping remains active despite questions about Trump's commitment to Indo-Pacific alliances.
- **No New Deals.** Rubio did not announce any new trade agreements or visa concessions. The India-U.S. trade deal deadline remains July 8, and digital trade rules were explicitly deferred.

## The Assessment

"The soundtrack to U.S.-India relations is less discordant than it has been," said Michael Kugelman, a senior fellow at the Atlantic Council. "But there are very hard constraints that have made it difficult to bring the relationship back to where it was some years ago."

For the 4.4 million Indian Americans in the U.S. and the millions more who depend on trade, remittances, and visa pathways between the two countries, the visit offered warm words but few concrete answers. The tariffs remain a live issue. The visa squeeze continues. And Pakistan's elevated role in U.S. diplomacy shows no sign of fading.

*Sources: Wall Street Journal, Reuters, The Hindu Business Line*"""

art2_keywords = ["rubio", "india", "visit", "jaishankar", "trump"]

articles.append({
    "headline": art2_headline,
    "subheadline": art2_subheadline,
    "slug": art2_slug,
    "body": art2_body,
    "category": "news",
    "keywords": art2_keywords,
    "person_for_image": "Marco Rubio",
    "pexels_query": None,
    "pexels_fallback": None,
    "sources": ["Wall Street Journal", "Reuters", "The Hindu Business Line"],
    "image_attribution": None,
})

# ============================================================
# ARTICLE 3: Bengaluru Ebola Case Tests Negative
# ============================================================

art3_headline = "Bengaluru's Ebola Scare Is Over. The Quarantined Ugandan Woman Tested Negative."
art3_subheadline = "India averted what would have been South Asia's first Ebola case since 2014. But the scare has exposed how close the country came — and how much the airport screening system will be tested in the weeks ahead."
art3_slug = "bengaluru-ebola-quarantine-tests-negative-india-airport-screening-20260527"

art3_body = """The 28-year-old Ugandan woman quarantined in Bengaluru on suspicion of carrying the Ebola virus has tested negative, averting what would have been South Asia's first confirmed case since 2014.

Samples sent to the National Institute of Virology in Pune came back clear, bringing to an end a scare that had put India's public health system on high alert and dominated headlines for 48 hours.

## What Happened

The woman, who had arrived from Uganda, was isolated at Bengaluru's Epidemic Diseases Hospital after airport screening flagged fatigue and mild symptoms consistent with early-stage Ebola infection. She showed no obvious severe symptoms — no fever spike, no haemorrhaging — but the global context made every protocol non-negotiable.

The World Health Organisation had declared the ongoing Ebola outbreak — caused by the rare Bundibugyo strain, for which there is no approved vaccine — a Public Health Emergency of International Concern just days earlier. Over 1,000 cases and 241 deaths have been reported across the Democratic Republic of Congo and Uganda.

## India's Response

Health Minister J.P. Nadda intensified surveillance across the country even before the test results came back:

- **Airport screenings** have been scaled up at all international terminals, with enhanced protocols for passengers arriving from the DRC, Uganda, and South Sudan.
- **Travel advisories** urging Indians to avoid non-essential travel to affected African nations were issued within hours of the WHO declaration.
- **Standard operating procedures** have been distributed to state health departments, with isolation wards activated at designated hospitals in every major city.
- **Repeat testing** was conducted on the quarantined woman as a precaution, given the Bundibugyo strain's unpredictable incubation period.

## The Diaspora Dimension

For the estimated 30,000 Indians living and working in East Africa — including significant communities in Uganda, Kenya, and Tanzania — the outbreak has created a new layer of anxiety. Return travel to India now involves enhanced screening, potential quarantine, and the social stigma that comes with arriving from an affected region.

Canada has already suspended visas for nationals of the DRC, Uganda, and South Sudan for 90 days and imposed a 21-day quarantine for asymptomatic travellers — a move that has affected dual nationals in the Indian diaspora as well.

India has stopped short of visa suspensions, but the pressure to tighten entry requirements is likely to grow if the outbreak spreads further. The FIFA World Cup, scheduled for later this year, has added urgency to global containment efforts.

## What Comes Next

The negative result is relief, not resolution. The Bundibugyo strain is the least-studied of the five known Ebola species, and the absence of a vaccine means containment depends entirely on surveillance, isolation, and contact tracing — the same tools India used during the early days of COVID-19.

With monsoon season approaching and international travel volumes rising through the summer, the screening infrastructure at India's airports will face its most sustained test. The Bengaluru case proved the system can catch a potential case. The question is whether it can keep catching them.

*Sources: Reuters, Bharat Affairs, Latestly, WHO*"""

art3_keywords = ["bengaluru", "ebola", "negative", "quarantine", "test"]

articles.append({
    "headline": art3_headline,
    "subheadline": art3_subheadline,
    "slug": art3_slug,
    "body": art3_body,
    "category": "news",
    "keywords": art3_keywords,
    "person_for_image": None,
    "pexels_query": "airport health screening passengers",
    "pexels_fallback": "airport terminal security passengers",
    "sources": ["Reuters", "Bharat Affairs", "Latestly", "WHO"],
    "image_attribution": None,
})


# ============================================================
# PUBLISH
# ============================================================

def publish_article(art):
    print(f"\n{'='*60}")
    print(f"Publishing: {art['headline'][:70]}...")
    
    # 1. Dedup check
    if check_duplicate(art['keywords']):
        print("  ⚠ Skipping — possible duplicate detected")
        return None
    
    # 2. Image sourcing
    image_url = None
    image_attribution = None
    
    # Try Wikipedia first for person articles
    if art.get("person_for_image"):
        image_url = fetch_wikipedia_person_image(art["person_for_image"])
        if image_url:
            image_attribution = "Wikimedia Commons"
    
    # Fall back to Pexels
    if not image_url and art.get("pexels_query"):
        image_url = fetch_pexels_image(art["pexels_query"], art.get("pexels_fallback"))
        if image_url:
            image_attribution = "Pexels"
    
    # Validate image
    if image_url and not validate_image_url(image_url):
        print(f"  ✗ Image validation failed, publishing without image")
        image_url = None
        image_attribution = None
    
    # 3. Build record
    now = datetime.now(timezone.utc).isoformat()
    record = {
        "headline": art["headline"],
        "subheadline": art["subheadline"],
        "slug": art["slug"],
        "body": art["body"],
        "category": art["category"],
        "status": "published",
        "published_at": now,
        "created_at": now,
        "updated_at": now,
        "author": "The Videshi Newsroom",
        "sources": json.dumps(art["sources"]),
    }
    
    if image_url:
        record["image_url"] = image_url
    if image_attribution:
        record["image_attribution"] = image_attribution
    
    # 4. Insert
    result = sb_insert("p2_articles", record)
    if result:
        art_id = result.get("id", "unknown")
        print(f"  ✓ Published: {art['slug']} (id: {art_id})")
        return art_id
    else:
        print(f"  ✗ Failed to publish: {art['slug']}")
        return None


# --- Main ---

if __name__ == "__main__":
    print(f"The Videshi News Writer — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"Publishing {len(articles)} articles...")
    
    results = []
    for art in articles:
        art_id = publish_article(art)
        results.append({"slug": art["slug"], "id": art_id, "success": art_id is not None})
    
    print(f"\n{'='*60}")
    print("SUMMARY:")
    for r in results:
        status = "✓" if r["success"] else "✗"
        print(f"  {status} {r['slug']}")
    
    success_count = sum(1 for r in results if r["success"])
    print(f"\n{success_count}/{len(results)} articles published successfully.")
