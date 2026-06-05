#!/usr/bin/env python3
"""NRI World Writer — 2026-06-05 00:00 UTC run"""

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


# ─────────────────────────────────────────────
# ARTICLE 1: Kuwait Airport Drone Strike
# ─────────────────────────────────────────────
article1_body = """An Indian national was killed on Wednesday when Iranian drones slammed into Kuwait International Airport's newly reopened Terminal 1, the Indian Embassy in Kuwait confirmed. Sixty-three others were wounded, some critically, in what US Central Command called a "deliberate, calculated and unjustified attack" on a civilian facility.

The strike hit a passenger building that had reopened only on Monday after months of closure prompted by the wider US-Iran conflict, which erupted on February 28 with American and Israeli strikes on Iranian targets. Surveillance footage released by Kuwait's Directorate General of Civil Aviation showed a delta-wing drone — consistent with Iran's Shahed series, the same design Russia deploys in Ukraine — slamming directly into the terminal.

## A Community in the Crosshairs

For the roughly 900,000 Indians living in Kuwait — and the estimated 8.9 million across all six Gulf Cooperation Council states — the attack was a visceral reminder of how quickly the ground can shift beneath a diaspora that has built its life in someone else's conflict zone.

Since the war began in late February, the Indian Ministry of External Affairs has been running a Special Control Room to monitor the welfare of nationals across the Gulf. By early March, more than 52,000 Indians had already been evacuated from the region on commercial and non-scheduled flights, with 32,107 travelling on Indian carriers. The ministry has issued repeated advisories urging Indian nationals to follow local authority guidelines and stay in contact with their nearest embassy or consulate.

Kuwait's response was swift and furious. The Foreign Ministry said the country would "neither accept nor tolerate" the attacks and expelled two Iranian diplomats. Kuwait Airways rerouted flights to an undamaged terminal before partially resuming operations.

## The Gulf's Indian Backbone

The Indian diaspora in the Gulf is not a marginal presence. It is the economic backbone of several nations. Indians constitute the single largest expatriate community in Kuwait, the UAE, Qatar and Bahrain, working across construction, healthcare, technology, retail and financial services. Their remittances — more than $50 billion annually from the Gulf alone — account for over half of all money sent back to India, making them a pillar of India's foreign exchange reserves.

That economic centrality, however, does not translate into political protection. Gulf labour laws offer limited safeguards for migrant workers, and in a conflict zone, foreign nationals are often the last to be evacuated and the first to be caught in the crossfire.

Iran's paramilitary Revolutionary Guard denied targeting the airport, claiming instead that a US-made interceptor damaged the terminal — a version US Central Command flatly rejected. Kuwait's Defence Ministry said it destroyed over a dozen Iranian missiles and a similar number of drones during the attack.

## What This Means for the Diaspora

The incident will sharpen an already uncomfortable conversation among Gulf-based Indians about contingency planning. Many have built entire careers and raised families in Kuwait, the UAE and Saudi Arabia without ever confronting the possibility that their adopted home could become a war zone. The February escalation and its aftermath have upended that assumption.

India's embassy in Kuwait has its 24/7 helpline operational, and the MEA's control room in Delhi continues to field calls from anxious families back home. For the families of the dead and wounded at Kuwait International Airport, however, the machinery of consular protection arrived a step too late.

The Gulf diaspora's compact with its host nations has always been transactional — labour for wages, skills for residency. Wednesday's drone strike was a brutal reminder that the transaction does not include a guarantee of safety."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "An Indian Was Killed at Kuwait Airport. For 8.9 Million Gulf Indians, the War Just Got Personal.",
    "subheadline": "Iranian drones struck the newly reopened terminal, killing one Indian national and wounding 63 others. India has already evacuated 52,000 from the region.",
    "slug": make_slug("indian-killed-kuwait-airport-iranian-drone-gulf-diaspora"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "The 8.9 million Indians living in the Gulf are caught between the economic necessity of staying and the escalating danger of the US-Iran war. This strike brings the conflict directly to the diaspora's doorstep.",
    "tags": ["nri", "diaspora", "gulf", "kuwait", "iran", "safety", "evacuation"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/world/middle-east/one-killed-iranian-attack-kuwait-airport-terminal-damaged-2026-06-04/"},
        {"name": "Audacy / AP", "url": "https://www.audacy.com/national-news/kuwait-says-iranian-drones-hit-airport-killed-1"},
        {"name": "India MEA", "url": "https://www.mea.gov.in/press-releases.htm?dtl/40846/Special_Control_Room_in_MEA"}
    ]),
    "score_total": 88,
    "status": "published",
    "published_at": now,
    "is_editorial": False,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/11/Kuwait_International_Airport.jpg/1280px-Kuwait_International_Airport.jpg",
    "image_caption": "Kuwait International Airport terminal building before the June 2026 drone strike",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body
}


# ─────────────────────────────────────────────
# ARTICLE 2: India-US Trade Deal 99% Done
# ─────────────────────────────────────────────
article2_body = """The India-US Bilateral Trade Agreement is "99% there," US Ambassador to India Sergio Gor declared on Tuesday, as a high-level American delegation wrapped up four days of face-to-face negotiations in New Delhi. For the 5.2 million Indian Americans who have spent decades building the human bridge between the two economies, the news landed as both vindication and relief.

