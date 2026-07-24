#!/usr/bin/env python3
"""Videshi Writer — 2 fresh NEWS articles for 2026-05-25 00:30 UTC batch
Topics: 1) OpenAI & Anthropic launch AI services companies that directly compete with India's $280B IT industry
        2) Gas prices hit $4.56/gallon — the most expensive Memorial Day weekend in four years — and the NRI summer squeeze
"""

import json, os, uuid, re, requests, subprocess
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
# Stagger by 1 minute
now_plus1 = (now + timedelta(minutes=1)).isoformat().replace('+00:00', 'Z')

articles = []

# ══════════════════════════════════════════════════════════════
# ARTICLE 1: OpenAI & Anthropic Launch AI Services Arms
# ══════════════════════════════════════════════════════════════

slug1 = make_slug("openai-anthropic-ai-services-india-it-industry-tcs-infosys-nri")
headline1_prefix = "openai and anthropic just launched companies"
if slug1 not in existing_slugs and not any(headline1_prefix in h for h in existing_headlines_lower):
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "OpenAI and Anthropic Just Launched Companies to Do the Exact Work That Employs Five Million Indians. The $280 Billion IT Industry Has Three Years to Respond.",
        "subheadline": "OpenAI formed DeployCo with $4 billion in backing from Brookfield, TPG, Bain Capital, and Advent. Anthropic built a joint venture with Blackstone, Goldman Sachs, and Hellman & Friedman. Both companies will send AI-powered teams into enterprises to build, deploy, and maintain software systems — the precise work that TCS, Infosys, Wipro, and HCL have billed human hours for since the 1990s. For the 300,000 Indian IT workers in America on H-1B visas, the companies that sponsor their presence in this country just became the targets of the two most well-funded AI startups on Earth.",
        "slug": slug1,
        "category": "news",
        "vertical": "technology",
        "diaspora_angle": "This is not an abstract industry story for the Indian diaspora. It is personal. Indian IT services companies are the single largest sponsors of H-1B visas in the United States. TCS, Infosys, Wipro, and Cognizant collectively hold hundreds of thousands of active H-1B petitions. These are not just employers — they are the legal basis on which hundreds of thousands of Indian professionals and their families live, work, send children to school, and build lives in America. When the revenue model that sustains these companies comes under structural pressure, the visa sponsorship pipeline comes under pressure too. Every NRI who works at an Indian IT company, married someone who does, or knows families whose green card applications depend on continued employment at one of these firms should understand what DeployCo and Anthropic's new venture mean. The companies are not threatening to replace Indian engineers. They are threatening to replace the business model that pays Indian engineers. The distinction matters because the engineers who can adapt — who learn to deploy AI systems rather than just write the code that AI can now write — will be more valuable than ever. But the ones who cannot will find that their employers have fewer projects to staff, fewer margins to protect, and fewer reasons to file the next H-1B petition.",
        "tags": ["OpenAI", "Anthropic", "DeployCo", "AI", "TCS", "Infosys", "Wipro", "HCL", "IT services", "H-1B", "NRI", "Silicon Valley", "India", "technology", "consulting", "Blackstone", "Goldman Sachs", "Bain Capital", "enterprise"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "AI Business — OpenAI Launches AI Consulting Company, Following Anthropic", "url": "https://aibusiness.com/generative-ai/openai-launches-ai-consulting-company-anthropic"},
            {"name": "Medium / Surya Kailash — Anthropic and OpenAI Launched AI Services Arms to Reshape Enterprise Tech", "url": "https://medium.com/@mnvsuryakailash/the-great-ai-shift-has-begun-in-indias-it-industry-b26e6baffae0"},
            {"name": "Inshorts — OpenAI beats Anthropic, earns over ₹54,000 crore revenue in Q1", "url": "https://inshorts.com/en/news/openai-beats-anthropic-earns-over-rs-54000-crore-revenue-in-q1-report-1716381480"},
            {"name": "India Today — Anthropic, OpenAI launch AI services companies, challenge TCS and Infosys", "url": "https://www.indiatoday.in/technology/news/story/anthropic-openai-launch-ai-services-companies-challenge-tcs-and-infosys-in-india-2906776-2026-05-05"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now_iso,
        "body": """For thirty years, India's IT services industry has run on a single, extraordinarily profitable idea: American companies need software built and maintained, Indian companies have the engineers to do it, and the time zone difference means work gets done overnight at a fraction of the cost.

That idea built TCS into a $180 billion company. It made Infosys a household name from Bengaluru to Bangalore Road in Edison, New Jersey. It put Wipro, HCL, and Cognizant into the Fortune 500. It created five million jobs in India and sent hundreds of thousands of engineers to the United States on H-1B visas, where they became the backbone of America's technology infrastructure.

Now two companies want to do the same work — faster, cheaper, and without a single visa application.

## What Just Happened

In early May, OpenAI announced the formation of **DeployCo**, a majority-owned subsidiary dedicated to helping enterprises build and deploy AI systems. The company launched with more than **$4 billion in initial investment** from Brookfield Asset Management, TPG, Advent, and Bain Capital — heavyweight financial operators who deploy billions only when they see a structural shift that is already underway.

DeployCo acquired **Tomoro**, an applied AI consulting firm, bringing 150 engineers on board immediately. Its model is borrowed from Palantir: embed specialised AI engineers directly inside client organisations to design, test, and deploy production-ready systems. OpenAI has also partnered with 19 investment and consulting firms to scale the operation.

Days earlier, **Anthropic** — the company behind the Claude AI model — announced a joint venture with **Blackstone, Goldman Sachs, and Hellman & Friedman**. The stated mission: work directly with mid-sized companies and bring Claude into their core business operations. Not as a software licence. As a managed service. The kind of service where Anthropic sits across the table from a business and says: *tell us your problem, we will use AI to solve it for you.*

That sentence describes, almost word for word, what TCS, Infosys, and Wipro have been doing for three decades — except they used teams of fifty engineers where Anthropic plans to use AI systems supervised by a handful of specialists.

## The $280 Billion Question

India's IT services industry is worth **$280 billion** in annual revenue. It employs over five million people directly and supports millions more in adjacent industries. It accounts for roughly 10% of India's GDP and is the single largest source of foreign exchange after oil imports.

The industry's most profitable business line — application development and maintenance — is precisely the category that DeployCo and Anthropic's venture will target first. This work is high-volume, predictable, and measurable, which makes it the easiest to automate with AI-driven delivery.

A Gartner analyst put it plainly: "There's a lot of piloting happening within the enterprise, but a lot of customers are not seeing clear value, and some of that is primarily because they don't have the internal expertise." OpenAI and Anthropic are offering to be that expertise — at a price point that does not require billing human hours across time zones.

The threat is not theoretical. OpenAI generated **$5.7 billion in revenue** in Q1 2026 alone. Anthropic expects its revenue to more than double to $11 billion in Q2 and anticipates its **first profitable quarter**. These are not startups burning through venture capital. They are companies with the revenue, the technology, and now the consulting infrastructure to compete directly for enterprise contracts that currently flow to Indian IT firms.

## Why This Is Personal for Every NRI in Tech

Indian IT services companies are the **single largest category of H-1B visa sponsors** in the United States. TCS, Infosys, Wipro, and Cognizant collectively hold hundreds of thousands of active H-1B petitions. For the approximately 300,000 Indian IT workers in America whose legal right to live and work here depends on continued employment at one of these firms, this is not an industry trend to watch from a distance.

When the revenue model that sustains these companies comes under structural pressure, the visa sponsorship pipeline comes under pressure with it. Fewer projects mean fewer billable hours. Fewer billable hours mean fewer positions to staff. Fewer positions mean fewer H-1B petitions filed, fewer extensions approved, and fewer green card applications moving through the decade-long queue that already has Indian applicants waiting 80 years or more.

The irony is sharp. The same AI technology that Indian engineers helped build — Claude was trained in part by data labellers in India; OpenAI's research teams include dozens of IIT graduates — is now being weaponised against the business model that brought those engineers to America in the first place.

## What the Indian IT Giants Are Doing

The largest companies have not been standing still. TCS launched its AI Cloud platform. Infosys has its **Topaz AI platform**, which it positions as a bridge between traditional service delivery and AI-augmented operations. Wipro has **ai360**. HCL has invested in generative AI tools for internal use.

But there is a critical difference between building AI tools and becoming an AI services company. TCS can offer Topaz to its existing clients as an enhancement. OpenAI can offer DeployCo to those same clients as a replacement.

India's IT companies also have something OpenAI and Anthropic lack: decades of trust with large enterprise clients, deep knowledge of client systems, regulatory compliance expertise, and on-the-ground delivery teams in 50 countries. An analyst at Futurum Group noted that "enterprises are looking at integrating what OpenAI offers with everything else the enterprise is already doing — the people who have the most experience integrating ten different things from ten different vendors are not one of those vendors."

That advantage is real. But it is also a rearguard argument. India's IT industry won the last war — the outsourcing revolution — by being cheaper and faster than the incumbents. Now it is the incumbent, and the challengers are cheaper and faster by orders of magnitude.

## The Three-Year Window

This is not a story of Indian IT dying tomorrow. The consulting arms of these companies — TCS Consulting, Infosys Consulting — are safer in the near term because they sell human judgement, relationships, and strategic thinking that AI cannot yet replicate.

But the window for transformation is narrow. Industry analysts estimate Indian IT companies have **three to five years** to pivot their most profitable service lines before DeployCo, Anthropic's venture, and the dozens of AI services startups that will follow them erode the margins that fund everything else — including the visa sponsorship pipeline.

India contributes 23% of all AI-related code on GitHub, more than any other country. India hosts 55% of the world's Global Capability Centres — the R&D arms of every major technology company. India's AI Mission has committed ₹10,371 crore to build the infrastructure, datasets, and talent pipeline for artificial intelligence.

The talent is there. The question is whether India's engineers and companies will be participants in the new AI services economy or casualties of it.

For NRIs who built their American lives on the foundation of India's IT industry, the answer to that question is not academic. It is the difference between a career that adapts and one that the machines learned to do first."""
    })
    print(f"✅ Article 1 queued: {slug1}")
