#!/usr/bin/env python3
"""
The Videshi — News Writer (May 27, 2026 morning run v2)
Publishes 3 news articles with proper images, dedup, and quality.
"""

import json, os, re, sys, time, uuid, urllib.parse
from datetime import datetime, timezone, timedelta

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
    """Fetch image from Pexels."""
    if not PEXELS_API_KEY:
        print("  ⚠ No Pexels API key")
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
        if "image" in ct:
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


def check_slug_exists(slug):
    """Check if an article with this exact slug already exists."""
    try:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/p2_articles",
            params={
                "select": "id,slug",
                "slug": f"eq.{slug}",
                "limit": "1"
            },
            headers=HEADERS,
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            if data:
                print(f"  ⚠ Slug already exists: {slug}")
                return True
    except Exception as e:
        print(f"  ⚠ Slug check error: {e}")
    return False


def check_headline_overlap(headline, category="news"):
    """Check for substantially similar headlines in recent articles."""
    try:
        ts = (datetime.now(timezone.utc) - timedelta(days=3)).strftime('%Y-%m-%dT00:00:00Z')
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/p2_articles",
            params={
                "select": "headline,slug",
                "status": "eq.published",
                "published_at": f"gte.{ts}",
                "order": "published_at.desc",
                "limit": "80"
            },
            headers=HEADERS,
            timeout=15
        )
        if r.status_code == 200:
            existing = r.json()
            # Extract significant words (4+ chars) from headline
            sig_words = set(w.lower() for w in re.findall(r'\b[a-zA-Z]{4,}\b', headline))
            for art in existing:
                existing_words = set(w.lower() for w in re.findall(r'\b[a-zA-Z]{4,}\b', art.get("headline", "")))
                overlap = sig_words & existing_words
                # Need 6+ significant word matches to flag as duplicate
                if len(overlap) >= 6:
                    print(f"  ⚠ High overlap ({len(overlap)} words) with: {art['headline'][:70]}")
                    print(f"    Shared words: {', '.join(list(overlap)[:10])}")
                    return True
    except Exception as e:
        print(f"  ⚠ Headline check error: {e}")
    return False


# --- Articles ---

articles = []

# ============================================================
# ARTICLE 1: Iran-US Draft MoU — The Deal Text
# ============================================================

art1_body = """Iranian state television on Tuesday revealed what it called a draft of an initial, unofficial framework for a memorandum of understanding between Tehran and Washington — the most detailed picture yet of what a deal to end the three-month-old war could look like.

## What the Draft Framework Says

Under the proposed MoU, Iran would restore commercial shipping through the Strait of Hormuz to pre-war levels within one month. In exchange, the United States would withdraw military forces from Iran's vicinity and lift its naval blockade of Iranian ports.

The framework excludes military vessels entirely. Ship traffic through the strait would be managed by Iran in cooperation with Oman — a provision that would effectively hand Tehran a gatekeeping role over the world's most critical oil chokepoint.

If a final agreement is reached within 60 days, the MoU could be approved as a binding United Nations Security Council resolution, according to the state TV broadcast. Tehran emphasised that no step would be taken without "tangible verification."

## Pakistan as Mediator, India on the Sidelines

The emerging framework stems from indirect talks launched after the war began in February, with Pakistan playing a central mediating role between Tehran and Washington. Pakistan Army Chief Asim Munir has been repeatedly praised by President Trump for his role — a dynamic that has deeply unsettled New Delhi, given the longstanding India-Pakistan rivalry.

For India, being sidelined in the resolution of a conflict that directly threatens its energy security is a strategic embarrassment. The country imports roughly 85 percent of its crude oil, and the strait's near-total closure has sent petrol prices past ₹100 per litre, pushed the rupee to 95.68 against the dollar, and forced a frantic reorientation of supply chains toward Venezuela, Brazil, Angola, and Nigeria.

## The Impasse

Despite the draft's detail, the Institute for the Study of War assessed that talks remain at a "major impasse." The core obstacles are formidable:

Iran is demanding the U.S. unfreeze $12 billion of $24 billion in frozen Iranian assets as a precondition for signing the MoU. Tehran's Foreign Affairs Ministry spokesperson explicitly said the money would be used to "reconstitute and improve" its ballistic missile and drone programmes — a statement that makes the demand all but impossible for Washington to accept.

Iran insists on retaining the right to enrich uranium on its own territory. The U.S. has made it clear there will be no sanctions relief without serious commitments on Iran's nuclear programme.

Supreme Leader Mojtaba Khamenei's guidance to the Iranian government on May 25 directed that Iran must "leverage the strait for economic gain" — a position fundamentally at odds with the free-navigation principles that India, Japan, South Korea, and other major importers have insisted on.

Iran is also demanding an end to hostilities "on all fronts," including Lebanon. But Israeli Prime Minister Benjamin Netanyahu has announced a deepening operation against Hezbollah, and Trump has backed Israel's right to act against imminent threats.

## Trump Convenes Full Cabinet

Trump convened a full Cabinet meeting at the White House on Wednesday to discuss the war's endgame. He moved the meeting from Camp David, citing "possible bad weather conditions." Defence Secretary Pete Hegseth departed for Singapore for the annual Shangri-La Dialogue, where he will deliver remarks on "United States' Strategy for Peace in the Indo-Pacific."

Secretary of State Marco Rubio, speaking from Jaipur during his four-day India visit, said negotiating the deal's language could "take a few days." Former Army Vice Chief General Jack Keane said on Fox News that the Iranians are "clearly not negotiating in good faith," citing their continued mining of the strait.

## What It Means for India

Every week the strait remains closed adds roughly ₹2 to the price of a litre of petrol and drains an estimated $1.5 billion from India's foreign exchange reserves. The Reserve Bank of India has intervened in currency markets to support the rupee, and traders are pricing in up to 100 basis points of rate hikes if oil stays above $95 per barrel.

A reopening within a month would offer immediate relief. But Iran's insistence on managing ship traffic — rather than restoring the pre-war status quo — could keep insurance premiums and shipping costs elevated for months even after an agreement.

India's 200 million Muslims are celebrating Eid al-Adha this week. The economy they're celebrating in is one where cooking gas and petrol have become luxury items, and the outcome of a deal being negotiated thousands of miles away — without India at the table — will determine whether that changes.

*Sources: Reuters, Washington Examiner, ISW, Livemint, Fox News*"""

