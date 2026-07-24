#!/usr/bin/env python3
"""NRI World Writer — 2026-06-15 batch"""

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


# ─────────────────────────────────────────────────────────────────────
# ARTICLE 1: Shrey Parikh Wins 2026 Scripps National Spelling Bee
# ─────────────────────────────────────────────────────────────────────

art1_body = """Shrey Parikh stood at the microphone inside DAR Constitution Hall on the evening of May 28, a buzzer in his hand and ninety seconds on the clock. By the time the timer ran out, the fourteen-year-old from Rancho Cucamonga, California, had correctly spelled thirty-two words — shattering the previous spell-off record of twenty-nine set in 2024 — and claimed the title of champion of the 101st Scripps National Spelling Bee.

His winning word was "bromocriptine," a polypeptide alkaloid derived from ergot that mimics the activity of dopamine. He spelled it cleanly. The crowd in Washington erupted.

## A Pattern Two Decades in the Making

Parikh's victory extends what has become one of the most quietly remarkable streaks in American academic competition. Indian-American contestants have dominated the Scripps Bee for more than two decades, winning the championship in the vast majority of recent years. The 2026 final was, characteristically, an all-Indian-American affair: facing Parikh in the spell-off was twelve-year-old Ishaan Gupta from Jersey City, New Jersey, who spelled twenty-five words correctly in his own attempt — a total that would have won almost any other year.

The final reached the spell-off format — only the third in the competition's history — after conventional dictionary rounds failed to separate the last two spellers. Under the protocol, one contestant was sequestered in an isolated room wearing noise-cancelling headphones while the other spelled. Both faced the identical word list in the same sequence.

## The Long Road from Day Creek Intermediate

Parikh's journey to the championship followed the classic arc of a competitive speller who treats the Bee as a multi-year campaign. He first appeared on the national stage in 2022, tying for eighty-ninth place. He returned in 2024 and finished tied for third, behind that year's champion Faizan Zaki, who went on to win again in 2025. This time, Parikh came back with the precision and speed of a veteran.

An eighth-grader at Day Creek Intermediate School in San Bernardino County, Parikh's interests range well beyond language. He plays percussion in his school band — snare drum, bass drum, timpani, toms, triangle, glockenspiel, and marimba. He qualified for the California state Mathcounts competition. He plays tennis, reads voraciously, and visits India frequently to spend time with his grandparents.

His prize package included $52,500 in cash, reference works from Encyclopaedia Britannica and Merriam-Webster, a custom trophy, and $1,000 in Delta Air Lines flight credits.

## Why the Diaspora Keeps Winning

The Indian-American dominance of the Spelling Bee has spawned its own cottage industry of analysis. The most common explanation — that South Asian families prize academic rigour — is true but insufficient. What sets the diaspora apart is an entire ecosystem: the South Asian Spelling Bee circuit, regional competitions organised by Indian community groups, and a deep bench of coaches and study networks that treat competitive spelling with the same seriousness other communities reserve for club soccer or debate.

For many diaspora families, the Bee has become a rite of passage, a way to channel the particular intensity of immigrant aspiration into something concrete and legible to American institutions. The kids who make it to the national stage have typically spent years drilling through obscure etymologies — Greek, Latin, French, German, Arabic — building a working knowledge of linguistic roots that most adults will never possess.

The competition also feeds on itself. When Nupur Lala won in 1999, she was a novelty. When Anurag Kashyap won in 2005, it was a trend. By the time the eight co-champions of 2019 included seven Indian-American spellers, it had become the expectation. Each champion produces the next generation of aspirants.

## The Road Ahead

Parikh, who turns fifteen later this year, has aged out of the competition. The 2027 Bee will proceed without its reigning champion, as the rules cap eligibility at eighth grade. But in Ishaan Gupta — younger, formidable, and now carrying the sting of finishing second — the pipeline has already produced its next contender.

For the Indian-American community, the annual Bee victory has become something close to tradition: a moment of collective pride that cuts across regional, linguistic, and generational lines within the diaspora. The kid from Rancho Cucamonga who spelled "bromocriptine" without flinching is, for a few days at least, everyone's nephew."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Thirty-Two Words in Ninety Seconds: Shrey Parikh Wins the 2026 Scripps National Spelling Bee",
    "subheadline": "The fourteen-year-old from Rancho Cucamonga shattered the spell-off record and extended Indian Americans' two-decade dominance of the country's premier academic competition.",
    "slug": make_slug("shrey-parikh-scripps-spelling-bee-champion-indian-american"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "Indian-American community has dominated the Spelling Bee for two decades; the victory reflects the diaspora's deep investment in academic competition and a self-reinforcing ecosystem of coaching, regional circuits, and family aspiration.",
    "tags": ["nri", "diaspora", "indian-american", "spelling-bee", "education", "achievement"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Dainik Jagran English", "url": "https://english.dainikjagranmpcg.com"},
        {"name": "Madhyamam Online", "url": "https://madhyamamonline.com"},
        {"name": "LatestLY / IANS", "url": "https://www.latestly.com"},
        {"name": "TV Insider", "url": "https://www.tvinsider.com"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/Scripps_National_Spelling_Bee_%2855301276503%29.jpg/1280px-Scripps_National_Spelling_Bee_%2855301276503%29.jpg",
    "image_caption": "A contestant at the Scripps National Spelling Bee competition in Washington, D.C.",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body
}


# ─────────────────────────────────────────────────────────────────────
# ARTICLE 2: India's Record Remittances
# ─────────────────────────────────────────────────────────────────────

art2_body = """India received $135.46 billion in inward remittances in the fiscal year ending March 2025 — a 14 per cent jump over the previous year and the largest single-country remittance inflow ever recorded. The figure, confirmed by Reserve Bank of India data and cited in the International Organization for Migration's World Migration Report 2026, cements India's position as the world's top remittance destination for over a decade. Mexico, the next-largest recipient, trailed at $68 billion. China came in third at $48 billion.

