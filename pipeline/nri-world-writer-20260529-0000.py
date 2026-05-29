#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

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

now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-" + datetime.now().strftime("%Y%m%d")

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Five Indian Americans Just Made TIME's 100 Most Influential List. The Spread Tells the Real Story.",
        "subheadline": "A Google CEO, a socialist mayor, a YouTube boss, a gene-therapy pioneer, and a celebrity chef — the 2026 TIME100 is less a who's who than a map of where diaspora power actually sits now.",
        "slug": make_slug("time100-2026-five-indian-americans-diaspora-influence"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Five Indian Americans across wildly different fields — from AI to gene therapy to municipal politics — making the same global influence list signals that diaspora success has moved well beyond the tech-CEO archetype into governance, science, and culture.",
        "tags": ["nri", "diaspora", "time100", "sundar-pichai", "zohran-mamdani", "neal-mohan", "vikas-khanna", "kiran-musunuru"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "American Kahani", "url": "https://americankahani.com/lead-stories/mamdani-and-musunuru-among-five-indian-americans-named-to-times-100-most-influential-people-of-2026/"},
            {"name": "TIME Magazine", "url": "https://time.com/collection/100-most-influential-people-2026/"},
            {"name": "Global Indian", "url": "https://globalindian.com/indian-origin-leaders-on-time-100-most-influential-people-2026/"},
            {"name": "Livemint", "url": "https://www.livemint.com/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/c3/Sundar_Pichai_-_2023_%28cropped%29.jpg",
        "image_caption": "Sundar Pichai, CEO of Alphabet and Google, named to TIME's 2026 list of 100 most influential people.",
        "body": """When TIME released its annual list of the 100 most influential people earlier this month, the Indian American contingent numbered five. That is not, by itself, remarkable — Indians have appeared on the list before. What matters is the range.

Sundar Pichai, 53, was placed in the "titans" category for steering Google through the AI arms race. Neal Mohan, 52, made it for transforming YouTube from a video-sharing curiosity into America's most-watched streaming platform — bigger than Netflix on living-room screens. Zohran Mamdani, 34, the democratic socialist who became New York City's first Muslim mayor, was recognised during his first hundred days in office. Dr. Kiran Musunuru, a cardiologist and geneticist at the University of Pennsylvania, earned his spot for co-developing the first personalised CRISPR gene therapy for a six-month-old baby. And Vikas Khanna, the Amritsar-born chef whose New York restaurant Bungalow treats dinner as heritage storytelling, rounded out the group.

## Beyond the corner office

For years, the Indian American success narrative centred on a specific archetype: the IIT-educated engineer who climbed to the C-suite of a Fortune 500 company. Pichai and Mohan still fit that template — both hold engineering degrees, both run trillion-dollar platforms. But the 2026 list breaks the frame.

Mamdani, the son of the Ugandan-born political theorist Mahmood Mamdani, ran on a platform of universal childcare and city-owned grocery stores. Within a hundred days he had filled 100,000 potholes and rolled out 2,000 daycare seats in low-income neighbourhoods. "I know there are many who use 'socialist' as a dirty word," he told a rally in late April. "We will not be ashamed of using government to fight for the many, not simply the few." For a community often stereotyped as politically conservative and professionally narrowcast, his presence on the list is quietly significant.

Musunuru's work sits at the frontier of precision medicine. When baby KJ was born in August 2024 with a rare metabolic disease, Musunuru and his colleague Rebecca Ahrens-Nicklas designed, tested, and administered a bespoke CRISPR therapy in six months. "We're simply one link in a very long chain," Musunuru said at the TIME100 Health dinner in February, before adding pointedly: "Now is not the time to take the foot off the accelerator" — a remark widely interpreted as a rebuke of proposed federal research funding cuts.

## The cultural bridge

Khanna's inclusion underscores a subtler shift. AI pioneer Andrew Ng wrote Pichai's TIME profile; Eric Ripert, the French chef behind Le Bernardin, wrote Khanna's. Ripert's tribute focused less on culinary technique than on Khanna's ability to use food as a "bridge across cultures." For the millions of NRIs who have spent decades explaining their grandmother's recipes at American dinner tables, the recognition lands differently than another tech-CEO profile.

## What it signals

No Indian appeared on the 2025 list — the first blank in the magazine's 21-year history. Five names in 2026 is not a correction; it is an acceleration. TIME and Reliance have separately announced TIME100 Next India, a new franchise recognising 100 emerging Indian leaders, with a gala planned for Mumbai in December 2026.

The Indian diaspora, now 35 million strong across 200 countries, has been making lists for a while. What the 2026 TIME100 suggests is that the era of fitting neatly into a single category — tech, medicine, business — is over. The new map is wider, and considerably less predictable."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "NRI Deposits in India Fell $2 Billion in a Single Month. The Gulf Is the Reason.",
        "subheadline": "RBI data shows outstanding non-resident deposits dropped to $165.65 billion in March as the West Asia conflict rattled the corridor that still channels most of India's inward remittances.",
        "slug": make_slug("nri-deposits-drop-2-billion-march-west-asia-rbi"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The deposit decline hits hardest for Gulf-based NRIs — blue-collar and mid-tier workers who park savings in NRE and FCNR accounts as their primary financial link to India. A $2 billion single-month drop is a stress signal for millions of families on both sides.",
        "tags": ["nri", "diaspora", "nri-deposits", "rbi", "remittances", "west-asia", "gulf-nri", "banking"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Inshorts", "url": "https://inshorts.com/en/news/nri-deposits-fall-by-nearly--19-000-crore-in-march-amid-west-asia-crisis-1779540001470"},
            {"name": "IBEF", "url": "https://www.ibef.org/blogs/the-diaspora-effect-driving-bilateral-ties-and-remittances-to-india"},
            {"name": "TradingView / RBI Bulletin", "url": "https://www.tradingview.com/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/"}
        ]),
        "score_total": 75,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/8139313/pexels-photo-8139313.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Indian rupee banknotes — NRI deposits in India fell by roughly ₹19,000 crore in March 2026.",
        "body": """The Reserve Bank of India's latest bulletin delivered a number that deserves more attention than it received: outstanding non-resident Indian deposits fell by roughly $2 billion — over ₹19,000 crore — in a single month. At the end of March 2026, the total stood at $165.65 billion, down from $167.58 billion in February. For a pool of savings that had been growing almost monotonically for years, the reversal is striking.

The proximate cause is no mystery. The West Asia conflict, which escalated sharply in late 2025, has disrupted the economic rhythms of the Gulf states where roughly six million Indians live and work. The UAE alone hosts 3.57 million; Saudi Arabia another 2.46 million. These are not, for the most part, tech executives. They are construction workers, nurses, accountants, shopkeepers, and mid-level managers whose NRE and FCNR(B) accounts represent their primary financial tether to India.

## The full-year picture is worse

The monthly dip is part of a broader slide. Total NRI deposit inflows for FY2025-26 fell to $14.41 billion, down from $16.16 billion in FY2024-25 — a decline of nearly 11 per cent. This comes against the backdrop of India's overall inward remittances hitting a record $136 billion in FY25, which suggests the problem is not with the diaspora's earning power but with its willingness — or ability — to park money in Indian banks.

Several factors are at play. The Gulf conflict has created job uncertainty, prompting workers to hold more cash locally rather than remitting. Currency hedging has become more expensive as the rupee weakened. And some NRIs report that the spread between Indian deposit rates and local savings options in the UAE and Saudi Arabia has narrowed enough to erode the incentive.

## FCNR(B) — the canary

The most closely watched category is FCNR(B) — Foreign Currency Non-Resident deposits denominated in dollars, pounds, or euros. These accounts let NRIs earn interest in foreign currency while keeping money in an Indian bank, with full repatriability. The RBI has historically raised FCNR(B) rate caps during currency crises to attract dollar inflows and defend the rupee. It did so again in late 2025, hiking the ceiling by 150 basis points.

Market analysts remain sceptical that the rate hike alone will reverse the trend. "The issue is not the interest rate," one Mumbai-based treasury head told The Hindu BusinessLine. "It's the risk premium. When your employer might not renew your contract because of regional instability, you don't lock money away for three years."

## What it means for families

The deposit decline is ultimately a story about millions of individual households. A construction supervisor in Dubai who would normally wire ₹50,000 a month into his NRE account for his children's school fees in Kerala is instead keeping the money liquid in a local account. A nurse in Riyadh who had been building an FCNR(B) corpus for a flat in Hyderabad is pausing contributions.

India's remittance economy — which covers 47 per cent of the country's merchandise trade deficit — depends on this invisible infrastructure of monthly transfers and fixed deposits. When the pipeline slows, the effects ripple through real estate markets in tier-two cities, school fee payments in southern states, and the household budgets of families who have built their financial architecture around a steady stream from abroad.

## The policy gap

New Delhi has spent considerable energy courting the diaspora through events like Pravasi Bharatiya Divas and investment schemes like the India Development Foundation of Overseas Indians. What it has spent less energy on is building a safety net for the Gulf-based NRI workforce that remains the backbone of India's remittance economy. The $2 billion March decline is a reminder that this corridor — older, less glamorous, and far less visible than Silicon Valley — still carries most of the weight."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Indian Diaspora Earns $730 Billion a Year. A New Report Asks Why India Isn't Benefiting More.",
        "subheadline": "Indiaspora's 'Partners in Progress' argues that the world's largest diaspora has evolved far beyond remittances — but structural barriers still prevent deeper engagement with India's economy.",
        "slug": make_slug("indiaspora-partners-progress-report-730-billion-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "For NRIs who have tried to invest in India, start a business, or even vote in Indian elections, the report validates a long-standing frustration: the desire to engage is there, but the institutional plumbing to channel it remains inadequate.",
        "tags": ["nri", "diaspora", "indiaspora", "remittances", "india-investment", "philanthropy", "india-at-100"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "GlobeNewsWire / Indiaspora", "url": "https://www.globenewswire.com/news-release/2026/03/23/indiaspora-releases-groundbreaking-report"},
            {"name": "IBEF", "url": "https://www.ibef.org/blogs/the-diaspora-effect-driving-bilateral-ties-and-remittances-to-india"},
            {"name": "Indiaspora", "url": "https://www.indiaspora.org"},
            {"name": "YouTube / India Abroad", "url": "https://www.youtube.com/@IndiaAbroad"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/8770950/pexels-photo-8770950.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "The Indian diaspora spans 200 countries and 35 million people, now earning an estimated $730 billion annually.",
        "body": """Here is a number that should reframe how India thinks about its diaspora: $730 billion. That is the estimated combined annual income of the 35 million people of Indian heritage living in more than 200 countries, according to a report released in March by Indiaspora, the San Francisco-based diaspora leadership nonprofit. To put it in perspective, that figure is larger than the GDP of Switzerland.

The report, titled *India and its Diaspora: Partners in Progress*, is not the first attempt to quantify the diaspora's economic heft. Indiaspora previously published impact reports with Boston Consulting Group in 2024 and 2025, covering Indian Americans and the Indian community in the UAE respectively. But *Partners in Progress* is the first to take a global view and, more importantly, to focus on what is not working.

## Beyond the remittance story

India received $136 billion in remittances in FY25 — a record, and enough to cover 47 per cent of the country's merchandise trade deficit. That number is routinely cited as proof of the diaspora's contribution. The report argues it is actually evidence of underperformance.

Remittances are, by definition, one-directional cash transfers. They support household consumption in India but do not create enterprises, build institutions, or transfer knowledge. The diaspora's potential contribution, the report suggests, lies in investment, technology partnerships, startup funding, philanthropic institution-building, and the kind of informal diplomatic capital that comes from having Indian-origin leaders running Alphabet, Microsoft, IBM, Adobe, YouTube, and — as of 2026 — New York City.

MR Rangaswami, Indiaspora's founder, frames it in terms of India's own ambition. "In 1991, India opened its doors to the world. Today, the world is knocking on India's door," he writes. "At this inflection point, India has the opportunity to unlock the power of a 35-million-strong diaspora, bringing capital, capability, and credibility."

## The barriers

The report draws on insights from more than 200 diaspora leaders across 24 countries and finds a recurring theme: desire without infrastructure. NRIs want to invest in Indian startups but find the regulatory process opaque. They want to contribute to educational institutions but encounter bureaucratic inertia. They want to vote in Indian elections but cannot do so from abroad without flying home. They want to set up philanthropic foundations but face tax structures that penalise cross-border giving.

These are not new complaints. What is new is the scale at which they are being articulated. The diaspora that once engaged with India primarily through annual visits and wire transfers now includes venture capitalists, university presidents, cabinet-level politicians, and Fortune 100 CEOs. Their capacity to contribute has outgrown the channels available to them.

## What the report recommends

*Partners in Progress* offers a set of recommendations aimed at both Indian policymakers and diaspora leaders. On the Indian side, it calls for streamlined investment regulations, dedicated diaspora engagement offices at the state level, and digital platforms that make it easier for NRIs to participate in India's startup ecosystem. On the diaspora side, it urges the creation of more structured mentorship networks, cross-border professional associations, and a shift from individual philanthropy to institutional giving.

The report also highlights the importance of cultural engagement — not as a soft add-on but as a strategic asset. The Indian diaspora's role in spreading yoga, Bollywood, Indian cuisine, and literary culture abroad has measurably increased India's soft power. But that cultural capital remains largely uncoordinated, driven by individual enthusiasm rather than institutional strategy.

## The India@100 frame

The timing is deliberate. India has set itself the goal of becoming a developed nation by 2047 — its centenary of independence — under the banner of "India@100" or "Viksit Bharat." The report positions the diaspora as a critical, underutilised asset in that journey.

Whether New Delhi responds with concrete policy changes or treats this as another well-intentioned document to be filed alongside previous diaspora reports remains to be seen. The diaspora, for its part, has stopped waiting for permission. Indian-origin founders raised more venture capital in the US than any other immigrant group in 2025. Indian-origin philanthropists gave more than $8.8 million through India Giving Day alone. And five Indian Americans just made TIME's list of the 100 most influential people in the world.

The capacity is there. The question, as it has been for thirty years, is whether the plumbing will catch up."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
