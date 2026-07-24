#!/usr/bin/env python3
"""
The Videshi — Lifestyle-Health & Markets-Finance Writer
Run: 2026-06-04 evening batch
Articles:
  1. Exercise Intensity + Mental Health (lifestyle-health)
  2. India-US Trade Deal 99% Done (markets-finance)
  3. Manufactured Gut Bacteria Breakthrough (lifestyle-health)
"""

import json, os, sys, time, uuid, re
import requests
from datetime import datetime, timezone

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, val = line.split('=', 1)
                    key = key.replace('export ', '').strip()
                    val = val.strip().strip('"').strip("'")
                    os.environ[key] = val

load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

UA = 'TheVideshi/1.0 (thevideshi.com)'


def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia."""
    encoded = person_name.replace(' ', '_')
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
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia error for '{person_name}': {e}")
    return None


def fetch_wikimedia_commons(query, limit=5):
    """Search Wikimedia Commons for CC images."""
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params={
                "action": "query",
                "generator": "search",
                "gsrsearch": query,
                "gsrnamespace": "6",
                "gsrlimit": str(limit),
                "prop": "imageinfo",
                "iiprop": "url|size|mime",
                "iiurlwidth": "1200",
                "format": "json"
            },
            headers={"User-Agent": UA},
            timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                info = page.get("imageinfo", [{}])[0]
                url = info.get("thumburl") or info.get("url")
                mime = info.get("mime", "")
                width = info.get("width", 0)
                if url and "image" in mime and width > 200:
                    results.append({"url": url, "title": page.get("title", ""), "width": width})
            if results:
                print(f"  ✓ Commons found {len(results)} images for '{query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Commons error for '{query}': {e}")
    return []


def fetch_pexels(query, per_page=5):
    """Search Pexels for stock photos using requests (not urllib)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels key")
        return []
    try:
        r = requests.get(
            "https://api.pexels.com/v1/search",
            params={"query": query, "per_page": per_page, "orientation": "landscape"},
            headers={"Authorization": PEXELS_KEY},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            photos = data.get("photos", [])
            results = [{"url": p["src"]["large2x"], "alt": p.get("alt", "")} for p in photos if p.get("src", {}).get("large2x")]
            if results:
                print(f"  ✓ Pexels found {len(results)} images for '{query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Pexels error for '{query}': {e}")
    return []


def validate_image(url):
    """Check that a URL returns a valid image > 5KB."""
    try:
        r = requests.head(url, timeout=10, allow_redirects=True, headers={"User-Agent": UA})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if "image" in ct and cl > 5000:
            print(f"  ✓ Image valid: {cl} bytes, {ct}")
            return True
        # try GET if HEAD didn't return content-length
        if "image" in ct and cl == 0:
            r2 = requests.get(url, timeout=10, stream=True, headers={"User-Agent": UA})
            chunk = r2.raw.read(10000)
            r2.close()
            if len(chunk) > 5000:
                print(f"  ✓ Image valid (via GET): {len(chunk)}+ bytes")
                return True
        print(f"  ✗ Image invalid: {cl} bytes, {ct}")
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
    return False


def insert_article(article):
    """Insert an article into Supabase."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=15
    )
    if r.status_code in (200, 201):
        result = r.json()
        aid = result[0].get('id', 'unknown') if isinstance(result, list) else result.get('id', 'unknown')
        print(f"  ✓ Inserted: {aid} — {article['headline'][:60]}...")
        return True
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:200]}")
        return False


# ─── ARTICLE 1: Exercise Intensity + Mental Health ──────────────────────────

def write_article_1():
    print("\n═══ ARTICLE 1: Exercise Intensity & Mental Health ═══")

    slug = "exercise-intensity-mental-health-depression-anxiety-midlife-south-asian-diaspora-20260604"
    headline = "Swapping 30 Minutes of Sitting for a Brisk Walk Cuts Depression by 9 Per Cent. For Desk-Bound NRIs, the Maths Is Simple."
    subheadline = "A new study in Depression and Anxiety finds that exercise intensity, not just movement, is the key to mental health at midlife. South Asians in sedentary tech jobs should take note."

    # Source image
    print("Sourcing image...")
    # Try Commons first - exercise, mental health
    commons = fetch_wikimedia_commons("brisk walking exercise park")
    pexels = fetch_pexels("person walking brisk exercise outdoors")

    image_url = None
    image_caption = None
    image_attribution = None

    # Check commons first
    for img in commons:
        if validate_image(img["url"]):
            image_url = img["url"]
            image_caption = "People exercising outdoors in a park setting"
            image_attribution = "Wikimedia Commons"
            break

    # Fallback to Pexels
    if not image_url:
        for img in pexels:
            if validate_image(img["url"]):
                image_url = img["url"]
                image_caption = "A person walking briskly outdoors for exercise"
                image_attribution = "Pexels"
                break

    if not image_url:
        print("  ⚠ No valid image found, skipping article")
        return False

    body = """A growing body of research has urged people to simply move more. Stand up from your desk. Take the stairs. Walk to the break room instead of emailing. But a new study published in *Depression and Anxiety* suggests that when it comes to your mental health, the kind of movement matters far more than the act of moving itself.

Researchers tracked the daily activity patterns of midlife adults — their exercise, their sleep, their hours of sitting — and modelled what would happen if participants swapped just 30 minutes of sedentary time for moderate-to-vigorous physical activity. The results were striking. Depressive symptoms dropped by roughly 9 per cent. Anxiety symptoms fell by about 5 per cent. No therapy. No medication. Just a half-hour of effort that gets the heart rate up and leaves you slightly breathless.

## Not All Movement Is Created Equal

The study drew a sharp line between light activity and exercise with genuine intensity. Replacing sitting with a gentle stroll offered marginal improvements. But replacing it with brisk walking, cycling, swimming, or a proper gym session delivered meaningfully larger reductions in both depression and anxiety. The implication is clear: intensity is doing the heavy lifting.

This distinction matters for the South Asian diaspora, a community that has undergone one of the most dramatic lifestyle shifts in a single generation. In India, daily life involved walking to the market, climbing stairs in buildings without lifts, and commuting on foot to bus stops and train stations. In the United States, Canada, and the United Kingdom, that same population now drives to work, sits at a desk for eight to ten hours, drives home, and watches television. The physical activity that was once baked into the day has evaporated.

The result is a community with some of the highest rates of metabolic disease and cardiovascular risk in the West — and, increasingly, a mental health burden that is poorly understood and rarely discussed.

## Sleep Is the Other Half of the Equation

The study also flagged a critical trade-off that too many people get wrong. Participants who slept an average of seven and a half hours a night showed better mental health outcomes. Even modest reductions in sleep — losing just five to thirty minutes per night — were associated with higher levels of both depression and anxiety.

This is a trap that the diaspora falls into with particular frequency. The impulse to wake up earlier for a 5 AM workout, a common recommendation in wellness circles, can backfire if it comes at the expense of sleep. The research suggests that the goal is not to exercise more at any cost, but to exercise more within a 24-hour budget that preserves adequate rest.

For NRIs working in demanding roles across technology, medicine, and finance, this framing is essential. The hours are long. The pressure is real. Cutting sleep to fit in a workout is not a net positive if the sleep loss is quietly eroding mental resilience.

## The Diaspora Mental Health Gap

Mental health remains one of the least addressed dimensions of South Asian health in the West. Cultural stigma, language barriers, and a historic under-representation in clinical research have left the community without the tailored guidance it needs. Depression and anxiety are frequently dismissed as personal weakness rather than clinical conditions, particularly among first-generation immigrants who were raised in environments where such conversations rarely happened.

Exercise offers something that traditional interventions do not: a starting point that requires no clinical diagnosis, no prescription, no waiting list, and no cultural negotiation. A 30-minute run, a cycling session, or even a vigorous game of badminton — a sport that is culturally familiar and widely played in diaspora communities — can begin to close the gap.

## What This Means in Practice

The prescription from this research is specific and achievable. Replace 30 minutes of sitting with moderate-to-vigorous exercise. Protect your sleep. Do not sacrifice one for the other.

For a community that is disproportionately affected by diabetes, heart disease, and now a growing burden of depression and anxiety, these findings are not abstract. They are a daily decision. And the data says that decision is worth making.

**Sources:**
1. Study published in *Depression and Anxiety* (2026), examining associations between physical activity intensity, sedentary behaviour, sleep duration, and mental health outcomes in midlife adults.
2. Medical Dialogues — "Exercise and Adequate Sleep Linked to Better Midlife Mental Health: Study" (June 2026)."""

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "slug": slug,
        "body": body,
        "category": "lifestyle-health",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": image_url,
        "image_caption": image_caption,
        "image_attribution": image_attribution,
        "vertical": "culture",
        "is_editorial": False,
        "sources": json.dumps([
            {"name": "Depression and Anxiety (journal)", "url": "https://onlinelibrary.wiley.com/journal/15206394"},
            {"name": "Medical Dialogues", "url": "https://medicaldialogues.in"}
        ])
    }

    return insert_article(article)


# ─── ARTICLE 2: India-US Trade Deal 99% Done ──────────────────────────

def write_article_2():
    print("\n═══ ARTICLE 2: India-US Trade Deal 99% Done ═══")

    slug = "india-us-trade-deal-99-percent-done-bilateral-agreement-nri-tariffs-20260604"
    headline = "India and the US Are '99 Per Cent' Done on a Trade Deal. Here Is What It Means for Every NRI."
    subheadline = "US Ambassador Sergio Gor says the bilateral trade agreement is imminent. Tariffs on Indian goods could drop from 50 to 18 per cent. For NRIs sending money, investing, or running businesses across both countries, the stakes are enormous."

    # Source image
    print("Sourcing image...")
    # Try Wikipedia for Sergio Gor
    wiki_img = fetch_wikipedia_person_image("Sergio Gor")
    commons = fetch_wikimedia_commons("India United States trade agreement")
    pexels = fetch_pexels("India US trade business handshake")

    image_url = None
    image_caption = None
    image_attribution = None

    # Try commons for trade imagery
    for img in commons:
        if validate_image(img["url"]):
            image_url = img["url"]
            image_caption = "India and the United States flags representing bilateral trade negotiations"
            image_attribution = "Wikimedia Commons"
            break

    # Try Pexels
    if not image_url:
        for img in pexels:
            if validate_image(img["url"]):
                image_url = img["url"]
                image_caption = "India-US bilateral trade negotiations approach their final stages"
                image_attribution = "Pexels"
                break

    # Try Wikipedia for Modi-Trump meeting
    if not image_url:
        commons2 = fetch_wikimedia_commons("Modi Trump bilateral meeting")
        for img in commons2:
            if validate_image(img["url"]):
                image_url = img["url"]
                image_caption = "Prime Minister Modi and President Trump during bilateral talks"
                image_attribution = "Wikimedia Commons"
                break

    if not image_url:
        print("  ⚠ No valid image found, skipping article")
        return False

    body = """The India-US trade relationship, which has been the subject of tariff battles, retaliatory levies, and tense back-channel negotiations for over a year, appears to be approaching its conclusion. US Ambassador to India Sergio Gor declared this week that the bilateral trade agreement is "99 per cent there," with the final one per cent consisting of technical legal language and implementation timelines.

The statement, made at the sidelines of CITI's 2026 India Conference in Mumbai, was followed by confirmation from the Ministry of Commerce and Industry that a US delegation led by Chief Negotiator Brendan Lynch visited New Delhi from June 1 to 4 to finalise details of the proposed Interim Agreement under the broader Bilateral Trade Agreement framework.

For the roughly 4.4 million Indian-origin residents in the United States — and the millions more with financial, familial, and business ties across both countries — this is not a diplomatic abstraction. It is a deal that could reshape the cost of goods, the flow of investments, and the terms under which NRI capital moves between the two largest democracies in the world.

## What the Deal Contains

The Interim Agreement framework, first announced in a joint statement on February 7, 2026, is structured around reciprocal market access. Under the current tariff regime, Indian goods entering the United States face a combined duty of roughly 50 per cent — a 25 per cent reciprocal tariff and an additional 25 per cent levy linked to India's purchases of Russian crude oil.

If the deal proceeds as outlined by Commerce Minister Piyush Goyal, that tariff burden would drop to 18 per cent through a US executive order, potentially issued within days of the formal signing. In return, India has proposed eliminating or reducing tariffs on a wide range of US industrial goods and agricultural products, including dried distillers' grains, red sorghum, tree nuts, fresh and processed fruit, soybean oil, wine, and spirits.

The broader Bilateral Trade Agreement is expected to cover market access, non-tariff barriers, customs and trade facilitation, investment promotion, and economic security alignment.

## Why NRIs Should Pay Attention

The agreement carries direct implications across several dimensions of NRI life.

**Remittances and the rupee.** India received over $125 billion in remittances in 2025, the largest amount for any country. The rupee, currently under pressure at around 95.75 to the dollar amid the Iran-fuelled oil shock, has weakened 6.5 per cent this year. A ratified trade deal would signal economic stability, attract foreign investment flows, and provide a floor for the currency. For NRIs sending money home, even a modest rupee recovery translates into thousands of dollars in annual savings.

**IT services and H-1B professionals.** While the Interim Agreement focuses on goods, the broader BTA framework explicitly includes services and investment promotion. India's IT services sector, which generated $194 billion in export revenue in FY2025, stands to gain from reduced non-tariff barriers and a more predictable regulatory environment. For the hundreds of thousands of Indian professionals on H-1B visas, a stable trade relationship reduces the political risk of retaliatory visa restrictions.

**Consumer goods and imports.** The deal would make US agricultural products, processed foods, and wines more accessible in India at lower prices. For NRIs who frequently ship goods to family or invest in food and retail businesses in India, reduced tariffs on both sides create new commercial opportunities.

**Indian exports to the US.** Sectors like textiles, pharmaceuticals, gems and jewellery, and auto components — all significant employers in India — would benefit directly from the tariff reduction. A thriving export sector in India means stronger job creation, higher GDP growth, and a more attractive environment for NRI real estate and equity investments.

## The Geopolitical Context

The deal is being negotiated against the backdrop of significant global turbulence. The US-Iran conflict has pushed Brent crude near $96 a barrel, squeezing India's current account and complicating the RBI's inflation calculus. The OECD recently warned of the weakest global growth since 2008. And the US administration, under President Trump, has simultaneously proposed new tariffs of up to 12.5 per cent on 60 economies over forced-labour concerns.

Ambassador Gor dismissed these headwinds, pointing to the "strong and growing relationship" between Trump and Prime Minister Modi as the primary driver of progress. Secretary of State Marco Rubio separately confirmed that the US is "on the verge" of completing the deal.

## What Happens Next

The final one per cent, as Ambassador Gor described it, involves resolving technical legal phrasing and settling implementation timelines. The formal agreement is expected to be signed within weeks, with the reduced tariff rate activated through a US executive order shortly after.

For NRI investors, business owners, and families with a foot in both economies, this is a deal worth tracking closely. Bilateral trade between India and the US has already grown from $20 billion to over $220 billion in two decades. A formal trade agreement would be the first in the history of the relationship — and its effects will be felt in bank accounts, investment portfolios, and grocery stores on both sides of the Pacific.

**Sources:**
1. The Indian EYE — "Last 1% being finalized: Gor on India-US trade agreement" (June 2026)
2. Reuters — "Indian shares muted ahead of crucial RBI policy decision" (June 4, 2026)
3. Ministry of Commerce and Industry, Government of India — Official statement on US trade delegation visit, June 1-4, 2026"""

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "slug": slug,
        "body": body,
        "category": "markets-finance",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": image_url,
        "image_caption": image_caption,
        "image_attribution": image_attribution,
        "vertical": "economy",
        "is_editorial": False,
        "sources": json.dumps([
            {"name": "The Indian EYE", "url": "https://theindianeye.com"},
            {"name": "Reuters", "url": "https://reuters.com"},
            {"name": "Ministry of Commerce and Industry, India", "url": "https://commerce.gov.in"}
        ])
    }

    return insert_article(article)


# ─── ARTICLE 3: Manufactured Gut Bacteria Breakthrough ──────────────────────

def write_article_3():
    print("\n═══ ARTICLE 3: Manufactured Gut Bacteria — Mount Sinai ═══")

    slug = "mount-sinai-manufactured-gut-bacteria-live-biotherapeutic-c-diff-nature-medicine-20260604"
    headline = "Scientists Built a Factory for Gut Bacteria. It Could Replace the Most Unpleasant Treatment in Medicine."
    subheadline = "A Mount Sinai team has developed a manufacturing platform for targeted mixtures of beneficial gut bacteria, offering a standardised alternative to faecal transplants. For South Asians with elevated antibiotic use, the implications are personal."

    # Source image
    print("Sourcing image...")
    commons = fetch_wikimedia_commons("gut bacteria microbiome microscope")
    pexels = fetch_pexels("gut microbiome bacteria science")

    image_url = None
    image_caption = None
    image_attribution = None

    for img in commons:
        if validate_image(img["url"]):
            image_url = img["url"]
            image_caption = "Microscopic view of gut bacteria, the focus of a new manufacturing breakthrough"
            image_attribution = "Wikimedia Commons"
            break

    if not image_url:
        for img in pexels:
            if validate_image(img["url"]):
                image_url = img["url"]
                image_caption = "A laboratory setting where scientists study gut microbiome composition"
                image_attribution = "Pexels"
                break

    if not image_url:
        print("  ⚠ No valid image found, skipping article")
        return False

    body = """Faecal microbiota transplant is one of medicine's most effective and least appealing treatments. The procedure — which involves transferring stool from a healthy donor into the gut of a patient with a dangerous bacterial infection — works remarkably well. It has saved thousands of lives. But it is also messy, difficult to standardise, dependent on donor availability, and carries inherent risks of transmitting unknown pathogens.

A team at the Icahn School of Medicine at Mount Sinai has now published results that could make the procedure obsolete. In a study published on June 2 in *Nature Medicine*, researchers described a cost-effective manufacturing platform capable of producing targeted mixtures of known beneficial gut bacteria — a live biotherapeutic product, or LBP — that can be given to patients instead of whole-stool material.

## How It Works

The platform isolates specific bacterial strains from healthy donor stool, cultures them in controlled conditions, and assembles them into a defined, reproducible product. Unlike traditional faecal transplants, where the exact composition of the transferred material is unknown and varies from donor to donor, the manufactured product contains identified strains in controlled quantities.

In a head-to-head phase 1b clinical trial, the team compared their manufactured LBP with conventional faecal microbiota transplant prepared from the same donor source. The study enrolled 18 participants with recurrent *Clostridioides difficile* infection across four treatment groups — low- and high-dose FMT and low- and high-dose LBP.

The results demonstrated that the manufactured product was comparable to the traditional transplant in restoring healthy gut flora and preventing recurrence of the infection, while offering the advantages of standardisation, scalability, and quality control.

## Why C. difficile Matters

*C. difficile* infection is a serious and often debilitating condition that typically follows antibiotic treatment. Antibiotics, while killing the targeted pathogen, also wipe out large populations of beneficial gut bacteria. In the absence of these protective microbes, *C. difficile* — a toxin-producing bacterium that is notoriously resistant to many drugs — can proliferate unchecked, causing severe diarrhoea, colitis, and in extreme cases, death.

Recurrent infections are the real problem. Up to 25 per cent of patients experience a recurrence after their first episode, and the risk climbs with each subsequent round. For these patients, faecal transplant has been the most reliable intervention, but access has been uneven, particularly in countries with underdeveloped donor screening infrastructure.

## The South Asian Angle

This matters more to the South Asian diaspora than most communities realise. Antibiotic overuse is a well-documented crisis across South Asia, where antimicrobial drugs are frequently available over the counter and prescribed with minimal oversight. First-generation immigrants who grew up in India, Pakistan, Bangladesh, or Sri Lanka often carry a history of high antibiotic exposure, which shapes their gut microbiome profile long after they have settled abroad.

Studies have shown that South Asian populations in the West carry distinct gut microbiome signatures compared to other ethnic groups, influenced by diet, early-life antibiotic exposure, and genetic factors. A disrupted microbiome increases vulnerability not only to *C. difficile* but also to a range of metabolic conditions, including type 2 diabetes, obesity, and inflammatory bowel disease — all of which affect South Asians at disproportionately high rates.

A standardised, scalable microbiome therapy addresses a need that is both clinical and cultural. For a community that often hesitates to discuss gut health openly and is underserved by a Western medical system that does not always account for the unique microbiome profiles shaped by South Asian diets and histories, a manufactured alternative to faecal transplant removes both a logistical and a psychological barrier.

## The Bigger Picture

The Mount Sinai platform is not just a solution for *C. difficile*. The ability to manufacture defined mixtures of gut bacteria opens the door to treatments for a range of conditions linked to microbiome disruption, from inflammatory bowel disease to metabolic syndrome. The technology is designed to be cost-effective and scalable, meaning it could eventually be deployed in resource-limited settings where donor-based faecal transplants are impractical.

For now, the immediate impact is on patients with recurrent *C. difficile* — a population that includes a disproportionate number of elderly, immunocompromised, and antibiotic-exposed individuals. The promise, though, extends much further. If gut bacteria can be manufactured like any other pharmaceutical product, the era of personalised microbiome therapy is no longer theoretical.

**Sources:**
1. Icahn School of Medicine at Mount Sinai — Study published in *Nature Medicine* (June 2, 2026), doi: 10.1038/s41591-026-04442-2
2. News-Medical.net — "New manufacturing platform produces targeted mixtures of beneficial gut bacteria" (June 2026)"""

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "slug": slug,
        "body": body,
        "category": "lifestyle-health",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": image_url,
        "image_caption": image_caption,
        "image_attribution": image_attribution,
        "vertical": "culture",
        "is_editorial": False,
        "sources": json.dumps([
            {"name": "Nature Medicine", "url": "https://nature.com/nm"},
            {"name": "News-Medical.net", "url": "https://news-medical.net"}
        ])
    }

    return insert_article(article)


# ─── MAIN ───────────────────────────────────────────────────────────────────

def main():
    print("The Videshi — Lifestyle/Markets Writer")
    print(f"Run time: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)

    results = []
    results.append(("Exercise Intensity & Mental Health", write_article_1()))
    results.append(("India-US Trade Deal", write_article_2()))
    results.append(("Manufactured Gut Bacteria", write_article_3()))

    print("\n" + "=" * 60)
    print("SUMMARY:")
    for name, success in results:
        status = "✓ Published" if success else "✗ Failed"
        print(f"  {status}: {name}")
    
    successes = sum(1 for _, s in results if s)
    print(f"\n{successes}/{len(results)} articles published")


if __name__ == "__main__":
    main()