The money is not slowing down. SBI Research projected in March 2026 that India would receive between $137 billion and $140 billion in FY26, based on $73 billion already counted in the first half of the fiscal year alone. The third quarter of FY26 — October through December 2025 — set a new quarterly record of $37.8 billion, up 5.1 per cent year-on-year.

## Where the Money Comes From

The geography of remittances has been quietly shifting. The United States, United Kingdom, and Singapore together now account for 45 per cent of total inflows — a growing share that reflects the upward mobility of India's skilled diaspora in high-income economies. The traditional Gulf corridor, once the backbone of India's remittance pipeline, continues to shrink in relative terms, pressured by fluctuating crude oil prices and Saudisation policies that have pushed some Indian workers out of the labour market.

This tilt toward developed-world sources matters. Remittances from the Gulf tend to come from blue-collar workers sending small, frequent transfers for family maintenance. Remittances from the US and UK increasingly include withdrawals from NRE and NRO deposit accounts, investment repatriations, and salary transfers from white-collar professionals earning in dollars and pounds. The per-capita remittance from a software engineer in Seattle is structurally different from that of a construction worker in Riyadh — in size, in regularity, and in sensitivity to exchange rates.

## The Macro Cushion

What makes these numbers matter beyond the individual families who receive them is their role in India's external balance sheet. In FY25, remittances financed roughly 47 per cent of India's merchandise trade deficit of $287 billion. They exceeded gross inward foreign direct investment. They dwarfed net FPI flows, which turned negative as foreign portfolio investors pulled $16.5 billion out of Indian equities.

In a year when India's net FDI sank to barely $1 billion and portfolio capital proved fickle, diaspora dollars were the ballast. The RBI has explicitly noted that remittances have "consistently exceeded gross inward FDI flows," a polite way of saying that the most reliable source of hard currency flowing into the country is not sovereign wealth funds or Goldman Sachs — it is the monthly SWIFT transfer from a nurse in Birmingham or a data scientist in New Jersey.

## What NRIs Should Know

For individual NRIs, the macro picture intersects with personal finance at several points. The rupee's relative weakness against the dollar — hovering around ₹84 — makes remittances more valuable in rupee terms, which partly explains why investment in Indian real estate by NRIs has been climbing. NRI participation now accounts for an estimated 15 to 25 per cent of investments in newly launched residential developments across Mumbai, Pune, Bengaluru, and Gurugram.

Indian banks have noticed. A rate war for NRI deposits broke out earlier this year, with lenders offering up to 7.1 per cent on FCNR dollar deposits — a spread engineered in part by the RBI to keep the capital flowing in. The GIFT City IFSC in Gujarat, which approved its first Foreign Family Investment Fund in April 2026, is positioning itself as a wealth-management hub specifically for NRI capital.