articles.append({
    "headline": "Iran Has Revealed the Text of a Draft Deal With the U.S. Hormuz Would Reopen in a Month. India Is Not at the Table.",
    "subheadline": "The unofficial framework envisions Iran managing ship traffic with Oman, a 60-day window for a binding UN Security Council resolution, and $12 billion in frozen assets as the price of entry. The ISW says talks are at a 'major impasse.'",
    "slug": "iran-draft-mou-framework-hormuz-reopen-month-india-not-at-table-20260527",
    "body": art1_body,
    "category": "news",
    "person_for_image": "Mojtaba Khamenei",
    "pexels_query": "strait of hormuz shipping oil tanker",
    "pexels_fallback": "oil tanker cargo ship ocean",
    "sources": ["Reuters", "Washington Examiner", "ISW", "Livemint", "Fox News"],
})

# ============================================================
# ARTICLE 2: H-1B Registrations Drop 38.5%
# ============================================================

art2_body = """U.S. Secretary of State Marco Rubio stood next to External Affairs Minister S. Jaishankar in New Delhi on Sunday and insisted — emphatically, repeatedly — that America's sweeping visa overhaul is not targeted at India. "The changes that are happening now are not India-specific; it is global," he said.

The numbers say otherwise.

## The 38.5% Collapse

H-1B visa registrations dropped 38.5 percent in fiscal year 2027, from 343,981 applications to just 211,600, according to data released by U.S. Citizenship and Immigration Services. The agency framed the decline as a deliberate correction — a feature, not a bug.

"We're approving more applicants with advanced degrees and higher salaries, especially those who studied at US universities," USCIS said. "An overwhelming 71.5 percent of selected aliens hold a US master's degree or higher, compared to 57 percent last year."

The agency added that only 17.7 percent of selected registrations were in the lowest wage category, calling it "a clear sign that the days of abusing the programme with mass, low-wage registrations are over."

## India's IT Giants Take the Hardest Hit

The arithmetic is straightforward. Indians account for approximately 71 percent of all approved H-1B applications. Any system-wide tightening lands disproportionately on Indian applicants — regardless of whether the intent is "global."

India's six largest IT services firms — TCS, Cognizant, Infosys, HCL Technologies, Wipro, and Tech Mahindra — collectively received 11,041 H-1B visas as of March 31, 2026. That represents a 40 percent decline from the previous year, when the same group received approximately 18,469 visas.

The contrasts within the group are striking. Infosys received 3,195 approvals — the highest in the cohort and the only firm to record an increase. TCS suffered the steepest drop, with approvals falling by 3,242 to approximately 2,885.

## The Green Card Bombshell

Perhaps the most disruptive development came on May 22, when USCIS announced that foreign nationals seeking permanent residency must now physically return to their home country to submit their Green Card applications.

"From now on, an alien who is in the US temporarily and wants a green card must return to their home country to apply, except in extraordinary circumstances," said Zach Kahler, a USCIS spokesman.

For Indian nationals, this is devastating. The Green Card backlog for India spans multiple decades. Workers who have spent ten or fifteen years building careers and lives in America — paying taxes, buying homes, raising children in American schools — now face a choice: leave the country to apply for a Green Card and potentially wait years to return, or stay and abandon the path to permanent residency entirely.

There is a narrow exception: USCIS has issued separate guidelines allowing some H-1B holders to remain in the U.S. during the Green Card process in "extraordinary circumstances." But the default has flipped. The presumption is now that you leave.

## The 33% Wage Hike Proposal

On top of the registration decline and the Green Card rule, the U.S. Department of Labour has proposed raising minimum prevailing wages for H-1B workers by as much as 33 percent across entry-level positions.

Under the proposed changes, the prevailing wage for entry-level foreign workers would rise to $97,746 per year, up from $73,279 — a jump of 33.4 percent. Level II workers would see wages rise to $123,212 from $98,987. Level III positions would move to $147,333, and Level IV — the most experienced workers — to $175,464.

The Department of Labour argues that existing wage levels were set more than two decades ago and no longer protect American workers from being undercut by cheaper foreign labour.

## Rubio's Impossible Needle

Rubio acknowledged that the changes would have a "disproportionate" impact on Indian students, engineers, and tech workers. He invoked his own family's immigrant story — his parents arrived from Cuba in 1956 — and insisted the U.S. remains "the most welcoming country in the world for immigration."

But his reassurance collides with a reality where the three pillars of the Indian professional pipeline to America — H-1B entry, employer-sponsored Green Cards, and wage-competitive hiring — are all being simultaneously squeezed. Rubio acknowledged the impact is disproportionate while insisting the intent is not discriminatory. For the estimated 800,000 Indians in the H-1B and Green Card queue, the distinction is academic.

*Sources: Livemint, USCIS, Fox News, Wall Street Journal*"""