else:
    print(f"⏭️  Article 1 skipped (duplicate): {slug1}")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Memorial Day gas prices — most expensive ever
# ══════════════════════════════════════════════════════════════

slug2 = make_slug("memorial-day-gas-prices-456-iran-war-nri-summer-squeeze")
headline2_prefix = "gas prices just hit $4.56"
if slug2 not in existing_slugs and not any(headline2_prefix in h for h in existing_headlines_lower):
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "Gas Prices Just Hit $4.56 a Gallon. This Is the Most Expensive Memorial Day in Four Years. For NRI Families Planning a Summer in India, the Math Just Broke.",
        "subheadline": "Forty-five million Americans hit the road this weekend. They are paying 30% more per gallon than last year. In California, the average is $6.13. Across 12 states, prices set Memorial Day records. The Iran war closed the Strait of Hormuz three months ago and Americans are spending $2 billion more on gas this weekend alone. For Indian American families, the summer squeeze is compounding: flights to India are at multi-year highs, the rupee is weakening, and the same war that raised pump prices is the reason India is being pressured to stop buying the discounted Russian oil that keeps its own economy afloat.",
        "slug": slug2,
        "category": "news",
        "vertical": "economy",
        "diaspora_angle": "Memorial Day weekend is when NRI families make the summer call: do we go to India this year? The answer has always been partly financial — flights, hotels, gifts, rupee conversion. This year, the calculation starts before anyone opens a booking app. Filling the minivan costs $80. Driving to the airport costs more than it did last Memorial Day by double digits. The flight itself — if you are flying Delhi, Mumbai, or Hyderabad from a US hub — is $1,200 to $1,800 roundtrip, up from $900 to $1,200 two summers ago. And when you land, the rupee has weakened against the dollar, which helps your purchasing power but signals an economy under stress from the same global energy crisis that emptied your wallet at the Costco gas pump. This is the summer where every NRI family budget gets stress-tested. The ones who planned early and booked in February are fine. Everyone else is doing the maths this weekend — and the maths says this is the most expensive summer to be Indian in America since the pandemic.",
        "tags": ["gas prices", "Memorial Day", "Iran war", "Strait of Hormuz", "oil", "NRI", "Indian American", "summer travel", "India flights", "economy", "inflation", "California", "AAA", "energy", "rupee"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "NBC Palm Springs — Record 45 Million Americans to Travel for Memorial Day Weekend Despite Highest Gas Prices in Four Years", "url": "https://nbcpalmsprings.com/2026/05/23/record-45-million-americans-to-travel-for-memorial-day-weekend-despite-highest-gas-prices-in-four-years/"},
            {"name": "Washington Examiner — Americans may spend $2 billion more on gas over Memorial Day as prices still surge", "url": "https://www.washingtonexaminer.com/policy/energy-and-environment/americans-spend-2-billion-more-gas-memorial-day-prices-surge/"},
            {"name": "Seeking Alpha — Memorial Day pump prices up 30% from last year, may get worse as gasoline storage tightens", "url": "https://seekingalpha.com/news/memorial-day-pump-prices-30-percent-higher/"},
            {"name": "Fox News — Trump economist points to 'great signs' of easing inflation, predicts fuel costs will 'plummet' with Iran deal", "url": "https://www.foxnews.com/politics/trump-economist-predicts-fuel-costs-plummet-iran-deal"},
            {"name": "CNN — Memorial Day weekend could be costly and chaotic", "url": "https://www.cnn.com/2026/05/23/economy/memorial-day-weekend-gas-travel-costs/"}
        ]),
        "score_total": 80,
        "status": "published",
        "published_at": now_plus1,
        "body": """Forty-five million Americans are travelling this Memorial Day weekend. They are paying more for gasoline than any Memorial Day traveller has paid in four years.

The national average price for a gallon of regular unleaded hit **$4.56** on Friday, according to AAA — nearly **30% higher** than this time last year. In California, drivers are paying **$6.13 a gallon**. Across 12 states, pump prices set Memorial Day records. GasBuddy called it the second-most-expensive Memorial Day ever recorded at the pump.

Americans will spend an estimated **$2 billion more on gasoline** this weekend alone compared to last year.

The cause is not a mystery. The Iran war — now in its third month — closed the Strait of Hormuz, which before the conflict carried one-fifth of global oil and liquefied natural gas shipments. The strait remains under U.S. naval blockade while negotiators work toward a deal. On Saturday, Trump said Washington and Iran had "largely negotiated" a memorandum of understanding. On Sunday, he said there was "no rush." Gas prices do not respond to maybes.

## The NRI Summer Budget Just Broke

For Indian American families, Memorial Day weekend is when the summer calculation happens. This is when parents look at calendars, check school end dates, and decide whether this is the year they take the kids to India.

That decision has always been partly financial. This year, the maths is punishing at every level.

**At the pump:** Filling a typical SUV — the vehicle of choice for Indian American families from Edison to Fremont — costs roughly $80 at today's national average. In the Bay Area, where gas regularly exceeds $5.50, it is closer to $100. A family driving from their suburban home to SFO, JFK, or IAD for an India flight is spending 30% more on the trip to the airport than they did last May.

**In the air:** Round-trip economy flights from major U.S. hubs to Delhi, Mumbai, or Hyderabad are running $1,200 to $1,800 this summer, up from $900 to $1,200 two summers ago. Air India's new SFO lounge opened this month — a nod to the Bay Area diaspora's purchasing power — but the fares to use it have climbed faster than the airline's service quality. The Iran war disrupted fuel supply chains globally, and airlines have passed the cost directly to passengers through fuel surcharges that now account for up to 25% of the ticket price.

**On the ground in India:** The rupee has weakened against the dollar, which makes the daily spending more affordable for NRIs converting at ₹86–87 to the dollar. But a weak rupee signals an Indian economy under stress from the same global energy crisis. India imports roughly 85% of its crude oil. When Hormuz closes and prices spike, India's import bill rises, inflation pushes up domestic costs, and the relatives you are visiting are paying more for cooking gas, petrol, and groceries.

## The India-Energy Irony

The geopolitics of this moment are painfully ironic for the diaspora.

India has been buying discounted Russian crude in record volumes — **$46 billion worth in fiscal year 2026** — because the Iran war and Hormuz closure made global oil unaffordably expensive. That Russian oil keeps India's economy functioning and domestic fuel prices from spiralling further.

But India's Russian oil purchases are exactly what prompted the Trump administration to slap 50% tariffs on Indian goods earlier this year. Those tariffs were partially rolled back to 18% in an interim deal, but the message was clear: America wants India to buy American energy, not Russian energy.

Marco Rubio — in New Delhi this weekend for Quad talks — made the point explicit. He told Indian officials that U.S. energy was "key to diversifying India's supply." On the same day that Americans were paying the highest Memorial Day gas prices in four years because of America's own war.

The NRI sits at the intersection of both realities. You pay $4.56 a gallon because of the Hormuz closure. India buys Russian oil to avoid paying $4.56 a gallon. America punishes India for buying that Russian oil. And the trade deal meant to fix the tariffs has been "near finalisation" since February.

## When Does It End?

Trump's National Economic Council Director Kevin Hassett told Fox News on Sunday that fuel prices would "plummet" once an Iran deal is reached. The deal's contours are emerging: a 60-day ceasefire, Hormuz reopened without tolls, Iran clearing its own mines, the U.S. lifting its naval blockade.

But oil analysts at MarketWatch caution that even if the strait reopens tomorrow, **prices will not return to pre-war levels quickly**. Months of logistical challenges lie ahead — clearing bottlenecks, reducing stockpiles, restarting production, repairing refinery schedules. CNN reported that the era of $3 gas may be over for the foreseeable future.

For NRI families making summer plans this weekend, the timeline is academic. The flights need to be booked now. The gas tank needs to be filled now. The summer camps, the grandparent visits, the wedding obligations — none of them wait for a peace deal.

## The Compound Squeeze

What makes this summer different from previous expensive summers is the **compounding**. It is not just gas. It is not just flights. It is everything simultaneously.

Grocery prices are up. Airfares are up. Hotels in India — particularly in the wedding-season cities of Jaipur, Udaipur, and Goa — are up. The cost of gifts (because no NRI arrives empty-handed) is up. School activity fees for the summer programmes you are leaving behind are up.

A mid-range NRI family trip to India — two adults, two children, three weeks, visiting family in two cities — ran roughly $8,000 to $10,000 all-in two years ago. This summer, the same trip costs $11,000 to $14,000. For families where one earner is on an H-1B visa and the other may not have work authorisation, that is a meaningful difference.

The families who will go anyway are the ones who budgeted for it in January, who bought tickets when fares dipped in February, who have parents in India they have not seen since the pandemic compressed everyone's sense of time and distance.

The ones who will not are making that decision right now, this weekend, standing at a gas pump that charges $4.56 a gallon and wondering whether this is the summer they stay home.

For forty-five million Americans, Memorial Day is the start of summer. For the 4.4 million Indian Americans among them, it is the start of a financial stress test that will not end until the last suitcase is unpacked in September — or until someone reopens the Strait of Hormuz. Whichever comes first."""
    })
    print(f"✅ Article 2 queued: {slug2}")
