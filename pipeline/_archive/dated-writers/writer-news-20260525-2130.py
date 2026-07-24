#!/usr/bin/env python3
"""Videshi Writer — 2 fresh NEWS articles for 2026-05-25 21:30 PDT batch
Topics: 1) India fuel price crisis — 4th hike in 10 days, Iran war / Hormuz driving inflation, oil import diversification, rupee at record low, Iran deal hope
        2) Sridhar Vembu (Zoho founder) tells Indians in US to "choose self-respect" and come home after new Green Card rule — backlash and the diaspora identity debate
"""

import json, os, uuid, re, requests, subprocess, urllib.parse
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ── Supabase config ──
env_file = Path.home() / ".env.supabase"
for line in env_file.read_text().strip().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

def sb_post(table, data):
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    r.raise_for_status()
    return r.json()

def sb_get(table, params):
    r = requests.get(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def sb_patch(table, params, data):
    h = {**HEADERS, "Prefer": "return=representation"}
    r = requests.patch(f"{SB_URL}/rest/v1/{table}", headers=h, params=params, json=data, timeout=30)
    r.raise_for_status()
    return r.json()

def make_slug(slug_base, date_suffix="20260525"):
    slug = slug_base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = slug[:70].rstrip('-')
    return f"{slug}-{date_suffix}"

# ── Wikipedia person image (MANDATORY for person articles) ──
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

# ── Pexels helper ──
pexels_env = Path.home() / "workspace" / ".env.pexels"
PEXELS_KEY = None
if pexels_env.exists():
    for line in pexels_env.read_text().strip().splitlines():
        if line.startswith("PEXELS_API_KEY="):
            PEXELS_KEY = line.split("=", 1)[1].strip()

def fetch_pexels_image(query, fallback_query=None):
    if not PEXELS_KEY:
        print("  ⚠ No Pexels key found")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            r = requests.get(
                "https://api.pexels.com/v1/search",
                headers={"Authorization": PEXELS_KEY},
                params={"query": q, "per_page": 5, "orientation": "landscape"},
                timeout=15
            )
            if r.status_code == 200:
                photos = r.json().get("photos", [])
                if photos:
                    url = photos[0]["src"]["large2x"]
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def upload_image_to_supabase(image_url, filename):
    try:
        img_data = requests.get(image_url, timeout=20).content
        content_type = "image/jpeg"
        upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
        h = {
            "apikey": SB_KEY,
            "Authorization": f"Bearer {SB_KEY}",
            "Content-Type": content_type,
            "x-upsert": "true",
        }
        r = requests.post(upload_url, headers=h, data=img_data, timeout=30)
        if r.status_code in (200, 201):
            public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {filename}")
            return public_url
        else:
            print(f"  ⚠ Upload failed ({r.status_code}): {r.text[:200]}")
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return image_url

# ── Duplicate check ──
existing = sb_get("p2_articles", {
    "select": "headline,slug",
    "status": "eq.published",
    "published_at": "gte.2026-05-23T00:00:00Z",
    "order": "published_at.desc",
    "limit": "80"
})
existing_slugs = {a["slug"] for a in existing}
existing_headlines_lower = {a["headline"].lower()[:60] for a in existing}
print(f"Found {len(existing)} recent articles for dedup check")

now = datetime.now(timezone.utc)
now_iso = now.isoformat().replace('+00:00', 'Z')
now_plus1 = (now + timedelta(minutes=1)).isoformat().replace('+00:00', 'Z')

articles = []

# ══════════════════════════════════════════════════════════════
# ARTICLE 1: India's Fuel Price Crisis — Fourth Hike in Ten Days
# ══════════════════════════════════════════════════════════════

slug1 = make_slug("india-fuel-price-crisis-fourth-hike-ten-days-iran-war-hormuz")
headline1_prefix = "india fuel price"
alt_prefix1 = "fourth hike"
if slug1 not in existing_slugs and not any(headline1_prefix in h or alt_prefix1 in h for h in existing_headlines_lower):
    body1 = """Petrol in New Delhi now costs ₹102.12 per litre. In Bengaluru, it has crossed ₹110. In Mumbai, it is ₹111.21.

On Monday, India's state-owned fuel retailers — Indian Oil Corporation, Bharat Petroleum, and Hindustan Petroleum, which together control 90 percent of the market — raised petrol prices by ₹2.61 per litre and diesel by ₹2.71 per litre. It was the fourth increase in ten days. The cumulative hike since May 15 has reached ₹7.50 per litre for petrol and over ₹8 for diesel — increases of 7.8 percent and 8.6 percent, respectively.

The companies had held prices steady for months through state elections. The moment the polls closed, the correction began.

The cause is not domestic. The cause is 7,400 kilometers away, in the Strait of Hormuz.

## The Strait That Controls India's Economy

The Iran war — now three months old — has effectively closed the Strait of Hormuz, the 33-kilometer-wide chokepoint between Iran and Oman through which roughly 20 percent of the world's oil supply passes. Iran mined the strait. The United States blockaded Iranian ports. The result is a supply disruption that has sent crude prices to their highest levels in years and forced every oil-importing nation on Earth to redraw its supply map.

India, the world's third-largest oil importer and consumer, has been hit harder than most.

In April 2026, India imported 4.57 million barrels of oil per day — down 15.5 percent from a year earlier. That is not because India wants less oil. It is because India cannot get enough of the oil it used to buy.

The traditional suppliers — Iraq, Saudi Arabia, the UAE — shipped their crude through the Strait of Hormuz. With the strait effectively closed, India has been forced into an emergency diversification that would have been unimaginable twelve months ago.

## The New Oil Map

Venezuela is now India's third-largest oil supplier. Twelve months ago, Venezuelan crude was a rounding error in India's import ledger. Today, Indian refiners are buying heavy, discounted Venezuelan grades — Merey and Boscan — because they are cheap and because the shipping routes do not pass through the Middle East.

Brazil's share has grown. Angola and Nigeria are back in the mix. Russian crude, which had dominated Indian imports since 2022 after Western sanctions on Moscow, has actually declined — from over 40 percent of India's imports to 35 percent — as some Russian shipments also faced routing challenges.

The UAE and Saudi Arabia have partially recovered by routing exports around the Arabian Peninsula through the Red Sea and the Suez Canal — a longer, more expensive journey that adds $3-5 per barrel in shipping costs.

India's refiners are not choosing these suppliers for quality or price optimization. They are choosing them because they exist outside the blast radius of the Hormuz closure.

## The Rupee

The Indian rupee has been one of the worst-performing Asian currencies in 2026. It has dropped 4.7 percent against the dollar since the Iran war began in late February, hitting a record low of 96.96 last week.

The mechanism is straightforward: India pays for oil in dollars. When oil prices rise, India needs more dollars. When India needs more dollars, the rupee weakens. When the rupee weakens, oil becomes even more expensive in rupee terms. It is a vicious cycle that the Reserve Bank of India has been trying to break by selling dollars from its reserves and floating rate hike scenarios.

Indian banks have asked the RBI for hedging cost subsidies to raise dollar funding — a technical request that translates to a simple message: the financial system is under strain.

For NRIs sending money home, the falling rupee is a mixed signal. One dollar now buys more rupees, which means remittances stretch further. But the purchasing power of those rupees is being eroded by the same inflation that is driving the rupee down. The ₹7.50 increase in petrol prices does not stay at the pump. It ripples through transportation costs, food prices, and every supply chain that depends on diesel — which, in India, is every supply chain.

## The Political Dimension

Rahul Gandhi called the Prime Minister "Inflation Man Modi." The opposition has demanded a rollback. The Congress party pointed out that fuel prices were frozen through state elections and released the moment votes were counted — a pattern that has repeated in every election cycle since 2014.

The government's response has been to frame the hikes as a response to global forces beyond India's control — which is true — while also introducing austerity measures to curb fuel consumption. Modi has called on the nation to reduce unnecessary driving. Zoho founder Sridhar Vembu announced his company would revisit work-from-home policies in part to reduce employee fuel costs.

The austerity measures are not performative. India's oil import bill is a genuine macroeconomic threat. But "drive less" is cold comfort when you are an autorickshaw driver in Bengaluru whose daily fuel cost just increased by 8.6 percent.

## The Iran Deal That Might Fix Everything

On Saturday, President Trump said a deal with Iran has been "largely negotiated." Axios reported a proposed 60-day ceasefire extension during which the Strait of Hormuz would be reopened, Iran would clear its mines, the U.S. would lift its blockade, and Iran would be allowed to sell oil freely.

Oil prices tumbled nearly 7 percent on the news. The rupee rallied to a two-week high of 95.27 per dollar.

A senior Trump administration official told the New York Post that Iran's supreme leader has agreed "in principle" to give up enriched uranium. The Nikkei reported that Iran would open the strait 30 days after a deal is signed. Rubio, speaking from Jaipur during his India trip, said the strait "has to be open, one way or the other."

If the deal holds, oil prices could fall substantially. India's fuel retailers could stabilize or even reduce prices. The rupee could recover. The inflation spiral could ease.

If the deal collapses — which it has done before, repeatedly, over the past three months — then the fifth hike will come. And the sixth. And the financial strain on 1.4 billion people who are already paying 8 percent more for the fuel that moves their food, their goods, and their lives will deepen.

## What NRIs Are Watching

For the Indian diaspora, the fuel price crisis is not abstract. It is the cost of the autorickshaw your parents take to the hospital. It is the diesel that powers the generator when the electricity cuts out. It is the cooking gas cylinder that costs ₹50 more than it did two weeks ago.

Remittance inflows to India — the largest in the world at over $125 billion annually — are partially offsetting the economic pressure. But remittances are sent in dollars and spent in rupees, and the gap between what a dollar buys at the forex counter and what it buys at the petrol pump is widening every week.

The Iran deal is the single variable that matters most. Everything else — opposition protests, government austerity measures, RBI interventions — is noise around the signal. The signal is: will the Strait of Hormuz reopen? And if so, when?

India is waiting. The world is waiting. The price board at the petrol pump will tell you when the answer arrives."""

    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "Petrol Has Crossed ₹102 in Delhi. ₹110 in Bengaluru. India Has Raised Fuel Prices Four Times in Ten Days. The Iran War Is the Reason. An Iran Deal Might Be the Only Relief.",
        "subheadline": "India's state-owned fuel retailers raised petrol and diesel prices for the fourth time in ten days on Monday, pushing cumulative increases past ₹7.50 per litre. The hikes are driven by the Iran war's closure of the Strait of Hormuz, which has disrupted 20 percent of global oil supply. India's oil imports fell 15.5 percent year-over-year in April. The rupee hit a record low of 96.96 before recovering on news that a US-Iran deal is 'largely negotiated.' If the strait reopens, relief could come within weeks. If the deal collapses, the fifth hike is coming.",
        "slug": slug1,
        "category": "news",
        "vertical": "nri-world",
        "diaspora_angle": "For NRIs, the fuel crisis hits home literally. Remittances — over $125 billion annually, the world's largest — are sent in dollars and spent in rupees. The rupee's 4.7 percent decline since the Iran war began means each dollar converts to more rupees, but the purchasing power of those rupees is being consumed by the same inflation driving the currency down. The ₹7.50 petrol hike ripples into autorickshaw fares, food prices, cooking gas, and every supply chain that runs on diesel. Parents, siblings, and extended families are absorbing costs that NRIs cannot control from abroad. The Iran deal is the variable that matters most — if the Strait of Hormuz reopens, oil prices drop, the rupee stabilizes, and the inflation pressure eases. If it collapses, the fifth hike is coming, and the remittance math gets worse.",
        "tags": ["fuel prices", "petrol", "diesel", "India", "Iran war", "Strait of Hormuz", "oil imports", "rupee", "RBI", "inflation", "NRI", "remittances", "Venezuela", "crude oil", "Modi", "austerity"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters — Indian retailers raise fuel prices a fourth time to rein in losses", "url": "https://www.reuters.com/business/energy/indian-retailers-raise-fuel-prices-fourth-time-amid-iran-war-2026-05-25/"},
            {"name": "Reuters — India turns to Latin American, African oil after Hormuz disruption", "url": "https://www.reuters.com/business/energy/india-turns-latin-american-african-oil-after-hormuz-disruption/"},
            {"name": "Reuters — Rupee gains to two-week high as oil prices slump", "url": "https://www.reuters.com/markets/currencies/rupee-gains-two-week-high-oil-prices-slump/"},
            {"name": "Reuters — Indian banks seek hedging cost subsidy from RBI", "url": "https://www.reuters.com/world/india/indian-banks-seek-hedging-cost-subsidy-from-rbi/"},
            {"name": "Reuters — Axios says proposed US-Iran deal involves opening strait during 60-day ceasefire", "url": "https://www.reuters.com/world/axios-says-proposed-us-iran-deal-involves-opening-strait-during-60-day-ceasefire-2026-05-24/"}
        ]),
        "score_total": 87,
        "status": "published",
        "published_at": now_iso,
        "body": body1
    })
    print(f"✓ Article 1 prepared: India fuel price crisis / Iran war / Hormuz")
