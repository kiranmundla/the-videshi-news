#!/usr/bin/env python3
"""
The Videshi — News Writer (2026-05-28)
Generates 3 news articles with proper images and publishes to Supabase.
"""

import os, json, re, uuid, subprocess, urllib.parse, time
from datetime import datetime, timezone

# ─── Env ───
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")

HEADERS_JSON = f'-H "apikey: {SUPABASE_KEY}" -H "Authorization: Bearer {SUPABASE_KEY}" -H "Content-Type: application/json" -H "Prefer: return=representation"'

# ─── Image Sourcing ───

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        import requests
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            # Prefer originalimage (higher res), fall back to thumbnail AS-IS
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None


def fetch_pexels_image(query, fallback_query=None):
    """Fetch a relevant image from Pexels using curl (urllib gets 403)."""
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            cmd = f'curl -sS "https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape" -H "Authorization: {PEXELS_API_KEY}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
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
    """Validate that URL returns a real image > 5KB."""
    if not url:
        return False
    try:
        cmd = f'curl -sS -o /dev/null -w "%{{http_code}} %{{size_download}} %{{content_type}}" -L "{url}" --max-time 10'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        parts = result.stdout.strip().split()
        if len(parts) >= 2:
            code = parts[0]
            size = int(parts[1])
            if code == "200" and size > 5000:
                print(f"  ✓ Image validated: {code}, {size} bytes")
                return True
            else:
                print(f"  ✗ Image invalid: HTTP {code}, {size} bytes")
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False


def publish_article(article):
    """Publish article to Supabase."""
    payload = json.dumps(article).replace("'", "'\\''")
    cmd = f"""curl -sS -X POST '{SUPABASE_URL}/rest/v1/p2_articles' \
      -H 'apikey: {SUPABASE_KEY}' \
      -H 'Authorization: Bearer {SUPABASE_KEY}' \
      -H 'Content-Type: application/json' \
      -H 'Prefer: return=representation' \
      -d '{payload}'"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
    if result.returncode == 0:
        try:
            resp = json.loads(result.stdout)
            if isinstance(resp, list) and len(resp) > 0:
                print(f"  ✓ Published: {resp[0].get('headline', '?')[:60]}...")
                return True
            elif isinstance(resp, dict) and resp.get("message"):
                print(f"  ✗ Error: {resp['message']}")
                return False
        except:
            pass
    print(f"  ✗ Publish failed: {result.stdout[:200]}")
    print(f"  stderr: {result.stderr[:200]}")
    return False


# ═══════════════════════════════════════════════════
# ARTICLE 1: H-1B Green Card Crisis
# ═══════════════════════════════════════════════════

def write_article_1():
    print("\n📝 Article 1: H-1B Green Card Crisis")

    headline = "The U.S. Just Told H-1B Workers to Go Home to Get a Green Card. A Million Indians Are in Line."
    subheadline = "A new USCIS policy ends in-country green card processing for temporary visa holders. AI-driven layoffs are compounding the crisis, giving laid-off workers 60 days to find a new sponsor or leave."
    slug = "uscis-green-card-consular-processing-h1b-indian-workers-layoffs-20260528"

    body = """The American dream for Indian tech workers just got a forced layover.

Under a policy memo issued by U.S. Citizenship and Immigration Services in May 2026, foreign nationals on temporary visas — including the hundreds of thousands of Indians on H-1B work permits — will generally no longer be allowed to complete the green card application process from within the United States. Instead, they must return to their home country and apply through a U.S. embassy or consulate.

"From now on, an alien who is in the US temporarily and wants a Green Card must return to their home country to apply, except in extraordinary circumstances," USCIS spokesman Zach Kahler said in a statement.

## The Numbers Tell the Story

The impact is staggering. Over 1.2 million Indians are currently in employment-based green card backlogs, many of whom have lived and worked in the United States for a decade or more. Indian nationals accounted for 283,772 of the 406,348 approved H-1B petitions in fiscal year 2025 — roughly 70 percent of the total.

H-1B registrations have already dropped 38.5 percent under the new Trump administration rules. Secretary of State Marco Rubio, during his recent visit to India, pushed back on concerns that the policies specifically target Indians, calling them a global modernization effort. But the data suggests otherwise.

## AI Layoffs Compound the Crisis

The policy shift arrives at the worst possible time. A wave of AI-driven restructuring at major tech companies — Meta, Amazon, LinkedIn, and others — has left over 110,000 tech workers without jobs in 2026 so far. For H-1B holders, a layoff starts a 60-day clock: find a new employer willing to sponsor your visa, or leave the country.