else:
    print(f"⏭️  Article 2 skipped (duplicate): {slug2}")


# ── Insert articles ──
for article in articles:
    try:
        result = sb_post("p2_articles", article)
        print(f"✅ Inserted: {article['slug']} → {article['id']}")
    except Exception as e:
        print(f"❌ Insert failed for {article['slug']}: {e}")

print(f"\n{'='*60}")
print(f"Published {len(articles)} articles")
print(f"{'='*60}")

# ── Score decay for news articles ──
try:
    decay_articles = sb_get("p2_articles", {
        "select": "id,score_total,published_at",
        "status": "eq.published",
        "category": "eq.news",
        "score_total": "gt.40",
        "published_at": "lt." + (now - timedelta(hours=12)).isoformat().replace('+00:00', 'Z'),
        "order": "published_at.desc",
        "limit": "50"
    })
    decayed = 0
    for a in decay_articles:
        age_hours = (now - datetime.fromisoformat(a["published_at"].replace('Z', '+00:00'))).total_seconds() / 3600
        if age_hours > 48:
            decay = 3
        elif age_hours > 24:
            decay = 2
        else:
            decay = 1
        new_score = max(40, a["score_total"] - decay)
        if new_score != a["score_total"]:
            sb_patch("p2_articles", {"id": f"eq.{a['id']}"}, {"score_total": new_score})
            decayed += 1
    print(f"\n📉 Score decay: {decayed} news articles decayed")
except Exception as e:
    print(f"⚠️ Score decay error: {e}")

print("\n✅ Writer pipeline complete")