else:
    print(f"✗ Article 1 skipped (duplicate detected)")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Sridhar Vembu "Choose Self-Respect" — The Diaspora Debate
# ══════════════════════════════════════════════════════════════

slug2 = make_slug("sridhar-vembu-zoho-indians-come-home-self-respect-green-card")
headline2_prefix = "sridhar vembu"
alt_prefix2 = "vembu"
if slug2 not in existing_slugs and not any(headline2_prefix in h or alt_prefix2 in h for h in existing_headlines_lower):
    body2 = """Three days after the United States government told every immigrant seeking a Green Card that they must leave the country to apply, a billionaire told them where to go.

"Choose self-respect," Sridhar Vembu wrote on X.

Vembu is the founder and CEO of Zoho Corporation, a privately held software company valued at over $5 billion that makes business applications used by over 100 million people worldwide. He is also an Indian-origin technologist who spent 25 years living in the United States before moving back to India — specifically, to a village in Tamil Nadu — in a decision he has framed as both personal and philosophical.

When the U.S. Citizenship and Immigration Services announced on May 22 that adjustment of status — the process by which immigrants already in the U.S. apply for permanent residency without leaving — would now be treated as "an extraordinary form of relief" rather than a routine pathway, Vembu responded with a message to the estimated 1.2 million Indian Americans affected: come home.

The internet did not receive this well.

## What USCIS Actually Did

The policy memo, released May 22, does not technically abolish adjustment of status. What it does is redefine it.

For six decades, adjustment of status has been the standard mechanism by which H-1B holders, L-1 visa holders, and other work-authorized immigrants applied for Green Cards while continuing to live and work in the United States. The process was slow — for Indian-born applicants in the EB-2 category, the current wait exceeds a decade — but it allowed people to remain in the country, keep their jobs, and maintain their children's schooling while the paperwork ground through the system.

Under the new guidance, USCIS officers are instructed to view adjustment of status as "a matter of discretion and administrative grace" — language that signals it should be the exception, not the rule. The default pathway is now consular processing: leave the United States, go to a U.S. embassy or consulate in your home country, and apply there.

"USCIS is trying to upend decades of processing of adjustment of status," said Shev Dalal-Dheini, senior director of government relations at the American Immigration Lawyers Association. "This applies very broadly to anyone seeking a green card."

For Indians specifically, the math is devastating. The EB-2 India backlog already stretches past 2012 for priority dates. Consular processing in India means joining a queue at embassies that are already overwhelmed — where B-2 tourist visa appointments have 300-day wait times and where the infrastructure was not built for the volume that adjustment of status was designed to absorb.

Former White House advisor Ajay Bhutoria put it bluntly: "This puts 1.2 million Indian Americans and their families in limbo after they followed every law, paid taxes, and waited legally for decades. Officials now have unchecked discretion."

## What Vembu Said

Vembu's response to the DHS announcement was not a policy analysis. It was a philosophical provocation.

He urged Indians living in the United States on visas to return to India — to "choose self-respect" over a system that he characterized as increasingly hostile to the people it claims to welcome. He pointed to his own example: he left Silicon Valley, moved to Tenkasi in rural Tamil Nadu, and built Zoho into one of the world's largest privately held software companies from a village.

Vembu has been consistent on this theme. At the ImagiNxt 2026 Summit, he warned against "digital colonialism" and advocated for what he calls "dharmic capitalism" — profitable enterprise rooted in Indian values and Indian soil. He has argued that India's tech ecosystem is mature enough to support world-class careers without the visa dependency that defines the professional lives of millions of Indian-origin workers in America.

His message to the diaspora was, in essence: the system does not respect you. Stop waiting for it to change. Come build India instead.

## Why He Got Slammed

The backlash was immediate and visceral.

On X and LinkedIn, Indian professionals pointed out the gap between Vembu's circumstances and theirs. Vembu is a billionaire. He owns his company. He does not need a visa, a Green Card, or an employer's sponsorship to live where he wants. His "choice" to return to India was made from a position of extraordinary financial security — a position that the H-1B software engineer with a mortgage in Sunnyvale, two children in American schools, and a Green Card application filed in 2016 does not share.

"Easy to say 'choose self-respect' when you have $5 billion of self-respect in the bank," one widely shared post read.

Critics also challenged the premise that returning to India was straightforward. Engineers who have spent 10-15 years in the United States have built lives — houses, school enrollments, professional networks, retirement savings in 401(k) accounts, credit histories, medical relationships. Uprooting is not a philosophical exercise. It is a logistical and financial ordeal that involves selling property, withdrawing retirement funds (with tax penalties), re-establishing credentials in India, and — for those with American-born children — navigating the citizenship and cultural implications of moving kids who have never lived in India.

Others pointed to structural challenges in India that Vembu's framing glosses over: lower salaries (even adjusted for purchasing power), infrastructure gaps, pollution levels that are among the worst in the world, and a professional culture that many returning NRIs describe as less meritocratic than the one they left.

"Come back to India for what?" one comment read. "To earn one-fifth the salary, breathe air that kills you, and deal with a system that makes the H-1B look efficient?"

## The Tension That Will Not Resolve

Vembu is not wrong that the U.S. immigration system has become hostile to Indian professionals. The numbers are stark: H-1B registrations dropped 38.5 percent. India's top IT firms lost 40 percent of their H-1B approvals. TCS alone lost 3,242 visas. The new adjustment of status guidance effectively forces people who have lived in America for a decade or more to leave the country and re-enter a queue from abroad.

But the critics are not wrong either. Telling people to "choose self-respect" when they are trapped in a system they entered legally, played by the rules of, and built their lives around is a message that lands differently depending on whether you have a private jet or a 7:04 AM Caltrain commute.

The deeper tension is one that the Indian diaspora has been navigating for decades: the gap between the America that recruits Indian talent and the America that processes Indian immigration. The first America wants your skills, your labor, your tax revenue, and your consumption. The second America makes you wait 12 years for a Green Card, tells you adjustment of status is now "extraordinary," and processes your visa renewal at a pace that would embarrass a municipal water department.

Vembu's provocation — intentional or not — has surfaced the question that 4.8 million Indian Americans avoid asking in polite company: at what point does staying become an act of endurance rather than an act of choice?

The answer is different for a 28-year-old engineer who just arrived on an H-1B and a 45-year-old with American-born teenagers. It is different for someone in Hyderabad's tech corridor and someone in a Tier 3 city. It is different for someone whose parents are in Chennai and someone whose parents are in Chicago.

There is no universal answer. There is only the question — and the fact that a billionaire asked it does not make it less real for the people who cannot afford to answer it the way he did."""

    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "Zoho's Sridhar Vembu Told 1.2 Million Indians in America to 'Choose Self-Respect' and Come Home After the New Green Card Rule. The Internet Told Him What Self-Respect Looks Like When You Don't Have $5 Billion.",
        "subheadline": "Three days after USCIS declared adjustment of status an 'extraordinary form of relief' rather than a routine pathway — effectively telling immigrants seeking Green Cards to leave the United States and apply from their home countries — Zoho founder Sridhar Vembu urged Indian professionals to return to India and 'choose self-respect.' The billionaire, who moved from Silicon Valley to a Tamil Nadu village after 25 years in the US, framed the return as both patriotic and practical. The backlash was immediate: critics called his advice tone-deaf, noting the gap between a billionaire's 'choice' and an H-1B holder's reality of mortgages, American-born children, decade-long Green Card waits, and lives built around a system that is now being redesigned mid-stream.",
        "slug": slug2,
        "category": "news",
        "vertical": "nri-world",
        "diaspora_angle": "This is the diaspora story of 2026. The new USCIS guidance affects an estimated 1.2 million Indian Americans directly — H-1B holders, L-1 holders, F-1 graduates, and their families who have been living, working, and paying taxes in the United States while waiting for permanent residency through adjustment of status. The Vembu controversy is not about one man's opinion; it is about the fracture line running through every Indian professional community in America. The 'should we stay or should we go' debate has been simmering for years, but the new Green Card rule — combined with a 38.5 percent drop in H-1B registrations and 40 percent loss in IT firm visa approvals — has made it urgent. For NRIs who have built their entire adult lives in the US, the question is not philosophical. It is logistical, financial, emotional, and — increasingly — existential.",
        "tags": ["Sridhar Vembu", "Zoho", "Green Card", "adjustment of status", "USCIS", "H-1B", "NRI", "Indian Americans", "immigration", "diaspora", "consular processing", "return to India", "self-respect", "Silicon Valley", "Tamil Nadu"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "USCIS — Adjustment of Status Only in Extraordinary Circumstances", "url": "https://www.uscis.gov/newsroom/news-releases/uscis-will-grant-adjustment-of-status-only-in-extraordinary-circumstances"},
            {"name": "Dainik Bhaskar — Zoho Founder Vembu Urges Indians Return US Amid Green Card Rules", "url": "https://bhaskarenglish.in/national/zoho-founder-sridhar-vembu-urges-indians-return-us-amid-green-card-rules/"},
            {"name": "Bloomberg Law — Trump Administration Narrows Path to Seek Green Cards Inside US", "url": "https://news.bloomberglaw.com/daily-labor-report/trump-admin-narrows-path-to-seek-green-cards-inside-us"},
            {"name": "Inshorts — 1.2 mn Indian-American families affected: Ex-WH aide on new Green Card rule", "url": "https://inshorts.com/en/news/1-2-mn-indian-american-families-affected--ex-wh-aide-on-new-green-card-rule"},
            {"name": "VisaVerge — USCIS Limits Adjustment of Status: New 2026 Policy Impact", "url": "https://www.visaverge.com/immigration-news/uscis-limits-adjustment-of-status-new-2026-policy-impact/"}
        ]),
        "score_total": 86,
        "status": "published",
        "published_at": now_plus1,
        "body": body2
    })
    print(f"✓ Article 2 prepared: Sridhar Vembu / Green Card / come home debate")
