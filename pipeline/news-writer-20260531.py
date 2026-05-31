#!/usr/bin/env python3
"""
The Videshi — News Writer (2026-05-31 batch)
Writes 3 articles: dabbawalas, Myanmar visit, RBI MPC
"""

import os, sys, json, uuid, requests, urllib.parse, re
from datetime import datetime, timezone

# ── Supabase config ──────────────────────────────────────────────────────────
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ── Pexels config ─────────────────────────────────────────────────────────────
PEXELS_KEY = None
pexels_env = os.path.expanduser("~/workspace/.env.pexels")
if os.path.exists(pexels_env):
    for line in open(pexels_env):
        if line.startswith("PEXELS_API_KEY="):
            PEXELS_KEY = line.strip().split("=", 1)[1].strip().strip('"').strip("'")

# ── Image helpers ─────────────────────────────────────────────────────────────

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    import time
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            # Prefer thumbnail (330px, always works) over originalimage (may get 429 on large files)
            img = data.get("thumbnail", {}).get("source") or data.get("originalimage", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                time.sleep(1)  # rate limit courtesy
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None


def fetch_pexels_image(query, fallback_query=None):
    """Fetch a relevant image from Pexels API using requests."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key available")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            r = requests.get(
                "https://api.pexels.com/v1/search",
                params={"query": q, "per_page": 5, "orientation": "landscape"},
                headers={"Authorization": PEXELS_KEY},
                timeout=10
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


def upload_image_to_supabase(image_url, filename):
    """Download image and upload to Supabase storage bucket 'article-images'."""
    try:
        r = requests.get(image_url, timeout=15, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        if r.status_code != 200:
            print(f"  ⚠ Image download failed ({r.status_code}): {image_url[:80]}")
            return image_url  # fall back to direct URL if it's a permanent source
        content_type = r.headers.get("Content-Type", "image/jpeg")
        if not content_type.startswith("image/"):
            print(f"  ⚠ Not an image: {content_type}")
            return image_url
        if len(r.content) < 5000:
            print(f"  ⚠ Image too small ({len(r.content)} bytes), skipping upload")
            return image_url

        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        up = requests.post(
            upload_url,
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": content_type,
                "x-upsert": "true",
            },
            data=r.content,
            timeout=20
        )
        if up.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Supabase upload failed ({up.status_code}): {up.text[:200]}")
            return image_url
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
        return image_url


def validate_image_url(url):
    """Validate that an image URL returns 200, is an image, and > 5KB."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # HEAD sometimes doesn't return Content-Length; try GET
        if r.status_code == 200 and "image" in ct:
            r2 = requests.get(url, timeout=10, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, stream=True)
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                return True
    except:
        pass
    return False


# ── Supabase helpers ──────────────────────────────────────────────────────────

def sb_insert(table, data):
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers=HEADERS,
        json=data,
        timeout=15,
    )
    if r.status_code in (200, 201):
        rows = r.json()
        if rows and isinstance(rows, list):
            return rows[0]
    print(f"  ⚠ Insert to {table} failed ({r.status_code}): {r.text[:300]}")
    return None


def sb_patch(table, match, data):
    params = "&".join(f"{k}={v}" for k, v in match.items())
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/{table}?{params}",
        headers=HEADERS,
        json=data,
        timeout=15,
    )
    if r.status_code in (200, 204):
        return True
    print(f"  ⚠ Patch {table} failed ({r.status_code}): {r.text[:300]}")
    return False


# ── Articles ──────────────────────────────────────────────────────────────────