articles.append({
    "headline": "H-1B Registrations Just Dropped 38.5 Percent. Rubio Says It's Not About India. The Numbers Say Otherwise.",
    "subheadline": "The six largest Indian IT firms lost 40 percent of their H-1B approvals in one year. A new rule forces Green Card applicants to leave the country. Proposed wage floors would rise 33 percent. And the Secretary of State says none of it is targeted.",
    "slug": "h1b-registrations-drop-38-percent-rubio-india-green-card-leave-country-20260527",
    "body": art2_body,
    "category": "news",
    "person_for_image": None,
    "pexels_query": "US visa passport immigration office",
    "pexels_fallback": "passport visa immigration documents",
    "sources": ["Livemint", "USCIS", "Fox News", "Wall Street Journal"],
})

# ============================================================
# ARTICLE 3: Bengaluru Ebola Tests Negative
# ============================================================

art3_body = """The 28-year-old Ugandan woman quarantined in Bengaluru on suspicion of carrying the Ebola virus has tested negative, averting what would have been South Asia's first confirmed case since 2014.

Samples sent to the National Institute of Virology in Pune came back clear, bringing to an end a scare that had put India's entire public health apparatus on high alert and dominated national headlines for 48 hours.

## How the Scare Unfolded

The woman, who had arrived from Uganda, was isolated at Bengaluru's Epidemic Diseases Hospital after airport screening flagged fatigue and mild symptoms. She showed no obvious severe symptoms — no fever spike, no haemorrhaging — but the global context made every screening hit a potential crisis.

The World Health Organisation had declared the ongoing Ebola outbreak a Public Health Emergency of International Concern just days earlier. The outbreak, caused by the rare Bundibugyo strain for which there is no approved vaccine, has killed 241 people across the Democratic Republic of Congo and Uganda, with over 1,000 confirmed cases.

India took no chances. Repeat testing was conducted as a precaution, given the Bundibugyo strain's variable incubation period. The negative results came back from the NIV Pune laboratory after exhaustive analysis.

## India's Preparedness Under the Microscope

Health Minister J.P. Nadda ordered intensified surveillance across the country even before the test results returned. The measures include enhanced airport screenings at all international terminals, with heightened protocols for passengers arriving from the DRC, Uganda, and South Sudan.

Travel advisories urging Indians to avoid non-essential visits to affected African nations were issued within hours of the WHO declaration. Standard operating procedures have been distributed to every state health department, and isolation wards have been activated at designated hospitals in every major metro.

India's response was swift — markedly different from the chaotic early days of the COVID-19 pandemic. The screening system at Bengaluru's airport caught the potential case on arrival, the quarantine was immediate, and the testing pipeline delivered results within 48 hours.

## The Diaspora Dimension

For the estimated 30,000 Indians living and working in East Africa — including significant communities in Uganda, Kenya, and Tanzania — the outbreak has created a new layer of anxiety. Return travel to India now involves enhanced screening, potential quarantine, and the social stigma that follows travellers from affected regions.

Canada has already suspended visas for nationals of the DRC, Uganda, and South Sudan for 90 days and imposed a 21-day quarantine for asymptomatic travellers. India has stopped short of visa suspensions, but pressure to tighten entry requirements will grow if the outbreak spreads further.

The FIFA World Cup, scheduled to begin in weeks, has added urgency to global containment efforts. Large international gatherings are precisely the transmission vectors that make epidemiologists lose sleep.

## Relief, Not Resolution

The negative result is reassuring but not conclusive about India's long-term risk. The Bundibugyo strain is the least-studied of the five known Ebola species, and the absence of a vaccine means containment depends entirely on surveillance, isolation, and contact tracing.

With monsoon season approaching and international travel volumes rising through the summer, India's airport screening infrastructure faces its most sustained test since the pandemic. The Bengaluru case proved the system can detect and respond to a potential case. The question is whether it can sustain that vigilance across dozens of airports, hundreds of flights, and thousands of passengers arriving from affected regions every week.

The system worked this time. It needs to keep working.

*Sources: Reuters, Bharat Affairs, WHO, Latestly, News Dive*"""