else:
    print(f"✗ Article 2 skipped (duplicate detected)")


# ══════════════════════════════════════════════════════════════
# PUBLISH + IMAGE SOURCING
# ══════════════════════════════════════════════════════════════

if not articles:
    print("\n⚠ No new articles to publish. Exiting.")
    exit(0)

print(f"\n📝 Publishing {len(articles)} articles...")

for i, art in enumerate(articles):
    art_id = art["id"]
    print(f"\n--- Article {i+1}: {art['headline'][:80]}...")

    try:
        result = sb_post("p2_articles", art)
        print(f"  ✓ Inserted: {art_id}")
    except Exception as e:
        print(f"  ✗ Insert failed: {e}")
        continue

    # Image sourcing — Wikipedia first for person articles, Pexels fallback
    img_url = None
    img_attribution = "The Videshi"

    if i == 0:
        # Fuel price article — no specific person, use Pexels with specific terms
        img_url = fetch_pexels_image("India petrol pump fuel price board", "India gas station fuel price")
    elif i == 1:
        # Sridhar Vembu — specific person, Wikipedia FIRST
        img_url = fetch_wikipedia_person_image("Sridhar Vembu")
        if img_url:
            img_attribution = "Wikimedia Commons"
        else:
            # Try alternate name
            img_url = fetch_wikipedia_person_image("Sridhar Vembu (businessman)")
            if img_url:
                img_attribution = "Wikimedia Commons"
            else:
                img_url = fetch_pexels_image("Indian tech entrepreneur silicon valley", "India software office professional")

    if img_url:
        filename = f"{art['slug']}.jpg"
        final_url = upload_image_to_supabase(img_url, filename)
        try:
            sb_patch("p2_articles", {"id": f"eq.{art_id}"}, {
                "image_url": final_url,
                "image_attribution": img_attribution
            })
            print(f"  ✓ Image linked (attribution: {img_attribution})")
        except Exception as e:
            print(f"  ⚠ Image PATCH failed: {e}")