Ambassador Gor, speaking on the sidelines of CITI's 2026 India Conference in Mumbai, said the remaining one per cent consists of "technical legal phrasing and implementation timelines" — the kind of granular drafting that signals a deal is functionally done. He praised India's "incredible negotiators" and called the agreement a "win-win situation."

## From $20 Billion to $220 Billion

The numbers tell a story the diaspora already knows. Bilateral trade in goods and services has rocketed from $20 billion two decades ago to over $220 billion today. A significant slice of that growth was seeded by Indian Americans who founded companies, staffed engineering teams, ran hospital systems and built supply chains that now stretch between Dallas and Delhi, San Jose and Bengaluru.

Sixteen Indian-origin CEOs run Fortune 500 companies. Together, their firms employ 2.7 million Americans and generate nearly $1 trillion in annual revenue. Indians have co-founded 72 of America's 648 unicorns. The community pays an estimated 5–6 per cent of all US federal income tax despite comprising barely 1.6 per cent of the population.

The trade deal, in other words, did not emerge from a diplomatic vacuum. It was made possible by the economic infrastructure the diaspora built over three decades.

## What Is in the Deal

The US delegation, led by Chief Negotiator Brendan Lynch, arrived in New Delhi on June 1 for talks with India's Additional Secretary for Commerce, Darpan Jain. The agenda covered market access, non-tariff barriers, customs and trade facilitation, investment promotion and — notably — "economic security alignment," a phrase that nods toward the growing strategic convergence between the two countries on China, technology exports and critical mineral supply chains.

Both sides are racing against a July 9 deadline, when the 90-day suspension of tariffs announced on April 2 expires. If no interim agreement is signed by then, tariff structures revert to their pre-pause levels — a prospect that would hit Indian IT services exporters, pharmaceutical firms and agricultural producers disproportionately.

## The NRI Stake

For Indian Americans, the agreement's fine print matters more than its headlines. Trade facilitation provisions could smooth the customs nightmare that small NRI importers face when shipping goods between the two countries. Investment promotion clauses may open doors for diaspora entrepreneurs looking to set up operations in India's growing manufacturing and fintech sectors. And economic security alignment could reinforce the institutional connective tissue that makes it easier for professionals to move between the two economies.

The deal also arrives at a fraught moment in US-India relations. President Trump's tariff policies have rattled Indian exporters, and the Carnegie Endowment's 2026 survey found that 55 per cent of Indian Americans disapprove of Trump's handling of the bilateral relationship. A signed agreement would go some way toward reassuring the community that the economic partnership they helped build is not being sacrificed to domestic political calculations.