Immigration attorney Rajiv Khanna told the Economic Times that scrutiny has intensified across the board. "We are seeing a significant spike in Requests for Evidence and Notices of Intent to Deny on change-of-status applications filed by laid-off H-1B workers," he said.

Some laid-off workers are scrambling for B-2 tourist visa conversions to buy time, but even those applications face rising denial rates. Others are exploring options in Canada, the U.K., or returning to India — where the booming Global Capability Center sector now employs many of the same companies that once sponsored their American visas.

## The Diaspora Impact

For the Indian American community — now the fastest-growing immigrant group in the United States — the policy represents a fundamental shift in the immigration bargain. Families who have built lives, bought homes, and put children through American schools now face the prospect of leaving the country to process paperwork that was previously handled domestically.

The per-country cap on green cards means Indian applicants already face estimated wait times of 50 to 80 years in some employment categories. The new consular processing requirement adds another layer of uncertainty: leaving the U.S. means risking delays, visa interview backlogs at overburdened consulates, and the possibility of being stuck abroad for months.

USCIS issued a partial clarification on May 26, noting that applicants who can demonstrate "economic or national interest benefits" may still qualify for in-country adjustment of status. But the criteria remain undefined, and immigration lawyers say the exception is likely to be narrow.

## What Comes Next

The policy change feeds into a broader pattern under the Trump administration's second term: tightening immigration pathways while maintaining the appearance of keeping the door open for skilled workers. The H-1B program was designed to bring the world's best talent to American companies. Whether it can continue to do that when the path from temporary work to permanent residency now requires leaving the country remains an open question.

For the million-plus Indians in the queue, the answer will shape not just their careers but their families, their children's futures, and the next chapter of the Indian American story.

*Sources: USCIS policy memo (May 2026), Livemint, Economic Times, Outlook Business, Fox News (Rubio interview), American Bazaar*"""

    # Image: Try Wikipedia for USCIS building or use Pexels
    print("  Sourcing image...")
    image_url = fetch_pexels_image("US visa stamp Indian passport", "immigration visa document")
    image_caption = "Indian H-1B workers face an uncertain path as new USCIS rules upend the green card process"
    image_attribution = "Pexels"

    if not validate_image_url(image_url):
        image_url = None
        image_caption = None
        image_attribution = None
        print("  ⚠ No valid image found, publishing without image")

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "slug": slug,
        "body": body,
        "category": "news",
        "vertical": "news",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": image_url,
        "image_caption": image_caption,
        "image_attribution": image_attribution,
        "sources": json.dumps([
            "USCIS policy memo (May 2026)",
            "Livemint",
            "Economic Times",
            "Outlook Business",
            "Fox News",
            "American Bazaar",
            "Archyde"
        ])
    }
    # Remove None values
    article = {k: v for k, v in article.items() if v is not None}
    return publish_article(article)


# ═══════════════════════════════════════════════════
# ARTICLE 2: Pope Leo's Encyclical
# ═══════════════════════════════════════════════════

def write_article_2():
    print("\n📝 Article 2: Pope Leo's Encyclical")

    headline = "Pope Leo Just Killed the 'Just War' Doctrine. His First Encyclical Also Wants to Regulate AI and Apologize for Slavery."
    subheadline = "Magnifica Humanitas — the first major document of Leo XIV's papacy — repudiates 1,600 years of Catholic war theory, calls for global AI regulation, and issues the Church's clearest apology for its role in transatlantic slavery."
    slug = "pope-leo-encyclical-magnifica-humanitas-just-war-ai-regulation-slavery-20260528"

    body = """The Catholic Church's new pope has declared war on war itself — and he did it while the Middle East burns.

In his first encyclical, released on May 25, Pope Leo XIV took a theological sledgehammer to one of Christianity's oldest and most politically convenient frameworks: the doctrine of just war. The 43,000-word document, titled *Magnifica Humanitas* ("Magnificent Humanity"), declared the theory "outdated" and argued that humanity now has better tools — dialogue, diplomacy, forgiveness — for resolving conflicts.

"The 'just war' theory which has all too often been used to justify any kind of war, is now outdated," Leo wrote. The timing was not accidental. The encyclical landed during Eid al-Adha, with U.S. and Iranian forces trading air strikes over the Strait of Hormuz, Israel declaring southern Lebanon a combat zone, and Vice President JD Vance publicly invoking just war theory to defend American military operations.

## More Than a Peace Document

But *Magnifica Humanitas* is about far more than pacifism. The pope used the document to stake out the Vatican's position on artificial intelligence — calling for global regulation of AI systems and warning against what he called the "algorithmic concentration of power." Leo argued that AI development without ethical guardrails risks creating new forms of exploitation and dehumanization.