Meanwhile, India's remittance costs remain among the lowest globally. An RBI paper noted that India was among the cheapest countries in the world to send $200 to, though costs vary by corridor: the US-India route is highly competitive thanks to fintech players like Wise, Remitly, and Instarem, while Gulf-India transfers remain more sensitive to oil-price-driven fee fluctuations.

## The Bigger Story

The remittance record is, in one sense, a story about money. In another, it is a census of connection — a quarterly measurement of how tightly thirty-five million overseas Indians remain tethered to the country they left. Every wire transfer is a decision: to maintain a home, fund a parent's medical bill, invest in a flat in Noida, or simply keep an NRE account topped up against the day of return.

For India, the diaspora dollar has become too large to take for granted. It is not aid. It is not charity. It is the aggregate of millions of private, emotional, and economic calculations made by people living between two countries — and it now bankrolls nearly half the trade deficit of the world's fifth-largest economy."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "India's Diaspora Dollars Hit $135 Billion — and They Are the Only Foreign Capital That Never Flinches",
    "subheadline": "Record remittances in FY25 financed nearly half of India's trade deficit. With $140 billion projected for FY26, the NRI wire transfer has quietly become India's most reliable external lifeline.",
    "slug": make_slug("india-remittance-record-135-billion-nri-diaspora-dollars"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "NRI remittances are the largest single source of hard currency flowing into India, outpacing FDI and FPI; the shift from Gulf blue-collar to US/UK white-collar sources reflects the diaspora's upward mobility; individual NRIs benefit from a weak rupee and competitive deposit rates.",
    "tags": ["nri", "remittances", "diaspora", "economy", "india", "finance"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reserve Bank of India / Trading Economics", "url": "https://tradingeconomics.com/india/remittances"},
        {"name": "SBI Research", "url": "https://thehindubusinessline.com"},
        {"name": "IBEF / Economic Survey 2025-26", "url": "https://ibef.org"},
        {"name": "Press Insider / RBI Data", "url": "https://pressinsider.com"},
        {"name": "Livemint", "url": "https://www.livemint.com"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/5476028/pexels-photo-5476028.jpeg",
    "image_caption": "Indian rupee notes and coins — remittances from the diaspora now constitute India's most stable source of foreign currency",
    "image_attribution": "Pexels",
    "body": art2_body
}


# ─────────────────────────────────────────────────────────────────────
# ARTICLE 3: India's Celebrity Chef Restaurant Brands Hit America
# ─────────────────────────────────────────────────────────────────────

art3_body = """There are now more than 40,000 Indian restaurants in the United States, a $15 billion market that has grown almost entirely without a unifying trade body, a dominant chain, or a single chef whose name carries the weight of a Gordon Ramsay or a David Chang. That is beginning to change.

In the past year, three Indian restaurant brands with serious credentials back home have opened their first American outposts, each with a different theory about what the US market wants from Indian food. Together, they represent something the diaspora food scene has not had before: branded, scalable concepts backed by established operators, arriving with coast-to-coast ambitions.

## The Three Arrivals

**The Yellow Chilli by Sanjeev Kapoor** landed in Santa Clara, California — the heart of Silicon Valley's Indian belt. Kapoor is perhaps the most recognisable chef in India, a household name through his long-running television show *Khana Khazana* and a portfolio of restaurants across India, the UAE, and Oman. The Yellow Chilli positions itself as a casual-dining "gastronomic tour of India," with menu highlights including Lalla Mussa Dal — black and green lentils cooked overnight with cream and ghee — and Puran Singh da Tariwala Murgh, a chicken curry inspired by a dhaba on the Ambala-Delhi highway. Prices stay under $30 a head. The location, at Monticello Apartment Homes developed by Irvine Company, is a bet on the everyday diaspora diner, not the expense-account crowd.

**Farzi Café by Zorawar Kalra** chose Bellevue, Washington, another Pacific Northwest tech hub dense with South Asian professionals. Kalra, the son of the legendary Jiggs Kalra — known as the "czar of Indian cuisine" — runs Massive Restaurants, overseeing more than two dozen establishments across eleven countries. Farzi Café's London outpost is listed in the Michelin Guide. The Bellevue location is the brand's US beachhead, with plans to expand coast to coast. The concept leans toward molecular gastronomy and reinvention — Indian food dressed up in European fine-dining technique.

**Rishtedar**, meanwhile, took a completely different path to America. The fine-dining brand was born not in India but in Santiago, Chile, founded by Vikram Thadani, who was born to Indian parents in South America. Its first US location opened in Wynwood, Miami's trendy arts district. The name means "family" in Hindi, and the concept aims to introduce Indian cuisine to audiences with no prior relationship to it — through samosas, tandoori chicken with tikka sauce, and shrimp with curry, all served in a space designed to evoke Indian colour and texture.

## The Market They Are Walking Into

The 40,000-plus Indian restaurants already operating in the US are overwhelmingly independent, family-run, and fragmented. There is no dominant chain equivalent to Chipotle or Panda Express. The sector has no unified trade journal, no professional directory, and no structured supply chain connecting Indian FMCG brands to operators in the American market.

A new initiative, the Global Indian HoReCa Journal — backed by hi-india Publication, a thirty-year-old diaspora media institution with 68,000 newsletter subscribers — is attempting to fill that gap by creating a trade media platform connecting India's hospitality industry with the US Indian restaurant ecosystem. Whether that infrastructure materialises will determine, in part, how far the branded chains can go.

## Why Now?

The timing reflects several converging forces. Indian Americans are now the largest Asian-alone ethnic group in the United States, at nearly 4.4 million — a 55 per cent increase over the past decade. Many arrived through the tech industry and are concentrated in exactly the metros where these restaurants are opening: the Bay Area, the Seattle corridor, and increasingly the Sun Belt.

But the real ambition of operators like Kalra and Kapoor is not to serve the diaspora — it is to go beyond it. Indian food in America has long been stuck in the "ethnic" category, associated with cheap lunch buffets and fluorescent-lit strip-mall storefronts. The new entrants are betting that the cuisine is ready for the same mainstreaming that happened to Japanese food (via sushi chains), Mexican food (via Chipotle), and Thai food (via Sweetgreen-adjacent fast-casual). Kalra has said explicitly that his mission is to "make Indian cuisine a mainstream cuisine across the US."

Whether the market agrees is another matter. The US restaurant landscape is brutally competitive, and several Indian concepts have struggled with the gap between the diaspora market — which demands authenticity, regional specificity, and value — and the broader American market, which gravitates toward simplified menus, consistent branding, and Instagram-friendly plating.

## What It Means for the Diaspora

For Indian Americans, the arrival of recognised brands from back home is both exciting and loaded. A Sanjeev Kapoor restaurant in Santa Clara carries an emotional charge that a random new tandoori place does not — it connects the diaspora diner to a shared cultural reference point, a face they grew up watching on television. At the same time, the question of who gets to define "Indian food in America" has always been contested within the community, and the entry of branded chains from India inevitably raises questions about whether local, independent operators will be squeezed.

For now, the market is large enough to absorb everyone. Forty thousand restaurants serving a $15 billion market, with no dominant player and a cuisine that most Americans still associate primarily with butter chicken and naan, leaves plenty of room. The question is not whether Indian food will go mainstream in America. It is who will be serving it when it does."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "Forty Thousand Restaurants and No Chain: India's Celebrity Chefs Are Finally Coming for the American Market",
    "subheadline": "Sanjeev Kapoor in Santa Clara, Zorawar Kalra in Bellevue, Rishtedar in Miami — three branded Indian restaurant concepts have opened their first US outposts, betting that the country's $15 billion Indian food market is ready for its Chipotle moment.",
    "slug": make_slug("indian-celebrity-chef-restaurants-us-market-yellow-chilli-farzi"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "The Indian restaurant market in the US has been built entirely by diaspora independents; the arrival of branded chains from India connects NRI diners to cultural touchstones from home while raising questions about mainstreaming vs. authenticity.",
    "tags": ["nri", "diaspora", "restaurants", "food", "indian-american", "business"],
    "urgency": "low",
    "sources": json.dumps([
        {"name": "Restaurant Business Online", "url": "https://www.restaurantbusinessonline.com"},
        {"name": "The Indian Eye", "url": "https://theindianeye.com"},
        {"name": "LinkedIn / Global Indian HoReCa Journal", "url": "https://linkedin.com"},
        {"name": "Irvine Company Retail", "url": "https://irvinecompanyretail.com"}
    ]),
    "score_total": 72,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/941869/pexels-photo-941869.jpeg",
    "image_caption": "An array of Indian dishes — the US Indian restaurant market is now valued at $15 billion",
    "image_attribution": "Pexels",
    "body": art3_body
}


# ─────────────────────────────────────────────────────────────────────
# INSERT ALL
# ─────────────────────────────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