India has pushed back firmly on US demands to lower duties on agricultural and dairy products and to grant market access for genetically modified crops — issues that are politically sensitive in a country where millions of farmers vote. Indian negotiators have also resisted broad-based access for the US dairy sector, citing food safety and public health concerns.

## What Comes Next

Ambassador Gor is scheduled to meet Union Commerce Minister Piyush Goyal in Delhi to finalize the last details. If both sides close the gap before July 9, the interim agreement will be the fastest major trade deal India has negotiated — a point Gor made explicitly, contrasting the 18-month India-US timeline with the years it took for India's pact with the European Union.

For the diaspora, the deal is less about tariff schedules and more about validation. Twenty years of building, hiring, investing and advocating between two countries may finally have a formal framework to show for it."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "The India-US Trade Deal Is '99% Done.' The Diaspora Built the Other 99 Per Cent.",
    "subheadline": "Ambassador Gor says only technical legal language remains. Bilateral trade has grown from $20 billion to $220 billion — much of it on the backs of 5.2 million Indian Americans.",
    "slug": make_slug("india-us-trade-deal-99-percent-diaspora-built-bridgehead"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "The India-US economic relationship was built by the diaspora over three decades. The trade deal formalizes what Indian Americans already made real — and its fine print on investment, trade facilitation and economic security alignment will directly affect NRI entrepreneurs and professionals.",
    "tags": ["nri", "diaspora", "trade", "india-us", "economy", "bilateral"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/06/04/last-1-being-finalized-gor-on-india-us-trade-agreement/"},
        {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/06/04/india-and-us-set-for-crucial-trade-talks-in-new-delhi/"},
        {"name": "AInvest", "url": "https://www.ainvest.com/news/india-us-engage-on-forced-labor-excess-capacity-concerns/"},
        {"name": "Indiaspora / BCG Report", "url": "https://www.indiaspora.org/impact-report"}
    ]),
    "score_total": 82,
    "status": "published",
    "published_at": now,
    "is_editorial": False,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/48/President_Trump_and_the_First_Lady_in_India_%2849588158612%29.jpg/1280px-President_Trump_and_the_First_Lady_in_India_%2849588158612%29.jpg",
    "image_caption": "President Trump with Indian officials during his visit to India",
    "image_attribution": "Wikimedia Commons",
    "body": article2_body
}