# ══════════════════════════════════════════════════════════════
# SCORE DECAY
# ══════════════════════════════════════════════════════════════

print("\n📉 Applying score decay to older news articles...")
try:
    old_arts = sb_get("p2_articles", {
        "select": "id,score_total",
        "status": "eq.published",
        "category": "eq.news",
        "published_at": f"lt.{(now - timedelta(days=7)).isoformat().replace('+00:00', 'Z')}",
        "score_total": "gt.35",
        "limit": "200"
    })
    for a in old_arts:
        sb_patch("p2_articles", {"id": f"eq.{a['id']}"}, {"score_total": 35})
    print(f"  Decayed {len(old_arts)} articles (>7d → 35)")

    mid_arts = sb_get("p2_articles", {
        "select": "id,score_total",
        "status": "eq.published",
        "category": "eq.news",
        "published_at": f"lt.{(now - timedelta(days=3)).isoformat().replace('+00:00', 'Z')}",
        "score_total": "gt.50",
        "limit": "200"
    })
    mid_arts = [a for a in mid_arts if a["id"] not in {x["id"] for x in old_arts}]
    for a in mid_arts:
        sb_patch("p2_articles", {"id": f"eq.{a['id']}"}, {"score_total": 50})
    print(f"  Decayed {len(mid_arts)} articles (3-7d → 50)")
except Exception as e:
    print(f"  ⚠ Decay error: {e}")

# ══════════════════════════════════════════════════════════════
# GIT COMMIT + PUSH
# ══════════════════════════════════════════════════════════════

print("\n📦 Committing and pushing...")
repo_dir = Path.home() / "workspace" / "the-videshi-news"
try:
    subprocess.run(["git", "add", "-A"], cwd=repo_dir, capture_output=True, timeout=15)
    result = subprocess.run(
        ["git", "commit", "-m", f"news: fuel crisis + Vembu come-home debate ({now.strftime('%Y-%m-%d %H:%M')} UTC)"],
        cwd=repo_dir, capture_output=True, text=True, timeout=15
    )
    print(f"  Commit: {result.stdout.strip()[:100]}")
    push = subprocess.run(["git", "push"], cwd=repo_dir, capture_output=True, text=True, timeout=30)
    if push.returncode == 0:
        print("  ✓ Pushed to main → Vercel auto-deploy")
    else:
        print(f"  ⚠ Push issue: {push.stderr[:200]}")
except Exception as e:
    print(f"  ⚠ Git error: {e}")

print("\n✅ News writer batch complete.")