The document drew parallels between the colonial era and the current technology landscape, warning that data concentration and algorithmic control could produce a new kind of digital colonialism. "The temptation to build a future that excludes God," Leo wrote, echoing the biblical story of the Tower of Babel, must be resisted.

The encyclical also contained the Catholic Church's clearest apology yet for its historic role in supporting transatlantic slavery — a statement that resonated across the Global South, including India, where the Portuguese colonial church's role in Goa and along the western coast remains a living memory.

## Why India Should Pay Attention

India's 19 million Catholics — concentrated in Goa, Kerala, Tamil Nadu, and the Northeast — make it one of Asia's largest Catholic populations. The encyclical's slavery apology carries particular weight in communities that trace their faith to Portuguese colonial-era conversions, many of which were coerced.

But it is the AI regulation language that may have the most practical impact. India's technology sector — now a $250 billion industry powering global capability centers for every major Western corporation — sits squarely in the crosshairs of any global AI regulatory framework. Pope Leo's call for algorithmic transparency and data governance aligns with debates already underway in Delhi about India's own AI governance policy.

For the Indian diaspora in Silicon Valley, Hyderabad's tech corridors, and Bengaluru's startup ecosystem, the encyclical raises questions that transcend theology: Who governs the algorithms? Who owns the data? And who is accountable when AI systems make decisions that affect millions of lives?

## The Pushback Has Already Started

Not everyone welcomed the encyclical. Anglican theologians pushed back on the just war repudiation, arguing that the doctrine — when properly applied — serves as a restraint on war rather than a permission slip. Vice President Vance, a Catholic convert, has been notably silent on the document.

Conservative Catholic media in the United States framed the encyclical as naive, particularly given the ongoing Iran conflict. But peace activists and interfaith groups hailed it as the most significant papal statement on war since the Second Vatican Council.

## The Bigger Picture

Leo XIV — the first American-born pope, born Robert Francis Prevost — appears to be signaling that his papacy will not shy away from the era's most contentious questions. In a single document, he took positions on war, technology, colonialism, and institutional accountability that will shape Catholic social teaching for a generation.

For India's Catholics, its tech workers, and its diaspora, the message is clear: the Church is watching the same future they are building.

*Sources: Reuters, Religion News Service, Le Monde, NCR Online, North Jersey Media, Barron's (via George Conger/Substack)*"""

    # Image: Pope Leo XIV
    print("  Sourcing image...")
    image_url = fetch_wikipedia_person_image("Pope Leo XIV")
    if not image_url:
        image_url = fetch_wikipedia_person_image("Robert Francis Prevost")
    image_caption = "Pope Leo XIV's first encyclical takes on war, AI, and slavery in a single sweeping document"
    image_attribution = "Wikimedia Commons"

    if not validate_image_url(image_url):
        # Fallback to Pexels
        image_url = fetch_pexels_image("Vatican St Peter Basilica", "Catholic church Rome")
        image_attribution = "Pexels"
        if not validate_image_url(image_url):
            image_url = None
            image_caption = None
            image_attribution = None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "slug": slug,
        "body": body,
        "category": "news",
        "vertical": "news",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": image_url,
        "image_caption": image_caption,
        "image_attribution": image_attribution,
        "sources": json.dumps([
            "Reuters",
            "Religion News Service",
            "Le Monde",
            "NCR Online",
            "North Jersey Media",
            "Medium (Pope Leo analysis)"
        ])
    }
    article = {k: v for k, v in article.items() if v is not None}
    return publish_article(article)


# ═══════════════════════════════════════════════════
# ARTICLE 3: US Inflation PCE at 3.8%
# ═══════════════════════════════════════════════════