# ─────────────────────────────────────────────
# ARTICLE 3: Carnegie Survey — Discrimination
# ─────────────────────────────────────────────
article3_body = """One in every two Indian Americans has experienced discrimination in the past year. Nearly half encounter racist social media posts targeting Indians "very or somewhat often." One in four has been called a slur since the start of 2025. These are not anecdotal impressions. They are the findings of the 2026 Indian American Attitudes Survey, a nationally representative study of 1,000 adults conducted by the Carnegie Endowment for International Peace in partnership with YouGov.

The survey, the third wave of the IAAS following editions in 2020 and 2024, paints the most comprehensive portrait yet of a community caught between its own success story and a rising tide of hostility.

## The Numbers That Sting

Discrimination based on skin colour is the most common form of bias reported: 30 per cent of respondents said they had been discriminated against because of the colour of their skin. Eighteen per cent reported discrimination based on gender, another 18 per cent based on religion. Sixteen per cent said their Indian heritage was the trigger.

Among religious groups, Muslims reported the highest rate of religious discrimination at 39 per cent, followed by Hindus at 18 per cent and Christians at 15 per cent. Five per cent of respondents — a small but non-trivial share — said they had faced caste-based discrimination.

The online dimension is particularly stark. In a test included in the survey, respondents were shown a real tweet that explicitly targeted Indian Americans. Forty-eight per cent said they encounter such content very or somewhat often. Anti-South Asian slurs in extremist online spaces doubled between 2023 and 2024, from roughly 23,000 to over 46,000, according to a separate report by Stop AAPI Hate. The Carnegie survey confirms that this wave has not receded.

## A Community Shifting Its Political Feet

The discrimination data sits alongside an equally striking political portrait. Indian Americans remain disproportionately Democratic — 46 per cent identify with the party — but that share has dropped from 52 per cent in 2020. Republican identification has crept up to 19 per cent, and the independent share has risen to nearly a third of the community.

Seventy-one per cent disapprove of President Trump's job performance, with more than half saying they "strongly disapprove." His handling of US-India relations draws 55 per cent disapproval. But the shift is real: in a hypothetical rerun of the 2024 election, Democratic support remains about ten points below its 2020 high-water mark.

The community's ideological centre of gravity is moderate. About a third of respondents place themselves in the middle of the spectrum. Only one in five identifies as conservative. Indian Americans are more Democratic-leaning than the American electorate as a whole, but the direction of travel is unmistakable.

## The Mamdani Factor

One data point stands out for its sheer brightness amid the gloom. Sixty-eight per cent of respondents expressed enthusiasm about Zohran Mamdani's election as Mayor of New York City — the first South Asian and first Muslim to hold the office. Mamdani, the son of filmmaker Mira Nair and Columbia professor Mahmood Mamdani, was born in Uganda to a family of Indian descent and was sworn in on January 1, 2026.

His victory appears to have resonated as a counterweight to the discrimination data — proof that political representation is possible even as the community navigates hostility.

## The Identity Paradox

The Indian American community occupies a peculiar position in America's racial landscape. It is, by several measures, the most economically successful immigrant group in the country: the highest median household income, the highest educational attainment, a vastly disproportionate presence in Fortune 500 boardrooms, Silicon Valley startups and the medical profession.

And yet half of its members report being discriminated against. The "model minority" framework, which the community has at various points embraced, resisted and simply endured, offers no real protection against a slur hurled in a parking lot or a social media post that goes viral.

The Carnegie survey does not resolve this paradox. It simply documents it, in granular and uncomfortable detail. The community's response — whether it leans further into political engagement, retreats into economic insularity, or does something entirely unpredictable — will shape the next chapter of the Indian American story."""

article3 = {
    "id": str(uuid.uuid4()),
    "headline": "Half of All Indian Americans Report Discrimination. The Carnegie Survey Puts a Number on What the Community Already Knew.",
    "subheadline": "The 2026 Indian American Attitudes Survey finds that one in four has been called a slur, 48 per cent regularly encounter racist posts online, and the community's Democratic lean is softening — but not breaking.",
    "slug": make_slug("carnegie-survey-indian-americans-discrimination-2026-political-shift"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "The Carnegie IAAS survey is the definitive portrait of where Indian Americans stand in 2026 — navigating discrimination, political realignment and an identity paradox that success alone cannot resolve.",
    "tags": ["nri", "diaspora", "discrimination", "indian-american", "politics", "survey", "carnegie"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Carnegie Endowment for International Peace", "url": "https://carnegieendowment.org/research/2026/02/indian-americans-in-a-time-of-turbulence-2026-survey-results"},
        {"name": "GG2.net", "url": "https://www.gg2.net/politics/trump-faces-71-disapproval-among-indian-americans"},
        {"name": "American Bazaar", "url": "https://www.americanbazaaronline.com/2026/02/22/7-in-10-indian-americans-disapprove-of-trump-carnegie-survey/"},
        {"name": "Stop AAPI Hate", "url": "https://stopaapihate.org/reports/"}
    ]),
    "score_total": 80,
    "status": "published",
    "published_at": now,
    "is_editorial": False,
    "image_url": "https://images.pexels.com/photos/37115762/pexels-photo-37115762.jpeg",
    "image_caption": "A South Asian couple on a street in the United States",
    "image_attribution": "Pexels",
    "body": article3_body
}


# ─────────────────────────────────────────────
# PUBLISH
# ─────────────────────────────────────────────
articles = [article1, article2, article3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