ARTICLES = [
    {
        "headline": "Mumbai's Dabbawalas Fed the City for 130 Years. Now Only 1,500 Are Left.",
        "subheadline": "Remote work, app-based delivery, and rising costs are dismantling a logistics system that Harvard studied and Prince Charles admired.",
        "slug": "mumbai-dabbawalas-disappearing-1500-left-remote-work-app-delivery-bbc-20260531",
        "category": "news",
        "tags": ["mumbai", "dabbawalas", "culture", "remote-work", "food-delivery"],
        "sources_list": ["BBC Marathi", "Mumbai Tiffin Box Suppliers Association", "New York Post"],
        "person_image": None,  # no single person
        "pexels_query": "Mumbai train station commuters",
        "pexels_fallback": "Indian lunchbox tiffin",
        "image_attribution": "Pexels",
        "body": """Every morning before Mumbai wakes up, men in white caps arrive at suburban railway stations on bicycles stacked with lunchboxes. They load the boxes onto trains, cross the city, and deliver hot, home-cooked meals to office workers. After lunch, they collect the empty boxes and return them by mid-afternoon.

These men are called dabbawalas, and for more than 130 years, they have kept Mumbai fed through a delivery system so precise it became world famous. Harvard Business School studied it as a masterclass in low-cost logistics. In 2003, the future King Charles spent time with dabbawalas during a visit to Mumbai. At its peak, roughly 4,500 registered dabbawalas moved 50,000 lunchboxes a day across India's financial capital — with no apps, no GPS, and an error rate of one in six million deliveries.

Now, according to the Mumbai Tiffin Box Suppliers Association, that number has fallen to about 1,500. The decline started during the pandemic, when offices closed and the daily lunch run simply stopped making sense. Even after offices reopened, hybrid schedules meant many workers go in only two or three days a week — not enough to justify a daily subscription. App-based food delivery services like Swiggy and Zomato, along with cloud kitchens offering cheap meals near office buildings, have given workers alternatives that require no advance planning.

**A system built for a city that no longer exists**

The dabbawala system was designed for a specific version of Mumbai: one where workers commuted to the same office every day, where home-cooked food was both a cultural expectation and an economic necessity, and where the suburban railway network was the circulatory system of the city's working life. Each lunchbox carries an alphanumeric code that tells a dabbawala where it came from, where it is going, which floor of which building it belongs to, and how to get it back. No technology — just a system passed down through generations of workers who know Mumbai's trains and streets instinctively.

That Mumbai still exists, but it is shrinking. The workers who remain are older, and younger men from the community are choosing other jobs. Rising transportation costs and stagnant subscription fees have made the economics increasingly difficult. A dabbawala delivering 35 boxes a day earns roughly $240 a month — below India's average monthly wage.

**What NRIs are losing**

For Indians abroad, the dabbawala is more than a delivery service. It is a symbol of a particular kind of Indian ingenuity — the ability to build extraordinarily efficient systems from nothing but human coordination and local knowledge. Many NRIs grew up eating meals that arrived in a dabba, or heard stories from parents and grandparents who did. The system represents a version of Mumbai that many in the diaspora still carry in their heads: a city where home-cooked food arrived hot at your desk every day, where a network of men on bicycles solved a logistics problem that Silicon Valley would later spend billions trying to replicate with algorithms.

Subhash Talekar, the spokesperson for the Mumbai Tiffin Box Suppliers Association, told the BBC that the dabbawalas have tried to adapt. Some have partnered with corporate canteens. Others offer meal plans that accommodate hybrid schedules. A few have experimented with WhatsApp-based ordering. But none of these adaptations have been enough to reverse the fundamental shift in how Mumbai works and eats.

**The bigger picture**

The story of the dabbawalas is ultimately about a city changing faster than the institutions built to serve it. Mumbai's office culture, food habits, and commuting patterns have all shifted, and a system engineered for the old rhythm is losing its place. The question is not whether the dabbawalas will survive — some will — but whether the system that made them extraordinary, the one that moved 50,000 boxes a day with near-perfect accuracy, will ever function at that scale again. The answer, increasingly, is no.""",
    },
    {
        "headline": "Myanmar's Junta Chief Turned President Is in India. He Wants Rare Earths and Legitimacy. Modi Wants to Counter China.",
        "subheadline": "Min Aung Hlaing's five-day trip is his first foreign visit as president. For India, it is a chance to dilute Beijing's outsized influence on its eastern neighbour.",
        "slug": "myanmar-president-min-aung-hlaing-india-visit-modi-china-rare-earths-20260531",
        "category": "news",
        "tags": ["myanmar", "india", "modi", "china", "geopolitics", "rare-earths"],
        "sources_list": ["Reuters", "India Ministry of External Affairs", "Crisis Group"],
        "person_image": "Min Aung Hlaing",
        "pexels_query": None,
        "pexels_fallback": None,
        "image_attribution": "Wikimedia Commons",
        "body": """Myanmar President Min Aung Hlaing arrived in India on Saturday for a five-day official visit that underscores the gradual return of regional re-engagement for a country that has been largely shunned by its neighbours since a military coup in 2021. The former general, who was elected president through a parliamentary vote in April after formalising his grip on power, is scheduled to meet Prime Minister Narendra Modi in New Delhi on June 1.

The visit began in Bodh Gaya, the Buddhist pilgrimage site in Bihar, before moving to the capital for bilateral talks. Min Aung Hlaing will also travel to Mumbai on June 2 for business and industry interactions. He is accompanied by a high-level delegation of cabinet ministers, senior officials, and business leaders.

**What India wants**

For India, the visit is about three things: rare earths, border security, and counterbalancing China. Myanmar sits on significant deposits of critical rare earth minerals that are essential for electronics, defence systems, and clean energy technology. China currently dominates Myanmar's rare earth sector, and India has been looking for ways to secure access to these resources as part of its broader strategy to reduce dependence on Chinese supply chains.

India and Myanmar share a 1,643-kilometre land border across four northeastern states — Arunachal Pradesh, Nagaland, Manipur, and Mizoram. Cross-border insurgent activity and the flow of refugees from Myanmar's civil conflict have been persistent security concerns. New Delhi wants to strengthen border management cooperation and ensure that instability in Myanmar does not spill over into India's northeast.

The third objective is geopolitical. China's influence over Myanmar has grown substantially since the coup, and India's Act East Policy — which positions Myanmar as a key corridor to Southeast Asia — has been stalled. The India-Myanmar-Thailand Trilateral Highway and the Kaladan Multi-Modal Transit Transport Project, both designed to improve connectivity through Myanmar, have faced repeated delays. Reviving these projects is expected to be on the agenda.

**What Myanmar wants**

Min Aung Hlaing is looking for something simpler: legitimacy. Five years after ousting the elected government of Aung San Suu Kyi, he has changed into civilian clothes and is seeking to rebuild diplomatic relationships that collapsed after the coup. India, as a fellow democracy that has maintained cautious engagement with Myanmar throughout, offers a less confrontational re-entry point than Western capitals.

"After changing into civilian clothes as president, Min Aung Hlaing is looking to boost diplomatic engagement across the region," Richard Horsey, senior Myanmar adviser at Crisis Group, told Reuters. "He expects more normal ties with ASEAN. He is also likely to visit Beijing soon to meet Xi Jinping. India is Myanmar's other key neighbour."

The visit was originally planned around the International Big Cat Alliance Summit in India, but when that summit was postponed, it was converted into an official bilateral visit — a signal that both sides considered the trip important enough to proceed regardless.

**The trade picture**

Bilateral trade between India and Myanmar stood at $1.95 billion in 2025-26, covering petroleum products, pharmaceuticals, machinery, and agricultural goods. Both sides are expected to discuss ways to increase this figure, particularly in energy, infrastructure, and manufacturing.

**The diaspora angle**

India is home to a small but significant Myanmar diaspora, concentrated in the northeastern states and in cities like Delhi and Kolkata. Many are refugees from the post-coup conflict, and their status — some documented, many not — is expected to be discussed at least informally during the visit. For the broader Indian diaspora, the visit matters because it shapes the security environment in India's northeast, a region that many NRIs trace their roots to.

Indian foreign ministry spokesman Randhir Jaiswal said on Friday that "all issues that form part of the gamut of relations between Myanmar and India will come up for discussion." The deliberate breadth of that statement suggests both sides want to use this visit to reset the relationship, not just manage it.""",
    },
    {
        "headline": "The RBI Will Decide on Interest Rates This Week. The Rupee, Oil, and a Weak Monsoon Are All Working Against It.",
        "subheadline": "Most economists expect the central bank to hold at 5.25 percent on June 5. But a growing minority thinks it should hike now before the situation gets worse.",
        "slug": "rbi-mpc-june-5-rate-decision-rupee-oil-monsoon-inflation-hold-hike-2026",
        "category": "news",
        "tags": ["rbi", "interest-rates", "rupee", "inflation", "monsoon", "oil", "economy"],
        "sources_list": ["Reuters", "Outlook Money", "Livemint", "Capital Economics"],
        "person_image": "Sanjay Malhotra (banker)",
        "pexels_query": "Reserve Bank of India Mumbai",
        "pexels_fallback": "Indian rupee currency notes",
        "image_attribution": "Wikimedia Commons",
        "body": """The Reserve Bank of India's Monetary Policy Committee will begin a three-day meeting on Tuesday, June 3, with Governor Sanjay Malhotra scheduled to announce the rate decision on Thursday, June 5. The meeting comes at one of the most complicated moments for Indian monetary policy in years, with the central bank caught between still-benign inflation and a constellation of risks that are all pointing in the wrong direction.

According to a Reuters poll of 56 economists conducted between May 22 and 29, nearly 80 percent — 44 of 56 — expect the MPC to keep the repo rate unchanged at 5.25 percent. But the minority calling for a hike has grown sharply: 11 economists now forecast a 25-basis-point increase, and one expects a larger 50-basis-point move. In an April poll, only one respondent had predicted a June rate lift.

**The case for holding**

India's retail inflation stood at 3.48 percent in April, comfortably below the RBI's 4 percent medium-term target and well within its 2-6 percent tolerance band. Headline inflation has been below target for over a year. With the economy facing downside growth risks from the Iran war's impact on trade and energy costs, hiking rates could slow growth without meaningfully addressing supply-side price pressures.

"Interest rates are not a good tool to counter large supply shocks," said Aditya Vyas, chief economist at STCI Primary Dealer. "Also, I do not think the RBI MPC will increase rates to defend the rupee since it is beyond the remit of the MPC."

**The case for hiking**

The problem is that every inflation risk indicator is flashing amber. Crude oil prices remain roughly 30 percent above pre-Iran-war levels. India is the world's third-largest crude oil importer, and elevated energy costs have a direct and rapid transmission mechanism into transport, food, and manufacturing costs. The finance ministry's own monthly report, released Saturday, warned that fuel price hikes and a weaker-than-normal monsoon could push retail inflation higher in the coming months. It called the duration of the Strait of Hormuz disruption "the single most consequential variable" for India's price and external outlook.

The rupee has lost more than 5 percent this year, briefly touching 97 per dollar on May 22 before apparent central bank intervention pulled it back to around 95. Foreign investors have pulled over $24 billion from Indian equities and debt on a net basis between March and May. A weaker rupee makes imports more expensive, creating another channel for inflation to accelerate.

The India Meteorological Department has forecast a below-normal monsoon for 2026, which threatens food production and rural demand. The finance ministry warned that "a significant rainfall deficit coupled with current geopolitical conditions could translate into food inflation, weakening rural demand and aggregate growth."

**What to watch on June 5**

Even if the MPC holds rates — the most likely outcome — the market will be watching the RBI's forward guidance closely. Any shift in the committee's stance from "accommodative" toward "neutral" would signal that rate hikes are coming, possibly as early as August. Standard Chartered has projected a 50-basis-point hike in the current fiscal year, with the first increase possible as early as this month. Capital Economics sees the repo rate reaching 6.00 percent before year-end, contingent on the Iran crisis ending and energy prices dropping.

**What this means for NRIs**

For Indians abroad, the rate decision has direct implications. A weaker rupee reduces the value of remittances sent to India in local purchasing power terms, although it makes those remittances go further when converted. Higher interest rates, if they come, would increase returns on NRI fixed deposits and debt instruments — several banks have already started offering enhanced rates to attract NRI capital. The RBI has been exploring expanding deposit schemes for non-resident Indians and may announce measures to mobilise dollar inflows.

On the investment side, a rate hike would likely weigh on equity markets in the short term, particularly rate-sensitive sectors like banking, real estate, and auto. But it could stabilise the rupee and attract foreign portfolio investment back into Indian debt, which has been under sustained selling pressure.

The decision on June 5 will not just set the interest rate. It will signal whether the RBI believes the current economic headwinds are temporary or structural — and that judgment will shape the investment landscape for the rest of 2026.""",
    },
]

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    published = 0

    for i, art in enumerate(ARTICLES, 1):
        print(f"\n{'='*60}")
        print(f"Article {i}/{len(ARTICLES)}: {art['headline'][:60]}...")
        print(f"{'='*60}")

        # ── Image sourcing ────────────────────────────────────────────
        img_url = None
        attribution = art.get("image_attribution", "The Videshi")

        # Try Wikipedia for person articles
        if art.get("person_image"):
            print(f"  → Trying Wikipedia for '{art['person_image']}'...")
            img_url = fetch_wikipedia_person_image(art["person_image"])
            if img_url:
                attribution = "Wikimedia Commons"

        # Fall back to Pexels
        if not img_url and art.get("pexels_query"):
            print(f"  → Trying Pexels for '{art['pexels_query']}'...")
            img_url = fetch_pexels_image(art["pexels_query"], art.get("pexels_fallback"))
            if img_url:
                attribution = "Pexels"

        # Upload to Supabase for permanence
        final_img_url = None
        if img_url:
            filename = f"{art['slug']}.jpg"
            final_img_url = upload_image_to_supabase(img_url, filename)
            if final_img_url and not validate_image_url(final_img_url):
                print(f"  ⚠ Uploaded image failed validation, trying direct URL...")
                if validate_image_url(img_url):
                    # Check if it's a permanent source
                    if any(d in img_url for d in ["upload.wikimedia.org", "images.pexels.com", "images.unsplash.com"]):
                        final_img_url = img_url
                    else:
                        final_img_url = None
                else:
                    final_img_url = None

        # ── Word count check ──────────────────────────────────────────
        word_count = len(art["body"].split())
        print(f"  Word count: {word_count}")
        if word_count < 400:
            print(f"  ⚠ SKIPPING: Below 400-word minimum")
            continue

        # ── Insert article ────────────────────────────────────────────
        article_id = str(uuid.uuid4())
        row = {
            "id": article_id,
            "headline": art["headline"],
            "subheadline": art["subheadline"],
            "slug": art["slug"],
            "body": art["body"],
            "category": art["category"],
            "vertical": art["category"],
            "status": "published",
            "published_at": now,
            "sources": art["sources_list"],
        "tags": art["tags"],
            "image_url": final_img_url,
            "image_attribution": attribution if final_img_url else None,
        }

        print(f"  → Inserting into p2_articles...")
        result = sb_insert("p2_articles", row)
        if result:
            print(f"  ✓ Published: {art['slug']}")
            published += 1
        else:
            print(f"  ✗ FAILED to publish: {art['slug']}")

    print(f"\n{'='*60}")
    print(f"Done. Published {published}/{len(ARTICLES)} articles.")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