def write_article_3():
    print("\n📝 Article 3: US Inflation PCE at 3.8%")

    headline = "U.S. Inflation Just Hit 3.8 Percent. The Iran War Is Baked Into Every Price Tag in America."
    subheadline = "The Fed's preferred inflation gauge rose to its highest level since May 2023, driven by energy costs from the Iran conflict. Rate hikes are back on the table — and that changes everything for Indian American homebuyers and H-1B workers."
    slug = "us-pce-inflation-3-8-percent-iran-war-fed-rate-hike-indian-americans-20260528"

    body = """The number the Federal Reserve watches most closely just confirmed what every American already feels at the gas pump: the Iran war is making everything more expensive.

The Bureau of Economic Analysis reported Thursday that the Personal Consumption Expenditures price index — the Fed's preferred inflation gauge — rose 3.8 percent in the 12 months through April, up from 3.5 percent in March. It is the largest annual increase since May 2023 and the sharpest acceleration since the Iran conflict began disrupting global energy markets in late February.

Core PCE, which strips out volatile food and energy prices, came in at 3.3 percent year-over-year — the highest since November 2023. Monthly core growth eased slightly to 0.2 percent from 0.3 percent, offering a faint silver lining that was immediately overwhelmed by the headline numbers.

## The Iran Premium

The math is straightforward. Crude oil prices have remained elevated since the Strait of Hormuz was effectively closed to commercial traffic in March, cutting off roughly 20 percent of global oil supply. Gasoline prices have driven the bulk of the PCE acceleration, but the ripple effects extend far beyond the pump: jet fuel costs have forced airlines to cut domestic flights, food logistics chains are passing through higher transport costs, and everything from plastics to pharmaceuticals has gotten more expensive.

"The headline PCE is well above the Fed's 2 percent inflation target, and it should justify a shift in the Fed's stance from dovish to neutral or hawkish," said Kathleen Brooks, research director at XTB.

Markets are now pricing in a roughly 50 percent chance of a 25-basis-point rate hike by the end of 2026 — a dramatic reversal from the rate-cutting expectations that dominated early this year.

## What This Means for Indian Americans

For Indian Americans — the fastest-growing homebuyer group in the United States, according to National Association of Realtors data — the inflation report lands like a second punch after mortgage rates hit a nine-month high earlier this week.

Higher inflation means higher rates for longer. Higher rates mean more expensive mortgages, car loans, and student debt. For dual-income households where one or both earners are on H-1B visas, the financial squeeze is compounded by immigration uncertainty: it is harder to make a 30-year mortgage commitment when your right to remain in the country depends on employer sponsorship.

Remittances are also affected. A stronger dollar — which typically accompanies rate hike expectations — makes transfers to India slightly more efficient in rupee terms, but the underlying squeeze on disposable income means there is less to send. India received $136 billion in remittances in fiscal year 2025, with the U.S. diaspora contributing a significant share.

## The Fed's Dilemma

The Federal Reserve now faces an uncomfortable choice. Inflation is accelerating, but the economy is showing signs of stress: consumer confidence is weakening, travel spending is splitting along income lines, and Obamacare enrollment is dropping as premium subsidies expire. Raising rates would fight inflation but risk tipping vulnerable households into genuine financial hardship.

The next Fed meeting in June will be watched closely. Chair Jerome Powell has been careful to describe the Iran-driven price increases as "supply-side" rather than demand-driven, leaving room to hold rates steady. But with headline PCE nearly double the 2 percent target and rising, the political and market pressure to act is mounting.

## The Bigger Picture

For the Indian diaspora, the inflation data is one more data point in a year that has reshaped the economics of living in America. Higher grocery bills, more expensive flights to India, rising insurance premiums, and a housing market that keeps moving further out of reach — all of it traces back, directly or indirectly, to a conflict 7,000 miles away that has rewritten the global energy map.

The PCE report is a number. But it measures something real: the cost of daily life in America is going up, and the people who came here to build a better future are feeling it as much as anyone.

*Sources: Bureau of Economic Analysis, MarketWatch, Barron's, Stifel Economics, FXStreet, Reuters, National Association of Realtors*"""

    # Image: Pexels for inflation/economy
    print("  Sourcing image...")
    image_url = fetch_pexels_image("US dollar bills inflation economy", "gasoline prices fuel pump")
    image_caption = "U.S. inflation hit 3.8 percent in April as the Iran war drives energy costs higher across the economy"
    image_attribution = "Pexels"

    if not validate_image_url(image_url):
        image_url = None
        image_caption = None
        image_attribution = None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "slug": slug,
        "body": body,
        "category": "news",
        "vertical": "news",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": image_url,
        "image_caption": image_caption,
        "image_attribution": image_attribution,
        "sources": json.dumps([
            "Bureau of Economic Analysis",
            "MarketWatch",
            "Barron's",
            "Stifel Economics",
            "FXStreet",
            "Reuters"
        ])
    }
    article = {k: v for k, v in article.items() if v is not None}
    return publish_article(article)


# ═══════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("The Videshi — News Writer")
    print(f"Run: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)

    results = []
    results.append(("H-1B Green Card Crisis", write_article_1()))
    results.append(("Pope Leo Encyclical", write_article_2()))
    results.append(("US Inflation PCE 3.8%", write_article_3()))

    print("\n" + "=" * 60)
    print("RESULTS:")
    for name, ok in results:
        print(f"  {'✓' if ok else '✗'} {name}")
    print("=" * 60)

    successes = sum(1 for _, ok in results if ok)
    print(f"\n{successes}/{len(results)} articles published successfully.")