articles.append({
    "headline": "Bengaluru's Ebola Scare Is Over. The Quarantined Ugandan Woman Tested Negative. India's Airport System Worked.",
    "subheadline": "India averted what would have been South Asia's first Ebola case since 2014. The screening infrastructure caught the case on arrival, the quarantine was immediate, and the NIV Pune lab delivered results in 48 hours. But the outbreak that triggered the scare is still growing.",
    "slug": "bengaluru-ebola-test-negative-india-airport-screening-worked-20260527",
    "body": art3_body,
    "category": "news",
    "person_for_image": None,
    "pexels_query": "airport health thermal screening passengers",
    "pexels_fallback": "hospital quarantine medical isolation",
    "sources": ["Reuters", "Bharat Affairs", "WHO", "Latestly", "News Dive"],
})


# ============================================================
# PUBLISH
# ============================================================

def publish_article(art):
    print(f"\n{'='*60}")
    print(f"Publishing: {art['headline'][:70]}...")

    # 1. Check slug doesn't exist
    if check_slug_exists(art['slug']):
        print("  ⚠ Skipping — slug already exists")
        return None

    # 2. Headline overlap check
    if check_headline_overlap(art['headline'], art['category']):
        print("  ⚠ Skipping — high headline overlap with existing article")
        return None

    # 3. Image sourcing
    image_url = None
    image_attribution = None

    if art.get("person_for_image"):
        image_url = fetch_wikipedia_person_image(art["person_for_image"])
        if image_url:
            image_attribution = "Wikimedia Commons"

    if not image_url and art.get("pexels_query"):
        image_url = fetch_pexels_image(art["pexels_query"], art.get("pexels_fallback"))
        if image_url:
            image_attribution = "Pexels"

    if image_url and not validate_image_url(image_url):
        print(f"  ✗ Image failed validation, publishing without image")
        image_url = None
        image_attribution = None

    # 4. Word count check
    word_count = len(art['body'].split())
    if word_count < 400:
        print(f"  ✗ Body too short ({word_count} words). Minimum is 400.")
        return None
    print(f"  ℹ Word count: {word_count}")

    # 5. Build record
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
        "sources": [{"name": s} for s in art["sources"]],
        "word_count": word_count,
        "vertical": art["category"],
    }

    if image_url:
        record["image_url"] = image_url
    if image_attribution:
        record["image_attribution"] = image_attribution

    # 6. Insert
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
    if success_count == 0:
        sys.exit(1)
